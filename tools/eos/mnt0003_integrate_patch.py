#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"missing patch anchor: {label}")
    return text.replace(old, new, 1)


# event_ledger.py
path = Path("tools/eos/event_ledger.py")
text = path.read_text(encoding="utf-8")
if "def is_git_repository(" not in text:
    anchor = "def git_commit_exists(root: Path, ref: str) -> bool:\n"
    addition = '''def is_git_repository(root: Path) -> bool:
    proc = _git(root, "rev-parse", "--is-inside-work-tree", check=False)
    return proc.returncode == 0 and proc.stdout.strip() == "true"


'''
    text = replace_once(text, anchor, addition + anchor, "event_ledger git_commit_exists")

# Tighten Git blob reading so only an actually absent historical ledger is empty.
old = '''    proc = _git(root, "show", f"{ref}:{EVENT_LEDGER_RELPATH}", check=False)
    if proc.returncode != 0:
        # A history that predates introduction of the EOS ledger contributes no events.
        return []
    return _events_from_text(proc.stdout, label=f"{ref}:{EVENT_LEDGER_RELPATH}")
'''
new = '''    object_ref = f"{ref}:{EVENT_LEDGER_RELPATH}"
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
'''
if old in text:
    text = text.replace(old, new, 1)

old = '''    proc = _git(root, "rev-parse", "--git-path", "MERGE_HEAD", check=False)
    if proc.returncode != 0:
        return []
    merge_head = Path(proc.stdout.strip())
    if not merge_head.is_absolute():
        merge_head = root / merge_head
'''
new = '''    proc = _git(root, "rev-parse", "--absolute-git-dir", check=False)
    if proc.returncode != 0:
        return []
    merge_head = Path(proc.stdout.strip()) / "MERGE_HEAD"
'''
if old in text:
    text = text.replace(old, new, 1)

if "def validate_working_history(" not in text:
    text = text.rstrip() + '''


def validate_working_history(root: Path) -> None:
    if not is_git_repository(root):
        return
    current = read_event_ledger(root / EVENT_LEDGER_RELPATH)
    if git_commit_exists(root, "HEAD"):
        validate_parent_superset(current, [ledger_from_git(root, "HEAD")])
    validate_working_merge(root)
'''
path.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")


# canonical_state.py
path = Path("tools/eos/canonical_state.py")
text = path.read_text(encoding="utf-8")
if "from event_ledger import (" not in text:
    anchor = "from typing import Iterable\n\nUTC = dt.timezone.utc\n"
    replacement = '''from typing import Iterable

TOOLS_EOS_DIR = Path(__file__).resolve().parent
if str(TOOLS_EOS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_EOS_DIR))

from event_ledger import (
    EventLedgerError,
    is_git_repository,
    validate_committed_history,
    validate_working_history,
)

UTC = dt.timezone.utc
'''
    text = replace_once(text, anchor, replacement, "canonical_state imports")

if "def event_history_failures(" not in text:
    anchor = 'LAST_ROLLBACK_PATH = EOS / "cache" / "canonical-state-last-rollback.json"\n'
    replacement = anchor + '''

def event_history_failures() -> list[str]:
    if not is_git_repository(ROOT):
        return []
    failures: list[str] = []
    try:
        validate_committed_history(ROOT)
    except EventLedgerError as exc:
        failures.append(f"committed event history invalid: {exc}")
    try:
        validate_working_history(ROOT)
    except EventLedgerError as exc:
        failures.append(f"working event history invalid: {exc}")
    return failures


def assert_event_history_integrity() -> None:
    failures = event_history_failures()
    if failures:
        raise StateError(
            "EOS event-history integrity failed:\n- " + "\n- ".join(failures)
        )
'''
    text = replace_once(text, anchor, replacement, "canonical_state history helpers")

pre = "    assert_clean(state, include_github_local=not is_github_sync)\n"
if pre + "    assert_event_history_integrity()\n" not in text:
    text = replace_once(text, pre, pre + "    assert_event_history_integrity()\n", "canonical_state pre")

post = "    changed = capture_successful_transaction(command)\n"
if "    assert_event_history_integrity()\n" + post not in text:
    text = replace_once(text, post, "    assert_event_history_integrity()\n" + post, "canonical_state post")

status = "    failures = projection_drift(state, include_github_local=True)\n"
if "    failures.extend(event_history_failures())\n" not in text:
    text = replace_once(
        text,
        status,
        status + "    failures.extend(event_history_failures())\n",
        "canonical_state status",
    )
path.write_text(text, encoding="utf-8")


# reconcile-eos-canonical-state.py
path = Path("scripts/reconcile-eos-canonical-state.py")
text = path.read_text(encoding="utf-8")
if "    cs.assert_event_history_integrity()\n" not in text:
    anchor = "    rows_by_kind = cs.rows_from_projections()\n"
    text = replace_once(
        text,
        anchor,
        "    cs.assert_event_history_integrity()\n\n" + anchor,
        "canonical reconciliation",
    )
path.write_text(text, encoding="utf-8")


