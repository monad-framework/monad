#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


# Repair literal newline escapes in the generated canonical-state error formatter.
path = Path("tools/eos/canonical_state.py")
text = path.read_text(encoding="utf-8")
start = text.find("def assert_event_history_integrity() -> None:\n")
end = text.find("\ndef now_iso()", start)
if start < 0 or end < 0:
    raise SystemExit("canonical_state generated helper boundaries missing")
replacement = r'''def assert_event_history_integrity() -> None:
    failures = event_history_failures()
    if failures:
        raise StateError(
            "EOS event-history integrity failed:\n- " + "\n- ".join(failures)
        )

'''
text = text[:start] + replacement + text[end + 1 :]
path.write_text(text, encoding="utf-8")


# Repair literal newline escapes in the generated EOSV report formatter.
path = Path("tools/eos/verification_v2.py")
text = path.read_text(encoding="utf-8")
start = text.find("def verify_event_history_integrity() -> tuple[bool, str]:\n")
end = text.find("\ndef cmd_validators(args):", start)
if start < 0 or end < 0:
    raise SystemExit("verification_v2 generated function boundaries missing")
replacement = r'''def verify_event_history_integrity() -> tuple[bool, str]:
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

print("MNT-0003 integration generated-source escapes normalized")
