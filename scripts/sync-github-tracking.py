#!/usr/bin/env python3
"""Project Monad MVP backlog into GitHub Issues, labels, milestones, and sub-issues.

Canonical Git artifacts remain authoritative. GitHub is a coordination projection.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "product" / "backlog" / "MVP-BACKLOG.md"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "monad-framework/monad")
API_ROOT = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
OWNER, REPO = REPOSITORY.split("/", 1)
API_VERSION = "2022-11-28"

LABELS: dict[str, tuple[str, str]] = {
    "type:epic": ("6f42c1", "MVP outcome spanning multiple features"),
    "type:feature": ("1d76db", "Feature-sized product or engineering outcome"),
    "type:work-packet": ("0e8a16", "Feature has a canonical Work Packet"),
    "type:story": ("2da44e", "User story within a feature"),
    "type:enabler": ("0e8a16", "Engineering enabler within a feature"),
    "status:backlog": ("d0d7de", "Planned but not yet Ready"),
    "status:ready": ("0e8a16", "Refined and ready for authorization"),
    "status:active": ("fbca04", "Currently active"),
    "status:review": ("5319e7", "Awaiting review or acceptance"),
    "status:blocked": ("b60205", "Blocked from progressing"),
    "status:done": ("8250df", "Accepted and complete"),
    "priority:p0": ("b60205", "Release- or program-blocking priority"),
    "priority:p1": ("d93f0b", "High priority on the MVP critical path"),
    "priority:p2": ("fbca04", "Normal planned MVP priority"),
    "priority:p3": ("d0d7de", "Lower priority or deferrable"),
    "release:mvp-1": ("5319e7", "Targeted to MVP Release 1"),
    "area:governance": ("c5def5", "Governance, authority, planning, and EOS"),
    "area:workspace": ("c5def5", "Repository identity, configuration, and discovery"),
    "area:ingestion": ("c5def5", "Canonical knowledge ingestion and parsing"),
    "area:graph": ("c5def5", "Semantic graph ontology, construction, and integrity"),
    "area:kir": ("c5def5", "Kernel Intermediate Representation"),
    "area:diagnostics": ("c5def5", "Diagnostics, validation, and conformance"),
    "area:query": ("c5def5", "Graph query and explanation"),
    "area:agent": ("c5def5", "AI agent context and governance"),
    "area:cli": ("c5def5", "CLI and developer experience"),
    "area:quality": ("c5def5", "Determinism, security, reliability, and performance"),
    "area:execution": ("c5def5", "Change intelligence and native validation"),
    "area:github": ("c5def5", "Dogfooding and GitHub projection"),
    "area:release": ("c5def5", "Packaging, documentation, acceptance, and release"),
}

AREA_BY_EPIC = {
    "001": "area:governance", "002": "area:workspace", "003": "area:ingestion",
    "004": "area:graph", "005": "area:kir", "006": "area:diagnostics",
    "007": "area:query", "008": "area:agent", "009": "area:cli",
    "010": "area:quality", "011": "area:execution", "012": "area:github",
    "013": "area:release", "014": "area:release",
}

MILESTONES = [
    ("M-000", "M-000 Foundation Stabilized", "Foundation stabilization gate: coherent authority, synchronized machine layer, and GitHub-operational MVP program.", "2026-08-16T23:59:59Z"),
    ("M-MVP-001", "M-MVP-001 Semantic Kernel Alpha", "PI-MVP-001 exit: identity, ingestion, semantic graph, KIR, diagnostics, and validation baseline.", "2026-09-13T23:59:59Z"),
    ("M-MVP-002", "M-MVP-002 MVP Beta", "PI-MVP-002 exit: query/explain, bounded agent context, CLI, and trust/performance baseline.", "2026-10-11T23:59:59Z"),
    ("M-MVP-003", "M-MVP-003 MVP Release 1", "PI-MVP-003 exit and MVP Release 1 acceptance gate.", "2026-11-08T23:59:59Z"),
]

@dataclass(frozen=True)
class Epic:
    ident: str
    title: str
    outcome: str
    forecast: str

@dataclass(frozen=True)
class Feature:
    ident: str
    title: str
    work_packet: str
    sprint: str
    children: tuple[tuple[str, str], ...]

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


def parse_backlog() -> tuple[list[Epic], list[Feature]]:
    text = BACKLOG.read_text(encoding="utf-8")
    epic_section = text.split("## Epic roadmap", 1)[1].split("## Feature / Work Packet map", 1)[0]
    feature_section = text.split("## Feature / Work Packet map", 1)[1].split("## Backlog ordering", 1)[0]
    epics: list[Epic] = []
    features: list[Feature] = []

    for line in epic_section.splitlines():
        if not line.startswith("| EPIC-"):
            continue
        left, outcome, forecast = [c.strip() for c in line.strip().strip("|").split("|")]
        match = re.match(r"(EPIC-\d{3})\s+(.+)", left)
        if not match:
            raise RuntimeError(f"cannot parse epic row: {line}")
        epics.append(Epic(match.group(1), match.group(2), outcome, forecast))

    for line in feature_section.splitlines():
        if not line.startswith("| F-"):
            continue
        left, wp, sprint, child_cell = [c.strip() for c in line.strip().strip("|").split("|")]
        match = re.match(r"(F-\d{3}-\d{2})\s+(.+)", left)
        if not match:
            raise RuntimeError(f"cannot parse feature row: {line}")
        children: list[tuple[str, str]] = []
        for raw in child_cell.split(";"):
            child = re.match(r"((?:US|EN)-\d{3})\s+(.+)", raw.strip())
            if not child:
                raise RuntimeError(f"cannot parse child item {raw!r}")
            children.append((child.group(1), child.group(2)))
        features.append(Feature(match.group(1), match.group(2), wp, sprint, tuple(children)))

    user_stories = {ident for f in features for ident, _ in f.children if ident.startswith("US-")}
    enablers = {ident for f in features for ident, _ in f.children if ident.startswith("EN-")}
    all_ids = [ident for f in features for ident, _ in f.children]
    if len(epics) != 14 or len(features) != 34:
        raise RuntimeError(f"unexpected backlog: {len(epics)} epics / {len(features)} features")
    if len(user_stories) != 105 or len(enablers) != 3 or len(all_ids) != 108:
        raise RuntimeError(
            "unexpected story/enabler inventory: "
            f"{len(user_stories)} unique user stories, {len(enablers)} unique enablers, {len(all_ids)} rows"
        )
    if len(set(all_ids)) != len(all_ids):
        raise RuntimeError("duplicate story/enabler identifiers found")
    return epics, features


def ensure_labels() -> None:
    existing = {row["name"] for row in paged(f"/repos/{OWNER}/{REPO}/labels")}
    for name, (color, description) in LABELS.items():
        if name not in existing:
            api("POST", f"/repos/{OWNER}/{REPO}/labels", {"name": name, "color": color, "description": description})
            print(f"created label: {name}")
            time.sleep(0.05)


def ensure_milestones() -> dict[str, int]:
    existing = {row["title"]: row for row in paged(f"/repos/{OWNER}/{REPO}/milestones?state=all")}
    result: dict[str, int] = {}
    for key, title, description, due_on in MILESTONES:
        row = existing.get(title)
        if row is None:
            row = api("POST", f"/repos/{OWNER}/{REPO}/milestones", {
                "title": title, "description": description, "due_on": due_on, "state": "open"
            })
            print(f"created milestone: {title}")
            time.sleep(0.05)
        result[key] = int(row["number"])
    return result


def milestone_key(forecast: str) -> str:
    cycles = [int(v) for v in re.findall(r"WC-MVP-(\d{4})", forecast)]
    if not cycles:
        raise RuntimeError(f"missing work cycle in {forecast!r}")
    last = max(cycles)
    if last == 0:
        return "M-000"
    if last <= 4:
        return "M-MVP-001"
    if last <= 8:
        return "M-MVP-002"
    return "M-MVP-003"


def state_labels(epic_id: str, feature_id: str | None = None) -> list[str]:
    return ["status:active", "priority:p0"] if epic_id == "EPIC-001" or feature_id == "F-001-01" else ["status:backlog", "priority:p1"]


def existing_issues() -> dict[str, dict[str, Any]]:
    rows = paged(f"/repos/{OWNER}/{REPO}/issues?state=all")
    return {row["title"]: row for row in rows if "pull_request" not in row}


def upsert(existing: dict[str, dict[str, Any]], title: str, body: str, labels: list[str], milestone: int) -> dict[str, Any]:
    payload = {"title": title, "body": body, "labels": labels, "milestone": milestone}
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


def project(epics: list[Epic], features: list[Feature], milestones: dict[str, int]):
    existing = existing_issues()
    epic_rows: dict[str, dict[str, Any]] = {}
    feature_rows: dict[str, dict[str, Any]] = {}
    child_rows: dict[str, dict[str, Any]] = {}
    epic_by_id = {e.ident: e for e in epics}

    for epic in epics:
        title = f"[Epic] {epic.ident} — {epic.title}"
        labels = ["type:epic", "release:mvp-1", AREA_BY_EPIC[epic.ident.split('-')[1]], *state_labels(epic.ident)]
        body = f"""<!-- monad-tracking kind=epic id={epic.ident} source=product/backlog/MVP-BACKLOG.md -->