# verification_v2.py
path = Path("tools/eos/verification_v2.py")
text = path.read_text(encoding="utf-8")
if "from event_ledger import (" not in text:
    anchor = '''from identity_families import (
    REQUIREMENT_ID_PATTERN,
    SPECIFICATION_ID_PATTERN,
    is_requirement_id,
    is_specification_id,
)
'''
    replacement = anchor + '''from event_ledger import (
    EventLedgerError,
    is_git_repository,
    validate_committed_history,
    validate_working_history,
)
'''
    text = replace_once(text, anchor, replacement, "verification_v2 imports")

start = text.find("def cmd_verify(args):\n")
end = text.find("\ndef cmd_validators(args):", start)
if start < 0 or end < 0:
    raise SystemExit("missing patch anchor: verification_v2 cmd_verify")
replacement = '''def verify_event_history_integrity() -> tuple[bool, str]:
    if not is_git_repository(ROOT):
        return True, "SKIP — repository is not a Git work tree"
    try:
        validate_committed_history(ROOT)
        validate_working_history(ROOT)
        return True, "PASS — current and working event histories preserve inherited events"
    except EventLedgerError as exc:
        return False, f"FAIL — {exc}"


def cmd_verify(args):
    p=core("verify",*( ["--strict"] if args.strict else [] )); ok_core=p.returncode==0
    ok_evid,evid_report=verify_evidence(args.strict)
    ok_history,history_report=verify_event_history_integrity()
    report={
        "core":{"passed":ok_core,"output":p.stdout+p.stderr},
        "event_history":{"passed":ok_history,"output":history_report},
        "evidence":{"passed":ok_evid,"output":evid_report},
        "passed":ok_core and ok_history and ok_evid,
    }
    if args.json: print(json.dumps(report,indent=2,sort_keys=True))
    else:
        print((p.stdout+p.stderr).rstrip())
        print("\nEOSV EVENT HISTORY INTEGRITY\n"+history_report)
        print("\nEOSV EVIDENCE INTEGRITY\n"+evid_report)
        print(f"\nEOSV RESULT: {'PASS' if report['passed'] else 'FAIL'}")
    if not report["passed"]: raise EosvError("EOS verification failed")

'''
text = text[:start] + replacement + text[end + 1 :]
path.write_text(text, encoding="utf-8")


# test_event_ledger_merge.py
path = Path("tools/eos/test_event_ledger_merge.py")
text = path.read_text(encoding="utf-8")
if "test_working_tree_cannot_delete_head_event" not in text:
    anchor = '\n\nif __name__ == "__main__":\n'
    addition = '''
    def test_working_tree_cannot_delete_head_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_git_repo(root)
            events = [
                event("EVT-A", target="WP-A", from_state="DRAFT", to_state="READY"),
                event("EVT-B", target="WP-B", from_state="DRAFT", to_state="READY"),
            ]
            self.write_git_ledger(root, events)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "base")
            self.write_git_ledger(root, [events[0]])
            with self.assertRaises(self.ledger.EventLedgerError):
                self.ledger.validate_working_history(root)

    def test_working_merge_rejects_same_entity_divergence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_git_repo(root)
            base = [event("EVT-BASE", target="WP-X", event_type="ENTITY_CREATED", to_state="DRAFT")]
            self.write_git_ledger(root, base)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "base")
            base_sha = self.git(root, "rev-parse", "HEAD").stdout.strip()
            self.git(root, "checkout", "-qb", "left")
            self.write_git_ledger(
                root,
                base + [event("EVT-LEFT", target="WP-X", from_state="DRAFT", to_state="READY")],
            )
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "left")
            self.git(root, "checkout", "-qb", "right", base_sha)
            self.write_git_ledger(
                root,
                base + [event("EVT-RIGHT", target="WP-X", from_state="DRAFT", to_state="BLOCKED")],
            )
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "right")
            self.git(root, "merge", "--no-commit", "--no-ff", "left")
            with self.assertRaises(self.ledger.EventLedgerConflict):
                self.ledger.validate_working_history(root)

    def test_working_merge_accepts_independent_entities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_git_repo(root)
            base = [event("EVT-BASE", target="WP-BASE", event_type="ENTITY_CREATED", to_state="DRAFT")]
            self.write_git_ledger(root, base)
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "base")
            base_sha = self.git(root, "rev-parse", "HEAD").stdout.strip()
            self.git(root, "checkout", "-qb", "left")
            self.write_git_ledger(
                root,
                base + [event("EVT-LEFT", target="WP-LEFT", from_state="DRAFT", to_state="READY")],
            )
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "left")
            self.git(root, "checkout", "-qb", "right", base_sha)
            self.write_git_ledger(
                root,
                base + [event("EVT-RIGHT", target="WP-RIGHT", from_state="DRAFT", to_state="READY")],
            )
            self.git(root, "add", ".")
            self.git(root, "commit", "-qm", "right")
            self.git(root, "merge", "--no-commit", "--no-ff", "left")
            self.ledger.validate_working_history(root)
'''
    if text.count(anchor) != 1:
        raise SystemExit("missing patch anchor: test main")
    text = text.replace(anchor, "\n" + addition + anchor, 1)
path.write_text(text, encoding="utf-8")

print("MNT-0003 integration patch applied")
