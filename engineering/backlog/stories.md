# MVP Product Backlog Items

**Status:** Proposed backlog baseline  
**Scope:** all MVP Features have at least one Product Backlog Item; near-term items are refined more deeply than later forecast work.

A Product Backlog Item (PBI) is either a **User Story** when value is naturally observable at a user/operator boundary, or an **Enabler** when the work establishes architecture, semantics, security, quality, or infrastructure required by user-facing behavior. Enablers are not forced into artificial “As a user” phrasing.

Story points are provisional Fibonacci estimates used for comparative planning only. Sprint targets are forecasts until Sprint Planning.

## Refined transition and SPRINT-001 through SPRINT-003 PBIs

| PBI | Feature | Type | Target | Points | Outcome / story | Acceptance anchor |
| --- | --- | --- | --- | ---: | --- | --- |
| EN-002-01 | F-002-01 Deterministic canonical source discovery | Enabler | STAB-0001 | 3 | Define exactly which repository files are canonical inputs to machine projection. | Discovery is deterministic, excludes generated/secrets/dependency trees per policy, and produces the same ordered source set from the same tree. |
| EN-002-02 | F-002-02 Per-document machine companions | Enabler | STAB-0001 | 3 | Generate structured semantic companions for every discovered canonical text source. | Each companion records source path/hash, metadata, sections, identifiers, relations, and generator identity; missing companions fail verification. |
| EN-002-03 | F-002-03 Machine manifest and source-tree hash | Enabler | STAB-0001 | 3 | Produce an authoritative generated inventory of the canonical source set. | Manifest source count/tree hash match discovery; ordering is deterministic; source/companion hashes are verifiable. |
| EN-002-04 | F-002-04 Generated semantic graph | Enabler | STAB-0001 | 5 | Project current document/identifier relationships into a deterministic bootstrap graph. | Node/edge order is canonical, references resolve where supported, and graph source-tree hash matches the manifest. |
| EN-002-05 | F-002-05 Section retrieval corpus | Enabler | STAB-0001 | 3 | Produce independently ingestible section records for search/RAG/context navigation. | Corpus records have stable IDs, source hashes, section locations, identifiers, and related documents and are deterministically ordered. |
| EN-002-06 | F-002-06 Drift/orphan synchronization enforcement | Enabler | STAB-0001 | 3 | Prevent canonical and generated knowledge from silently diverging. | `sync-machine-docs.py --check` detects stale, missing, and orphaned outputs and passes after deterministic regeneration. |
| EN-007-05 | F-007-05 Machine drift diagnostics | Enabler | STAB-0001 | 5 | Make projection drift explicit enough for humans and CI to repair. | Check output distinguishes stale/missing/orphaned artifacts, returns non-zero on drift, and points to the regeneration command without mutating in check mode. |
| US-015-04 | F-015-04 GitHub Issues projection | User Story | STAB-0001 | 3 | As a maintainer, I want canonical backlog items projected into GitHub Issues so collaboration status does not require manually reconstructing the Git plan. | Issue projection is idempotent, traceable to canonical IDs, and does not create duplicate canonical work. |
| US-015-05 | F-015-05 GitHub Project fields/views/iterations | User Story | STAB-0001 | 3 | As a maintainer, I want one Project surface for roadmap, backlog, Sprint, blocked work, and release readiness views. | Field/view/iteration specification is complete and live configuration is evidenced where authorized; unavailable mutations are recorded, not claimed. |
| US-015-06 | F-015-06 GitHub Wiki projection | User Story | STAB-0001 | 3 | As a contributor, I want a navigable Wiki projection so operational/community guidance is easy to discover without moving canonical authority out of Git. | Wiki-source pages link back to canonical artifacts, state their projection status, and can be republished without manual content divergence. |
| EN-001-01 | F-001-01 Canonical product thesis | Enabler | SPRINT-001 | 3 | Establish one coherent definition of Monad as an Engineering Knowledge Compilation Platform. | README, idea, vision, requirements, capabilities, architecture context, and roadmap do not describe a materially different primary product. |
| EN-001-02 | F-001-02 Product Goal and MVP scope | Enabler | SPRINT-001 | 3 | Freeze the minimum Release 1 outcome without freezing later implementation detail. | MVP success/guardrails, explicit exclusions, reference scenarios, and release acceptance are reviewable and internally consistent. |
| EN-001-03 | F-001-03 Authority hierarchy and ADR consolidation | Enabler | SPRINT-001 | 3 | Establish one discoverable architecture-decision authority and precedence model. | `architecture/decisions/` is canonical, ADR index/status is correct, `.monad` references the same path, and no live competing ADR root remains. |
| EN-001-04 | F-001-04 Artifact lifecycle and criticality | Enabler | SPRINT-001 | 3 | Distinguish complete taxonomy from approved authority and sequence review by delivery need. | C0–C4 criticality, Draft→Approved lifecycle, generated/canonical rules, and promotion criteria are documented and used in readiness review. |
| EN-001-05 | F-001-05 Canonical terminology | Enabler | SPRINT-001 | 3 | Eliminate ambiguous use of core terms before semantic-model implementation. | Terms for Artifact, Knowledge, MSG, KIR, Entity, Relationship, Provenance, Diagnostic, Plan, Evidence, Work Packet, Sprint, and Increment are unambiguous or explicitly scoped. |
| EN-001-06 | F-001-06 Scrum/EOS operating model | Enabler | SPRINT-001 | 5 | Integrate Scrum value planning with Monad's stricter engineering-authority/evidence model. | Product Goal→Epic→Feature→PBI→Sprint and Milestone/PI/WP/ADR/spec relationships are explicit; no two constructs compete for the same authority. |
| EN-001-07 | F-001-07 Repository governance and branch strategy | Enabler | SPRINT-001 | 3 | Make GitHub/Git contribution and protected-change flow ready for implementation. | Branch naming, PR/evidence expectations, CODEOWNERS, required checks, merge strategy, dependency automation, and target branch/ruleset settings are documented/configured. |
| EN-013-01 | F-013-01 Repository-input threat model | Enabler | SPRINT-001 | 5 | Model repository content as untrusted input before parser/execution implementation. | Threat model covers paths/symlinks, malicious config, command injection, generated content, secret disclosure, dependency metadata, tool output, and agent-context poisoning with owned mitigations. |
| US-015-01 | F-015-01 Documentation source-of-truth architecture | User Story | SPRINT-001 | 3 | As a maintainer, I want generated docs and project views to remain disposable projections so editing a dashboard cannot silently change engineering truth. | Canonical/generated boundaries, publication ownership, cross-links, regeneration, versioning, and conflict handling are approved for MVP. |
| US-015-07 | F-015-07 Project status/traceability projection | User Story | SPRINT-001 | 3 | As a maintainer, I want project status to be derivable from canonical work/evidence rather than maintained independently in many tools. | Status surfaces identify their source records, freshness, and projection rules; conflicts resolve in favor of canonical governed artifacts. |
| US-003-01 | F-003-01 Workspace root discovery | User Story | SPRINT-002 | 3 | As a software engineer, I want Monad to locate the intended workspace consistently so I can inspect a repository without private setup knowledge. | Root discovery handles supported invocation locations, nested repositories, no-repository cases, ambiguity, and filesystem boundaries deterministically. |
| US-003-02 | F-003-02 Repository identity | User Story | SPRINT-002 | 5 | As a software engineer, I want a stable repository identity so semantic entities and evidence remain attributable across commands and clean recompilation. | Identity rules distinguish path/location from semantic repository identity, detect ambiguity/collision, and are serialized in inspect output. |
| US-003-03 | F-003-03 Monad configuration model | User Story | SPRINT-002 | 5 | As a software engineer, I want one explicit configuration model so I know which settings govern semantic compilation and execution. | Config source, schema, defaults, precedence, validation, unknown-key behavior, paths, and secret boundaries are specified and tested. |
| US-003-04 | F-003-04 Lock and local state model | User Story | SPRINT-002 | 5 | As a software engineer, I want resolved state separated from disposable local state so reproducibility is clear. | `monad.lock`/equivalent and `.monad/` responsibilities, persistence, generated state, invalidation, portability, and cleanup are explicitly separated and tested. |
| US-003-05 | F-003-05 Component/package discovery | User Story | SPRINT-002 | 3 | As a software engineer, I want Monad to identify supported project components/packages so later graph and execution planning can operate on meaningful boundaries. | Reference repositories discover expected components deterministically; unsupported/ambiguous layouts remain visible through diagnostics. |
| US-003-06 | F-003-06 Native toolchain discovery | User Story | SPRINT-002 | 3 | As a software engineer, I want Monad to identify relevant native tools and versions without executing arbitrary repository instructions. | Discovery reports supported tools/version evidence, differentiates missing/unsupported tools, and does not cross into execution authority. |
| EN-007-02 | F-007-02 Workspace/configuration diagnostics | Enabler | SPRINT-002 | 5 | Define actionable diagnostics for workspace/config errors before semantic compilation proceeds. | Stable codes cover root ambiguity, missing/invalid config, unsupported version, bad paths, duplicate component identity, and missing required tool metadata. |
| EN-004-01 | F-004-01 Semantic identity model | Enabler | SPRINT-003 | 5 | Establish stable identity namespaces and lifetimes for documents and core semantic entities. | Identity is independent of traversal order; namespace/scope/uniqueness rules and collision behavior are specified and property-tested. |
| EN-004-02 | F-004-02 Canonicalization rules | Enabler | SPRINT-003 | 3 | Define which representational differences do and do not change semantic identity. | Equivalent supported forms converge; meaning-changing input differs; normalization is versioned and testable. |
| EN-004-03 | F-004-03 Content and semantic hashing | Enabler | SPRINT-003 | 3 | Define fingerprints suitable for source integrity, semantic invalidation, and future cache decisions. | Hash inputs, canonicalization, algorithm/version tagging, collision handling, and test vectors are explicit. |
| EN-004-04 | F-004-04 Source coordinates | Enabler | SPRINT-003 | 3 | Preserve locations from semantic entities/diagnostics back to canonical source. | Supported artifacts map semantic objects to stable path plus line/section/range coordinates sufficient for explanation and diagnostics. |
| EN-004-05 | F-004-05 Provenance model | Enabler | SPRINT-003 | 5 | Make every derived semantic claim attributable to source and transformation. | Provenance records source identity/hash, adapter/extractor/version, relevant coordinate, derivation class, and lineage needed for explanation/invalidation. |
| EN-004-06 | F-004-06 Alias/rename/collision handling | Enabler | SPRINT-003 | 3 | Prevent renames and identifier conflicts from silently corrupting semantic history. | Supported rename/alias behavior preserves lineage; collisions and ambiguous aliases produce blocking diagnostics instead of arbitrary merges. |
| EN-007-01 | F-007-01 Diagnostic model and registry | Enabler | SPRINT-003 | 5 | Establish one structured diagnostic contract for deterministic core failures/findings. | Diagnostic schema includes stable code, severity, message, entity/source, provenance/cause, remediation, structured details, and deterministic ordering. |
| EN-007-03 | F-007-03 Identity/provenance diagnostics | Enabler | SPRINT-003 | 5 | Surface identity/canonicalization/provenance defects with enough context to repair them. | Duplicate/colliding IDs, invalid namespace, unresolved alias, bad source coordinate, and incomplete required provenance have stable negative fixtures. |
| EN-014-01 | F-014-01 Semantic unit/property tests | Enabler | SPRINT-003 | 3 | Establish property-based/unit evidence for the semantic kernel before graph breadth increases. | Identity/canonicalization/hash/provenance invariants are tested across deterministic examples and generated edge cases appropriate to the chosen language/tooling. |

