#!/usr/bin/env python3
"""Verify or reconcile canonical EOS lifecycle states with operational state machines.

The canonical domain model/core schemas are normative. Operational PI/WC/WP
state machines may implement only states representable by that canonical model.
This tool therefore enforces a one-way compatibility invariant: every
operational state MUST exist in the canonical domain-model and core-schema
state sets. Canonical schemas may intentionally contain additional future
states not yet implemented by the operational CLI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EOS = ROOT / ".eos"
KINDS = ("PI", "WC", "WP")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_compact(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")


def ordered_union(existing: list[str], required: list[str]) -> list[str]:
    result = list(existing)
    seen = set(result)
    for value in required:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result


def sync_kind(kind: str, *, write: bool) -> list[str]:
    lower = kind.lower()
    machine_path = EOS / "state-machines" / f"{lower}.json"
    core_path = EOS / "schemas" / "core" / f"{lower}.schema.json"
    operational_schema_path = EOS / "schemas" / f"{lower}.schema.json"
    domain_path = EOS / "domain-model.json"

    machine = load(machine_path)
    core = load(core_path)
    operational_schema = load(operational_schema_path)
    domain = load(domain_path)

    operational_states = list(machine.get("states", []))
    domain_states = list(domain["entities"][kind].get("lifecycle_states", []))
    core_states = list(core["properties"]["lifecycle_state"].get("enum", []))

    problems: list[str] = []
    missing_domain = [state for state in operational_states if state not in domain_states]
    missing_core = [state for state in operational_states if state not in core_states]

    canonical_pattern = domain["identity"]["namespaces"][kind]
    entity_pattern = domain["entities"][kind]["id_pattern"]
    core_pattern = core["properties"]["id"]["pattern"]
    operational_pattern = operational_schema["properties"]["id"]["pattern"]
    patterns = {
        "domain namespace": canonical_pattern,
        "domain entity": entity_pattern,
        "core schema": core_pattern,
        "operational schema": operational_pattern,
    }
    if len(set(patterns.values())) != 1:
        problems.append(
            f"{kind}: identifier patterns disagree: "
            + "; ".join(f"{label}={value}" for label, value in patterns.items())
        )

    if missing_domain:
        problems.append(f"{kind}: canonical domain model missing operational states: {', '.join(missing_domain)}")
    if missing_core:
        problems.append(f"{kind}: canonical core schema missing operational states: {', '.join(missing_core)}")

    if write and (missing_domain or missing_core):
        domain["entities"][kind]["lifecycle_states"] = ordered_union(domain_states, operational_states)
        core["properties"]["lifecycle_state"]["enum"] = ordered_union(core_states, operational_states)
        write_compact(domain_path, domain)
        write_compact(core_path, core)
        # Problems repaired by this write are not reported as failures. Pattern
        # disagreement is intentionally never auto-repaired because identity
        # is a higher-risk canonical invariant.
        problems = [item for item in problems if "identifier patterns disagree" in item]

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Add missing operational states to canonical state sets")
    args = parser.parse_args()

    problems: list[str] = []
    for kind in KINDS:
        problems.extend(sync_kind(kind, write=args.write))

    if problems:
        print("EOS lifecycle-model consistency: FAIL", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1

    print("EOS lifecycle-model consistency: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
