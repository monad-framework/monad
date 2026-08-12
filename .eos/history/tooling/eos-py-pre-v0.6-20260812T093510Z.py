#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import uuid
from collections import deque
from pathlib import Path
from typing import Iterable

UTC = dt.timezone.utc

ID_RE = re.compile(
    r"\b(?:"
    r"REQ-[A-Z0-9][A-Z0-9-]*|"
    r"CAP-[A-Z0-9][A-Z0-9-]*|"
    r"QA-[A-Z0-9][A-Z0-9-]*|"
    r"ADR-\d{4}|"
    r"SPEC-[A-Z0-9][A-Z0-9-]*|"
    r"PI-\d{3}|"
    r"WC-\d{4}|"
    r"WP(?:-[A-Z][A-Z0-9]*)?-\d{4}|"
    r"CR-\d{4}|"
    r"MNT-\d{4}|"
    r"RISK-\d{3,4}|"
    r"REL-\d+\.\d+\.\d+"
    r")\b"
)

LAYER_ORDER = ("EOSB", "EOSP", "EOSE", "EOSV", "EOSR", "EOSC", "EOSL", "EOSM")

VALID_STATES = {
    "PI": {"DRAFT", "PLANNED", "AUTHORIZED", "ACTIVE", "IN_REVIEW", "CLOSED", "BLOCKED"},
    "WC": {"DRAFT", "READY", "AUTHORIZED", "ACTIVE", "IN_REVIEW", "CLOSED", "BLOCKED"},
    "WP": {
        "DRAFT",
        "READY",
        "AUTHORIZED",
        "IN_PROGRESS",
        "VERIFYING",
        "IN_REVIEW",
        "CLOSED",
        "BLOCKED",
    },
    "CR": {"DRAFT", "PROPOSED", "APPROVED", "APPLIED", "CLOSED", "REJECTED"},
    "MNT": {"OPEN", "PLANNED", "IN_PROGRESS", "VERIFYING", "CLOSED", "DEFERRED"},
    "REL": {"PROPOSED", "READY", "RELEASED", "WITHDRAWN"},
}

REGISTRY_FIELDS = {
    "PI": ["id", "path", "title", "status", "created", "updated", "github_url"],
    "WC": ["id", "path", "title", "status", "pi", "created", "updated", "github_url"],
    "WP": [
        "id",
        "path",
        "title",
        "status",
        "pi",
        "wc",
        "domain",
        "created",
        "updated",
        "github_url",
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


class EosError(RuntimeError):
    pass


def now_iso() -> str:
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return dt.date.today().isoformat()


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        check=check,
        capture_output=capture,
    )


def discover_root() -> Path:
    explicit = os.environ.get("EOS_ROOT", "").strip()
    if explicit:
        return Path(explicit).resolve()
    try:
        result = run(["git", "rev-parse", "--show-toplevel"])
        return Path(result.stdout.strip()).resolve()
    except Exception:
        # When tools/eos/eos.py is invoked directly, use the repository layout
        # relative to this file before falling back to the caller's cwd.
        candidate = Path(__file__).resolve().parents[2]
        if (candidate / ".eos").exists() or (candidate / "scripts" / "eos").exists():
            return candidate
        return Path.cwd().resolve()


ROOT = discover_root()
EOS = ROOT / ".eos"
SCHEMA_DIR = EOS / "schemas"
STATE_MACHINE_DIR = EOS / "state-machines"
EVENTS_PATH = EOS / "events.jsonl"
EOS_VERSION_PATH = EOS / "version.json"
POLICY_PATH = EOS / "policies" / "core.json"
OVERRIDES_PATH = EOS / "overrides.tsv"
STALE_PATH = EOS / "stale.tsv"
EVENT_SCHEMA_VERSION = "1.0.0"
OVERRIDE_FIELDS = [
    "id", "target", "gate", "status", "actor", "reason", "created", "expires", "consumed_at"
]
STALE_FIELDS = [
    "id", "target", "source", "reason", "status", "created",
    "cleared_at", "cleared_by", "clear_reason"
]
EXPLICIT_RELATION_RE = re.compile(
    r"^\s*-\s*(contains|implements|satisfies|depends-on|conforms-to|constrained-by|affects|includes|references):\s*"
    r"(" + ID_RE.pattern.strip(r"\b") + r")\s*$",
    re.I,
)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EosError(f"Missing EOS definition: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise EosError(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def state_machine(kind: str) -> dict:
    path = STATE_MACHINE_DIR / f"{kind.lower()}.json"
    machine = load_json(path)
    if machine.get("kind") != kind:
        raise EosError(f"State machine kind mismatch in {rel(path)}")
    return machine


def valid_states(kind: str) -> set[str]:
    return set(state_machine(kind).get("states", []))


def transition_allowed(kind: str, current: str, new: str) -> bool:
    machine = state_machine(kind)
    return new in machine.get("transitions", {}).get(current, [])


def validate_simple_schema(schema: dict, instance: dict[str, str], *, label: str) -> list[str]:
    errors: list[str] = []
    if schema.get("type") == "object" and not isinstance(instance, dict):
        return [f"{label}: expected object"]
    required = schema.get("required", [])
    for key in required:
        if key not in instance:
            errors.append(f"{label}: missing required field {key}")
    props = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        extras = sorted(set(instance) - set(props))
        for key in extras:
            errors.append(f"{label}: unexpected field {key}")
    for key, rules in props.items():
        if key not in instance:
            continue
        value = instance[key]
        if rules.get("type") == "string" and not isinstance(value, str):
            errors.append(f"{label}.{key}: expected string")
            continue
        if isinstance(value, str):
            if "minLength" in rules and len(value) < int(rules["minLength"]):
                errors.append(f"{label}.{key}: shorter than minLength")
            pattern = rules.get("pattern")
            if pattern and not re.fullmatch(pattern, value):
                errors.append(f"{label}.{key}: value {value!r} does not match {pattern}")
            enum = rules.get("enum")
            if enum and value not in enum:
                errors.append(f"{label}.{key}: value {value!r} is not in enum")
    return errors


def actor_name(explicit: str = "") -> str:
    return explicit or os.environ.get("EOS_ACTOR") or os.environ.get("USER") or "unknown"


def read_events() -> list[dict]:
    if not EVENTS_PATH.exists():
        return []
    events: list[dict] = []
    for lineno, raw in enumerate(EVENTS_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise EosError(f"Malformed event ledger line {lineno}: {exc}") from exc
        if not isinstance(event, dict):
            raise EosError(f"Malformed event ledger line {lineno}: expected object")
        events.append(event)
    return events


def append_event(
    event_type: str,
    *,
    target: str = "",
    entity_kind: str = "",
    action: str = "",
    from_state: str = "",
    to_state: str = "",
    actor: str = "",
    reason: str = "",
    metadata: dict | None = None,
) -> dict:
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "event_id": "EVT-" + uuid.uuid4().hex.upper(),
        "schema_version": EVENT_SCHEMA_VERSION,
        "timestamp": now_iso(),
        "event_type": event_type,
        "actor": actor_name(actor),
        "target": target,
        "entity_kind": entity_kind,
        "action": action,
        "from_state": from_state,
        "to_state": to_state,
        "reason": reason,
        "commit": commit_sha() if "commit_sha" in globals() else "",
        "metadata": metadata or {},
    }
    schema_path = SCHEMA_DIR / "event.schema.json"
    if schema_path.exists():
        errors = validate_simple_schema(load_json(schema_path), event, label=event["event_id"])
        if errors:
            raise EosError("Event schema validation failed:\n- " + "\n- ".join(errors))
    line = json.dumps(event, sort_keys=True, separators=(",", ":"))
    with EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())
    return event


def ensure_event_ledger_seeded() -> None:
    if EVENTS_PATH.exists() and EVENTS_PATH.stat().st_size > 0:
        return
    append_event(
        "EOS_INITIALIZED",
        action="bootstrap",
        reason="initialize append-only EOS lifecycle event ledger",
        metadata={"root": str(ROOT)},
    )
    for kind in ("PI", "WC", "WP", "CR", "MNT", "REL"):
        for row in registry(kind):
            append_event(
                "ENTITY_IMPORTED",
                target=row.get("id", ""),
                entity_kind=kind,
                action="import",
                to_state=row.get("status", ""),
                reason="seed existing lifecycle registry into event ledger",
                metadata={"row": row},
            )


def record_tool_upgrade_if_needed() -> None:
    previous = os.environ.get("EOS_PREVIOUS_TOOL_VERSION", "").strip()
    if not previous or not EOS_VERSION_PATH.exists():
        return
    current = load_json(EOS_VERSION_PATH).get("eos_tool_version", "")
    if not current or current == previous:
        return
    # Avoid duplicate upgrade events in case bootstrap invokes more than one EOS
    # command under the same environment.
    for event in reversed(read_events()):
        if event.get("event_type") == "EOS_TOOL_UPGRADED":
            meta = event.get("metadata", {})
            if meta.get("from") == previous and meta.get("to") == current:
                return
    append_event(
        "EOS_TOOL_UPGRADED",
        action="upgrade",
        reason=f"EOS tooling upgraded from {previous} to {current}",
        metadata={"from": previous, "to": current},
    )


def event_projected_state() -> dict[tuple[str, str], str]:
    state: dict[tuple[str, str], str] = {}
    for event in read_events():
        kind = event.get("entity_kind", "")
        target = event.get("target", "")
        if not kind or not target:
            continue
        if event.get("event_type") in {"ENTITY_CREATED", "ENTITY_IMPORTED"}:
            initial = event.get("to_state") or event.get("metadata", {}).get("row", {}).get("status", "")
            if initial:
                state[(kind, target)] = initial
        elif event.get("event_type") == "STATE_TRANSITION":
            if event.get("to_state"):
                state[(kind, target)] = event["to_state"]
    return state


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def ensure_dirs() -> None:
    for d in (
        EOS,
        EOS / "history",
        EOS / "checkpoints",
        EOS / "prompts",
        EOS / "contracts",
        EOS / "evidence",
        EOS / "decisions",
        EOS / "schemas",
        EOS / "state-machines",
        EOS / "policies",
        EOS / "cache",
        EOS / "sync",
        ROOT / "engineering" / "reviews",
        ROOT / "engineering" / "increments",
        ROOT / "engineering" / "work-cycles",
        ROOT / "engineering" / "work-packets",
        ROOT / "engineering" / "changes",
        ROOT / "engineering" / "releases",
        ROOT / "engineering" / "maintenance",
    ):
        d.mkdir(parents=True, exist_ok=True)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    tmp.replace(path)


def registry(kind: str) -> list[dict[str, str]]:
    kind = kind.upper()
    return read_tsv(ROOT / REGISTRY_PATHS[kind])


def save_registry(kind: str, rows: list[dict[str, str]]) -> None:
    kind = kind.upper()
    write_tsv(ROOT / REGISTRY_PATHS[kind], REGISTRY_FIELDS[kind], rows)


def find_row(kind: str, target: str) -> dict[str, str] | None:
    for row in registry(kind):
        if row["id"] == target:
            return row
    return None


def update_row(kind: str, target: str, **updates: str) -> dict[str, str]:
    rows = registry(kind)
    for row in rows:
        if row["id"] == target:
            row.update(updates)
            row["updated"] = now_iso()
            save_registry(kind, rows)
            return row
    raise EosError(f"{target} is not registered as {kind}")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, body


def write_frontmatter(path: Path, data: dict[str, str], body: str) -> None:
    ordered = (
        "artifact_id",
        "title",
        "type",
        "version",
        "status",
        "authority",
        "created",
        "updated",
    )
    lines = ["---"]
    seen = set()
    for key in ordered:
        if key in data:
            lines.append(f'{key}: "{data[key]}"')
            seen.add(key)
    for key, value in data.items():
        if key not in seen:
            lines.append(f'{key}: "{value}"')
    lines.append("---")
    path.write_text("\n".join(lines) + "\n\n" + body.lstrip("\n"), encoding="utf-8")


def set_frontmatter(path: Path, key: str, value: str) -> None:
    data, body = parse_frontmatter(path)
    if not data:
        raise EosError(f"{rel(path)} has no EOS YAML front matter")
    data[key] = value
    if key != "updated":
        data["updated"] = today()
    write_frontmatter(path, data, body)


def create_artifact(
    path: Path,
    artifact_id: str,
    title: str,
    artifact_type: str,
    authority: str,
    body: str,
    *,
    status: str = "Draft",
) -> None:
    if path.exists():
        raise EosError(f"Refusing to overwrite existing artifact: {rel(path)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "artifact_id": artifact_id,
        "title": title,
        "type": artifact_type,
        "version": "0.1.0",
        "status": status,
        "authority": authority,
        "created": today(),
        "updated": today(),
    }
    write_frontmatter(path, data, body)
    seed_snapshot(path)


def seed_snapshot(path: Path) -> None:
    data, _ = parse_frontmatter(path)
    version = data.get("version")
    if not version:
        return
    snap = snapshot_path(path, version)
    if not snap.exists():
        snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, snap)


def snapshot_path(path: Path, version: str) -> Path:
    rp = rel(path)
    p = Path(rp)
    return EOS / "history" / p.with_suffix("") / f"v{version}{p.suffix}"


def bump_semver(current: str, kind: str) -> str:
    try:
        major, minor, patch = map(int, current.split("."))
    except ValueError as exc:
        raise EosError(f"Invalid semantic version: {current}") from exc
    if kind == "patch":
        patch += 1
    elif kind == "minor":
        minor += 1
        patch = 0
    elif kind == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise EosError("Version change must be patch, minor, or major")
    return f"{major}.{minor}.{patch}"


def append_tsv(path: Path, fields: list[str], row: dict[str, str]) -> None:
    rows = read_tsv(path)
    rows.append(row)
    write_tsv(path, fields, rows)


def kind_for_id(target: str) -> str:
    if re.fullmatch(r"PI-\d{3}", target):
        return "PI"
    if re.fullmatch(r"WC-\d{4}", target):
        return "WC"
    if re.fullmatch(r"WP(?:-[A-Z][A-Z0-9]*)?-\d{4}", target):
        return "WP"
    if re.fullmatch(r"CR-\d{4}", target):
        return "CR"
    if re.fullmatch(r"MNT-\d{4}", target):
        return "MNT"
    if re.fullmatch(r"REL-\d+\.\d+\.\d+", target):
        return "REL"
    raise EosError(f"Unsupported lifecycle target: {target}")


def row_for_target(target: str) -> tuple[str, dict[str, str]]:
    kind = kind_for_id(target)
    row = find_row(kind, target)
    if row is None:
        raise EosError(f"{target} is not registered")
    return kind, row


def artifact_path_for_id(target: str) -> Path | None:
    try:
        _, row = row_for_target(target)
        return ROOT / row["path"]
    except EosError:
        pass

    artifacts = read_tsv(EOS / "artifacts.tsv")
    for row in artifacts:
        if row.get("artifact_id") == target:
            return ROOT / row.get("path", "")

    # Common filename-based fallback for ADRs/REQs/etc.
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts or ".eos/history" in path.as_posix():
            continue
        data, _ = parse_frontmatter(path) if path.suffix == ".md" else ({}, "")
        if data.get("artifact_id") == target:
            return path
        if target in path.name:
            return path
    return None


def next_number(kind: str, width: int, *, prefix: str | None = None) -> int:
    rows = registry(kind)
    nums: list[int] = []
    if kind == "WP" and prefix:
        pattern = re.compile(rf"^WP-{re.escape(prefix)}-(\d{{4}})$")
    elif kind == "WP":
        pattern = re.compile(r"^WP-(\d{4})$")
    elif kind == "PI":
        pattern = re.compile(r"^PI-(\d{3})$")
    elif kind == "WC":
        pattern = re.compile(r"^WC-(\d{4})$")
    elif kind == "CR":
        pattern = re.compile(r"^CR-(\d{4})$")
    elif kind == "MNT":
        pattern = re.compile(r"^MNT-(\d{4})$")
    else:
        raise EosError(f"Cannot allocate ID for kind {kind}")
    for row in rows:
        match = pattern.match(row["id"])
        if match:
            nums.append(int(match.group(1)))
    return max(nums, default=0) + 1


def state_line(path: Path) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("**State:**"):
            return line.split(":", 1)[1].strip()
    return None


def replace_state_line(path: Path, new_state: str) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("**State:**"):
            lines[i] = f"**State:** {new_state}"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    # No state line: insert after first heading.
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines.insert(i + 1, "")
            lines.insert(i + 2, f"**State:** {new_state}")
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return


def sync_artifact_state(path: Path, state: str) -> None:
    if not path.exists():
        return
    replace_state_line(path, state)
    data, _ = parse_frontmatter(path) if path.suffix == ".md" else ({}, "")
    if data:
        set_frontmatter(path, "status", state)


def set_lifecycle_state(
    target: str,
    state: str,
    *,
    action: str = "transition",
    actor: str = "",
    reason: str = "",
    force: bool = False,
) -> None:
    kind, row = row_for_target(target)
    current = row["status"]
    if state not in valid_states(kind):
        raise EosError(f"Invalid {kind} state: {state}")
    if current == state:
        return
    if not force and not transition_allowed(kind, current, state):
        allowed = state_machine(kind).get("transitions", {}).get(current, [])
        raise EosError(
            f"Illegal {kind} lifecycle transition {target}: {current} -> {state}. "
            f"Allowed from {current}: {', '.join(allowed) or '(none)'}"
        )

    # Append the durable mutation event first. Registry/artifact writes are
    # projections of this lifecycle mutation.
    append_event(
        "STATE_TRANSITION",
        target=target,
        entity_kind=kind,
        action=action,
        from_state=current,
        to_state=state,
        actor=actor,
        reason=reason,
        metadata={"path": row.get("path", "")},
    )
    update_row(kind, target, status=state)
    path = ROOT / row["path"]
    sync_artifact_state(path, state)


def normalize_decision(text: str) -> str:
    return text.strip().upper().replace(" ", "_")


def review_path(target: str) -> Path:
    return ROOT / "engineering" / "reviews" / f"{target}-REVIEW.md"


