#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tools" / "eos" / "eos.py"


def replace_function(text: str, name: str, next_name: str, body: str) -> str:
    start = text.find(f"def {name}(")
    if start < 0:
        raise RuntimeError(f"missing function {name}")
    end = text.find(f"def {next_name}(", start)
    if end < 0:
        raise RuntimeError(f"missing following function {next_name}")
    return text[:start] + body.rstrip() + "\n\n\n" + text[end:]


LATEST_ACTIVE = '''def latest_active(kind: str) -> dict[str, str] | None:
    rows = registry(kind)
    terminal = {"CLOSED", "RELEASED", "REJECTED", "WITHDRAWN", "SUPERSEDED"}
    priority = {
        "PI": ("ACTIVE", "AUTHORIZED", "IN_REVIEW", "PLANNED", "BLOCKED", "DRAFT"),
        "WC": ("ACTIVE", "AUTHORIZED", "READY", "IN_REVIEW", "BLOCKED", "DRAFT"),
        # Finish already-started work before selecting pre-start work. This is
        # both a WIP-control rule and the least-surprising behavior for `next`.
        "WP": ("IN_PROGRESS", "VERIFYING", "IN_REVIEW", "AUTHORIZED", "READY", "BLOCKED", "DRAFT"),
    }.get(kind, ())
    for status in priority:
        for row in reversed(rows):
            if row.get("status") == status:
                return row
    for row in reversed(rows):
        if row.get("status") not in terminal:
            return row
    return None
'''


ADOPTION_ENTITIES = '''def _adoption_entities(doc: dict) -> list[tuple[str, dict[str, str]]]:
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

            path_text = row.get("path", "").strip()
            if not path_text:
                raise EosError(f"{target} canonical path is missing")
            candidate = Path(path_text)
            if candidate.is_absolute():
                raise EosError(f"{target} canonical path must be repository-relative: {path_text}")
            path = (ROOT / candidate).resolve()
            try:
                canonical_rel = path.relative_to(ROOT).as_posix()
            except ValueError as exc:
                raise EosError(f"{target} canonical path escapes repository: {path_text}") from exc
            if not path.exists():
                raise EosError(f"{target} canonical path is missing: {path_text}")
            # Resolving above also prevents an in-repository symlink from
            # smuggling an external path into sync_artifact_state().
            row["path"] = canonical_rel

            if row.get("status") not in valid_states(kind):
                raise EosError(f"{target} has invalid adoption state {row.get('status')}")

            normalized = {field: row.get(field, "") for field in REGISTRY_FIELDS[kind]}
            schema = load_json(SCHEMA_DIR / f"{kind.lower()}.schema.json")
            errors = validate_simple_schema(schema, normalized, label=f"adoption:{target}")
            if errors:
                raise EosError("Adoption entity schema validation failed:\n- " + "\n- ".join(errors))
            entities.append((kind, normalized))
    return entities
'''


VALIDATE_ADOPTION = '''def _validate_adoption(doc: dict, entities: list[tuple[str, dict[str, str]]]) -> None:
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

    entity_by_id = {row["id"]: (kind, row) for kind, row in entities}
    imported_pi = {row["id"] for kind, row in entities if kind == "PI"}
    imported_wc = {row["id"] for kind, row in entities if kind == "WC"}
    known_pi = {row["id"] for row in registry("PI")} | imported_pi
    known_wc = {row["id"] for row in registry("WC")} | imported_wc

    # Preflight every existing-entity conflict before any bootstrap, lifecycle,
    # registry, artifact, or event mutation can occur.
    for kind, row in entities:
        target = row["id"]
        existing = find_row(kind, target)
        if existing:
            immutable_fields = ["path"]
            if kind == "WC":
                immutable_fields.append("pi")
            elif kind == "WP":
                immutable_fields.extend(["pi", "wc"])
            mismatches = [
                field for field in immutable_fields
                if existing.get(field, "") != row.get(field, "")
            ]
            if mismatches:
                raise EosError(
                    f"{target} already exists with conflicting adoption identity fields: "
                    + ", ".join(mismatches)
                )

        if kind == "WC" and row.get("pi") not in known_pi:
            raise EosError(f"{target} references unknown parent PI {row.get('pi')}")
        if kind == "WP":
            if row.get("pi") not in known_pi:
                raise EosError(f"{target} references unknown parent PI {row.get('pi')}")
            if row.get("wc") not in known_wc:
                raise EosError(f"{target} references unknown parent WC {row.get('wc')}")
            parent = next(
                (candidate for k, candidate in entities if k == "WC" and candidate["id"] == row.get("wc")),
                find_row("WC", row.get("wc", "")),
            )
            if parent and parent.get("pi") != row.get("pi"):
                raise EosError(f"{target} PI/WC parent mismatch")

    supersede = [str(target) for target in doc.get("supersede", [])]
    if len(set(supersede)) != len(supersede):
        raise EosError("adoption supersede list contains duplicate targets")
    for target in supersede:
        if target in entity_by_id:
            raise EosError(f"adoption cannot both supersede and import {target}")
        kind, existing = row_for_target(target)
        if "SUPERSEDED" not in valid_states(kind):
            raise EosError(f"{kind} state machine does not support SUPERSEDED")
        current = existing.get("status", "")
        if current != "SUPERSEDED" and not transition_allowed(kind, current, "SUPERSEDED"):
            raise EosError(f"{target} cannot transition from {current} to SUPERSEDED")
'''


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    text = replace_function(text, "latest_active", "cmd_layers", LATEST_ACTIVE)
    text = replace_function(text, "_adoption_entities", "_validate_adoption", ADOPTION_ENTITIES)
    text = replace_function(text, "_validate_adoption", "cmd_adopt", VALIDATE_ADOPTION)
    TARGET.write_text(text, encoding="utf-8")
    print("Applied EOS 0.8 review corrections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
