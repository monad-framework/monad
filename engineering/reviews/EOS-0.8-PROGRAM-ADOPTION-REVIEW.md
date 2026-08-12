# EOS 0.8 Program Adoption Review

**Review date:** 2026-08-12  
**Scope:** Engineering Operating System lifecycle reconciliation  
**Branch:** `eos/v0.8-program-adoption`  
**Disposition:** **PASS — READY FOR INTEGRATION**

## Purpose

Verify that EOS can adopt the already-accepted Monad MVP execution horizon without replaying obsolete bootstrap work, erasing lifecycle history, weakening parent/child authorization gates, or creating a competing source of engineering authority.

## Problem addressed

After Foundation Stabilization merged, canonical engineering state and EOS control state diverged:

- canonical planning used `PI-MVP-001`, `WC-MVP-0001`, and `WP-MVP-0001`;
- EOS 0.7 recognized namespaced Work Packets but not namespaced Program Increment or Work Cycle identifiers;
- EOS registries still exposed bootstrap placeholders `PI-001`, `WC-0001`, and `WP-0001` as Draft;
- `.eos/workflow.tsv` still treated EOSB-001 as the next action even though Foundation Stabilization had already satisfied and superseded the bootstrap purpose with stronger evidence.

Proceeding directly to product implementation would therefore have created contradictory lifecycle authority.

## Accepted solution

EOS 0.8 introduces a governed program-adoption mechanism and namespaced lifecycle identifiers.

### Identifier semantics

EOS accepts both historical unqualified identifiers and namespaced execution identifiers:

- `PI-001` and `PI-MVP-001`;
- `WC-0001` and `WC-MVP-0001`;
- `WP-0001`, `WP-MVP-0001`, and other existing Work Packet namespaces.

Schemas, trace/reference parsing, completion, lifecycle lookup, and EOSV identifier handling use the same model.

### Supersession semantics

`SUPERSEDED` is a terminal lifecycle state for PI, WC, and WP objects. Adoption preserves the historical objects rather than deleting or renumbering them.

Current supersession:

- `PI-001` → SUPERSEDED;
- `WC-0001` → SUPERSEDED;
- `WP-0001` → SUPERSEDED.

### Bootstrap reconciliation

`.eos/workflow.tsv` records EOSB-001 through EOSB-020 Complete under the explicit adoption disposition `superseded-by-foundation-stabilization`. This does not claim that the obsolete Draft Inception Review was independently completed. It records that the accepted Foundation Stabilization baseline superseded and satisfied the bootstrap purpose.

### Rolling-wave adoption

EOS does **not** import all future MVP forecast objects into active lifecycle control. The canonical roadmap remains authoritative for the full program. EOS adopts only the current execution horizon:

- `PI-MVP-001` — AUTHORIZED;
- `WC-MVP-0001` — READY;
- `WP-MVP-0001` — READY.

This keeps `status` and `next` useful and prevents distant forecast work from competing with current WIP.

### Parent-first execution

Adoption does not bypass normal authorization order.

The expected transition sequence is:

1. start `PI-MVP-001`;
2. authorize `WC-MVP-0001` only after its parent PI is Authorized/Active;
3. start `WC-MVP-0001`;
4. authorize `WP-MVP-0001` only after its parent WC is Authorized/Active;
5. start `WP-MVP-0001`;
6. create bounded EOSE/Codex execution only for that packet.

## Verification performed

The EOS 0.8 migration/adoption run completed successfully on GitHub Actions run `31598298583`.

The following stages passed:

- EOS source/schema/state-machine migration to the 0.8 fixed point;
- reviewed MVP execution-horizon adoption;
- EOS 0.8 program-adoption regression contract;
- `./scripts/eos verify --strict`;
- deterministic machine-document synchronization;
- deterministic commit of migrated control state.

The committed adoption result is rooted at commit `6084fe64b7617ee249377eb9f482dfca89eecd4c` before review/cleanup follow-up commits.

## Regression contract

`scripts/test-eos-0.8-program-adoption.py` verifies at minimum:

- EOSB reports complete after adoption;
- namespaced PI/WC/WP objects are visible to EOS;
- historical bootstrap objects remain visible as SUPERSEDED;
- `next` is lifecycle-aware and recommends the correct parent-first action;
- PI/WC/WP state machines support terminal SUPERSEDED state;
- `WC_AUTHORIZE` passes for the adopted Ready cycle while PI-MVP-001 is Authorized;
- `WP_AUTHORIZE` fails while WC-MVP-0001 is only Ready, proving parent authorization was not bypassed;
- adoption dry-run is non-mutating;
- reapplying the same adoption manifest is idempotent and does not reset lifecycle state.

## Authority and safety assessment

PASS.

The adoption manifest is a control-state bridge from accepted canonical evidence. It does not create product requirements, architecture decisions, or implementation authority by itself. Canonical Git artifacts remain authoritative; `.eos/` records the governed execution state derived from that authority.

The system preserves history, uses explicit supersession, requires reviewed evidence, and keeps Work Packet authorization separate from PI/WC adoption.

## Residual considerations

- Future PIs/WCs may use namespaced identifiers; namespace allocation should remain intentional and collision-free.
- Future forecast packets should enter EOS only when they approach the rolling-wave execution horizon.
- An adoption manifest must not be used as a shortcut around an unresolved readiness/authorization decision.
- Read-only EOS commands should remain observational; trace rebuilding may rewrite a generated file but must remain byte-stable when canonical state is unchanged.

## Decision

**Decision:** ACCEPTED

EOS 0.8 Program Adoption & Namespaced Lifecycle IDs is ready to integrate after normal PR checks pass. Product implementation remains unauthorized until the adopted parent lifecycle transitions are executed and `WP-MVP-0001` is explicitly authorized through EOS.