# Outcome

{epic.outcome}

## Forecast

- Work cycle: `{epic.forecast}`
- Product Goal: `PG-001`
- Target release: MVP Release 1
- Canonical source: `product/backlog/MVP-BACKLOG.md`

## Authority

This Issue is a coordination projection. Canonical artifacts in Git remain authoritative.
"""
        epic_rows[epic.ident] = upsert(existing, title, body, labels, milestones[milestone_key(epic.forecast)])

    for feature in features:
        epic = epic_by_id[feature.epic_id]
        area = AREA_BY_EPIC[feature.epic_id.split('-')[1]]
        title = f"[Feature] {feature.ident} / {feature.work_packet} — {feature.title}"
        labels = ["type:feature", "type:work-packet", "release:mvp-1", area, *state_labels(feature.epic_id, feature.ident)]
        child_lines = "\n".join(f"- `{ident}` — {name}" for ident, name in feature.children)
        body = f"""<!-- monad-tracking kind=feature id={feature.ident} wp={feature.work_packet} parent={feature.epic_id} source=product/backlog/MVP-BACKLOG.md -->
# Outcome

{feature.title}

## Engineering authority

- Parent Epic: `{feature.epic_id}`
- Work Packet: `{feature.work_packet}`
- Canonical Work Packet: `engineering/work-packets/{feature.work_packet}.md`
- Forecast Sprint: `{feature.sprint}`
- Product Goal: `PG-001`

