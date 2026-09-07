#!/usr/bin/env python3
"""Project canonical Monad planning/execution metadata into GitHub Projects.

Canonical Git/EOS artifacts remain authoritative. The projector derives planning
metadata from issue projections, but when an item references a registered Work
Packet its execution lifecycle, PI, Work Cycle, and domain are sourced from
`.eos/work-packets.tsv` before issue prose/labels are considered.

Project item field updates use GitHub's 2026 Project REST endpoint so all managed
fields for one item are updated in a single request.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

API_VERSION = "2026-03-10"
ROOT = Path(__file__).resolve().parents[1]
WORK_PACKETS = ROOT / ".eos" / "work-packets.tsv"

MANAGED_FIELDS = (
    "Item Type",
    "Product Goal",
    "Initiative",
    "Epic",
    "Feature",
    "Priority",
    "Product Area",
    "Domain",
    "Increment",
    "Work Cycle",
    "Work Packet",
    "Lifecycle",
    "Target Release",
)
SINGLE_SELECT_FIELDS = {"Item Type", "Priority", "Lifecycle"}
CORE_TYPES = {
    "Initiative",
    "Epic",
    "Feature",
    "Work Packet",
    "Defect",
    "Bug",
    "Change Request",
}

WORK_PACKET_LIFECYCLE = {
    "BACKLOG": "Backlog",
    "REFINING": "Refining",
    "READY": "Ready",
    "AUTHORIZED": "Authorized",
    "IN_PROGRESS": "Running",
    "RUNNING": "Running",
    "REVIEW": "Review",
    "VERIFIED": "Verified",
    "CLOSED": "Closed",
    "SUPERSEDED": "Closed",
    "BLOCKED": "Blocked",
}
LABEL_LIFECYCLE = {
    "status:backlog": "Backlog",
    "status:refining": "Refining",
    "status:ready": "Ready",
    "status:authorized": "Authorized",
    "status:active": "Running",
    "status:running": "Running",
    "status:review": "Review",
    "status:verified": "Verified",
    "status:done": "Closed",
    "status:closed": "Closed",
    "status:blocked": "Blocked",
}
RELEASE_LABELS = {
    "release:mvp-1": "MVP Release 1",
    "release:release-2": "Release 2",
}


def run_gh(
    *args: str,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["gh", *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
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


def label_names(row: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for raw in row.get("labels") or []:
        if isinstance(raw, str):
            name = raw
        else:
            name = raw.get("name") or ""
        if name:
            result.append(name)
    return result


def epic_to_initiative(epic: str) -> str:
    raw = match(r"EPIC-(\d+)", epic)
    if not raw:
        return ""
    number = int(raw)
    if number == 1:
        return "INIT-001"
    if 2 <= number <= 5:
        return "INIT-002"
    if 6 <= number <= 7:
        return "INIT-003"
    if 8 <= number <= 9:
        return "INIT-004"
    if 10 <= number <= 12:
        return "INIT-005"
    if 13 <= number <= 14:
        return "INIT-006"
    if number == 15:
        return "INIT-007"
    if 16 <= number <= 17:
        return "INIT-008"
    if number == 18:
        return "INIT-009"
    if 19 <= number <= 20:
        return "INIT-010"
    if number == 21:
        return "INIT-011"
    if number == 22:
        return "INIT-012"
    if number == 23:
        return "INIT-013"
    if number == 24:
        return "INIT-014"
    return ""


def initiative_to_product_goal(initiative: str) -> str:
    raw = match(r"INIT-(\d+)", initiative)
    if not raw:
        return ""
    number = int(raw)
    if 1 <= number <= 6:
        return "PG-001"
    if 7 <= number <= 8:
        return "PG-002"
    if 9 <= number <= 10:
        return "PG-003"
    if 11 <= number <= 14:
        return "PG-004"
    return ""


def item_type(title: str) -> str:
    raw = match(r"^\[([^\]]+)\]", title)
    aliases = {
        name.casefold(): name
        for name in (
            "Initiative",
            "Epic",
            "Feature",
            "Story",
            "Enabler",
            "Task",
            "Work Packet",
            "Defect",
            "Bug",
            "Change Request",
        )
    }
    return aliases.get(raw.casefold(), "")


def load_work_packets() -> dict[str, dict[str, str]]:
    if not WORK_PACKETS.exists():
        return {}
    with WORK_PACKETS.open(encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle, delimiter="\t")
        return {
            (row.get("id") or ""): {k: (v or "") for k, v in row.items()}
            for row in rows
            if row.get("id")
        }


def lifecycle_from_body(row: dict[str, Any]) -> str:
    state = (row.get("state") or "").upper()
    upper = (row.get("body") or "").upper()
    if state == "CLOSED":
        return "Closed"
    if "READY — NOT AUTHORIZED" in upper or "READY - NOT AUTHORIZED" in upper:
        return "Ready"
    if "**BLOCKED" in upper:
        return "Blocked"
    if (
        "**RUNNING" in upper
        or "**IN_PROGRESS" in upper
        or "**IN PROGRESS" in upper
    ):
        return "Running"
    if "**AUTHORIZED" in upper and "NOT AUTHORIZED" not in upper:
        return "Authorized"
    if "**VERIFIED" in upper:
        return "Verified"
    if "**REVIEW" in upper:
        return "Review"
    if "REMAINS **BACKLOG**" in upper:
        return "Backlog"
    return ""


def projected_lifecycle(
    row: dict[str, Any],
    work_packet: str,
    work_packets: dict[str, dict[str, str]],
) -> str:
    if work_packet and work_packet in work_packets:
        canonical = (work_packets[work_packet].get("status") or "").upper()
        mapped = WORK_PACKET_LIFECYCLE.get(canonical)
        if mapped:
            return mapped

    if (row.get("state") or "").upper() == "CLOSED":
        return "Closed"

    labels = {name.casefold() for name in label_names(row)}
    for label, value in LABEL_LIFECYCLE.items():
        if label in labels:
            return value
    return lifecycle_from_body(row)


def priority_from_labels(row: dict[str, Any]) -> str:
    for name in label_names(row):
        found = re.fullmatch(r"priority:(p[0-3])", name, re.I)
        if found:
            return found.group(1).upper()
    return ""


def area_from_labels(row: dict[str, Any]) -> str:
    for name in label_names(row):
        found = re.fullmatch(r"area:(.+)", name, re.I)
        if found:
            return found.group(1).strip()
    return ""


def release_from_labels(row: dict[str, Any]) -> str:
    names = {name.casefold() for name in label_names(row)}
    for label, value in RELEASE_LABELS.items():
        if label in names:
            return value
    return ""


def derive(
    row: dict[str, Any],
    work_packets: dict[str, dict[str, str]],
) -> dict[str, str]:
    title = row.get("title") or ""
    body = row.get("body") or ""
    kind = item_type(title)

    if not kind:
        cleared = {name: "" for name in MANAGED_FIELDS}
        return {"url": row.get("url") or "", **cleared}

    initiative = match(r"(INIT-\d{3})", title) if kind == "Initiative" else ""
    epic = (
        match(r"(EPIC-\d{3})", title)
        if kind == "Epic"
        else match(r"Parent Epic:\s*`(EPIC-\d{3})`", body)
    )
    feature = (
        match(r"(F-\d{3}-\d{2})", title)
        if kind == "Feature"
        else match(r"Parent Feature:\s*`(F-\d{3}-\d{2})`", body)
    )

    if not initiative:
        initiative = match(r"Initiative:\s*`(INIT-\d{3})`", body)
    if not initiative:
        initiative = epic_to_initiative(epic)

    product_goal = match(r"Product Goal:\s*`([^`]+)`", body)
    if not product_goal:
        product_goal = initiative_to_product_goal(initiative)

    work_packet = (
        match(r"Work Packet:\s*`([^`]+)`", body)
        or match(r"\b(WP-[A-Z0-9-]+)\b", title)
    )
    work_cycle = match(r"(?:Forecast\s+)?Work Cycle:\s*`([^`]+)`", body)
    increment = match(r"Program Increment:\s*`([^`]+)`", body)
    domain = ""

    canonical_wp = work_packets.get(work_packet) if work_packet else None
    if canonical_wp:
        increment = canonical_wp.get("pi") or increment
        work_cycle = canonical_wp.get("wc") or work_cycle
        domain = canonical_wp.get("domain") or ""

    return {
        "url": row.get("url") or "",
        "Item Type": kind,
        "Product Goal": product_goal,
        "Initiative": initiative,
        "Epic": epic,
        "Feature": feature,
        "Priority": priority_from_labels(row),
        "Product Area": area_from_labels(row),
        "Domain": domain,
        "Increment": increment,
        "Work Cycle": work_cycle,
        "Work Packet": work_packet,
        "Lifecycle": projected_lifecycle(row, work_packet, work_packets),
        "Target Release": release_from_labels(row),
    }


def projection_rows(
    issues: list[dict[str, Any]],
    work_packets: dict[str, dict[str, str]],
    mode: str,
) -> list[dict[str, str]]:
    rows = [derive(row, work_packets) for row in issues]
    if mode == "core":
        return [row for row in rows if row["Item Type"] in CORE_TYPES]
    return rows


def graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables})
    response = json.loads(
        run_gh("api", "graphql", "--input", "-", input_text=payload).stdout
    )
    if response.get("errors"):
        raise RuntimeError(f"GitHub GraphQL error: {response['errors']}")
    return response.get("data") or {}


def project_fields(org: str, number: int) -> tuple[str, list[dict[str, Any]]]:
    data = graphql(
        """
        query($org:String!,$number:Int!){
          organization(login:$org){
            projectV2(number:$number){
              id
              fields(first:100){
                nodes{
                  ... on ProjectV2FieldCommon { id databaseId name dataType }
                  ... on ProjectV2SingleSelectField {
                    id databaseId name dataType options { id name }
                  }
                }
              }
            }
          }
        }
        """,
        {"org": org, "number": number},
    )
    project = (data.get("organization") or {}).get("projectV2")
    if not project:
        raise RuntimeError(f"Could not resolve organization Project {org}#{number}")
    return project["id"], [field for field in project["fields"]["nodes"] if field]


def resolve_project_field(
    fields: list[dict[str, Any]], logical_name: str
) -> dict[str, Any]:
    exact = [
        field
        for field in fields
        if (field.get("name") or "").casefold() == logical_name.casefold()
    ]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        names = ", ".join(repr(field.get("name") or "") for field in exact)
        raise RuntimeError(
            f"duplicate exact Project fields for {logical_name!r}: {names}"
        )

    normalized = [
        field for field in fields if key(field.get("name")) == key(logical_name)
    ]
    if len(normalized) == 1:
        return normalized[0]
    if len(normalized) > 1:
        names = ", ".join(repr(field.get("name") or "") for field in normalized)
        raise RuntimeError(
            f"ambiguous legacy Project fields for {logical_name!r}: {names}; "
            "keep one canonical field and remove obsolete duplicates"
        )
    raise RuntimeError(
        f"canonical Project field {logical_name!r} could not be resolved"
    )


def project_item_database_ids(org: str, number: int) -> dict[str, str]:
    result: dict[str, str] = {}
    after: str | None = None
    while True:
        data = graphql(
            """
            query($org:String!,$number:Int!,$after:String){
              organization(login:$org){
                projectV2(number:$number){
                  items(first:100,after:$after){
                    nodes{
                      fullDatabaseId
                      content{
                        ... on Issue { url }
                        ... on PullRequest { url }
                      }
                    }
                    pageInfo{hasNextPage endCursor}
                  }
                }
              }
            }
            """,
            {"org": org, "number": number, "after": after},
        )
        project = (data.get("organization") or {}).get("projectV2")
        if not project:
            raise RuntimeError(
                f"Could not resolve organization Project {org}#{number}"
            )
        connection = project["items"]
        for item in connection["nodes"]:
            content = item.get("content") or {}
            url = content.get("url") or ""
            database_id = item.get("fullDatabaseId")
            if url and database_id is not None:
                result[url] = str(database_id)
        page_info = connection["pageInfo"]
        if not page_info.get("hasNextPage"):
            return result
        after = page_info.get("endCursor")


def select_option_id(field: dict[str, Any], value: str) -> str:
    for option in field.get("options") or []:
        if (option.get("name") or "").casefold() == value.casefold():
            return option.get("id") or ""
    return ""


def patch_item(
    org: str,
    project_number: str,
    item_database_id: str,
    updates: list[dict[str, Any]],
) -> subprocess.CompletedProcess[str]:
    payload = json.dumps({"fields": updates})
    return run_gh(
        "api",
        "--method",
        "PATCH",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        f"X-GitHub-Api-Version: {API_VERSION}",
        f"orgs/{org}/projectsV2/{project_number}/items/{item_database_id}",
        "--input",
        "-",
        input_text=payload,
        check=False,
    )


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "usage: sync-github-project-metadata.py ORG REPO PROJECT_NUMBER MODE",
            file=sys.stderr,
        )
        return 2
    org, repo, project_number, mode = sys.argv[1:]
    if mode not in {"core", "full"}:
        print(f"unsupported projection mode: {mode}", file=sys.stderr)
        return 2

    _, fields = project_fields(org, int(project_number))
    field_map = {
        name: resolve_project_field(fields, name) for name in MANAGED_FIELDS
    }
    for name, field in field_map.items():
        if field.get("databaseId") is None:
            raise RuntimeError(f"Project field {name!r} has no database ID")

    item_ids = project_item_database_ids(org, int(project_number))
    work_packets = load_work_packets()
    issues = load_gh_json(
        "issue",
        "list",
        "-R",
        f"{org}/{repo}",
        "--state",
        "all",
        "--limit",
        "1000",
        "--json",
        "title,body,url,state,labels",
    )

    rows = projection_rows(issues, work_packets, mode)

    failures = 0
    missing_options: set[tuple[str, str]] = set()
    print(
        f"Syncing {len(rows)} Project items with {mode} planning metadata "
        f"({len(work_packets)} canonical Work Packets loaded)..."
    )

    for index, row in enumerate(rows, start=1):
        url = row["url"]
        item_database_id = item_ids.get(url)
        if not item_database_id:
            failures += 1
            print(
                f"WARN: Project item database ID not found for {url}",
                file=sys.stderr,
            )
            continue

        updates: list[dict[str, Any]] = []
        for logical_name in MANAGED_FIELDS:
            field = field_map[logical_name]
            value = row[logical_name]
            projected_value: str | None = value or None
            if value and logical_name in SINGLE_SELECT_FIELDS:
                option_id = select_option_id(field, value)
                if not option_id:
                    missing_options.add((field.get("name") or logical_name, value))
                    continue
                projected_value = option_id
            updates.append(
                {"id": int(field["databaseId"]), "value": projected_value}
            )

        proc = patch_item(
            org,
            project_number,
            item_database_id,
            updates,
        )
        if proc.returncode != 0:
            failures += 1
            detail = proc.stderr.strip() or proc.stdout.strip() or "unknown gh error"
            print(
                f"WARN: could not update Project metadata for {url}: {detail}",
                file=sys.stderr,
            )

        if index % 20 == 0 or index == len(rows):
            print(f"  Project metadata: {index}/{len(rows)} items processed")

    for field_name, option_name in sorted(missing_options):
        print(
            f"NOTE: Project field {field_name!r} is missing single-select option "
            f"{option_name!r}. Run project-complete to converge required options.",
            file=sys.stderr,
        )

    if failures or missing_options:
        print(
            f"Metadata sync completed with {failures} failed item writes and "
            f"{len(missing_options)} missing select option(s).",
            file=sys.stderr,
        )
        return 1

    print("Metadata projection complete.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
