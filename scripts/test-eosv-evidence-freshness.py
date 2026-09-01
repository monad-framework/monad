#!/usr/bin/env python3
"""Regression coverage for EOSV execution and non-execution freshness."""

from __future__ import annotations

import csv
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "eos" / "verification_v2.py"


def run(*args: str, cwd: Path) -> None:
    subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )


def write_tsv(
    path: Path,
    fields: list[str],
    rows: list[dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def load_module(root: Path):
    spec = importlib.util.spec_from_file_location(
        "eosv_freshness",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MODULE_PATH}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    # Redirect EOSV's repository globals into the isolated fixture.
    module.ROOT = root
    module.EOS = root / ".eos"
    module.EVID_REG = module.EOS / "evidence.tsv"
    module.LINK_REG = module.EOS / "evidence-links.tsv"

    return module


def fixture(root: Path) -> None:
    # Real implementation source used to prove substantive source changes
    # invalidate non-execution and execution-bound fingerprints.
    (root / "src").mkdir(parents=True)
    (root / "src" / "lib.rs").write_text(
        "pub fn answer() -> u8 { 42 }\n",
        encoding="utf-8",
    )

    # Work packet deliberately uses the visible **State:** form.
    wp_dir = root / "engineering" / "work-packets"
    wp_dir.mkdir(parents=True)

    (wp_dir / "WP-TEST-0001.md").write_text(
        """---
status: IN_PROGRESS
updated: 2026-08-15
---

# WP

**State:** IN_PROGRESS

References PI-TEST-001.

Work-packet semantic content.
""",
        encoding="utf-8",
    )

    # Governing PI deliberately uses the visible **Status:** form so the test
    # covers both supported lifecycle-field spellings.
    pi_dir = root / "engineering" / "increments"
    pi_dir.mkdir(parents=True)

    (pi_dir / "PI-TEST-001.md").write_text(
        """---
status: IN_PROGRESS
updated: 2026-08-15
---

# PI

**Status:** IN_PROGRESS

Governing content.
""",
        encoding="utf-8",
    )

    write_tsv(
        root / ".eos" / "work-packets.tsv",
        ["id", "path", "pi", "wc"],
        [
            {
                "id": "WP-TEST-0001",
                "path": "engineering/work-packets/WP-TEST-0001.md",
                "pi": "PI-TEST-001",
                "wc": "",
            }
        ],
    )

    write_tsv(
        root / ".eos" / "program-increments.tsv",
        ["id", "path"],
        [
            {
                "id": "PI-TEST-001",
                "path": "engineering/increments/PI-TEST-001.md",
            }
        ],
    )

    # Minimal registries required by verification_v2 artifact lookup.
    for name in (
        "work-cycles.tsv",
        "change-requests.tsv",
        "maintenance.tsv",
        "releases.tsv",
        "evidence.tsv",
        "artifacts.tsv",
    ):
        write_tsv(
            root / ".eos" / name,
            ["id", "path"],
            [],
        )


def git_head(root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        fixture(root)

        # Establish the initial committed source state.
        run("git", "init", "-q", cwd=root)
        run(
            "git",
            "config",
            "user.email",
            "eosv-test@example.invalid",
            cwd=root,
        )
        run(
            "git",
            "config",
            "user.name",
            "EOSV test",
            cwd=root,
        )
        run("git", "add", ".", cwd=root)
        run("git", "commit", "-qm", "fixture", cwd=root)

        module = load_module(root)

        wp = root / "engineering" / "work-packets" / "WP-TEST-0001.md"
        governing = (
            root
            / "engineering"
            / "increments"
            / "PI-TEST-001.md"
        )
        source = root / "src" / "lib.rs"

        # ------------------------------------------------------------------
        # Baseline non-execution fingerprint
        # ------------------------------------------------------------------

        initial, initial_payload = module.source_fingerprint(
            "WP-TEST-0001"
        )

        # Non-execution freshness must not depend on raw HEAD/baseline-diff
        # state. Those semantics belong only to execution-bound evidence.
        assert "baseline" not in initial_payload, initial_payload
        assert "workspace_hash" not in initial_payload, initial_payload
        assert "source_content_hash" in initial_payload, initial_payload

        # Identical source state must be deterministic.
        repeated, repeated_payload = module.source_fingerprint(
            "WP-TEST-0001"
        )
        assert repeated == initial
        assert repeated_payload == initial_payload

        # Directly guard the semantic hash primitive. Different semantic
        # documents must not collapse to the same digest.
        wp_semantic = module.semantic_file_hash(wp)
        governing_semantic = module.semantic_file_hash(governing)

        assert wp_semantic != governing_semantic, (
            "semantic_file_hash() collapsed distinct Markdown documents "
            "to the same digest"
        )

        # ------------------------------------------------------------------
        # Excluded control/projection changes must not stale evidence
        # ------------------------------------------------------------------

        (root / ".eos" / "evidence").mkdir(parents=True)
        (root / ".eos" / "evidence" / "new.json").write_text(
            '{"control": true}\n',
            encoding="utf-8",
        )

        (root / "machine").mkdir()
        (root / "machine" / "projection.json").write_text(
            '{"projection": true}\n',
            encoding="utf-8",
        )

        (root / "engineering" / "evidence").mkdir()
        (
            root
            / "engineering"
            / "evidence"
            / "result.md"
        ).write_text(
            "# Evidence\n",
            encoding="utf-8",
        )

        (root / "engineering" / "reviews").mkdir()
        (
            root
            / "engineering"
            / "reviews"
            / "review.md"
        ).write_text(
            "# Review\n",
            encoding="utf-8",
        )

        assert (
            module.source_fingerprint("WP-TEST-0001")[0]
            == initial
        )

        # ------------------------------------------------------------------
        # Visible **State:** lifecycle-only change must be ignored
        # ------------------------------------------------------------------

        wp_original = wp.read_text(encoding="utf-8")

        wp.write_text(
            wp_original
            .replace("status: IN_PROGRESS", "status: VERIFYING")
            .replace("updated: 2026-08-15", "updated: 2026-08-16")
            .replace(
                "**State:** IN_PROGRESS",
                "**State:** VERIFYING",
            ),
            encoding="utf-8",
        )

        assert (
            module.source_fingerprint("WP-TEST-0001")[0]
            == initial
        ), "visible State/frontmatter lifecycle changes changed freshness"

        # Commit the control/projection artifacts AND the lifecycle-only WP
        # mutation. HEAD must change without changing the source fingerprint.
        head_before_control_commit = git_head(root)

        run(
            "git",
            "add",
            ".eos",
            "machine",
            "engineering/evidence",
            "engineering/reviews",
            "engineering/work-packets/WP-TEST-0001.md",
            cwd=root,
        )
        run(
            "git",
            "commit",
            "-qm",
            "control and lifecycle-only commit",
            cwd=root,
        )

        head_after_control_commit = git_head(root)

        assert head_after_control_commit != head_before_control_commit
        assert (
            module.source_fingerprint("WP-TEST-0001")[0]
            == initial
        ), (
            "non-execution fingerprint changed solely because an "
            "excluded/control/lifecycle-only commit changed HEAD"
        )

        # ------------------------------------------------------------------
        # Visible **Status:** lifecycle-only change must also be ignored
        # ------------------------------------------------------------------

        governing_before_lifecycle = governing.read_text(
            encoding="utf-8"
        )

        governing.write_text(
            governing_before_lifecycle
            .replace("status: IN_PROGRESS", "status: VERIFYING")
            .replace("updated: 2026-08-15", "updated: 2026-08-16")
            .replace(
                "**Status:** IN_PROGRESS",
                "**Status:** VERIFYING",
            ),
            encoding="utf-8",
        )

        assert (
            module.source_fingerprint("WP-TEST-0001")[0]
            == initial
        ), "visible Status/frontmatter lifecycle changes changed freshness"

        # Commit the Status-only lifecycle change too. This independently
        # proves that another raw HEAD change does not stale evidence.
        head_before_status_commit = git_head(root)

        run(
            "git",
            "add",
            "engineering/increments/PI-TEST-001.md",
            cwd=root,
        )
        run(
            "git",
            "commit",
            "-qm",
            "governing lifecycle-only commit",
            cwd=root,
        )

        head_after_status_commit = git_head(root)

        assert head_after_status_commit != head_before_status_commit
        assert (
            module.source_fingerprint("WP-TEST-0001")[0]
            == initial
        ), (
            "non-execution fingerprint changed after a committed "
            "Status-only lifecycle transition"
        )

        # The current governing file is now the lifecycle-updated committed
        # form. Its semantic hash must still equal the original semantic hash.
        governing_lifecycle = governing.read_text(encoding="utf-8")

        assert (
            module.semantic_file_hash(governing)
            == governing_semantic
        ), "lifecycle-only Status changes altered semantic Markdown hash"

        # ------------------------------------------------------------------
        # Real implementation change MUST stale non-execution evidence
        # ------------------------------------------------------------------

        source_original = source.read_text(encoding="utf-8")

        source.write_text(
            "pub fn answer() -> u8 { 7 }\n",
            encoding="utf-8",
        )

        assert (
            module.source_fingerprint("WP-TEST-0001")[0]
            != initial
        ), "real implementation source change did not change freshness"

        # Restoring identical source content must restore the fingerprint.
        source.write_text(source_original, encoding="utf-8")

        assert (
            module.source_fingerprint("WP-TEST-0001")[0]
            == initial
        ), "restoring identical implementation content did not converge"

        # ------------------------------------------------------------------
        # Real governing semantic change MUST stale evidence
        # ------------------------------------------------------------------

        governing_semantic_before = module.semantic_file_hash(
            governing
        )

        governing.write_text(
            governing_lifecycle
            + "\nSemantic governing change.\n",
            encoding="utf-8",
        )

        governing_semantic_after = module.semantic_file_hash(
            governing
        )

        assert (
            governing_semantic_after
            != governing_semantic_before
        ), (
            "semantic_file_hash() failed to detect substantive "
            "governing Markdown content"
        )

        assert (
            module.source_fingerprint("WP-TEST-0001")[0]
            != initial
        ), (
            "substantive governing Markdown change did not change "
            "the non-execution fingerprint"
        )

        # Restoring the governing semantic content must converge again.
        governing.write_text(
            governing_lifecycle,
            encoding="utf-8",
        )

        assert (
            module.semantic_file_hash(governing)
            == governing_semantic_before
        )

        assert (
            module.source_fingerprint("WP-TEST-0001")[0]
            == initial
        ), "restoring governing content did not restore fingerprint"

        # ------------------------------------------------------------------
        # Execution-bound evidence must retain EOSE baseline semantics
        # ------------------------------------------------------------------

        baseline = git_head(root)

        write_tsv(
            root / ".eos" / "executions.tsv",
            [
                "id",
                "target",
                "worktree",
                "baseline_commit",
            ],
            [
                {
                    "id": "EXEC-TEST-0001",
                    "target": "WP-TEST-0001",
                    "worktree": str(root),
                    "baseline_commit": baseline,
                }
            ],
        )

        execution_initial, execution_payload = (
            module.source_fingerprint(
                "WP-TEST-0001",
                "EXEC-TEST-0001",
            )
        )

        assert execution_payload["baseline"] == baseline
        assert "workspace_hash" in execution_payload

        # Execution-bound fingerprints remain deterministic in the
        # unchanged execution source state.
        execution_repeated, execution_repeated_payload = (
            module.source_fingerprint(
                "WP-TEST-0001",
                "EXEC-TEST-0001",
            )
        )

        assert execution_repeated == execution_initial
        assert execution_repeated_payload == execution_payload

        # Execution-bound evidence audit must reconstruct the exact same
        # target/execution fingerprint pair used during capture.
        evidence_row = {field: "" for field in module.EVID_FIELDS}
        evidence_row.update(
            {
                "id": "EVID-TEST-0001",
                "target": "WP-TEST-0001",
                "execution": "EXEC-TEST-0001",
                "status": "VALIDATED",
                "source_hash": execution_initial,
            }
        )
        write_tsv(
            root / ".eos" / "evidence.tsv",
            module.EVID_FIELDS,
            [evidence_row],
        )
        audit, failures = module.audit_evidence(mutate=False)
        assert not failures, failures
        audited = next(
            row for row in audit if row["id"] == "EVID-TEST-0001"
        )
        assert "source fingerprint changed" not in audited["issues"], audited

        # EOSV machine projections are generated outputs, not execution
        # source. Rewriting and committing them after evidence capture must
        # not stale execution-bound evidence. This reproduces the real
        # capture -> machine sync -> commit sequence that blocked WP-MVP-0002.
        projection = root / "machine" / "projection.json"
        projection.write_text(
            '{"projection": "refreshed"}\n',
            encoding="utf-8",
        )
        run("git", "add", "machine/projection.json", cwd=root)
        run("git", "commit", "-qm", "machine projection refresh", cwd=root)

        execution_after_projection, projection_payload = (
            module.source_fingerprint(
                "WP-TEST-0001",
                "EXEC-TEST-0001",
            )
        )
        assert execution_after_projection == execution_initial, projection_payload

        projection_audit, failures = module.audit_evidence(mutate=False)
        assert not failures, failures
        projection_row = next(
            row for row in projection_audit if row["id"] == "EVID-TEST-0001"
        )
        assert (
            "source fingerprint changed" not in projection_row["issues"]
        ), projection_row

        # A depth-1 clone can lack the immutable execution baseline object.
        # Materialize the same untracked execution metadata and require the
        # same fingerprint without depending on local history availability.
        shallow = root.parent / f"{root.name}-shallow"
        run(
            "git",
            "clone",
            "--depth",
            "1",
            f"file://{root}",
            str(shallow),
            cwd=root.parent,
        )
        absent = subprocess.run(
            ["git", "cat-file", "-e", f"{baseline}^{{commit}}"],
            cwd=shallow,
            check=False,
            text=True,
            capture_output=True,
        )
        assert absent.returncode != 0
        write_tsv(
            shallow / ".eos" / "executions.tsv",
            ["id", "target", "worktree", "baseline_commit"],
            [{
                "id": "EXEC-TEST-0001",
                "target": "WP-TEST-0001",
                "worktree": "",
                "baseline_commit": baseline,
            }],
        )
        shallow_module = load_module(shallow)
        shallow_hash, shallow_payload = shallow_module.source_fingerprint(
            "WP-TEST-0001", "EXEC-TEST-0001"
        )
        assert shallow_hash == execution_initial, shallow_payload
        assert shallow_payload["baseline"] == baseline

        # Real execution-source drift must still be detected relative to
        # the immutable EOSE baseline.
        source.write_text(
            "pub fn answer() -> u8 { 99 }\n",
            encoding="utf-8",
        )

        execution_changed, execution_changed_payload = (
            module.source_fingerprint(
                "WP-TEST-0001",
                "EXEC-TEST-0001",
            )
        )

        assert execution_changed != execution_initial
        assert execution_changed_payload["baseline"] == baseline

        drift_audit, failures = module.audit_evidence(mutate=False)
        assert not failures, failures
        drifted = next(
            row for row in drift_audit if row["id"] == "EVID-TEST-0001"
        )
        assert "source fingerprint changed" in drifted["issues"], drifted

        # The immutable execution baseline itself must not move because the
        # working source changed.
        assert execution_changed_payload["baseline"] == (
            execution_payload["baseline"]
        )

    print(
        "PASS: EOSV non-execution freshness is content-stable "
        "and execution freshness remains baseline-bound"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
