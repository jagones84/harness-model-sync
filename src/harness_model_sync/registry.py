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


def upsert_models(registry: Registry, models: list[Model]) -> Registry:
    """Merge ``models`` into ``registry`` keyed by ``provider/id``, keeping existing order."""
    index = {model_key(m.provider, m.id): m for m in registry.models}
    order = [model_key(m.provider, m.id) for m in registry.models]
    for model in models:
        key = model_key(model.provider, model.id)
        if key not in index:
            order.append(key)
        index[key] = model
    return Registry(version=registry.version, models=[index[key] for key in order])


REGISTRY_HEADER = (
    "# Single source of truth for model context windows.\n"
    "# contextWindow / maxOutput are tokens. Populate it with:\n"
    "#   harness-model-sync import --from openrouter\n"
    "#   harness-model-sync import --from llamacpp --base-url http://127.0.0.1:8080\n"
)


def dump_registry(registry: Registry, header: str = REGISTRY_HEADER) -> str:
    """Serialize a registry back to YAML (round-trips :func:`load_registry`)."""
    entries: list[dict[str, Any]] = []
    for m in registry.models:
        entry: dict[str, Any] = {
            "provider": m.provider,
            "id": m.id,
            "contextWindow": m.context_window,
        }
        if m.max_output is not None:
            entry["maxOutput"] = m.max_output
        if m.reserve is not None:
            entry["reserve"] = m.reserve
        entries.append(entry)
    body = yaml.safe_dump({"version": registry.version, "models": entries}, sort_keys=False)
    return header + body
