# 인허가 유형 레지스트리 — docs/ 마크다운 문서를 코드에서 안정적으로 참조하기 위한 매핑
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

# 에이전트에게 노출되는 가상 경로 접두사. main.py 의 CompositeBackend 라우트와 일치해야 한다.
DOCS_MOUNT = "/docs"
# 실제 마크다운이 위치한 디렉토리 (FilesystemBackend root_dir).
DOCS_DIR = Path(__file__).resolve().with_name("docs")


class PermitType(StrEnum):
    """지원하는 인허가 유형 코드."""

    BUILDING = "building"
    MOUNTAIN = "mountain"
    FARMLAND = "farmland"
    ROAD = "road"
    RIVER = "river"
    DEV_ACT = "dev_act"


@dataclass(frozen=True)
class PermitDoc:
    """단일 인허가 유형의 표시명·문서 경로·검색 키워드."""

    code: PermitType
    name: str
    filename: str
    keywords: tuple[str, ...]

    @property
    def doc_path(self) -> str:
        """에이전트가 read_file 에 쓰는 가상 경로. 예: /docs/03_농지전용_….md"""
        return f"{DOCS_MOUNT}/{self.filename}"


# 6개 인허가 유형 ↔ docs/ 파일 매핑. 새 유형은 docs/ 에 .md 추가 후 여기 1줄 등록한다.
PERMITS: tuple[PermitDoc, ...] = (
    PermitDoc(
        code=PermitType.BUILDING,
        name="건축ㆍ대수선ㆍ용도변경 허가",
        filename="건축ㆍ대수선ㆍ용도변경 허가 신청서.md",
        keywords=("건축", "신축", "증축", "대수선", "용도변경", "건물"),
    ),
    PermitDoc(
        code=PermitType.MOUNTAIN,
        name="산지전용 허가",
        filename="02_산지전용_허가_체크리스트_프로세스.md",
        keywords=("산지", "산지전용", "임야", "산림"),
    ),
    PermitDoc(
        code=PermitType.FARMLAND,
        name="농지전용 허가",
        filename="03_농지전용_허가_체크리스트_프로세스.md",
        keywords=("농지", "농지전용", "전답", "경작"),
    ),
    PermitDoc(
        code=PermitType.ROAD,
        name="도로점용 허가",
        filename="04_도로점용허가_체크리스트_프로세스.md",
        keywords=("도로", "도로점용", "점용", "굴착"),
    ),
    PermitDoc(
        code=PermitType.RIVER,
        name="하천점용 허가",
        filename="05_하천점용허가_체크리스트_프로세스.md",
        keywords=("하천", "하천점용", "홍수관리구역"),
    ),
    PermitDoc(
        code=PermitType.DEV_ACT,
        name="개발행위 허가",
        filename="06_개발행위허가_체크리스트_프로세스.md",
        keywords=("개발행위", "형질변경", "토석채취", "공작물"),
    ),
)

# 코드 문자열 → PermitDoc 빠른 조회용 인덱스.
PERMITS_BY_CODE: dict[str, PermitDoc] = {p.code.value: p for p in PERMITS}


def get_permit(code: str) -> PermitDoc | None:
    """유형 코드로 PermitDoc 을 조회한다. 미등록 코드면 None."""
    return PERMITS_BY_CODE.get(code)


def build_docs_index() -> str:
    """시스템 프롬프트에 주입할 인허가 문서 인덱스 텍스트를 만든다.

    에이전트는 이 인덱스로 '어떤 유형의 어떤 파일이 있는지'만 인지하고,
    실제 내용은 필요한 턴에 read_file(doc_path)로 직접 읽는다.
    """
    lines = [
        f"- {p.code.value} : {p.name} → {p.doc_path}  (키워드: {', '.join(p.keywords)})"
        for p in PERMITS
    ]
    return "\n".join(lines)
