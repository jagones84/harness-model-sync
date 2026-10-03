"""Renderers: turn the registry into each harness's native config format.

A renderer is a small adapter: it knows the target file and how to express the
model limits in that harness's schema. The core stays harness-agnostic.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from .registry import Model

# Providers whose model catalog the harness already knows about; for those we
# only need to override limits (Pi: `modelOverrides`) instead of redeclaring them.
BUILTIN_PROVIDERS = {"openrouter", "anthropic", "openai", "google", "google-generative-ai"}


class Renderer(Protocol):
    name: str
    target: str

    def render(self, models: list[Model], current: str) -> str: ...


def patch_json(text: str, edits: Iterable[tuple[Sequence[str], Any]]) -> str:
    """Set nested keys in a JSON document, creating intermediate objects."""
    data: Any = json.loads(text) if text.strip() else {}
    for path, value in edits:
        node = data
        for key in path[:-1]:
            nxt = node.get(key)
            if not isinstance(nxt, dict):
                nxt = {}
                node[key] = nxt
            node = nxt
        node[path[-1]] = value
    return json.dumps(data, indent=2) + "\n"


@dataclass
class OpencodeRenderer:
    """opencode.json -> provider.<p>.models.<id>.limit = {context, output}."""

    name: str = "opencode"
    target: str = "~/.config/opencode/opencode.json"

    def render(self, models: list[Model], current: str) -> str:
        edits = [
            (
                ["provider", m.provider, "models", m.id, "limit"],
                {"context": m.context_window, "output": m.max_output},
            )
            for m in models
        ]
        return patch_json(current, edits)


@dataclass
class PiRenderer:
    """~/.pi/agent/models.json -> modelOverrides (builtin) or models[] (custom)."""

    name: str = "pi"
    target: str = "~/.pi/agent/models.json"

    def render(self, models: list[Model], current: str) -> str:
        data: Any = json.loads(current) if current.strip() else {}
        providers = data.setdefault("providers", {})
        for m in models:
            provider = providers.setdefault(m.provider, {})
            if m.provider in BUILTIN_PROVIDERS:
                overrides = provider.setdefault("modelOverrides", {})
                overrides[m.id] = {"contextWindow": m.context_window, "maxTokens": m.max_output}
            else:
                entries = provider.setdefault("models", [])
                entry = next((x for x in entries if isinstance(x, dict) and x.get("id") == m.id), None)
                if entry is None:
                    entry = {"id": m.id}
                    entries.append(entry)
                entry["contextWindow"] = m.context_window
                entry["maxTokens"] = m.max_output
        return json.dumps(data, indent=2) + "\n"


@dataclass
class CodexRenderer:
    """~/.codex-openrouter/config.toml -> model_context_window for a single model."""

    model: str
    provider: str = "openrouter"
    base_url: str = "https://openrouter.ai/api/v1"
    env_key: str = "OPENROUTER_API_KEY"
    name: str = "codex"
    target: str = "~/.codex-openrouter/config.toml"

    def render(self, models: list[Model], current: str) -> str:
        match = next((m for m in models if m.provider == self.provider and m.id == self.model), None)
        if match is None:
            raise ValueError(f"model {self.provider}/{self.model} not found in registry")
        lines = [
            f'model = "{self.model}"',
            f'model_provider = "{self.provider}"',
            f"model_context_window = {match.context_window}",
            "",
            f"[model_providers.{self.provider}]",
            f'name = "{self.provider}"',
            f'base_url = "{self.base_url}"',
            f'env_key = "{self.env_key}"',
            'wire_api = "responses"',
        ]
        return "\n".join(lines) + "\n"
