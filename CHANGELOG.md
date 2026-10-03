# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/). Versioning: [SemVer](https://semver.org/).

## [0.1.1] - 2026-10-03

### Changed
- README: cross-platform install instructions (Windows PowerShell / macOS / Linux),
  explicit Python `>= 3.11` requirement, `pip install git+...` and no-install run
  examples, and the missing `openclaw` renderer row in the target table.

### Verified
- Test suite passes on Windows (Python 3.12): 17 passed.
- All four renderers (opencode, pi, codex, openclaw) write the correct config on
  Windows using a redirected `--home`.

## [0.1.0] - 2026-10-03

### Added
- Single-source `registry.yaml` (provider, model id, `contextWindow`, `maxOutput`) plus
  `registry.example.yaml`.
- Renderers that express model limits in each harness's native schema:
  - `opencode`: `provider.<p>.models.<id>.limit = {context, output}`
  - `pi`: `providers.<p>.modelOverrides.<id> = {contextWindow, maxTokens}` for built-in
    providers, `models[]` entries for custom ones (preserves the rest of the file)
  - `codex`: TOML `model_context_window` (merges, preserving sections the tool does not
    own, e.g. `[projects.*]`)
  - `openclaw`: `models.providers.<p>.models[].contextWindow`, update-only (the catalog is
    curated and each provider carries its own baseUrl/apiKey)
- CLI `sync` with `--registry`, `--home`, `--renderer`, `--dry-run` and automatic
  `*.bak-<timestamp>` backups.
- Sources with pure, unit-tested parsers: `parse_openrouter` (`context_length`) and
  `parse_llamacpp` (context from launch args `--ctx-size`).
- Test suite (17 tests, written test-first).
