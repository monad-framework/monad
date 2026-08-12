#!/usr/bin/env python3
"""One-way, idempotent migration for MVP planning identifiers.

EOS bootstrap/history owns the unqualified PI-NNN and WC-NNNN namespaces.
MVP Release 1 planning therefore uses PI-MVP-NNN and WC-MVP-NNNN so the two
systems can coexist without ambiguous identity.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = (
    ROOT / "scripts" / "generate-mvp-work-packets.py",
    ROOT / "product" / "backlog" / "MVP-BACKLOG.md",
    ROOT / "engineering" / "work-cycles" / "MVP-SPRINT-SCHEDULE.md",
)

PI_RENAMES = {
    "PI-001-SEMANTIC-FOUNDATION.md": "PI-MVP-001-SEMANTIC-FOUNDATION.md",
    "PI-002-INTELLIGENCE-CONTEXT.md": "PI-MVP-002-INTELLIGENCE-CONTEXT.md",
    "PI-003-INTEGRATION-RELEASE.md": "PI-MVP-003-INTEGRATION-RELEASE.md",
}


def namespace_cycles(text: str) -> str:
    for number in range(13):
        old = f"WC-{number:04d}"
        new = f"WC-MVP-{number:04d}"
        text = text.replace(old, new)
    # Expand shorthand ranges after namespacing, e.g. WC-MVP-0001–0002.
    text = re.sub(r"WC-MVP-(\d{4})–(\d{4})", r"WC-MVP-\1–WC-MVP-\2", text)
    return text


def migrate_file(path: Path) -> bool:
    if not path.exists():
        return False
    original = path.read_text(encoding="utf-8")
    migrated = namespace_cycles(original)
    if migrated == original:
        return False
    path.write_text(migrated, encoding="utf-8")
    return True


def migrate_increment(old_name: str, new_name: str) -> bool:
    directory = ROOT / "engineering" / "increments"
    old_path = directory / old_name
    new_path = directory / new_name
    changed = False

    source = new_path if new_path.exists() else old_path
    if not source.exists():
        return False

    text = source.read_text(encoding="utf-8")
    text = namespace_cycles(text)
    old_id = old_name.split("-", 3)[0] + "-" + old_name.split("-", 3)[1]
    # old_id is PI-001 / PI-002 / PI-003.
    new_id = old_id.replace("PI-", "PI-MVP-")
    text = text.replace(old_id, new_id)

    if not new_path.exists() or new_path.read_text(encoding="utf-8") != text:
        new_path.write_text(text, encoding="utf-8")
        changed = True
    if old_path.exists() and old_path != new_path:
        old_path.unlink()
        changed = True
    return changed


def main() -> int:
    changed: list[str] = []
    for path in TARGETS:
        if migrate_file(path):
            changed.append(path.relative_to(ROOT).as_posix())

    for old_name, new_name in PI_RENAMES.items():
        if migrate_increment(old_name, new_name):
            changed.append(f"engineering/increments/{old_name} -> {new_name}")

    if changed:
        print("Namespaced MVP planning identifiers:")
        for item in changed:
            print(f"  {item}")
    else:
        print("MVP planning identifiers already namespaced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
