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


def issue(
    *,
    title: str,
    state: str = "OPEN",
    labels: tuple[str, ...] = (),
    body: str = "",
    url: str = "https://github.com/monad-framework/monad/issues/1",
) -> dict[str, object]:
    return {
        "title": title,
        "body": body,
        "url": url,
        "state": state,
        "labels": [{"name": label} for label in labels],
    }


def main() -> int:
    try:
        sync = load_module("monad_github_project_sync_review", SYNC_PATH)
        configure = load_module("monad_github_project_configure_review", CONFIGURE_PATH)

        work_packets = {
            "WP-MVP-0005": {
                "status": "IN_PROGRESS",
                "pi": "PI-MVP-001",
                "wc": "WC-MVP-0002",
                "domain": "CORE",
            }
        }

        # 1. Registered Work Packet EOS state remains authoritative even when
        # GitHub's issue state/labels disagree.
        registered_closed_issue = issue(
            title="[Feature] F-003-03 / WP-MVP-0005 — parser",
            state="CLOSED",
            labels=("status:backlog",),
            body="\n".join(
                (
                    "- Parent Epic: `EPIC-003`",
                    "- Initiative: `INIT-002`",
                    "- Product Goal: `PG-001`",
                    "- Work Packet: `WP-MVP-0005`",
                )
            ),
        )
        registered = sync.derive(registered_closed_issue, work_packets)
        require(
            registered["Lifecycle"] == "Running",
            "registered WP lifecycle must override GitHub CLOSED/labels",
        )
        require(registered["Increment"] == "PI-MVP-001", "canonical PI not projected")
        require(registered["Work Cycle"] == "WC-MVP-0002", "canonical Work Cycle not projected")
        require(registered["Domain"] == "CORE", "canonical domain not projected")

        # 2. Without registered WP authority, GitHub CLOSED outranks stale
        # lifecycle labels/prose.
        closed_unregistered = issue(
            title="[Defect] closed but stale label",
            state="CLOSED",
            labels=("status:active", "status:backlog"),
            body="This item remains **Backlog**.",
            url="https://github.com/monad-framework/monad/issues/2",
        )
        require(
            sync.derive(closed_unregistered, {})["Lifecycle"] == "Closed",
            "closed unregistered issue must project Closed before label fallback",
        )

        # 3. Open/unregistered issues retain normal fallback semantics.
        active_unregistered = issue(
            title="[Defect] active fallback",
            labels=("status:active",),
            url="https://github.com/monad-framework/monad/issues/3",
        )
        require(
            sync.derive(active_unregistered, {})["Lifecycle"] == "Running",
            "open unregistered issue should use lifecycle-label fallback",
        )

        # 4-6. Coverage is exact repository-Issue URL membership, not counts.
        repo_urls = {
            "https://github.com/monad-framework/monad/issues/1",
            "https://github.com/monad-framework/monad/issues/2",
        }
        covered_plus_extra = {
            *repo_urls,
            "https://github.com/monad-framework/monad/pull/999",
            "draft:123",
        }
        require(
            configure.missing_issue_urls(repo_urls, covered_plus_extra) == [],
            "extra non-Issue Project items must not affect complete coverage",
        )
        missing_with_extras = {
            "https://github.com/monad-framework/monad/issues/1",
            "https://github.com/monad-framework/monad/pull/999",
            "draft:123",
        }
        require(
            configure.missing_issue_urls(repo_urls, missing_with_extras)
            == ["https://github.com/monad-framework/monad/issues/2"],
            "extra Project items must not mask a missing repository Issue",
        )

        original_graphql = configure.graphql
        try:
            def fake_graphql(_query: str, _variables: dict[str, object]):
                return {
                    "organization": {
                        "projectV2": {
                            "items": {
                                "nodes": [
                                    {
                                        "content": {
                                            "url": "https://github.com/monad-framework/monad/issues/1",
                                            "repository": {"nameWithOwner": "monad-framework/monad"},
                                        }
                                    },
                                    # Pull requests/drafts do not populate the Issue fragment.
                                    {"content": {}},
                                    {
                                        "content": {
                                            "url": "https://github.com/other/repo/issues/7",
                                            "repository": {"nameWithOwner": "other/repo"},
                                        }
                                    },
                                ],
                                "pageInfo": {"hasNextPage": False, "endCursor": None},
                            }
                        }
                    }
                }

            configure.graphql = fake_graphql
            require(
                configure.project_issue_urls("monad-framework", 1, "monad-framework/monad")
                == {"https://github.com/monad-framework/monad/issues/1"},
                "coverage collector must ignore PR/draft/other-repository Project items",
            )
        finally:
            configure.graphql = original_graphql

        # 7. Full projection keeps an Issue that lost its recognized [Type] so
        # every projection-managed field can converge to null/empty.
        untyped = issue(
            title="Former Feature whose prefix was removed",
            labels=("status:active", "priority:p1"),
            body="- Work Packet: `WP-MVP-0005`",
            url="https://github.com/monad-framework/monad/issues/4",
        )
        rows = sync.projection_rows([untyped], work_packets, "full")
        require(len(rows) == 1, "full projection must retain untyped repository Issues")
        require(
            all(rows[0][field] == "" for field in sync.MANAGED_FIELDS),
            "untyped Issue must clear every projection-managed field",
        )

        # Core projection remains intentionally hierarchy-first and does not
        # mutate an untyped Issue during the lightweight pass.
        require(
            sync.projection_rows([untyped], work_packets, "core") == [],
            "core projection should remain hierarchy-first",
        )

        # 8. Only explicitly managed projection fields are candidates for
        # clearing/writing. User-owned/unmanaged fields remain outside the patch
        # contract.
        for unmanaged in ("Risk", "Executor", "Story Points", "Status", "Assignees"):
            require(
                unmanaged not in sync.MANAGED_FIELDS,
                f"unmanaged Project field unexpectedly entered projection contract: {unmanaged}",
            )

        # 9. Projection derivation is deterministic/idempotent: the same input
        # converges to the same managed state on repeated runs.
        inputs = [registered_closed_issue, closed_unregistered, active_unregistered, untyped]
        first = sync.projection_rows(inputs, work_packets, "full")
        second = sync.projection_rows(inputs, work_packets, "full")
        require(first == second, "repeated full projection must be deterministic/idempotent")

        print("GitHub Project review-regression checks: PASS")
        return 0
    except (OSError, ImportError, AttributeError, TestFailure) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
