import json

from harness_model_sync.registry import Model
from harness_model_sync.renderers import (
    CodexRenderer,
    OpencodeRenderer,
    PiRenderer,
    patch_json,
)

MODELS = [
    Model(provider="openrouter", id="z-ai/glm-5.3-flash", context_window=1048576, max_output=131072),
    Model(provider="llama-dgx", id="nex-n25-mini-uncensored-q8", context_window=262144, max_output=32768),
]


def test_patch_json_sets_nested_value():
    out = patch_json('{"a": {"b": {}}}', [(["a", "b", "c"], 5)])
    assert json.loads(out)["a"]["b"]["c"] == 5


def test_opencode_renderer_sets_model_limits():
    out = OpencodeRenderer().render(MODELS, '{"provider": {}}')
    d = json.loads(out)
    assert d["provider"]["openrouter"]["models"]["z-ai/glm-5.3-flash"]["limit"] == {
        "context": 1048576,
        "output": 131072,
    }
    assert d["provider"]["llama-dgx"]["models"]["nex-n25-mini-uncensored-q8"]["limit"] == {
        "context": 262144,
        "output": 32768,
    }


def test_pi_renderer_uses_overrides_for_builtin_and_models_for_custom():
    out = PiRenderer().render(MODELS, "")
    d = json.loads(out)
    assert d["providers"]["openrouter"]["modelOverrides"]["z-ai/glm-5.3-flash"]["contextWindow"] == 1048576
    assert d["providers"]["llama-dgx"]["models"][0]["id"] == "nex-n25-mini-uncensored-q8"
    assert d["providers"]["llama-dgx"]["models"][0]["contextWindow"] == 262144


def test_pi_renderer_preserves_existing_provider_config():
    current = json.dumps({"providers": {"llama-dgx": {"baseUrl": "http://127.0.0.1:8080/v1"}}})
    out = PiRenderer().render(MODELS, current)
    assert json.loads(out)["providers"]["llama-dgx"]["baseUrl"] == "http://127.0.0.1:8080/v1"


def test_codex_renderer_writes_context_window_and_provider():
    r = CodexRenderer(model="z-ai/glm-5.3-flash", provider="openrouter")
    out = r.render(MODELS, "")
    assert "model_context_window = 1048576" in out
    assert 'model_provider = "openrouter"' in out
    assert 'wire_api = "responses"' in out


def test_codex_renderer_preserves_existing_sections():
    current = '[projects."/x"]\ntrust_level = "trusted"\n'
    out = CodexRenderer(model="z-ai/glm-5.3-flash", provider="openrouter").render(MODELS, current)
    assert "trusted" in out
    assert "model_context_window = 1048576" in out
