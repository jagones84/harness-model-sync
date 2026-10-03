import pytest

from harness_model_sync.registry import Model, load_registry, model_key


def test_load_registry_parses_models(tmp_path):
    p = tmp_path / "registry.yaml"
    p.write_text(
        "version: 1\n"
        "models:\n"
        "  - provider: openrouter\n"
        "    id: z-ai/glm-5.3-flash\n"
        "    contextWindow: 1048576\n"
        "    maxOutput: 131072\n"
    )
    reg = load_registry(p)
    assert reg.version == 1
    assert reg.models == [
        Model(provider="openrouter", id="z-ai/glm-5.3-flash", context_window=1048576, max_output=131072)
    ]


def test_model_key_joins_provider_and_id():
    assert model_key("openrouter", "z-ai/glm-5.3-flash") == "openrouter/z-ai/glm-5.3-flash"


def test_load_registry_rejects_missing_context_window(tmp_path):
    p = tmp_path / "registry.yaml"
    p.write_text("version: 1\nmodels:\n  - provider: openrouter\n    id: x\n")
    with pytest.raises(ValueError):
        load_registry(p)


def test_load_registry_rejects_unknown_version(tmp_path):
    p = tmp_path / "registry.yaml"
    p.write_text("version: 99\nmodels: []\n")
    with pytest.raises(ValueError):
        load_registry(p)
