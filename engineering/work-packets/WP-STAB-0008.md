# WP-STAB-0008 — Reconcile First-Slice C1 Architecture and Specifications

**Status:** Planned  
**Owner:** Architecture Owner / Engineering Owner  
**Program:** STAB-0001

## Objective

Determine the minimum architecture decisions and normative specifications that must be sufficiently accepted before SPRINT-002 can implement workspace/configuration discovery without inventing semantic-kernel authority inside code.

## Scope

### Review concerns

- local-first runtime/module boundary;
- workspace root and repository identity;
- configuration source/schema/precedence;
- canonical versus generated artifact semantics;
- stable identity/canonicalization/provenance direction;
- diagnostic contract;
- first semantic graph boundary and relationship to the existing bootstrap `machine/graph.json`;
- KIR responsibility boundary;
- repository-input trust/security boundary;
- public CLI/config/schema compatibility direction;
- implementation-language/runtime decision if it materially constrains the first slice.

### Out of scope

- approving all C1/C2 artifact-system documents;
- remote execution, registry, hosted control plane, enterprise governance;
- detailed implementation of SPRINT-004+ graph/KIR algorithms before their refinement windows.

## Method

1. Inventory C1 Drafts relevant to SPRINT-002/003.
2. Identify contradictions, duplicates, and decisions already covered by ADR-0001 or higher authority.
3. Classify each concern as:
   - accepted authority already sufficient;
   - requires an ADR before implementation;
   - requires a specification before implementation;
   - implementation-local/reversible and may be decided inside the Work Packet;
   - deliberately deferred with bounded interface.
4. Produce only the new ADR/specification artifacts required by the first vertical slice.
5. Run implementation-readiness review for WP-WS-0001/WP-CONF-0001/WP-DISC-0001/WP-DIAG-0001.

## Acceptance criteria

- [ ] First-slice implementers have an explicit runtime/config/workspace/identity/diagnostic contract or a documented local-decision allowance.
- [ ] Bootstrap machine projection and future production MSG are not conflated.
- [ ] No two approved artifacts claim conflicting authority for the same semantic concern.
- [ ] Required new ADRs/specifications are identified with owners/status and dependency order.
- [ ] SPRINT-002 packet readiness can be evaluated without relying on chat context.
- [ ] Lower-criticality C1/C2 artifacts remain Draft rather than being bulk-approved for convenience.

## Validation

Run a paper implementation walkthrough: starting from an empty implementation directory, identify every consequential design question required to build SPRINT-002. Any question whose answer could materially alter public semantics, security, compatibility, or downstream architecture must point to sufficient authority or remain an explicit blocker.

## Completion evidence

C1 reconciliation review, required ADR/specification changes, and updated Work Packet readiness states.
