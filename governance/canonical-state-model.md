---
artifact_id: "GOV-STATE-0001"
title: "Canonical EOS State Model"
type: "governance"
version: "1.0.0"
status: "Implemented"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# Canonical EOS State Model

## Normative Rule

There is exactly one canonical representation of **current EOS operational state**:

`.eos/state/current.json`

It is machine-readable, versioned, schema-governed EOS metadata. No Markdown file,
TSV registry, GitHub Issue, event replay, runtime cache, or Git view may silently
override it.

## Representation Roles

| Representation | Role | May define current operational state? |
|---|---|---:|
| `.eos/state/current.json` | Canonical operational state | **Yes — exclusively** |
| `.eos/events.jsonl` | Append-only mutation/audit history | No |
| `.eos/*.tsv` lifecycle registries | Generated compatibility projections | No |
| Governed Markdown | Human-readable governed content; lifecycle metadata is projected | No |
| Git | Version history, integrity, provenance, rollback evidence | No |
| GitHub Issues/Projects | Synchronized collaboration projection | No |
| EOS runtime cache/internal state | Ephemeral execution support | No |

The machine-readable definition of this contract is `.eos/state-model.json`.

## Canonical State

The canonical store contains current first-class operational records for PI, WC,
WP, ChangeRequest, MaintenanceItem, and Release. Each stored entity carries the
core EOS identity/version/lifecycle/timestamp/relationship/authority/provenance
contract established by the EOS Core Schema and Canonical Domain Model.

Canonical state has a monotonically increasing `revision`. A canonical digest is
computed over the semantic current-state payload. A revision advances only when
a successful EOS operation materially changes operational state.

## Transaction Invariant

All ordinary `./scripts/eos ...` commands execute through the canonical-state
transaction wrapper.

1. Load and validate canonical state.
2. Compare TSV, governed Markdown lifecycle metadata, and event-derived lifecycle
   history against canonical state.
3. Fail closed if any local representation has drifted.
4. For an applying GitHub synchronization, verify the current remote object
   against the previous synchronization receipt before allowing an overwrite.
5. Record the starting canonical revision/digest and event count in an ephemeral
   transaction receipt.
6. Run the existing EOS compatibility runtime against generated projections.
7. If the command fails, discard the transaction receipt; canonical state does
   not advance.
8. If the command succeeds, require TSV, Markdown lifecycle metadata, and event
   history to converge on the same resulting state.
9. Capture that successful result into canonical machine-readable state.
10. Regenerate exact TSV projections from canonical state.
11. Refresh projection fingerprints/synchronization receipts.
12. Report any GitHub projection that is now stale.

A failed or inconsistent operation can therefore leave evidence of an interrupted
projection write, but it cannot silently change canonical operational state.

## TSV Registries

The lifecycle TSV files remain for compatibility with the current EOS
implementation and shell tooling. They are **generated projections**.

Direct manual edits are forbidden. A byte-level difference between the expected
canonical rendering and the checked-in TSV is drift and blocks ordinary EOS
operations.

`./scripts/eos state project --apply` repairs them from canonical state.

## Governed Markdown

Markdown remains the authoritative human-readable expression of governed
engineering content. It does **not** independently own lifecycle state.

For managed lifecycle entities:

- visible `**State:**` / legacy `**Status:**` values must equal canonical state;
- front-matter `status`, when present, must equal canonical state;
- ordinary prose/content remains governed Markdown content and is not replaced
  merely because canonical lifecycle state changes.

Lifecycle disagreement is drift and blocks ordinary EOS operations.

## Event Ledger

`.eos/events.jsonl` remains append-only history. Its replayed lifecycle result
must agree with canonical current state, but replay is no longer allowed to
silently replace current state.

Historical corrections must be represented by new governed events. The event
ledger must never be rewritten merely to make a projection check pass.

The former `rebuild-state` command is retained only as a compatibility alias for
projection **from canonical state**. It no longer treats event replay as the
current-state authority.

## Git

Git is authoritative history, not authoritative current operational state.

Git provides:

- immutable commit history;
- provenance and review evidence;
- change comparison;
- recovery inputs;
- signed/protected history where configured.

Checking out an older Git revision naturally yields the canonical state that was
valid in that revision. Within any one checkout, `.eos/state/current.json` is the
sole current operational authority.

## GitHub

GitHub Issues/Projects are collaboration projections.

Canonical -> GitHub is the normal synchronization direction. Every synchronized
issue receives a local receipt containing the canonical revision plus expected
and observed remote fingerprints.

If a GitHub issue changes independently:

- EOS detects the remote fingerprint change before automatic synchronization;
- EOS refuses to overwrite the remote change silently;
- the operator must explicitly reconcile;
- GitHub content never becomes canonical merely because it was edited remotely.

An external GitHub proposal that should alter EOS meaning must enter the governed
EOS change process rather than being implicitly imported.

## Drift Semantics

Drift is a first-class fault, not a warning that may be ignored silently.

- **TSV drift:** hard failure.
- **Markdown lifecycle drift:** hard failure.
- **Event-history/current-state drift:** hard failure.
- **GitHub unexpected remote drift:** blocks automatic overwrite.
- **GitHub stale after a legitimate canonical mutation:** explicitly reported;
  subsequent ordinary work is blocked until GitHub synchronization or explicit
  reconciliation.

## Reconciliation

Projection reconciliation is one-way by default: **canonical wins**.

```bash
./scripts/eos state status
./scripts/eos state project --apply
./scripts/eos state reconcile local --strategy canonical-wins
./scripts/eos state reconcile github --target WP-0001 --strategy canonical-wins
./scripts/eos github-sync --apply
```

There is intentionally no `projection-wins` shortcut. If a projection contains a
change worth adopting, that change must be translated into an explicit governed
EOS mutation/change request.

## Migration Decision

At migration, the accepted machine-readable lifecycle registries and append-only
event history agree that PI-001, WC-0001, and WP-0001 are `DRAFT`. Existing
Markdown said `Planned` for PI-001 and WC-0001. The migration does not guess or
merge these competing states: it seeds canonical state from the agreeing
machine-readable operational/event representations and repairs Markdown lifecycle
metadata to `DRAFT`.

## Verification

`./scripts/eos state status` is the canonical state/projection integrity check.
The standard `./scripts/eos verify` command now passes through canonical
preflight before the legacy verifier runs, so detected drift cannot be bypassed
silently by the ordinary EOS command path.
