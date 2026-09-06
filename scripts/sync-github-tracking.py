#!/usr/bin/env python3
"""Project Monad's approved product roadmap into GitHub tracking objects.

Canonical Git/EOS artifacts remain authoritative. GitHub Issues, labels,
milestones, and sub-issue relationships are coordination projections only.
Formal implementation Tasks are intentionally excluded from this projection;
Tasks remain rolling-wave and are refined only as a Work Packet approaches Ready.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MVP_BACKLOG = ROOT / "product" / "backlog" / "MVP-BACKLOG.md"
EXPANDED_BACKLOG = ROOT / "product" / "backlog" / "EXPANDED-BACKLOG.md"
INITIATIVES = ROOT / "product" / "initiatives.md"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "monad-framework/monad")
API_ROOT = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
OWNER, REPO = REPOSITORY.split("/", 1)
API_VERSION = "2022-11-28"

LABELS: dict[str, tuple[str, str]] = {
    "type:initiative": ("8b5cf6", "Finite outcome-oriented program grouping beneath a Product Goal"),
    "type:epic": ("6f42c1", "Outcome spanning multiple features"),
    "type:feature": ("1d76db", "Feature-sized product or engineering outcome"),
    "type:work-packet": ("0e8a16", "Feature has a forecast or canonical Work Packet"),
    "type:story": ("2da44e", "User or system story within a feature"),
    "type:enabler": ("0e8a16", "Engineering enabler within a feature"),
    "status:backlog": ("d0d7de", "Planned but not yet Ready"),
    "status:ready": ("0e8a16", "Refined and ready for authorization"),
    "status:active": ("fbca04", "Currently active"),
    "status:review": ("5319e7", "Awaiting review or acceptance"),
    "status:blocked": ("b60205", "Blocked from progressing"),
    "status:done": ("8250df", "Accepted and complete"),
    "priority:p0": ("b60205", "Release- or program-blocking priority"),
    "priority:p1": ("d93f0b", "High priority on the current critical path"),
    "priority:p2": ("fbca04", "Normal planned roadmap priority"),
    "priority:p3": ("d0d7de", "Lower priority or deferrable"),
    "release:mvp-1": ("5319e7", "Targeted to MVP Release 1"),
    "release:release-2": ("7057ff", "Targeted to the approved post-MVP Release 2 horizon"),
    "area:governance": ("c5def5", "Governance, authority, planning, and EOS"),
    "area:workspace": ("c5def5", "Repository identity, configuration, and discovery"),
    "area:ingestion": ("c5def5", "Canonical knowledge ingestion and parsing"),
    "area:graph": ("c5def5", "Semantic graph ontology, construction, and integrity"),
    "area:kir": ("c5def5", "Kernel Intermediate Representation"),
    "area:diagnostics": ("c5def5", "Diagnostics, validation, and conformance"),
    "area:query": ("c5def5", "Graph query and explanation"),
    "area:agent": ("c5def5", "AI agent context, orchestration, and governance"),
    "area:cli": ("c5def5", "CLI and developer experience"),
    "area:quality": ("c5def5", "Determinism, reliability, performance, and scale"),
    "area:execution": ("c5def5", "Change intelligence and native validation"),
    "area:github": ("c5def5", "Dogfooding and GitHub projection"),
    "area:release": ("c5def5", "Packaging, documentation, acceptance, and release"),
    "area:intelligence": ("c5def5", "Workspace intelligence, memory, health, and learning"),
    "area:integration": ("c5def5", "Automation, adapters, ecosystem, and integration surfaces"),
    "area:security": ("c5def5", "Identity, attestation, cryptography, and AI security"),
    "area:observability": ("c5def5", "Telemetry, analytics, health, and operations"),
    "area:deployment": ("c5def5", "Deployment, portability, workspace lifecycle, and environments"),
}

AREA_BY_EPIC = {
    "001": "area:governance", "002": "area:workspace", "003": "area:ingestion",
    "004": "area:graph", "005": "area:kir", "006": "area:diagnostics",
    "007": "area:query", "008": "area:agent", "009": "area:cli",
    "010": "area:quality", "011": "area:execution", "012": "area:github",
    "013": "area:release", "014": "area:release", "015": "area:intelligence",
    "016": "area:agent", "017": "area:integration", "018": "area:security",
    "019": "area:governance", "020": "area:observability", "021": "area:deployment",
    "022": "area:integration", "023": "area:quality", "024": "area:release",
}

MILESTONES = [
    ("M-000", "M-000 Foundation Stabilized", "Foundation stabilization gate: coherent authority, synchronized machine layer, and GitHub-operational MVP program.", "2026-08-16T23:59:59Z"),
    ("M-MVP-001", "M-MVP-001 Semantic Kernel Alpha", "PI-MVP-001 exit: identity, ingestion, semantic graph, KIR, diagnostics, and validation baseline.", "2026-09-13T23:59:59Z"),
    ("M-MVP-002", "M-MVP-002 MVP Beta", "PI-MVP-002 exit: query/explain, bounded agent context, CLI, and trust/performance baseline.", "2026-10-11T23:59:59Z"),
    ("M-MVP-003", "M-MVP-003 MVP Release 1", "PI-MVP-003 exit and MVP Release 1 acceptance gate.", "2026-11-08T23:59:59Z"),
    ("M-004", "M-004 Living Intelligence Alpha", "PI-EXP-001 exit: living workspace intelligence, bounded autonomous orchestration, and governed automation baseline.", "2026-12-13T23:59:59Z"),
    ("M-005", "M-005 Governed Automation Beta", "PI-EXP-002 exit: security, identity, attestation, policy, change control, audit, and operational observability baseline.", "2027-01-10T23:59:59Z"),
    ("M-006", "M-006 Living Engineering OS Release 2", "PI-EXP-003 exit and Release 2 acceptance gate for deployment, ecosystem, scale, and expanded end-to-end readiness.", "2027-02-14T23:59:59Z"),
]


@dataclass(frozen=True)
class Initiative:
    ident: str
    title: str
    product_goal: str
    outcome: str
    epics: tuple[str, ...]
    exit_condition: str


@dataclass(frozen=True)
class Epic:
    ident: str
    title: str
    outcome: str
    forecast: str
    source: str


@dataclass(frozen=True)
class Feature:
    ident: str
    title: str
    work_packet: str
    work_cycle: str
    children: tuple[tuple[str, str], ...]
    source: str

    @property
    def epic_id(self) -> str:
        return f"EPIC-{self.ident.split('-')[1]}"


def api(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    if not TOKEN:
        raise SystemExit("GITHUB_TOKEN is required")
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{API_ROOT}{path}", data=data, method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "monad-github-tracking-sync",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
            return None if not raw else json.loads(raw.decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"{method} {path}: HTTP {exc.code}: {detail}") from exc


def paged(path: str) -> list[dict[str, Any]]:
    sep = "&" if "?" in path else "?"
    result: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = api("GET", f"{path}{sep}per_page=100&page={page}")
        if not isinstance(batch, list):
            raise RuntimeError(f"expected list from {path}")
        result.extend(batch)
        if len(batch) < 100:
            return result
        page += 1


def parse_initiatives() -> list[Initiative]:
    text = INITIATIVES.read_text(encoding="utf-8")
    lines = text.splitlines()
    initiatives: list[Initiative] = []
    current_goal = ""
    current: dict[str, Any] | None = None
    section = ""

    def flush() -> None:
        nonlocal current
        if current is None:
            return
        outcome = " ".join(current["outcome"]).strip()
        exit_condition = " ".join(current["exit"]).strip()
        initiatives.append(Initiative(
            current["ident"], current["title"], current["product_goal"],
            outcome, tuple(current["epics"]), exit_condition,
        ))
        current = None

    for raw in lines:
        line = raw.strip()
        goal_match = re.match(r"^# (PG-\d{3})\s+—\s+(.+)$", line)
        if goal_match:
            flush()
            current_goal = goal_match.group(1)
            section = ""
            continue
        init_match = re.match(r"^## (INIT-\d{3})\s+—\s+(.+)$", line)
        if init_match:
            flush()
            if not current_goal:
                raise RuntimeError(f"initiative {init_match.group(1)} has no Product Goal heading")
            current = {
                "ident": init_match.group(1), "title": init_match.group(2),
                "product_goal": current_goal, "outcome": [], "epics": [], "exit": [],
            }
            section = ""
            continue
        if current is None:
            continue
        if line.startswith("**Outcome:**"):
            current["outcome"].append(line.split("**Outcome:**", 1)[1].strip())
            section = "outcome"
            continue
        if line == "### Epics":
            section = "epics"
            continue
        if line == "### Exit condition":
            section = "exit"
            continue
        if line.startswith("## Initiative mapping"):
            flush()
            break
        if section == "epics":
            epic_match = re.match(r"^- `(EPIC-\d{3})`\s+—\s+.+$", line)
            if epic_match:
                current["epics"].append(epic_match.group(1))
        elif section == "outcome" and line and not line.startswith("#"):
            current["outcome"].append(line)
        elif section == "exit" and line and not line.startswith("#"):
            current["exit"].append(line)
    flush()

    if len(initiatives) != 14:
        raise RuntimeError(f"unexpected initiative inventory: {len(initiatives)}")
    ids = [item.ident for item in initiatives]
    expected_ids = [f"INIT-{n:03d}" for n in range(1, 15)]
    if ids != expected_ids:
        raise RuntimeError(f"unexpected initiative IDs: {ids}")
    epic_ids = [epic for item in initiatives for epic in item.epics]
    expected_epics = [f"EPIC-{n:03d}" for n in range(1, 25)]
    if epic_ids != expected_epics:
        raise RuntimeError(f"initiative Epic coverage mismatch: {epic_ids}")
    if any(not item.outcome or not item.exit_condition for item in initiatives):
        raise RuntimeError("initiative outcome/exit condition is missing")
    return initiatives


def parse_backlog(
    path: Path,
    *,
    expected_epics: int,
    expected_features: int,
    expected_stories: int,
    expected_enablers: int,
) -> tuple[list[Epic], list[Feature]]:
    text = path.read_text(encoding="utf-8")
    try:
        epic_section = text.split("## Epic roadmap", 1)[1].split("## Feature / Work Packet map", 1)[0]
        feature_section = text.split("## Feature / Work Packet map", 1)[1]
    except IndexError as exc:
        raise RuntimeError(f"required backlog sections missing in {path}") from exc

    source = path.relative_to(ROOT).as_posix()
    epics: list[Epic] = []
    features: list[Feature] = []

    for line in epic_section.splitlines():
        if not line.startswith("| EPIC-"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3:
            raise RuntimeError(f"cannot parse Epic row in {source}: {line}")
        left, outcome, forecast = cells
        match = re.match(r"(EPIC-\d{3})\s+(.+)", left)
        if not match:
            raise RuntimeError(f"cannot parse Epic row in {source}: {line}")
        epics.append(Epic(match.group(1), match.group(2), outcome, forecast, source))

    for line in feature_section.splitlines():
        if not line.startswith("| F-"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            raise RuntimeError(f"cannot parse Feature row in {source}: {line}")
        left, wp, work_cycle, child_cell = cells
        match = re.match(r"(F-\d{3}-\d{2})\s+(.+)", left)
        if not match:
            raise RuntimeError(f"cannot parse Feature row in {source}: {line}")
        children: list[tuple[str, str]] = []
        for raw_child in child_cell.split(";"):
            child = re.match(r"((?:US|EN)-\d{3})\s+(.+)", raw_child.strip())
            if not child:
                raise RuntimeError(f"cannot parse child item {raw_child!r} in {source}")
            children.append((child.group(1), child.group(2)))
        features.append(Feature(match.group(1), match.group(2), wp, work_cycle, tuple(children), source))

    user_stories = {ident for f in features for ident, _ in f.children if ident.startswith("US-")}
    enablers = {ident for f in features for ident, _ in f.children if ident.startswith("EN-")}
    all_ids = [ident for f in features for ident, _ in f.children]
    if len(epics) != expected_epics or len(features) != expected_features:
        raise RuntimeError(
            f"unexpected backlog inventory in {source}: {len(epics)} epics / {len(features)} features"
        )
    if len(user_stories) != expected_stories or len(enablers) != expected_enablers:
        raise RuntimeError(
            f"unexpected story/enabler inventory in {source}: "
            f"{len(user_stories)} user stories / {len(enablers)} enablers"
        )
    if len(set(all_ids)) != len(all_ids):
        raise RuntimeError(f"duplicate story/enabler identifiers found in {source}")
    return epics, features


def load_plan() -> tuple[list[Initiative], list[Epic], list[Feature], dict[str, Initiative]]:
    initiatives = parse_initiatives()
    mvp_epics, mvp_features = parse_backlog(
        MVP_BACKLOG, expected_epics=14, expected_features=34,
        expected_stories=105, expected_enablers=3,
    )
    exp_epics, exp_features = parse_backlog(
        EXPANDED_BACKLOG, expected_epics=10, expected_features=40,
        expected_stories=132, expected_enablers=0,
    )
    epics = [*mvp_epics, *exp_epics]
    features = [*mvp_features, *exp_features]
    if [e.ident for e in epics] != [f"EPIC-{n:03d}" for n in range(1, 25)]:
        raise RuntimeError("combined Epic IDs are not EPIC-001 through EPIC-024")
    if len(features) != 74 or len({f.ident for f in features}) != 74:
        raise RuntimeError("combined Feature inventory must contain 74 unique Features")
    child_ids = [ident for feature in features for ident, _ in feature.children]
    if len(child_ids) != 240 or len(set(child_ids)) != 240:
        raise RuntimeError("combined Story/Enabler inventory must contain 240 unique items")
    expected_stories = {f"US-{n:03d}" for n in range(1, 238)}
    actual_stories = {ident for ident in child_ids if ident.startswith("US-")}
    if actual_stories != expected_stories:
        raise RuntimeError("combined user-story inventory must cover US-001 through US-237")
    initiative_by_epic = {epic: initiative for initiative in initiatives for epic in initiative.epics}
    if set(initiative_by_epic) != {e.ident for e in epics}:
        raise RuntimeError("Initiative-to-Epic mapping does not cover the combined roadmap")
    return initiatives, epics, features, initiative_by_epic


def release_label(product_goal: str) -> str:
    return "release:mvp-1" if product_goal == "PG-001" else "release:release-2"


def target_release(product_goal: str) -> str:
    return "MVP Release 1" if product_goal == "PG-001" else "Monad Release 2"


def program_increment(work_cycle: str) -> str:
    match = re.search(r"WC-(MVP|EXP)-(\d{4})", work_cycle)
    if not match:
        return ""
    namespace, raw = match.groups()
    number = int(raw)
    if namespace == "MVP":
        if number == 0:
            return ""
        if number <= 4:
            return "PI-MVP-001"
        if number <= 8:
            return "PI-MVP-002"
        return "PI-MVP-003"
    if number <= 5:
        return "PI-EXP-001"
    if number <= 9:
        return "PI-EXP-002"
    return "PI-EXP-003"


def milestone_key(forecast: str) -> str:
    matches = re.findall(r"WC-(MVP|EXP)-(\d{4})", forecast)
    if not matches:
        raise RuntimeError(f"missing Work Cycle in {forecast!r}")
    namespaces = {namespace for namespace, _ in matches}
    if len(namespaces) != 1:
        raise RuntimeError(f"mixed Work Cycle namespaces in {forecast!r}")
    namespace = matches[0][0]
    number = max(int(raw) for _, raw in matches)
    if namespace == "MVP":
        if number == 0:
            return "M-000"
        if number <= 4:
            return "M-MVP-001"
        if number <= 8:
            return "M-MVP-002"
        return "M-MVP-003"
    if number <= 5:
        return "M-004"
    if number <= 9:
        return "M-005"
    return "M-006"


def goal_milestone(product_goal: str) -> str:
    return {
        "PG-001": "M-MVP-003",
        "PG-002": "M-004",
        "PG-003": "M-005",
        "PG-004": "M-006",
    }[product_goal]


def state_labels(product_goal: str, epic_id: str, feature_id: str | None = None) -> list[str]:
    if epic_id == "EPIC-001" or feature_id == "F-001-01":
        return ["status:active", "priority:p0"]
    if product_goal == "PG-001":
        return ["status:backlog", "priority:p1"]
    return ["status:backlog", "priority:p2"]


def ensure_labels() -> None:
    existing = {row["name"] for row in paged(f"/repos/{OWNER}/{REPO}/labels")}
    for name, (color, description) in LABELS.items():
        if name not in existing:
            api("POST", f"/repos/{OWNER}/{REPO}/labels", {
                "name": name, "color": color, "description": description,
            })
            print(f"created label: {name}")
            time.sleep(0.05)


def ensure_milestones() -> dict[str, int]:
    existing = {row["title"]: row for row in paged(f"/repos/{OWNER}/{REPO}/milestones?state=all")}
    result: dict[str, int] = {}
    for key, title, description, due_on in MILESTONES:
        row = existing.get(title)
        if row is None:
            row = api("POST", f"/repos/{OWNER}/{REPO}/milestones", {
                "title": title, "description": description, "due_on": due_on, "state": "open",
            })
            print(f"created milestone: {title}")
            time.sleep(0.05)
        result[key] = int(row["number"])
    return result


def existing_issues() -> dict[str, dict[str, Any]]:
    rows = paged(f"/repos/{OWNER}/{REPO}/issues?state=all")
    return {row["title"]: row for row in rows if "pull_request" not in row}


def upsert(
    existing: dict[str, dict[str, Any]],
    title: str,
    body: str,
    labels: list[str],
    milestone: int | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": title, "body": body, "labels": labels, "milestone": milestone,
    }
    row = existing.get(title)
    if row is None:
        row = api("POST", f"/repos/{OWNER}/{REPO}/issues", payload)
        existing[title] = row
        print(f"created #{row['number']}: {title}")
        time.sleep(0.08)
        return row
    current_labels = sorted(label["name"] for label in row.get("labels", []))
    current_milestone = (row.get("milestone") or {}).get("number")
    if row.get("body") != body or current_labels != sorted(labels) or current_milestone != milestone:
        row = api("PATCH", f"/repos/{OWNER}/{REPO}/issues/{row['number']}", payload)
        existing[title] = row
        print(f"updated #{row['number']}: {title}")
        time.sleep(0.04)
    return row


def project(
    initiatives: list[Initiative],
    epics: list[Epic],
    features: list[Feature],
    initiative_by_epic: dict[str, Initiative],
    milestones: dict[str, int],
):
    existing = existing_issues()
    initiative_rows: dict[str, dict[str, Any]] = {}
    epic_rows: dict[str, dict[str, Any]] = {}
    feature_rows: dict[str, dict[str, Any]] = {}
    child_rows: dict[str, dict[str, Any]] = {}
    epic_by_id = {e.ident: e for e in epics}

    for initiative in initiatives:
        title = f"[Initiative] {initiative.ident} — {initiative.title}"
        child_epics = ", ".join(f"`{epic}`" for epic in initiative.epics)
        body = f"""<!-- monad-tracking kind=initiative id={initiative.ident} source=product/initiatives.md -->
