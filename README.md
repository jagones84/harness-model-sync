# harness-model-sync

One source of truth for **LLM model context windows**, rendered into each coding-harness config.

Coding harnesses store model limits in different formats (JSON with `limit`, JSON with
`contextWindow`, TOML...). Instead of editing every file, keep one `registry.yaml` and let
this tool render the right one for each harness.

## Why

A compaction threshold is only meaningful relative to the model's **real context window**.
Declaring the window once removes drift between harnesses (opencode / pi / codex / openclaw).

## Install

```bash
pip install -e .
```

(or run without installing: `PYTHONPATH=src python3 -m harness_model_sync.cli ...`)

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

## Adding a harness

Implement a renderer with three members — `name`, `target`, `render(models, current) -> str` —
and register it in `cli._make_renderer`. The core stays harness-agnostic.

## Development

```bash
pytest -q
```

## License

MIT
