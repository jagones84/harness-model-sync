# harness-model-sync

One source of truth for **LLM model limits** (context window and max output), rendered into
each coding-harness config.

Coding harnesses store model limits in different formats (JSON with `limit`, JSON with
`contextWindow`, TOML...). Instead of editing every file, keep one `registry.yaml` and let
this tool render the right one for each harness.

## Why

A compaction threshold is only meaningful relative to the model's **real context window**.
Declaring the limits once removes drift between harnesses (opencode / pi / codex / openclaw).

## Requirements

- Python **>= 3.11** (uses the stdlib `tomllib`).
- Works on **Windows, macOS and Linux**: every target uses `~`, resolved to the
  operating system's home directory, so no path is hardcoded.

## Install

Clone and install:

```bash
git clone https://github.com/jagones84/harness-model-sync.git
cd harness-model-sync
pip install .
```

Editable install (for development):

```bash
pip install -e ".[dev]"
```

Install straight from git (no clone):

```bash
pip install git+https://github.com/jagones84/harness-model-sync.git
```

Run without installing:

```bash
# Linux / macOS
PYTHONPATH=src python3 -m harness_model_sync.cli sync --dry-run
```

```powershell
# Windows (PowerShell)
$env:PYTHONPATH = "src"; python -m harness_model_sync.cli sync --dry-run
```

> `registry.yaml` is **not** shipped (it is gitignored). Copy `registry.example.yaml`
> to `registry.yaml` and fill in your models.

## Import (refresh from sources)

Instead of hand-editing numbers, pull them from a live catalog. `import` merges the
fetched models into the registry (keyed by `provider/id`), so you can run it once per
source and it accumulates:

```bash
# OpenRouter (reads $OPENROUTER_API_KEY, or pass --api-key)
harness-model-sync import --from openrouter

# A local llama.cpp server (context read from the launch args)
harness-model-sync import --from llamacpp --base-url http://127.0.0.1:8080 --provider llama-dgx
```

`--dry-run` previews; a real run backs the registry up to `registry.yaml.bak-<timestamp>`.

## Registry

See `registry.example.yaml`:

```yaml
version: 1
models:
  - provider: openrouter
    id: z-ai/glm-5.3-flash
    contextWindow: 1048576
    maxOutput: 131072
```

## Usage

```bash
harness-model-sync sync --registry registry.yaml --dry-run
harness-model-sync sync --registry registry.yaml
harness-model-sync sync --registry registry.yaml --renderer codex --model z-ai/glm-5.3-flash
```

`--dry-run` never writes. Real writes create a `*.bak-<timestamp>` next to the target.

## Renderers

| renderer | target | writes |
|---|---|---|
| `opencode` | `~/.config/opencode/opencode.json` | `provider.<p>.models.<id>.limit` |
| `pi` | `~/.pi/agent/models.json` | `modelOverrides` / `models[].contextWindow` |
| `codex` | `~/.codex-openrouter/config.toml` | `model_context_window` |
| `openclaw` | `~/.openclaw/openclaw.json` | `models.providers.<p>.models[].contextWindow` (update-only) |

## Adding a harness

Implement a renderer with three members — `name`, `target`, `render(models, current) -> str` —
and register it in `cli._make_renderer`. The core stays harness-agnostic.

## Development

```bash
pytest -q
```

## License

MIT