def review_decision(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    patterns = (
        r"\*\*Decision:\*\*\s*([A-Za-z _-]+)",
        r"\*\*Authorization:\*\*\s*([A-Za-z _-]+)",
        r"^Decision:\s*([A-Za-z _-]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.M)
        if match:
            return normalize_decision(match.group(1))
    return ""


def is_review_accepted(path: Path) -> bool:
    decision = review_decision(path)
    return decision in {
        "ACCEPTED",
        "APPROVED",
        "AUTHORIZED",
        "AUTHORIZED_WITH_CONDITIONS",
        "ACCEPTED_WITH_FOLLOW_UP",
        "CLOSED",
        "PASS",
        "PASSED",
    }


def accepted_review_complete(path: Path) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not path.exists():
        return False, [f"missing review {rel(path)}"]
    if not is_review_accepted(path):
        reasons.append(f"review decision is not accepted: {rel(path)}")
    complete, issues = artifact_is_complete_enough(path)
    if not complete:
        reasons.extend(f"review {rel(path)}: {issue}" for issue in issues)
    return not reasons, reasons


def artifact_is_complete_enough(path: Path) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not path.exists():
        return False, [f"missing artifact {rel(path)}"]
    text = path.read_text(encoding="utf-8")
    if re.search(r"\bTBD\b", text):
        reasons.append("artifact still contains TBD markers")
    if len(text.strip()) < 300:
        reasons.append("artifact appears unusually short")
    return not reasons, reasons


def record_decision(
    target: str,
    action: str,
    outcome: str,
    actor: str,
    reason: str,
) -> None:
    fields = ["timestamp", "target", "action", "outcome", "actor", "reason"]
    append_tsv(
        EOS / "decisions.tsv",
        fields,
        {
            "timestamp": now_iso(),
            "target": target,
            "action": action,
            "outcome": outcome,
            "actor": actor,
            "reason": reason,
        },
    )
    try:
        entity_kind = kind_for_id(target)
    except EosError:
        entity_kind = ""
    append_event(
        "DECISION_RECORDED",
        target=target,
        entity_kind=entity_kind,
        action=action,
        actor=actor,
        reason=reason,
        metadata={"outcome": outcome},
    )



def policy_document() -> dict:
    return load_json(POLICY_PATH)


def policy_gate(name: str) -> list[dict]:
    gates = policy_document().get("gates", {})
    if name not in gates:
        raise EosError(f"Unknown policy gate: {name}")
    checks = gates[name]
    if not isinstance(checks, list):
        raise EosError(f"Policy gate {name} is malformed")
    return checks


def override_rows() -> list[dict[str, str]]:
    return read_tsv(OVERRIDES_PATH)


def save_overrides(rows: list[dict[str, str]]) -> None:
    write_tsv(OVERRIDES_PATH, OVERRIDE_FIELDS, rows)


def next_override_id() -> str:
    nums: list[int] = []
    for row in override_rows():
        match = re.fullmatch(r"OVR-(\d{4})", row.get("id", ""))
        if match:
            nums.append(int(match.group(1)))
    return f"OVR-{max(nums, default=0) + 1:04d}"


def override_expired(row: dict[str, str]) -> bool:
    expires = row.get("expires", "").strip()
    if not expires:
        return False
    try:
        return dt.date.fromisoformat(expires) < dt.date.today()
    except ValueError:
        return True


def active_override(target: str, gate: str) -> dict[str, str] | None:
    rows = override_rows()
    changed = False
    found: dict[str, str] | None = None
    for row in rows:
        if row.get("status") == "ACTIVE" and override_expired(row):
            row["status"] = "EXPIRED"
            changed = True
        if (
            row.get("target") == target
            and row.get("gate") == gate
            and row.get("status") == "ACTIVE"
            and not override_expired(row)
        ):
            found = row
    if changed:
        save_overrides(rows)
    return found


def create_override(
    target: str,
    gate: str,
    *,
    actor: str,
    reason: str,
    expires: str = "",
) -> dict[str, str]:
    if not reason.strip():
        raise EosError("A durable override requires an explicit --reason")
    policy_gate(gate)  # validate gate name
    if expires:
        try:
            dt.date.fromisoformat(expires)
        except ValueError as exc:
            raise EosError("--expires must be YYYY-MM-DD") from exc
    row = {
        "id": next_override_id(),
        "target": target,
        "gate": gate,
        "status": "ACTIVE",
        "actor": actor_name(actor),
        "reason": reason.strip(),
        "created": now_iso(),
        "expires": expires,
        "consumed_at": "",
    }
    rows = override_rows()
    rows.append(row)
    save_overrides(rows)
    append_event(
        "OVERRIDE_CREATED",
        target=target,
        action=gate,
        actor=row["actor"],
        reason=row["reason"],
        metadata={"override": row},
    )
    return row


def consume_override(row: dict[str, str]) -> None:
    rows = override_rows()
    for item in rows:
        if item.get("id") == row.get("id"):
            item["status"] = "CONSUMED"
            item["consumed_at"] = now_iso()
            save_overrides(rows)
            append_event(
                "OVERRIDE_CONSUMED",
                target=item.get("target", ""),
                action=item.get("gate", ""),
                actor=item.get("actor", ""),
                reason=item.get("reason", ""),
                metadata={"override_id": item.get("id", "")},
            )
            return
    raise EosError(f"Override {row.get('id')} disappeared before consumption")


def check_result(name: str, passed: bool, message: str, evidence: dict | None = None) -> dict:
    return {
        "check": name,
        "passed": bool(passed),
        "message": message,
        "evidence": evidence or {},
    }


def evaluate_policy_check(target: str, spec: dict) -> dict:
    kind, row = row_for_target(target)
    name = spec.get("check", "")
    path = ROOT / row["path"]

    if name == "state_is":
        expected = str(spec.get("value", ""))
        return check_result(
            name,
            row["status"] == expected,
            f"state is {row['status']}; required {expected}",
            {"actual": row["status"], "required": expected},
        )

    if name == "artifact_complete":
        passed, issues = artifact_is_complete_enough(path)
        return check_result(
            name,
            passed,
            "artifact is complete enough" if passed else "; ".join(issues),
            {"path": rel(path), "issues": issues},
        )

    if name == "parent_state":
        allowed = set(spec.get("values", []))
        parent_id = row.get("wc") if kind == "WP" else row.get("pi") if kind == "WC" else ""
        if not parent_id:
            return check_result(name, False, "entity has no applicable parent")
        p_kind, p_row = row_for_target(parent_id)
        passed = p_row["status"] in allowed
        return check_result(
            name,
            passed,
            f"parent {parent_id} is {p_row['status']}; allowed: {', '.join(sorted(allowed))}",
            {"parent": parent_id, "parent_kind": p_kind, "actual": p_row["status"], "allowed": sorted(allowed)},
        )

    if name == "review_accepted":
        rpath = review_path(target)
        passed, issues = accepted_review_complete(rpath)
        return check_result(
            name,
            passed,
            f"review accepted: {rel(rpath)}" if passed else "; ".join(issues),
            {"review": rel(rpath), "issues": issues},
        )

    if name == "pi_readiness_review_accepted":
        candidates = [
            ROOT / "engineering" / "reviews" / f"{target}-READINESS-REVIEW.md",
            review_path(target),
        ]
        if target == "PI-001":
            candidates.append(ROOT / "engineering" / "reviews" / "PI-001-READINESS-REVIEW.md")
        details = []
        for candidate in candidates:
            ok, issues = accepted_review_complete(candidate)
            details.append({"path": rel(candidate), "passed": ok, "issues": issues})
            if ok:
                return check_result(name, True, f"accepted readiness review: {rel(candidate)}", {"candidates": details})
        return check_result(name, False, "no accepted complete PI readiness review", {"candidates": details})

    if name == "pi_closeout_review_accepted":
        candidates = [
            ROOT / "engineering" / "reviews" / f"{target}-CLOSEOUT-REVIEW.md",
            review_path(target),
        ]
        details = []
        for candidate in candidates:
            ok, issues = accepted_review_complete(candidate)
            details.append({"path": rel(candidate), "passed": ok, "issues": issues})
            if ok:
                return check_result(name, True, f"accepted PI closeout review: {rel(candidate)}", {"candidates": details})
        return check_result(name, False, "no accepted complete PI closeout review", {"candidates": details})

    if name == "no_unchecked_items":
        count = unchecked_boxes(path)
        return check_result(
            name,
            count == 0,
            "no unchecked items" if count == 0 else f"{count} unchecked item(s) remain",
            {"count": count, "path": rel(path)},
        )

    if name == "has_children":
        if kind == "WC":
            children = [r for r in registry("WP") if r.get("wc") == target]
        elif kind == "PI":
            children = [r for r in registry("WC") if r.get("pi") == target]
        else:
            children = []
        return check_result(
            name,
            bool(children),
            f"{len(children)} child object(s) registered",
            {"children": [r["id"] for r in children]},
        )

    if name == "children_closed":
        if kind == "WC":
            children = [r for r in registry("WP") if r.get("wc") == target]
        elif kind == "PI":
            children = [r for r in registry("WC") if r.get("pi") == target]
        else:
            children = []
        open_ids = [r["id"] for r in children if r.get("status") != "CLOSED"]
        return check_result(
            name,
            not open_ids,
            "all children closed" if not open_ids else "open children: " + ", ".join(open_ids),
            {"open": open_ids},
        )

    if name == "change_decision_approved":
        decision = review_decision(path)
        passed = decision in {"APPROVED", "ACCEPTED"}
        return check_result(
            name,
            passed,
            f"change decision is {decision or '(unset)'}; required APPROVED/ACCEPTED",
            {"decision": decision},
        )

    raise EosError(f"Unsupported policy predicate: {name}")


def evaluate_gate(name: str, target: str) -> dict:
    results = [evaluate_policy_check(target, spec) for spec in policy_gate(name)]
    failures = [r for r in results if not r["passed"]]
    override = active_override(target, name)
    return {
        "gate": name,
        "target": target,
        "passed": not failures,
        "effective_pass": not failures or override is not None,
        "checks": results,
        "failures": failures,
        "override": override,
    }


def format_gate(result: dict) -> str:
    lines = [
        f"Gate:   {result['gate']}",
        f"Target: {result['target']}",
        f"Result: {'PASS' if result['passed'] else 'FAIL'}",
    ]
    if result.get("override"):
        lines.append(
            f"Override: {result['override']['id']} ACTIVE by {result['override']['actor']}"
        )
    lines.append("Checks:")
    for item in result["checks"]:
        lines.append(
            f"  {'PASS' if item['passed'] else 'FAIL'}  "
            f"{item['check']}: {item['message']}"
        )
    return "\n".join(lines)


def enforce_gate(
    name: str,
    target: str,
    *,
    force: bool = False,
    actor: str = "",
    reason: str = "",
) -> dict[str, str] | None:
    result = evaluate_gate(name, target)
    if result["passed"]:
        return None

    override = result.get("override")
    if override:
        return override

    if force:
        override = create_override(
            target,
            name,
            actor=actor_name(actor),
            reason=reason,
        )
        return override

    failures = "\n- ".join(item["message"] for item in result["failures"])
    raise EosError(
        f"{name} gate failed for {target}:\n- {failures}\n"
        f"Inspect with: ./scripts/eos gate explain {name} {target}\n"
        "An explicit human override may be created only with a recorded reason."
    )


def cmd_policy_list(_: argparse.Namespace) -> None:
    doc = policy_document()
    for name in sorted(doc.get("gates", {})):
        print(name)


def cmd_policy_show(args: argparse.Namespace) -> None:
    print(json.dumps({"gate": args.gate, "checks": policy_gate(args.gate)}, indent=2, sort_keys=True))


def cmd_gate(args: argparse.Namespace) -> None:
    result = evaluate_gate(args.gate, args.target)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(format_gate(result))
    if not result["effective_pass"]:
        raise EosError("Gate did not pass")


def cmd_override_create(args: argparse.Namespace) -> None:
    row = create_override(
        args.target,
        args.gate,
        actor=args.by,
        reason=args.reason,
        expires=args.expires,
    )
    print(
        f"Created {row['id']} for {row['target']} gate {row['gate']} "
        f"by {row['actor']}"
    )


def cmd_override_list(args: argparse.Namespace) -> None:
    rows = override_rows()
    if args.target:
        rows = [r for r in rows if r.get("target") == args.target]
    if args.active:
        rows = [r for r in rows if r.get("status") == "ACTIVE" and not override_expired(r)]
    for row in rows:
        print(
            f"{row['id']}  {row['status']:<9}  {row['target']:<20} "
            f"{row['gate']:<20} {row['actor']}  {row['reason']}"
        )


def cmd_override_expire(args: argparse.Namespace) -> None:
    rows = override_rows()
    for row in rows:
        if row.get("id") == args.override_id:
            if row.get("status") != "ACTIVE":
                raise EosError(f"{args.override_id} is {row.get('status')}, not ACTIVE")
            row["status"] = "EXPIRED"
            save_overrides(rows)
            append_event(
                "OVERRIDE_EXPIRED",
                target=row.get("target", ""),
                action=row.get("gate", ""),
                actor=actor_name(),
                reason="override explicitly expired",
                metadata={"override_id": args.override_id},
            )
            print(f"{args.override_id} EXPIRED.")
            return
    raise EosError(f"Unknown override: {args.override_id}")


def git_available() -> bool:
    return shutil.which("git") is not None


def git_clean() -> bool:
    if not git_available():
        return False
    try:
        return not run(["git", "status", "--porcelain"], cwd=ROOT).stdout.strip()
    except Exception:
        return False


def git_status() -> str:
    if not git_available():
        return "git unavailable"
    try:
        out = run(["git", "status", "--short"], cwd=ROOT).stdout.strip()
        return out or "clean"
    except Exception as exc:
        return f"git status unavailable: {exc}"


def current_branch() -> str:
    try:
        return run(["git", "branch", "--show-current"], cwd=ROOT).stdout.strip()
    except Exception:
        return ""


def commit_sha() -> str:
    try:
        return run(["git", "rev-parse", "HEAD"], cwd=ROOT).stdout.strip()
    except Exception:
        return ""


def latest_active(kind: str) -> dict[str, str] | None:
    rows = registry(kind)
    closed = {"CLOSED", "RELEASED", "REJECTED", "WITHDRAWN"}
    for row in reversed(rows):
        if row.get("status") not in closed:
            return row
    return None


def cmd_layers(_: argparse.Namespace) -> None:
    rows = read_tsv(EOS / "layers.tsv")
    print("PERMANENT EOS OPERATING LAYERS\n")
    for row in rows:
        print(f"{row['code']} — {row['name']}")
        print(f"  {row['purpose']}")
        print()


def cmd_status(_: argparse.Namespace) -> None:
    print("ENGINEERING OPERATING SYSTEM\n")
    print("Permanent layers:")
    for row in read_tsv(EOS / "layers.tsv"):
        print(f"  {row['code']:<5} {row['name']:<20} {row['purpose']}")

    workflow = read_tsv(EOS / "workflow.tsv")
    next_stage = next((row for row in workflow if row.get("status") != "COMPLETE"), None)
    print("\nBootstrap:")
    if next_stage:
        print(
            f"  next={next_stage['stage']} phase={next_stage['phase']} "
            f"output={next_stage['primary_output']}"
        )
    else:
        print("  EOSB bootstrap complete; permanent operating lifecycle is active.")

    for kind, label in (("PI", "Program increments"), ("WC", "Work cycles"), ("WP", "Work packets")):
        print(f"\n{label}:")
        rows = registry(kind)
        if not rows:
            print("  none")
        for row in rows[-20:]:
            parent = ""
            if kind == "WC":
                parent = f" pi={row.get('pi','')}"
            elif kind == "WP":
                parent = f" wc={row.get('wc','')} pi={row.get('pi','')}"
            print(f"  {row['id']:<16} {row['status']:<12}{parent} {row['title']}")

    print("\nGit:")
    print(textwrap.indent(git_status(), "  "))


def cmd_next(_: argparse.Namespace) -> None:
    workflow = read_tsv(EOS / "workflow.tsv")
    row = next((r for r in workflow if r.get("status") != "COMPLETE"), None)
    if row:
        print(f"{row['stage']} — {row['phase']} — {row['primary_output']}")
        print(f"./scripts/eos prompt {row['stage']}")
        return

    active_wp = latest_active("WP")
    active_wc = latest_active("WC")
    active_pi = latest_active("PI")
    if active_wp and active_wp["status"] not in {"CLOSED"}:
        print(f"Permanent lifecycle: continue {active_wp['id']} ({active_wp['status']})")
        print(f"./scripts/eos codex {active_wp['id']}")
    elif active_wc and active_wc["status"] not in {"CLOSED"}:
        print(f"Permanent lifecycle: decompose {active_wc['id']} into the next work packet")
        print(f"./scripts/eos create-wp --wc {active_wc['id']}")
    elif active_pi and active_pi["status"] not in {"CLOSED"}:
        print(f"Permanent lifecycle: create/continue a work cycle for {active_pi['id']}")
        print(f"./scripts/eos create-wc --pi {active_pi['id']}")
    else:
        print("Permanent lifecycle: plan the next program increment")
        print("./scripts/eos plan")


def cmd_prompt(args: argparse.Namespace) -> None:
    prompt = EOS / "prompts" / f"{args.stage}.md"
    if not prompt.exists():
        raise EosError(f"No prompt registered for {args.stage}")
    workflow = read_tsv(EOS / "workflow.tsv")
    row = next((r for r in workflow if r.get("stage") == args.stage), None)
    if not row:
        raise EosError(f"Stage not found: {args.stage}")

    print(f"# Engineering Operating System Task — {args.stage}\n")
    print("## Permanent Responsibility Model\n")
    print("- Human: final authority and gate approval.")
    print("- ChatGPT: reasoning, synthesis, architecture, planning, traceability, and review.")
    print("- Codex: bounded repository-local implementation and validation after authorization.")
    print("- GitHub: canonical remote history, issues, PRs, CI, releases, and audit trail.\n")
    print("## Stage\n")
    print(f"- Phase: {row['phase']}")
    print(f"- Primary output: {row['primary_output']}")
    print(f"- Lead: {row['lead']}")
    print(f"- Reviewer: {row['reviewer']}")
    print(f"- Gate: {row['gate']}\n")
    print("## Instruction\n")
    print(prompt.read_text(encoding="utf-8").rstrip())
    print("\n## Governing Rules\n")
    print("1. Read idea.md first.")
    print("2. Respect accepted higher-authority artifacts.")
    print("3. Surface contradictions rather than silently choosing.")
    print("4. Preserve stable identifiers and traceability.")
    print("5. Do not impersonate human approval.")
    print("6. Version materially changed accepted artifacts.\n")
    idea = ROOT / "idea.md"
    if idea.exists():
        print("## Primary Inception Source\n")
        print(idea.read_text(encoding="utf-8"))


def update_bootstrap_stage(stage: str, status: str) -> None:
    path = EOS / "workflow.tsv"
    rows = read_tsv(path)
    found = False
    for row in rows:
        if row["stage"] == stage:
            row["status"] = status
            row["completed_at"] = now_iso() if status == "COMPLETE" else "-"
            found = True
            break
    if not found:
        raise EosError(f"Stage not found: {stage}")
    fields = [
        "order",
        "stage",
        "phase",
        "primary_output",
        "lead",
        "reviewer",
        "gate",
        "status",
        "completed_at",
    ]
    write_tsv(path, fields, rows)


def cmd_complete(args: argparse.Namespace) -> None:
    update_bootstrap_stage(args.stage, "COMPLETE")
    print(f"Marked {args.stage} COMPLETE.")
    print(f'Checkpoint suggestion: ./scripts/eos checkpoint "complete {args.stage}"')


def cmd_reopen(args: argparse.Namespace) -> None:
    update_bootstrap_stage(args.stage, "PENDING")
    print(f"Reopened {args.stage}.")


def cmd_version(args: argparse.Namespace) -> None:
    path = (ROOT / args.path).resolve()
    if not path.exists():
        raise EosError(f"Artifact not found: {args.path}")
    data, body = parse_frontmatter(path)
    current = data.get("version")
    if not current:
        raise EosError(f"{args.path} has no governed artifact version")
    snap = snapshot_path(path, current)
    if not snap.exists():
        snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, snap)
    new = bump_semver(current, args.kind)
    data["version"] = new
    data["updated"] = today()
    write_frontmatter(path, data, body)

    fields = [
        "timestamp",
        "artifact_id",
        "path",
        "from_version",
        "to_version",
        "change_type",
        "message",
    ]
    append_tsv(
        EOS / "artifact-changelog.tsv",
        fields,
        {
            "timestamp": now_iso(),
            "artifact_id": data.get("artifact_id", "UNREGISTERED"),
            "path": rel(path),
            "from_version": current,
            "to_version": new,
            "change_type": args.kind,
            "message": args.message,
        },
    )
    source_id = data.get("artifact_id", "UNREGISTERED")
    stale_created = mark_dependents_stale(
        source_id,
        f"{source_id} changed {current} -> {new}: {args.message}",
    )
    print(f"{rel(path)}: {current} -> {new} ({args.message})")
    if stale_created:
        print(f"Marked {len(stale_created)} downstream artifact(s) stale: {', '.join(stale_created)}")


def cmd_history(args: argparse.Namespace) -> None:
    path = (ROOT / args.path).resolve()
    data, _ = parse_frontmatter(path) if path.exists() else ({}, "")
    print(f"Artifact: {data.get('artifact_id', 'UNREGISTERED')}")
    print(f"Path: {rel(path)}\n")
    print("Semantic artifact history:")
    for row in read_tsv(EOS / "artifact-changelog.tsv"):
        if row.get("path") == rel(path):
            print(
                f"  {row['timestamp']} {row['from_version']} -> {row['to_version']} "
                f"{row['change_type']} {row['message']}"
            )
    base = EOS / "history" / Path(rel(path)).with_suffix("")
    print("\nRetained snapshots:")
    if base.exists():
        for p in sorted(base.glob("*")):
            print(f"  {rel(p)}")
    else:
        print("  none")
    if git_available():
        print("\nGit history:")
        result = run(["git", "log", "--oneline", "--follow", "--", rel(path)], cwd=ROOT, check=False)
        print(textwrap.indent(result.stdout.strip() or "none", "  "))


def cmd_rollback(args: argparse.Namespace) -> None:
    path = (ROOT / args.path).resolve()
    if not path.exists():
        raise EosError(f"Current artifact not found: {args.path}")
    data, _ = parse_frontmatter(path)
    current = data.get("version")
    if not current:
        raise EosError(f"{args.path} is not a governed artifact")
    target = args.version.removeprefix("v")
    target_path = snapshot_path(path, target)
    if not target_path.exists():
        raise EosError(f"No retained snapshot for {args.path} v{target}")

    current_snap = snapshot_path(path, current)
    if not current_snap.exists():
        current_snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, current_snap)

    restored_data, restored_body = parse_frontmatter(target_path)
    new_version = bump_semver(current, "patch")
    restored_data["version"] = new_version
    restored_data["updated"] = today()
    write_frontmatter(path, restored_data, restored_body)

    fields = [
        "timestamp",
        "artifact_id",
        "path",
        "from_version",
        "to_version",
        "change_type",
        "message",
    ]
    append_tsv(
        EOS / "artifact-changelog.tsv",
        fields,
        {
            "timestamp": now_iso(),
            "artifact_id": restored_data.get("artifact_id", "UNREGISTERED"),
            "path": rel(path),
            "from_version": current,
            "to_version": new_version,
            "change_type": "rollback",
            "message": f"RESTORE v{target}: {args.message}",
        },
    )
    source_id = restored_data.get("artifact_id", "UNREGISTERED")
    stale_created = mark_dependents_stale(
        source_id,
        f"{source_id} rollback restored v{target} as v{new_version}: {args.message}",
    )
    print(f"Restored v{target} content as new version v{new_version}.")
    if stale_created:
        print(f"Marked {len(stale_created)} downstream artifact(s) stale: {', '.join(stale_created)}")


