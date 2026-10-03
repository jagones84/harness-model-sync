"""Registry: the single source of truth (models + context windows)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SUPPORTED_VERSION = 1


@dataclass(frozen=True)
class Model:
    provider: str
    id: str
    context_window: int
    max_output: int | None = None
    reserve: int | None = None


@dataclass(frozen=True)
class Registry:
    version: int
    models: list[Model]


def model_key(provider: str, model_id: str) -> str:
    """Canonical ``provider/id`` key for a model."""
    return f"{provider}/{model_id}"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_registry(path: str | Path) -> Registry:
    """Load and validate a registry YAML file."""
    raw: Any = yaml.safe_load(Path(path).read_text())
    _require(isinstance(raw, dict), "registry must be a mapping")

    version = raw.get("version")
    _require(
        version == SUPPORTED_VERSION,
        f"unsupported registry version: {version!r} (expected {SUPPORTED_VERSION})",
    )

    models_raw = raw.get("models") or []
    _require(isinstance(models_raw, list), "models must be a list")

    models: list[Model] = []
    for item in models_raw:
        _require(isinstance(item, dict), "each model must be a mapping")
        provider = item.get("provider")
        model_id = item.get("id")
        _require(bool(provider) and bool(model_id), "each model needs a provider and an id")

        cw = item.get("contextWindow")
        _require(
            isinstance(cw, int) and not isinstance(cw, bool) and cw > 0,
            f"model {provider}/{model_id} needs a positive integer contextWindow",
        )

        mo = item.get("maxOutput")
        _require(
            mo is None or (isinstance(mo, int) and not isinstance(mo, bool) and mo > 0),
            f"model {provider}/{model_id} maxOutput must be a positive integer when set",
        )

        reserve = item.get("reserve")
        models.append(
            Model(
                provider=str(provider),
                id=str(model_id),
                context_window=int(cw),
                max_output=int(mo) if mo is not None else None,
                reserve=int(reserve) if reserve is not None else None,
            )
        )

    return Registry(version=int(version), models=models)
