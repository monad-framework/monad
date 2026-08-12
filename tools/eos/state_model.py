#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EOS = ROOT / ".eos"
STATE = EOS / "state" / "canonical.json"
MODEL = EOS / "state-model.json"
DOMAIN = EOS / "domain-model.json"
EVENTS = EOS / "events.jsonl"
GITHUB_PROJECTION = EOS / "sync" / "github-projection.json"

REGISTRIES = {
    "PI": EOS / "program-increments.tsv",
    "WC": EOS / "work-cycles.tsv",
    "WP": EOS / "work-packets.tsv",
    "CR": EOS / "change-requests.tsv",
    "MNT": EOS / "maintenance.tsv",
    "REL": EOS / "releases.tsv",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def norm_state(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", value.strip().upper()).strip("_")


def entity_fingerprint(entity: dict) -> str:
    payload = json.dumps(entity, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def markdown_state(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    for pattern in (r"(?m)^\*\*(?:Status|State):\*\*\s*([^\n]+)", r"(?m)^status:\s*[\"']?([^\n\"']+)"):
        match = re.search(pattern, text, re.I)
        if match:
            return norm_state(match.group(1).rstrip().rstrip("  "))
    return None


def event_states() -> dict[str, str]:
    result: dict[str, str] = {}
    if not EVENTS.exists():
        return result
    for raw in EVENTS.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        event = json.loads(raw)
        target = event.get("target", "")
        if not target:
            continue
        if event.get("event_type") in {"ENTITY_CREATED", "ENTITY_IMPORTED", "STATE_TRANSITION"}:
            state = event.get("to_state", "")
            if state:
                result[target] = norm_state(state)
    return result


def parent_value(entity: dict, target_type: str) -> str:
    for relation in entity.get("relationships", []):
        if relation.get("type") == "BELONGS_TO" and relation.get("target_type") == target_type:
            return relation.get("target_id", "")
    return ""


def verify() -> list[str]:
    errors: list[str] = []
    state = load(STATE)
    domain = load(DOMAIN)
    policy = load(MODEL)
    if policy.get("canonical_operational_state") != ".eos/state/canonical.json":
        errors.append("state-model.json does not designate canonical.json as sole operational authority")
    entities = state.get("entities", {})
    event_projection = event_states()

    registry_rows: dict[str, dict[str, dict[str, str]]] = {}
    for kind, path in REGISTRIES.items():
        registry_rows[kind] = {row.get("id", ""): row for row in read_tsv(path)}

    for entity_id, entity in entities.items():
        if entity.get("id") != entity_id:
            errors.append(f"{entity_id}: map key and entity.id differ")
        kind = entity.get("entity_type", "")
        domain_entity = next((v for v in domain.get("entities", {}).values() if v.get("entity_type") == kind or v.get("name") == kind), None)
        if domain_entity and entity.get("lifecycle_state") not in domain_entity.get("lifecycle_states", []):
            errors.append(f"{entity_id}: lifecycle state is not allowed by domain model")
        if entity_id in event_projection and event_projection[entity_id] != entity.get("lifecycle_state"):
            errors.append(f"{entity_id}: event history projects {event_projection[entity_id]}, canonical state says {entity.get('lifecycle_state')}")

        if kind in REGISTRIES:
            row = registry_rows[kind].get(entity_id)
            if not row:
                errors.append(f"{entity_id}: missing TSV projection")
            else:
                expected = {
                    "status": entity.get("lifecycle_state", ""),
                    "path": entity.get("artifact_path", ""),
                    "title": entity.get("title", ""),
                }
                if kind in {"WC", "WP"}:
                    expected["pi"] = parent_value(entity, "PI")
                if kind == "WP":
                    expected["wc"] = parent_value(entity, "WC")
                for field, value in expected.items():
                    if row.get(field, "") != value:
                        errors.append(f"{entity_id}: TSV {field}={row.get(field, '')!r}, canonical={value!r}")

        artifact = ROOT / entity.get("artifact_path", "")
        visible_state = markdown_state(artifact)
        if visible_state is None:
            errors.append(f"{entity_id}: Markdown projection has no Status/State marker")
        elif visible_state != entity.get("lifecycle_state"):
            errors.append(f"{entity_id}: Markdown projects {visible_state}, canonical state says {entity.get('lifecycle_state')}")

    canonical_ids = set(entities)
    for kind, rows in registry_rows.items():
        for entity_id in rows:
            if entity_id and entity_id not in canonical_ids:
                errors.append(f"{entity_id}: exists in {REGISTRIES[kind].relative_to(ROOT)} but not canonical state")

    github = load(GITHUB_PROJECTION)
    for entity_id, projection in github.get("entities", {}).items():
        entity = entities.get(entity_id)
        if not entity:
            errors.append(f"{entity_id}: GitHub projection has no canonical entity")
            continue
        if projection.get("canonical_revision") != state.get("revision"):
            errors.append(f"{entity_id}: GitHub projection revision is stale")
        if projection.get("canonical_fingerprint") != entity_fingerprint(entity):
            errors.append(f"{entity_id}: GitHub projection fingerprint is stale")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the EOS single canonical operational state model")
    parser.add_argument("command", choices=["verify", "fingerprint"])
    args = parser.parse_args()
    if args.command == "fingerprint":
        state = load(STATE)
        for entity_id, entity in sorted(state.get("entities", {}).items()):
            print(f"{entity_id}\t{entity_fingerprint(entity)}")
        return 0
    errors = verify()
    if errors:
        print("EOS canonical-state drift detected:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("EOS canonical state and projections agree.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