def cmd_checkpoint(args: argparse.Namespace) -> None:
    if not git_available():
        raise EosError("git is required for checkpoints")
    stamp = dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    meta = EOS / "checkpoints" / f"{stamp}.txt"
    meta.write_text(f"timestamp={now_iso()}\nmessage={args.message}\n", encoding="utf-8")
    run(["git", "add", "-A"], cwd=ROOT)
    diff = run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
    if diff.returncode == 0:
        meta.unlink(missing_ok=True)
        print("No changes to checkpoint.")
        return
    run(["git", "commit", "-m", f"checkpoint: {args.message}"], cwd=ROOT, capture=False)
    tag = f"eos/checkpoint-{stamp}"
    run(["git", "tag", "-a", tag, "-m", args.message], cwd=ROOT, capture=False)
    print(f"Created {tag} at {commit_sha()[:12]}")


def pi_body(pi_id: str, title: str, objective: str) -> str:
    return f"""# {pi_id} — {title}

**State:** DRAFT

## Objective

{objective}

## Intended Outcomes

TBD.

## Governing Artifacts

TBD.

## Included Work Cycles

TBD.

## Scope

### In Scope

TBD.

### Out of Scope

TBD.

## Dependencies

TBD.

## Risks

TBD.

## Entry Criteria

- [ ] Governing requirements are accepted.
- [ ] Architecture/specification deltas are understood.
- [ ] Dependencies are identified.
- [ ] PI readiness review is accepted.

## Exit Criteria

- [ ] Included work cycles are closed.
- [ ] PI acceptance evidence is complete.
- [ ] PI closeout review is accepted.
"""


def cmd_plan(args: argparse.Namespace) -> None:
    if args.pi:
        if not re.fullmatch(r"PI-\d{3}", args.pi):
            raise EosError("PI id must look like PI-002")
        pi_id = args.pi
    else:
        pi_id = f"PI-{next_number('PI', 3):03d}"
    if find_row("PI", pi_id):
        raise EosError(f"{pi_id} already exists")

    title = args.title or f"Program Increment {pi_id.split('-')[1]}"
    objective = args.objective or "TBD."
    path = ROOT / "engineering" / "increments" / f"{pi_id}.md"
    create_artifact(path, pi_id, title, "program-increment", "planning-authoritative", pi_body(pi_id, title, objective))
    rows = registry("PI")
    rows.append(
        {
            "id": pi_id,
            "path": rel(path),
            "title": title,
            "status": "DRAFT",
            "created": now_iso(),
            "updated": now_iso(),
            "github_url": "",
        }
    )
    save_registry("PI", rows)
    append_event(
        "ENTITY_CREATED",
        target=pi_id,
        entity_kind="PI",
        action="plan",
        to_state="DRAFT",
        reason="program increment created",
        metadata={"row": rows[-1]},
    )
    print(f"Created {pi_id}: {rel(path)}")
    print(f"Next: complete the PI definition, then ./scripts/eos ready {pi_id}")


def wc_body(wc_id: str, title: str, pi: str) -> str:
    return f"""# {wc_id} — {title}

**State:** DRAFT

## Objective

TBD.

## Parent Program Increment

- {pi}

## Included Work Packets

TBD.

## Scope

### In Scope

TBD.

### Out of Scope

TBD.

## Dependencies

TBD.

## Entry Criteria

- [ ] Parent PI is authorized.
- [ ] Scope is bounded.
- [ ] Required work packets can be defined.

## Exit Criteria

- [ ] All included work packets are closed.
- [ ] Work-cycle review is accepted.
"""


def cmd_create_wc(args: argparse.Namespace) -> None:
    pi = args.pi
    if not pi:
        row = latest_active("PI")
        if not row:
            raise EosError("No active PI; create one with ./scripts/eos plan")
        pi = row["id"]
    pi_row = find_row("PI", pi)
    if not pi_row:
        raise EosError(f"Unknown parent PI: {pi}")
    wc_id = f"WC-{next_number('WC', 4):04d}"
    title = args.title or f"Work Cycle {wc_id.split('-')[1]}"
    path = ROOT / "engineering" / "work-cycles" / f"{wc_id}.md"
    create_artifact(path, wc_id, title, "work-cycle", "planning-authoritative", wc_body(wc_id, title, pi))
    rows = registry("WC")
    rows.append(
        {
            "id": wc_id,
            "path": rel(path),
            "title": title,
            "status": "DRAFT",
            "pi": pi,
            "created": now_iso(),
            "updated": now_iso(),
            "github_url": "",
        }
    )
    save_registry("WC", rows)
    append_event(
        "ENTITY_CREATED",
        target=wc_id,
        entity_kind="WC",
        action="create-wc",
        to_state="DRAFT",
        reason="work cycle created",
        metadata={"row": rows[-1]},
    )
    print(f"Created {wc_id} under {pi}: {rel(path)}")
    print(f"Next: complete the work-cycle definition, then ./scripts/eos ready {wc_id}")


def wp_body(wp_id: str, title: str, pi: str, wc: str) -> str:
    return f"""# {wp_id} — {title}

**State:** DRAFT

## Objective

TBD.

## Parent

- PI: {pi}
- Work Cycle: {wc}

## Scope

### In Scope

TBD.

### Out of Scope

TBD.

## Governing Artifacts

- Requirements: TBD
- Specifications: TBD
- ADRs: TBD
- Quality attributes: TBD

## Dependencies

TBD.

## Deliverables

TBD.

## Acceptance Criteria

- [ ] TBD

## Validation

TBD.

## Risks

TBD.

## Completion Evidence

TBD.
"""


def cmd_create_wp(args: argparse.Namespace) -> None:
    wc = args.wc
    if not wc:
        row = latest_active("WC")
        if not row:
            raise EosError("No active work cycle; create one with ./scripts/eos create-wc")
        wc = row["id"]
    wc_row = find_row("WC", wc)
    if not wc_row:
        raise EosError(f"Unknown parent work cycle: {wc}")
    pi = wc_row["pi"]

    domain = args.domain.upper() if args.domain else ""
    if domain and not re.fullmatch(r"[A-Z][A-Z0-9]{1,15}", domain):
        raise EosError("Domain must be 2-16 uppercase alphanumeric characters")
    number = next_number("WP", 4, prefix=domain or None)
    wp_id = f"WP-{domain}-{number:04d}" if domain else f"WP-{number:04d}"
    title = args.title or f"Work Packet {wp_id}"
    path = ROOT / "engineering" / "work-packets" / f"{wp_id}.md"
    create_artifact(path, wp_id, title, "work-packet", "planning-authoritative", wp_body(wp_id, title, pi, wc))
    rows = registry("WP")
    rows.append(
        {
            "id": wp_id,
            "path": rel(path),
            "title": title,
            "status": "DRAFT",
            "pi": pi,
            "wc": wc,
            "domain": domain,
            "created": now_iso(),
            "updated": now_iso(),
            "github_url": "",
        }
    )
    save_registry("WP", rows)
    append_event(
        "ENTITY_CREATED",
        target=wp_id,
        entity_kind="WP",
        action="create-wp",
        to_state="DRAFT",
        reason="work packet created",
        metadata={"row": rows[-1]},
    )
    print(f"Created {wp_id} under {wc}/{pi}: {rel(path)}")
    print(f"Next: complete the work-packet definition, then ./scripts/eos ready {wp_id}")



