# EOS 0.8 Canonical State Reconciliation

**State:** COMPLETED  
**Date:** 2026-08-12  
**Scope:** EOS control integrity only  
**Product implementation authorized by this artifact:** No

## Purpose

Reconcile the accepted EOS 0.8 MVP program-adoption lifecycle state with the single canonical operational state model introduced concurrently during EOS hardening.

## Observed defect

After the EOS 0.8 adoption integration, the append-only event ledger, TSV lifecycle registries, and governed Markdown lifecycle metadata represented the accepted program-adoption state, while `.eos/state/current.json` remained at its earlier migration snapshot.

The stale canonical snapshot still contained only:

- `PI-001` — `DRAFT`;
- `WC-0001` — `DRAFT`;
- `WP-0001` — `DRAFT`.

Accepted lifecycle evidence instead records:

- `PI-001` — `SUPERSEDED`;
- `WC-0001` — `SUPERSEDED`;
- `WP-0001` — `SUPERSEDED`;
- `PI-MVP-001` — `AUTHORIZED`;
- `WC-MVP-0001` — `READY`;
- `WP-MVP-0001` — `READY`.

Consequently the canonical controller correctly failed closed and refused normal EOS commands.

## Root cause

The single-canonical-state work and the EOS 0.8 program-adoption work were developed as concurrent control-system tranches. The adoption migration updated accepted lifecycle projections and event history outside a canonical-state transaction, while the newly introduced canonical snapshot had already been seeded from the pre-adoption lifecycle state.

The merge reconciled schemas and runtime behavior but did not advance the canonical snapshot itself. Existing CI ran governed EOS verification but did not execute `./scripts/eos state status`, so this cross-model drift was not a merge gate.

## Reconciliation rule

Canonical state may be advanced from the accepted lifecycle records only when all of the following agree for every managed lifecycle entity:

1. the TSV lifecycle registry;
2. the governed Markdown lifecycle field;
3. the append-only EOS event ledger.

The reconciliation MUST fail if:

- any lifecycle state differs across those representations;
- an event-history entity is absent from the accepted registries;
- an existing canonical entity would disappear;
- an interrupted canonical transaction is present.

This is an explicit migration/reconciliation rule, not a general projection-wins policy. After reconciliation, `.eos/state/current.json` remains the sole operational current-state authority.

## GitHub projection clarification

GitHub Issue #21 is the product/coordination projection for Feature `F-002-01` / Work Packet `WP-MVP-0001`; it is not an EOS-owned lifecycle synchronization target.

Therefore its URL is removed from the EOS registry/adoption `github_url` field. The GitHub issue remains linked through product/backlog coordination artifacts, while EOS is prevented from treating that product issue as an object it may rewrite via `github-sync`.

## Permanent controls

- `scripts/reconcile-eos-canonical-state.py` performs the evidence-consensus reconciliation and is dry-run/check by default.
- `--apply` is required to write a new canonical revision.
- EOS Integrity must run the reconciliation check and `./scripts/eos state status` in addition to strict governed verification.
- Reconciliation preserves all existing canonical entities and records migration provenance on changed/new canonical entities.

## Expected reconciled state

Canonical revision advances from `1` to `2` with six managed lifecycle entities:

| Entity | State |
|---|---|
| PI-001 | SUPERSEDED |
| WC-0001 | SUPERSEDED |
| WP-0001 | SUPERSEDED |
| PI-MVP-001 | AUTHORIZED |
| WC-MVP-0001 | READY |
| WP-MVP-0001 | READY |

## Authority boundary

This reconciliation repairs EOS control integrity only. It does not start `PI-MVP-001`, authorize or start `WC-MVP-0001`, authorize or start `WP-MVP-0001`, or authorize product implementation.

After this reconciliation is merged and pulled locally, normal EOS parent-first lifecycle transitions may resume.
