#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = Path(__file__).with_name("event_ledger.py")


def event(
    event_id: str,
    *,
    target: str,
    entity_kind: str = "WP",
    event_type: str = "STATE_TRANSITION",
    from_state: str = "",
    to_state: str = "",
    timestamp: str = "2026-09-05T00:00:00Z",
) -> dict:
    return {
        "event_id": event_id,
        "schema_version": "1.0.0",
        "timestamp": timestamp,
        "event_type": event_type,
        "actor": "test",
        "target": target,
        "entity_kind": entity_kind,
        "action": "test",
        "from_state": from_state,
        "to_state": to_state,
        "reason": "test",
        "commit": "test",
        "metadata": {},
    }


class EventLedgerMergeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not MODULE_PATH.exists():
            raise AssertionError(
                "MNT-0003 implementation missing "
                "tools/eos/event_ledger.py"
            )

        spec = importlib.util.spec_from_file_location(
            "mnt0003_event_ledger",
            MODULE_PATH,
        )
        assert spec and spec.loader

        cls.ledger = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.ledger)

    def test_repository_declares_union_merge_for_event_ledger(self):
        attributes = (
            ROOT / ".gitattributes"
        ).read_text(encoding="utf-8")

        lines = {
            line.strip()
            for line in attributes.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }

        self.assertIn(
            ".eos/events.jsonl merge=union",
            lines,
        )

    def test_missing_parent_event_fails_closed(self):
        parent = [
            event(
                "EVT-A",
                target="WP-X",
                from_state="DRAFT",
                to_state="READY",
            ),
            event(
                "EVT-B",
                target="WP-Y",
                from_state="DRAFT",
                to_state="READY",
            ),
        ]

        result = [parent[0]]

        with self.assertRaises(
            self.ledger.EventLedgerError
        ):
            self.ledger.validate_parent_superset(
                result,
                [parent],
            )

    def test_inherited_event_payload_must_not_change(self):
        parent_event = event(
            "EVT-A",
            target="WP-X",
            from_state="DRAFT",
            to_state="READY",
        )

        changed = dict(parent_event)
        changed["to_state"] = "BLOCKED"

        with self.assertRaises(
            self.ledger.EventLedgerError
        ):
            self.ledger.validate_parent_superset(
                [changed],
                [[parent_event]],
            )

    def test_conflicting_duplicate_event_id_fails_closed(self):
        first = event(
            "EVT-A",
            target="WP-X",
            from_state="DRAFT",
            to_state="READY",
        )

        second = dict(first)
        second["to_state"] = "BLOCKED"

        with self.assertRaises(
            self.ledger.EventLedgerError
        ):
            self.ledger.validate_event_identity(
                [first, second]
            )

    def test_independent_divergent_entities_are_allowed(self):
        base = []

        left = [
            event(
                "EVT-A",
                target="WP-X",
                from_state="DRAFT",
                to_state="READY",
            )
        ]

        right = [
            event(
                "EVT-B",
                target="MNT-Y",
                entity_kind="MNT",
                from_state="PLANNED",
                to_state="IN_PROGRESS",
            )
        ]

        self.ledger.validate_divergent_history(
            base,
            left,
            right,
        )

    def test_same_entity_divergent_lifecycle_fails_closed(self):
        base = [
            event(
                "EVT-BASE",
                target="WP-X",
                event_type="ENTITY_CREATED",
                to_state="DRAFT",
            )
        ]

        left = base + [
            event(
                "EVT-A",
                target="WP-X",
                from_state="DRAFT",
                to_state="READY",
            )
        ]

        right = base + [
            event(
                "EVT-B",
                target="WP-X",
                from_state="DRAFT",
                to_state="BLOCKED",
            )
        ]

        with self.assertRaises(
            self.ledger.EventLedgerConflict
        ):
            self.ledger.validate_divergent_history(
                base,
                left,
                right,
            )

    def test_same_event_in_both_parents_is_not_a_conflict(self):
        base = []

        shared = event(
            "EVT-A",
            target="WP-X",
            from_state="DRAFT",
            to_state="READY",
        )

        self.ledger.validate_divergent_history(
            base,
            [shared],
            [shared],
        )

    def test_jsonl_reader_preserves_event_identity(self):
        events = [
            event(
                "EVT-A",
                target="WP-X",
                from_state="DRAFT",
                to_state="READY",
            ),
            event(
                "EVT-B",
                target="WP-Y",
                from_state="DRAFT",
                to_state="READY",
            ),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"

            path.write_text(
                "".join(
                    json.dumps(item, sort_keys=True) + "\n"
                    for item in events
                ),
                encoding="utf-8",
            )

            loaded = self.ledger.read_event_ledger(path)

        self.assertEqual(
            ["EVT-A", "EVT-B"],
            [item["event_id"] for item in loaded],
        )


if __name__ == "__main__":
    unittest.main()
