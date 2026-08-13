# EOS 0.9 — Decision and Readiness Engine

**Status:** Proposed
**Date:** 2026-08-13
**Related:** ADR-0006, CR-0001, `engineering/eos/AI-SDLC-ASSIMILATION-PROGRAM.md`

## Objective

Strengthen EOS planning so a Work Packet reaches readiness only when EOS can explain why its contract is sufficiently bounded, decided, traceable, and verifiable for the requested lifecycle transition.

EOS 0.9 is an engineering-control-plane change. It does not change Monad product-runtime architecture or broaden any existing MVP Work Packet.

## Required outcomes

1. Unresolved Decisions can exist as first-class records without requiring a fictitious outcome.
2. Decision, Approval, and Dependency records can participate in canonical operational state through the existing EOS transaction model.
3. Work Packet readiness evaluates deterministic structural, reference, dependency, decision, authority, staleness, scope, acceptance, and verification predicates.
4. Gate results are explainable and identify the smallest unmet condition.
5. A blocked decision or dependency affects only graph-related work.
6. Existing PI/WC/WP/CR/MNT/REL behavior remains compatible unless an explicit migration says otherwise.

## Decision lifecycle correction

Current Decision schema requires `outcome` even in the `PROPOSED` state. EOS 0.9 should permit an unresolved lifecycle such as:

```text
PROPOSED -> OPEN -> DECIDED -> SUPERSEDED
                 \-> DEFERRED -> OPEN
```

`outcome` and final rationale become required when the record is decided, not while the question is still open.

The exact state names may be adjusted during implementation review, but the invariant is fixed: unresolved decisions must be representable without inventing an answer.

## Canonical-state extension

EOS 0.9 should admit `DEC`, `APR`, and `DEP` as operational entity kinds under `.eos/state/current.json`.

The migration must preserve the single-authority rule:

- canonical state is written only through EOS transactions;
- event history remains append-only evidence;
- TSV/Markdown/GitHub representations are projections;
- migration failure leaves prior canonical state authoritative;
- successful migration increments canonical state revision and regenerates projections.

No parallel decision database or external control-state directory is introduced.

## Readiness dimensions

### Structural

- registered identity and parent links are valid;
- required sections/fields exist;
- unresolved placeholders are absent except where policy permits them.

### Governing references

- referenced requirements/specifications/ADRs exist;
- governing artifacts are not known stale or superseded for the requested transition;
- required authority level is sufficient.

### Dependencies

- dependency references resolve;
- dependency graph is acyclic;
- blocking prerequisites have the required lifecycle disposition;
- optional/reference-only relationships do not become accidental blockers.

### Decision closure

- decisions that govern or block the packet are resolved at the required authority level;
- required approvals are present and current;
- unresolved decisions unrelated to the packet do not block it.

### Scope

- implementation surface is bounded;
- exclusions are explicit;
- oversized work requires decomposition or an accepted exception.

### Acceptance and verification

- acceptance criteria are observable/testable enough for delivery work;
- required validation/evidence expectations are declared;
- security/operations/release checks apply when their thresholds are crossed.

## Deterministic-first rule

Schema checks, reference resolution, lifecycle checks, graph traversal, policy evaluation, and unresolved-marker checks run before semantic/model-assisted evaluation.

If a semantic evaluator is later used, its output is attributed evidence. It cannot silently create binding/sovereign authority or override a deterministic gate failure.

## Candidate policy predicates

`WP_READY` and, where appropriate, `WP_AUTHORIZE` should compose named predicates such as:

- `artifact_complete`
- `no_unresolved_markers`
- `governing_refs_resolve`
- `governing_refs_current`
- `dependencies_valid`
- `blocking_dependencies_satisfied`
- `blocking_decisions_resolved`
- `required_approvals_present`
- `scope_bounded`
- `acceptance_testable`
- `verification_contract_present`

Names remain implementation details until authorized.

## Explainability contract

For every readiness predicate, EOS should be able to report:

```text
predicate
result
reason
evidence/source
blocking entity when applicable
smallest corrective action when determinable
```

The existing `gate check` and `gate explain` surfaces remain the primary operator interface unless a later decision changes that boundary.

## Migration sequence

1. accept governing architecture;
2. add versioned schemas and lifecycle definitions;
3. extend canonical-state schema/model and transaction support;
4. prove migration and rollback on fixtures;
5. add projections and CLI operations for DEC/APR/DEP;
6. add readiness predicates and explainability;
7. validate positive/negative fixtures;
8. verify existing lifecycle compatibility;
9. enable strengthened gates only after migration verification passes.

## Validation expectations

The implementation tranche must prove at least:

- open Decision without outcome is valid;
- decided Decision without outcome is invalid;
- invalid/revoked approval cannot satisfy required approval;
- unresolved blocking dependency prevents readiness;
- unrelated unresolved decision does not prevent readiness;
- stale governing authority prevents readiness where required;
- deterministic gate explanation is stable for identical state;
- canonical-state migration is repeatable and rejects drift;
- existing MVP state is semantically unchanged by migration;
- `./scripts/eos state status` passes;
- `./scripts/eos verify --strict` passes.

## Explicitly deferred

EOS 0.9 does not implement worker pools, dispatch expansion, multi-harness review, proof-of-execution Merkle structures, TUI, cost governance, or an AI-SDLC compatibility adapter. Those remain later program tranches.
