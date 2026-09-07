#!/usr/bin/env python3
"""Regression coverage for scope-sensitive EOSV evidence freshness."""
from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MODULE = REPO / "tools" / "eos" / "verification_v2.py"


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(root: Path):
    spec = importlib.util.spec_from_file_location("eosv_scope_test", MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    for name, value in {
        "ROOT": root,
        "EOS": root / ".eos",
        "CORE": root / "tools" / "eos" / "eos.py",
        "EVID_REG": root / ".eos" / "evidence.tsv",
        "LINK_REG": root / ".eos" / "evidence-links.tsv",
        "PERF_REG": root / ".eos" / "performance-baselines.tsv",
        "EVENTS": root / ".eos" / "events.jsonl",
    }.items():
        setattr(module, name, value)
    return module


def set_state(root: Path, lifecycle: str) -> None:
    path = root / ".eos/state/current.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"entities": {"WP": {"WP-TEST-0001": {"id": "WP-TEST-0001", "kind": "WP", "lifecycle_state": lifecycle}}}}, indent=2) + "\n")


def build_fixture(root: Path) -> str:
    (root / "src").mkdir(parents=True)
    (root / "src/relevant.py").write_text("VALUE = 1\n")
    (root / "scripts").mkdir(parents=True)
    (root / "scripts/unrelated.py").write_text("OTHER = 1\n")
    (root / "engineering/work-packets").mkdir(parents=True)
    (root / "engineering/work-packets/WP-TEST-0001.md").write_text("# WP-TEST-0001\n\nReferences PI-TEST-001.\n")
    (root / "engineering/increments").mkdir(parents=True)
    (root / "engineering/increments/PI-TEST-001.md").write_text("# PI-TEST-001\n\nGoverning semantics.\n")

    eos = root / ".eos"
    (eos / "executions").mkdir(parents=True)
    (eos / "evidence").mkdir(parents=True)
    (eos / "state-machines").mkdir(parents=True)
    (eos / "state-machines/wp.json").write_text(json.dumps({"terminal_states": ["CLOSED", "SUPERSEDED"]}))
    set_state(root, "CLOSED")

    write_tsv(eos / "work-packets.tsv", ["id", "path", "status", "pi", "wc"], [{"id": "WP-TEST-0001", "path": "engineering/work-packets/WP-TEST-0001.md", "status": "CLOSED", "pi": "PI-TEST-001", "wc": ""}])
    write_tsv(eos / "program-increments.tsv", ["id", "path"], [{"id": "PI-TEST-001", "path": "engineering/increments/PI-TEST-001.md"}])
    for name in ["work-cycles.tsv", "change-requests.tsv", "maintenance.tsv", "releases.tsv", "artifacts.tsv"]:
        write_tsv(eos / name, ["id", "path"], [])
    write_tsv(eos / "evidence-links.tsv", ["evidence_id", "reference", "relation", "created", "actor"], [])
    write_tsv(eos / "performance-baselines.tsv", ["id", "name", "target", "unit", "direction", "baseline", "tolerance", "created", "updated"], [])
    (eos / "events.jsonl").write_text("")

    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "EOSV test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)
    baseline = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()

    write_tsv(eos / "executions.tsv", ["id", "path", "target", "status", "branch", "worktree", "baseline_commit", "governing_hash", "contract_hash", "result_path", "actor", "created", "updated"], [{"id": "EXEC-TEST-0001", "path": ".eos/executions/EXEC-TEST-0001.json", "target": "WP-TEST-0001", "status": "CLOSED", "branch": "test", "worktree": str(root / "missing-historical-worktree"), "baseline_commit": baseline, "governing_hash": "gov-v1", "contract_hash": "contract-v1", "result_path": ".eos/evidence/EXEC-TEST-0001-result.json", "actor": "test", "created": "2026-09-07T00:00:00Z", "updated": "2026-09-07T00:00:01Z"}])
    (eos / "executions/EXEC-TEST-0001.json").write_text(json.dumps({"governing_inputs": [{"path": "engineering/work-packets/WP-TEST-0001.md"}, {"path": "engineering/increments/PI-TEST-001.md"}], "result": {"path": ".eos/evidence/EXEC-TEST-0001-result.json"}}, indent=2))
    (eos / "evidence/EXEC-TEST-0001-result.json").write_text(json.dumps({"agent_result": {"changed_files": ["src/relevant.py"]}, "eos_observation": {"actual_changed_files": ["src/relevant.py"]}}, indent=2))
    return baseline


def write_legacy_stale(root: Path, module) -> None:
    machine = root / ".eos/evidence/EVID-TEST-0001.json"
    machine.write_text('{"historical": true}\n')
    row = {field: "" for field in module.EVID_FIELDS}
    row.update({"id": "EVID-TEST-0001", "path": "engineering/evidence/EVID-TEST-0001.md", "target": "WP-TEST-0001", "validator": "repository", "profile": "wp", "kind": "repository", "status": "STALE", "result": "PASSED", "exit_code": "0", "command": "fixture", "source_hash": "a" * 64, "environment_hash": "b" * 64, "artifact_hash": module.file_hash(machine), "created": "2026-09-01T00:00:00Z", "updated": "2026-09-01T00:00:00Z"})
    write_tsv(root / ".eos/evidence.tsv", module.EVID_FIELDS, [row])


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        build_fixture(root)
        module = load_module(root)

        first, payload = module.source_fingerprint("WP-TEST-0001")
        assert first.startswith("scope-v2:")
        assert set(payload["implementation_scope"]) == {"src/relevant.py"}

        unrelated = root / "scripts/unrelated.py"
        unrelated.write_text("OTHER = 2\n")
        assert module.source_fingerprint("WP-TEST-0001")[0] == first

        relevant = root / "src/relevant.py"
        relevant.write_text("VALUE = 2\n")
        assert module.source_fingerprint("WP-TEST-0001")[0] != first
        relevant.write_text("VALUE = 1\n")

        governing = root / "engineering/increments/PI-TEST-001.md"
        governing.write_text("# PI-TEST-001\n\nChanged governing semantics.\n")
        assert module.source_fingerprint("WP-TEST-0001")[0] != first

        write_legacy_stale(root, module)
        ok, report = module.verify_evidence(True)
        assert ok, report
        assert "current stale evidence: 0" in report
        assert "legacy terminal evidence: 1" in report

        set_state(root, "IN_PROGRESS")
        ok, report = module.verify_evidence(True)
        assert not ok, report
        assert "current stale evidence: 1" in report

        print("EOSV scope-sensitive evidence freshness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
