#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable

UTC = dt.timezone.utc
SCHEMA_VERSION = "1.0.0"
STATE_MODEL_ID = "EOS-SINGLE-CANONICAL-STATE-1"
KINDS = ("PI", "WC", "WP", "CR", "MNT", "REL")
REGISTRY_FIELDS = {
    "PI": ["id", "path", "title", "status", "created", "updated", "github_url"],
    "WC": ["id", "path", "title", "status", "pi", "created", "updated", "github_url"],
    "WP": [
        "id", "path", "title", "status", "pi", "wc", "domain",
        "created", "updated", "github_url",
    ],
    "CR": ["id", "path", "target", "summary", "status", "created", "updated", "github_url"],
    "MNT": ["id", "path", "type", "summary", "status", "created", "updated", "github_url"],
    "REL": ["id", "path", "version", "status", "created", "updated", "github_url"],
}
REGISTRY_PATHS = {
    "PI": ".eos/program-increments.tsv",
    "WC": ".eos/work-cycles.tsv",
    "WP": ".eos/work-packets.tsv",
    "CR": ".eos/change-requests.tsv",
    "MNT": ".eos/maintenance.tsv",
    "REL": ".eos/releases.tsv",
}
MANAGED_GITHUB_LABELS = {
    "eos",
    "program-increment",
    "work-cycle",
    "work-packet",
    "change-request",
    "maintenance",
    "release",
    "authorized",
    "blocked",
}
KIND_LABEL = {
    "PI": "program-increment",
    "WC": "work-cycle",
    "WP": "work-packet",
    "CR": "change-request",
    "MNT": "maintenance",
    "REL": "release",
}

class StateError(RuntimeError):
    pass

def root() -> Path:
    explicit = os.environ.get("EOS_ROOT", "").strip()
    if explicit:
        return Path(explicit).resolve()
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            check=True,
        )
        return Path(proc.stdout.strip()).resolve()
    except Exception:
        return Path(__file__).resolve().parents[2]

ROOT = root()
EOS = ROOT / ".eos"
STATE_DIR = EOS / "state"
CANONICAL_PATH = STATE_DIR / "current.json"
PROJECTIONS_PATH = STATE_DIR / "projections.json"
TRANSACTION_PATH = EOS / "cache" / "canonical-state-transaction.json"
EVENTS_PATH = EOS / "events.jsonl"

def now_iso() -> str:
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def canonical_json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())

def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StateError(f"Missing canonical EOS state file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise StateError(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise StateError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value

def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(path)

def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))

def render_tsv(fields: list[str], rows: Iterable[dict[str, str]]) -> bytes:
    import io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fields})
    return buf.getvalue().encode("utf-8")

def write_bytes_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(payload)
    tmp.replace(path)

def normalize_state(value: str) -> str:
    return re.sub(r"[\s-]+", "_", value.strip()).upper()

def markdown_states(path: Path) -> dict[str, str]:
    if not path.exists():
        return {"visible": "", "frontmatter": ""}
    text = path.read_text(encoding="utf-8")
    visible = ""
    match = re.search(r"^\*\*(?:State|Status):\*\*\s*([A-Za-z0-9 _-]+?)\s{0,2}$", text, flags=re.M)
    if match:
        visible = normalize_state(match.group(1))
    frontmatter = ""
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end >= 0:
            header = text[4:end]
            match = re.search(r"^status:\s*[\"']?([^\"'\n]+)[\"']?\s*$", header, flags=re.M | re.I)
            if match:
                frontmatter = normalize_state(match.group(1))
    return {"visible": visible, "frontmatter": frontmatter}

def set_markdown_state(path: Path, state: str) -> None:
    if not path.exists():
        raise StateError(f"Cannot project state into missing Markdown artifact: {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    replacement = f"**State:** {state}"
    pattern = re.compile(r"^\*\*(?:State|Status):\*\*\s*[A-Za-z0-9 _-]+?\s{0,2}$", flags=re.M)
    if pattern.search(text):
        text = pattern.sub(replacement, text, count=1)
    else:
        lines = text.splitlines()
        insert_at = 1 if lines and lines[0].startswith("# ") else 0
        lines[insert_at:insert_at] = ["", replacement]
        text = "\n".join(lines) + ("\n" if not text.endswith("\n") else "")
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end >= 0:
            header = text[4:end]
            fm_pattern = re.compile(r"^status:\s*.*$", flags=re.M | re.I)
            if fm_pattern.search(header):
                header = fm_pattern.sub(f'status: "{state}"', header, count=1)
                text = "---\n" + header + text[end:]
    path.write_text(text, encoding="utf-8")

def semver_patch(value: str) -> str:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:[-+].*)?", value or "")
    if not match:
        return "1.0.0"
    return f"{match.group(1)}.{match.group(2)}.{int(match.group(3)) + 1}"

