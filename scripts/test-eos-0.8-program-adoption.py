#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EOS = ROOT / "scripts" / "eos"
MANIFEST = ".eos/adoptions/mvp-foundation.json"


class TestFailure(RuntimeError):
    pass


def run(*args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        [str(EOS), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != expect:
        raise TestFailure(
            f"{' '.join(args)} returned {proc.returncode}, expected {expect}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise TestFailure(f"{label}: expected {needle!r}\n{text}")


def git_diff() -> str:
    proc = subprocess.run(
        ["git", "diff", "--", ".eos", "engineering/increments", "engineering/work-cycles", "engineering/work-packets"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout


def main() -> int:
    try:
        status = run("status").stdout
        assert_contains(status, "EOSB bootstrap complete", "status bootstrap")
        assert_contains(status, "PI-MVP-001", "status PI")
        assert_contains(status, "WC-MVP-0001", "status WC")
        assert_contains(status, "WP-MVP-0001", "status WP")
        assert_contains(status, "PI-001", "status legacy PI preserved")
        assert_contains(status, "SUPERSEDED", "status legacy supersession")

        nxt = run("next").stdout
        assert_contains(nxt, "start authorized program increment PI-MVP-001", "next action")
        assert_contains(nxt, "./scripts/eos start PI-MVP-001", "next command")

        pi_machine = run("state-machine", "PI").stdout
        assert_contains(pi_machine, "SUPERSEDED", "PI state machine")
        wc_machine = run("state-machine", "WC").stdout
        assert_contains(wc_machine, "SUPERSEDED", "WC state machine")
        wp_machine = run("state-machine", "WP").stdout
        assert_contains(wp_machine, "SUPERSEDED", "WP state machine")

        wc_gate = run("gate", "explain", "WC_AUTHORIZE", "WC-MVP-0001").stdout
        assert_contains(wc_gate, "Result: PASS", "WC authorization gate")

        wp_gate = run("gate", "explain", "WP_AUTHORIZE", "WP-MVP-0001", expect=2)
        assert_contains(wp_gate.stdout, "Result: FAIL", "WP authorization gate must wait for WC")
        assert_contains(wp_gate.stdout, "parent WC-MVP-0001 is READY", "WP parent-state failure")

        before = git_diff()
        dry = run("adopt", MANIFEST).stdout
        assert_contains(dry, "DRY-RUN", "adoption dry-run")
        if git_diff() != before:
            raise TestFailure("dry-run adoption changed governed/control files")

        apply = run("adopt", MANIFEST, "--apply", "--by", "regression-test").stdout
        assert_contains(apply, "Imported 0 new lifecycle object(s)", "idempotent adoption")
        if git_diff() != before:
            raise TestFailure("idempotent adoption changed governed/control files")

        print("EOS 0.8 program-adoption regression checks: PASS")
        return 0
    except (TestFailure, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
