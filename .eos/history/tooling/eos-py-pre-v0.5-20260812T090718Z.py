#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import textwrap
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
    try:
        result = run(["git", "rev-parse", "--show-toplevel"])
        return Path(result.stdout.strip()).resolve()
    except Exception:
        return Path.cwd().resolve()


ROOT = discover_root()
EOS = ROOT / ".eos"


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


def set_lifecycle_state(target: str, state: str) -> None:
    kind, row = row_for_target(target)
    if state not in VALID_STATES[kind]:
        raise EosError(f"Invalid {kind} state: {state}")
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
    print(f"{rel(path)}: {current} -> {new} ({args.message})")


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
    print(f"Restored v{target} content as new version v{new_version}.")


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
    print(f"Created {pi_id}: {rel(path)}")
    print(f"Next: complete the PI definition, then ./scripts/eos review {pi_id}")


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
    print(f"Created {wc_id} under {pi}: {rel(path)}")


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
    print(f"Created {wp_id} under {wc}/{pi}: {rel(path)}")


def gate_authorization(target: str) -> list[str]:
    kind, row = row_for_target(target)
    reasons: list[str] = []
    path = ROOT / row["path"]
    complete, issues = artifact_is_complete_enough(path)
    if not complete:
        reasons.extend(issues)

    if kind == "WP":
        wc = find_row("WC", row["wc"])
        if not wc or wc["status"] not in {"AUTHORIZED", "ACTIVE"}:
            reasons.append(f"parent {row['wc']} is not authorized/active")
    elif kind == "WC":
        pi = find_row("PI", row["pi"])
        if not pi or pi["status"] not in {"AUTHORIZED", "ACTIVE"}:
            reasons.append(f"parent {row['pi']} is not authorized/active")
    elif kind == "PI":
        readiness = ROOT / "engineering" / "reviews" / f"{target}-READINESS-REVIEW.md"
        generic = review_path(target)
        bootstrap_rpath = ROOT / "engineering" / "reviews" / "PI-001-READINESS-REVIEW.md"
        candidates = [readiness, generic]
        if target == "PI-001":
            candidates.append(bootstrap_rpath)
        accepted_complete = [
            candidate for candidate in candidates
            if accepted_review_complete(candidate)[0]
        ]
        if not accepted_complete:
            reasons.append(
                "PI readiness review is not accepted and complete: "
                + " or ".join(rel(candidate) for candidate in candidates)
            )
    return reasons


