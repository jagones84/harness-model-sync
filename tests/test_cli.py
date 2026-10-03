import json

from harness_model_sync.cli import main

REGISTRY = (
    "version: 1\n"
    "models:\n"
    "  - provider: openrouter\n"
    "    id: z-ai/glm-5.3-flash\n"
    "    contextWindow: 1048576\n"
    "    maxOutput: 131072\n"
)


def _home(tmp_path):
    home = tmp_path / "home"
    (home / ".config/opencode").mkdir(parents=True)
    (home / ".config/opencode/opencode.json").write_text('{"provider": {}}')
    return home


def test_dry_run_reports_and_does_not_write(tmp_path):
    reg = tmp_path / "registry.yaml"
    reg.write_text(REGISTRY)
    home = _home(tmp_path)

    rc = main(["sync", "--dry-run", "--registry", str(reg), "--home", str(home), "--renderer", "opencode"])

    assert rc == 0
    assert json.loads((home / ".config/opencode/opencode.json").read_text()) == {"provider": {}}


def test_sync_writes_opencode_limit(tmp_path):
    reg = tmp_path / "registry.yaml"
    reg.write_text(REGISTRY)
    home = _home(tmp_path)

    rc = main(["sync", "--registry", str(reg), "--home", str(home), "--renderer", "opencode"])

    assert rc == 0
    d = json.loads((home / ".config/opencode/opencode.json").read_text())
    assert d["provider"]["openrouter"]["models"]["z-ai/glm-5.3-flash"]["limit"] == {
        "context": 1048576,
        "output": 131072,
    }


def test_sync_backs_up_then_reports_up_to_date(tmp_path, capsys):
    reg = tmp_path / "registry.yaml"
    reg.write_text(REGISTRY)
    home = _home(tmp_path)
    target = home / ".config/opencode/opencode.json"

    rc = main(["sync", "--registry", str(reg), "--home", str(home), "--renderer", "opencode"])

    assert rc == 0
    backups = list(target.parent.glob("opencode.json.bak-*"))
    assert len(backups) == 1
    assert json.loads(backups[0].read_text()) == {"provider": {}}

    capsys.readouterr()
    rc = main(["sync", "--registry", str(reg), "--home", str(home), "--renderer", "opencode"])

    assert rc == 0
    assert "up to date" in capsys.readouterr().out
    assert len(list(target.parent.glob("opencode.json.bak-*"))) == 1
