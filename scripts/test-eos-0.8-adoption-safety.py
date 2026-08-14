#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Failure(RuntimeError):
    pass


def project_fixture_from_canonical(root: Path) -> None:
    env = os.environ.copy()
    env["EOS_ROOT"] = str(root)
    proc = subprocess.run(
        [sys.executable, str(root / "tools" / "eos" / "canonical_state.py"), "project", "--apply"],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise Failure(
            "failed to initialize isolated safety fixture from canonical state\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )


def copy_repo(target: Path) -> None:
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(".git", "machine", "__pycache__", "*.pyc"),
        dirs_exist_ok=True,
    )
    # Safety cases exercise the full canonical wrapper. Seed every isolated
    # fixture from canonical authority so stale/mutable compatibility
    # projections inherited from the source checkout cannot mask the intended
    # negative adoption assertion.
    project_fixture_from_canonical(target)


def eos(root: Path, *args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["EOS_ROOT"] = str(root)
    proc = subprocess.run(
        [str(root / "scripts" / "eos"), *args],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
    )
    if proc.returncode != expect:
        raise Failure(
            f"eos {' '.join(args)} returned {proc.returncode}, expected {expect}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def compatibility_eos(root: Path, *args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    """Run the TSV compatibility runtime for synthetic ordering fixtures.

    The priority/recency tests intentionally construct lifecycle rows that are
    not valid canonical repository state. Running them through `scripts/eos`
    would correctly fail closed before the compatibility selection algorithm is
    reached. These two tests target only `latest_active` / `next` ordering, so
    they invoke the compatibility runtime directly in an isolated temp repo.
    """
    env = os.environ.copy()
    env["EOS_ROOT"] = str(root)
    proc = subprocess.run(
        [sys.executable, str(root / "tools" / "eos" / "eos.py"), *args],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
    )
    if proc.returncode != expect:
        raise Failure(
            f"compatibility eos {' '.join(args)} returned {proc.returncode}, expected {expect}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def snapshot(root: Path) -> dict[str, bytes]:
    paths = (
        ".eos/workflow.tsv",
        ".eos/program-increments.tsv",
        ".eos/work-cycles.tsv",
        ".eos/work-packets.tsv",
        ".eos/events.jsonl",
        "engineering/increments/PI-MVP-001-SEMANTIC-FOUNDATION.md",
        "engineering/work-cycles/WC-MVP-0001.md",
        "engineering/work-packets/WP-MVP-0001.md",
    )
    return {path: (root / path).read_bytes() for path in paths}


def write_manifest(root: Path, name: str, doc: dict) -> str:
    rel = f".eos/adoptions/{name}.json"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return rel


def evidence() -> list[str]:
    return ["engineering/reviews/FOUNDATION-STABILIZATION-CLOSURE-2026-08-12.md"]


def assert_unchanged(root: Path, before: dict[str, bytes], label: str) -> None:
    after = snapshot(root)
    changed = [path for path in before if before[path] != after[path]]
    if changed:
        raise Failure(f"{label} mutated governed state before failing: {changed}")


def test_schema_preflight(root: Path) -> None:
    before = snapshot(root)
    manifest = write_manifest(
        root,
        "test-missing-title",
        {
            "schema_version": "1.0.0",
            "adoption_id": "ADOPT-TEST-MISSING-TITLE",
            "reason": "negative regression fixture",
            "evidence": evidence(),
            "bootstrap": {"complete": True},
            "supersede": [],
            "program_increments": [
                {
                    "id": "PI-MVP-099",
                    "path": "engineering/increments/PI-MVP-001-SEMANTIC-FOUNDATION.md",
                    "status": "DRAFT",
                    "created": "2026-08-12T00:00:00Z",
                    "updated": "2026-08-12T00:00:00Z",
                    "github_url": "",
                }
            ],
            "work_cycles": [],
            "work_packets": [],
        },
    )
    proc = eos(root, "adopt", manifest, "--apply", expect=2)
    output = proc.stdout + proc.stderr
    lowered = output.lower()
    title_schema_failure = (
        "title" in lowered
        and any(
            marker in lowered
            for marker in (
                "schema validation failed",
                "shorter than minlength",
                "missing required field",
            )
        )
    )
    if not title_schema_failure:
        raise Failure(
            "missing-title adoption was not rejected for a title schema violation\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    assert_unchanged(root, before, "schema preflight")


def test_path_containment(root: Path, external: Path) -> None:
    external.write_text("# external\n", encoding="utf-8")
    before = snapshot(root)
    manifest = write_manifest(
        root,
        "test-external-path",
        {
            "schema_version": "1.0.0",
            "adoption_id": "ADOPT-TEST-EXTERNAL-PATH",
            "reason": "negative regression fixture",
            "evidence": evidence(),
            "bootstrap": {"complete": True},
            "supersede": [],
            "program_increments": [
                {
                    "id": "PI-MVP-098",
                    "path": str(external.resolve()),
                    "title": "External path fixture",
                    "status": "DRAFT",
                    "created": "2026-08-12T00:00:00Z",
                    "updated": "2026-08-12T00:00:00Z",
                    "github_url": "",
                }
            ],
            "work_cycles": [],
            "work_packets": [],
        },
    )
    proc = eos(root, "adopt", manifest, "--apply", expect=2)
    if "repository-relative" not in (proc.stdout + proc.stderr):
        raise Failure("absolute external adoption path was not rejected")
    assert_unchanged(root, before, "path containment")
    if external.read_text(encoding="utf-8") != "# external\n":
        raise Failure("external artifact was modified")


def test_atomic_conflict_preflight(root: Path) -> None:
    before = snapshot(root)
    manifest = write_manifest(
        root,
        "test-conflict",
        {
            "schema_version": "1.0.0",
            "adoption_id": "ADOPT-TEST-CONFLICT",
            "reason": "negative regression fixture",
            "evidence": evidence(),
            "bootstrap": {"complete": True},
            "supersede": ["PI-MVP-001"],
            "program_increments": [],
            "work_cycles": [
                {
                    "id": "WC-MVP-0001",
                    "path": "engineering/work-cycles/WC-MVP-0001.md",
                    "title": "Conflicting parent fixture",
                    "status": "READY",
                    "pi": "PI-001",
                    "created": "2026-08-12T00:00:00Z",
                    "updated": "2026-08-12T00:00:00Z",
                    "github_url": "",
                }
            ],
            "work_packets": [],
        },
    )
    proc = eos(root, "adopt", manifest, "--apply", expect=2)
    if "conflicting adoption identity fields" not in (proc.stdout + proc.stderr):
        raise Failure("immutable-field conflict was not caught during preflight")
    assert_unchanged(root, before, "conflict preflight")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def activate_parents(root: Path) -> None:
    pi_rows = read_tsv(root / ".eos/program-increments.tsv")
    for row in pi_rows:
        if row["id"] == "PI-MVP-001":
            row["status"] = "ACTIVE"
    write_tsv(root / ".eos/program-increments.tsv", pi_rows)

    wc_rows = read_tsv(root / ".eos/work-cycles.tsv")
    for row in wc_rows:
        if row["id"] == "WC-MVP-0001":
            row["status"] = "ACTIVE"
    write_tsv(root / ".eos/work-cycles.tsv", wc_rows)


def wp_row(identifier: str, status: str) -> dict[str, str]:
    return {
        "id": identifier,
        "path": "engineering/work-packets/WP-MVP-0001.md",
        "title": identifier,
        "status": status,
        "pi": "PI-MVP-001",
        "wc": "WC-MVP-0001",
        "domain": "CORE",
        "created": "2026-08-12T00:00:00Z",
        "updated": "2026-08-12T00:00:00Z",
        "github_url": "",
    }


def test_inflight_priority(root: Path) -> None:
    activate_parents(root)
    rows = [
        wp_row("WP-MVP-0097", "READY"),
        wp_row("WP-MVP-0098", "AUTHORIZED"),
        wp_row("WP-MVP-0099", "VERIFYING"),
    ]
    write_tsv(root / ".eos/work-packets.tsv", rows)
    out = compatibility_eos(root, "next").stdout
    if "verify WP-MVP-0099" not in out:
        raise Failure(f"next did not prioritize VERIFYING work over pre-start work:\n{out}")


def test_equal_priority_recency(root: Path) -> None:
    activate_parents(root)
    rows = [wp_row("WP-MVP-0096", "READY"), wp_row("WP-MVP-0097", "READY")]
    write_tsv(root / ".eos/work-packets.tsv", rows)
    out = compatibility_eos(root, "next").stdout
    if "authorize ready work packet WP-MVP-0097" not in out:
        raise Failure(f"next did not choose the newest equally prioritized record:\n{out}")


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="eos08-safety-") as tmp:
            base = Path(tmp)
            repo = base / "repo"
            copy_repo(repo)
            test_schema_preflight(repo)
            test_path_containment(repo, base / "external.md")
            test_atomic_conflict_preflight(repo)

        with tempfile.TemporaryDirectory(prefix="eos08-priority-") as tmp:
            repo = Path(tmp) / "repo"
            copy_repo(repo)
            test_inflight_priority(repo)

        with tempfile.TemporaryDirectory(prefix="eos08-recency-") as tmp:
            repo = Path(tmp) / "repo"
            copy_repo(repo)
            test_equal_priority_recency(repo)

        print("EOS 0.8 adoption safety regression checks: PASS")
        return 0
    except (Failure, OSError, subprocess.SubprocessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
