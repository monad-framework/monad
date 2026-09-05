#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CORE = load_module("eos_identity_test_core", "tools/eos/eos.py")
EXECUTION = load_module(
    "eos_identity_test_execution",
    "tools/eos/execution_v2.py",
)
VERIFICATION = load_module(
    "eos_identity_test_verification",
    "tools/eos/verification_v2.py",
)

REQUIREMENT_IDS = (
    "REQ-FOO-0001",
    "FR-043",
    "QR-010",
)

SPECIFICATION_IDS = (
    "SPEC-CORE-0001",
    "FUN-AIENG-0001",
    "IFC-AIENG-0001",
    "SEC-AIENG-0001",
    "TECH-HARNESS-0001",
    "DATA-SOURCE-0001",
    "MKE-CORE-0001",
)

SPECIFICATION_FAMILIES = {
    "SPEC",
    "FUN",
    "IFC",
    "SEC",
    "TECH",
    "DATA",
    "MKE",
}


class IdentifierFamilyTests(unittest.TestCase):
    def test_core_extracts_native_requirement_and_specification_ids(self):
        text = " ".join(REQUIREMENT_IDS + SPECIFICATION_IDS)

        self.assertEqual(
            set(REQUIREMENT_IDS + SPECIFICATION_IDS),
            set(CORE.ID_RE.findall(text)),
        )

    def test_execution_context_extracts_native_ids(self):
        text = " ".join(REQUIREMENT_IDS + SPECIFICATION_IDS)

        self.assertEqual(
            set(REQUIREMENT_IDS + SPECIFICATION_IDS),
            set(EXECUTION.ID_RE.findall(text)),
        )

    def test_verification_context_extracts_native_ids(self):
        text = " ".join(REQUIREMENT_IDS + SPECIFICATION_IDS)

        self.assertEqual(
            set(REQUIREMENT_IDS + SPECIFICATION_IDS),
            set(VERIFICATION.ID_RE.findall(text)),
        )

    def test_family_patterns_reject_noncanonical_suffixes(self):
        invalid = (
            "FR-43",
            "FR-0043",
            "QR-10",
            "REQ-FOO",
            "REQ-FOO-V01",
            "FUN-AIENG-V01",
            "FUN-AIENG-V09",
            "IFC-AIENG-V02",
            "SEC-AIENG-V06",
            "DATA-SOURCE-0001-",
            "FUN-AIENG-0001-",
        )

        for identifier in invalid:
            with self.subTest(identifier=identifier):
                self.assertFalse(
                    CORE.is_requirement_id(identifier)
                    if identifier.startswith(
                        ("REQ-", "FR-", "QR-")
                    )
                    else CORE.is_specification_id(identifier)
                )

    def test_filename_separator_is_not_part_of_spec_identity(self):
        cases = {
            "DATA-SOURCE-0001-stable-source-document-identity.md":
                "DATA-SOURCE-0001",
            "FUN-AIENG-0001-adaptive-engineering-workflow.md":
                "FUN-AIENG-0001",
            "IFC-AIENG-0001-engineering-agent-contract.md":
                "IFC-AIENG-0001",
            "SEC-AIENG-0001-autonomy-authority-and-approval-gates.md":
                "SEC-AIENG-0001",
        }

        for filename, expected in cases.items():
            with self.subTest(filename=filename):
                match = CORE.ID_RE.search(
                    Path(filename).stem
                )
                self.assertIsNotNone(match)
                self.assertEqual(
                    expected,
                    match.group(0),
                )

    def test_verification_scenario_ids_are_not_specifications(self):
        for identifier in (
            "FUN-AIENG-V01",
            "FUN-AIENG-V09",
            "IFC-AIENG-V02",
            "IFC-AIENG-V10",
            "SEC-AIENG-V01",
            "SEC-AIENG-V11",
        ):
            with self.subTest(identifier=identifier):
                self.assertFalse(
                    CORE.is_specification_id(identifier)
                )
                self.assertIsNone(
                    CORE.ID_RE.fullmatch(identifier)
                )

    def test_native_requirement_edge_inference(self):
        self.assertEqual(
            "implements",
            CORE.infer_edge_type("WP-MVP-0005", "FR-043"),
        )
        self.assertEqual(
            "implements",
            CORE.infer_edge_type("WP-MVP-0005", "QR-010"),
        )

    def test_native_specification_edge_inference(self):
        for spec_id in SPECIFICATION_IDS:
            with self.subTest(spec_id=spec_id):
                self.assertEqual(
                    "satisfies",
                    CORE.infer_edge_type("WP-MVP-0005", spec_id),
                )

    def test_specification_to_native_requirement_inference(self):
        self.assertEqual(
            "satisfies",
            CORE.infer_edge_type("FUN-AIENG-0001", "FR-043"),
        )

    def test_requirement_schema_accepts_native_families(self):
        schema = json.loads(
            (
                ROOT
                / ".eos/schemas/core/requirement.schema.json"
            ).read_text()
        )
        pattern = schema["properties"]["id"]["pattern"]

        for identifier in REQUIREMENT_IDS:
            with self.subTest(identifier=identifier):
                self.assertIsNotNone(
                    re.fullmatch(pattern, identifier),
                    identifier,
                )

        self.assertIsNone(
            re.fullmatch(pattern, "BOGUS-043")
        )

    def test_specification_schema_accepts_native_families(self):
        schema = json.loads(
            (
                ROOT
                / ".eos/schemas/core/specification.schema.json"
            ).read_text()
        )
        pattern = schema["properties"]["id"]["pattern"]

        for identifier in SPECIFICATION_IDS:
            with self.subTest(identifier=identifier):
                self.assertIsNotNone(
                    re.fullmatch(pattern, identifier),
                    identifier,
                )

        self.assertIsNone(
            re.fullmatch(pattern, "BOGUS-CORE-0001")
        )

    def test_domain_model_declares_requirement_families(self):
        model = json.loads(
            (ROOT / ".eos/domain-model.json").read_text()
        )
        requirement = model["entities"]["REQ"]

        self.assertEqual(
            ["REQ", "FR", "QR"],
            requirement["id_families"],
        )

        for identifier in REQUIREMENT_IDS:
            self.assertIsNotNone(
                re.fullmatch(
                    requirement["id_pattern"],
                    identifier,
                )
            )

    def test_domain_model_declares_specification_families(self):
        model = json.loads(
            (ROOT / ".eos/domain-model.json").read_text()
        )
        specification = model["entities"]["SPEC"]

        self.assertEqual(
            ["SPEC", "FUN", "IFC", "SEC", "TECH", "DATA", "MKE"],
            specification["id_families"],
        )

        for identifier in SPECIFICATION_IDS:
            self.assertIsNotNone(
                re.fullmatch(
                    specification["id_pattern"],
                    identifier,
                )
            )

    def test_repository_has_no_unrecognized_established_spec_family(self):
        prefixes = set()

        # The repository's governed spec filename convention is
        # <CLASS>-<AREA>-NNNN-...
        filename_re = re.compile(
            r"^([A-Z][A-Z0-9]*)-[A-Z0-9][A-Z0-9-]*-\d{4}(?:-|\.md$)"
        )

        root = ROOT / "specifications"

        for path in root.rglob("*.md"):
            match = filename_re.match(path.name)
            if match:
                prefixes.add(match.group(1))

        unexpected = prefixes - SPECIFICATION_FAMILIES

        self.assertEqual(
            set(),
            unexpected,
            "additional established specification families found: "
            + ", ".join(sorted(unexpected)),
        )



