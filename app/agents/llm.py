# Anthropic 채팅 모델 생성 공유 헬퍼 — 환경변수(ANTHROPIC_URL, GMS_API_KEY) 기반
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# 이 패키지 폴더의 .env 에서 환경변수를 로드한다(main.py 와 동일 계약).
load_dotenv(Path(__file__).resolve().with_name(".env"))

MODEL_NAME = "claude-sonnet-4-6"


def _normalize_base_url(url: str) -> str:
    """base_url 끝의 /v1/messages, /v1 경로를 제거한다.

    Anthropic SDK 가 자동으로 /v1/messages 를 붙이므로, 환경변수에 해당 경로가
    포함돼 있으면 중복되어 404 가 발생한다.
    """
    url = url.rstrip("/")
    for suffix in ("/v1/messages", "/v1"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
            break
    return url


def build_model() -> ChatAnthropic:
    """환경변수(ANTHROPIC_URL, GMS_API_KEY)로 Anthropic 채팅 모델을 만든다."""
    base_url = _normalize_base_url(os.environ["ANTHROPIC_URL"])
    api_key = os.environ["GMS_API_KEY"]
    return ChatAnthropic(model=MODEL_NAME, base_url=base_url, api_key=api_key)
