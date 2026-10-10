"""Provider selection from environment. Keys come from env only; never from files."""
from __future__ import annotations

from typing import Mapping

from ..application.ports import FeedbackProvider
from .anthropic_provider import AnthropicProvider
from .stub_provider import StubProvider


def provider_from_env(env: Mapping[str, str]) -> FeedbackProvider:
    key = env.get("ANTHROPIC_API_KEY", "").strip()
    model = env.get("CRUCIBLE_MODEL", "").strip()
    if key and model:
        return AnthropicProvider(api_key=key, model=model)
    return StubProvider()
