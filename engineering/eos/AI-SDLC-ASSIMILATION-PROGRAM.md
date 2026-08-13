# AI-SDLC Capability Assimilation Program

**Status:** Proposed  
**Date:** 2026-08-13  
**Target:** EOS evolution beginning with 0.9  
**Governing decision:** ADR-0006 (Accepted)

## Purpose

Define the controlled program by which Monad may absorb high-value concepts from `ai-sdlc-framework/ai-sdlc` without importing a competing lifecycle/control plane or disturbing the authorized Monad MVP product implementation stream.

This program is architecture and EOS evolution. It is not authorization to implement product-runtime features, run autonomous workers, change current canonical operational state manually, or copy external source code without provenance/license review.

## Program thesis

AI-assisted execution becomes dependable only when the work contract is sufficiently decided, bounded, authorized, independently verifiable, and recoverable. Monad already owns the canonical engineering knowledge, semantic graph, authority model, lifecycle, and evidence model needed to make that premise stronger than a standalone pipeline framework can.

The program therefore follows this composition:

```text
canonical engineering knowledge
          |
          v
  Monad semantic graph
          |
     +----+----+
     |         |
    EOSP   decision/readiness
     |         |
     +----+----+
          v
         EOSE
          |
   role/harness adapters
          |
         EOSV
          |
         EOSR
          |
      EOSC/EOSL
          |
         EOSM
```

## Non-negotiable invariants

1. **One control plane.** EOS is the only repository lifecycle/control plane.
2. **One canonical current operational state.** New operational entities must enter `.eos/state/current.json` through the canonical transaction model, not through parallel stores or hand-edited projections.
3. **Canonical artifacts remain authoritative.** GitHub, generated machine representations, external frameworks, model output, and caches remain projections, evidence, or integrations unless governance explicitly changes their role.
4. **Human sovereignty is preserved.** Automation may recommend, route, enforce, and execute delegated actions; it does not silently acquire authority over material risk, architecture, strategy, irreversible action, or governance override.
5. **Deterministic-first evaluation.** Regex/schema/graph/policy checks run before semantic or LLM evaluation whenever possible.
6. **Bounded execution.** Every mutable execution is tied to an authorized unit of work, governed inputs, allowed scope, an isolated worktree/branch, and a recorded execution identity.
7. **Independent verification/review.** Agent self-report is evidence input, never sole proof. Policy may require reviewer independence from the implementing harness/model family.
8. **Unrelated work remains dispatchable.** A decision or dependency blocks only the work whose graph says it is affected.
9. **MVP product continuity.** Existing MVP ADRs, PI/WC/WP contracts, and Rust topology are not reopened merely because EOS is evolving.
10. **Conceptual assimilation before direct reuse.** Direct copying of external code or substantial documentation requires explicit provenance and license handling.

## Workstreams

### Workstream A — Decision and Readiness

Goal: mechanically prove that a Work Packet is safe and sufficiently decided before authorization/execution.

Capabilities:

- operational Decision and Approval entities;
- decision closure and authority routing;
- richer dependency semantics;
- deterministic unresolved-marker and reference checks;
- authority/lifecycle/staleness-aware governing-reference validation;
- acceptance-criterion testability checks;
- execution-surface and verification-contract checks;
- explainable readiness reports;
- semantic/LLM checks only as explicitly declared secondary evidence.

Target release: **EOS 0.9**.

### Workstream B — Execution Role and Harness Abstraction

Goal: make EOSE execution depend on a role/capability contract rather than a hard-coded provider name.

Capabilities:

- executor/reviewer role profiles;
- harness identity and capability model;
- allowed tools and environment permissions;
- generic `execute` surface with compatibility aliases;
- structured handoff contracts;
- harness/model/version provenance.

Target release: **EOS 0.10**.

### Workstream C — Independent Review

Goal: enforce independent code/test/security review where policy requires it.

Capabilities:

- reviewer identity and harness provenance;
- independence policy dimensions;
- structured findings/severity/disposition;
- review aggregation;
- acceptance conditioned on review/evidence policy.

Target release: **EOS 0.11**.

### Workstream D — Autonomous Dispatch

Goal: safely select and execute only work whose canonical state and graph make it dispatchable.

Capabilities:

- dispatch frontier;
- dependency/decision/risk filtering;
- bounded worker pool;
- leases/claims;
- worktree allocation;
- concurrency limits;
- resumable worker state;
- quarantine.

Target release: **EOS 0.12**.

### Workstream E — Failure and Recovery

Goal: make known execution failures deterministic operational states with prescribed remediation.

Capabilities:

- failure taxonomy;
- retry budgets;
- stale-contract handling;
- rebase/conflict policy;
- verification-failure handling;
- reviewer rejection flow;
- environment failure handling;
- quarantine and human escalation.

Target release: **EOS 0.13**.

### Workstream F — Proof of Execution

Goal: strengthen evidence that an execution and its reviews occurred against the claimed contract and source state.

Capabilities:

- execution provenance graph;
- contract/governing/baseline hashes;
- reviewer work-product/transcript hashes;
- evidence bundle manifests;
- optional Merkle anchoring;
- configurable retention for raw transcripts rather than mandatory repository commits.

Target release: **EOS 0.14**.

### Workstream G — Emergent Work and Exploration

Goal: capture unknown work without scope creep and distinguish delivery from intentional discovery.

Capabilities:

- `eos capture` finding records;
- deterministic triage destinations;
- scope-extension through EOSC rather than silent implementation;
- exploration/investigation readiness profiles;
- explicit budgets, success criteria, exclusions, and crystallization;
- outputs that may include EVID, DEC, ADR, SPEC, CR, and new WP records.

Target release: **EOS 0.15**.

### Workstream H — Operator Surface

Goal: expose the information a human decision steward needs without forcing repository spelunking.

Capabilities:

- decisions queue;
- readiness/blocker explanations;
- dispatch frontier;
- semantic impact;
- execution/worker status;
- review/evidence status;
- risk/autonomy posture;
- cost and quality signals.

Target release: **EOS 0.16**.

### Workstream I — Conformance

Goal: make EOS contracts implementation- and adapter-testable.

Capabilities:

- core lifecycle fixtures;
- readiness fixtures;
- canonical-state fixtures;
- execution/verification/review fixtures;
- adapter fixtures;
- valid cases that must pass and invalid cases that must fail;
- declared conformance levels.

Target release: **EOS 0.17**.

### Workstream J — Advanced Governance and Interoperability

Goal: add higher-order operational controls only after the core loop is proven.

Capabilities:

- cost attribution/budgets;
- compliance reporting;
- zero-trust untrusted-contributor verification;
- evidence-calibrated autonomy;
- quality monitoring and calibration;
- signal ingestion and prioritization extensions;
- optional AI-SDLC import/export adapter.

Target: **EOS 0.18+ and later interoperability tranche**.

## Program release map

| Release | Theme | Exit condition |
| --- | --- | --- |
| EOS 0.9 | Decision & Readiness Engine | readiness is explainable, decision-aware, dependency-aware, authority-aware, and canonical-state safe |
| EOS 0.10 | Harness abstraction | execution role is decoupled from a specific harness and provenance is recorded |
| EOS 0.11 | Independent review | policy can require and prove reviewer independence |
| EOS 0.12 | Dispatch frontier | only canonically dispatchable work can be claimed by bounded workers |
| EOS 0.13 | Failure/recovery | known failures have deterministic transitions and remediation |
| EOS 0.14 | Proof of execution | execution/review/evidence claims are cryptographically linked |
| EOS 0.15 | Emergent/exploration | findings are captured without scope creep and exploration has bounded semantics |
| EOS 0.16 | Operator surface | decisions, blockers, frontier, evidence, and alerts are visible coherently |
| EOS 0.17 | Conformance | contracts can be tested language-/adapter-independently |
| EOS 0.18+ | Advanced controls | cost/compliance/zero-trust/autonomy controls are evidence-backed |
| later | AI-SDLC bridge | import/export does not create competing authority |

Release numbers are planning targets until individually authorized; they are not retroactive claims that those releases already exist.

## Coexistence with Monad MVP Release 1

The assimilation program and product MVP are parallel workstreams.

```text
Product delivery                   EOS evolution
----------------                   -------------
PI-MVP-001                         EOS 0.9
WC-MVP-0001                        EOS 0.10
WP-MVP-0001...                     EOS 0.11...
Rust monad-core/monad-cli          repository engineering control plane
```

Rules:

- EOS changes must not broaden an MVP WP's authorized source boundary.
- Product WPs use the EOS version actually merged and authorized at execution time.
- A later EOS improvement may strengthen gates for future authorization, but must not falsify historical evidence or silently rewrite completed lifecycle events.
- If an EOS change materially invalidates a currently authorized execution contract, the contract must be explicitly invalidated/reissued through governed process rather than silently changed.

## Governance path

The program itself is not implementation authorization.

Before code/state mutation for each tranche:

1. governing ADR(s) are Accepted where required;
2. the tranche has a bounded specification/design;
3. affected canonical-state/schema migration is explicit;
4. the tranche is represented by authorized EOS planning entities;
5. allowed implementation paths and validation commands are explicit;
6. verification and review evidence are required before closure.

A formal ChangeRequest should be created through EOS when the current CLI/canonical-state path supports doing so without manual projection edits. Until then this program document and ADR-0006 remain proposal/design authority only.

## Licensing and provenance

The external AI-SDLC repository is Apache-2.0 licensed. Monad is MIT licensed. This program prefers independent Monad-native implementation of general concepts and patterns. If code, schemas, or substantial textual material are copied or adapted directly, the specific change must record provenance and satisfy applicable license/NOTICE/attribution obligations before merge.

## Success criteria

The assimilation program succeeds when Monad can:

- tell an operator exactly why work is or is not ready;
- surface unresolved load-bearing decisions before execution;
- continue unrelated work while a specific decision is blocked;
- execute through interchangeable bounded harnesses;
- enforce independent review;
- dispatch multiple authorized packets safely according to dependencies and policy;
- recover deterministically from known execution failures;
- prove the relationship among contract, source state, execution, review, evidence, and approval;
- capture emergent findings without unauthorized scope growth;
- support bounded exploration without pretending uncertainty is resolved;
- expose all of this through coherent operator and conformance surfaces;
- interoperate with AI-SDLC later without making AI-SDLC canonical.

## Source material

Primary design donor: `https://github.com/ai-sdlc-framework/ai-sdlc`, including its vision, DoR, orchestration, decision-catalog, cross-harness review, proof-of-execution, emergent-work, exploration, autonomy, declarative-resource, and conformance designs as inspected in August 2026.