## Forecast MVP PBIs — SPRINT-004 through SPRINT-014

These PBIs are intentionally less detailed than the near-term refinement horizon. Each must be refined against then-current specifications/ADRs before Sprint commitment.

| PBI | Feature | Type | Forecast | Points | Refinement state |
| --- | --- | --- | --- | ---: | --- |
| EN-005-01 | F-005-01 Core ontology | Enabler | SPRINT-004 | 3 | Planned |
| EN-005-02 | F-005-02 Node/entity taxonomy | Enabler | SPRINT-004 | 3 | Planned |
| EN-005-03 | F-005-03 Relationship/edge taxonomy | Enabler | SPRINT-004 | 3 | Planned |
| EN-005-04 | F-005-04 Deterministic graph construction | Enabler | SPRINT-004 | 8 | Planned |
| EN-005-05 | F-005-05 Graph invariants and validation | Enabler | SPRINT-004 | 5 | Planned |
| EN-005-06 | F-005-06 Canonical graph snapshot/serialization | Enabler | SPRINT-004 | 5 | Planned |
| EN-005-07 | F-005-07 Graph traversal/indexes | Enabler | SPRINT-004 | 5 | Planned |
| EN-006-01 | F-006-01 KIR charter and semantic boundary | Enabler | SPRINT-005 | 3 | Planned |
| EN-006-02 | F-006-02 KIR schema | Enabler | SPRINT-005 | 5 | Planned |
| EN-006-03 | F-006-03 Canonical KIR serialization | Enabler | SPRINT-005 | 3 | Planned |
| EN-006-04 | F-006-04 MSG-to-KIR lowering | Enabler | SPRINT-005 | 8 | Planned |
| EN-006-05 | F-006-05 KIR validation/conformance | Enabler | SPRINT-005 | 3 | Planned |
| EN-006-06 | F-006-06 KIR versioning/compatibility/migrations | Enabler | SPRINT-005 | 5 | Planned |
| EN-007-04 | F-007-04 Semantic graph diagnostics | Enabler | SPRINT-004 | 5 | Planned |
| US-008-01 | F-008-01 Entity inspect/lookup | User Story | SPRINT-006 | 3 | Planned |
| US-008-02 | F-008-02 Relationship query/traversal | User Story | SPRINT-006 | 5 | Planned |
| US-008-03 | F-008-03 Why/provenance explanation | User Story | SPRINT-006 | 5 | Planned |
| US-008-04 | F-008-04 Coverage and gap queries | User Story | SPRINT-006 | 3 | Planned |
| US-008-05 | F-008-05 Structured query output | User Story | SPRINT-006 | 5 | Planned |
| US-008-06 | F-008-06 Search/navigation indexes | User Story | SPRINT-006 | 3 | Planned |
| US-009-01 | F-009-01 Git/repository change ingestion | User Story | SPRINT-006 | 3 | Planned |
| US-009-02 | F-009-02 Semantic affected-set calculation | User Story | SPRINT-006 | 8 | Planned |
| US-009-03 | F-009-03 Impact-path explanation | User Story | SPRINT-007 | 5 | Planned |
| US-009-06 | F-009-06 Conservative uncertainty/fallback | User Story | SPRINT-007 | 3 | Planned |
| US-009-04 | F-009-04 Incremental graph invalidation/update | User Story | SPRINT-008 | 5 | Planned |
| US-009-05 | F-009-05 Fingerprints and cache validity | User Story | SPRINT-008 | 3 | Planned |
| US-010-01 | F-010-01 Execution-plan schema | User Story | SPRINT-008 | 5 | Planned |
| US-010-02 | F-010-02 Plan construction | User Story | SPRINT-008 | 8 | Planned |
| EN-013-02 | F-013-02 Authority/policy evaluator | Enabler | SPRINT-008 | 5 | Planned |
| EN-007-06 | F-007-06 Execution/native-tool diagnostics | Enabler | SPRINT-009 | 5 | Planned |
| US-010-03 | F-010-03 Native-tool adapter contract | User Story | SPRINT-009 | 5 | Planned |
| US-010-04 | F-010-04 Local execution runtime | User Story | SPRINT-009 | 8 | Planned |
| US-010-05 | F-010-05 Parallelism/cancellation/failure propagation | User Story | SPRINT-009 | 3 | Planned |
| US-010-06 | F-010-06 Verified cache | User Story | SPRINT-009 | 3 | Planned |
| US-010-07 | F-010-07 Execution evidence/provenance | User Story | SPRINT-009 | 5 | Planned |
| US-011-01 | F-011-01 CLI information architecture | User Story | SPRINT-010 | 3 | Planned |
| US-011-02 | F-011-02 inspect/validate/graph commands | User Story | SPRINT-010 | 5 | Planned |
| US-011-03 | F-011-03 query/explain/affected commands | User Story | SPRINT-010 | 5 | Planned |
| US-011-04 | F-011-04 context/plan/run commands | User Story | SPRINT-010 | 5 | Planned |
| US-011-05 | F-011-05 doctor/version/init workflow | User Story | SPRINT-010 | 3 | Planned |
| US-011-06 | F-011-06 Text/JSON/structured output contracts | User Story | SPRINT-010 | 3 | Planned |
| US-011-07 | F-011-07 Shell completion and first-run guidance | User Story | SPRINT-010 | 3 | Planned |
| US-012-01 | F-012-01 Agent identity/capability model | User Story | SPRINT-010 | 5 | Planned |
| US-012-02 | F-012-02 Task and Work Packet contract | User Story | SPRINT-010 | 3 | Planned |
| US-012-03 | F-012-03 Semantic context selection/minimization | User Story | SPRINT-010 | 5 | Planned |
| US-012-04 | F-012-04 Context package schema | User Story | SPRINT-010 | 5 | Planned |
| US-012-05 | F-012-05 Codex context/export workflow | User Story | SPRINT-010 | 5 | Planned |
| US-012-06 | F-012-06 AI provenance/audit/evaluation safeguards | User Story | SPRINT-010 | 5 | Planned |
| EN-013-03 | F-013-03 Secrets and sensitive-data boundaries | Enabler | SPRINT-010 | 3 | Planned |
| EN-013-04 | F-013-04 Agent/tool least privilege | Enabler | SPRINT-010 | 3 | Planned |
| EN-014-03 | F-014-03 Determinism/reproducibility suite | Enabler | SPRINT-011 | 8 | Planned |
| EN-014-04 | F-014-04 Integration/E2E reference repositories | Enabler | SPRINT-011 | 8 | Planned |
| EN-013-05 | F-013-05 Supply-chain/dependency controls | Enabler | SPRINT-012 | 3 | Planned |
| EN-013-06 | F-013-06 Security review and exception model | Enabler | SPRINT-012 | 5 | Planned |
| EN-014-05 | F-014-05 Performance benchmark suite | Enabler | SPRINT-012 | 3 | Planned |
| EN-014-06 | F-014-06 Security/fuzz/negative testing | Enabler | SPRINT-012 | 5 | Planned |
| EN-014-07 | F-014-07 Compatibility/migration tests | Enabler | SPRINT-012 | 5 | Planned |
| US-016-01 | F-016-01 Packaging and installation | User Story | SPRINT-012 | 3 | Planned |
| US-016-02 | F-016-02 Versioning/compatibility policy | User Story | SPRINT-012 | 5 | Planned |
| US-015-02 | F-015-02 Generated documentation/publication | User Story | SPRINT-013 | 3 | Planned |
| US-015-03 | F-015-03 Documentation search/navigation | User Story | SPRINT-013 | 3 | Planned |
| US-016-03 | F-016-03 Release CI/provenance/SBOM/signing | User Story | SPRINT-013 | 5 | Planned |
| US-016-04 | F-016-04 Monad-on-Monad dogfooding | User Story | SPRINT-013 | 3 | Planned |
| US-016-05 | F-016-05 Release documentation/changelog | User Story | SPRINT-013 | 3 | Planned |
| US-016-06 | F-016-06 Release readiness/rollback/support | User Story | SPRINT-014 | 3 | Planned |
| US-016-07 | F-016-07 MVP Release 1 publication | User Story | SPRINT-014 | 3 | Planned |

## Refinement requirement for forecast PBIs

Before a forecast PBI enters a Sprint it must gain explicit user/engineering outcome, governing requirement/specification/ADR links, dependencies, acceptance criteria including negative/boundary behavior, security/compatibility implications, estimate confirmation, and a Work Packet when implementation is consequential enough to require formal engineering authorization.
