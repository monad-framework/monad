#!/usr/bin/env python3
"""EOSV v2 compatibility facade with scope-sensitive evidence freshness.

The original EOSV implementation remains intact in ``verification_v2_impl.py``.
This facade narrows source freshness to the implementation files actually
observed for a Work Packet execution plus its governed inputs. It also keeps
legacy whole-repository fingerprints readable without allowing their known
scope-sensitivity defect to block terminal historical work.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_IMPL_PATH = Path(__file__).with_name("verification_v2_impl.py")
_SPEC = importlib.util.spec_from_file_location("eos_verification_v2_impl", _IMPL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot load {_IMPL_PATH}")
_impl = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _impl
_SPEC.loader.exec_module(_impl)

for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

_LEGACY_SOURCE_FINGERPRINT = _impl.source_fingerprint
FINGERPRINT_VERSION = "scope-v2"
FINGERPRINT_PREFIX = f"{FINGERPRINT_VERSION}:"
_SYNCED_GLOBALS = (
    "ROOT",
    "EOS",
    "CORE",
    "EVID_REG",
    "LINK_REG",
    "PERF_REG",
    "EVENTS",
)


def _sync_impl_globals() -> None:
    """Keep fixture-overridden module globals aligned with the implementation."""
    for name in _SYNCED_GLOBALS:
        if name in globals():
            setattr(_impl, name, globals()[name])


def _safe_relative_path(value: str) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    candidate = Path(raw)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    normalized = candidate.as_posix()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized or None


def _canonical_entity(target: str) -> dict | None:
    state = _impl.load_json(_impl.EOS / "state" / "current.json", {})
    entities = state.get("entities", {}) if isinstance(state, dict) else {}
    if not isinstance(entities, dict):
        return None
    for bucket in entities.values():
        if isinstance(bucket, dict) and isinstance(bucket.get(target), dict):
            return bucket[target]
    return None


def _is_terminal_target(target: str) -> bool:
    entity = _canonical_entity(target)
    if not entity:
        return False
    kind = str(entity.get("kind", "")).strip().lower()
    lifecycle = str(entity.get("lifecycle_state", "")).strip()
    if not kind or not lifecycle:
        return False
    machine = _impl.load_json(
        _impl.EOS / "state-machines" / f"{kind}.json",
        {},
    )
    terminal = machine.get("terminal_states", []) if isinstance(machine, dict) else []
    return lifecycle in terminal


def _execution_rows(work_packet: str, execution: str) -> list[dict[str, str]]:
    rows = _impl.read_tsv(_impl.EOS / "executions.tsv")
    if execution:
        rows = [row for row in rows if row.get("id") == execution]
    else:
        rows = [row for row in rows if row.get("target") == work_packet]
    return sorted(rows, key=lambda row: (row.get("created", ""), row.get("id", "")))


def _execution_payload(row: dict[str, str]) -> dict:
    path_text = _safe_relative_path(row.get("path", ""))
    if not path_text:
        return {}
    path = _impl.ROOT / path_text
    data = _impl.load_json(path, {}) if path.exists() else {}
    return data if isinstance(data, dict) else {}


def _execution_result(row: dict[str, str], payload: dict) -> dict:
    path_text = _safe_relative_path(row.get("result_path", ""))
    if not path_text:
        result = payload.get("result", {}) if isinstance(payload, dict) else {}
        if isinstance(result, dict):
            path_text = _safe_relative_path(str(result.get("path", "")))
    if not path_text:
        return {}
    path = _impl.ROOT / path_text
    data = _impl.load_json(path, {}) if path.exists() else {}
    return data if isinstance(data, dict) else {}


def _changed_files(row: dict[str, str], payload: dict) -> set[str]:
    result = _execution_result(row, payload)
    observed = result.get("eos_observation", {}) if isinstance(result, dict) else {}
    agent = result.get("agent_result", {}) if isinstance(result, dict) else {}

    candidates = []
    if isinstance(observed, dict):
        candidates = observed.get("actual_changed_files", []) or observed.get(
            "declared_changed_files",
            [],
        )
    if not candidates and isinstance(agent, dict):
        candidates = agent.get("changed_files", [])

    paths: set[str] = set()
    for value in candidates if isinstance(candidates, list) else []:
        normalized = _safe_relative_path(str(value))
        if normalized:
            paths.add(normalized)
    return paths


def _execution_governing_paths(payload: dict) -> set[str]:
    inputs = payload.get("governing_inputs", []) if isinstance(payload, dict) else []
    paths: set[str] = set()
    for item in inputs if isinstance(inputs, list) else []:
        if not isinstance(item, dict):
            continue
        normalized = _safe_relative_path(str(item.get("path", "")))
        if normalized:
            paths.add(normalized)
    return paths


def _hash_paths(root: Path, paths: set[str]) -> dict[str, str]:
    hashed: dict[str, str] = {}
    for relative in sorted(paths):
        candidate = root / relative
        if not _impl.is_source_path(candidate, root):
            continue
        if candidate.is_file():
            hashed[relative] = _impl.semantic_file_hash(candidate)
        elif candidate.exists():
            hashed[relative] = "<NON_FILE>"
        else:
            hashed[relative] = "<MISSING>"
    return hashed


def _governing_hashes(
    work_packet: str,
    target: str,
    execution: str,
    execution_payloads: list[dict],
) -> dict[str, str]:
    paths: list[Path] = []
    ids: list[str] = []
    wp_path = _impl.artifact_path(work_packet) if work_packet else _impl.artifact_path(target)
    if wp_path and wp_path.exists():
        paths.append(wp_path)
        ids.extend(_impl.references_from(wp_path))

    row = _impl.wp_row(work_packet) if work_packet else None
    if row:
        ids.extend([row.get("pi", ""), row.get("wc", "")])

    for ref in sorted(set(item for item in ids if item and item not in {target, execution, work_packet})):
        artifact = _impl.artifact_path(ref)
        if artifact and artifact.exists():
            paths.append(artifact)

    for payload in execution_payloads:
        for relative in _execution_governing_paths(payload):
            artifact = _impl.ROOT / relative
            if artifact.exists():
                paths.append(artifact)

    return {
        _impl.rel(path): _impl.semantic_file_hash(path)
        for path in sorted(set(paths), key=lambda item: _impl.rel(item))
    }


def source_fingerprint(target: str, execution: str = "") -> tuple[str, dict]:
    """Return a deterministic, scope-sensitive EOSV source fingerprint.

    When execution results expose observed changed files, freshness is bound to
    those implementation paths rather than the entire repository. Governing
    artifacts and immutable execution descriptors remain independently bound.
    Older/no-scope workflows fail closed to the original whole-source hash.
    """
    _sync_impl_globals()
    work_packet, exec_id, cwd, baseline = _impl.context_for_target(target, execution)
    rows = _execution_rows(work_packet, exec_id)
    payloads = [_execution_payload(row) for row in rows]

    scope_paths: set[str] = set()
    for row, payload in zip(rows, payloads):
        scope_paths.update(_changed_files(row, payload))

    source_root = _impl.ROOT if _is_terminal_target(work_packet) else cwd
    implementation = _hash_paths(source_root, scope_paths) if scope_paths else {}

    execution_descriptors = [
        {
            "id": row.get("id", ""),
            "baseline": row.get("baseline_commit", ""),
            "contract_hash": row.get("contract_hash", ""),
            "governing_hash": row.get("governing_hash", ""),
        }
        for row in rows
    ]

    payload = {
        "fingerprint_version": FINGERPRINT_VERSION,
        "target": target,
        "work_packet": work_packet,
        "execution": exec_id,
        "governing": _governing_hashes(
            work_packet,
            target,
            exec_id,
            payloads,
        ),
        "executions": execution_descriptors,
    }

    if exec_id:
        payload["baseline"] = baseline
        payload["workspace_hash"] = (
            _impl.canonical_hash(implementation)
            if implementation
            else _impl.workspace_hash(cwd, baseline)
        )
    else:
        payload["source_content_hash"] = (
            _impl.canonical_hash(implementation)
            if implementation
            else _impl.source_content_hash(cwd)
        )

    if implementation:
        payload["implementation_scope"] = implementation

    return FINGERPRINT_PREFIX + _impl.canonical_hash(payload), payload


def _legacy_terminal_fingerprint(source_hash: str, target: str) -> bool:
    return bool(source_hash) and not source_hash.startswith(FINGERPRINT_PREFIX) and _is_terminal_target(target)


def audit_evidence(*, mutate: bool = True) -> tuple[list[dict], list[str]]:
    """Audit evidence without re-staling legacy terminal records by broad scope."""
    _sync_impl_globals()
    report: list[dict] = []
    failures: list[str] = []

    for row in _impl.read_tsv(_impl.EVID_REG):
        evid = row.get("id", "")
        machine = _impl.EOS / "evidence" / f"{evid}.json"
        issues: list[str] = []
        if not machine.exists():
            issues.append("machine evidence missing")
        elif row.get("artifact_hash") != _impl.file_hash(machine):
            issues.append("machine evidence hash mismatch")

        if row.get("status") in {"VALIDATED", "STALE"}:
            source_hash = row.get("source_hash", "")
            if _legacy_terminal_fingerprint(source_hash, row.get("target", "")):
                issues.append("legacy unscoped fingerprint retained for terminal target")
            else:
                try:
                    if source_hash.startswith(FINGERPRINT_PREFIX):
                        current, _ = source_fingerprint(
                            row.get("target", ""),
                            row.get("execution", ""),
                        )
                    else:
                        current, _ = _LEGACY_SOURCE_FINGERPRINT(
                            row.get("target", ""),
                            row.get("execution", ""),
                        )
                except Exception as exc:
                    current = ""
                    issues.append(f"source fingerprint unavailable: {exc}")

                if current and current != source_hash:
                    issues.append("source fingerprint changed")
                    if mutate and row.get("status") == "VALIDATED":
                        _impl.transition_evidence(
                            evid,
                            "STALE",
                            "governing or implementation source fingerprint changed",
                        )

        report.append({"id": evid, "status": row.get("status"), "issues": issues})
        if "machine evidence hash mismatch" in issues:
            failures.append(f"{evid}: machine evidence hash mismatch")

    return report, failures


def verify_evidence(strict: bool) -> tuple[bool, str]:
    """Verify current evidence while preserving legacy terminal history."""
    _sync_impl_globals()
    rows = _impl.read_tsv(_impl.EVID_REG)
    ids: set[str] = set()
    failures: list[str] = []
    warnings: list[str] = []

    for row in rows:
        if row.get("id") in ids:
            failures.append(f"duplicate evidence id: {row.get('id')}")
        ids.add(row.get("id", ""))
        if row.get("status") not in {
            "CAPTURED",
            "VALIDATED",
            "FAILED",
            "STALE",
            "SUPERSEDED",
        }:
            failures.append(f"{row.get('id')}: invalid status {row.get('status')}")

    _, hard = audit_evidence(mutate=True)
    failures.extend(hard)

    latest: dict[tuple[str, str], dict[str, str]] = {}
    for row in _impl.read_tsv(_impl.EVID_REG):
        if row.get("status") == "SUPERSEDED":
            continue
        latest[(row.get("target", ""), row.get("validator", ""))] = row

    stale = [row for row in latest.values() if row.get("status") == "STALE"]
    legacy_terminal_stale = [
        row
        for row in stale
        if _legacy_terminal_fingerprint(
            row.get("source_hash", ""),
            row.get("target", ""),
        )
    ]
    current_stale = [row for row in stale if row not in legacy_terminal_stale]

    if current_stale:
        messages = [
            f"{row['id']} target={row['target']} validator={row['validator']}"
            for row in current_stale
        ]
        (failures if strict else warnings).extend(
            "stale current evidence: " + message for message in messages
        )

    if legacy_terminal_stale:
        warnings.extend(
            "legacy terminal evidence cannot be scope-reconstructed: "
            f"{row['id']} target={row['target']} validator={row['validator']}"
            for row in legacy_terminal_stale
        )

    legacy_terminal = [
        row
        for row in latest.values()
        if _legacy_terminal_fingerprint(
            row.get("source_hash", ""),
            row.get("target", ""),
        )
    ]

    lines = [
        f"evidence records: {len(rows)}",
        f"current stale evidence: {len(current_stale)}",
        f"legacy terminal evidence: {len(legacy_terminal)}",
    ]
    if warnings:
        lines += ["warnings:"] + ["  WARN " + item for item in warnings]
    if failures:
        lines += ["failures:"] + ["  FAIL " + item for item in failures]
    return not failures, "\n".join(lines)


_impl.source_fingerprint = source_fingerprint
_impl.audit_evidence = audit_evidence
_impl.verify_evidence = verify_evidence


if __name__ == "__main__":
    _sync_impl_globals()
    raise SystemExit(_impl.main())
