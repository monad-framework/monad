#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
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
            raise AssertionError("MNT-0003 implementation missing tools/eos/event_ledger.py")
        spec = importlib.util.spec_from_file_location("mnt0003_event_ledger", MODULE_PATH)
        assert spec and spec.loader
        cls.ledger = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.ledger)

    def git(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            text=True,
            capture_output=True,
            check=True,
        )

    def init_git_repo(self, root: Path) -> None:
        self.git(root, "init", "-q")
        self.git(root, "config", "user.email", "mnt0003-test@example.invalid")
        self.git(root, "config", "user.name", "MNT-0003 Test")
        (root / ".gitattributes").write_text(
            ".eos/events.jsonl merge=union\n",
            encoding="utf-8",
        )

    def write_git_ledger(self, root: Path, events: list[dict]) -> None:
        path = root / ".eos/events.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "".join(
                json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n"
                for item in events
            ),
            encoding="utf-8",
        )

    def test_repository_declares_union_merge_for_event_ledger(self):
        attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        lines = {
            line.strip()
            for line in attributes.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        self.assertIn(".eos/events.jsonl merge=union", lines)

    def test_missing_parent_event_fails_closed(self):
        parent = [
            event("EVT-A", target="WP-X", from_state="DRAFT", to_state="READY"),
            event("EVT-B", target="WP-Y", from_state="DRAFT", to_state="READY"),
        ]
        with self.assertRaises(self.ledger.EventLedgerError):
            self.ledger.validate_parent_superset([parent[0]], [parent])

    def test_inherited_event_payload_must_not_change(self):
        parent_event = event("EVT-A", target="WP-X", from_state="DRAFT", to_state="READY")
        changed = dict(parent_event)
        changed["to_state"] = "BLOCKED"
        with self.assertRaises(self.ledger.EventLedgerError):
            self.ledger.validate_parent_superset([changed], [[parent_event]])

    def test_conflicting_duplicate_event_id_fails_closed(self):
        first = event("EVT-A", target="WP-X", from_state="DRAFT", to_state="READY")
        second = dict(first)
        second["to_state"] = "BLOCKED"
        with self.assertRaises(self.ledger.EventLedgerError):
            self.ledger.validate_event_identity([first, second])

    def test_independent_divergent_entities_are_allowed(self):
        self.ledger.validate_divergent_history(
            [],
            [event("EVT-A", target="WP-X", from_state="DRAFT", to_state="READY")],
            [
                event(
                    "EVT-B",
                    target="MNT-Y",
                    entity_kind="MNT",
                    from_state="PLANNED",
                    to_state="IN_PROGRESS",
                )
            ],
        )

    def test_same_entity_divergent_lifecycle_fails_closed(self):
        base = [event("EVT-BASE", target="WP-X", event_type="ENTITY_CREATED", to_state="DRAFT")]
        left = base + [event("EVT-A", target="WP-X", from_state="DRAFT", to_state="READY")]
        right = base + [event("EVT-B", target="WP-X", from_state="DRAFT", to_state="BLOCKED")]
        with self.assertRaises(self.ledger.EventLedgerConflict):
            self.ledger.validate_divergent_history(base, left, right)

    def test_same_event_in_both_parents_is_not_a_conflict(self):
        shared = event("EVT-A", target="WP-X", from_state="DRAFT", to_state="READY")
        self.ledger.validate_divergent_history([], [shared], [shared])

    def test_jsonl_reader_preserves_event_identity(self):
        events = [
            event("EVT-A", target="WP-X", from_state="DRAFT", to_state="READY"),
            event("EVT-B", target="WP-Y", from_state="DRAFT", to_state="READY"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text(
                "".join(json.dumps(item, sort_keys=True) + "\n" for item in events),
                encoding="utf-8",
            )
            loaded = self.ledger.read_event_ledger(path)
        self.assertEqual(["EVT-A", "EVT-B"], [item["event_id"] for item in loaded])

    def test_identical_duplicate_event_payload_is_semantically_stable(self):
        shared = event("EVT-A", target="WP-X", from_state="DRAFT", to_state="READY")
        mapping = self.ledger.validate_event_identity([shared, dict(shared)])
        self.assertEqual(["EVT-A"], sorted(mapping))

    def test_missing_event_id_fails_closed(self):
        malformed = event("EVT-A", target="WP-X", from_state="DRAFT", to_state="READY")
        malformed.pop("event_id")
        with self.assertRaises(self.ledger.EventLedgerError):
            self.ledger.validate_event_identity([malformed])

    def test_real_git_union_merge_preserves_independent_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_git_repo(root)
            base = [
                event(
                    "EVT-BASE",
                    target="WP-BASE",
                    event_type="ENTITY_CREATED",
                    to_state="DRAFT",
                )
            ]
            self.write_git_ledger(root, base)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "base")
            base_sha = self.git(root, "rev-parse", "HEAD").stdout.strip()

            self.git(root, "checkout", "-qb", "left")
            left = base + [
                event("EVT-LEFT", target="WP-LEFT", from_state="DRAFT", to_state="READY")
            ]
            self.write_git_ledger(root, left)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "left")

            self.git(root, "checkout", "-qb", "right", base_sha)
            right = base + [
                event("EVT-RIGHT", target="WP-RIGHT", from_state="DRAFT", to_state="READY")
            ]
            self.write_git_ledger(root, right)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "right")
            self.git(root, "merge", "--no-edit", "left")

            merged = self.ledger.read_event_ledger(root / ".eos/events.jsonl")
            ids = {item["event_id"] for item in merged}
            self.assertIn("EVT-LEFT", ids)
            self.assertIn("EVT-RIGHT", ids)
            self.ledger.validate_committed_history(root)

    def test_committed_child_cannot_delete_parent_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_git_repo(root)
            events = [
                event("EVT-A", target="WP-A", from_state="DRAFT", to_state="READY"),
                event("EVT-B", target="WP-B", from_state="DRAFT", to_state="READY"),
            ]
            self.write_git_ledger(root, events)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "parent")

            self.write_git_ledger(root, [events[0]])
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "bad child")
            with self.assertRaises(self.ledger.EventLedgerError):
                self.ledger.validate_committed_history(root)

    def test_real_git_same_entity_divergence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_git_repo(root)
            base = [event("EVT-BASE", target="WP-X", event_type="ENTITY_CREATED", to_state="DRAFT")]
            self.write_git_ledger(root, base)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "base")
            base_sha = self.git(root, "rev-parse", "HEAD").stdout.strip()

            self.git(root, "checkout", "-qb", "left")
            left = base + [
                event("EVT-LEFT", target="WP-X", from_state="DRAFT", to_state="READY")
            ]
            self.write_git_ledger(root, left)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "left")

            self.git(root, "checkout", "-qb", "right", base_sha)
            right = base + [
                event("EVT-RIGHT", target="WP-X", from_state="DRAFT", to_state="BLOCKED")
            ]
            self.write_git_ledger(root, right)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "right")
            self.git(root, "merge", "--no-edit", "left")

            with self.assertRaises(self.ledger.EventLedgerConflict):
                self.ledger.validate_committed_history(root)


    def test_working_tree_cannot_delete_head_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_git_repo(root)
            events = [
                event("EVT-A", target="WP-A", from_state="DRAFT", to_state="READY"),
                event("EVT-B", target="WP-B", from_state="DRAFT", to_state="READY"),
            ]
            self.write_git_ledger(root, events)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "base")
            self.write_git_ledger(root, [events[0]])
            with self.assertRaises(self.ledger.EventLedgerError):
                self.ledger.validate_working_history(root)

    def test_working_merge_rejects_same_entity_divergence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_git_repo(root)
            base = [event("EVT-BASE", target="WP-X", event_type="ENTITY_CREATED", to_state="DRAFT")]
            self.write_git_ledger(root, base)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "base")
            base_sha = self.git(root, "rev-parse", "HEAD").stdout.strip()
            self.git(root, "checkout", "-qb", "left")
            self.write_git_ledger(
                root,
                base + [event("EVT-LEFT", target="WP-X", from_state="DRAFT", to_state="READY")],
            )
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "left")
            self.git(root, "checkout", "-qb", "right", base_sha)
            self.write_git_ledger(
                root,
                base + [event("EVT-RIGHT", target="WP-X", from_state="DRAFT", to_state="BLOCKED")],
            )
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "right")
            self.git(root, "merge", "--no-commit", "--no-ff", "left")
            with self.assertRaises(self.ledger.EventLedgerConflict):
                self.ledger.validate_working_history(root)

    def test_working_merge_accepts_independent_entities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_git_repo(root)
            base = [event("EVT-BASE", target="WP-BASE", event_type="ENTITY_CREATED", to_state="DRAFT")]
            self.write_git_ledger(root, base)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "base")
            base_sha = self.git(root, "rev-parse", "HEAD").stdout.strip()
            self.git(root, "checkout", "-qb", "left")
            self.write_git_ledger(
                root,
                base + [event("EVT-LEFT", target="WP-LEFT", from_state="DRAFT", to_state="READY")],
            )
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "left")
            self.git(root, "checkout", "-qb", "right", base_sha)
            self.write_git_ledger(
                root,
                base + [event("EVT-RIGHT", target="WP-RIGHT", from_state="DRAFT", to_state="READY")],
            )
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "right")
            self.git(root, "merge", "--no-commit", "--no-ff", "left")
            self.ledger.validate_working_history(root)


if __name__ == "__main__":
    unittest.main()
