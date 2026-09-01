#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

CANONICAL_PATH = Path(__file__).with_name("canonical_state.py")
RECONCILE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "reconcile-eos-canonical-state.py"


class CanonicalReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for directory in (
            ".eos/state",
            ".eos/cache",
            "engineering/increments",
            "engineering/work-cycles",
            "engineering/work-packets",
            "engineering/reviews",
        ):
            (self.root / directory).mkdir(parents=True, exist_ok=True)

        os.environ["EOS_ROOT"] = str(self.root)
        self.cs = self._load_module(CANONICAL_PATH, f"canonical_state_reconcile_{id(self)}")
        self.reconcile = self._load_module(RECONCILE_PATH, f"reconcile_script_{id(self)}")

        self._write_registries(adopted=False)
        self._write_markdown(adopted=False)
        self._write_events(adopted=False)
        self._seed_canonical_revision_one()

    def tearDown(self) -> None:
        os.environ.pop("EOS_ROOT", None)
        self.temp.cleanup()

    @staticmethod
    def _load_module(path: Path, name: str):
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _write_registries(self, *, adopted: bool) -> None:
        legacy_state = "SUPERSEDED" if adopted else "DRAFT"
        legacy_updated = "2026-08-12T12:49:23Z" if adopted else "2026-08-12T00:00:00Z"
        pi = (
            "id\tpath\ttitle\tstatus\tcreated\tupdated\tgithub_url\n"
            f"PI-001\tengineering/increments/PI-001.md\tProgram Increment 001\t{legacy_state}\t"
            f"2026-08-12T00:00:00Z\t{legacy_updated}\t\n"
        )
        wc = (
            "id\tpath\ttitle\tstatus\tpi\tcreated\tupdated\tgithub_url\n"
            f"WC-0001\tengineering/work-cycles/WC-0001.md\tWork Cycle 0001\t{legacy_state}\tPI-001\t"
            f"2026-08-12T00:00:00Z\t{legacy_updated}\t\n"
        )
        wp = (
            "id\tpath\ttitle\tstatus\tpi\twc\tdomain\tcreated\tupdated\tgithub_url\n"
            f"WP-0001\tengineering/work-packets/WP-0001.md\tFirst Work Packet\t{legacy_state}\tPI-001\tWC-0001\t\t"
            f"2026-08-12T00:00:00Z\t{legacy_updated}\t\n"
        )
        if adopted:
            pi += (
                "PI-MVP-001\tengineering/increments/PI-MVP-001-SEMANTIC-FOUNDATION.md\tSemantic Foundation\t"
                "AUTHORIZED\t2026-08-12T00:00:00Z\t2026-08-12T00:00:00Z\t\n"
            )
            wc += (
                "WC-MVP-0001\tengineering/work-cycles/WC-MVP-0001.md\tWorkspace, Discovery, and Identity\t"
                "READY\tPI-MVP-001\t2026-08-12T00:00:00Z\t2026-08-12T00:00:00Z\t\n"
            )
            wp += (
                "WP-MVP-0001\tengineering/work-packets/WP-MVP-0001.md\tRepository identity and effective configuration\t"
                "READY\tPI-MVP-001\tWC-MVP-0001\tCORE\t2026-08-12T00:00:00Z\t2026-08-12T00:00:00Z\t\n"
            )
        payloads = {
            ".eos/program-increments.tsv": pi,
            ".eos/work-cycles.tsv": wc,
            ".eos/work-packets.tsv": wp,
            ".eos/change-requests.tsv": "id\tpath\ttarget\tsummary\tstatus\tcreated\tupdated\tgithub_url\n",
            ".eos/maintenance.tsv": "id\tpath\ttype\tsummary\tstatus\tcreated\tupdated\tgithub_url\n",
            ".eos/releases.tsv": "id\tpath\tversion\tstatus\tcreated\tupdated\tgithub_url\n",
        }
        for relpath, content in payloads.items():
            (self.root / relpath).write_text(content, encoding="utf-8")

    def _write_markdown(self, *, adopted: bool) -> None:
        legacy_state = "SUPERSEDED" if adopted else "DRAFT"
        for relpath, target in (
            ("engineering/increments/PI-001.md", "PI-001"),
            ("engineering/work-cycles/WC-0001.md", "WC-0001"),
            ("engineering/work-packets/WP-0001.md", "WP-0001"),
        ):
            (self.root / relpath).write_text(
                f"# {target}\n\n**State:** {legacy_state}\n", encoding="utf-8"
            )
        if adopted:
            for relpath, target, state in (
                ("engineering/increments/PI-MVP-001-SEMANTIC-FOUNDATION.md", "PI-MVP-001", "AUTHORIZED"),
                ("engineering/work-cycles/WC-MVP-0001.md", "WC-MVP-0001", "READY"),
                ("engineering/work-packets/WP-MVP-0001.md", "WP-MVP-0001", "READY"),
            ):
                (self.root / relpath).write_text(
                    f"# {target}\n\n**Status:** {state}\n", encoding="utf-8"
                )

    def _write_events(self, *, adopted: bool) -> None:
        events = [
            {"event_type": "ENTITY_IMPORTED", "entity_kind": "PI", "target": "PI-001", "to_state": "DRAFT", "timestamp": "2026-08-12T09:07:18Z"},
            {"event_type": "ENTITY_IMPORTED", "entity_kind": "WC", "target": "WC-0001", "to_state": "DRAFT", "timestamp": "2026-08-12T09:07:18Z"},
            {"event_type": "ENTITY_IMPORTED", "entity_kind": "WP", "target": "WP-0001", "to_state": "DRAFT", "timestamp": "2026-08-12T09:07:18Z"},
        ]
        if adopted:
            events.extend(
                [
                    {"event_type": "STATE_TRANSITION", "entity_kind": "PI", "target": "PI-001", "from_state": "DRAFT", "to_state": "SUPERSEDED", "timestamp": "2026-08-12T12:49:23Z"},
                    {"event_type": "STATE_TRANSITION", "entity_kind": "WC", "target": "WC-0001", "from_state": "DRAFT", "to_state": "SUPERSEDED", "timestamp": "2026-08-12T12:49:23Z"},
                    {"event_type": "STATE_TRANSITION", "entity_kind": "WP", "target": "WP-0001", "from_state": "DRAFT", "to_state": "SUPERSEDED", "timestamp": "2026-08-12T12:49:23Z"},
                    {"event_type": "ENTITY_IMPORTED", "entity_kind": "PI", "target": "PI-MVP-001", "to_state": "AUTHORIZED", "timestamp": "2026-08-12T12:49:23Z"},
                    {"event_type": "ENTITY_IMPORTED", "entity_kind": "WC", "target": "WC-MVP-0001", "to_state": "READY", "timestamp": "2026-08-12T12:49:23Z"},
                    {"event_type": "ENTITY_IMPORTED", "entity_kind": "WP", "target": "WP-MVP-0001", "to_state": "READY", "timestamp": "2026-08-12T12:49:23Z"},
                ]
            )
        (self.root / ".eos/events.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events), encoding="utf-8"
        )

    def _seed_canonical_revision_one(self) -> None:
        entities = {kind: {} for kind in self.cs.KINDS}
        for kind in self.cs.KINDS:
            for row in self.cs.read_tsv(self.root / self.cs.REGISTRY_PATHS[kind]):
                entities[kind][row["id"]] = self.cs.row_to_entity(
                    kind, row, origin="MIGRATION", generation_method="test seed"
                )
        state = {
            "schema_version": self.cs.SCHEMA_VERSION,
            "model": self.cs.STATE_MODEL_ID,
            "revision": 1,
            "updated_at": "2026-08-12T12:28:00Z",
            "entities": entities,
        }
        self.cs.write_json_atomic(self.root / ".eos/state/current.json", state)
        self.cs.write_json_atomic(
            self.root / ".eos/state/projections.json",
            self.cs.local_projection_snapshot(state, {}),
        )

    def _adopt_external_evidence(self) -> None:
        self._write_registries(adopted=True)
        self._write_markdown(adopted=True)
        self._write_events(adopted=True)

    def test_consensus_reconciliation_advances_revision_and_preserves_history(self) -> None:
        self._adopt_external_evidence()
        cs = self.reconcile.load_controller()
        old, candidate, changed = self.reconcile.build_candidate(cs)
        self.assertEqual(1, old["revision"])
        self.assertEqual(2, candidate["revision"])
        self.assertEqual(
            {"PI-001", "WC-0001", "WP-0001", "PI-MVP-001", "WC-MVP-0001", "WP-MVP-0001"},
            set(changed),
        )
        self.reconcile.apply_candidate(cs, candidate)
        state = cs.load_state()
        self.assertEqual("SUPERSEDED", state["entities"]["PI"]["PI-001"]["lifecycle_state"])
        self.assertEqual("SUPERSEDED", state["entities"]["WC"]["WC-0001"]["lifecycle_state"])
        self.assertEqual("SUPERSEDED", state["entities"]["WP"]["WP-0001"]["lifecycle_state"])
        self.assertEqual("AUTHORIZED", state["entities"]["PI"]["PI-MVP-001"]["lifecycle_state"])
        self.assertEqual("READY", state["entities"]["WC"]["WC-MVP-0001"]["lifecycle_state"])
        self.assertEqual("READY", state["entities"]["WP"]["WP-MVP-0001"]["lifecycle_state"])
        self.assertEqual([], cs.projection_drift(state))
        _, unchanged, changed_again = self.reconcile.build_candidate(cs)
        self.assertEqual(state, unchanged)
        self.assertEqual([], changed_again)

    def test_event_disagreement_fails_closed_without_advancing_canonical(self) -> None:
        self._adopt_external_evidence()
        events = (self.root / ".eos/events.jsonl").read_text(encoding="utf-8")
        events = events.replace('"target": "WP-MVP-0001", "to_state": "READY"', '"target": "WP-MVP-0001", "to_state": "AUTHORIZED"')
        (self.root / ".eos/events.jsonl").write_text(events, encoding="utf-8")
        cs = self.reconcile.load_controller()
        with self.assertRaises(cs.StateError):
            self.reconcile.build_candidate(cs)
        self.assertEqual(1, cs.load_state()["revision"])

    def test_reconciliation_cannot_remove_existing_canonical_entity(self) -> None:
        cs = self.reconcile.load_controller()
        path = self.root / ".eos/work-packets.tsv"
        lines = path.read_text(encoding="utf-8").splitlines()
        path.write_text(lines[0] + "\n", encoding="utf-8")
        with self.assertRaises(cs.StateError):
            self.reconcile.build_candidate(cs)
        self.assertEqual(1, cs.load_state()["revision"])


if __name__ == "__main__":
    unittest.main()
