#!/usr/bin/env python3
"""Project canonical Monad planning metadata into GitHub Projects.

Uses the stable node-ID form of `gh project item-edit` so the projection works
across GitHub CLI versions that do not support newer field-name convenience
flags. Canonical Git/EOS artifacts remain authoritative.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import Any


def run_gh(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(["gh", *args], text=True, capture_output=True, check=False)
    if check and proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "unknown gh error"
        raise RuntimeError(f"gh {' '.join(args)} failed: {detail}")
    return proc


def load_gh_json(*args: str) -> Any:
    return json.loads(run_gh(*args).stdout)


def key(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def match(pattern: str, text: str) -> str:
    found = re.search(pattern, text or "", re.I | re.M)
    return found.group(1).strip() if found else ""


def epic_to_initiative(epic: str) -> str:
    raw = match(r"EPIC-(\d+)", epic)
    if not raw:
        return ""
    number = int(raw)
    if number == 1: return "INIT-001"
    if 2 <= number <= 5: return "INIT-002"
    if 6 <= number <= 7: return "INIT-003"
    if 8 <= number <= 9: return "INIT-004"
    if 10 <= number <= 12: return "INIT-005"
    if 13 <= number <= 14: return "INIT-006"
    return ""


def item_type(title: str) -> str:
    raw = match(r"^\[([^\]]+)\]", title)
    aliases = {name: name for name in (
        "Initiative", "Epic", "Feature", "Story", "Enabler",
        "Defect", "Bug", "Change Request"
    )}
    return aliases.get(raw, "")


def lifecycle(row: dict[str, Any]) -> str:
    state = (row.get("state") or "").upper()
    upper = (row.get("body") or "").upper()
    if state == "CLOSED": return "Closed"
    if "READY — NOT AUTHORIZED" in upper or "READY - NOT AUTHORIZED" in upper: return "Ready"
    if "REMAINS **BACKLOG**" in upper: return "Backlog"
    if "**BLOCKED" in upper: return "Blocked"
    if "**RUNNING" in upper: return "Running"
    if "**AUTHORIZED" in upper and "NOT AUTHORIZED" not in upper: return "Authorized"
    if "**VERIFIED" in upper: return "Verified"
    if "**REVIEW" in upper: return "Review"
    return ""


def derive(row: dict[str, Any]) -> dict[str, str]:
    title = row.get("title") or ""
    body = row.get("body") or ""
    kind = item_type(title)
    initiative = match(r"(INIT-\d{3})", title) if kind == "Initiative" else ""
    epic = match(r"(EPIC-\d{3})", title) if kind == "Epic" else match(r"Parent Epic:\s*`(EPIC-\d{3})`", body)
    if not initiative:
        initiative = epic_to_initiative(epic)
    product_goal = match(r"Product Goal:\s*`([^`]+)`", body)
    if not product_goal and (initiative or epic):
        product_goal = "PG-001"
    work_packet = match(r"Work Packet:\s*`([^`]+)`", body) or match(r"\b(WP-[A-Z0-9-]+)\b", title)
    work_cycle = match(r"(?:Work Cycle|Forecast Sprint):\s*`([^`]+)`", body)
    return {
        "url": row.get("url") or "",
        "Item Type": kind,
        "Product Goal": product_goal,
        "Initiative": initiative,
        "Epic": epic,
        "Work-Cycle": work_cycle,
        "Work-Packet": work_packet,
        "Lifecycle": lifecycle(row),
    }


def main() -> int:
    if len(sys.argv) != 5:
        print("usage: sync-github-project-metadata.py ORG REPO PROJECT_NUMBER MODE", file=sys.stderr)
        return 2
    org, repo, project_number, mode = sys.argv[1:]
    if mode not in {"core", "full"}:
        print(f"unsupported projection mode: {mode}", file=sys.stderr)
        return 2

    project = load_gh_json("project", "view", project_number, "--owner", org, "--format", "json")
    project_id = project.get("id")
    if not project_id:
        raise RuntimeError("GitHub Project node ID was not returned by gh project view")

    fields_payload = load_gh_json("project", "field-list", project_number, "--owner", org, "--format", "json", "--limit", "100")
    fields = fields_payload.get("fields", [])
    fields_by_key = {key(field.get("name")): field for field in fields}

    items_payload = load_gh_json("project", "item-list", project_number, "--owner", org, "--limit", "1000", "--format", "json")
    item_ids: dict[str, str] = {}
    for item in items_payload.get("items", []):
        content = item.get("content") or {}
        url = content.get("url") or ""
        item_id = item.get("id") or ""
        if url and item_id:
            item_ids[url] = item_id

    issues = load_gh_json("issue", "list", "-R", f"{org}/{repo}", "--state", "all", "--limit", "1000", "--json", "title,body,url,state")
    core_types = {"Initiative", "Epic", "Feature", "Defect", "Bug", "Change Request"}
    rows = [derive(row) for row in issues]
    if mode == "core":
        rows = [row for row in rows if row["Item Type"] in core_types]

    single_select_fields = {"Item Type", "Lifecycle"}
    missing_options: set[tuple[str, str]] = set()
    failures = 0
    print(f"Syncing {len(rows)} Project items with {mode} planning metadata...")

    def set_value(url: str, logical_name: str, value: str) -> None:
        nonlocal failures
        if not value:
            return
        item_id = item_ids.get(url)
        if not item_id:
            failures += 1
            print(f"WARN: Project item ID not found for {url}", file=sys.stderr)
            return
        field = fields_by_key.get(key(logical_name))
        if not field:
            failures += 1
            print(f"WARN: Project field '{logical_name}' not found", file=sys.stderr)
            return
        field_id = field.get("id") or ""
        if not field_id:
            failures += 1
            print(f"WARN: Project field '{logical_name}' has no node ID", file=sys.stderr)
            return

        args = ["project", "item-edit", "--id", item_id, "--project-id", project_id, "--field-id", field_id]
        if logical_name in single_select_fields:
            option_id = ""
            for option in field.get("options", []) or []:
                if (option.get("name") or "").casefold() == value.casefold():
                    option_id = option.get("id") or ""
                    break
            if not option_id:
                missing_options.add((field.get("name") or logical_name, value))
                return
            args += ["--single-select-option-id", option_id]
        else:
            args += ["--text", value]

        proc = run_gh(*args, check=False)
        if proc.returncode != 0:
            failures += 1
            detail = proc.stderr.strip() or proc.stdout.strip() or "unknown gh error"
            print(f"WARN: could not set Project field '{field.get('name')}'='{value}' for {url}: {detail}", file=sys.stderr)

    for index, row in enumerate(rows, start=1):
        url = row["url"]
        for logical_name in ("Item Type", "Product Goal", "Initiative", "Epic", "Work-Cycle", "Work-Packet", "Lifecycle"):
            set_value(url, logical_name, row[logical_name])
        if index % 5 == 0 or index == len(rows):
            print(f"  Project metadata: {index}/{len(rows)} items processed")

    for field_name, option_name in sorted(missing_options):
        print(f"NOTE: Project field '{field_name}' is missing single-select option '{option_name}'. Add it once in the Project UI and rerun the sync.", file=sys.stderr)

    if failures:
        print(f"Metadata sync completed with {failures} failed field writes.", file=sys.stderr)
        return 1
    print("Metadata projection complete.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