## Planned stories / enablers

{child_lines}

## Readiness

This Feature remains **Backlog** unless its labels and canonical Work Packet explicitly say otherwise. Scheduling does not authorize implementation.
"""
        feature_rows[feature.ident] = upsert(existing, title, body, labels, milestones[milestone_key(feature.sprint)])

        for ident, name in feature.children:
            is_enabler = ident.startswith("EN-")
            kind = "Enabler" if is_enabler else "Story"
            child_title = f"[{kind}] {ident} — {name[0].upper() + name[1:]}"
            child_labels = ["type:enabler" if is_enabler else "type:story", "release:mvp-1", area, *state_labels(feature.epic_id, feature.ident)]
            child_body = f"""<!-- monad-tracking kind=child id={ident} parent={feature.ident} wp={feature.work_packet} source=product/backlog/MVP-BACKLOG.md -->
# Planned outcome

{name}

## Planning context

- Parent Feature: `{feature.ident}`
- Parent Epic: `{feature.epic_id}`
- Work Packet: `{feature.work_packet}`
- Forecast Sprint: `{feature.sprint}`
- Product Goal: `PG-001`

## Readiness rule

Before this item enters Ready, observable acceptance, negative/boundary behavior, governing ADR/specification where applicable, verification method, and Work Packet ownership must be explicit in canonical engineering artifacts.
"""
            child_rows[ident] = upsert(existing, child_title, child_body, child_labels, milestones[milestone_key(feature.sprint)])
    return epic_rows, feature_rows, child_rows


def children_of(parent_number: int) -> set[int]:
    return {int(row["id"]) for row in paged(f"/repos/{OWNER}/{REPO}/issues/{parent_number}/sub_issues")}


def ensure_child(parent: dict[str, Any], child: dict[str, Any]) -> None:
    existing = children_of(int(parent["number"]))
    if int(child["id"]) not in existing:
        api("POST", f"/repos/{OWNER}/{REPO}/issues/{parent['number']}/sub_issues", {"sub_issue_id": int(child["id"])})
        print(f"linked #{child['number']} under #{parent['number']}")
        time.sleep(0.04)


def main() -> int:
    epics, features = parse_backlog()
    ensure_labels()
    milestones = ensure_milestones()
    epic_rows, feature_rows, child_rows = project(epics, features, milestones)
    for feature in features:
        ensure_child(epic_rows[feature.epic_id], feature_rows[feature.ident])
        for ident, _ in feature.children:
            ensure_child(feature_rows[feature.ident], child_rows[ident])
    print(
        "GitHub tracking synchronized: "
        f"{len(epic_rows)} epics, {len(feature_rows)} features/work packets, "
        "105 user stories, 3 engineering enablers (108 child backlog items)."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
