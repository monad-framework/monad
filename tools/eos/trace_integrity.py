#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EOS = ROOT / ".eos"
TRACE = EOS / "trace-edges.tsv"
CORE = ROOT / "tools" / "eos" / "eos.py"
FIELDS = ["source_id", "target_id", "edge_type", "source_path", "evidence"]
CONFLICT_MARKERS = ("<<<<<<<", "=======", ">>>>>>>")


class TraceIntegrityError(RuntimeError):
    pass


def load_core():
    os.environ["EOS_ROOT"] = str(ROOT)
    spec = importlib.util.spec_from_file_location("eos_trace_core", CORE)
    if spec is None or spec.loader is None:
        raise TraceIntegrityError(f"cannot load {CORE.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render(rows: list[dict[str, str]]) -> str:
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(
        buf,
        fieldnames=FIELDS,
        delimiter="\t",
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in FIELDS})
    return buf.getvalue()


def expected_trace() -> str:
    core = load_core()
    writes: list[Path] = []

    def deny_write(path, fields, rows):
        target = Path(path).resolve()
        writes.append(target)
        if target != TRACE.resolve():
            raise TraceIntegrityError(
                f"trace rebuild attempted unexpected write: {target}"
            )
        # Intentionally do not write. rebuild_trace() returns the deterministic
        # rows, allowing verification to remain side-effect free.

    core.write_tsv = deny_write
    rows = core.rebuild_trace()
    if writes != [TRACE.resolve()]:
        raise TraceIntegrityError(
            "trace rebuild did not attempt exactly one trace projection write"
        )
    return render(rows)


def atomic_write(text: str) -> None:
    TRACE.parent.mkdir(parents=True, exist_ok=True)
    tmp = TRACE.with_suffix(TRACE.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="")
    os.replace(tmp, TRACE)


def check(current: str, expected: str) -> list[str]:
    failures: list[str] = []
    for marker in CONFLICT_MARKERS:
        if any(line.startswith(marker) for line in current.splitlines()):
            failures.append(f"tracked trace contains merge-conflict marker {marker}")
    if current != expected:
        failures.append(
            "tracked trace projection is stale; run "
            "python3 tools/eos/trace_integrity.py --write"
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check or regenerate the deterministic EOS trace projection"
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="atomically replace .eos/trace-edges.tsv with the deterministic projection",
    )
    args = parser.parse_args()

    expected = expected_trace()
    current = TRACE.read_text(encoding="utf-8") if TRACE.exists() else ""

    if args.write:
        atomic_write(expected)
        current = expected

    failures = check(current, expected)
    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        return 1

    print(f"TRACE PROJECTION: CONSISTENT ({len(expected.splitlines()) - 1} edges)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
