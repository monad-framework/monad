# Near-Term Task Registry

**Status:** Active planning baseline  
**Task horizon:** STAB-0001 through SPRINT-003

Tasks are decomposed only near execution. Later Sprints remain at Story/Enabler and Work Packet level until refinement supplies sufficient evidence. A task is normally one focused human/Codex execution unit with a verifiable result.

## STAB-0001 — Foundation stabilization tasks

| Task | Parent | State | Result / evidence |
| --- | --- | --- | --- |
| T-STAB-001 | WP-STAB-0001 | Review | Reconcile root README, idea, vision, requirements, capabilities, roadmap, architecture context, engineering plan, and success criteria around the Engineering Knowledge Compilation thesis. |
| T-STAB-002 | WP-STAB-0002 | Review | Consolidate ADR-0001 under `architecture/decisions/`, remove competing live ADR path, update `.monad` and decision index. |
| T-STAB-003 | WP-STAB-0003 | Review | Add deterministic artifact-system materializer that never overwrites authored non-empty files by default. |
| T-STAB-004 | WP-STAB-0003 | Review | Populate all empty `artifact-system/**/*.md` files with substantive Draft baselines. |
| T-STAB-005 | WP-STAB-0004 | Review | Regenerate machine document companions, manifest, graph, and corpus against the complete canonical tree. |
| T-STAB-006 | WP-STAB-0004 | Review | Verify zero machine drift with `sync-machine-docs.py --check` and preserve CI enforcement. |
| T-STAB-007 | WP-STAB-0005 | Active | Create complete Epic registry and forecast all MVP/post-MVP/Future Epics. |
| T-STAB-008 | WP-STAB-0005 | Active | Create complete Feature registry and schedule every MVP Feature to a forecast Sprint. |
| T-STAB-009 | WP-STAB-0005 | Active | Create MVP Story/Enabler registry, estimates, refinement state, and near-term acceptance anchors. |
| T-STAB-010 | WP-STAB-0005 | Active | Create Sprint, PI, Milestone, Work Packet, ordered-backlog, and near-term Task records. |
| T-STAB-011 | WP-STAB-0006 | Active | Establish GitHub labels, milestones, Issue Forms, issue projection, Project configuration contract, Wiki source, repository settings target, and automation plan. |
| T-STAB-012 | WP-STAB-0006 | Planned | Project Epics and refinement-horizon Features/PBIs into live GitHub Issues idempotently. |
| T-STAB-013 | WP-STAB-0006 | Planned | Populate or prepare Wiki projection and record any GitHub permission boundary that prevents live publication. |
| T-STAB-014 | WP-STAB-0006 | Planned | Define required branch/ruleset/Actions/dependency/security settings and verify current repository configuration against the target. |
| T-STAB-015 | WP-STAB-0007 | Planned | Run C0 product/authority consistency review and record unresolved decisions/conditions. |
| T-STAB-016 | WP-STAB-0008 | Planned | Review C1 semantic-kernel Drafts and identify the minimum ADR/specification set required by SPRINT-002 implementation. |
| T-STAB-017 | WP-STAB-0007 | Planned | Run final artifact/machine/GitHub/backlog/CI readiness checks and record Proceed / Proceed with Conditions / Do Not Proceed. |

## SPRINT-001 — Stabilized foundation tasks

| Task | Parent | State | Result / evidence |
| --- | --- | --- | --- |
| T-001-001 | WP-FND-0001 | Planned | Compare C0 foundation documents for contradictory product definitions, terminology, scope, and authority. |
| T-001-002 | WP-FND-0001 | Planned | Resolve or record every blocking C0 finding and prepare foundation acceptance review. |
| T-001-003 | WP-FND-0001 | Planned | Establish Product Goal and Release 1 scope as the backlog commitment baseline. |
| T-001-004 | WP-ARCH-0001 | Planned | Review five-plane architecture, semantic pipeline, domain boundaries, deterministic/AI boundary, and local-first deployment model. |
| T-001-005 | WP-ARCH-0001 | Planned | Enumerate first-slice architectural decisions and classify each as Accepted, Proposed ADR required, or implementation-local. |
| T-001-006 | WP-ARCH-0001 | Planned | Reconcile ADR-0001 with current Knowledge Plane/MKE/MSG/KIR responsibilities and create superseding ADR proposal only if necessary. |
| T-001-007 | WP-SPEC-0001 | Planned | Define the initial specification registry/IDs for workspace, identity/provenance, graph, diagnostics, and configuration contracts. |
| T-001-008 | WP-SPEC-0001 | Planned | Produce or promote the minimum SPRINT-002 specifications to Review/Approved status with verification anchors. |
| T-001-009 | WP-SEC-0001 | Planned | Complete repository-input threat-model review including symlink/path, malicious config, command/context injection, secrets, and tool output. |
| T-001-010 | WP-SEC-0001 | Planned | Map MVP security controls to first-slice design/test obligations and identify blocking security ADR/spec needs. |
| T-001-011 | WP-GH-0001 | Planned | Verify Issue/PR templates, CODEOWNERS, labels, milestones, Project schema, Wiki source, and repository settings targets against the new backlog model. |
| T-001-012 | WP-GH-0001 | Planned | Establish required-check/ruleset target for `main` and document any settings requiring organization-owner/UI action. |
| T-001-013 | WP-GH-0001 | Planned | Establish dependency update and Actions pinning/security policy appropriate to the implementation stack selected by accepted ADR. |
| T-001-014 | WP-FND-0001 | Planned | Re-run artifact materialization and machine synchronization after all accepted foundation edits. |
| T-001-015 | WP-FND-0001 | Planned | Conduct SPRINT-001 Review/Retrospective and refine SPRINT-002/003 backlog from evidence. |