# Outcome

{initiative.outcome}

## Product context

- Product Goal: `{initiative.product_goal}`
- Canonical source: `product/initiatives.md`
- Child Epics: {child_epics}

## Exit condition

{initiative.exit_condition}

## Authority

This Issue is a coordination projection. Canonical artifacts in Git and governed EOS state remain authoritative.
"""
        initiative_rows[initiative.ident] = upsert(
            existing,
            title,
            body,
            ["type:initiative", release_label(initiative.product_goal)],
            milestones[goal_milestone(initiative.product_goal)],
        )

    for epic in epics:
        initiative = initiative_by_epic[epic.ident]
        product_goal = initiative.product_goal
        title = f"[Epic] {epic.ident} — {epic.title}"
        labels = [
            "type:epic", release_label(product_goal),
            AREA_BY_EPIC[epic.ident.split('-')[1]],
            *state_labels(product_goal, epic.ident),
        ]
        body = f"""<!-- monad-tracking kind=epic id={epic.ident} parent={initiative.ident} source={epic.source} -->
# Outcome

{epic.outcome}

## Forecast

- Initiative: `{initiative.ident}`
- Work Cycle: `{epic.forecast}`
- Product Goal: `{product_goal}`
- Target release: {target_release(product_goal)}
- Canonical source: `{epic.source}`

