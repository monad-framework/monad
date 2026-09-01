# EOS Trace Projection Integrity Repair — 2026-08-12

**Decision:** ACCEPTED

## Finding

A clean checkout of protected `main` could pass `./scripts/eos verify --strict` while leaving `.eos/trace-edges.tsv` modified. The tracked trace projection contained stale merge-resolution residue and no gate required the deterministic projection to match the committed file after verification.

The repository wrapper also dispatched commands twice: it executed the legacy controller inside the canonical transaction and then executed the selected legacy/v2 runtime again. This duplicated output and could duplicate side effects.

## Root Cause

1. `tools/eos/eos.py::rebuild_trace()` is used by verification and planning/query paths and writes `.eos/trace-edges.tsv` as a side effect.
2. EOS Integrity validated the logical report but did not require the tracked trace projection to equal deterministic regeneration.
3. Repository Integrity did not reject unresolved Git conflict-marker lines.
4. `scripts/eos` selected the v2 runtime only after already invoking the legacy runtime once.

## Repair

- Regenerate `.eos/trace-edges.tsv` from the current governed repository state.
- Add `tools/eos/trace_integrity.py` to compute the expected trace without writing during checks and to support explicit atomic regeneration with `--write`.
- Add `tools/eos/test_wrapper_dispatch.py` to prove one-runtime dispatch for legacy, EOSE v2, and EOSV v2 commands.
- Change `scripts/eos` so one selected runtime executes exactly once inside the canonical transaction.
- Require EOS Integrity to check trace freshness before verification and require the full working tree to remain unchanged afterward.
- Require Repository Integrity to reject unresolved `<<<<<<<` / `>>>>>>>` conflict markers and to reject EOS verification that changes tracked files.

## Safety Properties

- Verification may inspect/recompute trace semantics but a stale committed projection is a gate failure, not a silent repair.
- Explicit trace regeneration is separate from verification.
- Canonical lifecycle state remains unchanged by this repair.
- `PI-MVP-001`, `WC-MVP-0001`, and `WP-MVP-0001` are not started or authorized by this repair.
- Existing EOSV Verification v2 behavior is preserved behind single-dispatch routing.

## Required Evidence

The repair is acceptable only when all of the following are true on the final branch head:

1. `python3 tools/eos/test_wrapper_dispatch.py` passes.
2. `python3 tools/eos/trace_integrity.py` reports the tracked trace as consistent.
3. `./scripts/eos state status` reports `RESULT: CONSISTENT`.
4. `./scripts/eos verify --strict` passes.
5. `git diff --exit-code` passes after verification.
6. machine documentation synchronization passes.
7. permanent PR Repository Integrity, EOS Integrity, and Machine Document Synchronization checks pass.

## Disposition

**ACCEPTED** as a blocking control-integrity repair that must merge before the first MVP lifecycle transition.
