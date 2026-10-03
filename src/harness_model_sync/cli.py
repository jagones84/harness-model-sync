"""CLI: sync a registry into each harness config (with --dry-run and backups)."""

from __future__ import annotations

import argparse
import os
import shutil
import time
from pathlib import Path

from .registry import SUPPORTED_VERSION, Registry, dump_registry, load_registry, upsert_models
from .renderers import CodexRenderer, OpenclawRenderer, OpencodeRenderer, PiRenderer, Renderer
from .sources import fetch_llamacpp, fetch_openrouter, parse_llamacpp, parse_openrouter

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
    if name == "openclaw":
        return OpenclawRenderer()
    if name == "codex":
        if not model:
            raise SystemExit("--model is required for the codex renderer")
        return CodexRenderer(model=model, provider=provider)
    raise SystemExit(f"unknown renderer: {name}")


def _cmd_import(args: argparse.Namespace) -> int:
    path = Path(args.registry)
    registry = load_registry(path) if path.exists() else Registry(version=SUPPORTED_VERSION, models=[])

    if args.source == "openrouter":
        api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise SystemExit("set OPENROUTER_API_KEY or pass --api-key")
        fetched = parse_openrouter(fetch_openrouter(api_key))
    else:
        fetched = parse_llamacpp(fetch_llamacpp(args.base_url), provider=args.provider)

    merged = upsert_models(registry, fetched)
    content = dump_registry(merged)
    current = path.read_text() if path.exists() else ""

    if current == content:
        print(f"[import:{args.source}] {path}: up to date")
        return 0
    if args.dry_run:
        print(f"[import:{args.source}] {path}: would write ({len(fetched)} fetched, {len(merged.models)} total)")
        return 0

    if path.exists():
        backup = f"{path}.bak-{time.strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(path, backup)
        print(f"[import:{args.source}] {path}: backup -> {backup}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"[import:{args.source}] {path}: wrote {len(merged.models)} models")
    return 0


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

    imp = sub.add_parser("import", help="refresh the registry from an external catalog")
    imp.add_argument("--from", dest="source", required=True, choices=["openrouter", "llamacpp"])
    imp.add_argument("--registry", default="registry.yaml")
    imp.add_argument("--base-url", default="http://127.0.0.1:8080")
    imp.add_argument("--provider", default="llama-dgx", help="provider name for llamacpp models")
    imp.add_argument("--api-key", default=None, help="OpenRouter key (default: $OPENROUTER_API_KEY)")
    imp.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "import":
        return _cmd_import(args)

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
