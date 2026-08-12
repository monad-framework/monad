---
artifact_id: "GOV-STATE-0001"
title: "Canonical EOS State Model"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# Canonical EOS State Model

## Rule

EOS lifecycle state is changed through **append-only events** and projected into
human- and machine-readable representations.

## Representations

1. `.eos/events.jsonl` — append-only lifecycle/audit event ledger.
2. `.eos/*.tsv` lifecycle registries — current operational projections.
3. governed Markdown artifacts — human-readable projection with front-matter
   status and a visible `**State:**` line where applicable.
4. Git — authoritative repository version history.
5. GitHub — synchronized collaboration projection, never a silent replacement
   for EOS engineering meaning.

## Mutation Invariant

A lifecycle command must:

1. validate the requested transition against the declarative state machine;
2. append an event describing the mutation;
3. update the current registry projection;
4. update the governed artifact projection;
5. leave the repository in a state that `./scripts/eos verify --strict` can
   validate.

Direct manual edits to operational registries are discouraged because they
bypass the audit ledger.

## Reconstruction

`./scripts/eos rebuild-state` replays lifecycle events and compares the derived
state with current registries. `--apply` is an explicit repair operation.