## SPRINT-002 — Workspace and artifact intelligence tasks

| Task | Parent | State | Result / evidence |
| --- | --- | --- | --- |
| T-002-001 | WP-WS-0001 | Planned | Create reference repository fixtures covering root invocation, nested directories, multiple markers, no repository, and unsupported layouts. |
| T-002-002 | WP-WS-0001 | Planned | Implement deterministic workspace-root discovery under the accepted language/runtime architecture. |
| T-002-003 | WP-WS-0001 | Planned | Implement repository identity and inspectable identity output. |
| T-002-004 | WP-CONF-0001 | Planned | Implement the minimum versioned Monad configuration schema and parser. |
| T-002-005 | WP-CONF-0001 | Planned | Implement configuration precedence/defaults/path normalization and unknown/invalid key diagnostics. |
| T-002-006 | WP-CONF-0001 | Planned | Implement the first lock/resolved-state and disposable local-state boundary or explicitly defer lockfile creation with accepted rationale. |
| T-002-007 | WP-DISC-0001 | Planned | Define adapter interface for deterministic artifact/component discovery without execution side effects. |
| T-002-008 | WP-DISC-0001 | Planned | Implement component/package discovery for the first reference ecosystems. |
| T-002-009 | WP-DISC-0001 | Planned | Implement native toolchain discovery/version evidence without executing repository-declared arbitrary commands. |
| T-002-010 | WP-DIAG-0001 | Planned | Implement stable workspace/config diagnostic codes and structured representation. |
| T-002-011 | WP-DIAG-0001 | Planned | Add positive, negative, ambiguity, symlink/path-boundary, and unsupported-layout tests. |
| T-002-012 | WP-WS-0001 | Planned | Demonstrate `monad inspect` or internal equivalent over reference repositories and record Sprint acceptance evidence. |

## SPRINT-003 — Semantic identity and provenance tasks

| Task | Parent | State | Result / evidence |
| --- | --- | --- | --- |
| T-003-001 | WP-ID-0001 | Planned | Define stable namespaces/lifetimes for documents, components, specifications, decisions, tests, work, and derived semantic entities used in the first graph slice. |
| T-003-002 | WP-ID-0001 | Planned | Implement versioned canonicalization primitives and deterministic identity construction. |
| T-003-003 | WP-HASH-0001 | Planned | Implement content/source hashing with algorithm/version tagging and deterministic test vectors. |
| T-003-004 | WP-HASH-0001 | Planned | Implement semantic fingerprint inputs required by identity/invalidation without prematurely defining execution-cache semantics. |
| T-003-005 | WP-PROV-0001 | Planned | Implement source-coordinate representation for supported Markdown/config/code metadata adapters. |
| T-003-006 | WP-PROV-0001 | Planned | Implement provenance record carrying source hash, adapter/extractor/version, coordinate, and derivation class. |
| T-003-007 | WP-HASH-0001 | Planned | Implement collision detection, supported alias/rename lineage, and blocking ambiguity diagnostics. |
| T-003-008 | WP-DIAG-0002 | Planned | Implement the common diagnostic schema/registry and deterministic sorting/serialization. |
| T-003-009 | WP-DIAG-0002 | Planned | Implement identity/provenance diagnostic families and remediation context. |
| T-003-010 | WP-TEST-0001 | Planned | Add unit/property tests for identity stability, canonical equivalence, hashing, coordinates, and provenance. |
| T-003-011 | WP-TEST-0001 | Planned | Add negative/property fixtures for collisions, malformed coordinates, unsupported normalization, and provenance loss. |
| T-003-012 | WP-PROV-0001 | Planned | Demonstrate a semantic entity resolving from canonical source through stable identity and provenance into inspectable machine output. |

## Task decomposition rule

Tasks for SPRINT-004 and later are intentionally not pre-generated. During refinement, each selected PBI is decomposed into the smallest coherent steps needed to implement and validate the then-accepted contract. This prevents later implementation assumptions from becoming accidental authority merely because a task list was written months earlier.