## Authority

This Issue is a coordination projection. Canonical artifacts in Git remain authoritative.
"""
        epic_rows[epic.ident] = upsert(
            existing, title, body, labels, milestones[milestone_key(epic.forecast)]
        )

    for feature in features:
        epic = epic_by_id[feature.epic_id]
        initiative = initiative_by_epic[feature.epic_id]
        product_goal = initiative.product_goal
        area = AREA_BY_EPIC[feature.epic_id.split('-')[1]]
        title = f"[Feature] {feature.ident} / {feature.work_packet} — {feature.title}"
        labels = [
            "type:feature", "type:work-packet", release_label(product_goal), area,
            *state_labels(product_goal, feature.epic_id, feature.ident),
        ]
        child_lines = "\n".join(f"- `{ident}` — {name}" for ident, name in feature.children)
        increment = program_increment(feature.work_cycle)
        increment_line = f"- Program Increment: `{increment}`\n" if increment else ""
        if feature.work_packet.startswith("WP-EXP-"):
            packet_line = (
                f"- Work Packet: `{feature.work_packet}` (forecast identity; detailed packet is created during rolling-wave refinement)\n"
            )
        else:
            packet_line = (
                f"- Work Packet: `{feature.work_packet}`\n"
                f"- Canonical Work Packet: `engineering/work-packets/{feature.work_packet}.md`\n"
            )
        body = f"""<!-- monad-tracking kind=feature id={feature.ident} wp={feature.work_packet} parent={feature.epic_id} source={feature.source} -->
