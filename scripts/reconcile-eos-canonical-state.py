#!/usr/bin/env python3
"""Reconcile accepted EOS lifecycle evidence into the canonical state snapshot.

This is intentionally narrower than generic projection-wins reconciliation. It may
advance `.eos/state/current.json` only when every lifecycle row agrees with both
the governed Markdown lifecycle field and the append-only event ledger. Existing
canonical entities may not disappear.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "eos" / "canonical_state.py"
EVIDENCE_PATH = "engineering/reviews/EOS-0.8-CANONICAL-STATE-RECONCILIATION.md"
GENERATION_METHOD = (
    "explicit evidence-consensus reconciliation from accepted TSV, Markdown, "
    "and append-only EOS event history"
)


def load_controller():
    spec = importlib.util.spec_from_file_location("eos_canonical_state", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def latest_event_timestamp(cs) -> str:
    stamps = [str(event.get("timestamp", "")) for event in cs.read_events()]
    stamps = [stamp for stamp in stamps if stamp]
    return max(stamps) if stamps else cs.now_iso()


def build_candidate(cs):
    old = cs.load_state()
    if cs.TRANSACTION_PATH.exists():
        raise cs.StateError(
            "Interrupted canonical-state transaction exists; remove/reconcile it before evidence reconciliation"
        )

    rows_by_kind = cs.rows_from_projections()
    failures = cs.validate_projection_rows_against_events(rows_by_kind)

    row_keys = {
        (kind, row.get("id", ""))
        for kind, rows in rows_by_kind.items()
        for row in rows
        if row.get("id")
    }
    event_keys = set(cs.projected_event_states())
    for kind, target in sorted(event_keys - row_keys):
        failures.append(
            f"event-history entity is absent from accepted TSV projection: {target} ({kind})"
        )

    old_entities = old.get("entities", {})
    for kind in cs.KINDS:
        accepted_ids = {row.get("id", "") for row in rows_by_kind[kind]}
        removed = set(old_entities.get(kind, {})) - accepted_ids
        if removed:
            failures.append(
                "evidence reconciliation cannot remove canonical entities: "
                + ", ".join(sorted(removed))
            )

    if failures:
        raise cs.StateError(
            "Accepted lifecycle evidence does not form a safe consensus:\n- "
            + "\n- ".join(failures)
        )

    new_entities: dict[str, dict[str, dict]] = {kind: {} for kind in cs.KINDS}
    changed_ids: list[str] = []
    for kind in cs.KINDS:
        prior_map = old_entities.get(kind, {})
        for row in rows_by_kind[kind]:
            prior = prior_map.get(row["id"])
            entity = cs.row_to_entity(
                kind,
                row,
                previous=prior,
                origin="MIGRATION",
                generation_method=GENERATION_METHOD,
            )
            if entity is not prior and entity.get("provenance"):
                refs = list(entity["provenance"].get("source_refs", []))
                if EVIDENCE_PATH not in refs:
                    refs.append(EVIDENCE_PATH)
                entity["provenance"]["source_refs"] = refs
                entity["provenance"]["created_by"] = "EOS evidence-consensus reconciler"
            new_entities[kind][row["id"]] = entity
            if prior != entity:
                changed_ids.append(row["id"])

    if not changed_ids:
        return old, old, []

    new_state = {
        "schema_version": cs.SCHEMA_VERSION,
        "model": cs.STATE_MODEL_ID,
        "revision": int(old.get("revision", 0)) + 1,
        "updated_at": latest_event_timestamp(cs),
        "entities": new_entities,
    }
    return old, new_state, changed_ids


def apply_candidate(cs, new_state: dict) -> None:
    cs.write_json_atomic(cs.CANONICAL_PATH, new_state)
    for kind in cs.KINDS:
        cs.write_bytes_atomic(ROOT / cs.REGISTRY_PATHS[kind], cs.expected_tsv(new_state, kind))

    old_manifest = cs.load_json(cs.PROJECTIONS_PATH) if cs.PROJECTIONS_PATH.exists() else {}
    receipts = old_manifest.get("github", {}).get("receipts", {})
    cs.write_json_atomic(cs.PROJECTIONS_PATH, cs.local_projection_snapshot(new_state, receipts))

    failures = cs.projection_drift(new_state)
    if failures:
        raise cs.StateError(
            "Reconciled canonical state did not converge with local evidence:\n- "
            + "\n- ".join(failures)
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile accepted EOS lifecycle evidence into canonical operational state"
    )
    parser.add_argument("--apply", action="store_true", help="write the reconciled canonical snapshot")
    args = parser.parse_args()

    cs = load_controller()
    try:
        old, candidate, changed_ids = build_candidate(cs)
        if not changed_ids:
            print(
                f"Canonical state already matches accepted lifecycle evidence at revision {old['revision']}."
            )
            return 0

        print(f"Evidence consensus: PASS ({len(changed_ids)} canonical entities change)")
        print(f"Canonical revision: {old['revision']} -> {candidate['revision']}")
        for target in changed_ids:
            print(f"  {target}")

        if not args.apply:
            print("Canonical state requires reconciliation. Re-run with --apply after review.")
            return 2

        apply_candidate(cs, candidate)
        print("Canonical state reconciled from accepted evidence consensus.")
        return 0
    except cs.StateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