def entity_type(kind: str) -> str:
    return {
        "PI": "PI",
        "WC": "WC",
        "WP": "WP",
        "CR": "ChangeRequest",
        "MNT": "MaintenanceItem",
        "REL": "Release",
    }[kind]

def relationships_for(kind: str, row: dict[str, str]) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    if kind == "WC" and row.get("pi"):
        edges.append({"type": "BELONGS_TO", "target_id": row["pi"], "target_type": "PI"})
    if kind == "WP":
        if row.get("pi"):
            edges.append({"type": "BELONGS_TO", "target_id": row["pi"], "target_type": "PI"})
        if row.get("wc"):
            edges.append({"type": "BELONGS_TO", "target_id": row["wc"], "target_type": "WC"})
    if kind in {"CR", "MNT"} and row.get("target"):
        edges.append({"type": "AFFECTS", "target_id": row["target"]})
    return edges

def row_to_entity(
    kind: str,
    row: dict[str, str],
    *,
    previous: dict | None = None,
    origin: str = "AUTOMATION",
    generation_method: str = "EOS canonical-state capture",
) -> dict:
    row_copy = {field: row.get(field, "") for field in REGISTRY_FIELDS[kind]}
    state = normalize_state(row_copy.pop("status", ""))
    metadata = {key: value for key, value in row_copy.items() if key not in {"id", "created", "updated"}}
    previous_projection = previous.get("operational_metadata", {}) if previous else {}
    created = row.get("created") or (previous.get("created_at") if previous else "") or now_iso()
    updated = row.get("updated") or now_iso()
    relationships = relationships_for(kind, row)
    if previous and (
        previous.get("lifecycle_state") == state
        and previous_projection == metadata
        and previous.get("created_at") == created
        and previous.get("updated_at") == updated
        and previous.get("relationships", []) == relationships
    ):
        return previous
    version = semver_patch(previous.get("version", "1.0.0")) if previous else "1.0.0"
    return {
        "id": row["id"],
        "entity_type": entity_type(kind),
        "schema_version": "2.0.0",
        "version": version,
        "lifecycle_state": state,
        "created_at": created,
        "updated_at": updated,
        "relationships": relationships,
        "authority_level": "L3_BINDING",
        "provenance": {
            "origin": origin,
            "created_by": "EOS canonical-state adapter",
            "source_refs": [
                REGISTRY_PATHS[kind],
                row.get("path", ""),
                ".eos/events.jsonl",
            ],
            "generation_method": generation_method,
        },
        "kind": kind,
        "operational_metadata": metadata,
    }

def entity_to_row(kind: str, entity: dict) -> dict[str, str]:
    metadata = dict(entity.get("operational_metadata", {}))
    row = {
        "id": entity["id"],
        "status": entity["lifecycle_state"],
        "created": entity.get("created_at", ""),
        "updated": entity.get("updated_at", ""),
        **metadata,
    }
    return {field: str(row.get(field, "")) for field in REGISTRY_FIELDS[kind]}

def state_entities(state: dict, kind: str) -> list[dict]:
    values = state.get("entities", {}).get(kind, {})
    if not isinstance(values, dict):
        raise StateError(f"Canonical entities.{kind} must be an object")
    return [values[key] for key in sorted(values)]

def canonical_rows(state: dict, kind: str) -> list[dict[str, str]]:
    return [entity_to_row(kind, entity) for entity in state_entities(state, kind)]

def canonical_core(state: dict) -> dict:
    return {
        "schema_version": state.get("schema_version"),
        "model": state.get("model"),
        "revision": state.get("revision"),
        "entities": state.get("entities", {}),
    }

def canonical_digest(state: dict) -> str:
    return sha256_bytes(canonical_json_bytes(canonical_core(state)))

