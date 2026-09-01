#!/usr/bin/env python3
"""Regression tests for the deterministic Monad publication exporter."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/export-site-state.py"

spec = importlib.util.spec_from_file_location("monad_export_site_state", SCRIPT)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import exporter: {SCRIPT}")
exporter = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = exporter
spec.loader.exec_module(exporter)


def digest_tree(root: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        values[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return values


def resolve_main_ref() -> str | None:
    for ref in ("main", "origin/main"):
        result = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--verify", f"{ref}^{{commit}}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return ref
    return None


class ExporterUnitTests(unittest.TestCase):
    def test_recursive_glob_matches_zero_or_more_directories(self) -> None:
        self.assertTrue(exporter.pattern_matches("architecture/decisions/ADR-0001.md", "architecture/decisions/**/*.md"))
        self.assertTrue(exporter.pattern_matches("architecture/decisions/runtime/ADR-0002.md", "architecture/decisions/**/*.md"))
        self.assertFalse(exporter.pattern_matches("architecture/overview.md", "architecture/decisions/**/*.md"))

    def test_frontmatter_injection_preserves_existing_frontmatter(self) -> None:
        source = '---\ntitle: "Example"\nstatus: Draft\n---\n\n# Example\n'
        result = exporter.inject_frontmatter(source, "specifications/example.md", "a" * 40, "b" * 40)
        self.assertIn('title: "Example"', result)
        self.assertIn('source_path: "specifications/example.md"', result)
        self.assertEqual(result.count("---"), 2)

    def test_frontmatter_injection_rejects_reserved_source_key(self) -> None:
        source = "---\ngenerated: false\n---\n# Example\n"
        with self.assertRaises(exporter.ExportError):
            exporter.inject_frontmatter(source, "example.md", "a" * 40, "b" * 40)

    def test_markdown_table_parser(self) -> None:
        text = """# Risks

| ID | Risk | L | I | Owner | State |
| --- | --- | ---: | ---: | --- | --- |
| R-001 | Example | 3 | 5 | Owner | Open |
"""
        rows = exporter.parse_markdown_table(text, "ID")
        self.assertEqual(rows[0]["ID"], "R-001")
        self.assertEqual(rows[0]["State"], "Open")

    def test_commit_timestamp_is_not_wall_clock_input(self) -> None:
        # The implementation contract deliberately derives generatedAt from Git.
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"show", "-s", "--format=%cI"', source)
        self.assertNotIn("datetime.now(", source)


class ExporterIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_ref = resolve_main_ref()
        if cls.main_ref is None:
            raise unittest.SkipTest("main/origin/main is unavailable")
        if not (ROOT / ".git").exists():
            raise unittest.SkipTest("tests must run in a Git checkout")

    def run_export(self, output: Path) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--root",
                str(ROOT),
                "--ref",
                self.main_ref,
                "--output",
                str(output),
                "--verify-determinism",
                "--quiet",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        self.assertIn("Publication export: PASS", result.stdout)

    def test_real_main_export_is_byte_reproducible_and_schema_valid(self) -> None:
        with tempfile.TemporaryDirectory(prefix="monad-export-test-") as temp:
            base = Path(temp)
            first = base / "first"
            second = base / "second"
            self.run_export(first)
            self.run_export(second)
            self.assertEqual(digest_tree(first), digest_tree(second))

            generated = first / "content/generated/monad"
            manifest = json.loads((generated / "manifest.json").read_text(encoding="utf-8"))
            provenance = json.loads((generated / "provenance.json").read_text(encoding="utf-8"))

            self.assertEqual(manifest["sourceBranch"], "main")
            self.assertEqual(provenance["sourceCommit"], manifest["sourceCommit"])
            destinations = [artifact["destinationPath"] for artifact in manifest["artifacts"]]
            self.assertEqual(destinations, sorted(destinations))
            self.assertEqual(len(destinations), len(set(destinations)))
            self.assertNotIn("content/generated/monad/manifest.json", destinations)
            self.assertNotIn("content/generated/monad/provenance.json", destinations)

            for filename in (
                "project.json",
                "roadmap.json",
                "work-packets.json",
                "milestones.json",
                "risks.json",
                "releases.json",
                "verification.json",
                "artifacts.json",
                "research.json",
                "evolution.json",
            ):
                self.assertTrue((generated / "state" / filename).is_file(), filename)


if __name__ == "__main__":
    unittest.main(verbosity=2)
