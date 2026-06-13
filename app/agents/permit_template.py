# 서류 정보 마크다운 폼 → DocumentTemplate 파서 — permit_type 로 양식을 로드해 자동작성에 쓴다
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from app.agents.permits import DOCS_DIR, get_permit
from app.schemas.permit_document import DocumentTemplate, Question, Section

logger = logging.getLogger(__name__)

# 프론트매터에서 템플릿 본문 필드로 승격할 키. 나머지는 metadata 로 모은다.
_TEMPLATE_KEYS = {"templatecode": "templateCode", "name": "name", "description": "description", "version": "version"}

# 질문 하위 속성 키 매핑(영문/한글 혼용). 값은 내부 누적 딕셔너리의 키.
_SCALAR_ATTRS = {"type": "questionType", "display": "displayType", "validation": "validation"}
_DESC_ATTRS = {"설명", "description", "예시", "예"}
_LIST_ATTRS = {"options", "columns", "rows"}

# 라벨 끝의 `layoutKey` 추출용. 예: "접수일 `receiptDate`" → ("접수일", "receiptDate")
_KEY_RE = re.compile(r"^(?P<name>.*?)\s*`(?P<key>[^`]+)`\s*$")
# "## 4. 전용대상 산지" → 번호 4, 제목 "전용대상 산지"
_SECTION_RE = re.compile(r"^#{2,3}\s+(?:(?P<no>\d+)\.\s*)?(?P<title>.+?)\s*$")


def _indent(line: str) -> int:
    """선행 공백 수(탭은 4칸으로 환산)."""
    expanded = line.replace("\t", "    ")
    return len(expanded) - len(expanded.lstrip(" "))


def _clean(value: str) -> str:
    """값에서 백틱과 양끝 공백을 제거한다."""
    return value.strip().strip("`").strip()


class _QBuilder:
    """파싱 도중 질문 1개의 속성을 누적하는 가변 버퍼."""

    def __init__(self, qid: int, name: str, layout_key: str | None, order: int) -> None:
        self.id = qid
        self.name = name
        self.layout_key = layout_key
        self.order = order
        self.questionType: str | None = None
        self.displayType: str | None = None
        self.validation: str | None = None
        self.desc: list[str] = []
        self.options: list[str] = []
        self.columns: list[str] = []
        self.rows: list[str] = []
        # 현재 깊은 들여쓰기 불릿을 모으는 대상 리스트(options/columns/rows). 없으면 None.
        self.collect: list[str] | None = None

    def to_question(self) -> Question:
        sub: dict[str, list[str]] = {}
        if self.columns:
            sub["columns"] = self.columns
        if self.rows:
            sub["rows"] = self.rows
        return Question(
            id=self.id,
            layoutKey=self.layout_key,
            questionType=self.questionType,
            displayType=self.displayType,
            name=self.name or None,
            description=" / ".join(self.desc) or None,
            options=json.dumps(self.options, ensure_ascii=False) if self.options else None,
            validation=self.validation,
            subFields=sub or None,
            orderNo=self.order,
        )


def _parse_attr(builder: _QBuilder, content: str) -> None:
    """질문 하위 들여쓰기 라인('- key: val' 또는 깊은 '- 값')을 해석한다."""
    key, sep, raw = content.partition(":")
    key_norm = key.strip().lower()
    val = _clean(raw) if sep else ""

    if sep and key_norm in _SCALAR_ATTRS:
        setattr(builder, _SCALAR_ATTRS[key_norm], val or None)
        builder.collect = None
        return
    if sep and (key.strip() in _DESC_ATTRS or key_norm in _DESC_ATTRS):
        if val:
            builder.desc.append(val)
        builder.collect = None
        return
    if sep and key_norm in _LIST_ATTRS:
        target = getattr(builder, key_norm)
        builder.collect = target
        if val:
            target.append(val)
        return
    if sep and key_norm == "unit":
        # 단위는 설명에 녹여 추출 모델이 인지하게 한다.
        if val:
            builder.desc.append(f"단위: {val}")
        builder.collect = None
        return

    # 알려진 키가 아니면 현재 수집 중인 리스트(options 등)의 항목으로 본다.
    if builder.collect is not None:
        item = _KEY_RE.sub(lambda m: m.group("name"), content).strip()
        if item:
            builder.collect.append(_clean(item))


