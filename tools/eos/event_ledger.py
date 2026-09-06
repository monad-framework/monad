#!/usr/bin/env python3
from __future__ import annotations

import json
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


def canonical_event(event: dict) -> str:
    return json.dumps(
        event,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def read_event_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []

    events: list[dict] = []

    for lineno, raw in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not raw.strip():
            continue

        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise EventLedgerError(
                f"{path}: malformed JSON at line {lineno}: {exc}"
            ) from exc

        if not isinstance(event, dict):
            raise EventLedgerError(
                f"{path}: line {lineno} must contain a JSON object"
            )

        events.append(event)

    validate_event_identity(events)

    return events


def event_map(events: Iterable[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}

    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            raise EventLedgerError(
                f"event {index} must be a JSON object"
            )

        event_id = event.get("event_id")

        if not isinstance(event_id, str) or not event_id.strip():
            raise EventLedgerError(
                f"event {index} has no valid event_id"
            )

        previous = result.get(event_id)

        if previous is None:
            result[event_id] = event
            continue

        if canonical_event(previous) != canonical_event(event):
            raise EventLedgerError(
                "conflicting immutable payloads for "
                f"event_id {event_id}"
            )

    return result


def validate_event_identity(
    events: Iterable[dict],
) -> dict[str, dict]:
    return event_map(events)


def validate_parent_superset(
    result_events: Iterable[dict],
    parent_ledgers: Iterable[Iterable[dict]],
) -> None:
    result = event_map(result_events)

    for parent_number, parent_events in enumerate(
        parent_ledgers,
        start=1,
    ):
        parent = event_map(parent_events)

        for event_id in sorted(parent):
            inherited = parent[event_id]
            surviving = result.get(event_id)

            if surviving is None:
                raise EventLedgerError(
                    "result ledger is missing inherited event "
                    f"{event_id} from parent {parent_number}"
                )

            if canonical_event(inherited) != canonical_event(surviving):
                raise EventLedgerError(
                    "result ledger mutated inherited event "
                    f"{event_id} from parent {parent_number}"
                )


def _introduced_events(
    base: dict[str, dict],
    branch: dict[str, dict],
) -> dict[str, dict]:
    introduced: dict[str, dict] = {}

    for event_id, event in branch.items():
        base_event = base.get(event_id)

        if base_event is None:
            introduced[event_id] = event
            continue

        if canonical_event(base_event) != canonical_event(event):
            raise EventLedgerError(
                "branch mutated immutable base event "
                f"{event_id}"
            )

    return introduced


def _lifecycle_key(
    event: dict,
) -> tuple[str, str] | None:
    if event.get("event_type") not in LIFECYCLE_EVENT_TYPES:
        return None

    entity_kind = str(
        event.get("entity_kind", "")
    ).strip()

    target = str(
        event.get("target", "")
    ).strip()

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
        if (
            canonical_event(left_added[event_id])
            != canonical_event(right_added[event_id])
        ):
            raise EventLedgerError(
                "divergent histories contain conflicting "
                f"payloads for event_id {event_id}"
            )

        left_added.pop(event_id)
        right_added.pop(event_id)

    left_by_entity: dict[
        tuple[str, str],
        list[str],
    ] = defaultdict(list)

    right_by_entity: dict[
        tuple[str, str],
        list[str],
    ] = defaultdict(list)

    for event_id, event in left_added.items():
        key = _lifecycle_key(event)

        if key is not None:
            left_by_entity[key].append(event_id)

    for event_id, event in right_added.items():
        key = _lifecycle_key(event)

        if key is not None:
            right_by_entity[key].append(event_id)

    conflicts = sorted(
        set(left_by_entity) & set(right_by_entity)
    )

    if not conflicts:
        return

    details: list[str] = []

    for entity_kind, target in conflicts:
        left_ids = ",".join(
            sorted(
                left_by_entity[
                    (entity_kind, target)
                ]
            )
        )

        right_ids = ",".join(
            sorted(
                right_by_entity[
                    (entity_kind, target)
                ]
            )
        )

        details.append(
            f"{entity_kind}/{target}: "
            f"left=[{left_ids}] "
            f"right=[{right_ids}]"
        )

    raise EventLedgerConflict(
        "divergent lifecycle histories require explicit "
        "reconciliation: "
        + "; ".join(details)
    )