def read_events() -> list[dict]:
    if not EVENTS_PATH.exists():
        return []
    out = []
    for lineno, raw in enumerate(EVENTS_PATH.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise StateError(f"Malformed event ledger line {lineno}: {exc}") from exc
        if not isinstance(item, dict):
            raise StateError(f"Malformed event ledger line {lineno}: expected object")
        out.append(item)
    return out

def projected_event_states() -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for event in read_events():
        kind = event.get("entity_kind", "")
        target = event.get("target", "")
        if kind not in KINDS or not target:
            continue
        if event.get("event_type") in {"ENTITY_CREATED", "ENTITY_IMPORTED"}:
            value = event.get("to_state") or event.get("metadata", {}).get("row", {}).get("status", "")
            if value:
                result[(kind, target)] = normalize_state(value)
        elif event.get("event_type") == "STATE_TRANSITION":
            value = event.get("to_state", "")
            if value:
                result[(kind, target)] = normalize_state(value)
    return result

def projection_policy() -> dict:
    return {
        "canonical": {
            "path": ".eos/state/current.json",
            "role": "SOLE_OPERATIONAL_AUTHORITY",
            "write_policy": "EOS_TRANSACTION_ONLY",
        },
        "event_ledger": {
            "path": ".eos/events.jsonl",
            "role": "APPEND_ONLY_MUTATION_HISTORY",
            "canonical_current_state": False,
        },
        "tsv": {
            "role": "GENERATED_COMPATIBILITY_PROJECTION",
            "write_policy": "READ_ONLY_OUTSIDE_EOS",
            "drift_policy": "FAIL_CLOSED",
        },
        "markdown": {
            "role": "HUMAN_READABLE_GOVERNED_ARTIFACT",
            "lifecycle_fields": "PROJECTION_OF_CANONICAL_STATE",
            "content_authority": "GOVERNED_HUMAN_ARTIFACT",
            "drift_policy": "FAIL_CLOSED_FOR_LIFECYCLE_METADATA",
        },
        "git": {
            "role": "VERSION_HISTORY_AND_INTEGRITY_LEDGER",
            "canonical_current_state": False,
        },
        "github": {
            "role": "SYNCHRONIZED_COLLABORATION_PROJECTION",
            "write_back_policy": "NEVER_IMPLICIT",
            "external_edits": "DRIFT_UNTIL_EXPLICIT_RECONCILIATION",
        },
    }

def load_state() -> dict:
    state = load_json(CANONICAL_PATH)
    if state.get("schema_version") != SCHEMA_VERSION:
        raise StateError(
            f"Unsupported canonical state schema {state.get('schema_version')!r}; expected {SCHEMA_VERSION}"
        )
    if state.get("model") != STATE_MODEL_ID:
        raise StateError(f"Unexpected canonical state model {state.get('model')!r}")
    return state

def expected_tsv(state: dict, kind: str) -> bytes:
    return render_tsv(REGISTRY_FIELDS[kind], canonical_rows(state, kind))

def markdown_fingerprint(path: Path, expected_state: str) -> str:
    observed = markdown_states(path)
    payload = {
        "path": path.relative_to(ROOT).as_posix(),
        "expected": normalize_state(expected_state),
        "visible": observed["visible"],
        "frontmatter": observed["frontmatter"],
    }
    return sha256_bytes(canonical_json_bytes(payload))

def local_projection_snapshot(state: dict, github_receipts: dict | None = None) -> dict:
    tsv = {}
    markdown = {}
    for kind in KINDS:
        path = ROOT / REGISTRY_PATHS[kind]
        expected = expected_tsv(state, kind)
        tsv[REGISTRY_PATHS[kind]] = {
            "canonical_revision": state["revision"],
            "expected_sha256": sha256_bytes(expected),
            "actual_sha256": sha256_file(path) if path.exists() else "",
        }
        for entity in state_entities(state, kind):
            row = entity_to_row(kind, entity)
            relpath = row.get("path", "")
            if not relpath:
                continue
            md_path = ROOT / relpath
            markdown[entity["id"]] = {
                "path": relpath,
                "canonical_revision": state["revision"],
                "state_fingerprint": markdown_fingerprint(md_path, entity["lifecycle_state"])
                if md_path.exists() else "",
            }
    return {
        "schema_version": SCHEMA_VERSION,
        "canonical_revision": state["revision"],
        "canonical_digest": canonical_digest(state),
        "policy": projection_policy(),
        "tsv": tsv,
        "markdown": markdown,
        "github": {
            "receipts": github_receipts or {},
            "network_verification": "ON_DEMAND",
        },
    }

def projection_drift(
    state: dict, *, check_manifest: bool = True, include_github_local: bool = False
) -> list[str]:
    failures: list[str] = []
    for kind in KINDS:
        path = ROOT / REGISTRY_PATHS[kind]
        expected = expected_tsv(state, kind)
        if not path.exists():
            failures.append(f"missing TSV projection: {REGISTRY_PATHS[kind]}")
        elif path.read_bytes() != expected:
            failures.append(
                f"TSV projection drift: {REGISTRY_PATHS[kind]} differs from canonical revision {state['revision']}"
            )
        for entity in state_entities(state, kind):
            row = entity_to_row(kind, entity)
            relpath = row.get("path", "")
            if not relpath:
                failures.append(f"{entity['id']} canonical metadata has no governed artifact path")
                continue
            path = ROOT / relpath
            if not path.exists():
                failures.append(f"{entity['id']} Markdown projection missing: {relpath}")
                continue
            observed = markdown_states(path)
            expected_state = normalize_state(entity["lifecycle_state"])
            if not observed["visible"]:
                failures.append(f"{entity['id']} Markdown projection has no visible State/Status field: {relpath}")
            elif observed["visible"] != expected_state:
                failures.append(
                    f"{entity['id']} Markdown lifecycle drift: canonical={expected_state} markdown={observed['visible']}"
                )
            if observed["frontmatter"] and observed["frontmatter"] != expected_state:
                failures.append(
                    f"{entity['id']} frontmatter lifecycle drift: canonical={expected_state} frontmatter={observed['frontmatter']}"
                )

    event_states = projected_event_states()
    canonical_keys: set[tuple[str, str]] = set()
    for kind in KINDS:
        for entity in state_entities(state, kind):
            key = (kind, entity["id"])
            canonical_keys.add(key)
            actual = event_states.get(key)
            expected = normalize_state(entity["lifecycle_state"])
            if actual is None:
                failures.append(f"{entity['id']} has no reconstructable lifecycle state in event history")
            elif actual != expected:
                failures.append(
                    f"{entity['id']} event-history drift: canonical={expected} event-history={actual}"
                )
    for key in sorted(set(event_states) - canonical_keys):
        failures.append(f"event history contains unmanaged lifecycle entity {key[1]} ({key[0]})")

    if check_manifest:
        if not PROJECTIONS_PATH.exists():
            failures.append("missing projection manifest: .eos/state/projections.json")
        else:
            manifest = load_json(PROJECTIONS_PATH)
            if manifest.get("canonical_revision") != state.get("revision"):
                failures.append(
                    "projection manifest canonical revision does not match .eos/state/current.json"
                )
            if manifest.get("canonical_digest") != canonical_digest(state):
                failures.append(
                    "projection manifest canonical digest does not match .eos/state/current.json"
                )
    if include_github_local:
        failures.extend(github_local_drift(state))
    return failures

def github_local_drift(state: dict) -> list[str]:
    if not PROJECTIONS_PATH.exists():
        return ["missing projection manifest: .eos/state/projections.json"]
    manifest = load_json(PROJECTIONS_PATH)
    receipts = manifest.get("github", {}).get("receipts", {})
    failures: list[str] = []
    for kind in KINDS:
        for entity in state_entities(state, kind):
            row = entity_to_row(kind, entity)
            url = row.get("github_url", "")
            if not url:
                continue
            receipt = receipts.get(entity["id"])
            if not receipt:
                failures.append(
                    f"{entity['id']} GitHub projection has no synchronization receipt"
                )
                continue
            if receipt.get("url") != url:
                failures.append(
                    f"{entity['id']} GitHub projection URL differs from its synchronization receipt"
                )
            expected = expected_github_projection(kind, entity)
            if github_receipt_digest(expected) != receipt.get("expected_digest"):
                failures.append(
                    f"{entity['id']} GitHub projection is stale relative to canonical/Markdown state"
                )
    return failures

def assert_clean(
    state: dict, *, check_manifest: bool = True, include_github_local: bool = False
) -> None:
    failures = projection_drift(
        state,
        check_manifest=check_manifest,
        include_github_local=include_github_local,
    )
    if failures:
        raise StateError(
            "EOS canonical-state drift detected; refusing to continue:\n- "
            + "\n- ".join(failures)
            + "\nUse `./scripts/eos state status` and an explicit `state reconcile` operation."
        )

def event_count() -> int:
    return len(read_events())

def save_transaction(command: list[str], state: dict) -> None:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "started_at": now_iso(),
        "canonical_revision": state["revision"],
        "canonical_digest": canonical_digest(state),
        "event_count": event_count(),
        "command": command,
    }
    write_json_atomic(TRANSACTION_PATH, payload)

