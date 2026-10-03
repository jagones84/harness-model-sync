import json

from harness_model_sync.registry import Model
from harness_model_sync.renderers import OpenclawRenderer

MODELS = [
    Model(provider="openrouter", id="z-ai/glm-5.3-flash", context_window=1048576, max_output=131072),
    Model(provider="llama-dgx", id="nex-n25-mini-uncensored-q8", context_window=262144, max_output=32768),
]

CURRENT = json.dumps(
    {
        "models": {
            "providers": {
                "openrouter": {"models": [{"id": "z-ai/glm-5.3-flash", "contextWindow": 999}]},
                "llama-dgx": {"models": [{"id": "nex-n25-mini-uncensored-q8", "contextWindow": 1}]},
            }
        }
    }
)


def test_openclaw_renderer_updates_existing_catalog_entries():
    out = OpenclawRenderer().render(MODELS, CURRENT)
    d = json.loads(out)
    provs = d["models"]["providers"]
    assert provs["openrouter"]["models"][0]["contextWindow"] == 1048576
    assert provs["llama-dgx"]["models"][0]["contextWindow"] == 262144


def test_openclaw_renderer_does_not_duplicate_entries():
    out = OpenclawRenderer().render(MODELS, CURRENT)
    d = json.loads(out)
    assert len(d["models"]["providers"]["openrouter"]["models"]) == 1


def test_openclaw_renderer_ignores_models_absent_from_the_catalog():
    out = OpenclawRenderer().render(MODELS, "{}")
    assert json.loads(out) == {}