def cmd_ready(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind not in {"PI", "WC", "WP"}:
        raise EosError("ready applies to PI, WC, or WP")

    destination = {"PI": "PLANNED", "WC": "READY", "WP": "READY"}[kind]
    gate_name = f"{kind}_READY"
    override = enforce_gate(
        gate_name,
        args.target,
        actor=getattr(args, "by", ""),
        reason=getattr(args, "reason", ""),
    )
    set_lifecycle_state(
        args.target,
        destination,
        action="ready",
        actor=actor_name(getattr(args, "by", "")),
        reason=getattr(args, "reason", "") or "definition complete enough for next gate",
    )
    if override:
        consume_override(override)
    print(f"{args.target} -> {destination}")



def cmd_authorize(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind not in {"PI", "WC", "WP"}:
        raise EosError("authorize currently applies to PI, WC, or WP")
    gate_name = f"{kind}_AUTHORIZE"
    actor = args.by or os.environ.get("USER") or "human"
    if args.force and not args.reason.strip():
        raise EosError("--force requires an explicit --reason so a durable override can be recorded")
    reason = args.reason or "human authorization"
    override = enforce_gate(
        gate_name,
        args.target,
        force=args.force,
        actor=actor,
        reason=reason if args.force else args.reason,
    )
    set_lifecycle_state(
        args.target,
        "AUTHORIZED",
        action="authorize",
        actor=actor,
        reason=reason if not override else f"authorized under {override['id']}: {override['reason']}",
    )
    if override:
        consume_override(override)
    record_decision(args.target, "authorize", "AUTHORIZED", actor, reason)
    print(f"{args.target} AUTHORIZED by {actor}.")



def cmd_start(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    current = row["status"]
    if kind == "PI":
        allowed, new = {"AUTHORIZED", "ACTIVE"}, "ACTIVE"
    elif kind == "WC":
        allowed, new = {"AUTHORIZED", "ACTIVE"}, "ACTIVE"
    elif kind == "WP":
        allowed, new = {"AUTHORIZED", "IN_PROGRESS"}, "IN_PROGRESS"
    elif kind == "MNT":
        allowed, new = {"OPEN", "PLANNED", "IN_PROGRESS"}, "IN_PROGRESS"
    else:
        raise EosError(f"start is not supported for {kind}")
    if current not in allowed:
        raise EosError(f"{args.target} cannot start from state {current}")
    set_lifecycle_state(
        args.target,
        new,
        action="start",
        actor=actor_name(),
        reason="authorized execution started",
    )
    print(f"{args.target} -> {new}")


def referenced_ids(path: Path) -> list[str]:
    if not path.exists():
        return []
    ids = sorted(set(ID_RE.findall(path.read_text(encoding="utf-8", errors="ignore"))))
    data, _ = parse_frontmatter(path) if path.suffix == ".md" else ({}, "")
    own = data.get("artifact_id")
    return [x for x in ids if x != own]


def cmd_codex(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "WP":
        raise EosError("Codex execution contracts are generated for work packets")
    if row["status"] not in {"AUTHORIZED", "IN_PROGRESS", "VERIFYING"} and not args.force:
        raise EosError(
            f"{args.target} is {row['status']}; authorize it before generating an execution contract"
        )
    path = ROOT / row["path"]
    refs = referenced_ids(path)
    related: list[Path] = []
    for rid in refs:
        p = artifact_path_for_id(rid)
        if p and p.exists():
            related.append(p)
    for parent in (row.get("pi"), row.get("wc")):
        if parent:
            p = artifact_path_for_id(parent)
            if p and p.exists():
                related.append(p)

    contract = EOS / "contracts" / f"{args.target}.codex.md"
    parts = [
        f"# Codex Execution Contract — {args.target}",
        "",
        f"Generated: {now_iso()}",
        f"Repository: {ROOT}",
        f"Branch: {current_branch() or '(detached/unknown)'}",
        f"HEAD: {commit_sha() or '(no commit yet)'}",
        "",
        "## Authority",
        "",
        "This contract authorizes bounded implementation only. Codex must not invent or",
        "silently modify product requirements, architecture policy, specifications,",
        "security policy, or scope to make implementation easier.",
        "",
        "## Work Packet",
        "",
        path.read_text(encoding="utf-8"),
        "",
        "## Governing / Related Artifacts",
        "",
    ]
    for p in sorted(set(related), key=lambda x: rel(x)):
        parts.extend([f"### {rel(p)}", "", p.read_text(encoding="utf-8"), ""])
    parts.extend(
        [
            "## Required Operating Procedure",
            "",
            "1. Inspect repository state before modifying files.",
            "2. Create or use a branch scoped to this work packet.",
            "3. Modify only the authorized scope.",
            "4. Preserve identifiers and traceability.",
            "5. Run all repository-prescribed validation plus WP-specific validation.",
            "6. Run `./scripts/eos verify`.",
            "7. Report exact changed files, commands, results, and unresolved findings.",
            "8. Stop and escalate if implementation requires changing governing policy.",
            "",
            "## Required Completion Report",
            "",
            "- Changed files",
            "- Implementation summary",
            "- Acceptance criteria mapping",
            "- Validation commands and results",
            "- Risks / unresolved issues",
            "- Proposed commit message",
            "- Proposed PR title/body",
            "",
        ]
    )
    contract.write_text("\n".join(parts), encoding="utf-8")
    print(contract.read_text(encoding="utf-8"))
    print(f"\nContract persisted to {rel(contract)}", file=sys.stderr)


def run_validation_commands() -> list[tuple[str, int, str]]:
    config = EOS / "validation.commands"
    results: list[tuple[str, int, str]] = []
    if not config.exists():
        return results
    for raw in config.read_text(encoding="utf-8").splitlines():
        cmd = raw.strip()
        if not cmd or cmd.startswith("#"):
            continue
        proc = subprocess.run(
            ["bash", "-lc", cmd],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        output = (proc.stdout + proc.stderr).strip()
        results.append((cmd, proc.returncode, output))
    return results


def cmd_validate(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind == "WP":
        if row["status"] == "AUTHORIZED":
            raise EosError(
                f"{args.target} is AUTHORIZED; start it first with ./scripts/eos start {args.target}"
            )
        if row["status"] == "IN_PROGRESS":
            set_lifecycle_state(
                args.target,
                "VERIFYING",
                action="validate",
                actor=actor_name(),
                reason="deterministic verification started",
            )
        elif row["status"] != "VERIFYING":
            raise EosError(
                f"{args.target} must be IN_PROGRESS or VERIFYING before validation; "
                f"current state is {row['status']}"
            )
    verify_ok, verify_report = verify_all(strict=True)
    custom = run_validation_commands()
    stamp = dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    evidence = EOS / "evidence" / f"{args.target}-{stamp}.md"
    lines = [
        f"# Verification Evidence — {args.target}",
        "",
        f"Generated: {now_iso()}",
        f"HEAD: {commit_sha() or '(none)'}",
        "",
        "## EOS Integrity",
        "",
        "```text",
        verify_report,
        "```",
        "",
        "## Repository Validation Commands",
        "",
    ]
    if custom:
        for command, rc, output in custom:
            lines += [
                f"### `{command}`",
                "",
                f"Exit code: {rc}",
                "",
                "```text",
                output[:20000],
                "```",
                "",
            ]
    else:
        lines.append("No additional commands configured in `.eos/validation.commands`.")
    evidence.write_text("\n".join(lines) + "\n", encoding="utf-8")
    failures = [cmd for cmd, rc, _ in custom if rc != 0]
    print(f"Verification evidence: {rel(evidence)}")
    if not verify_ok or failures:
        raise EosError("Verification failed; inspect the evidence artifact.")
    print("Verification passed.")


def review_body(target: str, row: dict[str, str], verify_ok: bool, report: str) -> str:
    return f"""# {target} — Engineering Review

**Decision:** PENDING

## Target

- Artifact: `{row['path']}`
- State at review start: {row['status']}
- Review generated: {now_iso()}
- Git HEAD: {commit_sha() or '(none)'}

## Deterministic Verification

**Result:** {'PASS' if verify_ok else 'FAIL'}

```text
{report}
```

## Scope Conformance

TBD.

## Requirements / Specification Conformance

TBD.

## Architecture Conformance

TBD.

## Acceptance Criteria Evidence

TBD.

## Test / Validation Evidence

TBD.

## Security / Reliability Findings

TBD.

## Traceability Findings

TBD.

## Blocking Findings

TBD.

## Non-Blocking Findings

TBD.

## Decision

Set the top-level `**Decision:**` to one of:

- ACCEPTED
- ACCEPTED_WITH_FOLLOW_UP
- REJECTED
- BLOCKED
"""


def cmd_review(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    verify_ok, report = verify_all()
    path = review_path(args.target)
    if not path.exists():
        create_artifact(
            path,
            f"REV-{args.target}",
            f"{args.target} Engineering Review",
            "review",
            "review-authoritative",
            review_body(args.target, row, verify_ok, report),
            status="In Review",
        )
    else:
        # Preserve human content; add a deterministic evidence companion instead.
        stamp = dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        evidence = EOS / "evidence" / f"{args.target}-review-{stamp}.md"
        evidence.write_text(report + "\n", encoding="utf-8")
    if kind in {"PI", "WC", "WP"}:
        set_lifecycle_state(
            args.target,
            "IN_REVIEW",
            action="review",
            actor=actor_name(),
            reason="engineering review started",
        )
    contract = EOS / "contracts" / f"{args.target}.review.md"
    target_path = ROOT / row["path"]
    contract.write_text(
        f"""# ChatGPT Review Contract — {args.target}

Review the target against all applicable accepted higher-authority artifacts.

## Target

{target_path.read_text(encoding='utf-8')}

## Required Review Dimensions

- scope conformance;
- requirements and specification conformance;
- architecture conformance;
- acceptance criteria;
- deterministic validation evidence;
- security/reliability risk;
- traceability completeness;
- unresolved findings;
- recommendation: ACCEPTED / ACCEPTED_WITH_FOLLOW_UP / REJECTED / BLOCKED.

Do not impersonate final human authorization where the governance model reserves
that decision to the human.
""",
        encoding="utf-8",
    )
    print(f"Review artifact: {rel(path)}")
    print(f"Review contract: {rel(contract)}")
    print(f"Deterministic verification: {'PASS' if verify_ok else 'FAIL'}")


def unchecked_boxes(path: Path) -> int:
    if not path.exists():
        return 0
    return len(re.findall(r"^- \[ \]", path.read_text(encoding="utf-8"), flags=re.M))


def cmd_close(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "WP":
        raise EosError("Use close-cycle or close-pi for WC/PI")
    actor = args.by or os.environ.get("USER") or "human"
    override = enforce_gate(
        "WP_CLOSE",
        args.target,
        force=args.force,
        actor=actor,
        reason=args.reason,
    )
    set_lifecycle_state(
        args.target,
        "CLOSED",
        action="close",
        actor=actor,
        reason=args.reason or (
            f"closure under {override['id']}" if override else "closure gate satisfied"
        ),
    )
    if override:
        consume_override(override)
    record_decision(args.target, "close", "CLOSED", actor, args.reason or "work packet closure")
    print(f"{args.target} CLOSED.")



def cmd_close_cycle(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "WC":
        raise EosError("close-cycle requires a WC id")
    actor = args.by or os.environ.get("USER") or "human"
    override = enforce_gate(
        "WC_CLOSE",
        args.target,
        force=args.force,
        actor=actor,
        reason=args.reason,
    )
    set_lifecycle_state(
        args.target,
        "CLOSED",
        action="close-cycle",
        actor=actor,
        reason=args.reason or (
            f"closure under {override['id']}" if override else "work-cycle closure gate satisfied"
        ),
    )
    if override:
        consume_override(override)
    record_decision(args.target, "close-cycle", "CLOSED", actor, args.reason or "work cycle closure")
    print(f"{args.target} CLOSED.")



def cmd_close_pi(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "PI":
        raise EosError("close-pi requires a PI id")
    actor = args.by or os.environ.get("USER") or "human"
    override = enforce_gate(
        "PI_CLOSE",
        args.target,
        force=args.force,
        actor=actor,
        reason=args.reason,
    )
    set_lifecycle_state(
        args.target,
        "CLOSED",
        action="close-pi",
        actor=actor,
        reason=args.reason or (
            f"closure under {override['id']}" if override else "program-increment closure gate satisfied"
        ),
    )
    if override:
        consume_override(override)
    record_decision(args.target, "close-pi", "CLOSED", actor, args.reason or "program increment closure")
    print(f"{args.target} CLOSED.")




def stale_rows() -> list[dict[str, str]]:
    return read_tsv(STALE_PATH)


def save_stale(rows: list[dict[str, str]]) -> None:
    write_tsv(STALE_PATH, STALE_FIELDS, rows)


def next_stale_id() -> str:
    nums: list[int] = []
    for row in stale_rows():
        match = re.fullmatch(r"STL-(\d{4})", row.get("id", ""))
        if match:
            nums.append(int(match.group(1)))
    return f"STL-{max(nums, default=0) + 1:04d}"


def strip_fenced_code(text: str) -> str:
    """Remove fenced Markdown code blocks so documentation examples do not become graph edges."""
    out: list[str] = []
    in_fence = False
    fence = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            token = stripped[:3]
            if not in_fence:
                in_fence = True
                fence = token
            elif token == fence:
                in_fence = False
                fence = ""
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def stale_relevant_target(target: str) -> bool:
    path = artifact_path_for_id(target)
    if path and path.suffix == ".md":
        data, _ = parse_frontmatter(path)
        authority = data.get("authority", "")
        artifact_type = data.get("type", "")
        if authority in {"historical", "informative", "historical-source"}:
            return False
        if artifact_type in {"journal", "index", "template"}:
            return False
    return not target.startswith("FILE:")


def infer_edge_type(source: str, target: str) -> str:
    if source.startswith("WP-"):
        if target.startswith("REQ-"):
            return "implements"
        if target.startswith("SPEC-"):
            return "satisfies"
        if target.startswith(("ADR-", "QA-")):
            return "conforms-to"
    if source.startswith("SPEC-"):
        if target.startswith(("REQ-", "CAP-")):
            return "satisfies"
        if target.startswith(("ADR-", "QA-")):
            return "constrained-by"
    if source.startswith("ADR-"):
        if target.startswith(("REQ-", "QA-", "SPEC-")):
            return "constrains"
    if source.startswith("CR-"):
        return "affects"
    if source.startswith("MNT-"):
        return "affects"
    if source.startswith("REL-"):
        return "includes"
    return "references"


def impacted_entities(source_id: str, *, transitive: bool = True) -> list[dict[str, str]]:
    edges = rebuild_trace()
    reverse: dict[str, list[dict[str, str]]] = {}
    for edge in edges:
        reverse.setdefault(edge["target_id"], []).append(edge)

    queue = deque([(source_id, 0)])
    seen = {source_id}
    out: list[dict[str, str]] = []
    while queue:
        node, depth = queue.popleft()
        for edge in sorted(
            reverse.get(node, []),
            key=lambda e: (e["source_id"], e["edge_type"], e["source_path"]),
        ):
            dependent = edge["source_id"]
            if dependent in seen:
                continue
            seen.add(dependent)
            row = dict(edge)
            row["depth"] = str(depth + 1)
            out.append(row)
            if transitive:
                queue.append((dependent, depth + 1))
    return out


def mark_dependents_stale(source_id: str, reason: str) -> list[str]:
    if not source_id or source_id in {"UNREGISTERED", "INCEPT-IDEA-0001"}:
        return []
    impacts = impacted_entities(source_id, transitive=True)
    rows = stale_rows()
    open_pairs = {(r.get("target"), r.get("source")) for r in rows if r.get("status") == "OPEN"}
    created: list[str] = []
    for impact in impacts:
        target = impact["source_id"]
        if target == source_id or not stale_relevant_target(target):
            continue
        pair = (target, source_id)
        if pair in open_pairs:
            continue
        stale_id = next_stale_id()
        # next_stale_id() reads disk, so account for rows not yet persisted.
        if created:
            stale_id = f"STL-{int(created[-1].split('-')[1]) + 1:04d}"
        row = {
            "id": stale_id,
            "target": target,
            "source": source_id,
            "reason": reason,
            "status": "OPEN",
            "created": now_iso(),
            "cleared_at": "",
            "cleared_by": "",
            "clear_reason": "",
        }
        rows.append(row)
        open_pairs.add(pair)
        created.append(stale_id)
        append_event(
            "DEPENDENT_MARKED_STALE",
            target=target,
            action="trace-stale",
            reason=reason,
            metadata={
                "stale_id": stale_id,
                "source": source_id,
                "depth": impact.get("depth", ""),
                "edge_type": impact.get("edge_type", ""),
            },
        )
    if created:
        save_stale(rows)
    return created


def cmd_stale_list(args: argparse.Namespace) -> None:
    rows = stale_rows()
    if not args.all:
        rows = [r for r in rows if r.get("status") == "OPEN"]
    if args.target:
        rows = [r for r in rows if r.get("target") == args.target or r.get("source") == args.target]
    if not rows:
        print("No matching stale records.")
        return
    for row in rows:
        print(
            f"{row['id']}  {row['status']:<7}  target={row['target']:<20} "
            f"source={row['source']:<20} {row['reason']}"
        )


def cmd_stale_clear(args: argparse.Namespace) -> None:
    rows = stale_rows()
    matched = False
    for row in rows:
        if row.get("id") == args.stale_id:
            matched = True
            if row.get("status") != "OPEN":
                raise EosError(f"{args.stale_id} is {row.get('status')}, not OPEN")
            if not args.reason.strip():
                raise EosError("Clearing stale state requires --reason")
            row["status"] = "CLEARED"
            row["cleared_at"] = now_iso()
            row["cleared_by"] = actor_name(args.by)
            row["clear_reason"] = args.reason.strip()
            append_event(
                "STALE_CLEARED",
                target=row.get("target", ""),
                action="stale-clear",
                actor=row["cleared_by"],
                reason=row["clear_reason"],
                metadata={"stale_id": row["id"], "source": row.get("source", "")},
            )
            break
    if not matched:
        raise EosError(f"Unknown stale record: {args.stale_id}")
    save_stale(rows)
    print(f"{args.stale_id} CLEARED.")



def candidate_trace_files() -> Iterable[Path]:
    # Trace governing/project artifacts, not generated EOS state, contracts,
    # templates, tooling, or documentation examples. This keeps impact analysis
    # semantically useful instead of treating example IDs as real dependencies.
    allowed = {".md", ".yml", ".yaml", ".toml"}
    excluded_prefixes = (
        ".git/",
        ".eos/",
        "tools/",
        "engineering/lifecycle/",
        "engineering/prompts/",
    )
    excluded_names = {
        "README.md",
        "template.md",
        "ADR-0000-template.md",
    }
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        rp = rel(path)
        if rp in excluded_names or path.name in excluded_names:
            continue
        if rp.startswith(excluded_prefixes):
            continue
        yield path


def source_id_for(path: Path) -> str:
    if path.suffix == ".md":
        data, _ = parse_frontmatter(path)
        if data.get("artifact_id"):
            return data["artifact_id"]
    stem = path.stem
    m = ID_RE.search(stem)
    return m.group(0) if m else f"FILE:{rel(path)}"


def rebuild_trace() -> list[dict[str, str]]:
    edges: dict[tuple[str, str, str, str], dict[str, str]] = {}

    # Structural lifecycle edges are authoritative and do not depend on prose.
    for wc in registry("WC"):
        key = (wc["pi"], wc["id"], "contains", wc["path"])
        edges[key] = {
            "source_id": wc["pi"],
            "target_id": wc["id"],
            "edge_type": "contains",
            "source_path": wc["path"],
            "evidence": "lifecycle-registry",
        }
    for wp in registry("WP"):
        key = (wp["wc"], wp["id"], "contains", wp["path"])
        edges[key] = {
            "source_id": wp["wc"],
            "target_id": wp["id"],
            "edge_type": "contains",
            "source_path": wp["path"],
            "evidence": "lifecycle-registry",
        }
    for cr in registry("CR"):
        target = cr.get("target", "")
        if target:
            key = (cr["id"], target, "affects", cr["path"])
            edges[key] = {
                "source_id": cr["id"],
                "target_id": target,
                "edge_type": "affects",
                "source_path": cr["path"],
                "evidence": "change-registry",
            }

    for path in candidate_trace_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        source = source_id_for(path)
        scan_text = strip_fenced_code(text) if path.suffix == ".md" else text
        explicit_pairs: set[tuple[str, str]] = set()

        for lineno, line in enumerate(scan_text.splitlines(), start=1):
            m = EXPLICIT_RELATION_RE.match(line)
            if not m:
                continue
            edge_type = m.group(1).lower()
            target = m.group(2)
            if target == source:
                continue
            explicit_pairs.add((source, target))
            key = (source, target, edge_type, rel(path))
            edges[key] = {
                "source_id": source,
                "target_id": target,
                "edge_type": edge_type,
                "source_path": rel(path),
                "evidence": f"explicit-line:{lineno}",
            }

        for target in set(ID_RE.findall(scan_text)):
            if target == source or (source, target) in explicit_pairs:
                continue
            edge_type = infer_edge_type(source, target)
            key = (source, target, edge_type, rel(path))
            edges[key] = {
                "source_id": source,
                "target_id": target,
                "edge_type": edge_type,
                "source_path": rel(path),
                "evidence": "inferred-reference",
            }

    fields = ["source_id", "target_id", "edge_type", "source_path", "evidence"]
    rows = sorted(
        edges.values(),
        key=lambda r: (r["source_id"], r["target_id"], r["edge_type"], r["source_path"]),
    )
    write_tsv(EOS / "trace-edges.tsv", fields, rows)
    return rows


def trace_coverage_report() -> dict:
    edges = rebuild_trace()
    nodes: set[str] = set()
    for edge in edges:
        nodes.add(edge["source_id"])
        nodes.add(edge["target_id"])
    for kind in ("PI", "WC", "WP", "CR", "MNT", "REL"):
        nodes.update(row["id"] for row in registry(kind))

    requirements = sorted(n for n in nodes if n.startswith("REQ-"))
    specifications = sorted(n for n in nodes if n.startswith("SPEC-"))
    work_packets = sorted(row["id"] for row in registry("WP"))

    incoming: dict[str, list[dict[str, str]]] = {}
    outgoing: dict[str, list[dict[str, str]]] = {}
    for edge in edges:
        incoming.setdefault(edge["target_id"], []).append(edge)
        outgoing.setdefault(edge["source_id"], []).append(edge)

    req_uncovered = [
        req
        for req in requirements
        if not any(
            e["source_id"].startswith(("SPEC-", "WP-"))
            and e["edge_type"] in {"implements", "satisfies", "references"}
            for e in incoming.get(req, [])
        )
    ]
    spec_untraced = [
        spec
        for spec in specifications
        if not any(e["target_id"].startswith(("REQ-", "CAP-", "ADR-", "QA-")) for e in outgoing.get(spec, []))
    ]
    wp_untraced = [
        wp
        for wp in work_packets
        if not any(
            e["target_id"].startswith(("REQ-", "SPEC-", "ADR-", "QA-"))
            for e in outgoing.get(wp, [])
        )
    ]
    closed_without_evidence = []
    for row in registry("WP"):
        if row["status"] != "CLOSED":
            continue
        if not list((EOS / "evidence").glob(f"{row['id']}-*")):
            closed_without_evidence.append(row["id"])

    total = len(requirements) + len(specifications) + len(work_packets)
    gaps = len(req_uncovered) + len(spec_untraced) + len(wp_untraced)
    score = 100.0 if total == 0 else max(0.0, 100.0 * (total - gaps) / total)

    return {
        "score": round(score, 1),
        "requirements": len(requirements),
        "specifications": len(specifications),
        "work_packets": len(work_packets),
        "requirement_gaps": req_uncovered,
        "specification_gaps": spec_untraced,
        "work_packet_gaps": wp_untraced,
        "closed_wp_without_evidence": closed_without_evidence,
    }


def cmd_trace(args: argparse.Namespace) -> None:
    if args.target.lower() == "coverage":
        report = trace_coverage_report()
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
            return
        print(f"TRACEABILITY COVERAGE — {report['score']:.1f}%")
        print(
            f"requirements={report['requirements']} "
            f"specifications={report['specifications']} "
            f"work_packets={report['work_packets']}"
        )
        for label, key in (
            ("Requirements without implementation/spec trace", "requirement_gaps"),
            ("Specifications without governing trace", "specification_gaps"),
            ("Work packets without governing trace", "work_packet_gaps"),
            ("Closed work packets without evidence", "closed_wp_without_evidence"),
        ):
            values = report[key]
            print(f"\n{label}:")
            if values:
                for value in values:
                    print(f"  - {value}")
            else:
                print("  none")
        return

    edges = rebuild_trace()
    target = args.target
    path = artifact_path_for_id(target)
    outgoing = [e for e in edges if e["source_id"] == target]
    incoming = [e for e in edges if e["target_id"] == target]

    if args.json:
        print(
            json.dumps(
                {
                    "target": target,
                    "artifact": rel(path) if path else "",
                    "outgoing": outgoing,
                    "incoming": incoming,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return

    print(f"TRACE — {target}")
    print(f"Artifact: {rel(path) if path else '(not directly located)'}\n")

    print("Outgoing relationships:")
    if outgoing:
        for e in outgoing:
            print(
                f"  {e['edge_type']:<16} {e['target_id']:<20} "
                f"via {e['source_path']} ({e['evidence']})"
            )
    else:
        print("  none discovered")

    print("\nIncoming relationships:")
    if incoming:
        for e in incoming:
            print(
                f"  {e['source_id']:<20} {e['edge_type']:<16} "
                f"via {e['source_path']} ({e['evidence']})"
            )
    else:
        print("  none discovered")


def impact_class(edge_type: str, entity: str) -> str:
    if edge_type in {"implements", "satisfies"} or entity.startswith("WP-"):
        return "implementation"
    if edge_type in {"conforms-to", "constrained-by", "constrains"} or entity.startswith(("ADR-", "SPEC-")):
        return "architecture/specification"
    if edge_type == "contains" or entity.startswith(("PI-", "WC-")):
        return "planning"
    if edge_type in {"affects", "includes"}:
        return "change/release"
    return "reference"


def cmd_impact(args: argparse.Namespace) -> None:
    results = impacted_entities(args.target, transitive=True)
    enriched = [
        {
            **row,
            "impact_class": impact_class(row["edge_type"], row["source_id"]),
        }
        for row in results
    ]

    if args.json:
        print(json.dumps({"target": args.target, "impacts": enriched}, indent=2, sort_keys=True))
        return

    print(f"IMPACT ANALYSIS — {args.target}\n")
    if not enriched:
        print("No downstream references discovered.")
        return
    for row in enriched:
        depth = int(row["depth"])
        print(
            f"{'  ' * (depth - 1)}- {row['source_id']} "
            f"[{row['impact_class']}; {row['edge_type']}; {row['source_path']}]"
        )




def pi_work_packets(pi_id: str) -> list[dict[str, str]]:
    return [row for row in registry("WP") if row.get("pi") == pi_id]


def wp_dependency_map(pi_id: str) -> tuple[dict[str, set[str]], list[str]]:
    wps = {row["id"]: row for row in pi_work_packets(pi_id)}
    deps: dict[str, set[str]] = {wp_id: set() for wp_id in wps}
    errors: list[str] = []
    for edge in rebuild_trace():
        if edge["edge_type"] != "depends-on":
            continue
        source = edge["source_id"]
        target = edge["target_id"]
        if source not in wps:
            continue
        if not target.startswith("WP-"):
            errors.append(f"{source} depends-on non-WP target {target}")
            continue
        if not find_row("WP", target):
            errors.append(f"{source} depends on unknown work packet {target}")
            continue
        deps[source].add(target)
    return deps, errors


def topological_wp_order(pi_id: str) -> tuple[list[str], list[str]]:
    deps, errors = wp_dependency_map(pi_id)
    if errors:
        return [], errors
    nodes = set(deps)
    # Include cross-PI dependencies as prerequisite nodes for cycle detection
    # only when they are themselves in the requested PI; external dependencies
    # are reported separately by planning checks.
    indegree = {node: 0 for node in nodes}
    dependents: dict[str, set[str]] = {node: set() for node in nodes}
    for source, targets in deps.items():
        for target in targets:
            if target not in nodes:
                continue
            indegree[source] += 1
            dependents[target].add(source)

    ready = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    order: list[str] = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for dependent in sorted(dependents.get(node, set())):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)

    if len(order) != len(nodes):
        cyclic = sorted(node for node, degree in indegree.items() if degree > 0)
        errors.append("work-packet dependency cycle detected involving: " + ", ".join(cyclic))
        return [], errors
    return order, errors


def critical_path_for_pi(pi_id: str) -> tuple[list[str], list[str]]:
    order, errors = topological_wp_order(pi_id)
    if errors:
        return [], errors
    deps, _ = wp_dependency_map(pi_id)
    in_pi = set(order)
    distance: dict[str, int] = {}
    predecessor: dict[str, str] = {}
    for node in order:
        local_deps = [dep for dep in deps.get(node, set()) if dep in in_pi]
        if not local_deps:
            distance[node] = 1
            continue
        best = max(local_deps, key=lambda dep: distance.get(dep, 1))
        distance[node] = distance.get(best, 1) + 1
        predecessor[node] = best

    if not distance:
        return [], []
    end = max(distance, key=distance.get)
    path = [end]
    while end in predecessor:
        end = predecessor[end]
        path.append(end)
    path.reverse()
    return path, []


def wp_size_analysis(wp_id: str) -> dict:
    kind, row = row_for_target(wp_id)
    if kind != "WP":
        raise EosError("planning size requires a work-packet ID")
    path = ROOT / row["path"]
    text = path.read_text(encoding="utf-8")
    refs = referenced_ids(path)
    acceptance = len(re.findall(r"^- \[[ xX]\]", text, flags=re.M))
    headings = len(re.findall(r"^#{2,4}\s+", text, flags=re.M))
    deps, _ = wp_dependency_map(row["pi"])
    dependency_count = len(deps.get(wp_id, set()))
    score = 0
    reasons: list[str] = []

    if len(text) > 6000:
        score += 3
        reasons.append("artifact text exceeds 6000 characters")
    elif len(text) > 3500:
        score += 2
        reasons.append("artifact text exceeds 3500 characters")
    elif len(text) > 2200:
        score += 1
        reasons.append("artifact text exceeds 2200 characters")

    if acceptance > 10:
        score += 3
        reasons.append(f"{acceptance} acceptance/exit checklist items")
    elif acceptance > 6:
        score += 2
        reasons.append(f"{acceptance} acceptance/exit checklist items")
    elif acceptance > 3:
        score += 1
        reasons.append(f"{acceptance} acceptance/exit checklist items")

    if len(refs) > 10:
        score += 2
        reasons.append(f"{len(refs)} governing/reference IDs")
    elif len(refs) > 6:
        score += 1
        reasons.append(f"{len(refs)} governing/reference IDs")

    if dependency_count > 4:
        score += 2
        reasons.append(f"{dependency_count} work-packet dependencies")
    elif dependency_count > 2:
        score += 1
        reasons.append(f"{dependency_count} work-packet dependencies")

    if headings > 16:
        score += 1
        reasons.append(f"{headings} subsections suggest broad scope")

    if score <= 2:
        size = "SMALL"
    elif score <= 5:
        size = "MEDIUM"
    elif score <= 8:
        size = "LARGE"
    else:
        size = "OVERSIZED"

    return {
        "wp": wp_id,
        "size": size,
        "score": score,
        "characters": len(text),
        "acceptance_items": acceptance,
        "references": len(refs),
        "dependencies": dependency_count,
        "subheadings": headings,
        "reasons": reasons,
    }


def planning_check(pi_id: str) -> dict:
    pi = find_row("PI", pi_id)
    if not pi:
        raise EosError(f"Unknown program increment: {pi_id}")

    failures: list[str] = []
    warnings: list[str] = []
    order, dep_errors = topological_wp_order(pi_id)
    failures.extend(dep_errors)

    wcs = [row for row in registry("WC") if row.get("pi") == pi_id]
    wps = pi_work_packets(pi_id)
    if not wcs:
        warnings.append(f"{pi_id} has no work cycles")
    if not wps:
        warnings.append(f"{pi_id} has no work packets")

    for wc in wcs:
        children = [wp for wp in wps if wp.get("wc") == wc["id"]]
        if not children:
            warnings.append(f"{wc['id']} has no work packets")
        if wc["status"] in {"AUTHORIZED", "ACTIVE", "IN_REVIEW", "CLOSED"}:
            parent = find_row("PI", wc["pi"])
            if parent and parent["status"] not in {"AUTHORIZED", "ACTIVE", "IN_REVIEW", "CLOSED"}:
                failures.append(
                    f"{wc['id']} is {wc['status']} while parent {wc['pi']} is {parent['status']}"
                )

    deps, _ = wp_dependency_map(pi_id)
    for wp in wps:
        if wp["status"] in {"READY", "AUTHORIZED", "IN_PROGRESS", "VERIFYING", "IN_REVIEW", "CLOSED"}:
            complete, issues = artifact_is_complete_enough(ROOT / wp["path"])
            if not complete:
                failures.extend(f"{wp['id']}: {issue}" for issue in issues)
        wc = find_row("WC", wp["wc"])
        if wp["status"] in {"AUTHORIZED", "IN_PROGRESS", "VERIFYING", "IN_REVIEW", "CLOSED"}:
            if wc and wc["status"] not in {"AUTHORIZED", "ACTIVE", "IN_REVIEW", "CLOSED"}:
                failures.append(
                    f"{wp['id']} is {wp['status']} while parent {wp['wc']} is {wc['status']}"
                )
        for dep in deps.get(wp["id"], set()):
            dep_row = find_row("WP", dep)
            if dep_row and dep_row.get("pi") != pi_id:
                warnings.append(
                    f"{wp['id']} has cross-PI dependency {dep} in {dep_row.get('pi')}"
                )

        size = wp_size_analysis(wp["id"])
        if size["size"] == "OVERSIZED":
            warnings.append(
                f"{wp['id']} sizing heuristic is OVERSIZED (score {size['score']}); consider decomposition"
            )

    return {
        "pi": pi_id,
        "passed": not failures,
        "failures": failures,
        "warnings": warnings,
        "order": order,
        "work_cycles": [wc["id"] for wc in wcs],
        "work_packets": [wp["id"] for wp in wps],
    }


def cmd_planning_check(args: argparse.Namespace) -> None:
    report = planning_check(args.pi)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"PLANNING CHECK — {args.pi}")
        print(f"Result: {'PASS' if report['passed'] else 'FAIL'}")
        if report["order"]:
            print("Execution order: " + " -> ".join(report["order"]))
        if report["warnings"]:
            print("\nWarnings:")
            for item in report["warnings"]:
                print(f"  WARN {item}")
        if report["failures"]:
            print("\nFailures:")
            for item in report["failures"]:
                print(f"  FAIL {item}")
    if not report["passed"]:
        raise EosError("Planning feasibility check failed")


def cmd_planning_order(args: argparse.Namespace) -> None:
    order, errors = topological_wp_order(args.pi)
    if errors:
        raise EosError("\n- ".join(["Planning dependency error:", *errors]))
    if args.json:
        print(json.dumps({"pi": args.pi, "order": order}, indent=2))
    elif order:
        for index, wp in enumerate(order, start=1):
            print(f"{index:03d}  {wp}")
    else:
        print("No work packets in the requested PI.")


def cmd_planning_critical_path(args: argparse.Namespace) -> None:
    path, errors = critical_path_for_pi(args.pi)
    if errors:
        raise EosError("\n- ".join(["Critical path unavailable:", *errors]))
    if args.json:
        print(json.dumps({"pi": args.pi, "critical_path": path, "length": len(path)}, indent=2))
    else:
        print(f"CRITICAL PATH — {args.pi}")
        print(f"Length: {len(path)} work packet(s)")
        print(" -> ".join(path) if path else "(none)")


def cmd_planning_graph(args: argparse.Namespace) -> None:
    deps, errors = wp_dependency_map(args.pi)
    if errors:
        raise EosError("\n- ".join(["Planning graph error:", *errors]))
    if args.format == "mermaid":
        print("graph TD")
        emitted = False
        for source in sorted(deps):
            if not deps[source]:
                print(f"  {source.replace('-', '_')}[\"{source}\"]")
                emitted = True
            for target in sorted(deps[source]):
                print(
                    f"  {source.replace('-', '_')}[\"{source}\"] "
                    f"--> |depends on| {target.replace('-', '_')}[\"{target}\"]"
                )
                emitted = True
        if not emitted:
            print("  EMPTY[\"No work packets\"]")
        return
    for source in sorted(deps):
        targets = sorted(deps[source])
        print(f"{source}: {', '.join(targets) if targets else '(no WP dependencies)'}")


def cmd_planning_size(args: argparse.Namespace) -> None:
    result = wp_size_analysis(args.wp)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print(f"WORK PACKET SIZE — {args.wp}")
    print(f"Classification: {result['size']} (score {result['score']})")
    print(
        f"characters={result['characters']} acceptance={result['acceptance_items']} "
        f"references={result['references']} dependencies={result['dependencies']} "
        f"subheadings={result['subheadings']}"
    )
    if result["reasons"]:
        print("Signals:")
        for reason in result["reasons"]:
            print(f"  - {reason}")



def gh_repo() -> str:
    if shutil.which("gh"):
        proc = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], cwd=ROOT, check=False)
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    if git_available():
        proc = run(["git", "remote", "get-url", "origin"], cwd=ROOT, check=False)
        url = proc.stdout.strip()
        m = re.search(r"github\.com[:/]([^/]+/[^/.]+)(?:\.git)?$", url)
        if m:
            return m.group(1)
    raise EosError("Cannot determine GitHub repository. Configure origin or authenticate gh.")


def gh_label_ensure(repo: str, name: str, description: str, apply: bool) -> None:
    if not apply:
        print(f"DRY-RUN label {name}: {description}")
        return
    proc = run(["gh", "label", "create", name, "--repo", repo, "--description", description], cwd=ROOT, check=False)
    if proc.returncode != 0 and "already exists" not in (proc.stderr or ""):
        # Attempt edit to keep description current.
        run(["gh", "label", "edit", name, "--repo", repo, "--description", description], cwd=ROOT, check=False)


def github_milestone_ensure(repo: str, title: str, apply: bool) -> str:
    if not apply:
        print(f"DRY-RUN milestone: {title}")
        return title
    import json
    proc = run(
        ["gh", "api", f"repos/{repo}/milestones?state=all&per_page=100"],
        cwd=ROOT,
        check=False,
    )
    if proc.returncode == 0:
        try:
            for item in json.loads(proc.stdout or "[]"):
                if item.get("title") == title:
                    return title
        except Exception:
            pass
    run(
        ["gh", "api", "--method", "POST", f"repos/{repo}/milestones", "-f", f"title={title}"],
        cwd=ROOT,
        check=True,
    )
    return title


def github_issue_for(
    repo: str,
    title: str,
    body_file: Path,
    labels: list[str],
    milestone: str,
    apply: bool,
) -> str:
    if not apply:
        print(
            f"DRY-RUN issue: {title} labels={','.join(labels)} "
            f"milestone={milestone or '-'} body={rel(body_file)}"
        )
        return ""
    search = run(
        ["gh", "issue", "list", "--repo", repo, "--state", "all", "--search", f'"{title}" in:title', "--json", "title,url"],
        cwd=ROOT,
        check=False,
    )
    if search.returncode == 0:
        import json
        try:
            for item in json.loads(search.stdout or "[]"):
                if item.get("title") == title:
                    return item.get("url", "")
        except Exception:
            pass
    args = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body-file", str(body_file)]
    for label in labels:
        args += ["--label", label]
    if milestone:
        args += ["--milestone", milestone]
    proc = run(args, cwd=ROOT, check=True)
    return proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""


def github_issue_sync(
    url: str,
    body_file: Path,
    labels: list[str],
    milestone: str,
    status: str,
    *,
    apply: bool,
    project: str,
    owner: str,
) -> None:
    if not url:
        return
    if not apply:
        print(
            f"DRY-RUN update: {url} status={status} milestone={milestone or '-'} "
            f"project={project or '-'}"
        )
        return
    args = ["gh", "issue", "edit", url, "--body-file", str(body_file)]
    for label in labels:
        args += ["--add-label", label]
    if milestone:
        args += ["--milestone", milestone]
    run(args, cwd=ROOT, check=False)
    if status == "CLOSED":
        run(["gh", "issue", "close", url, "--reason", "completed"], cwd=ROOT, check=False)
    if project:
        run(
            ["gh", "project", "item-add", project, "--owner", owner, "--url", url],
            cwd=ROOT,
            check=False,
        )


def update_github_url(kind: str, target: str, url: str) -> None:
    if url:
        row = find_row(kind, target)
        old_url = row.get("github_url", "") if row else ""
        update_row(kind, target, github_url=url)
        if old_url != url:
            append_event(
                "ENTITY_PATCHED",
                target=target,
                entity_kind=kind,
                action="github-sync",
                reason="GitHub projection URL updated",
                metadata={"field": "github_url", "from": old_url, "to": url},
            )


def cmd_github_sync(args: argparse.Namespace) -> None:
    if args.apply and not shutil.which("gh"):
        raise EosError("GitHub CLI `gh` is required for --apply")
    repo = gh_repo()
    owner = args.owner or repo.split("/", 1)[0]
    print(f"GitHub repository: {repo}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    if args.project:
        print(f"GitHub Project: {owner}/{args.project}")
    print()

    labels = {
        "eos": "Managed by the Engineering Operating System",
        "program-increment": "Program increment tracking",
        "work-cycle": "Work cycle tracking",
        "work-packet": "Work packet tracking",
        "change-request": "Governed change request",
        "maintenance": "Maintenance work",
        "release": "Release lifecycle",
        "authorized": "Authorized for execution",
        "blocked": "Blocked by a gate or dependency",
    }
    for name, desc in labels.items():
        gh_label_ensure(repo, name, desc, args.apply)

    milestones: dict[str, str] = {}
    for pi in registry("PI"):
        milestones[pi["id"]] = github_milestone_ensure(repo, pi["id"], args.apply)

    for kind, label in (("PI", "program-increment"), ("WC", "work-cycle"), ("WP", "work-packet"), ("CR", "change-request"), ("MNT", "maintenance")):
        rows = registry(kind)
        for row in rows:
            path = ROOT / row["path"]
            if not path.exists():
                continue
            title = f"{row['id']}: {row.get('title') or row.get('summary') or row['id']}"
            issue_labels = ["eos", label]
            if row.get("status") == "AUTHORIZED":
                issue_labels.append("authorized")
            if row.get("status") == "BLOCKED":
                issue_labels.append("blocked")
            pi_id = row["id"] if kind == "PI" else row.get("pi", "")
            milestone = milestones.get(pi_id, "")
            url = row.get("github_url", "")
            if not url:
                url = github_issue_for(repo, title, path, issue_labels, milestone, args.apply)
                if args.apply and url:
                    update_github_url(kind, row["id"], url)
                    print(f"SYNCED {row['id']} -> {url}")
            if url:
                github_issue_sync(
                    url,
                    path,
                    issue_labels,
                    milestone,
                    row.get("status", ""),
                    apply=args.apply,
                    project=args.project,
                    owner=owner,
                )

    stamp = dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    (EOS / "sync" / f"github-{stamp}.txt").write_text(
        f"timestamp={now_iso()}\nrepo={repo}\nmode={'apply' if args.apply else 'dry-run'}\n",
        encoding="utf-8",
    )
    if not args.apply:
        print("\nNo GitHub changes were made. Re-run with --apply to synchronize.")


def cmd_change_create(args: argparse.Namespace) -> None:
    cr_id = f"CR-{next_number('CR', 4):04d}"
    title = args.summary
    path = ROOT / "engineering" / "changes" / f"{cr_id}.md"
    body = f"""# {cr_id} — {title}

**State:** PROPOSED

## Target

{args.target}

## Summary

{args.summary}

## Motivation

{args.reason or 'TBD.'}

## Proposed Change

TBD.

## Impact Analysis

Run:

`./scripts/eos impact {args.target}`

Then summarize affected artifacts and implementation.

## Alternatives

TBD.

## Risks

TBD.

## Migration / Rollback

TBD.

## Decision

**Decision:** PENDING
"""
    create_artifact(path, cr_id, title, "change-request", "governance-authoritative", body, status="Proposed")
    rows = registry("CR")
    rows.append(
        {
            "id": cr_id,
            "path": rel(path),
            "target": args.target,
            "summary": args.summary,
            "status": "PROPOSED",
            "created": now_iso(),
            "updated": now_iso(),
            "github_url": "",
        }
    )
    save_registry("CR", rows)
    append_event(
        "ENTITY_CREATED",
        target=cr_id,
        entity_kind="CR",
        action="change-create",
        to_state="PROPOSED",
        reason=args.reason or "change request created",
        metadata={"row": rows[-1]},
    )
    print(f"Created {cr_id}: {rel(path)}")


def cmd_change_approve(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "CR":
        raise EosError("change approve requires CR-NNNN")
    actor = args.by or os.environ.get("USER") or "human"
    override = enforce_gate(
        "CR_APPROVE",
        args.target,
        force=args.force,
        actor=actor,
        reason=args.reason,
    )
    set_lifecycle_state(
        args.target,
        "APPROVED",
        action="change-approve",
        actor=actor,
        reason=args.reason or (
            f"change approved under {override['id']}" if override else "change approved"
        ),
    )
    if override:
        consume_override(override)
    record_decision(args.target, "change-approve", "APPROVED", actor, args.reason or "change approved")
    print(f"{args.target} APPROVED.")



def cmd_change_apply(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "CR":
        raise EosError("change apply requires CR-NNNN")
    set_lifecycle_state(
        args.target,
        "APPLIED",
        action="change-apply",
        actor=actor_name(),
        reason="approved change has been applied to governed artifacts/implementation",
    )
    print(f"{args.target} APPLIED.")


def cmd_change_close(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "CR":
        raise EosError("change close requires CR-NNNN")
    set_lifecycle_state(
        args.target,
        "CLOSED",
        action="change-close",
        actor=actor_name(),
        reason="change implementation and required verification are complete",
    )
    print(f"{args.target} CLOSED.")


def cmd_maintain_create(args: argparse.Namespace) -> None:
    mnt_id = f"MNT-{next_number('MNT', 4):04d}"
    path = ROOT / "engineering" / "maintenance" / f"{mnt_id}.md"
    body = f"""# {mnt_id} — {args.summary}

**State:** OPEN

## Type

{args.type}

## Summary

{args.summary}

## Context

{args.context or 'TBD.'}

## Affected Artifacts / Components

TBD.

## Risk if Deferred

TBD.

## Proposed Resolution

TBD.

## Validation

TBD.

## Closure Evidence

TBD.
"""
    create_artifact(path, mnt_id, args.summary, "maintenance", "planning-authoritative", body, status="Open")
    rows = registry("MNT")
    rows.append(
        {
            "id": mnt_id,
            "path": rel(path),
            "type": args.type,
            "summary": args.summary,
            "status": "OPEN",
            "created": now_iso(),
            "updated": now_iso(),
            "github_url": "",
        }
    )
    save_registry("MNT", rows)
    append_event(
        "ENTITY_CREATED",
        target=mnt_id,
        entity_kind="MNT",
        action="maintenance-create",
        to_state="OPEN",
        reason="maintenance item created",
        metadata={"row": rows[-1]},
    )
    print(f"Created {mnt_id}: {rel(path)}")
    print(f"Next: ./scripts/eos maintain plan {mnt_id}")


def cmd_maintain_plan(args: argparse.Namespace) -> None:
    kind, _ = row_for_target(args.target)
    if kind != "MNT":
        raise EosError("maintain plan requires MNT-NNNN")
    set_lifecycle_state(
        args.target,
        "PLANNED",
        action="maintenance-plan",
        actor=actor_name(),
        reason="maintenance resolution has been planned",
    )
    print(f"{args.target} PLANNED.")


def cmd_maintain_start(args: argparse.Namespace) -> None:
    kind, _ = row_for_target(args.target)
    if kind != "MNT":
        raise EosError("maintain start requires MNT-NNNN")
    set_lifecycle_state(
        args.target,
        "IN_PROGRESS",
        action="maintenance-start",
        actor=actor_name(),
        reason="maintenance execution started",
    )
    print(f"{args.target} IN_PROGRESS.")


def cmd_maintain_verify(args: argparse.Namespace) -> None:
    kind, _ = row_for_target(args.target)
    if kind != "MNT":
        raise EosError("maintain verify requires MNT-NNNN")
    set_lifecycle_state(
        args.target,
        "VERIFYING",
        action="maintenance-verify",
        actor=actor_name(),
        reason="maintenance verification started",
    )
    print(f"{args.target} VERIFYING.")


def cmd_maintain_close(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "MNT":
        raise EosError("maintain close requires MNT-NNNN")
    override = enforce_gate(
        "MNT_CLOSE",
        args.target,
        force=args.force,
        actor=actor_name(),
        reason=getattr(args, "reason", ""),
    )
    set_lifecycle_state(
        args.target,
        "CLOSED",
        action="maintenance-close",
        actor=actor_name(),
        reason=(
            f"maintenance closure under {override['id']}"
            if override
            else "maintenance completion verified"
        ),
    )
    if override:
        consume_override(override)
    print(f"{args.target} CLOSED.")



def release_artifact(version: str) -> tuple[str, Path]:
    rel_id = f"REL-{version}"
    path = ROOT / "engineering" / "releases" / f"{rel_id}.md"
    return rel_id, path


def release_readiness_path(version: str) -> Path:
    return ROOT / "engineering" / "reviews" / f"REL-{version}-READINESS-REVIEW.md"


def prepare_release(version: str) -> tuple[str, Path, Path]:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise EosError("Release version must be semantic version X.Y.Z")
    rel_id, path = release_artifact(version)
    if not path.exists():
        body = f"""# {rel_id} — Release {version}

**State:** PROPOSED

## Release Objective

TBD.

## Included Program Increments / Work

TBD.

## User-Visible Changes

TBD.

## Compatibility / Migration

TBD.

## Security and Supply-Chain Evidence

TBD.

## Verification Evidence

TBD.

## Known Limitations

TBD.

## Rollback / Recovery

TBD.

## Release Notes

TBD.
"""
        create_artifact(path, rel_id, f"Release {version}", "release", "release-authoritative", body, status="Proposed")
        rows = registry("REL")
        rows.append(
            {
                "id": rel_id,
                "path": rel(path),
                "version": version,
                "status": "PROPOSED",
                "created": now_iso(),
                "updated": now_iso(),
                "github_url": "",
            }
        )
        save_registry("REL", rows)
        append_event(
            "ENTITY_CREATED",
            target=rel_id,
            entity_kind="REL",
            action="release-prepare",
            to_state="PROPOSED",
            reason="release candidate prepared",
            metadata={"row": rows[-1]},
        )

    review = release_readiness_path(version)
    if not review.exists():
        body = f"""# {rel_id} — Release Readiness Review

**Decision:** PENDING

## Release Artifact

- `{rel(path)}`

## Integrity

TBD.

## Included Work Closed

TBD.

## Test / Verification Evidence

TBD.

## Security / Supply Chain

TBD.

## Documentation / Migration

TBD.

## Rollback Readiness

TBD.

## Blocking Findings

TBD.

## Decision

Set `**Decision:**` to APPROVED only when the release may be tagged/published.
"""
        create_artifact(review, f"REV-{rel_id}", f"{rel_id} Release Readiness Review", "review", "review-authoritative", body, status="In Review")
    return rel_id, path, review


def cmd_release(args: argparse.Namespace) -> None:
    rel_id, path, review = prepare_release(args.version)
    verify_ok, report = verify_all(strict=True)
    print(report)
    if not verify_ok and not args.force:
        raise EosError("EOS verification failed; release blocked.")

    release_complete, release_issues = artifact_is_complete_enough(path)
    review_complete, review_issues = accepted_review_complete(review)
    release_gate_issues = []
    if not release_complete:
        release_gate_issues.extend(release_issues)
    if not review_complete:
        release_gate_issues.extend(review_issues)
    if release_gate_issues and not args.force:
        print(f"\nPrepared release artifacts:")
        print(f"  {rel(path)}")
        print(f"  {rel(review)}")
        raise EosError(
            "Release gate is not complete:\n- " + "\n- ".join(release_gate_issues)
        )

    if not git_available():
        raise EosError("git is required to finalize a release")
    if not git_clean() and not args.force:
        raise EosError("Working tree must be clean before final release execution")

    tag = f"v{args.version}"
    existing = run(["git", "tag", "--list", tag], cwd=ROOT).stdout.strip()
    if existing:
        print(f"{tag} already exists.")
    else:
        # Advance through the declarative release state machine before tagging.
        current_rel = find_row("REL", rel_id)
        if current_rel and current_rel["status"] == "PROPOSED":
            set_lifecycle_state(
                rel_id,
                "READY",
                action="release-ready",
                actor=actor_name(),
                reason="release readiness gate satisfied",
                    )
        set_lifecycle_state(
            rel_id,
            "RELEASED",
            action="release",
            actor=actor_name(),
            reason=f"release {args.version} finalized",
            )
        run(
            ["git", "add", rel(path), rel(review), REGISTRY_PATHS["REL"], rel(EVENTS_PATH)],
            cwd=ROOT,
        )
        staged = run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
        if staged.returncode != 0:
            run(["git", "commit", "-m", f"release: {tag}"], cwd=ROOT, capture=False)
        run(["git", "tag", "-a", tag, "-m", f"Release {args.version}"], cwd=ROOT, capture=False)
        print(f"Created annotated release tag {tag}")

    if args.publish:
        if not shutil.which("gh"):
            raise EosError("gh CLI is required for --publish")
        repo = gh_repo()
        run(["git", "push", "origin", "HEAD", tag], cwd=ROOT, capture=False)
        proc = run(
            ["gh", "release", "view", tag, "--repo", repo],
            cwd=ROOT,
            check=False,
        )
        if proc.returncode != 0:
            run(
                ["gh", "release", "create", tag, "--repo", repo, "--title", f"Release {args.version}", "--notes-file", str(path)],
                cwd=ROOT,
                capture=False,
            )
        print(f"Published {tag} to GitHub repository {repo}")



def cmd_events(args: argparse.Namespace) -> None:
    events = read_events()
    if args.target:
        events = [event for event in events if event.get("target") == args.target]
    if args.limit:
        events = events[-args.limit :]
    if args.json:
        print(json.dumps(events, indent=2, sort_keys=True))
        return
    for event in events:
        print(
            f"{event.get('timestamp','')}  {event.get('event_type',''):<18} "
            f"{event.get('target',''):<20} "
            f"{event.get('from_state','') or '-'} -> {event.get('to_state','') or '-'}  "
            f"{event.get('actor','')}"
        )


def cmd_state_machine(args: argparse.Namespace) -> None:
    target = args.target.upper()
    try:
        kind = kind_for_id(target)
    except EosError:
        kind = target
    if kind not in REGISTRY_PATHS:
        raise EosError("State machine target must be PI, WC, WP, CR, MNT, REL, or an entity ID")
    machine = state_machine(kind)
    if args.json:
        print(json.dumps(machine, indent=2, sort_keys=True))
        return
    print(f"{kind} state machine v{machine.get('version','?')}")
    print(f"initial: {machine.get('initial_state')}")
    print(f"terminal: {', '.join(machine.get('terminal_states', [])) or '(none)'}")
    print("transitions:")
    for source in machine.get("states", []):
        destinations = machine.get("transitions", {}).get(source, [])
        print(f"  {source:<14} -> {', '.join(destinations) or '(terminal)'}")


def cmd_schema(args: argparse.Namespace) -> None:
    name = args.name.lower()
    aliases = {
        "pi": "pi", "wc": "wc", "wp": "wp", "cr": "cr", "mnt": "mnt",
        "rel": "rel", "artifact": "artifact", "event": "event",
    }
    if name not in aliases:
        raise EosError("Schema must be one of PI, WC, WP, CR, MNT, REL, artifact, event")
    schema = load_json(SCHEMA_DIR / f"{aliases[name]}.schema.json")
    print(json.dumps(schema, indent=2, sort_keys=True))


def cmd_rebuild_state(args: argparse.Namespace) -> None:
    projected = event_projected_state()
    mismatches: list[tuple[str, str, str, str]] = []
    for kind in ("PI", "WC", "WP", "CR", "MNT", "REL"):
        for row in registry(kind):
            key = (kind, row["id"])
            if key not in projected:
                continue
            expected = projected[key]
            actual = row["status"]
            if expected != actual:
                mismatches.append((kind, row["id"], actual, expected))

    if not mismatches:
        print("Lifecycle registry projections match the event ledger.")
        return

    print("Lifecycle state mismatches:")
    for kind, target, actual, expected in mismatches:
        print(f"  {target}: registry={actual} event-ledger={expected}")

    if not args.apply:
        raise EosError("Run with --apply to repair registry/artifact lifecycle state from the event ledger.")

    for kind, target, actual, expected in mismatches:
        row = find_row(kind, target)
        if not row:
            continue
        update_row(kind, target, status=expected)
        sync_artifact_state(ROOT / row["path"], expected)
        append_event(
            "PROJECTION_REPAIRED",
            target=target,
            entity_kind=kind,
            action="rebuild-state",
            from_state=actual,
            to_state=expected,
            actor=actor_name(),
            reason="registry/artifact projection repaired from append-only event ledger",
        )
        print(f"  repaired {target} -> {expected}")


def verify_all(*, strict: bool = False) -> tuple[bool, str]:
    failures: list[str] = []
    warnings: list[str] = []
    lines: list[str] = []

    required = [
        ROOT / "idea.md",
        EOS / "layers.tsv",
        EOS / "workflow.tsv",
        EOS / "artifacts.tsv",
        EOS / "domain-model.json",
        EOS / "version.json",
        EOS / "events.jsonl",
        EOS / "policies" / "core.json",
        EOS / "overrides.tsv",
        ROOT / "governance" / "responsibility-model.md",
        ROOT / "governance" / "canonical-state-model.md",
    ]
    for path in required:
        if not path.exists():
            failures.append(f"missing required file: {rel(path)}")

    # Permanent layers.
    layers = read_tsv(EOS / "layers.tsv")
    layer_codes = [r.get("code", "") for r in layers]
    if layer_codes != list(LAYER_ORDER):
        failures.append(
            "permanent layer registry must contain EOSB, EOSP, EOSE, EOSV, EOSR, EOSC, EOSL, EOSM in order"
        )

    # Artifact registry.
    artifacts = read_tsv(EOS / "artifacts.tsv")
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for row in artifacts:
        aid = row.get("artifact_id", "")
        p = row.get("path", "")
        if aid in seen_ids:
            failures.append(f"duplicate artifact id: {aid}")
        seen_ids.add(aid)
        if p in seen_paths:
            warnings.append(f"duplicate artifact path in registry: {p}")
        seen_paths.add(p)
        path = ROOT / p
        if not path.exists():
            failures.append(f"registered artifact missing: {aid} -> {p}")
            continue
        if path.suffix == ".md":
            data, _ = parse_frontmatter(path)
            fm_id = data.get("artifact_id")
            if fm_id and fm_id != aid:
                failures.append(f"artifact id mismatch: registry {aid}, frontmatter {fm_id}, path {p}")
            artifact_schema_path = SCHEMA_DIR / "artifact.schema.json"
            if data and artifact_schema_path.exists():
                failures.extend(
                    validate_simple_schema(
                        load_json(artifact_schema_path),
                        data,
                        label=f"artifact:{aid}",
                    )
                )
            elif not data and p != "idea.md":
                warnings.append(f"registered Markdown artifact has no EOS front matter: {p}")

    # Lifecycle registries and parent integrity.
    all_pi = {r["id"]: r for r in registry("PI")}
    all_wc = {r["id"]: r for r in registry("WC")}
    all_wp = {r["id"]: r for r in registry("WP")}
    for kind, rows in (("PI", all_pi.values()), ("WC", all_wc.values()), ("WP", all_wp.values()), ("CR", registry("CR")), ("MNT", registry("MNT")), ("REL", registry("REL"))):
        ids: set[str] = set()
        for row in rows:
            rid = row["id"]
            if rid in ids:
                failures.append(f"duplicate {kind} id: {rid}")
            ids.add(rid)
            try:
                states = valid_states(kind)
            except EosError as exc:
                failures.append(str(exc))
                states = set()
            if row["status"] not in states:
                failures.append(f"{rid} has invalid state {row['status']}")
            schema_path = SCHEMA_DIR / f"{kind.lower()}.schema.json"
            if schema_path.exists():
                failures.extend(
                    validate_simple_schema(
                        load_json(schema_path),
                        row,
                        label=f"{kind}:{rid}",
                    )
                )
            path = ROOT / row["path"]
            if not path.exists():
                failures.append(f"{rid} path missing: {row['path']}")
        if kind == "WC":
            for row in rows:
                if row.get("pi") not in all_pi:
                    failures.append(f"{row['id']} references missing parent PI {row.get('pi')}")
        if kind == "WP":
            for row in rows:
                wc = all_wc.get(row.get("wc", ""))
                if not wc:
                    failures.append(f"{row['id']} references missing parent WC {row.get('wc')}")
                elif wc.get("pi") != row.get("pi"):
                    failures.append(
                        f"{row['id']} parent mismatch: registry pi={row.get('pi')} but {wc['id']} belongs to {wc.get('pi')}"
                    )

    # Declarative state-machine integrity.
    for kind in ("PI", "WC", "WP", "CR", "MNT", "REL"):
        try:
            machine = state_machine(kind)
            states = set(machine.get("states", []))
            initial = machine.get("initial_state")
            if initial not in states:
                failures.append(f"{kind} state machine initial_state {initial!r} is not declared")
            for terminal in machine.get("terminal_states", []):
                if terminal not in states:
                    failures.append(f"{kind} state machine terminal state {terminal!r} is not declared")
            transitions = machine.get("transitions", {})
            for source in states:
                if source not in transitions:
                    failures.append(f"{kind} state machine missing transition entry for {source}")
                    continue
                for dest in transitions.get(source, []):
                    if dest not in states:
                        failures.append(f"{kind} state machine {source} references unknown destination {dest}")
        except EosError as exc:
            failures.append(str(exc))

    # Append-only event ledger syntax/schema + projection consistency.
    try:
        event_schema = load_json(SCHEMA_DIR / "event.schema.json")
        events = read_events()
        event_ids: set[str] = set()
        for i, event in enumerate(events, start=1):
            event_id = event.get("event_id", "")
            if event_id in event_ids:
                failures.append(f"duplicate event id: {event_id}")
            event_ids.add(event_id)
            failures.extend(
                validate_simple_schema(event_schema, event, label=f"event-line-{i}")
            )
            kind = event.get("entity_kind", "")
            frm = event.get("from_state", "")
            to = event.get("to_state", "")
            if event.get("event_type") == "STATE_TRANSITION" and kind in REGISTRY_PATHS:
                if not transition_allowed(kind, frm, to):
                    failures.append(
                        f"illegal recorded transition in {event_id}: {kind} {frm} -> {to}"
                    )
        projected = event_projected_state()
        for kind in ("PI", "WC", "WP", "CR", "MNT", "REL"):
            for row in registry(kind):
                expected = projected.get((kind, row["id"]))
                if expected and expected != row["status"]:
                    failures.append(
                        f"{row['id']} projection drift: registry={row['status']} event-ledger={expected}"
                    )
        lines.append(f"events: {len(events)}")
    except EosError as exc:
        failures.append(str(exc))

    # Policy-as-code definitions and override registry.
    try:
        policy = policy_document()
        gates = policy.get("gates", {})
        if not gates:
            failures.append("policy document contains no gates")
        for gate_name, checks in gates.items():
            if not re.fullmatch(r"[A-Z][A-Z0-9_]+", gate_name):
                failures.append(f"invalid policy gate name: {gate_name}")
            if not isinstance(checks, list) or not checks:
                failures.append(f"policy gate {gate_name} has no checks")
            for spec in checks if isinstance(checks, list) else []:
                if not isinstance(spec, dict) or not spec.get("check"):
                    failures.append(f"policy gate {gate_name} contains malformed check")
    except EosError as exc:
        failures.append(str(exc))

    try:
        override_schema = load_json(SCHEMA_DIR / "override.schema.json")
        seen_overrides: set[str] = set()
        for row in override_rows():
            oid = row.get("id", "")
            if oid in seen_overrides:
                failures.append(f"duplicate override id: {oid}")
            seen_overrides.add(oid)
            failures.extend(validate_simple_schema(override_schema, row, label=f"override:{oid}"))
            if row.get("status") not in {"ACTIVE", "CONSUMED", "EXPIRED"}:
                failures.append(f"{oid} has invalid override status {row.get('status')}")
            if row.get("gate") and row.get("gate") not in policy_document().get("gates", {}):
                failures.append(f"{oid} references unknown policy gate {row.get('gate')}")
        lines.append(f"overrides: {len(seen_overrides)}")
    except EosError as exc:
        failures.append(str(exc))

    # Bootstrap stages.
    workflow = read_tsv(EOS / "workflow.tsv")
    stages = [r.get("stage") for r in workflow]
    if len(stages) != len(set(stages)):
        failures.append("duplicate EOSB workflow stage IDs")

    # Trace graph can be rebuilt as a verification side effect.
    try:
        edges = rebuild_trace()
        lines.append(f"trace edges: {len(edges)}")
    except Exception as exc:
        failures.append(f"trace rebuild failed: {exc}")

    lines.insert(0, f"registered artifacts: {len(artifacts)}")
    lines.append(f"program increments: {len(all_pi)}")
    lines.append(f"work cycles: {len(all_wc)}")
    lines.append(f"work packets: {len(all_wp)}")

    open_stale = [row for row in stale_rows() if row.get("status") == "OPEN"]
    lines.append(f"open stale records: {len(open_stale)}")
    if open_stale:
        messages = [
            f"{row['id']} target={row['target']} source={row['source']}"
            for row in open_stale
        ]
        if strict:
            failures.extend(f"unresolved stale dependency: {message}" for message in messages)
        else:
            warnings.extend(f"unresolved stale dependency: {message}" for message in messages)

    coverage = trace_coverage_report()
    lines.append(f"trace coverage: {coverage['score']:.1f}%")
    if warnings:
        lines.append("warnings:")
        lines.extend(f"  WARN {w}" for w in warnings)
    if failures:
        lines.append("failures:")
        lines.extend(f"  FAIL {f}" for f in failures)
        lines.append(f"RESULT: FAIL ({len(failures)} failure(s))")
        return False, "\n".join(lines)
    lines.append("RESULT: PASS")
    return True, "\n".join(lines)


def cmd_verify(args: argparse.Namespace) -> None:
    ok, report = verify_all(strict=args.strict)
    print(report)
    if not ok:
        raise EosError("EOS verification failed")


def cmd_doctor(_: argparse.Namespace) -> None:
    print("EOS DOCTOR\n")
    checks = [
        ("python3", shutil.which("python3") or ""),
        ("git", shutil.which("git") or ""),
        ("gh (optional)", shutil.which("gh") or ""),
        ("bash", shutil.which("bash") or ""),
    ]
    for name, value in checks:
        print(f"{name:<16} {'OK ' + value if value else 'MISSING'}")
    if EOS_VERSION_PATH.exists():
        versions = load_json(EOS_VERSION_PATH)
        print(
            f"\nEOS tool/schema: "
            f"{versions.get('eos_tool_version','?')} / {versions.get('eos_schema_version','?')}"
        )
    print(f"root: {ROOT}")
    print(f"branch: {current_branch() or '(unknown)'}")
    print(f"HEAD: {commit_sha() or '(none)'}")
    print(f"git: {git_status()}")


TOP_LEVEL_COMPLETION_COMMANDS = (
    "layers", "status", "next", "prompt", "complete", "reopen", "version",
    "history", "rollback", "checkpoint", "plan", "create-wc", "create-wp",
    "ready", "authorize", "start", "codex", "validate", "review", "close",
    "close-cycle", "close-pi", "trace", "impact", "github-sync", "change",
    "maintain", "release", "planning", "policy", "gate", "override", "stale", "events",
    "state-machine", "schema", "rebuild-state", "verify", "doctor",
    "responsibilities", "completion",
)

COMMAND_COMPLETION_OPTIONS = {
    "plan": ("--title", "--objective"),
    "create-wc": ("--pi", "--title"),
    "create-wp": ("--wc", "--domain", "--title"),
    "ready": ("--reason", "--by"),
    "authorize": ("--force", "--reason", "--by"),
    "codex": ("--force",),
    "close": ("--force", "--reason", "--by"),
    "close-cycle": ("--force", "--reason", "--by"),
    "close-pi": ("--force", "--reason", "--by"),
    "github-sync": ("--apply", "--project", "--owner"),
    "release": ("--publish", "--force"),
    "events": ("--limit", "--json"),
    "state-machine": ("--json",),
    "rebuild-state": ("--apply",),
    "verify": ("--strict",),
    "trace": ("--json",),
    "impact": ("--json",),
    "stale": ("--all", "--by", "--reason"),
    "planning": ("--json", "--format"),
    "gate": ("--json",),
    "override": ("--active", "--by", "--reason", "--expires"),
}


def completion_artifact_ids() -> list[str]:
    values: set[str] = set()
    for row in read_tsv(EOS / "artifacts.tsv"):
        if row.get("artifact_id"):
            values.add(row["artifact_id"])
    for kind in REGISTRY_PATHS:
        for row in registry(kind):
            if row.get("id"):
                values.add(row["id"])
    for base in (
        ROOT / "vision", ROOT / "product", ROOT / "architecture",
        ROOT / "specifications", ROOT / "engineering", ROOT / "research",
        ROOT / "governance", ROOT / "journal",
    ):
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            try:
                data, _ = parse_frontmatter(path)
            except OSError:
                continue
            if data.get("artifact_id"):
                values.add(data["artifact_id"])
    return sorted(values)


def completion_artifact_paths() -> list[str]:
    values: set[str] = set()
    for row in read_tsv(EOS / "artifacts.tsv"):
        if row.get("path"):
            values.add(row["path"])
    for kind in REGISTRY_PATHS:
        for row in registry(kind):
            if row.get("path"):
                values.add(row["path"])
    return sorted(v for v in values if (ROOT / v).exists())


def completion_ids(*kinds: str, states: set[str] | None = None) -> list[str]:
    out: list[str] = []
    for kind in kinds:
        for row in registry(kind):
            if states is None or row.get("status") in states:
                out.append(row["id"])
    return sorted(out)


def completion_stages() -> list[str]:
    return sorted(
        row.get("stage", "")
        for row in read_tsv(EOS / "workflow.tsv")
        if row.get("stage")
    )


def completion_snapshot_versions(path_text: str) -> list[str]:
    path = Path(path_text)
    base = EOS / "history" / path.with_suffix("")
    if not base.exists():
        return []
    suffix = path.suffix
    versions: list[str] = []
    for snap in base.glob(f"v*{suffix}"):
        name = snap.name
        if name.startswith("v") and name.endswith(suffix):
            versions.append(name[1 : -len(suffix)] if suffix else name[1:])
    return sorted(set(versions), key=lambda x: tuple(int(p) if p.isdigit() else 0 for p in x.split(".")))


def completion_release_versions() -> list[str]:
    versions: set[str] = set()
    for row in registry("REL"):
        if row.get("version"):
            versions.add(row["version"])
    version_file = ROOT / "VERSION"
    current = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "0.1.0"
    try:
        major, minor, patch = map(int, current.split("."))
        versions.update({
            f"{major}.{minor}.{patch + 1}",
            f"{major}.{minor + 1}.0",
            f"{major + 1}.0.0",
        })
    except ValueError:
        pass
    return sorted(versions)


def completion_domains() -> list[str]:
    defaults = {"CORE", "CLI", "API", "ENGINE", "UI", "DATA", "SECURITY", "OPS", "DOCS", "TOOLING"}
    for row in registry("WP"):
        if row.get("domain"):
            defaults.add(row["domain"].upper())
    return sorted(defaults)


def filter_completion(values: Iterable[str], prefix: str) -> list[str]:
    return sorted({v for v in values if v and v.startswith(prefix)})


def completion_candidates(words: list[str]) -> list[str]:
    if not words:
        return list(TOP_LEVEL_COMPLETION_COMMANDS)

    current = words[-1]
    if len(words) == 1:
        return filter_completion(TOP_LEVEL_COMPLETION_COMMANDS, current)

    command = words[0]
    args = words[1:]
    current = args[-1] if args else ""
    prior = args[:-1] if args else []
    previous = prior[-1] if prior else ""

    # Subcommand discovery.
    if command == "change" and len(args) == 1:
        return filter_completion(("create", "approve", "apply", "close"), current)
    if command == "maintain" and len(args) == 1:
        return filter_completion(("create", "plan", "start", "verify", "close"), current)
    if command == "planning" and len(args) == 1:
        return filter_completion(("check", "order", "critical-path", "graph", "size"), current)
    if command == "policy" and len(args) == 1:
        return filter_completion(("list", "show"), current)
    if command == "gate" and len(args) == 1:
        return filter_completion(("check", "explain"), current)
    if command == "override" and len(args) == 1:
        return filter_completion(("create", "list", "expire"), current)
    if command == "stale" and len(args) == 1:
        return filter_completion(("list", "clear"), current)
    if command == "completion" and len(args) == 1:
        return filter_completion(("bash", "zsh", "fish", "write", "install"), current)

    # Values for preceding options.
    if previous == "--pi":
        return filter_completion(completion_ids("PI"), current)
    if previous == "--wc":
        return filter_completion(completion_ids("WC"), current)
    if previous == "--domain":
        return filter_completion(completion_domains(), current.upper())
    if previous == "--format" and command == "planning":
        return filter_completion(("text", "mermaid"), current)
    if command == "completion" and args and args[0] == "install" and len(args) <= 2:
        return filter_completion(("bash", "zsh", "fish", "all"), current)

    # Context-sensitive options.
    if current.startswith("-"):
        options = [o for o in COMMAND_COMPLETION_OPTIONS.get(command, ()) if o not in args]
        if command == "change" and args:
            if args[0] == "create":
                options += [o for o in ("--reason",) if o not in args]
            elif args[0] == "approve":
                options += [o for o in ("--force", "--reason", "--by") if o not in args]
        elif command == "maintain" and args:
            if args[0] == "create":
                options += [o for o in ("--context",) if o not in args]
            elif args[0] == "close":
                options += [o for o in ("--force", "--reason") if o not in args]
        elif command == "override" and args:
            if args[0] == "create":
                options += [o for o in ("--by", "--reason", "--expires") if o not in args]
            elif args[0] == "list":
                options += [o for o in ("--active",) if o not in args]
        elif command == "gate" and args:
            options += [o for o in ("--json",) if o not in args]
        elif command == "stale" and args:
            if args[0] == "list":
                options += [o for o in ("--all",) if o not in args]
            elif args[0] == "clear":
                options += [o for o in ("--by", "--reason") if o not in args]
        elif command == "planning" and args:
            if args[0] in {"check", "order", "critical-path", "size"}:
                options += [o for o in ("--json",) if o not in args]
            elif args[0] == "graph":
                options += [o for o in ("--format",) if o not in args]
        return filter_completion(options, current)

    # Bootstrap/versioning commands.
    if command in {"prompt", "complete", "reopen"}:
        return filter_completion(completion_stages(), current)
    if command == "version":
        positional = [a for a in args if not a.startswith("-")]
        if len(positional) <= 1:
            return filter_completion(completion_artifact_paths(), current)
        if len(positional) == 2:
            return filter_completion(("patch", "minor", "major"), current)
        return []
    if command == "history":
        return filter_completion(completion_artifact_paths(), current)
    if command == "rollback":
        positional = [a for a in args if not a.startswith("-")]
        if len(positional) <= 1:
            return filter_completion(completion_artifact_paths(), current)
        if len(positional) == 2:
            path_arg = next((a for a in args[:-1] if not a.startswith("-")), "")
            return filter_completion(completion_snapshot_versions(path_arg), current)
        return []

    # Planning/execution lifecycle.
    if command == "plan":
        if not current.startswith("-") and not prior:
            next_id = f"PI-{next_number('PI', 3):03d}"
            return filter_completion([next_id], current)
        return []
    if command == "ready":
        return filter_completion(completion_ids("PI", "WC", "WP"), current)
    if command == "authorize":
        return filter_completion(completion_ids("PI", "WC", "WP"), current)
    if command == "start":
        return filter_completion(completion_ids("PI", "WC", "WP", "MNT"), current)
    if command == "codex":
        return filter_completion(completion_ids("WP"), current)
    if command in {"validate", "review"}:
        return filter_completion(completion_ids("PI", "WC", "WP", "CR", "MNT", "REL"), current)
    if command == "close":
        return filter_completion(completion_ids("WP"), current)
    if command == "close-cycle":
        return filter_completion(completion_ids("WC"), current)
    if command == "close-pi":
        return filter_completion(completion_ids("PI"), current)
    if command == "trace":
        return filter_completion(["coverage", *completion_artifact_ids()], current)
    if command in {"impact", "events"}:
        return filter_completion(completion_artifact_ids(), current)
    if command == "state-machine":
        values = ["PI", "WC", "WP", "CR", "MNT", "REL"] + completion_ids(
            "PI", "WC", "WP", "CR", "MNT", "REL"
        )
        return filter_completion(values, current.upper())
    if command == "schema":
        return filter_completion(
            ("PI", "WC", "WP", "CR", "MNT", "REL", "artifact", "event", "override"),
            current,
        )
    if command == "release":
        if not current.startswith("-") and not prior:
            return filter_completion(completion_release_versions(), current)
        return []

    if command == "planning" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd in {"check", "order", "critical-path", "graph"} and len(subargs) <= 1:
            return filter_completion(completion_ids("PI"), subcurrent)
        if subcmd == "size" and len(subargs) <= 1:
            return filter_completion(completion_ids("WP"), subcurrent)
        return []

    # Policy/gates/overrides.
    if command == "policy" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "show" and len(subargs) <= 1:
            return filter_completion(sorted(policy_document().get("gates", {}).keys()), subcurrent.upper())
        return []

    if command == "gate" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd in {"check", "explain"}:
            if len(subargs) <= 1:
                return filter_completion(sorted(policy_document().get("gates", {}).keys()), subcurrent.upper())
            if len(subargs) == 2:
                return filter_completion(completion_ids("PI", "WC", "WP", "CR", "MNT", "REL"), subcurrent)
        return []

    if command == "override" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "create":
            if len(subargs) <= 1:
                return filter_completion(completion_ids("PI", "WC", "WP", "CR", "MNT", "REL"), subcurrent)
            if len(subargs) == 2:
                return filter_completion(sorted(policy_document().get("gates", {}).keys()), subcurrent.upper())
        if subcmd == "list" and len(subargs) <= 1:
            return filter_completion(completion_ids("PI", "WC", "WP", "CR", "MNT", "REL"), subcurrent)
        if subcmd == "expire" and len(subargs) <= 1:
            return filter_completion(
                [r["id"] for r in override_rows() if r.get("status") == "ACTIVE"],
                subcurrent.upper(),
            )
        return []

    if command == "stale" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "list" and len(subargs) <= 1:
            values = sorted({r["target"] for r in stale_rows()} | {r["source"] for r in stale_rows()})
            return filter_completion(values, subcurrent)
        if subcmd == "clear" and len(subargs) <= 1:
            values = [r["id"] for r in stale_rows() if r.get("status") == "OPEN"]
            return filter_completion(values, subcurrent.upper())
        return []

    # Change/maintenance subcommands.
    if command == "change" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "create" and len(subargs) <= 1:
            return filter_completion(completion_artifact_ids(), subcurrent)
        if subcmd in {"approve", "apply", "close"} and len(subargs) <= 1:
            return filter_completion(completion_ids("CR"), subcurrent)
        return []

    if command == "maintain" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "create" and len(subargs) <= 1:
            return filter_completion(
                ("bug", "debt", "security", "dependency", "operations", "performance", "documentation"),
                subcurrent,
            )
        if subcmd in {"plan", "start", "verify", "close"} and len(subargs) <= 1:
            return filter_completion(completion_ids("MNT"), subcurrent)
        return []

    return []


BASH_COMPLETION = r"""# Bash completion for repository-local EOS.
_eos_complete() {
  local cmd="${COMP_WORDS[0]}"
  local -a args
  local line
  COMPREPLY=()
  args=("${COMP_WORDS[@]:1}")
  while IFS= read -r line; do
    [[ -n "$line" ]] && COMPREPLY+=("$line")
  done < <("$cmd" completion candidates -- "${args[@]}" 2>/dev/null)
  if type compopt >/dev/null 2>&1; then
    compopt -o nosort 2>/dev/null || true
  fi
}
complete -o default -F _eos_complete eos ./scripts/eos scripts/eos
"""

ZSH_COMPLETION = r"""#compdef eos
# Zsh completion for repository-local EOS.
_eos() {
  local cmd="${words[1]}"
  local -a candidates argv_words
  argv_words=("${words[@]:1}")
  candidates=("${(@f)$("$cmd" completion candidates -- "${argv_words[@]}" 2>/dev/null)}")
  compadd -Q -- "${candidates[@]}"
}
compdef _eos eos
"""

FISH_COMPLETION = r"""# Fish completion for repository-local EOS.
function __eos_dynamic_complete
    set -l tokens (commandline -opc)
    set -l current (commandline -ct)
    if test (count $tokens) -eq 0
        return
    end
    set -l cmd $tokens[1]
    set -e tokens[1]
    command $cmd completion candidates -- $tokens $current 2>/dev/null
end
complete -c eos -f -a '(__eos_dynamic_complete)'
"""


def completion_script(shell: str) -> str:
    scripts = {"bash": BASH_COMPLETION, "zsh": ZSH_COMPLETION, "fish": FISH_COMPLETION}
    try:
        return scripts[shell]
    except KeyError as exc:
        raise EosError(f"Unsupported shell completion: {shell}") from exc


def write_completion_files() -> list[Path]:
    files = {
        ROOT / "completions" / "bash" / "eos": BASH_COMPLETION,
        ROOT / "completions" / "zsh" / "_eos": ZSH_COMPLETION,
        ROOT / "completions" / "fish" / "eos.fish": FISH_COMPLETION,
    }
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    readme = ROOT / "completions" / "README.md"
    readme.write_text(
        "# EOS Shell Completion\n\n"
        "The EOS provides dynamic completion for Bash, Zsh, and Fish. Candidate IDs "
        "are read from the live repository registries, so newly created PI/WC/WP, "
        "change, maintenance, release, and artifact IDs appear automatically.\n\n"
        "## Install\n\n"
        "```bash\n./scripts/eos completion install\n```\n\n"
        "The shell is inferred from `$SHELL`, or choose it explicitly:\n\n"
        "```bash\n"
        "./scripts/eos completion install bash\n"
        "./scripts/eos completion install zsh\n"
        "./scripts/eos completion install fish\n"
        "./scripts/eos completion install all\n"
        "```\n",
        encoding="utf-8",
    )
    return [*files, readme]


def install_completion(shell: str) -> list[Path]:
    home = Path.home()
    shells = ("bash", "zsh", "fish") if shell == "all" else (shell,)
    installed: list[Path] = []
    for item in shells:
        if item == "bash":
            dest = home / ".local" / "share" / "bash-completion" / "completions" / "eos"
        elif item == "zsh":
            dest = home / ".zfunc" / "_eos"
        elif item == "fish":
            dest = home / ".config" / "fish" / "completions" / "eos.fish"
        else:
            raise EosError(f"Unsupported shell: {item}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(completion_script(item), encoding="utf-8")
        installed.append(dest)
    return installed


def cmd_completion(args: argparse.Namespace) -> None:
    action = args.completion_command
    if action in {"bash", "zsh", "fish"}:
        print(completion_script(action), end="")
        return
    if action == "write":
        for path in write_completion_files():
            print(rel(path))
        return
    if action == "install":
        shell = args.shell
        if not shell:
            shell = Path(os.environ.get("SHELL", "")).name
            if shell not in {"bash", "zsh", "fish"}:
                raise EosError("Could not infer shell; specify bash, zsh, fish, or all")
        for path in install_completion(shell):
            print(f"Installed: {path}")
        if shell in {"zsh", "all"}:
            print("Zsh: ensure ~/.zfunc is in fpath before compinit, e.g. fpath=(~/.zfunc $fpath).")
        print("Start a new shell (or reload its completion system) to activate completion.")
        return
    if action == "candidates":
        words = list(args.words)
        if words and words[0] == "--":
            words = words[1:]
        for value in completion_candidates(words):
            print(value)
        return
    raise EosError(f"Unknown completion action: {action}")


def cmd_responsibilities(_: argparse.Namespace) -> None:
    print((ROOT / "governance" / "responsibility-model.md").read_text(encoding="utf-8"))


def add_override_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--force", action="store_true", help="Explicit human gate override")
    parser.add_argument("--reason", default="", help="Reason for action or override")
    parser.add_argument("--by", default="", help="Human actor/approver identity")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="./scripts/eos", description="Engineering Operating System")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("layers", help="Show permanent EOS operating layers")
    p.set_defaults(func=cmd_layers)

    p = sub.add_parser("status", help="Show bootstrap and permanent lifecycle status")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("next", help="Show the next recommended lifecycle action")
    p.set_defaults(func=cmd_next)

    p = sub.add_parser("prompt", help="Render an EOSB prompt with project context")
    p.add_argument("stage")
    p.set_defaults(func=cmd_prompt)

    p = sub.add_parser("complete", help="Mark an EOSB stage complete")
    p.add_argument("stage")
    p.set_defaults(func=cmd_complete)

    p = sub.add_parser("reopen", help="Reopen an EOSB stage")
    p.add_argument("stage")
    p.set_defaults(func=cmd_reopen)

    p = sub.add_parser("version", help="Version a governed artifact")
    p.add_argument("path")
    p.add_argument("kind", choices=("patch", "minor", "major"))
    p.add_argument("message")
    p.set_defaults(func=cmd_version)

    p = sub.add_parser("history", help="Show semantic and Git history for an artifact")
    p.add_argument("path")
    p.set_defaults(func=cmd_history)

    p = sub.add_parser("rollback", help="Restore historical content as a new version")
    p.add_argument("path")
    p.add_argument("version")
    p.add_argument("message")
    p.set_defaults(func=cmd_rollback)

    p = sub.add_parser("checkpoint", help="Commit and tag a coherent repository checkpoint")
    p.add_argument("message")
    p.set_defaults(func=cmd_checkpoint)

    p = sub.add_parser("plan", help="Create the next program increment")
    p.add_argument("pi", nargs="?")
    p.add_argument("--title", default="")
    p.add_argument("--objective", default="")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("create-wc", help="Create a work cycle")
    p.add_argument("--pi", default="")
    p.add_argument("--title", default="")
    p.set_defaults(func=cmd_create_wc)

    p = sub.add_parser("create-wp", help="Create a work packet")
    p.add_argument("--wc", default="")
    p.add_argument("--domain", default="")
    p.add_argument("--title", default="")
    p.set_defaults(func=cmd_create_wp)

    p = sub.add_parser("ready", help="Declare a PI/WC/WP definition ready for its next gate")
    p.add_argument("target")
    p.add_argument("--reason", default="")
    p.add_argument("--by", default="")
    p.set_defaults(func=cmd_ready)

    p = sub.add_parser("authorize", help="Authorize a PI, WC, or WP after gate checks")
    p.add_argument("target")
    add_override_args(p)
    p.set_defaults(func=cmd_authorize)

    p = sub.add_parser("start", help="Start authorized work")
    p.add_argument("target")
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("codex", help="Generate a bounded Codex execution contract")
    p.add_argument("target")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_codex)

    p = sub.add_parser("validate", help="Run deterministic verification for a target")
    p.add_argument("target")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("review", help="Generate review artifact + automated evidence")
    p.add_argument("target")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("close", help="Close an accepted work packet")
    p.add_argument("target")
    add_override_args(p)
    p.set_defaults(func=cmd_close)

    p = sub.add_parser("close-cycle", help="Close a work cycle after child/review gates")
    p.add_argument("target")
    add_override_args(p)
    p.set_defaults(func=cmd_close_cycle)

    p = sub.add_parser("close-pi", help="Close a program increment after child/review gates")
    p.add_argument("target")
    add_override_args(p)
    p.set_defaults(func=cmd_close_pi)

    p = sub.add_parser("trace", help="Show typed traceability or coverage")
    p.add_argument("target", help="Artifact ID or literal 'coverage'")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_trace)

    p = sub.add_parser("impact", help="Show typed transitive downstream impact of an artifact")
    p.add_argument("target")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_impact)

    p = sub.add_parser("github-sync", help="Synchronize EOS planning state to GitHub")
    p.add_argument("--apply", action="store_true", help="Actually create/update GitHub objects")
    p.add_argument("--project", default="", help="Optional GitHub Project number to add synced issues to")
    p.add_argument("--owner", default="", help="GitHub organization/user owning --project (defaults to repo owner)")
    p.set_defaults(func=cmd_github_sync)

    change = sub.add_parser("change", help="Govern architecture/requirements/specification changes")
    change_sub = change.add_subparsers(dest="change_command", required=True)
    p = change_sub.add_parser("create")
    p.add_argument("target")
    p.add_argument("summary")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_change_create)
    p = change_sub.add_parser("approve")
    p.add_argument("target")
    add_override_args(p)
    p.set_defaults(func=cmd_change_approve)
    p = change_sub.add_parser("apply")
    p.add_argument("target")
    p.set_defaults(func=cmd_change_apply)
    p = change_sub.add_parser("close")
    p.add_argument("target")
    p.set_defaults(func=cmd_change_close)

    maintain = sub.add_parser("maintain", help="Create/close maintenance work")
    maintain_sub = maintain.add_subparsers(dest="maintain_command", required=True)
    p = maintain_sub.add_parser("create")
    p.add_argument("type", choices=("bug", "debt", "security", "dependency", "operations", "performance", "documentation"))
    p.add_argument("summary")
    p.add_argument("--context", default="")
    p.set_defaults(func=cmd_maintain_create)
    p = maintain_sub.add_parser("plan")
    p.add_argument("target")
    p.set_defaults(func=cmd_maintain_plan)
    p = maintain_sub.add_parser("start")
    p.add_argument("target")
    p.set_defaults(func=cmd_maintain_start)
    p = maintain_sub.add_parser("verify")
    p.add_argument("target")
    p.set_defaults(func=cmd_maintain_verify)
    p = maintain_sub.add_parser("close")
    p.add_argument("target")
    p.add_argument("--force", action="store_true")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_maintain_close)

    p = sub.add_parser("release", help="Prepare/finalize a governed release")
    p.add_argument("version")
    p.add_argument("--publish", action="store_true", help="Push and create GitHub Release")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_release)

    planning = sub.add_parser("planning", help="Analyze PI/WC/WP dependency feasibility and execution order")
    planning_sub = planning.add_subparsers(dest="planning_command", required=True)
    p = planning_sub.add_parser("check")
    p.add_argument("pi")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_planning_check)
    p = planning_sub.add_parser("order")
    p.add_argument("pi")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_planning_order)
    p = planning_sub.add_parser("critical-path")
    p.add_argument("pi")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_planning_critical_path)
    p = planning_sub.add_parser("graph")
    p.add_argument("pi")
    p.add_argument("--format", choices=("text", "mermaid"), default="text")
    p.set_defaults(func=cmd_planning_graph)
    p = planning_sub.add_parser("size")
    p.add_argument("wp")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_planning_size)

    policy = sub.add_parser("policy", help="Inspect policy-as-code gate definitions")
    policy_sub = policy.add_subparsers(dest="policy_command", required=True)
    p = policy_sub.add_parser("list")
    p.set_defaults(func=cmd_policy_list)
    p = policy_sub.add_parser("show")
    p.add_argument("gate")
    p.set_defaults(func=cmd_policy_show)

    gate = sub.add_parser("gate", help="Evaluate/explain a named policy gate")
    gate_sub = gate.add_subparsers(dest="gate_command", required=True)
    for gate_action in ("check", "explain"):
        p = gate_sub.add_parser(gate_action)
        p.add_argument("gate")
        p.add_argument("target")
        p.add_argument("--json", action="store_true")
        p.set_defaults(func=cmd_gate)

    override = sub.add_parser("override", help="Create/list/expire durable human gate overrides")
    override_sub = override.add_subparsers(dest="override_command", required=True)
    p = override_sub.add_parser("create")
    p.add_argument("target")
    p.add_argument("gate")
    p.add_argument("--by", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--expires", default="")
    p.set_defaults(func=cmd_override_create)
    p = override_sub.add_parser("list")
    p.add_argument("target", nargs="?")
    p.add_argument("--active", action="store_true")
    p.set_defaults(func=cmd_override_list)
    p = override_sub.add_parser("expire")
    p.add_argument("override_id")
    p.set_defaults(func=cmd_override_expire)

    stale = sub.add_parser("stale", help="Inspect/clear stale dependency records")
    stale_sub = stale.add_subparsers(dest="stale_command", required=True)
    p = stale_sub.add_parser("list")
    p.add_argument("target", nargs="?")
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_stale_list)
    p = stale_sub.add_parser("clear")
    p.add_argument("stale_id")
    p.add_argument("--by", required=True)
    p.add_argument("--reason", required=True)
    p.set_defaults(func=cmd_stale_clear)

    p = sub.add_parser("events", help="Inspect the append-only EOS lifecycle event ledger")
    p.add_argument("target", nargs="?")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_events)

    p = sub.add_parser("state-machine", help="Inspect declarative lifecycle transitions")
    p.add_argument("target")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_state_machine)

    p = sub.add_parser("schema", help="Inspect an EOS entity/event schema")
    p.add_argument("name")
    p.set_defaults(func=cmd_schema)

    p = sub.add_parser("rebuild-state", help="Compare/repair lifecycle projections from the event ledger")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_rebuild_state)

    p = sub.add_parser("verify", help="Verify EOS registry/schema/state/event/traceability integrity")
    p.add_argument("--strict", action="store_true")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("doctor", help="Check local EOS dependencies and repository state")
    p.set_defaults(func=cmd_doctor)

    completion = sub.add_parser("completion", help="Generate/install dynamic shell tab completion")
    completion_sub = completion.add_subparsers(dest="completion_command", required=True)
    for shell_name in ("bash", "zsh", "fish"):
        p = completion_sub.add_parser(shell_name, help=f"Print {shell_name} completion script")
        p.set_defaults(func=cmd_completion)
    p = completion_sub.add_parser("write", help="Write repository-local completion files")
    p.set_defaults(func=cmd_completion)
    p = completion_sub.add_parser("install", help="Install completion into the user shell completion directory")
    p.add_argument("shell", nargs="?", choices=("bash", "zsh", "fish", "all"))
    p.set_defaults(func=cmd_completion)
    p = completion_sub.add_parser("candidates", help=argparse.SUPPRESS)
    p.add_argument("words", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_completion)

    p = sub.add_parser("responsibilities", help="Show Human/ChatGPT/Codex/GitHub responsibilities")
    p.set_defaults(func=cmd_responsibilities)

    return parser


def main() -> int:
    ensure_dirs()
    ensure_event_ledger_seeded()
    record_tool_upgrade_if_needed()
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except EosError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: command failed ({exc.returncode}): {' '.join(exc.cmd)}", file=sys.stderr)
        if exc.stdout:
            print(exc.stdout, file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return exc.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
