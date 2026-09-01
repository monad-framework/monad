#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EOS = ROOT / ".eos"
MANIFEST_PATH = EOS / "adoptions" / "mvp-foundation.json"
STATE_PATH = EOS / "state" / "current.json"


class TestFailure(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TestFailure(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TestFailure(message)


def entity(state: dict, kind: str, target: str) -> dict:
    value = state.get("entities", {}).get(kind, {}).get(target)
    if not isinstance(value, dict):
        raise TestFailure(f"canonical state is missing adopted {kind} entity {target}")
    return value


def reachable(kind: str, start: str, current: str) -> bool:
    machine = load_json(EOS / "state-machines" / f"{kind.lower()}.json")
    transitions = machine.get("transitions", {})
    states = set(machine.get("states", []))
    if start not in states or current not in states:
        return False
    queue: deque[str] = deque([start])
    seen = {start}
    while queue:
        state = queue.popleft()
        if state == current:
            return True
        for nxt in transitions.get(state, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return False


def assert_adopted_progression(
    state: dict,
    manifest_rows: list[dict],
    kind: str,
) -> None:
    for row in manifest_rows:
        target = row["id"]
        baseline = row["status"]
        current = entity(state, kind, target).get("lifecycle_state", "")
        require(
            reachable(kind, baseline, current),
            f"{target} current state {current!r} is not legally reachable from adoption baseline {baseline!r}",
        )


def main() -> int:
    try:
        manifest = load_json(MANIFEST_PATH)
        state = load_json(STATE_PATH)

        require(
            manifest.get("adoption_id") == "ADOPT-MVP-FOUNDATION-2026-08-12",
            "unexpected MVP foundation adoption identifier",
        )
        bootstrap = manifest.get("bootstrap", {})
        require(bootstrap.get("complete") is True, "MVP adoption must record bootstrap complete")
        require(
            bootstrap.get("disposition") == "superseded-by-foundation-stabilization",
            "unexpected bootstrap adoption disposition",
        )

        expected_superseded = {"PI-001", "WC-0001", "WP-0001"}
        require(
            set(manifest.get("supersede", [])) == expected_superseded,
            "legacy supersession set changed",
        )
        for kind, target in (("PI", "PI-001"), ("WC", "WC-0001"), ("WP", "WP-0001")):
            require(
                entity(state, kind, target).get("lifecycle_state") == "SUPERSEDED",
                f"legacy lifecycle object {target} must remain SUPERSEDED",
            )

        pi_rows = manifest.get("program_increments", [])
        wc_rows = manifest.get("work_cycles", [])
        wp_rows = manifest.get("work_packets", [])
        require([row.get("id") for row in pi_rows] == ["PI-MVP-001"], "unexpected adopted PI set")
        require([row.get("id") for row in wc_rows] == ["WC-MVP-0001"], "unexpected adopted WC set")
        require([row.get("id") for row in wp_rows] == ["WP-MVP-0001"], "unexpected adopted WP set")

        assert_adopted_progression(state, pi_rows, "PI")
        assert_adopted_progression(state, wc_rows, "WC")
        assert_adopted_progression(state, wp_rows, "WP")

        require(
            entity(state, "WC", "WC-MVP-0001").get("operational_metadata", {}).get("pi") == "PI-MVP-001",
            "WC-MVP-0001 parent PI changed",
        )
        wp_metadata = entity(state, "WP", "WP-MVP-0001").get("operational_metadata", {})
        require(wp_metadata.get("pi") == "PI-MVP-001", "WP-MVP-0001 parent PI changed")
        require(wp_metadata.get("wc") == "WC-MVP-0001", "WP-MVP-0001 parent WC changed")

        for kind in ("PI", "WC", "WP"):
            machine = load_json(EOS / "state-machines" / f"{kind.lower()}.json")
            require("SUPERSEDED" in machine.get("states", []), f"{kind} state machine lost SUPERSEDED")
            require("SUPERSEDED" in machine.get("terminal_states", []), f"{kind} SUPERSEDED must remain terminal")

        print("EOS 0.8 program-adoption invariant checks: PASS")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TestFailure) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
