"""Sources: refresh registry numbers from external catalogs (pure parsers + fetchers)."""

from __future__ import annotations

import json
import urllib.request
from typing import Any

from .registry import Model

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


def parse_openrouter(payload: dict) -> list[Model]:
    """Map an OpenRouter /models payload to models (context_length is authoritative)."""
    models: list[Model] = []
    for entry in payload.get("data", []) or []:
        if not isinstance(entry, dict):
            continue
        cw = entry.get("context_length")
        if not isinstance(cw, int) or isinstance(cw, bool) or cw <= 0:
            continue
        max_out = (entry.get("top_provider") or {}).get("max_completion_tokens")
        models.append(
            Model(
                provider="openrouter",
                id=str(entry.get("id", "")),
                context_window=int(cw),
                max_output=int(max_out) if isinstance(max_out, int) and not isinstance(max_out, bool) else None,
            )
        )
    return models


def _ctx_from_args(args: list[Any]) -> int | None:
    for index, arg in enumerate(args):
        if not isinstance(arg, str):
            continue
        if arg in ("--ctx-size", "-c") and index + 1 < len(args):
            try:
                return int(args[index + 1])
            except (TypeError, ValueError):
                return None
        if arg.startswith("--ctx-size="):
            try:
                return int(arg.split("=", 1)[1])
            except ValueError:
                return None
    return None


def parse_llamacpp(payload: dict, provider: str) -> list[Model]:
    """Map a llama.cpp /v1/models payload to models (ctx from the launch args)."""
    models: list[Model] = []
    for entry in payload.get("data", []) or []:
        if not isinstance(entry, dict):
            continue
        cw = _ctx_from_args((entry.get("status") or {}).get("args") or [])
        if cw is None:
            continue
        models.append(Model(provider=provider, id=str(entry.get("id", "")), context_window=cw))
    return models


def fetch_openrouter(api_key: str) -> dict:
    request = urllib.request.Request(
        OPENROUTER_MODELS_URL, headers={"Authorization": f"Bearer {api_key}"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode())


def fetch_llamacpp(base_url: str) -> dict:
    url = base_url.rstrip("/") + "/v1/models"
    with urllib.request.urlopen(url, timeout=15) as response:
        return json.loads(response.read().decode())
