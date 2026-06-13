# 서류 폼 마크다운 파서 단위 테스트 — 실제 문서 6종 파싱·로드를 검증한다(네트워크 없음)
import json

import pytest

from app.agents.permit_template import load_template, parse_form_markdown
from app.agents.permits import PERMITS, get_permit

_MOUNTAIN_MD = """# 6. 산지전용 허가 신청서

- templateCode: `mountain_permit`
- name: `산지전용 허가 신청서`
- version: `1`
- processingDays:
    - 시도: `20일`
    - 시군구: `10일`

<!-- 주석은 무시된다 -->

## 1. 기본 정보

- 접수번호 `receiptNumber`
- 접수일 `receiptDate`
    - type: `DATE`
    - display: `date`
- 신청유형 `applicationType`
    - type: `CHOICE`
    - display: `radioGroup`
    - options:
        - 허가
        - 변경허가

## 4. 전용대상 산지

- 전용대상 산지 명세 `conversionTargetTable`
    - type: `TABLE`
    - 설명: 필지별 정보를 입력합니다
    - columns:
        - 소재지 `location`
        - 면적 계 `totalArea`
            - unit: `㎡`
"""


def test_parse_frontmatter_and_metadata() -> None:
    template = parse_form_markdown(_MOUNTAIN_MD)
    assert template.templateCode == "mountain_permit"
    assert template.name == "산지전용 허가 신청서"
    assert template.version == "1"
    assert template.metadata["processingDays"] == {"시도": "20일", "시군구": "10일"}


def test_parse_sections_and_question_ids_are_unique() -> None:
    template = parse_form_markdown(_MOUNTAIN_MD)
    assert [s.id for s in template.sections] == [1, 4]
    ids = [q.id for s in template.sections for q in s.questions]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))  # 전 질문 id 유일


def test_parse_field_attributes_and_options() -> None:
    template = parse_form_markdown(_MOUNTAIN_MD)
    basic = template.sections[0]
    by_key = {q.layoutKey: q for q in basic.questions}

    assert by_key["receiptDate"].questionType == "DATE"
    assert by_key["receiptDate"].displayType == "date"

    app_type = by_key["applicationType"]
    assert app_type.questionType == "CHOICE"
    assert json.loads(app_type.options) == ["허가", "변경허가"]


def test_parse_table_columns_into_subfields() -> None:
    template = parse_form_markdown(_MOUNTAIN_MD)
    table_q = template.sections[1].questions[0]
    assert table_q.questionType == "TABLE"
    assert table_q.subFields["columns"] == ["소재지", "면적 계"]
    assert "필지별 정보를 입력합니다" in table_q.description


@pytest.mark.parametrize("permit", PERMITS, ids=[p.code.value for p in PERMITS])
def test_all_registered_forms_parse(permit) -> None:
    """등록된 6개 유형 서식이 모두 파일에서 로드·파싱되고 질문을 갖는다."""
    template = load_template(permit.code.value)
    assert template is not None, f"{permit.code.value} 서식 로드 실패"
    assert template.templateCode
    questions = [q for s in template.sections for q in s.questions]
    assert len(questions) > 0
    # layoutKey 가 있는 질문은 키가 비어있지 않다.
    assert all(q.name for q in questions)


def test_load_template_unknown_type_returns_none() -> None:
    assert load_template("does_not_exist") is None


def test_every_permit_has_form_file() -> None:
    """레지스트리의 모든 유형에 서식 파일 경로가 등록되어 실제로 존재한다."""
    from app.agents.permits import DOCS_DIR

    for permit in PERMITS:
        assert permit.form_rel_path is not None
        assert (DOCS_DIR / permit.form_rel_path).exists(), permit.form_rel_path
    assert get_permit("mountain").form_filename == "산지전용 허가 신청서.md"