def load_transaction() -> dict:
    return load_json(TRANSACTION_PATH)

def remove_transaction() -> None:
    try:
        TRANSACTION_PATH.unlink()
    except FileNotFoundError:
        pass

def rows_from_projections() -> dict[str, list[dict[str, str]]]:
    return {kind: read_tsv(ROOT / REGISTRY_PATHS[kind]) for kind in KINDS}

def validate_projection_rows_against_events(rows_by_kind: dict[str, list[dict[str, str]]]) -> list[str]:
    failures: list[str] = []
    event_states = projected_event_states()
    for kind, rows in rows_by_kind.items():
        ids: set[str] = set()
        for row in rows:
            target = row.get("id", "")
            if not target:
                failures.append(f"{REGISTRY_PATHS[kind]} contains row with no id")
                continue
            if target in ids:
                failures.append(f"{REGISTRY_PATHS[kind]} contains duplicate id {target}")
            ids.add(target)
            expected = normalize_state(row.get("status", ""))
            actual = event_states.get((kind, target))
            if actual != expected:
                failures.append(
                    f"{target} cannot be captured: TSV={expected or '(empty)'} event-history={actual or '(missing)'}"
                )
            relpath = row.get("path", "")
            if relpath:
                md = markdown_states(ROOT / relpath)
                if not md["visible"]:
                    failures.append(f"{target} cannot be captured: Markdown has no visible lifecycle field")
                elif md["visible"] != expected:
                    failures.append(
                        f"{target} cannot be captured: TSV={expected} Markdown={md['visible']}"
                    )
                if md["frontmatter"] and md["frontmatter"] != expected:
                    failures.append(
                        f"{target} cannot be captured: TSV={expected} frontmatter={md['frontmatter']}"
                    )
    return failures