# Outcome

{feature.title}

## Engineering authority

- Parent Epic: `{feature.epic_id}`
- Initiative: `{initiative.ident}`
{packet_line}{increment_line}- Forecast Work Cycle: `{feature.work_cycle}`
- Product Goal: `{product_goal}`
- Canonical backlog: `{feature.source}`

## Planned stories / enablers

{child_lines}

## Readiness

This Feature remains **Backlog** unless its canonical Work Packet or governed lifecycle state explicitly says otherwise. Forecast scheduling and Initiative assignment do not authorize implementation.
"""
        feature_rows[feature.ident] = upsert(
            existing, title, body, labels, milestones[milestone_key(feature.work_cycle)]
        )

        for ident, name in feature.children:
            is_enabler = ident.startswith("EN-")
            kind = "Enabler" if is_enabler else "Story"
            child_title = f"[{kind}] {ident} — {name[0].upper() + name[1:]}"
            child_labels = [
                "type:enabler" if is_enabler else "type:story",
                release_label(product_goal), area,
                *state_labels(product_goal, feature.epic_id, feature.ident),
            ]
            child_body = f"""<!-- monad-tracking kind=child id={ident} parent={feature.ident} wp={feature.work_packet} source={feature.source} -->
# Planned outcome

{name}

## Planning context

