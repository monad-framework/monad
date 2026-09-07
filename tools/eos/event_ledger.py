#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Iterable


class EventLedgerError(RuntimeError):
    """Event ledger is structurally or historically invalid."""


class EventLedgerConflict(EventLedgerError):
    """Divergent histories require explicit governed reconciliation."""


LIFECYCLE_EVENT_TYPES = {
    "ENTITY_CREATED",
    "ENTITY_IMPORTED",
    "STATE_TRANSITION",
}
EVENT_LEDGER_RELPATH = ".eos/events.jsonl"


def canonical_event(event: dict) -> str:
    return json.dumps(
        event,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _events_from_text(text: str, *, label: str) -> list[dict]:
    events: list[dict] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise EventLedgerError(f"{label}: malformed JSON at line {lineno}: {exc}") from exc
        if not isinstance(event, dict):
            raise EventLedgerError(f"{label}: line {lineno} must contain a JSON object")
        events.append(event)
    validate_event_identity(events)
    return events


def read_event_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return _events_from_text(path.read_text(encoding="utf-8"), label=str(path))


def event_map(events: Iterable[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            raise EventLedgerError(f"event {index} must be a JSON object")
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id.strip():
            raise EventLedgerError(f"event {index} has no valid event_id")
        previous = result.get(event_id)
        if previous is None:
            result[event_id] = event
            continue
        if canonical_event(previous) != canonical_event(event):
            raise EventLedgerError(f"conflicting immutable payloads for event_id {event_id}")
    return result


def validate_event_identity(events: Iterable[dict]) -> dict[str, dict]:
    return event_map(events)


def validate_parent_superset(
    result_events: Iterable[dict],
    parent_ledgers: Iterable[Iterable[dict]],
) -> None:
    result = event_map(result_events)
    for parent_number, parent_events in enumerate(parent_ledgers, start=1):
        parent = event_map(parent_events)
        for event_id in sorted(parent):
            inherited = parent[event_id]
            surviving = result.get(event_id)
            if surviving is None:
                raise EventLedgerError(
                    f"result ledger is missing inherited event {event_id} from parent {parent_number}"
                )
            if canonical_event(inherited) != canonical_event(surviving):
                raise EventLedgerError(
                    f"result ledger mutated inherited event {event_id} from parent {parent_number}"
                )


def _introduced_events(base: dict[str, dict], branch: dict[str, dict]) -> dict[str, dict]:
    introduced: dict[str, dict] = {}
    for event_id, event in branch.items():
        base_event = base.get(event_id)
        if base_event is None:
            introduced[event_id] = event
            continue
        if canonical_event(base_event) != canonical_event(event):
            raise EventLedgerError(f"branch mutated immutable base event {event_id}")
    return introduced


def _lifecycle_key(event: dict) -> tuple[str, str] | None:
    if event.get("event_type") not in LIFECYCLE_EVENT_TYPES:
        return None
    entity_kind = str(event.get("entity_kind", "")).strip()
    target = str(event.get("target", "")).strip()
    if not entity_kind or not target:
        return None
    return entity_kind, target


def validate_divergent_history(
    base_events: Iterable[dict],
    left_events: Iterable[dict],
    right_events: Iterable[dict],
) -> None:
    base = event_map(base_events)
    left = event_map(left_events)
    right = event_map(right_events)
    left_added = _introduced_events(base, left)
    right_added = _introduced_events(base, right)

    shared_ids = set(left_added) & set(right_added)
    for event_id in sorted(shared_ids):
        if canonical_event(left_added[event_id]) != canonical_event(right_added[event_id]):
            raise EventLedgerError(
                f"divergent histories contain conflicting payloads for event_id {event_id}"
            )
        left_added.pop(event_id)
        right_added.pop(event_id)

    left_by_entity: dict[tuple[str, str], list[str]] = defaultdict(list)
    right_by_entity: dict[tuple[str, str], list[str]] = defaultdict(list)
    for event_id, event in left_added.items():
        key = _lifecycle_key(event)
        if key is not None:
            left_by_entity[key].append(event_id)
    for event_id, event in right_added.items():
        key = _lifecycle_key(event)
        if key is not None:
            right_by_entity[key].append(event_id)

    conflicts = sorted(set(left_by_entity) & set(right_by_entity))
    if not conflicts:
        return

    details: list[str] = []
    for entity_kind, target in conflicts:
        left_ids = ",".join(sorted(left_by_entity[(entity_kind, target)]))
        right_ids = ",".join(sorted(right_by_entity[(entity_kind, target)]))
        details.append(f"{entity_kind}/{target}: left=[{left_ids}] right=[{right_ids}]")
    raise EventLedgerConflict(
        "divergent lifecycle histories require explicit reconciliation: " + "; ".join(details)
    )


def _git(
    root: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=check,
    )


def is_git_repository(root: Path) -> bool:
    proc = _git(root, "rev-parse", "--is-inside-work-tree", check=False)
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def git_commit_exists(root: Path, ref: str) -> bool:
    proc = _git(
        root,
        "rev-parse",
        "--verify",
        "--quiet",
        f"{ref}^{{commit}}",
        check=False,
    )
    return proc.returncode == 0


def ledger_from_git(root: Path, ref: str) -> list[dict]:
    if not git_commit_exists(root, ref):
        raise EventLedgerError(f"Git commit/ref does not exist: {ref}")
    object_ref = f"{ref}:{EVENT_LEDGER_RELPATH}"
    exists = _git(root, "cat-file", "-e", object_ref, check=False)
    if exists.returncode != 0:
        # A history that predates introduction of the EOS ledger contributes no events.
        return []
    proc = _git(root, "show", object_ref, check=False)
    if proc.returncode != 0:
        raise EventLedgerError(
            f"Unable to read inherited event ledger {object_ref}: {proc.stderr.strip()}"
        )
    return _events_from_text(proc.stdout, label=object_ref)


def immediate_parents(root: Path, ref: str = "HEAD") -> list[str]:
    proc = _git(root, "rev-list", "--parents", "-n", "1", ref)
    parts = proc.stdout.strip().split()
    if not parts:
        raise EventLedgerError(f"Cannot resolve Git parents for {ref}")
    return parts[1:]


def merge_head_refs(root: Path) -> list[str]:
    proc = _git(root, "rev-parse", "--absolute-git-dir", check=False)
    if proc.returncode != 0:
        return []
    merge_head = Path(proc.stdout.strip()) / "MERGE_HEAD"
    if not merge_head.exists():
        return []
    refs = [line.strip() for line in merge_head.read_text(encoding="utf-8").splitlines() if line.strip()]
    for ref in refs:
        if not git_commit_exists(root, ref):
            raise EventLedgerError(f"MERGE_HEAD contains invalid commit {ref}")
    return refs


def merge_base(root: Path, left: str, right: str) -> str:
    proc = _git(root, "merge-base", "--all", left, right, check=False)
    bases = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if proc.returncode != 0 or len(bases) != 1:
        raise EventLedgerError(
            f"Expected one merge base for {left} and {right}; found {len(bases)}"
        )
    return bases[0]


def validate_committed_history(root: Path, ref: str = "HEAD") -> None:
    result = ledger_from_git(root, ref)
    parents = immediate_parents(root, ref)
    parent_ledgers = [ledger_from_git(root, parent) for parent in parents]
    validate_parent_superset(result, parent_ledgers)

    if len(parents) <= 1:
        return
    if len(parents) != 2:
        raise EventLedgerConflict(
            "octopus merge history requires explicit EOS event-history reconciliation"
        )

    base = ledger_from_git(root, merge_base(root, parents[0], parents[1]))
    validate_divergent_history(base, parent_ledgers[0], parent_ledgers[1])


def validate_working_merge(root: Path) -> None:
    other_heads = merge_head_refs(root)
    if not other_heads:
        return
    if len(other_heads) != 1:
        raise EventLedgerConflict(
            "octopus merges require explicit EOS event-history reconciliation"
        )

    current = read_event_ledger(root / EVENT_LEDGER_RELPATH)
    head_events = ledger_from_git(root, "HEAD")
    other_ref = other_heads[0]
    other_events = ledger_from_git(root, other_ref)
    validate_parent_superset(current, [head_events, other_events])

    base = ledger_from_git(root, merge_base(root, "HEAD", other_ref))
    validate_divergent_history(base, head_events, other_events)


def validate_working_history(root: Path) -> None:
    if not is_git_repository(root):
        return
    current = read_event_ledger(root / EVENT_LEDGER_RELPATH)
    if git_commit_exists(root, "HEAD"):
        validate_parent_superset(current, [ledger_from_git(root, "HEAD")])
    validate_working_merge(root)
