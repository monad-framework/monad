#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("canonical_state.py")

REGISTRIES = {
    ".eos/program-increments.tsv":
        "id\tpath\ttitle\tstatus\tcreated\tupdated\tgithub_url\n"
        "PI-001\tengineering/increments/PI-001.md\tProgram Increment 001\tDRAFT\t"
        "2026-08-12T00:00:00Z\t2026-08-12T00:00:00Z\t\n",
    ".eos/work-cycles.tsv":
        "id\tpath\ttitle\tstatus\tpi\tcreated\tupdated\tgithub_url\n"
        "WC-0001\tengineering/work-cycles/WC-0001.md\tWork Cycle 0001\tDRAFT\tPI-001\t"
        "2026-08-12T00:00:00Z\t2026-08-12T00:00:00Z\t\n",
    ".eos/work-packets.tsv":
        "id\tpath\ttitle\tstatus\tpi\twc\tdomain\tcreated\tupdated\tgithub_url\n"
        "WP-0001\tengineering/work-packets/WP-0001.md\tFirst Work Packet\tDRAFT\tPI-001\t"
        "WC-0001\t\t2026-08-12T00:00:00Z\t2026-08-12T00:00:00Z\t\n",
    ".eos/change-requests.tsv":
        "id\tpath\ttarget\tsummary\tstatus\tcreated\tupdated\tgithub_url\n",
    ".eos/maintenance.tsv":
        "id\tpath\ttype\tsummary\tstatus\tcreated\tupdated\tgithub_url\n",
    ".eos/releases.tsv":
        "id\tpath\tversion\tstatus\tcreated\tupdated\tgithub_url\n",
}

class CanonicalStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for directory in (
            ".eos/state", ".eos/cache", "engineering/increments",
            "engineering/work-cycles", "engineering/work-packets",
        ):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        for path, content in REGISTRIES.items():
            (self.root / path).write_text(content, encoding="utf-8")
        (self.root / "engineering/increments/PI-001.md").write_text(
            "# PI-001\n\n**State:** DRAFT\n", encoding="utf-8"
        )
        (self.root / "engineering/work-cycles/WC-0001.md").write_text(
            "# WC-0001\n\n**State:** DRAFT\n", encoding="utf-8"
        )
        (self.root / "engineering/work-packets/WP-0001.md").write_text(
            "# WP-0001\n\n**State:** DRAFT\n", encoding="utf-8"
        )
        events = [
            {"event_type": "ENTITY_IMPORTED", "entity_kind": "PI", "target": "PI-001", "to_state": "DRAFT"},
            {"event_type": "ENTITY_IMPORTED", "entity_kind": "WC", "target": "WC-0001", "to_state": "DRAFT"},
            {"event_type": "ENTITY_IMPORTED", "entity_kind": "WP", "target": "WP-0001", "to_state": "DRAFT"},
        ]
        (self.root / ".eos/events.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events),
            encoding="utf-8",
        )
        os.environ["EOS_ROOT"] = str(self.root)
        spec = importlib.util.spec_from_file_location(
            f"canonical_state_test_{id(self)}", MODULE_PATH
        )
        assert spec and spec.loader
        self.cs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.cs)
        entities = {kind: {} for kind in self.cs.KINDS}
        for kind in self.cs.KINDS:
            for row in self.cs.read_tsv(self.root / self.cs.REGISTRY_PATHS[kind]):
                entities[kind][row["id"]] = self.cs.row_to_entity(
                    kind,
                    row,
                    origin="MIGRATION",
                    generation_method="test seed",
                )
        state = {
            "schema_version": "1.0.0",
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

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_clean_seed_has_no_drift(self) -> None:
        self.assertEqual([], self.cs.projection_drift(self.cs.load_state(), include_github_local=True))

    def test_direct_tsv_edit_is_detected(self) -> None:
        path = self.root / ".eos/program-increments.tsv"
        path.write_text(path.read_text().replace("\tDRAFT\t", "\tAUTHORIZED\t"), encoding="utf-8")
        failures = self.cs.projection_drift(self.cs.load_state())
        self.assertTrue(any("TSV projection drift" in item for item in failures))

    def test_direct_markdown_state_edit_is_detected(self) -> None:
        path = self.root / "engineering/increments/PI-001.md"
        path.write_text("# PI-001\n\n**Status:** Planned\n", encoding="utf-8")
        failures = self.cs.projection_drift(self.cs.load_state())
        self.assertTrue(any("Markdown lifecycle drift" in item for item in failures))

    def test_successful_transition_advances_canonical_state(self) -> None:
        args = argparse.Namespace(command=["authorize", "PI-001"])
        self.cs.cmd_pre(args)
        with (self.root / ".eos/events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "event_type": "STATE_TRANSITION",
                "entity_kind": "PI",
                "target": "PI-001",
                "from_state": "DRAFT",
                "to_state": "AUTHORIZED",
            }) + "\n")
        rows = self.cs.read_tsv(self.root / ".eos/program-increments.tsv")
        rows[0]["status"] = "AUTHORIZED"
        rows[0]["updated"] = "2026-08-12T12:30:00Z"
        (self.root / ".eos/program-increments.tsv").write_bytes(
            self.cs.render_tsv(self.cs.REGISTRY_FIELDS["PI"], rows)
        )
        self.cs.set_markdown_state(
            self.root / "engineering/increments/PI-001.md", "AUTHORIZED"
        )
        self.assertEqual(0, self.cs.cmd_post(args))
        state = self.cs.load_state()
        self.assertEqual(2, state["revision"])
        self.assertEqual("AUTHORIZED", state["entities"]["PI"]["PI-001"]["lifecycle_state"])
        self.assertEqual([], self.cs.projection_drift(state))

    def test_projection_repair_is_one_way_from_canonical(self) -> None:
        path = self.root / "engineering/increments/PI-001.md"
        path.write_text("# PI-001\n\n**State:** PLANNED\n", encoding="utf-8")
        self.assertEqual(0, self.cs.cmd_project(argparse.Namespace(apply=True)))
        self.assertIn("**State:** DRAFT", path.read_text(encoding="utf-8"))
        self.assertEqual([], self.cs.projection_drift(self.cs.load_state()))

if __name__ == "__main__":
    unittest.main()
