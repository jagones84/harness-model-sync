"""CLI: sync a registry into each harness config (with --dry-run and backups)."""

from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path

from .registry import load_registry
from .renderers import CodexRenderer, OpencodeRenderer, PiRenderer, Renderer

DEFAULT_RENDERERS = ("opencode", "pi")


def _resolve_target(target: str, home: Path) -> Path:
    if target == "~" or target.startswith("~/"):
        return home / target[2:]
    return Path(target)


def _make_renderer(name: str, model: str | None, provider: str) -> Renderer:
    if name == "opencode":
        return OpencodeRenderer()
    if name == "pi":
        return PiRenderer()
    if name == "codex":
        if not model:
            raise SystemExit("--model is required for the codex renderer")
        return CodexRenderer(model=model, provider=provider)
    raise SystemExit(f"unknown renderer: {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="harness-model-sync")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sync = sub.add_parser("sync", help="render the registry into harness configs")
    sync.add_argument("--registry", default="registry.yaml")
    sync.add_argument("--home", default=None, help="override home dir (~ expansion)")
    sync.add_argument("--renderer", action="append", default=None)
    sync.add_argument("--dry-run", action="store_true")
    sync.add_argument("--model", default=None, help="model id (codex renderer)")
    sync.add_argument("--provider", default="openrouter", help="provider (codex renderer)")

    args = parser.parse_args(argv)

    registry = load_registry(args.registry)
    home = Path(args.home).expanduser() if args.home else Path.home()
    names = args.renderer or list(DEFAULT_RENDERERS)

    updated = 0
    for name in names:
        renderer = _make_renderer(name, args.model, args.provider)
        path = _resolve_target(renderer.target, home)
        current = path.read_text() if path.exists() else ""
        new_content = renderer.render(registry.models, current)

        if current == new_content:
            print(f"[{name}] {path}: up to date")
            continue

        updated += 1
        if args.dry_run:
            print(f"[{name}] {path}: would update ({len(registry.models)} models)")
            continue

        if path.exists():
            backup = f"{path}.bak-{time.strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(path, backup)
            print(f"[{name}] {path}: backup -> {backup}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_content)
        print(f"[{name}] {path}: updated ({len(registry.models)} models)")

    if args.dry_run:
        print(f"dry-run: {updated} file(s) would change")
    else:
        print(f"sync: {updated} file(s) updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