def capture_successful_transaction(command: list[str]) -> bool:
    old = load_state()
    tx = load_transaction()
    if tx.get("canonical_revision") != old.get("revision") or tx.get("canonical_digest") != canonical_digest(old):
        raise StateError("Canonical state changed during the EOS transaction; refusing capture")
    if tx.get("command") != command:
        raise StateError("EOS transaction command mismatch; refusing capture")

    rows_by_kind = rows_from_projections()
    failures = validate_projection_rows_against_events(rows_by_kind)
    if failures:
        raise StateError(
            "Successful command left inconsistent projections; canonical state was NOT advanced:\n- "
            + "\n- ".join(failures)
        )

    old_entities = old.get("entities", {})
    new_entities: dict[str, dict[str, dict]] = {kind: {} for kind in KINDS}
    changed = False
    for kind in KINDS:
        prior_map = old_entities.get(kind, {})
        for row in rows_by_kind[kind]:
            prior = prior_map.get(row["id"])
            entity = row_to_entity(kind, row, previous=prior)
            new_entities[kind][row["id"]] = entity
            if prior != entity:
                changed = True
        removed = set(prior_map) - set(new_entities[kind])
        if removed:
            raise StateError(
                f"EOS transaction attempted to remove canonical entities without explicit retirement: {', '.join(sorted(removed))}"
            )

    if changed:
        new_state = {
            "schema_version": SCHEMA_VERSION,
            "model": STATE_MODEL_ID,
            "revision": int(old.get("revision", 0)) + 1,
            "updated_at": now_iso(),
            "entities": new_entities,
        }
        write_json_atomic(CANONICAL_PATH, new_state)
    else:
        new_state = old

    for kind in KINDS:
        write_bytes_atomic(ROOT / REGISTRY_PATHS[kind], expected_tsv(new_state, kind))

    old_manifest = load_json(PROJECTIONS_PATH) if PROJECTIONS_PATH.exists() else {}
    github_receipts = old_manifest.get("github", {}).get("receipts", {})
    manifest = local_projection_snapshot(new_state, github_receipts)
    write_json_atomic(PROJECTIONS_PATH, manifest)
    remove_transaction()
    return changed

def cmd_pre(args: argparse.Namespace) -> int:
    state = load_state()
    if TRANSACTION_PATH.exists():
        raise StateError(
            "An interrupted canonical-state transaction receipt exists at "
            ".eos/cache/canonical-state-transaction.json. Inspect `./scripts/eos state status` "
            "and explicitly reconcile projections before continuing."
        )
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if command[:2] == ["state", "reconcile"]:
        return 0
    is_github_sync = bool(command and command[0] == "github-sync")
    assert_clean(state, include_github_local=not is_github_sync)
    if is_github_sync and "--apply" in command:
        verify_github_receipts(state)
    save_transaction(command, state)
    return 0

