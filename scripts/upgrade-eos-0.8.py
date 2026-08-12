#!/usr/bin/env python3
"""Deterministically upgrade EOS 0.7 to 0.8 program-adoption semantics.

This migration is intentionally source-controlled and idempotent. It upgrades the
repository-local EOS implementation, schemas, and lifecycle state machines but
does not adopt a program by itself. Program adoption remains an explicit
`./scripts/eos adopt ... --apply` operation backed by a reviewed manifest.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools" / "eos" / "eos.py"
VERIFY = ROOT / "tools" / "eos" / "verification_v2.py"
VERSION = ROOT / ".eos" / "version.json"


class UpgradeError(RuntimeError):
    pass


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise UpgradeError(f"{label}: expected exactly one old pattern, found {count}")
    return text.replace(old, new, 1)


def replace_between(text: str, start: str, end: str, replacement: str, *, label: str) -> str:
    if replacement in text:
        return text
    start_pos = text.find(start)
    if start_pos < 0:
        raise UpgradeError(f"{label}: start marker not found")
    end_pos = text.find(end, start_pos)
    if end_pos < 0:
        raise UpgradeError(f"{label}: end marker not found")
    return text[:start_pos] + replacement + "\n\n" + text[end_pos:]


def patch_core(text: str) -> str:
    text = replace_once(
        text,
        '    r"PI-\\d{3}|"\n',
        '    r"PI(?:-[A-Z][A-Z0-9]*)?-\\d{3}|"\n',
        label="core ID_RE PI",
    )
    text = replace_once(
        text,
        '    r"WC-\\d{4}|"\n',
        '    r"WC(?:-[A-Z][A-Z0-9]*)?-\\d{4}|"\n',
        label="core ID_RE WC",
    )
    text = replace_once(
        text,
        '    if re.fullmatch(r"PI-\\d{3}", target):\n',
        '    if re.fullmatch(r"PI(?:-[A-Z][A-Z0-9]*)?-\\d{3}", target):\n',
        label="kind_for_id PI",
    )
    text = replace_once(
        text,
        '    if re.fullmatch(r"WC-\\d{4}", target):\n',
        '    if re.fullmatch(r"WC(?:-[A-Z][A-Z0-9]*)?-\\d{4}", target):\n',
        label="kind_for_id WC",
    )
    text = replace_once(
        text,
        '        if not re.fullmatch(r"PI-\\d{3}", args.pi):\n',
        '        if not re.fullmatch(r"PI(?:-[A-Z][A-Z0-9]*)?-\\d{3}", args.pi):\n',
        label="plan explicit PI",
    )
    text = replace_once(
        text,
        '            raise EosError("PI id must look like PI-002")\n',
        '            raise EosError("PI id must look like PI-002 or PI-MVP-002")\n',
        label="plan PI message",
    )

    old_state_line = '''def state_line(path: Path) -> str | None:\n    if not path.exists():\n        return None\n    for line in path.read_text(encoding="utf-8").splitlines():\n        if line.startswith("**State:**"):\n            return line.split(":", 1)[1].strip()\n    return None\n\n\ndef replace_state_line(path: Path, new_state: str) -> None:\n    text = path.read_text(encoding="utf-8")\n    lines = text.splitlines()\n    for i, line in enumerate(lines):\n        if line.startswith("**State:**"):\n            lines[i] = f"**State:** {new_state}"\n            path.write_text("\\n".join(lines) + "\\n", encoding="utf-8")\n            return\n    # No state line: insert after first heading.\n    for i, line in enumerate(lines):\n        if line.startswith("# "):\n            lines.insert(i + 1, "")\n            lines.insert(i + 2, f"**State:** {new_state}")\n            path.write_text("\\n".join(lines) + "\\n", encoding="utf-8")\n            return\n'''
    new_state_line = '''def state_line(path: Path) -> str | None:\n    if not path.exists():\n        return None\n    for line in path.read_text(encoding="utf-8").splitlines():\n        if line.startswith("**State:**") or line.startswith("**Status:**"):\n            return line.split(":", 1)[1].strip()\n    return None\n\n\ndef replace_state_line(path: Path, new_state: str) -> None:\n    text = path.read_text(encoding="utf-8")\n    lines = text.splitlines()\n    for i, line in enumerate(lines):\n        if line.startswith("**State:**") or line.startswith("**Status:**"):\n            label = "Status" if line.startswith("**Status:**") else "State"\n            lines[i] = f"**{label}:** {new_state}"\n            path.write_text("\\n".join(lines) + "\\n", encoding="utf-8")\n            return\n    # No lifecycle line: insert a canonical State line after the first heading.\n    for i, line in enumerate(lines):\n        if line.startswith("# "):\n            lines.insert(i + 1, "")\n            lines.insert(i + 2, f"**State:** {new_state}")\n            path.write_text("\\n".join(lines) + "\\n", encoding="utf-8")\n            return\n'''
    text = replace_once(text, old_state_line, new_state_line, label="status/state synchronization")

    latest_active = '''def latest_active(kind: str) -> dict[str, str] | None:\n    rows = registry(kind)\n    terminal = {"CLOSED", "RELEASED", "REJECTED", "WITHDRAWN", "SUPERSEDED"}\n    priority = {\n        "PI": ("ACTIVE", "AUTHORIZED", "IN_REVIEW", "PLANNED", "BLOCKED", "DRAFT"),\n        "WC": ("ACTIVE", "AUTHORIZED", "READY", "IN_REVIEW", "BLOCKED", "DRAFT"),\n        "WP": ("IN_PROGRESS", "AUTHORIZED", "READY", "VERIFYING", "IN_REVIEW", "BLOCKED", "DRAFT"),\n    }.get(kind, ())\n    for status in priority:\n        for row in rows:\n            if row.get("status") == status:\n                return row\n    for row in rows:\n        if row.get("status") not in terminal:\n            return row\n    return None\n'''
    text = replace_between(
        text,
        "def latest_active(kind: str) -> dict[str, str] | None:\n",
        "def cmd_layers(_: argparse.Namespace) -> None:\n",
        latest_active,
        label="latest_active",
    )

    adopt_function = r'''def _adoption_manifest(path_text: str) -> tuple[Path, dict]:
    path = (ROOT / path_text).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise EosError("adoption manifest must be inside the repository") from exc
    if not path.exists():
        raise EosError(f"Adoption manifest not found: {path_text}")
    doc = load_json(path)
    if doc.get("schema_version") != "1.0.0":
        raise EosError("Unsupported adoption manifest schema_version")
    if not doc.get("adoption_id"):
        raise EosError("Adoption manifest requires adoption_id")
    return path, doc


def _adoption_entities(doc: dict) -> list[tuple[str, dict[str, str]]]:
    sections = (
        ("PI", "program_increments"),
        ("WC", "work_cycles"),
        ("WP", "work_packets"),
    )
    entities: list[tuple[str, dict[str, str]]] = []
    seen: set[str] = set()
    for kind, section in sections:
        values = doc.get(section, [])
        if not isinstance(values, list):
            raise EosError(f"{section} must be an array")
        for raw in values:
            if not isinstance(raw, dict):
                raise EosError(f"{section} contains a non-object entry")
            row = {key: str(value) for key, value in raw.items()}
            target = row.get("id", "")
            if not target:
                raise EosError(f"{section} entry is missing id")
            if target in seen:
                raise EosError(f"duplicate adoption entity id: {target}")
            seen.add(target)
            if kind_for_id(target) != kind:
                raise EosError(f"{target} is not a valid {kind} identifier")
            path = ROOT / row.get("path", "")
            if not row.get("path") or not path.exists():
                raise EosError(f"{target} canonical path is missing: {row.get('path','')}")
            if row.get("status") not in valid_states(kind):
                raise EosError(f"{target} has invalid adoption state {row.get('status')}")
            entities.append((kind, row))
    return entities


def _validate_adoption(doc: dict, entities: list[tuple[str, dict[str, str]]]) -> None:
    evidence = doc.get("evidence", [])
    if not isinstance(evidence, list) or not evidence:
        raise EosError("adoption manifest requires at least one evidence path")
    for item in evidence:
        path = (ROOT / str(item)).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError as exc:
            raise EosError(f"adoption evidence must be inside repository: {item}") from exc
        if not path.exists():
            raise EosError(f"adoption evidence missing: {item}")

    imported_pi = {row["id"] for kind, row in entities if kind == "PI"}
    imported_wc = {row["id"] for kind, row in entities if kind == "WC"}
    known_pi = {row["id"] for row in registry("PI")} | imported_pi
    known_wc = {row["id"] for row in registry("WC")} | imported_wc
    for kind, row in entities:
        if kind == "WC" and row.get("pi") not in known_pi:
            raise EosError(f"{row['id']} references unknown parent PI {row.get('pi')}")
        if kind == "WP":
            if row.get("pi") not in known_pi:
                raise EosError(f"{row['id']} references unknown parent PI {row.get('pi')}")
            if row.get("wc") not in known_wc:
                raise EosError(f"{row['id']} references unknown parent WC {row.get('wc')}")
            parent = next(
                (candidate for k, candidate in entities if k == "WC" and candidate["id"] == row.get("wc")),
                find_row("WC", row.get("wc", "")),
            )
            if parent and parent.get("pi") != row.get("pi"):
                raise EosError(f"{row['id']} PI/WC parent mismatch")

    for target in doc.get("supersede", []):
        kind, _ = row_for_target(str(target))
        if "SUPERSEDED" not in valid_states(kind):
            raise EosError(f"{kind} state machine does not support SUPERSEDED")


def cmd_adopt(args: argparse.Namespace) -> None:
    manifest_path, doc = _adoption_manifest(args.manifest)
    entities = _adoption_entities(doc)
    _validate_adoption(doc, entities)
    actor = actor_name(args.by)
    reason = args.reason.strip() or str(doc.get("reason", "")).strip()
    if not reason:
        raise EosError("program adoption requires an explicit durable reason")

    print(f"Adoption: {doc['adoption_id']}")
    print(f"Manifest: {rel(manifest_path)}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    print(f"Entities: {len(entities)}")
    print(f"Supersede: {len(doc.get('supersede', []))}")
    if not args.apply:
        print("No EOS control state was changed. Re-run with --apply after review.")
        return

    stamp = now_iso()
    workflow = read_tsv(EOS / "workflow.tsv")
    workflow_changed = False
    if doc.get("bootstrap", {}).get("complete"):
        for row in workflow:
            if row.get("status") != "COMPLETE":
                row["status"] = "COMPLETE"
                row["completed_at"] = stamp
                workflow_changed = True
        if workflow_changed and workflow:
            write_tsv(EOS / "workflow.tsv", list(workflow[0].keys()), workflow)
            append_event(
                "BOOTSTRAP_RECONCILED",
                target=str(doc["adoption_id"]),
                action="adopt",
                actor=actor,
                reason=reason,
                metadata={
                    "manifest": rel(manifest_path),
                    "disposition": doc.get("bootstrap", {}).get("disposition", "complete"),
                    "evidence": doc.get("evidence", []),
                },
            )

    for target in doc.get("supersede", []):
        kind, row = row_for_target(str(target))
        if row.get("status") == "SUPERSEDED":
            continue
        set_lifecycle_state(
            str(target),
            "SUPERSEDED",
            action="adopt-supersede",
            actor=actor,
            reason=f"superseded by {doc['adoption_id']}: {reason}",
        )

    imported = 0
    for kind, row in entities:
        target = row["id"]
        existing = find_row(kind, target)
        if existing:
            immutable_fields = ["path"]
            if kind == "WC":
                immutable_fields.append("pi")
            elif kind == "WP":
                immutable_fields.extend(["pi", "wc"])
            mismatches = [field for field in immutable_fields if existing.get(field, "") != row.get(field, "")]
            if mismatches:
                raise EosError(
                    f"{target} already exists with conflicting adoption identity fields: {', '.join(mismatches)}"
                )
            continue
        normalized = {field: row.get(field, "") for field in REGISTRY_FIELDS[kind]}
        normalized["created"] = normalized.get("created") or stamp
        normalized["updated"] = normalized.get("updated") or stamp
        rows = registry(kind)
        rows.append(normalized)
        save_registry(kind, rows)
        sync_artifact_state(ROOT / normalized["path"], normalized["status"])
        append_event(
            "ENTITY_IMPORTED",
            target=target,
            entity_kind=kind,
            action="adopt",
            to_state=normalized["status"],
            actor=actor,
            reason=reason,
            metadata={"row": normalized, "adoption_id": doc["adoption_id"], "manifest": rel(manifest_path)},
        )
        imported += 1

    already_recorded = any(
        event.get("event_type") == "PROGRAM_ADOPTED"
        and event.get("target") == doc["adoption_id"]
        for event in read_events()
    )
    if not already_recorded:
        append_event(
            "PROGRAM_ADOPTED",
            target=str(doc["adoption_id"]),
            action="adopt",
            actor=actor,
            reason=reason,
            metadata={"manifest": rel(manifest_path), "evidence": doc.get("evidence", []), "imported": imported},
        )

    print(f"Imported {imported} new lifecycle object(s).")
    print("Adoption is idempotent: existing matching lifecycle objects were preserved without resetting state.")
'''
    if "def _adoption_manifest(" not in text:
        marker = "def cmd_prompt(args: argparse.Namespace) -> None:\n"
        pos = text.find(marker)
        if pos < 0:
            raise UpgradeError("adopt function insertion marker not found")
        text = text[:pos] + adopt_function + "\n\n" + text[pos:]

    cmd_next = r'''def cmd_next(_: argparse.Namespace) -> None:
    workflow = read_tsv(EOS / "workflow.tsv")
    row = next((r for r in workflow if r.get("status") != "COMPLETE"), None)
    if row:
        print(f"{row['stage']} — {row['phase']} — {row['primary_output']}")
        print(f"./scripts/eos prompt {row['stage']}")
        return

    pi = latest_active("PI")
    wc = latest_active("WC")
    wp = latest_active("WP")

    if pi:
        state = pi["status"]
        if state == "DRAFT":
            print(f"Permanent lifecycle: prepare {pi['id']} for planning readiness")
            print(f"./scripts/eos ready {pi['id']}")
            return
        if state == "PLANNED":
            print(f"Permanent lifecycle: review {pi['id']} for authorization")
            print(f"./scripts/eos review {pi['id']}")
            return
        if state == "IN_REVIEW":
            print(f"Permanent lifecycle: authorize {pi['id']} after accepted readiness evidence")
            print(f"./scripts/eos authorize {pi['id']}")
            return
        if state == "AUTHORIZED":
            print(f"Permanent lifecycle: start authorized program increment {pi['id']}")
            print(f"./scripts/eos start {pi['id']}")
            return
        if state == "BLOCKED":
            print(f"Permanent lifecycle: resolve blocker for {pi['id']}")
            print(f"./scripts/eos status")
            return

    if wc:
        state = wc["status"]
        if state == "DRAFT":
            print(f"Permanent lifecycle: prepare {wc['id']} for readiness")
            print(f"./scripts/eos ready {wc['id']}")
            return
        if state == "READY":
            print(f"Permanent lifecycle: authorize ready work cycle {wc['id']}")
            print(f"./scripts/eos authorize {wc['id']}")
            return
        if state == "AUTHORIZED":
            print(f"Permanent lifecycle: start authorized work cycle {wc['id']}")
            print(f"./scripts/eos start {wc['id']}")
            return
        if state == "BLOCKED":
            print(f"Permanent lifecycle: resolve blocker for {wc['id']}")
            print(f"./scripts/eos status")
            return

    if wp:
        state = wp["status"]
        if state == "DRAFT":
            print(f"Permanent lifecycle: refine/ready {wp['id']}")
            print(f"./scripts/eos ready {wp['id']}")
            return
        if state == "READY":
            print(f"Permanent lifecycle: authorize ready work packet {wp['id']}")
            print(f"./scripts/eos authorize {wp['id']}")
            return
        if state == "AUTHORIZED":
            print(f"Permanent lifecycle: start authorized work packet {wp['id']}")
            print(f"./scripts/eos start {wp['id']}")
            return
        if state == "IN_PROGRESS":
            print(f"Permanent lifecycle: execute bounded work for {wp['id']}")
            print(f"./scripts/eos codex {wp['id']}")
            return
        if state == "VERIFYING":
            print(f"Permanent lifecycle: verify {wp['id']}")
            print(f"./scripts/eos validate {wp['id']}")
            return
        if state == "IN_REVIEW":
            print(f"Permanent lifecycle: review/close {wp['id']} from accepted evidence")
            print(f"./scripts/eos review {wp['id']}")
            return
        if state == "BLOCKED":
            print(f"Permanent lifecycle: resolve blocker for {wp['id']}")
            print(f"./scripts/eos status")
            return

    if pi and pi.get("status") == "ACTIVE" and not wc:
        print(f"Permanent lifecycle: adopt/create the next work cycle for {pi['id']}")
        print(f"./scripts/eos create-wc --pi {pi['id']}")
    elif wc and wc.get("status") == "ACTIVE" and not wp:
        print(f"Permanent lifecycle: adopt/create the next work packet for {wc['id']}")
        print(f"./scripts/eos create-wp --wc {wc['id']}")
    else:
        print("Permanent lifecycle: plan or adopt the next program increment")
        print("./scripts/eos plan")
'''
    text = replace_between(
        text,
        "def cmd_next(_: argparse.Namespace) -> None:\n",
        "def cmd_prompt(args: argparse.Namespace) -> None:\n",
        cmd_next,
        label="cmd_next",
    )

    text = replace_once(
        text,
        '    "layers", "status", "next", "prompt", "complete", "reopen", "version",\n',
        '    "layers", "status", "next", "adopt", "prompt", "complete", "reopen", "version",\n',
        label="completion adopt command",
    )
    text = replace_once(
        text,
        '    "plan": ("--title", "--objective"),\n',
        '    "plan": ("--title", "--objective"),\n    "adopt": ("--apply", "--by", "--reason"),\n',
        label="completion adopt options",
    )
    parser_marker = '''    p = sub.add_parser("next", help="Show the next recommended lifecycle action")\n    p.set_defaults(func=cmd_next)\n\n'''
    parser_replacement = parser_marker + '''    p = sub.add_parser("adopt", help="Adopt an already-approved canonical program horizon into EOS control state")\n    p.add_argument("manifest")\n    p.add_argument("--apply", action="store_true", help="Apply the reviewed adoption manifest; default is dry-run")\n    p.add_argument("--by", default="", help="Human/authority actor recorded in adoption events")\n    p.add_argument("--reason", default="", help="Durable adoption reason; defaults to manifest reason")\n    p.set_defaults(func=cmd_adopt)\n\n'''
    text = replace_once(text, parser_marker, parser_replacement, label="adopt parser")
    return text


def patch_verification(text: str) -> str:
    old = '|PI-\\d{3}|WC-\\d{4}|WP(?:-[A-Z][A-Z0-9]*)?-\\d{4}|'
    new = '|PI(?:-[A-Z][A-Z0-9]*)?-\\d{3}|WC(?:-[A-Z][A-Z0-9]*)?-\\d{4}|WP(?:-[A-Z][A-Z0-9]*)?-\\d{4}|'
    return replace_once(text, old, new, label="EOSV ID_RE")


def update_schema(path: Path, kind: str) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    before = json.dumps(data, sort_keys=True)
    props = data["properties"]
    if kind == "PI":
        props["id"]["pattern"] = r"^PI(?:-[A-Z][A-Z0-9]*)?-[0-9]{3}$"
    elif kind == "WC":
        props["id"]["pattern"] = r"^WC(?:-[A-Z][A-Z0-9]*)?-[0-9]{4}$"
        props["pi"]["pattern"] = r"^PI(?:-[A-Z][A-Z0-9]*)?-[0-9]{3}$"
    elif kind == "WP":
        props["pi"]["pattern"] = r"^PI(?:-[A-Z][A-Z0-9]*)?-[0-9]{3}$"
        props["wc"]["pattern"] = r"^WC(?:-[A-Z][A-Z0-9]*)?-[0-9]{4}$"
    data["$id"] = f"eos://schemas/{kind.lower()}/1.2.0"
    after = json.dumps(data, sort_keys=True)
    if before == after:
        return False
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def update_state_machine(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    before = json.dumps(data, sort_keys=True)
    states = data.setdefault("states", [])
    if "SUPERSEDED" not in states:
        states.append("SUPERSEDED")
    terminals = data.setdefault("terminal_states", [])
    if "SUPERSEDED" not in terminals:
        terminals.append("SUPERSEDED")
    transitions = data.setdefault("transitions", {})
    for state in states:
        destinations = transitions.setdefault(state, [])
        if state not in {"CLOSED", "SUPERSEDED"} and "SUPERSEDED" not in destinations:
            destinations.append("SUPERSEDED")
    transitions["SUPERSEDED"] = []
    data["version"] = "1.2.0"
    after = json.dumps(data, sort_keys=True)
    if before == after:
        return False
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def run_upgrade(*, apply: bool) -> list[str]:
    changes: list[tuple[Path, str]] = []

    core_old = CORE.read_text(encoding="utf-8")
    core_new = patch_core(core_old)
    if core_new != core_old:
        changes.append((CORE, core_new))

    verify_old = VERIFY.read_text(encoding="utf-8")
    verify_new = patch_verification(verify_old)
    if verify_new != verify_old:
        changes.append((VERIFY, verify_new))

    touched = [path for path, _ in changes]
    if apply:
        for path, content in changes:
            path.write_text(content, encoding="utf-8")

    for kind in ("PI", "WC", "WP"):
        path = ROOT / ".eos" / "schemas" / f"{kind.lower()}.schema.json"
        original = path.read_text(encoding="utf-8")
        if apply:
            changed = update_schema(path, kind)
        else:
            # Evaluate on a temporary in-memory model without writing.
            data = json.loads(original)
            props = data["properties"]
            if kind == "PI":
                props["id"]["pattern"] = r"^PI(?:-[A-Z][A-Z0-9]*)?-[0-9]{3}$"
            elif kind == "WC":
                props["id"]["pattern"] = r"^WC(?:-[A-Z][A-Z0-9]*)?-[0-9]{4}$"
                props["pi"]["pattern"] = r"^PI(?:-[A-Z][A-Z0-9]*)?-[0-9]{3}$"
            else:
                props["pi"]["pattern"] = r"^PI(?:-[A-Z][A-Z0-9]*)?-[0-9]{3}$"
                props["wc"]["pattern"] = r"^WC(?:-[A-Z][A-Z0-9]*)?-[0-9]{4}$"
            data["$id"] = f"eos://schemas/{kind.lower()}/1.2.0"
            changed = json.dumps(data, indent=2) + "\n" != original
        if changed:
            touched.append(path)

    for kind in ("pi", "wc", "wp"):
        path = ROOT / ".eos" / "state-machines" / f"{kind}.json"
        original = path.read_text(encoding="utf-8")
        if apply:
            changed = update_state_machine(path)
        else:
            data = json.loads(original)
            states = data.setdefault("states", [])
            if "SUPERSEDED" not in states:
                states.append("SUPERSEDED")
            terminals = data.setdefault("terminal_states", [])
            if "SUPERSEDED" not in terminals:
                terminals.append("SUPERSEDED")
            transitions = data.setdefault("transitions", {})
            for state in states:
                destinations = transitions.setdefault(state, [])
                if state not in {"CLOSED", "SUPERSEDED"} and "SUPERSEDED" not in destinations:
                    destinations.append("SUPERSEDED")
            transitions["SUPERSEDED"] = []
            data["version"] = "1.2.0"
            changed = json.dumps(data, indent=2) + "\n" != original
        if changed:
            touched.append(path)

    versions = json.loads(VERSION.read_text(encoding="utf-8"))
    if versions.get("eos_tool_version") != "0.8.0" or versions.get("eos_schema_version") != "1.2.0" or versions.get("state_machine_version") != "1.2.0":
        touched.append(VERSION)
        if apply:
            versions["eos_tool_version"] = "0.8.0"
            versions["eos_schema_version"] = "1.2.0"
            versions["state_machine_version"] = "1.2.0"
            VERSION.write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")

    return sorted({path.relative_to(ROOT).as_posix() for path in touched})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        touched = run_upgrade(apply=args.apply)
    except UpgradeError as exc:
        print(f"ERROR: {exc}")
        return 2
    if args.apply:
        print(f"EOS 0.8 upgrade applied; changed files: {len(touched)}")
    else:
        print(f"EOS 0.8 upgrade check; files requiring migration: {len(touched)}")
    for path in touched:
        print(f"  {path}")
    return 0 if args.apply or not touched else 1


if __name__ == "__main__":
    raise SystemExit(main())
