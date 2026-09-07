#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC_PATH = ROOT / "scripts" / "sync-github-project-metadata.py"
CONFIGURE_PATH = ROOT / "scripts" / "configure-github-project.py"


class TestFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TestFailure(message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise TestFailure(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    try:
        sync = load_module("monad_github_project_sync", SYNC_PATH)
        configure = load_module("monad_github_project_configure", CONFIGURE_PATH)

        work_packets = {
            "WP-MVP-0005": {
                "status": "IN_PROGRESS",
                "pi": "PI-MVP-001",
                "wc": "WC-MVP-0002",
                "domain": "CORE",
            }
        }
        feature = {
            "title": "[Feature] F-003-03 / WP-MVP-0005 — Structured configuration parser",
            "body": "\n".join(
                (
                    "- Parent Epic: `EPIC-003`",
                    "- Initiative: `INIT-002`",
                    "- Work Packet: `WP-MVP-0005`",
                    "- Program Increment: `PI-MVP-001`",
                    "- Forecast Work Cycle: `WC-MVP-0002`",
                    "- Product Goal: `PG-001`",
                    "This Feature remains **Backlog** unless its canonical Work Packet says otherwise.",
                )
            ),
            "url": "https://github.com/monad-framework/monad/issues/38",
            "state": "OPEN",
            "labels": [
                {"name": "status:backlog"},
                {"name": "priority:p1"},
                {"name": "area:ingestion"},
                {"name": "release:mvp-1"},
            ],
        }
        projected = sync.derive(feature, work_packets)
        require(
            projected["Lifecycle"] == "Running",
            "canonical WP state must override stale Backlog issue metadata",
        )
        require(
            projected["Increment"] == "PI-MVP-001",
            "canonical WP PI was not projected",
        )
        require(
            projected["Work Cycle"] == "WC-MVP-0002",
            "canonical WP Work Cycle was not projected",
        )
        require(
            projected["Domain"] == "CORE",
            "canonical WP domain was not projected",
        )
        require(projected["Priority"] == "P1", "priority label projection failed")
        require(
            projected["Product Area"] == "ingestion",
            "area label projection failed",
        )
        require(
            projected["Target Release"] == "MVP Release 1",
            "release label projection failed",
        )

        task = {
            "title": "[Task] WP-MVP-0005 / US-015 — Implement bounded parser behavior",
            "body": "\n".join(
                (
                    "- Parent Feature: `F-003-03`",
                    "- Parent Epic: `EPIC-003`",
                    "- Initiative: `INIT-002`",
                    "- Product Goal: `PG-001`",
                    "- Work Packet: `WP-MVP-0005` — **IN_PROGRESS**",
                )
            ),
            "url": "https://github.com/monad-framework/monad/issues/475",
            "state": "OPEN",
            "labels": [],
        }
        task_projected = sync.derive(task, work_packets)
        require(task_projected["Item Type"] == "Task", "Task title projection failed")
        require(
            task_projected["Lifecycle"] == "Running",
            "Task did not inherit canonical WP execution lifecycle",
        )
        require(
            task_projected["Feature"] == "F-003-03",
            "Task Feature relationship was not projected",
        )

        defect = {
            "title": "[Defect] Unrelated control-plane defect",
            "body": "",
            "url": "https://github.com/monad-framework/monad/issues/999",
            "state": "OPEN",
            "labels": [{"name": "status:blocked"}],
        }
        defect_projected = sync.derive(defect, work_packets)
        require(
            defect_projected["Lifecycle"] == "Blocked",
            "fallback lifecycle label projection failed",
        )
        require(
            defect_projected["Product Goal"] == "",
            "unrelated defect must not be forced into a Product Goal",
        )
        require(
            defect_projected["Initiative"] == "",
            "unrelated defect must not be forced into an Initiative",
        )

        names = [view["name"] for view in configure.REQUIRED_VIEWS]
        require(len(names) == 21, f"expected 21 required views, found {len(names)}")
        require(
            len(set(names)) == len(names),
            "required Project view names must be unique",
        )
        require(
            names[:6]
            == [
                "Program",
                "MVP Roadmap",
                "Current Work",
                "Next Up",
                "Defects",
                "Release 1",
            ],
            "daily Project view order changed",
        )
        require(
            "Task" in configure.ITEM_TYPE_OPTIONS,
            "Task must remain a required Item Type",
        )
        require(
            "Running" in configure.LIFECYCLE_OPTIONS,
            "Running must remain a required Lifecycle state",
        )

        print("GitHub Project metadata/configuration invariant checks: PASS")
        return 0
    except (OSError, ImportError, AttributeError, TestFailure) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
