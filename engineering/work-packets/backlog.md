# Work Packet Backlog and Release Map

**Status:** Proposed delivery baseline

The backlog below forecasts formal engineering packets through MVP Release 1. Forecast packets do not authorize implementation. A packet becomes Ready only after its scope, governing authority, dependencies, acceptance, validation, and risks satisfy `engineering/definition-of-ready.md`.

| Order | Work Packet | Target | State | Outcome |
| ---: | --- | --- | --- | --- |
| 1 | WP-STAB-0008 | STAB-0001 | Planned | Reconcile minimum C1 semantic-kernel architecture/specification authority. |
| 2 | WP-STAB-0007 | STAB-0001 | Planned | Stabilization readiness review and transition decision. |
| 3 | WP-FND-0001 | SPRINT-001 | Draft | C0 foundation acceptance and Product Goal baseline. |
| 4 | WP-ARCH-0001 | SPRINT-001 | Draft | First-slice architecture decision set and semantic-kernel responsibility review. |
| 5 | WP-SPEC-0001 | SPRINT-001 | Draft | First-slice specification pack for workspace/configuration/identity/provenance/diagnostics. |
| 6 | WP-SEC-0001 | SPRINT-001 | Draft | Repository-input threat model and first-slice security obligations. |
| 7 | WP-GH-0001 | SPRINT-001 | Draft | Protected GitHub operating/repository quality baseline. |
| 8 | WP-WS-0001 | SPRINT-002 | Draft | Workspace root discovery and repository identity. |
| 9 | WP-CONF-0001 | SPRINT-002 | Draft | Monad configuration plus lock/local-state boundary. |
| 10 | WP-DISC-0001 | SPRINT-002 | Draft | Component/package/artifact/toolchain discovery adapter slice. |
| 11 | WP-DIAG-0001 | SPRINT-002 | Draft | Workspace/configuration diagnostic family. |
| 12 | WP-ID-0001 | SPRINT-003 | Forecast | Stable semantic identity and canonicalization. |
| 13 | WP-PROV-0001 | SPRINT-003 | Forecast | Source coordinates and provenance model/implementation. |
| 14 | WP-HASH-0001 | SPRINT-003 | Forecast | Content/semantic hashing plus alias/rename/collision handling. |
| 15 | WP-DIAG-0002 | SPRINT-003 | Forecast | Common diagnostic registry plus identity/provenance diagnostics. |
| 16 | WP-TEST-0001 | SPRINT-003 | Forecast | Semantic unit/property tests for identity/provenance foundation. |
| 17 | WP-MSG-0001 | SPRINT-004 | Forecast | Core ontology, entity and relationship taxonomy. |
| 18 | WP-MSG-0002 | SPRINT-004 | Forecast | Deterministic graph construction, invariants, snapshot, traversal. |
| 19 | WP-KIR-0001 | SPRINT-005 | Forecast | KIR charter/schema/canonical serialization and MSG lowering. |
| 20 | WP-KIR-0002 | SPRINT-005 | Forecast | KIR validation, conformance, versioning, compatibility, migration baseline. |
| 21 | WP-QUERY-0001 | SPRINT-006 | Forecast | Entity/relationship query, provenance explanation, structured output. |
| 22 | WP-IMPACT-0001 | SPRINT-006 | Forecast | Git change ingestion and first conservative semantic affected set. |
| 23 | WP-DIAG-0003 | SPRINT-007 | Forecast | Impact-path explanation, uncertainty behavior, diagnostic hardening. |
| 24 | WP-INCR-0001 | SPRINT-008 | Forecast | Incremental invalidation/update, fingerprints and cache-validity semantics. |
| 25 | WP-PLAN-0001 | SPRINT-008 | Forecast | Execution-plan schema, deterministic planner and authority/policy first slice. |
| 26 | WP-EXEC-0001 | SPRINT-009 | Forecast | Native-tool adapter, local runtime, failure/cancellation, evidence and verified cache slice. |
| 27 | WP-CLI-0001 | SPRINT-010 | Forecast | Integrated Release 1 CLI and structured-output contracts. |
| 28 | WP-AGENT-0001 | SPRINT-010 | Forecast | Agent task contract, semantic context package, Codex export, capability/privacy boundaries. |
| 29 | WP-CONF-0002 | SPRINT-011 | Forecast | Determinism/reproducibility and integrated reference-repository conformance suite. |
| 30 | WP-SEC-0002 | SPRINT-012 | Forecast | Security/fuzz/supply-chain/performance/compatibility hardening evidence. |
| 31 | WP-REL-0001 | SPRINT-012 | Forecast | Packaging, installation, versioning and compatibility baseline. |
| 32 | WP-DOG-0001 | SPRINT-013 | Forecast | Monad-on-Monad dogfooding, generated documentation, beta and gap closure. |
| 33 | WP-REL-0002 | SPRINT-013/014 | Forecast | Release CI/provenance/SBOM/signing, documentation, readiness, rollback and Release 1 publication. |

## Readiness progression

- `Draft`: packet exists to support refinement but may still depend on unresolved authority.
- `Forecast`: only outcome/sequence is currently reliable; details must be derived later.
- `Ready`: all Definition of Ready conditions and required authority are satisfied.
- `Active`: explicitly pulled for execution.
- `Review`: implementation complete enough for acceptance review.
- `Done`: accepted evidence satisfies Definition of Done and closure is recorded.
- `Blocked`: execution cannot safely proceed; blocker/owner/next action are explicit.

## Critical path

```text
STAB C0/C1 reconciliation
  ↓
Workspace/configuration
  ↓
Identity + provenance
  ↓
Semantic graph
  ↓
KIR
  ↓
Query + affected set
  ↓
Incrementality + planner
  ↓
Native execution
  ↓
CLI + agent context
  ↓
Integrated conformance
  ↓
Security/performance/packaging
  ↓
Dogfood + release readiness
  ↓
MVP Release 1
```

Work outside this path may run in parallel when it does not consume unresolved semantics or increase integration risk.
