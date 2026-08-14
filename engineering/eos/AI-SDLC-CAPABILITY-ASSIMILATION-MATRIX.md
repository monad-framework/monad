# AI-SDLC → Monad Capability Assimilation Matrix

**Status:** Proposed
**Date:** 2026-08-13
**Governing:** ADR-0006, CR-0001

Classification meanings:

- **Adopt** — concept fits Monad substantially as-is.
- **Adapt** — valuable concept, implemented with Monad-native semantics.
- **Interoperate** — retain as an external compatibility boundary.
- **Defer** — useful, but depends on earlier EOS capabilities.
- **Reject** — conflicts with Monad authority or architecture.

| AI-SDLC capability | Disposition | Monad destination | Notes |
| --- | --- | --- | --- |
| Deterministic Definition of Ready | Adapt | EOSP / policy gates | Strengthen with authority, staleness, graph, decision, and evidence checks. |
| Decision Catalog | Adapt | DEC/APR + canonical state | Preserve explicit authority; affected work may block while unrelated work continues. |
| Dependency graph composition | Adapt | DEP + semantic trace graph | Do not create a second dependency graph. |
| Pipeline orchestrator | Defer/Adapt | EOSE dispatch frontier | Implement after readiness, provenance, verification, and review are strong enough. |
| Worktree pooling | Adapt | EOSE | Build on existing isolated execution/worktree controls. |
| Agent roles | Adapt | EOSE/EOSR role profiles | Role is independent of any particular harness/provider. |
| Typed handoff contracts | Adopt/Adapt | execution/review contracts | Versioned structured payloads with validation and provenance. |
| Cross-harness review | Adapt | EOSR | Enforce independence through policy rather than convention. |
| QualityGate resources | Adapt | EOS policy/validators | Keep policy-as-code constrained and deterministic-first. |
| AutonomyPolicy | Adapt | EOS authority/risk/evidence policy | Use bounded permission envelopes rather than seniority labels. |
| AdapterBinding | Adopt/Adapt | integration registry | External tools remain replaceable adapters. |
| Proof of execution | Adapt | EXEC/EVID/REV/APR provenance | Prefer hashes/manifests; raw transcripts separately governed. |
| Emergent issue capture | Adapt | EOSC/EOSP capture flow | Route findings without silent scope expansion. |
| Exploration workstream | Adapt | EOSP readiness profiles | Different readiness contract; explicit budget and crystallization. |
| Operator TUI | Defer | EOS operator surface | Build after decision/frontier/evidence data models stabilize. |
| Conformance suite | Adopt | EOS conformance fixtures | Valid fixtures must pass; invalid fixtures must fail. |
| Cost governance | Defer | EOS governance/analytics | Add after execution identity and accounting are stable. |
| Compliance/audit reporting | Defer/Adapt | EOSV/EOSL/governance | Derive from canonical evidence and authority. |
| Zero-trust external PR verification | Defer/Adapt | EOSR/security | Requires isolated untrusted execution and explicit policy. |
| Progressive autonomy | Adapt | EOS risk/authority/evidence | Least autonomy; promote permissions only from evidence and explicit policy. |
| Signal ingestion / priority algorithms | Defer | product planning analytics | Useful later; must not replace product authority. |
| Kubernetes-style declarative resource envelope | Interoperate/Selective | adapters/schemas | Borrow versioning/spec-status ideas only where they improve Monad. |
| AI-SDLC task model | Reject as authority | WP/WC/PI remain canonical | Compatibility mapping may exist later. |
| AI-SDLC control-state directory | Reject | `.eos/` remains sole control plane | Parallel operational state is prohibited. |
| AI-SDLC dependency graph as authority | Reject | Monad graph remains canonical | Import/export only if needed. |
| AI-SDLC attestations as canonical evidence | Reject as replacement | EOS Evidence remains canonical | Selected proof techniques may be adapted. |
| AI-SDLC RFC system replacing Monad ADR/specs | Reject | Monad ADR/spec system | Concepts may inform process; authority remains Monad-native. |
| Direct codebase embedding | Reject by default | optional adapter later | Direct reuse requires explicit provenance/license handling. |

## Release placement

- EOS 0.9: DoR, Decision Catalog, operational DEC/APR/DEP.
- EOS 0.10: role/harness abstraction and typed handoffs.
- EOS 0.11: independent review.
- EOS 0.12: dispatch frontier and worker pool.
- EOS 0.13: failure/recovery playbook.
- EOS 0.14: proof-of-execution provenance.
- EOS 0.15: emergent capture and exploration.
- EOS 0.16: operator surface.
- EOS 0.17: conformance.
- EOS 0.18+: cost, compliance, zero-trust, advanced autonomy.
- Later: AI-SDLC compatibility adapter.
