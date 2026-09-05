---

artifact_id: "SPEC-BASE-0001"
title: "Specification Baseline"
type: "specification"
version: "0.1.0"
status: "Approved"
authority: "specification-authoritative"
created: "2026-08-12"
updated: "2026-09-05"
approval_evidence: "engineering/reviews/DECISION-0005-2026-09-05-aieng-normative-baseline-approval.md"
---------------------

# Specification Baseline

## Purpose

Define the current governed specification baseline for Monad and the traceability expectations that connect accepted product requirements and architecture to implementation work.

This baseline is a catalog and governance boundary. It does not itself authorize implementation.

The current AI-driven engineering tranche is authorized for normative definition by `CR-0003`, governed architecturally by accepted `ADR-0008`, and operationalized by accepted `EOS-AI-0001`.

## Governing sources

The AI-driven engineering specification tranche is governed by:

* `ADR-0006` — EOS Sovereignty and External SDLC Assimilation;
* `ADR-0008` — AI-Driven Engineering as the Default EOS Operating Model;
* `CR-0003` — Establish Monad AI-Driven Engineering Operating Model;
* `EOS-AI-0001` — AI-Driven Engineering Operating Model;
* `product/product-requirements.md`;
* `governance/authority.md`;
* `governance/canonical-state-model.md`;
* `governance/decision-process.md`;
* `governance/planning-engine.md`;
* `governance/policy-engine.md`;
* `governance/execution-engine.md`;
* the permanent EOS lifecycle contracts.

`ADR-0007` remains independently governed and Proposed. Specifications derived from or related to its Governed Execution Harness architecture do not become accepted merely by inclusion in this baseline.

## AI-driven engineering requirement ownership

The initial AIENG specification family refines the following committed product requirements:

* `FR-007` — bounded governed context;
* `FR-012` — memory, intelligence, and execution loop;
* `FR-013` — anti-hallucination engineering memory;
* `FR-014` — dependency-aware agent work;
* `FR-015` — progressive autonomy;
* `FR-016` — cross-harness review;
* `FR-023` — governance, change control, and audit;
* `FR-024` — operational health and execution observability;
* `FR-043` — Adaptive AI-Driven Engineering Workflow Planning;
* `QR-008` — progressive trust;
* `QR-010` — auditability.

The existing governed-execution requirements remain complementary:

* `FR-037` — Execution Envelope compilation;
* `FR-038` — fail-closed governed execution;
* `FR-039` — replaceable agent harness adapters;
* `FR-040` — independent completion verification;
* `FR-041` — recovery without loss of governing identity;
* `FR-042` — governed harness/model conformance evaluation.

## Required AIENG specifications

The initial normative AIENG tranche consists of:

| Specification    | Class      | Responsibility                                                                    | Initial status |
| ---------------- | ---------- | --------------------------------------------------------------------------------- | -------------- |
| `FUN-AIENG-0001` | Functional | Adaptive engineering pathway, clarification, replanning, and workflow progression | Draft          |
| `IFC-AIENG-0001` | Interface  | Provider-neutral engineering-agent interaction contract                           | Draft          |
| `SEC-AIENG-0001` | Security   | Autonomy, authority, delegation, approval, revocation, and fail-closed boundaries | Draft          |

These specifications refine one operating model. They MUST NOT create separate lifecycle, decision, approval, evidence, authority, or canonical-state systems.

## Relationship to governed execution specifications

The AIENG specifications operate upstream of and across the existing execution-governance boundary.

The intended composition is:

```text
governed intent
    ↓
FUN-AIENG-0001
adaptive pathway / clarification / decision routing
    ↓
EOSP + native authority/policy
    ↓
FR-037..FR-042 governed execution semantics
    ↓
replaceable executor / harness
    ↓
EOSV verification
    ↓
EOSR review
    ↓
EOSC / EOSL / EOSM as applicable
```

`TECH-HARNESS-0001` and `IFC-HARNESS-0001` are related execution-governance specifications and retain the status and architectural dependencies declared in their own artifacts.

## Specification invariants

Every AIENG specification MUST preserve these cross-family invariants:

1. EOS remains the sole engineering lifecycle/control plane.
2. `.eos/state/current.json` remains the sole current EOS operational authority.
3. AI initiative does not imply AI authority.
4. AI output does not become canonical merely through model confidence or consensus.
5. Human accountability and consequential authority remain explicit.
6. Adaptive workflow cannot bypass mandatory EOS gates.
7. Material ambiguity routes to native clarification, decision, approval, or change semantics.
8. Execution remains bounded by explicit authority and capability.
9. Governing-input drift can invalidate or suspend stale authorization.
10. Evidence controls acceptance.
11. Required review independence is policy-governed.
12. Raw transcripts and private chain-of-thought are noncanonical.
13. Model, provider, and harness identity are non-authoritative.
14. Autonomy is explicit, bounded, observable, attributable, policy-controlled, and revocable.
15. Existing Monad entities are reused unless a separately governed semantic gap is established.
16. Product-runtime implementation requires separately planned and authorized EOS work.

## Required conformance coverage

The AIENG specification family MUST collectively own verification for:

* `AIENG-CONF-A` — low-risk reversible change;
* `AIENG-CONF-B` — ambiguous product intent;
* `AIENG-CONF-C` — architecture change discovered during execution;
* `AIENG-CONF-D` — bounded autonomous Work Packet;
* `AIENG-CONF-E` — security-sensitive work;
* `AIENG-CONF-F` — independent review;
* `AIENG-CONF-G` — governing-input drift;
* `AIENG-CONF-H` — provider failure;
* `AIENG-CONF-I` — human denial;
* `AIENG-CONF-J` — evidence invalidates an assumption.

A later traceability review MUST demonstrate that every scenario has one or more normative specification owners and corresponding verification assets or explicitly planned verification assets.

## Traceability expectations

Every implementation Work Packet derived from this baseline MUST identify:

* governing requirement IDs;
* applicable specification IDs;
* applicable ADRs;
* applicable authority/policy constraints;
* acceptance criteria;
* required verification evidence;
* required review obligations.

Specifications MUST trace upward to requirements and architecture and downward to verification/conformance assets.

Missing traceability is a baseline defect, not permission to infer intent from implementation.

## Implementation authorization

This baseline does not authorize runtime implementation.

The sequence remains:

```text
accepted architecture
→ accepted operating model
→ requirements
→ specifications
→ traceability/conformance review
→ EOSP planning
→ separately authorized WC/WP
→ implementation
```

## Known Machine-Traceability Identity Gap

The human-authored product and specification conventions currently identify
requirements as `FR-*` / `QR-*` and specifications as class-specific
`FUN-*` / `IFC-*` / `SEC-*` identifiers.

The EOS canonical domain model currently defines canonical Requirement and
Specification entity namespaces as `REQ-*` and `SPEC-*`.

This mismatch does not invalidate the semantic requirement/specification
relationships established by this baseline, but it prevents this baseline from
claiming complete canonical machine-level REQ/SPEC identity coverage until the
namespace/convention relationship is explicitly reconciled.

The reconciliation MUST preserve existing human-authored identifiers and
history and MUST NOT silently renumber accepted requirements or specifications.

Resolution of this gap is required before the AIENG tranche claims complete
machine-level traceability or proceeds into implementation planning.