def parse_form_markdown(text: str, *, template_id: int | None = None) -> DocumentTemplate:
    """서류 정보 bullet 형식 마크다운을 DocumentTemplate 으로 변환한다.

    - 첫 '## ' 이전 불릿은 프론트매터(templateCode·name·… + metadata).
    - '## N. 제목'은 섹션, '- 라벨 `key`'는 질문, 들여쓴 불릿은 질문 속성.
    """
    lines = text.splitlines()
    meta: dict[str, object] = {}
    template_fields: dict[str, str] = {}
    sections: list[Section] = []

    cur_section_qs: list[_QBuilder] = []
    cur_section: dict[str, object] | None = None
    cur_q: _QBuilder | None = None
    last_meta_key: str | None = None
    qid = 0
    in_frontmatter = True

    def flush_section() -> None:
        if cur_section is not None:
            sections.append(
                Section(
                    id=int(cur_section["id"]),
                    name=str(cur_section["name"]),
                    orderNo=int(cur_section["id"]),
                    questions=[b.to_question() for b in cur_section_qs],
                )
            )

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("<!--"):
            continue

        section_match = _SECTION_RE.match(stripped) if stripped.startswith("#") else None
        if section_match:
            in_frontmatter = False
            cur_q = None
            # '###' 서브섹션은 별도 섹션으로 두지 않고 직전 섹션에 이어 붙인다.
            if stripped.startswith("### ") and cur_section is not None:
                continue
            flush_section()
            cur_section_qs = []
            no = section_match.group("no")
            cur_section = {"id": int(no) if no else len(sections) + 1, "name": section_match.group("title")}
            continue

        if not stripped.startswith("- "):
            continue
        content = stripped[2:].strip()
        indent = _indent(raw_line)

        if in_frontmatter:
            key, sep, raw = content.partition(":")
            key_norm = key.strip().lower()
            if indent >= 4 and last_meta_key:  # processingDays 같은 중첩 항목
                bucket = meta.setdefault(last_meta_key, {})
                if isinstance(bucket, dict):
                    bucket[key.strip()] = _clean(raw)
                continue
            if not sep:
                continue
            val = _clean(raw)
            if key_norm in _TEMPLATE_KEYS:
                template_fields[_TEMPLATE_KEYS[key_norm]] = val
            else:
                meta[key.strip()] = val if val else {}
            last_meta_key = key.strip()
            continue

        if cur_section is None:
            continue

        if indent < 4:  # 질문(필드) 라인
            m = _KEY_RE.match(content)
            name = m.group("name").strip() if m else content.rstrip(":").strip()
            layout_key = m.group("key") if m else None
            qid += 1
            cur_q = _QBuilder(qid, name, layout_key, len(cur_section_qs) + 1)
            cur_section_qs.append(cur_q)
        elif cur_q is not None:  # 질문 속성 라인
            _parse_attr(cur_q, content)

    flush_section()

    return DocumentTemplate(
        id=template_id,
        templateCode=template_fields.get("templateCode"),
        name=template_fields.get("name"),
        description=template_fields.get("description"),
        version=template_fields.get("version"),
        metadata=meta or None,
        sections=sections,
    )


def load_template(permit_type: str) -> DocumentTemplate | None:
    """permit_type 의 신청서 서식 마크다운을 읽어 DocumentTemplate 으로 반환한다.

    미등록 유형이거나 서식 파일이 없으면 None.
    """
    permit = get_permit(permit_type)
    if permit is None or permit.form_rel_path is None:
        return None
    path = DOCS_DIR / permit.form_rel_path
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        logger.warning("서식 문서 읽기 실패: %s", path)
        return None
    return parse_form_markdown(text)


def form_path(permit_type: str) -> Path | None:
    """permit_type 서식 문서의 실제 파일 경로(없으면 None). 테스트·디버깅용."""
    permit = get_permit(permit_type)
    if permit is None or permit.form_rel_path is None:
        return None
    return DOCS_DIR / permit.form_rel_path
