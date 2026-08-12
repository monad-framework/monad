# EOS Single Canonical State Model — Implementation Record

**Status:** Implemented  
**Date:** 2026-08-12  
**Canonical model:** `EOS-SINGLE-CANONICAL-STATE-1`

## Scope

This tranche makes machine-readable EOS metadata the sole canonical current
operational state and explicitly demotes TSV registries, Markdown lifecycle
fields, Git history, GitHub collaboration objects, and runtime cache state to
their correct roles.

## Implementation

- `.eos/state/current.json` — canonical current operational state.
- `.eos/state/projections.json` — local projection fingerprints and GitHub sync
  receipts.
- `.eos/state-model.json` — normative machine-readable representation policy.
- `.eos/schemas/canonical-state.schema.json` — canonical store schema.
- `.eos/schemas/projection-manifest.schema.json` — projection receipt schema.
- `tools/eos/canonical_state.py` — canonical transaction, drift detection,
  projection, and reconciliation controller.
- `scripts/eos` — transaction wrapper around the compatibility EOS runtime.
- `tools/eos/test_canonical_state.py` — deterministic regression tests.

## Compatibility Strategy

The existing `tools/eos/eos.py` implementation is retained as a compatibility
runtime during this tranche. It still operates on TSV/Markdown projections, but
it can no longer be invoked through the supported `scripts/eos` entry point
without canonical preflight and post-transaction capture.

This avoids a high-risk monolithic rewrite while immediately enforcing one
operational source of truth.

## Fail-closed cases

The controller rejects:

- direct TSV edits;
- Markdown lifecycle edits inconsistent with canonical state;
- event history whose reconstructed lifecycle differs from canonical state;
- entity disappearance during a normal transaction;
- a successful legacy command that leaves its projections mutually
  inconsistent;
- GitHub automatic overwrite when the remote issue changed since the last
  synchronization receipt.

## Explicit projection repair

Local projections can only be repaired from canonical state. GitHub reconciliation
requires an explicit target and `canonical-wins` strategy. There is no implicit
projection-to-canonical import.

## Initial inconsistency resolved

Before this tranche, `.eos/program-increments.tsv` and `.eos/events.jsonl` said
PI-001 was `DRAFT`, while the governed Markdown said `Planned`. WC-0001 had the
same discrepancy. The initial canonical seed follows the agreeing operational
registry/event history and repairs the Markdown lifecycle fields to `DRAFT`.

## Tests

The regression suite covers:

1. clean canonical/projection state;
2. direct TSV drift detection;
3. direct Markdown lifecycle drift detection;
4. successful transaction advancement of canonical revision/state;
5. one-way local projection repair from canonical state.