def cmd_post(args: argparse.Namespace) -> int:
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    changed = capture_successful_transaction(command)
    state = load_state()
    if command and command[0] == "github-sync" and "--apply" in command:
        refresh_github_receipts(state)
    assert_clean(state)
    github_stale = github_local_drift(state)
    print(
        f"EOS canonical state: revision {state['revision']} "
        f"({'advanced' if changed else 'unchanged'}); local projections consistent."
    )
    if github_stale:
        print("EOS GitHub projection requires synchronization:", file=sys.stderr)
        for item in github_stale:
            print(f"  WARN {item}", file=sys.stderr)
        print("  Run: ./scripts/eos github-sync --apply", file=sys.stderr)
    return 0

def project_from_canonical(state: dict, *, apply: bool) -> list[str]:
    actions: list[str] = []
    for kind in KINDS:
        path = ROOT / REGISTRY_PATHS[kind]
        expected = expected_tsv(state, kind)
        if not path.exists() or path.read_bytes() != expected:
            actions.append(f"TSV <- canonical: {REGISTRY_PATHS[kind]}")
            if apply:
                write_bytes_atomic(path, expected)
        for entity in state_entities(state, kind):
            row = entity_to_row(kind, entity)
            relpath = row.get("path", "")
            if not relpath:
                continue
            path = ROOT / relpath
            observed = markdown_states(path)
            expected_state = normalize_state(entity["lifecycle_state"])
            if observed["visible"] != expected_state or (
                observed["frontmatter"] and observed["frontmatter"] != expected_state
            ):
                actions.append(f"Markdown lifecycle <- canonical: {entity['id']} ({relpath})")
                if apply:
                    set_markdown_state(path, expected_state)
    if apply:
        old_manifest = load_json(PROJECTIONS_PATH) if PROJECTIONS_PATH.exists() else {}
        receipts = old_manifest.get("github", {}).get("receipts", {})
        write_json_atomic(PROJECTIONS_PATH, local_projection_snapshot(state, receipts))
        remove_transaction()
    return actions