def cmd_authorize(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind not in {"PI", "WC", "WP"}:
        raise EosError("authorize currently applies to PI, WC, or WP")
    reasons = gate_authorization(args.target)
    if reasons and not args.force:
        raise EosError(
            "Authorization gate failed:\n- " + "\n- ".join(reasons) +
            "\nUse --force --reason '...' only for an explicit human override."
        )
    actor = args.by or os.environ.get("USER") or "human"
    reason = args.reason or ("human authorization" if not reasons else "human override")
    set_lifecycle_state(args.target, "AUTHORIZED")
    record_decision(args.target, "authorize", "AUTHORIZED", actor, reason)
    print(f"{args.target} AUTHORIZED by {actor}.")
    if reasons:
        print("Override findings retained:")
        for item in reasons:
            print(f"  - {item}")


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
    set_lifecycle_state(args.target, new)
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
    if kind == "WP" and row["status"] in {"AUTHORIZED", "IN_PROGRESS"}:
        set_lifecycle_state(args.target, "VERIFYING")
    verify_ok, verify_report = verify_all()
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
        set_lifecycle_state(args.target, "IN_REVIEW")
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
    path = ROOT / row["path"]
    reasons: list[str] = []
    if row["status"] != "IN_REVIEW":
        reasons.append(f"work packet state is {row['status']}, expected IN_REVIEW")
    complete, issues = artifact_is_complete_enough(path)
    if not complete:
        reasons.extend(issues)
    if unchecked_boxes(path):
        reasons.append(f"{unchecked_boxes(path)} unchecked acceptance/exit item(s) remain")
    rpath = review_path(args.target)
    review_ok, review_issues = accepted_review_complete(rpath)
    if not review_ok:
        reasons.extend(review_issues)
    if reasons and not args.force:
        raise EosError("Closure gate failed:\n- " + "\n- ".join(reasons))
    set_lifecycle_state(args.target, "CLOSED")
    actor = args.by or os.environ.get("USER") or "human"
    record_decision(args.target, "close", "CLOSED", actor, args.reason or "work packet closure")
    print(f"{args.target} CLOSED.")


def cmd_close_cycle(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "WC":
        raise EosError("close-cycle requires a WC id")
    children = [wp for wp in registry("WP") if wp.get("wc") == args.target]
    open_children = [wp["id"] for wp in children if wp["status"] != "CLOSED"]
    reasons: list[str] = []
    if row["status"] != "IN_REVIEW":
        reasons.append(f"work cycle state is {row['status']}, expected IN_REVIEW")
    complete, issues = artifact_is_complete_enough(ROOT / row["path"])
    if not complete:
        reasons.extend(issues)
    if not children:
        reasons.append("work cycle has no registered work packets")
    if open_children:
        reasons.append("open work packets: " + ", ".join(open_children))
    rpath = review_path(args.target)
    review_ok, review_issues = accepted_review_complete(rpath)
    if not review_ok:
        reasons.extend(review_issues)
    if reasons and not args.force:
        raise EosError("Work-cycle closure gate failed:\n- " + "\n- ".join(reasons))
    set_lifecycle_state(args.target, "CLOSED")
    actor = args.by or os.environ.get("USER") or "human"
    record_decision(args.target, "close-cycle", "CLOSED", actor, args.reason or "work cycle closure")
    print(f"{args.target} CLOSED.")


def cmd_close_pi(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "PI":
        raise EosError("close-pi requires a PI id")
    children = [wc for wc in registry("WC") if wc.get("pi") == args.target]
    open_children = [wc["id"] for wc in children if wc["status"] != "CLOSED"]
    reasons: list[str] = []
    if row["status"] != "IN_REVIEW":
        reasons.append(f"program increment state is {row['status']}, expected IN_REVIEW")
    complete, issues = artifact_is_complete_enough(ROOT / row["path"])
    if not complete:
        reasons.extend(issues)
    if not children:
        reasons.append("program increment has no registered work cycles")
    if open_children:
        reasons.append("open work cycles: " + ", ".join(open_children))
    rpath = review_path(args.target)
    closeout = ROOT / "engineering" / "reviews" / f"{args.target}-CLOSEOUT-REVIEW.md"
    closeout_ok, closeout_issues = accepted_review_complete(closeout)
    generic_ok, generic_issues = accepted_review_complete(rpath)
    if not (closeout_ok or generic_ok):
        reasons.append(
            f"PI closeout review is not accepted and complete: {rel(closeout)} or {rel(rpath)}"
        )
        # Keep the most useful details without duplicating missing-review messages.
        reasons.extend(closeout_issues if closeout.exists() else generic_issues)
    if reasons and not args.force:
        raise EosError("PI closure gate failed:\n- " + "\n- ".join(reasons))
    set_lifecycle_state(args.target, "CLOSED")
    actor = args.by or os.environ.get("USER") or "human"
    record_decision(args.target, "close-pi", "CLOSED", actor, args.reason or "program increment closure")
    print(f"{args.target} CLOSED.")


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
    edges: dict[tuple[str, str, str], dict[str, str]] = {}
    for path in candidate_trace_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        source = source_id_for(path)
        for target in set(ID_RE.findall(text)):
            if target == source:
                continue
            key = (source, target, rel(path))
            edges[key] = {
                "source_id": source,
                "target_id": target,
                "source_path": rel(path),
            }
    fields = ["source_id", "target_id", "source_path"]
    rows = sorted(edges.values(), key=lambda r: (r["source_id"], r["target_id"], r["source_path"]))
    write_tsv(EOS / "trace-edges.tsv", fields, rows)
    return rows


def cmd_trace(args: argparse.Namespace) -> None:
    edges = rebuild_trace()
    target = args.target
    path = artifact_path_for_id(target)
    print(f"TRACE — {target}")
    print(f"Artifact: {rel(path) if path else '(not directly located)'}\n")

    outgoing = [e for e in edges if e["source_id"] == target]
    incoming = [e for e in edges if e["target_id"] == target]

    print("Depends on / references:")
    if outgoing:
        for e in outgoing:
            print(f"  {e['target_id']:<20} via {e['source_path']}")
    else:
        print("  none discovered")

    print("\nReferenced by:")
    if incoming:
        for e in incoming:
            print(f"  {e['source_id']:<20} via {e['source_path']}")
    else:
        print("  none discovered")


def cmd_impact(args: argparse.Namespace) -> None:
    edges = rebuild_trace()
    reverse: dict[str, set[str]] = {}
    locations: dict[tuple[str, str], set[str]] = {}
    for e in edges:
        reverse.setdefault(e["target_id"], set()).add(e["source_id"])
        locations.setdefault((e["target_id"], e["source_id"]), set()).add(e["source_path"])

    queue = deque([(args.target, 0)])
    seen = {args.target}
    results: list[tuple[int, str, str]] = []
    while queue:
        node, depth = queue.popleft()
        for dependent in sorted(reverse.get(node, set())):
            if dependent in seen:
                continue
            seen.add(dependent)
            results.append((depth + 1, dependent, ", ".join(sorted(locations.get((node, dependent), set())))))
            queue.append((dependent, depth + 1))

    print(f"IMPACT ANALYSIS — {args.target}\n")
    if not results:
        print("No downstream references discovered.")
        return
    for depth, entity, paths in results:
        print(f"{'  ' * (depth - 1)}- {entity}  [{paths}]")


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
        update_row(kind, target, github_url=url)


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
    print(f"Created {cr_id}: {rel(path)}")


def cmd_change_approve(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "CR":
        raise EosError("change approve requires CR-NNNN")
    path = ROOT / row["path"]
    if not is_review_accepted(path) and not args.force:
        # Change request uses its own Decision field; ACCEPTED/APPROVED counts.
        decision = review_decision(path)
        if decision not in {"APPROVED", "ACCEPTED"}:
            raise EosError(
                "Change request decision is not APPROVED/ACCEPTED. "
                "Update the artifact or use --force with an explicit reason."
            )
    update_row("CR", args.target, status="APPROVED")
    sync_artifact_state(path, "APPROVED")
    actor = args.by or os.environ.get("USER") or "human"
    record_decision(args.target, "change-approve", "APPROVED", actor, args.reason or "change approved")
    print(f"{args.target} APPROVED.")


def cmd_change_close(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "CR":
        raise EosError("change close requires CR-NNNN")
    update_row("CR", args.target, status="CLOSED")
    sync_artifact_state(ROOT / row["path"], "CLOSED")
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
    print(f"Created {mnt_id}: {rel(path)}")


def cmd_maintain_close(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "MNT":
        raise EosError("maintain close requires MNT-NNNN")
    path = ROOT / row["path"]
    if unchecked_boxes(path) and not args.force:
        raise EosError("Maintenance artifact still has unchecked completion items")
    update_row("MNT", args.target, status="CLOSED")
    sync_artifact_state(path, "CLOSED")
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
    verify_ok, report = verify_all()
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
        # Update lifecycle state before tagging; commit the release state.
        update_row("REL", rel_id, status="RELEASED")
        sync_artifact_state(path, "RELEASED")
        run(["git", "add", rel(path), rel(review), REGISTRY_PATHS["REL"]], cwd=ROOT)
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


def verify_all() -> tuple[bool, str]:
    failures: list[str] = []
    warnings: list[str] = []
    lines: list[str] = []

    required = [
        ROOT / "idea.md",
        EOS / "layers.tsv",
        EOS / "workflow.tsv",
        EOS / "artifacts.tsv",
        ROOT / "governance" / "responsibility-model.md",
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
            if row["status"] not in VALID_STATES[kind]:
                failures.append(f"{rid} has invalid state {row['status']}")
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


def cmd_verify(_: argparse.Namespace) -> None:
    ok, report = verify_all()
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
    print(f"\nroot: {ROOT}")
    print(f"branch: {current_branch() or '(unknown)'}")
    print(f"HEAD: {commit_sha() or '(none)'}")
    print(f"git: {git_status()}")


TOP_LEVEL_COMPLETION_COMMANDS = (
    "layers", "status", "next", "prompt", "complete", "reopen", "version",
    "history", "rollback", "checkpoint", "plan", "create-wc", "create-wp",
    "authorize", "start", "codex", "validate", "review", "close",
    "close-cycle", "close-pi", "trace", "impact", "github-sync", "change",
    "maintain", "release", "verify", "doctor", "responsibilities", "completion",
)

COMMAND_COMPLETION_OPTIONS = {
    "plan": ("--title", "--objective"),
    "create-wc": ("--pi", "--title"),
    "create-wp": ("--wc", "--domain", "--title"),
    "authorize": ("--force", "--reason", "--by"),
    "codex": ("--force",),
    "close": ("--force", "--reason", "--by"),
    "close-cycle": ("--force", "--reason", "--by"),
    "close-pi": ("--force", "--reason", "--by"),
    "github-sync": ("--apply", "--project", "--owner"),
    "release": ("--publish", "--force"),
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

    if command == "change" and len(args) == 1:
        return filter_completion(("create", "approve", "close"), current)
    if command == "maintain" and len(args) == 1:
        return filter_completion(("create", "close"), current)
    if command == "completion" and len(args) == 1:
        return filter_completion(("bash", "zsh", "fish", "write", "install"), current)

    previous = prior[-1] if prior else ""
    if previous == "--pi":
        return filter_completion(completion_ids("PI"), current)
    if previous == "--wc":
        return filter_completion(completion_ids("WC"), current)
    if previous == "--domain":
        return filter_completion(completion_domains(), current.upper())
    if command == "completion" and args and args[0] == "install" and len(args) <= 2:
        return filter_completion(("bash", "zsh", "fish", "all"), current)

    if current.startswith("-") or (current == "" and command in COMMAND_COMPLETION_OPTIONS):
        options = [o for o in COMMAND_COMPLETION_OPTIONS.get(command, ()) if o not in args]
        if command == "change" and args:
            subcmd = args[0]
            if subcmd == "create":
                options += [o for o in ("--reason",) if o not in args]
            elif subcmd == "approve":
                options += [o for o in ("--force", "--reason", "--by") if o not in args]
        elif command == "maintain" and args:
            subcmd = args[0]
            if subcmd == "create":
                options += [o for o in ("--context",) if o not in args]
            elif subcmd == "close":
                options += [o for o in ("--force",) if o not in args]
        return filter_completion(options, current)

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
    if command == "plan":
        if not current.startswith("-") and not prior:
            next_id = f"PI-{next_number('PI', 3):03d}"
            return filter_completion([next_id], current)
        return []
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
    if command in {"trace", "impact"}:
        return filter_completion(completion_artifact_ids(), current)
    if command == "release":
        if not current.startswith("-") and not prior:
            return filter_completion(completion_release_versions(), current)
        return []

    if command == "change" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "create" and len(subargs) <= 1:
            return filter_completion(completion_artifact_ids(), subcurrent)
        if subcmd in {"approve", "close"} and len(subargs) <= 1:
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
        if subcmd == "close" and len(subargs) <= 1:
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

    p = sub.add_parser("trace", help="Show direct traceability for an artifact ID")
    p.add_argument("target")
    p.set_defaults(func=cmd_trace)

    p = sub.add_parser("impact", help="Show transitive downstream impact of an artifact")
    p.add_argument("target")
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
    p = maintain_sub.add_parser("close")
    p.add_argument("target")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_maintain_close)

    p = sub.add_parser("release", help="Prepare/finalize a governed release")
    p.add_argument("version")
    p.add_argument("--publish", action="store_true", help="Push and create GitHub Release")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_release)

    p = sub.add_parser("verify", help="Verify EOS registry/state/traceability integrity")
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
