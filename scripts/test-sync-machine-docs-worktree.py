#!/usr/bin/env python3
"""Regression test: machine-doc discovery must ignore a linked-worktree .git file."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "sync-machine-docs.py"


def load_module():
    spec = importlib.util.spec_from_file_location("sync_machine_docs", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".git").write_text(
            "gitdir: /private/example/.git/worktrees/feature\n",
            encoding="utf-8",
        )
        (root / "README.md").write_text("# Fixture\n", encoding="utf-8")
        (root / ".gitignore").write_text("target/\n", encoding="utf-8")

        sources = module.discover_sources(root)
        paths = {source.relative_path for source in sources}

        assert ".git" not in paths, paths
        assert "README.md" in paths, paths
        assert ".gitignore" in paths, paths

    print("PASS: linked-worktree .git metadata is excluded from machine-doc discovery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