- Parent Feature: `{feature.ident}`
- Parent Epic: `{feature.epic_id}`
- Initiative: `{initiative.ident}`
- Work Packet: `{feature.work_packet}`
{increment_line}- Forecast Work Cycle: `{feature.work_cycle}`
- Product Goal: `{product_goal}`

## Readiness rule

Before this item enters Ready, observable acceptance, negative/boundary behavior, governing ADR/specification where applicable, verification method, and Work Packet ownership must be explicit in canonical engineering artifacts. Formal implementation Tasks are refined inside the Work Packet near the Ready horizon; they are not pre-generated across the roadmap.
"""
            child_rows[ident] = upsert(
                existing, child_title, child_body, child_labels,
                milestones[milestone_key(feature.work_cycle)],
            )
    return initiative_rows, epic_rows, feature_rows, child_rows


_child_cache: dict[int, set[int]] = {}


def children_of(parent_number: int) -> set[int]:
    if parent_number not in _child_cache:
        _child_cache[parent_number] = {
            int(row["id"])
            for row in paged(f"/repos/{OWNER}/{REPO}/issues/{parent_number}/sub_issues")
        }
    return _child_cache[parent_number]


def ensure_child(parent: dict[str, Any], child: dict[str, Any]) -> None:
    parent_number = int(parent["number"])
    existing = children_of(parent_number)
    child_id = int(child["id"])
    if child_id not in existing:
        api("POST", f"/repos/{OWNER}/{REPO}/issues/{parent_number}/sub_issues", {
            "sub_issue_id": child_id,
        })
        existing.add(child_id)
        print(f"linked #{child['number']} under #{parent['number']}")
        time.sleep(0.04)


def validate_plan() -> tuple[list[Initiative], list[Epic], list[Feature], dict[str, Initiative]]:
    plan = load_plan()
    initiatives, epics, features, _ = plan
    child_count = sum(len(feature.children) for feature in features)
    print(
        "GitHub tracking plan valid: "
        f"{len(initiatives)} initiatives, {len(epics)} epics, {len(features)} features/work packets, "
        f"{child_count} stories/enablers; Tasks remain rolling-wave."
    )
    return plan


def main() -> int:
    plan = validate_plan()
    if "--validate" in sys.argv[1:]:
        return 0
    initiatives, epics, features, initiative_by_epic = plan
    ensure_labels()
    milestones = ensure_milestones()
    initiative_rows, epic_rows, feature_rows, child_rows = project(
        initiatives, epics, features, initiative_by_epic, milestones
    )
    for initiative in initiatives:
        for epic_id in initiative.epics:
            ensure_child(initiative_rows[initiative.ident], epic_rows[epic_id])
    for feature in features:
        ensure_child(epic_rows[feature.epic_id], feature_rows[feature.ident])
        for ident, _ in feature.children:
            ensure_child(feature_rows[feature.ident], child_rows[ident])
    print(
        "GitHub tracking synchronized: "
        f"{len(initiative_rows)} initiatives, {len(epic_rows)} epics, "
        f"{len(feature_rows)} features/work packets, {len(child_rows)} stories/enablers. "
        "No speculative Tasks were created."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