class IdentifierFamilyBehaviorTests(unittest.TestCase):
    def test_subsystem_non_target_vocabularies_are_not_broadened(self):
        # Core already recognized CR/MNT; EOSE/EOSV did not.
        self.assertIsNotNone(CORE.ID_RE.fullmatch("CR-0003"))
        self.assertIsNotNone(CORE.ID_RE.fullmatch("MNT-0005"))

        self.assertIsNone(EXECUTION.ID_RE.fullmatch("CR-0003"))
        self.assertIsNone(EXECUTION.ID_RE.fullmatch("MNT-0005"))

        self.assertIsNone(VERIFICATION.ID_RE.fullmatch("CR-0003"))
        self.assertIsNone(VERIFICATION.ID_RE.fullmatch("MNT-0005"))

    def test_explicit_relationship_parser_accepts_native_ids(self):
        for target in (
            "FR-043",
            "QR-010",
            "FUN-AIENG-0001",
            "IFC-AIENG-0001",
            "SEC-AIENG-0001",
        ):
            with self.subTest(target=target):
                match = CORE.EXPLICIT_RELATION_RE.match(
                    f"- references: {target}"
                )
                self.assertIsNotNone(match)

    def test_specification_filename_resolves_to_native_source_id(self):
        cases = {
            "specifications/functional/"
            "FUN-AIENG-0001-adaptive-engineering-workflow.md":
                "FUN-AIENG-0001",

            "specifications/interfaces/"
            "IFC-AIENG-0001-engineering-agent-contract.md":
                "IFC-AIENG-0001",

            "specifications/security/"
            "SEC-AIENG-0001-autonomy-authority-and-approval-gates.md":
                "SEC-AIENG-0001",
        }

        for relative, expected in cases.items():
            with self.subTest(relative=relative):
                self.assertEqual(
                    expected,
                    CORE.source_id_for(ROOT / relative),
                )

    def test_trace_coverage_classifies_native_families(self):
        edges = [
            {
                "source_id": "FUN-AIENG-0001",
                "target_id": "FR-043",
                "edge_type": "satisfies",
                "source_path": "fun.md",
                "evidence": "test",
            },
            {
                "source_id": "IFC-AIENG-0001",
                "target_id": "FR-043",
                "edge_type": "satisfies",
                "source_path": "ifc.md",
                "evidence": "test",
            },
            {
                "source_id": "SEC-AIENG-0001",
                "target_id": "FR-043",
                "edge_type": "satisfies",
                "source_path": "sec.md",
                "evidence": "test",
            },
            {
                "source_id": "WP-MVP-0005",
                "target_id": "FUN-AIENG-0001",
                "edge_type": "satisfies",
                "source_path": "wp.md",
                "evidence": "test",
            },
        ]

        old_rebuild = CORE.rebuild_trace
        old_registry = CORE.registry

        try:
            CORE.rebuild_trace = lambda: edges

            def registry(kind):
                if kind == "WP":
                    return [{
                        "id": "WP-MVP-0005",
                        "status": "IN_PROGRESS",
                    }]
                return []

            CORE.registry = registry

            report = CORE.trace_coverage_report()

            self.assertEqual(1, report["requirements"])
            self.assertEqual(3, report["specifications"])
            self.assertEqual(1, report["work_packets"])
            self.assertEqual([], report["requirement_gaps"])
            self.assertEqual([], report["specification_gaps"])
            self.assertEqual([], report["work_packet_gaps"])
            self.assertEqual(100.0, report["score"])
        finally:
            CORE.rebuild_trace = old_rebuild
            CORE.registry = old_registry

    def test_impact_traversal_reaches_native_specifications(self):
        edges = [
            {
                "source_id": "FUN-AIENG-0001",
                "target_id": "FR-043",
                "edge_type": "satisfies",
                "source_path": "fun.md",
                "evidence": "test",
            },
            {
                "source_id": "IFC-AIENG-0001",
                "target_id": "FR-043",
                "edge_type": "satisfies",
                "source_path": "ifc.md",
                "evidence": "test",
            },
            {
                "source_id": "SEC-AIENG-0001",
                "target_id": "FR-043",
                "edge_type": "satisfies",
                "source_path": "sec.md",
                "evidence": "test",
            },
            {
                "source_id": "WP-MVP-0005",
                "target_id": "FUN-AIENG-0001",
                "edge_type": "satisfies",
                "source_path": "wp.md",
                "evidence": "test",
            },
        ]

        old_rebuild = CORE.rebuild_trace

        try:
            CORE.rebuild_trace = lambda: edges

            impacts = CORE.impacted_entities(
                "FR-043",
                transitive=True,
            )

            reached = {
                row["source_id"]
                for row in impacts
            }

            self.assertTrue(
                {
                    "FUN-AIENG-0001",
                    "IFC-AIENG-0001",
                    "SEC-AIENG-0001",
                    "WP-MVP-0005",
                }.issubset(reached)
            )
        finally:
            CORE.rebuild_trace = old_rebuild

    def test_evidence_links_accept_native_families(self):
        for identifier in (
            "REQ-FOO-0001",
            "FR-043",
            "QR-010",
            "SPEC-CORE-0001",
            "FUN-AIENG-0001",
            "IFC-AIENG-0001",
            "SEC-AIENG-0001",
            "TECH-HARNESS-0001",
            "DATA-SOURCE-0001",
            "MKE-CORE-0001",
        ):
            with self.subTest(identifier=identifier):
                self.assertTrue(
                    VERIFICATION.is_evidence_reference_id(
                        identifier
                    )
                )

        self.assertFalse(
            VERIFICATION.is_evidence_reference_id(
                "BOGUS-CORE-0001"
            )
        )

if __name__ == "__main__":
    unittest.main()
