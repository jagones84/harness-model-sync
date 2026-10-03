# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/). Versioning: [SemVer](https://semver.org/).

## [0.2.0] - 2026-10-03

### Added
- `import` subcommand: refresh `registry.yaml` from a live catalog
  (`import --from openrouter` or `import --from llamacpp --base-url ...`). It merges by
  `provider/id`, so running it once per source accumulates. This wires the previously
  unreachable `sources.py` parsers/fetchers into the CLI, making `registry.example.yaml`
  accurate.
- Test: end-to-end `sync` verifying the `*.bak-<timestamp>` backup and the `up to date`
  no-op on a second run (18 tests total).

### Fixed
- `__version__` now derives from the installed package metadata instead of a hardcoded
  string, so it can no longer drift from `pyproject.toml` (was `0.1.0` vs package `0.1.1`).

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
