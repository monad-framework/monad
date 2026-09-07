#!/usr/bin/env python3
"""Complete and verify the Monad Engineering Program GitHub Project.

This script mutates only the GitHub Project coordination projection. Canonical
Git/EOS artifacts remain authoritative.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import Any

API_VERSION = "2026-03-10"

ITEM_TYPE_OPTIONS = (
    "Initiative",
    "Epic",
    "Feature",
    "Story",
    "Enabler",
    "Task",
    "Work Packet",
    "Bug",
    "Defect",
    "Change Request",
)

LIFECYCLE_OPTIONS = (
    "Backlog",
    "Refining",
    "Ready",
    "Authorized",
    "Running",
    "Review",
    "Verified",
    "Closed",
    "Blocked",
)

OPTION_COLORS = {
    "Initiative": "PURPLE",
    "Epic": "PURPLE",
    "Feature": "BLUE",
    "Story": "GREEN",
    "Enabler": "YELLOW",
    "Task": "GRAY",
    "Work Packet": "GREEN",
    "Bug": "RED",
    "Defect": "RED",
    "Change Request": "ORANGE",
    "Backlog": "GRAY",
    "Refining": "YELLOW",
    "Ready": "BLUE",
    "Authorized": "PURPLE",
    "Running": "GREEN",
    "Review": "YELLOW",
    "Verified": "BLUE",
    "Closed": "GRAY",
    "Blocked": "RED",
}

OPTION_DESCRIPTIONS = {
    "Initiative": "Finite outcome-oriented program grouping beneath a Product Goal",
    "Epic": "Major capability or outcome within an Initiative",
    "Feature": "Feature-sized product or engineering outcome",
    "Story": "User/system outcome within a Feature",
    "Enabler": "Technical or architectural work enabling product outcomes",
    "Task": "Concrete refined unit of implementation work",
    "Work Packet": "Governed executable realization of planned work",
    "Bug": "Product defect",
    "Defect": "Engineering-system or control-plane defect",
    "Change Request": "Governed request to change accepted scope or behavior",
    "Backlog": "Planned but not yet Ready",
    "Refining": "Being refined toward readiness",
    "Ready": "Ready but not necessarily Authorized",
    "Authorized": "Explicitly authorized for execution",
    "Running": "Execution is in progress",
    "Review": "Awaiting review",
    "Verified": "Verification evidence accepted",
    "Closed": "Completed/closed",
    "Blocked": "Unable to proceed",
}

# Required Project views. The first six are the daily-use views; the remaining
# views are scoped projections for investigation and agent-assisted explanation.
REQUIRED_VIEWS: tuple[dict[str, Any], ...] = (
    {
        "name": "Program",
        "layout": "table",
        "filter": 'is:issue label:"type:initiative"',
        "visible": (
            "Title",
            "Product Goal",
            "Initiative",
            "Lifecycle",
            "Priority",
            "Target Release",
        ),
        "group_by": ("Product Goal",),
        "sort_by": (("Initiative", "asc"),),
    },
    {
        "name": "MVP Roadmap",
        "layout": "roadmap",
        "filter": (
            'is:issue label:"release:mvp-1" '
            'label:"type:initiative","type:epic","type:feature"'
        ),
        "group_by": ("Initiative",),
        "sort_by": (("Epic", "asc"), ("Feature", "asc")),
    },
    {
        "name": "Current Work",
        "layout": "board",
        "filter": "is:issue lifecycle:Ready,Authorized,Running,Review,Blocked",
        "visible": (
            "Title",
            "Initiative",
            "Epic",
            "Feature",
            "Work Cycle",
            "Work Packet",
            "Priority",
        ),
        "vertical_group_by": ("Lifecycle",),
    },
    {
        "name": "Next Up",
        "layout": "table",
        "filter": "is:issue lifecycle:Ready",
        "visible": (
            "Title",
            "Initiative",
            "Epic",
            "Feature",
            "Work Cycle",
            "Work Packet",
            "Priority",
            "Risk",
        ),
        "group_by": ("Initiative",),
        "sort_by": (("Priority", "asc"), ("Work Cycle", "asc")),
    },
    {
        "name": "Defects",
        "layout": "board",
        "filter": 'is:issue label:"type:defect","type:bug"',
        "visible": (
            "Title",
            "Lifecycle",
            "Priority",
            "Risk",
            "Product Area",
            "Domain",
        ),
        "vertical_group_by": ("Lifecycle",),
    },
    {
        "name": "Release 1",
        "layout": "table",
        "filter": 'is:issue label:"release:mvp-1"',
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Lifecycle",
            "Priority",
            "Work Cycle",
            "Work Packet",
        ),
        "group_by": ("Initiative",),
        "sort_by": (("Epic", "asc"), ("Feature", "asc")),
    },
    {
        "name": "Work Cycles",
        "layout": "table",
        "filter": "is:issue",
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Work Cycle",
            "Work Packet",
            "Lifecycle",
            "Priority",
        ),
        "group_by": ("Work Cycle",),
        "sort_by": (("Work Cycle", "asc"), ("Priority", "asc")),
    },
    {
        "name": "By Initiative",
        "layout": "table",
        "filter": "is:issue",
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Lifecycle",
            "Priority",
            "Work Cycle",
        ),
        "group_by": ("Initiative",),
        "sort_by": (("Epic", "asc"), ("Feature", "asc")),
    },
    {
        "name": "By Epic",
        "layout": "table",
        "filter": "is:issue",
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Lifecycle",
            "Priority",
            "Work Cycle",
        ),
        "group_by": ("Epic",),
        "sort_by": (("Feature", "asc"), ("Priority", "asc")),
    },
    {
        "name": "By Feature",
        "layout": "table",
        "filter": "is:issue",
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Lifecycle",
            "Priority",
            "Work Cycle",
            "Work Packet",
        ),
        "group_by": ("Feature",),
        "sort_by": (("Priority", "asc"),),
    },
    {
        "name": "Work Packets",
        "layout": "table",
        "filter": 'is:issue label:"type:work-packet"',
        "visible": (
            "Title",
            "Initiative",
            "Epic",
            "Feature",
            "Increment",
            "Work Cycle",
            "Work Packet",
            "Lifecycle",
            "Priority",
        ),
        "group_by": ("Work Cycle",),
        "sort_by": (("Work Cycle", "asc"), ("Priority", "asc")),
    },
    {
        "name": "Product Backlog",
        "layout": "table",
        "filter": 'is:issue label:"release:mvp-1" -lifecycle:Closed',
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Lifecycle",
            "Priority",
            "Work Cycle",
            "Work Packet",
        ),
        "group_by": ("Initiative",),
        "sort_by": (("Priority", "asc"), ("Work Cycle", "asc")),
    },
    {
        "name": "Blocked",
        "layout": "table",
        "filter": "is:issue lifecycle:Blocked",
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Priority",
            "Risk",
            "Work Cycle",
            "Work Packet",
        ),
        "group_by": ("Initiative",),
        "sort_by": (("Priority", "asc"),),
    },
    {
        "name": "Dogfooding",
        "layout": "table",
        "filter": 'is:issue label:"area:github"',
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Lifecycle",
            "Priority",
            "Work Cycle",
            "Work Packet",
        ),
        "group_by": ("Epic",),
        "sort_by": (("Priority", "asc"),),
    },
    {
        "name": "AI / Agents",
        "layout": "table",
        "filter": 'is:issue label:"area:agent","area:execution"',
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Lifecycle",
            "Executor",
            "Priority",
            "Work Cycle",
        ),
        "group_by": ("Initiative",),
        "sort_by": (("Epic", "asc"), ("Priority", "asc")),
    },
    {
        "name": "Semantic Core",
        "layout": "table",
        "filter": (
            'is:issue label:"area:workspace","area:ingestion","area:graph",'
            '"area:kir","area:diagnostics","area:query"'
        ),
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Lifecycle",
            "Priority",
            "Work Cycle",
            "Work Packet",
        ),
        "group_by": ("Epic",),
        "sort_by": (("Feature", "asc"), ("Priority", "asc")),
    },
    {
        "name": "Architecture & Specs",
        "layout": "table",
        "filter": 'is:issue label:"area:governance"',
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Lifecycle",
            "ADR",
            "Specification",
            "Priority",
        ),
        "group_by": ("Initiative",),
        "sort_by": (("Epic", "asc"), ("Priority", "asc")),
    },
    {
        "name": "Codex Queue",
        "layout": "table",
        "filter": "is:issue executor:Codex,Mixed lifecycle:Ready,Authorized,Running",
        "visible": (
            "Title",
            "Executor",
            "Lifecycle",
            "Initiative",
            "Epic",
            "Feature",
            "Work Cycle",
            "Work Packet",
            "Priority",
            "Risk",
        ),
        "group_by": ("Lifecycle",),
        "sort_by": (("Priority", "asc"), ("Work Cycle", "asc")),
    },
    {
        "name": "Release Readiness",
        "layout": "table",
        "filter": 'is:issue label:"release:mvp-1" label:"area:release"',
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Lifecycle",
            "Priority",
            "Risk",
            "Work Cycle",
            "Work Packet",
        ),
        "group_by": ("Epic",),
        "sort_by": (("Priority", "asc"), ("Work Cycle", "asc")),
    },
    {
        "name": "Risks & Decisions",
        "layout": "table",
        "filter": "is:issue risk:Critical,High",
        "visible": (
            "Title",
            "Risk",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "ADR",
            "Specification",
            "Lifecycle",
            "Priority",
        ),
        "group_by": ("Initiative",),
        "sort_by": (("Risk", "asc"), ("Priority", "asc")),
    },
    {
        "name": "Recently Completed",
        "layout": "table",
        "filter": "is:issue lifecycle:Verified,Closed updated:>@today-30d",
        "visible": (
            "Title",
            "Item Type",
            "Initiative",
            "Epic",
            "Feature",
            "Lifecycle",
            "Updated",
        ),
        "group_by": ("Initiative",),
        "sort_by": (("Updated", "desc"),),
    },
)


def run(
    args: list[str],
    *,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        args,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "unknown command error"
        raise RuntimeError(f"{' '.join(args)} failed: {detail}")
    return proc


def gh_json(*args: str) -> Any:
    return json.loads(run(["gh", *args]).stdout)


def graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables})
    response = json.loads(
        run(["gh", "api", "graphql", "--input", "-"], input_text=payload).stdout
    )
    if response.get("errors"):
        raise RuntimeError(f"GitHub GraphQL error: {response['errors']}")
    return response["data"]


def normalized(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").casefold())


def project_query(org: str, number: int) -> dict[str, Any]:
    data = graphql(
        """
        query($org:String!,$number:Int!){
          organization(login:$org){
            projectV2(number:$number){
              id
              number
              title
              fields(first:100){
                nodes{
                  ... on ProjectV2FieldCommon{id name dataType}
                  ... on ProjectV2SingleSelectField{
                    id
                    name
                    dataType
                    options{id name color description}
                  }
                }
              }
              views(first:100){
                nodes{id number name layout filter}
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
    return project


def resolve_field(
    fields: list[dict[str, Any]],
    wanted: str,
    *,
    allow_legacy_equivalent: bool = True,
) -> dict[str, Any]:
    exact = [
        field
        for field in fields
        if (field.get("name") or "").casefold() == wanted.casefold()
    ]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        names = sorted({field.get("name") or "" for field in exact})
        raise RuntimeError(f"Ambiguous Project fields for {wanted!r}: {names}")

    if allow_legacy_equivalent:
        equivalent = [
            field
            for field in fields
            if normalized(field.get("name")) == normalized(wanted)
        ]
        if len(equivalent) == 1:
            return equivalent[0]
        if len(equivalent) > 1:
            names = sorted({field.get("name") or "" for field in equivalent})
            raise RuntimeError(f"Ambiguous Project fields for {wanted!r}: {names}")

    raise RuntimeError(f"Required Project field not found: {wanted}")


def canonicalize_field_names(project: dict[str, Any]) -> int:
    """Rename punctuation-only legacy fields without changing field identity."""
    changes = 0
    fields = [field for field in project["fields"]["nodes"] if field]
    for canonical in ("Work Cycle", "Work Packet"):
        exact = [
            field
            for field in fields
            if (field.get("name") or "").casefold() == canonical.casefold()
        ]
        if exact:
            continue
        equivalent = [
            field
            for field in fields
            if normalized(field.get("name")) == normalized(canonical)
        ]
        if len(equivalent) > 1:
            names = sorted({field.get("name") or "" for field in equivalent})
            raise RuntimeError(
                f"Cannot canonicalize {canonical!r}; ambiguous legacy fields: {names}"
            )
        if len(equivalent) != 1:
            continue
        field = equivalent[0]
        old_name = field.get("name") or ""
        graphql(
            """
            mutation($fieldId:ID!,$name:String!){
              updateProjectV2Field(input:{fieldId:$fieldId,name:$name}){
                projectV2Field{... on ProjectV2FieldCommon{id name}}
              }
            }
            """,
            {"fieldId": field["id"], "name": canonical},
        )
        print(f"Renamed Project field {old_name!r} -> {canonical!r}.")
        changes += 1
    return changes


def ensure_single_select_options(
    project: dict[str, Any],
    field_name: str,
    required: tuple[str, ...],
) -> int:
    fields = [field for field in project["fields"]["nodes"] if field]
    field = resolve_field(fields, field_name)
    if field.get("dataType") != "SINGLE_SELECT":
        raise RuntimeError(f"Project field {field_name!r} is not SINGLE_SELECT")

    existing = list(field.get("options") or [])
    have = {(option.get("name") or "").casefold() for option in existing}
    missing = [name for name in required if name.casefold() not in have]
    if not missing:
        print(f"Project field {field.get('name')!r}: all required options present.")
        return 0

    options = []
    for option in existing:
        options.append(
            {
                "id": option["id"],
                "name": option["name"],
                "color": option.get("color") or "GRAY",
                "description": option.get("description") or "",
            }
        )
    for name in missing:
        options.append(
            {
                "name": name,
                "color": OPTION_COLORS.get(name, "GRAY"),
                "description": OPTION_DESCRIPTIONS.get(name, ""),
            }
        )

    # Existing option IDs are passed back deliberately so values already stored
    # on Project items are preserved when the options list is overwritten.
    graphql(
        """
        mutation(
          $fieldId:ID!,
          $options:[ProjectV2SingleSelectFieldOptionInput!]!
        ){
          updateProjectV2Field(
            input:{fieldId:$fieldId,singleSelectOptions:$options}
          ){
            projectV2Field{
              ... on ProjectV2SingleSelectField{id name}
            }
          }
        }
        """,
        {"fieldId": field["id"], "options": options},
    )
    print(
        f"Project field {field.get('name')!r}: "
        f"added option(s): {', '.join(missing)}"
    )
    return len(missing)


def rest_fields(org: str, number: int) -> list[dict[str, Any]]:
    return gh_json(
        "api",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        f"X-GitHub-Api-Version: {API_VERSION}",
        f"orgs/{org}/projectsV2/{number}/fields?per_page=100",
    )


def field_database_id(fields: list[dict[str, Any]], wanted: str) -> int:
    exact = [
        field
        for field in fields
        if (field.get("name") or "").casefold() == wanted.casefold()
    ]
    if len(exact) == 1:
        return int(exact[0]["id"])
    if len(exact) > 1:
        names = sorted({field.get("name") or "" for field in exact})
        raise RuntimeError(f"Ambiguous REST Project fields for {wanted!r}: {names}")

    equivalent = [
        field
        for field in fields
        if normalized(field.get("name")) == normalized(wanted)
    ]
    if len(equivalent) == 1:
        return int(equivalent[0]["id"])
    if len(equivalent) > 1:
        names = sorted({field.get("name") or "" for field in equivalent})
        raise RuntimeError(f"Ambiguous REST Project fields for {wanted!r}: {names}")
    raise RuntimeError(f"Required REST Project field not found: {wanted}")


def create_view(
    org: str,
    number: int,
    spec: dict[str, Any],
    fields: list[dict[str, Any]],
) -> None:
    body: dict[str, Any] = {
        "name": spec["name"],
        "layout": spec["layout"],
        "filter": spec["filter"],
    }
    if spec["layout"] != "roadmap":
        body["visible_fields"] = [
            field_database_id(fields, name) for name in spec.get("visible", ())
        ]
    if spec.get("group_by"):
        body["group_by"] = [field_database_id(fields, spec["group_by"][0])]
    if spec.get("vertical_group_by"):
        body["vertical_group_by"] = [
            field_database_id(fields, spec["vertical_group_by"][0])
        ]
    if spec.get("sort_by"):
        body["sort_by"] = [
            [field_database_id(fields, name), direction]
            for name, direction in spec["sort_by"]
        ]

    run(
        [
            "gh",
            "api",
            "--method",
            "POST",
            "-H",
            "Accept: application/vnd.github+json",
            "-H",
            f"X-GitHub-Api-Version: {API_VERSION}",
            f"orgs/{org}/projectsV2/{number}/views",
            "--input",
            "-",
        ],
        input_text=json.dumps(body),
    )


def ensure_views(org: str, number: int) -> int:
    project = project_query(org, number)
    existing = {
        (view.get("name") or "").casefold(): view
        for view in project["views"]["nodes"]
        if view
    }
    fields = rest_fields(org, number)
    created = 0
    for spec in REQUIRED_VIEWS:
        current = existing.get(spec["name"].casefold())
        if current:
            print(
                f"Project view {spec['name']!r} already exists "
                f"(#{current.get('number')}, {current.get('layout')})."
            )
            continue
        create_view(org, number, spec, fields)
        created += 1
        print(f"Created Project view: {spec['name']}")
    return created


def verify(org: str, repo: str, number: int) -> int:
    failures: list[str] = []
    warnings: list[str] = []
    project = project_query(org, number)
    fields = [field for field in project["fields"]["nodes"] if field]

    required_fields = (
        "Item Type",
        "Product Goal",
        "Initiative",
        "Epic",
        "Feature",
        "Priority",
        "Criticality",
        "Product Area",
        "Domain",
        "Increment",
        "Work Cycle",
        "Lifecycle",
        "Story Points",
        "Risk",
        "Executor",
        "Work Packet",
        "Specification",
        "ADR",
        "Target Release",
        "Start Date",
        "Target Date",
    )
    for field_name in required_fields:
        try:
            resolve_field(fields, field_name, allow_legacy_equivalent=False)
        except RuntimeError as exc:
            failures.append(str(exc))

    for field_name, required in (
        ("Item Type", ITEM_TYPE_OPTIONS),
        ("Lifecycle", LIFECYCLE_OPTIONS),
    ):
        try:
            field = resolve_field(fields, field_name)
            names = {
                (option.get("name") or "").casefold()
                for option in field.get("options") or []
            }
            missing = [name for name in required if name.casefold() not in names]
            if missing:
                failures.append(
                    f"{field_name} missing option(s): {', '.join(missing)}"
                )
        except RuntimeError as exc:
            failures.append(str(exc))

    view_by_name = {
        (view.get("name") or "").casefold(): view
        for view in project["views"]["nodes"]
        if view
    }
    for spec in REQUIRED_VIEWS:
        view = view_by_name.get(spec["name"].casefold())
        if not view:
            failures.append(f"Required Project view missing: {spec['name']}")
            continue
        if (view.get("layout") or "").casefold() != spec["layout"].casefold():
            warnings.append(
                f"View {spec['name']!r} exists with layout "
                f"{view.get('layout')!r}; expected {spec['layout']!r}"
            )
        actual_filter = (view.get("filter") or "").strip()
        if actual_filter and actual_filter != spec["filter"]:
            warnings.append(
                f"View {spec['name']!r} preserves existing custom filter "
                f"{actual_filter!r}; canonical default is {spec['filter']!r}"
            )

    total_issues = len(
        gh_json(
            "issue",
            "list",
            "-R",
            f"{org}/{repo}",
            "--state",
            "all",
            "--limit",
            "1000",
            "--json",
            "number",
        )
    )
    total_items = len(
        gh_json(
            "project",
            "item-list",
            str(number),
            "--owner",
            org,
            "--limit",
            "1000",
            "--format",
            "json",
        ).get("items", [])
    )
    if total_items < total_issues:
        failures.append(
            f"Project has {total_items} items but repository has {total_issues} issues"
        )

    representative_queries = (
        ("initiatives", 'label:"type:initiative"', 1),
        ("MVP Release 1", 'label:"release:mvp-1"', 1),
        ("Tasks", 'title:"[Task]"', 1),
        ("Ready or active work", "lifecycle:Ready,Authorized,Running", 1),
    )
    for label, query, minimum in representative_queries:
        result = gh_json(
            "project",
            "item-list",
            str(number),
            "--owner",
            org,
            "--limit",
            "1000",
            "--query",
            query,
            "--format",
            "json",
        )
        count = len(result.get("items", []))
        if count < minimum:
            failures.append(
                f"Project query check {label!r} returned {count}; "
                f"expected at least {minimum}"
            )
        else:
            print(f"Verification query {label!r}: {count} item(s).")

    # PI and Sprint are deliberately not deleted automatically. They may contain
    # historical values from the pre-canonical Project configuration, so deletion
    # requires a separate value migration/audit rather than an unsafe cleanup.
    legacy_names = {(field.get("name") or "").casefold() for field in fields}
    for legacy in ("PI", "Sprint"):
        if legacy.casefold() in legacy_names:
            warnings.append(
                f"Legacy compatibility field {legacy!r} remains; retain until "
                "its values have been audited against canonical fields"
            )

    for warning in warnings:
        print(f"NOTE: {warning}", file=sys.stderr)

    if failures:
        print("GitHub Project verification FAILED:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print(
        "GitHub Project verification passed: "
        f"{total_items} project items, {total_issues} repository issues, "
        f"{len(REQUIRED_VIEWS)} required views, canonical fields/options present."
    )
    return 0


def complete(org: str, repo: str, number: int) -> int:
    project = project_query(org, number)
    canonicalize_field_names(project)

    project = project_query(org, number)
    ensure_single_select_options(project, "Item Type", ITEM_TYPE_OPTIONS)

    project = project_query(org, number)
    ensure_single_select_options(project, "Lifecycle", LIFECYCLE_OPTIONS)

    ensure_views(org, number)
    return verify(org, repo, number)


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "usage: configure-github-project.py "
            "ORG REPO PROJECT_NUMBER "
            "{options|views|verify|complete}",
            file=sys.stderr,
        )
        return 2

    org, repo, raw_number, action = sys.argv[1:]
    number = int(raw_number)

    if action == "options":
        project = project_query(org, number)
        canonicalize_field_names(project)
        project = project_query(org, number)
        ensure_single_select_options(project, "Item Type", ITEM_TYPE_OPTIONS)
        project = project_query(org, number)
        ensure_single_select_options(project, "Lifecycle", LIFECYCLE_OPTIONS)
        return 0
    if action == "views":
        ensure_views(org, number)
        return 0
    if action == "verify":
        return verify(org, repo, number)
    if action == "complete":
        return complete(org, repo, number)

    print(f"unsupported action: {action}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