def cmd_status(args: argparse.Namespace) -> int:
    state = load_state()
    failures = projection_drift(state, include_github_local=True)
    if TRANSACTION_PATH.exists():
        failures.append(
            "interrupted canonical-state transaction receipt is present; explicit reconciliation required"
        )
    result = {
        "model": state["model"],
        "revision": state["revision"],
        "canonical_digest": canonical_digest(state),
        "canonical_path": ".eos/state/current.json",
        "drift": failures,
        "consistent": not failures,
        "policy": projection_policy(),
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Canonical operational state: .eos/state/current.json")
        print(f"Revision: {state['revision']}")
        print(f"Digest: {result['canonical_digest']}")
        print("Representations:")
        print("  CANONICAL  machine EOS metadata (.eos/state/current.json)")
        print("  HISTORY    append-only events + Git")
        print("  PROJECTION TSV registries")
        print("  PROJECTION Markdown lifecycle metadata")
        print("  PROJECTION GitHub collaboration objects")
        if failures:
            print("DRIFT DETECTED:")
            for item in failures:
                print(f"  FAIL {item}")
            return 2
        print("RESULT: CONSISTENT")
    return 0 if not failures else 2

def cmd_project(args: argparse.Namespace) -> int:
    state = load_state()
    actions = project_from_canonical(state, apply=args.apply)
    if not actions:
        print("All local projections already match canonical state.")
        return 0
    for item in actions:
        print(item)
    if not args.apply:
        print("No files changed. Re-run with --apply to project canonical state.")
        return 2
    failures = projection_drift(state)
    if failures:
        raise StateError("Projection repair incomplete:\n- " + "\n- ".join(failures))
    print("Local projections reconciled from canonical state.")
    return 0

def parse_github_issue(url: str) -> tuple[str, int]:
    match = re.search(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", url)
    if not match:
        raise StateError(f"Unsupported GitHub issue URL: {url}")
    return match.group(1), int(match.group(2))

def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if check and proc.returncode != 0:
        raise StateError(
            f"Command failed ({proc.returncode}): {' '.join(args)}\n{proc.stderr.strip()}"
        )
    return proc

def expected_github_projection(kind: str, entity: dict) -> dict:
    row = entity_to_row(kind, entity)
    labels = {"eos", KIND_LABEL[kind]}
    if entity["lifecycle_state"] == "AUTHORIZED":
        labels.add("authorized")
    if entity["lifecycle_state"] == "BLOCKED":
        labels.add("blocked")
    path = ROOT / row["path"]
    body = path.read_text(encoding="utf-8") if path.exists() else ""
    title = f"{entity['id']}: {row.get('title') or row.get('summary') or entity['id']}"
    return {
        "title": title,
        "body_sha256": sha256_bytes(body.encode("utf-8")),
        "labels": sorted(labels),
        "state": "CLOSED" if entity["lifecycle_state"] == "CLOSED" else "OPEN",
        "milestone": row.get("pi", "") or (entity["id"] if kind == "PI" else ""),
    }

def remote_github_projection(url: str) -> dict:
    if not shutil_which("gh"):
        raise StateError("GitHub CLI `gh` is required to verify GitHub projection drift")
    repo, issue = parse_github_issue(url)
    proc = run(
        [
            "gh", "issue", "view", str(issue), "--repo", repo,
            "--json", "title,body,state,labels,milestone,url",
        ]
    )
    data = json.loads(proc.stdout)
    labels = sorted(
        item.get("name", "")
        for item in data.get("labels", [])
        if item.get("name", "") in MANAGED_GITHUB_LABELS
    )
    milestone = data.get("milestone") or {}
    return {
        "title": data.get("title", ""),
        "body_sha256": sha256_bytes((data.get("body") or "").encode("utf-8")),
        "labels": labels,
        "state": normalize_state(data.get("state", "")),
        "milestone": milestone.get("title", "") if isinstance(milestone, dict) else "",
    }

def shutil_which(name: str) -> str | None:
    import shutil
    return shutil.which(name)

def github_receipt_digest(value: dict) -> str:
    return sha256_bytes(canonical_json_bytes(value))

def verify_github_receipts(state: dict) -> None:
    manifest = load_json(PROJECTIONS_PATH)
    receipts = manifest.get("github", {}).get("receipts", {})
    failures: list[str] = []
    for kind in KINDS:
        for entity in state_entities(state, kind):
            row = entity_to_row(kind, entity)
            url = row.get("github_url", "")
            if not url:
                continue
            receipt = receipts.get(entity["id"])
            if not receipt:
                failures.append(
                    f"{entity['id']} has GitHub URL but no synchronization receipt; explicit reconciliation required"
                )
                continue
            remote = remote_github_projection(url)
            if github_receipt_digest(remote) != receipt.get("remote_digest"):
                failures.append(f"{entity['id']} GitHub issue changed since last EOS synchronization")
    if failures:
        raise StateError(
            "GitHub projection drift detected; automatic overwrite is forbidden:\n- "
            + "\n- ".join(failures)
            + "\nRun `./scripts/eos state reconcile github --target <ID> --strategy canonical-wins` "
              "or convert the external change into a governed EOS change."
        )

def refresh_github_receipts(state: dict) -> None:
    if not shutil_which("gh"):
        return
    manifest = load_json(PROJECTIONS_PATH) if PROJECTIONS_PATH.exists() else local_projection_snapshot(state)
    receipts = dict(manifest.get("github", {}).get("receipts", {}))
    for kind in KINDS:
        for entity in state_entities(state, kind):
            row = entity_to_row(kind, entity)
            url = row.get("github_url", "")
            if not url:
                continue
            apply_github_expected(kind, entity)
            remote = remote_github_projection(url)
            expected = expected_github_projection(kind, entity)
            if github_receipt_digest(remote) != github_receipt_digest(expected):
                raise StateError(
                    f"{entity['id']} GitHub projection did not converge to canonical state"
                )
            receipts[entity["id"]] = {
                "url": url,
                "canonical_revision": state["revision"],
                "synced_at": now_iso(),
                "expected_digest": github_receipt_digest(expected),
                "remote_digest": github_receipt_digest(remote),
            }
    write_json_atomic(PROJECTIONS_PATH, local_projection_snapshot(state, receipts))

def find_entity(state: dict, target: str) -> tuple[str, dict]:
    for kind in KINDS:
        entity = state.get("entities", {}).get(kind, {}).get(target)
        if entity:
            return kind, entity
    raise StateError(f"Unknown canonical entity: {target}")

def apply_github_expected(kind: str, entity: dict) -> None:
    if not shutil_which("gh"):
        raise StateError("GitHub CLI `gh` is required for GitHub synchronization")
    row = entity_to_row(kind, entity)
    url = row.get("github_url", "")
    if not url:
        raise StateError(f"{entity['id']} has no GitHub projection URL")
    repo, issue = parse_github_issue(url)
    expected = expected_github_projection(kind, entity)
    tmp = None
    try:
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        tmp = Path(handle.name)
        handle.write((ROOT / row["path"]).read_text(encoding="utf-8"))
        handle.close()
        run(
            [
                "gh", "issue", "edit", str(issue), "--repo", repo,
                "--title", expected["title"], "--body-file", str(tmp),
            ]
        )
        remote_before = remote_github_projection(url)
        current_labels = set(remote_before.get("labels", []))
        expected_labels = set(expected["labels"])
        for label in sorted(current_labels - expected_labels):
            run(
                ["gh", "issue", "edit", str(issue), "--repo", repo, "--remove-label", label],
                check=False,
            )
        for label in sorted(expected_labels - current_labels):
            run(
                ["gh", "issue", "edit", str(issue), "--repo", repo, "--add-label", label],
                check=False,
            )
        if expected["milestone"]:
            run(
                [
                    "gh", "issue", "edit", str(issue), "--repo", repo,
                    "--milestone", expected["milestone"],
                ],
                check=False,
            )
        if expected["state"] == "CLOSED":
            run(
                ["gh", "issue", "close", str(issue), "--repo", repo, "--reason", "completed"],
                check=False,
            )
        else:
            run(["gh", "issue", "reopen", str(issue), "--repo", repo], check=False)
    finally:
        if tmp:
            try:
                tmp.unlink()
            except FileNotFoundError:
                pass

def reconcile_github_canonical_wins(state: dict, target: str) -> None:
    kind, entity = find_entity(state, target)
    row = entity_to_row(kind, entity)
    if not row.get("github_url", ""):
        raise StateError(
            f"{target} has no GitHub projection URL; use github-sync --apply to create it"
        )
    apply_github_expected(kind, entity)
    remote = remote_github_projection(row["github_url"])
    expected = expected_github_projection(kind, entity)
    if github_receipt_digest(remote) != github_receipt_digest(expected):
        raise StateError(f"{target} GitHub projection did not converge to canonical state")
    manifest = load_json(PROJECTIONS_PATH)
    receipts = dict(manifest.get("github", {}).get("receipts", {}))
    receipts[target] = {
        "url": row["github_url"],
        "canonical_revision": state["revision"],
        "synced_at": now_iso(),
        "expected_digest": github_receipt_digest(expected),
        "remote_digest": github_receipt_digest(remote),
    }
    write_json_atomic(PROJECTIONS_PATH, local_projection_snapshot(state, receipts))

def cmd_reconcile(args: argparse.Namespace) -> int:
    state = load_state()
    projection = args.projection.lower()
    if projection in {"tsv", "markdown", "local"}:
        if args.strategy != "canonical-wins":
            raise StateError("Local projections support only --strategy canonical-wins")
        actions = project_from_canonical(state, apply=True)
        print("\n".join(actions) if actions else "Local projections already match canonical state.")
    elif projection == "github":
        if not args.target:
            raise StateError("GitHub reconciliation requires --target <EOS-ID>")
        if args.strategy != "canonical-wins":
            raise StateError(
                "GitHub is a collaboration projection; external edits cannot become canonical implicitly. "
                "Use --strategy canonical-wins, or model the external proposal as an explicit governed EOS change."
            )
        reconcile_github_canonical_wins(state, args.target)
        remove_transaction()
        print(f"GitHub projection for {args.target} reconciled from canonical EOS state.")
    else:
        raise StateError("Projection must be one of local, tsv, markdown, github")
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EOS single canonical state controller")
    sub = parser.add_subparsers(dest="command_name", required=True)
    p = sub.add_parser("pre", help=argparse.SUPPRESS)
    p.add_argument("command", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_pre)
    p = sub.add_parser("post", help=argparse.SUPPRESS)
    p.add_argument("command", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_post)
    p = sub.add_parser("status", help="Check canonical state and all local projections")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_status)
    p = sub.add_parser("project", help="Project canonical state into local TSV/Markdown representations")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_project)
    p = sub.add_parser("reconcile", help="Explicitly reconcile a projection from canonical state")
    p.add_argument("projection", choices=("local", "tsv", "markdown", "github"))
    p.add_argument("--target", default="")
    p.add_argument("--strategy", choices=("canonical-wins",), default="canonical-wins")
    p.set_defaults(func=cmd_reconcile)
    return parser

def main() -> int:
    try:
        args = build_parser().parse_args()
        return int(args.func(args) or 0)
    except StateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
