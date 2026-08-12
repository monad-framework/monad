# Ordered Product Backlog

**Status:** Active ordering baseline  
**Product Goal:** MVP Release 1 — deterministic semantic engineering loop

This is the current order in which product/engineering outcomes should be pulled, subject to Sprint Planning, newly discovered risk, and explicit Product Owner reprioritization. The order follows the dependency critical path; it is not simply Feature ID order.

## Now — STAB-0001

1. **EN-001-01 / F-001-01** — Canonical product thesis reconciliation.
2. **EN-001-03 / F-001-03** — Authority hierarchy and canonical ADR location.
3. **EN-001-02 / F-001-02** — Product Goal, MVP scope, success criteria, exclusions.
4. **EN-001-04 / F-001-04** — Artifact lifecycle/criticality; Draft versus approved authority.
5. **EN-002-01..06** — Complete deterministic machine projection and drift enforcement.
6. **EN-007-05** — Machine drift diagnostics.
7. **US-015-04** — GitHub Issues projection.
8. **US-015-05** — GitHub Project schema/views/iterations.
9. **US-015-06** — GitHub Wiki projection.
10. **STAB readiness** — complete Sprint/PI/WP plan and review the transition baseline.

## Next — SPRINT-001 / PI-001

11. **EN-001-05** — Canonical terminology.
12. **EN-001-06** — Scrum/EOS operating model.
13. **EN-001-07** — Repository governance/branch strategy/quality baseline.
14. **EN-013-01** — Repository-input threat model.
15. **US-015-01** — Documentation source-of-truth architecture.
16. **US-015-07** — Project status/traceability projection.
17. **C1 decision set** — identify and disposition first-slice architecture decisions.
18. **First-slice specification pack** — workspace/configuration/identity/provenance/diagnostics contracts.
19. **First implementation readiness review** — make SPRINT-002 Work Packets Ready.

## SPRINT-002 — Workspace and configuration intelligence

20. **US-003-01** — Workspace root discovery.
21. **US-003-02** — Repository identity.
22. **US-003-03** — Monad configuration model.
23. **EN-007-02** — Workspace/configuration diagnostics.
24. **US-003-05** — Component/package discovery.
25. **US-003-06** — Native toolchain discovery.
26. **US-003-04** — Lock/local-state model, to the minimum maturity required by semantic compilation.

## SPRINT-003 — Identity and provenance

27. **EN-004-01** — Semantic identity model.
28. **EN-004-02** — Canonicalization rules.
29. **EN-004-03** — Content/semantic hashing.
30. **EN-004-04** — Source coordinates.
31. **EN-004-05** — Provenance model.
32. **EN-004-06** — Alias/rename/collision handling.
33. **EN-007-01** — Diagnostic model/registry.
34. **EN-007-03** — Identity/provenance diagnostics.
35. **EN-014-01** — Semantic unit/property tests.

## SPRINT-004 — Monad Semantic Graph

36. Core ontology.
37. Node/entity taxonomy.
38. Relationship/edge taxonomy.
39. Deterministic graph construction.
40. Graph invariants/validation and diagnostics.
41. Canonical graph snapshot/serialization.
42. Graph traversal/indexes and golden/conformance fixtures.

## SPRINT-005 — KIR

43. KIR charter/semantic boundary.
44. KIR schema.
45. Canonical serialization.
46. MSG→KIR lowering.
47. KIR validation/conformance.
48. Versioning/compatibility/migration baseline.

## SPRINT-006 — Query and first semantic impact

49. Entity lookup/inspect.
50. Relationship query/traversal.
51. Why/provenance explanation.
52. Structured query output and indexes.
53. Coverage/gap query first slice.
54. Git/repository change ingestion.
55. Conservative semantic affected-set calculation.

## SPRINT-007 — Impact and diagnostic hardening

56. Impact-path explanation.
57. Conservative uncertainty/fallback.
58. Affected-set negative/boundary corpus and diagnostic hardening.

## SPRINT-008 — Incrementality and execution planning

59. Incremental graph invalidation/update.
60. Content/semantic fingerprints and cache-validity rules.
61. Execution-plan schema.
62. Deterministic plan construction.
63. Authority/policy evaluator first slice.

## SPRINT-009 — Native execution

64. Native-tool adapter contract.
65. Local execution runtime.
66. Parallelism/cancellation/failure propagation.
67. Execution/native-tool diagnostics.
68. Verified cache first slice.
69. Execution evidence/provenance.

## SPRINT-010 — CLI and agent context

70. CLI information architecture and output contracts.
71. `inspect`/`validate`/`graph` command integration.
72. `query`/`explain`/`affected` command integration.
73. `context`/`plan`/`run` integration.
74. `doctor`/`version` and first-run guidance; `init` only if ready.
75. Agent identity/capabilities and Task/Work Packet contract.
76. Semantic context selection/minimization.
77. Context package schema and Codex export.
78. Secrets/context boundaries and least privilege.
79. AI provenance/audit/evaluation safeguards.

## SPRINT-011 — Integrated conformance

80. Determinism/reproducibility suite.
81. Integration/E2E reference repositories.
82. Full MVP reference acceptance scenario runner.
83. Local/CI parity and clean-checkout execution evidence.

## SPRINT-012 — Security, performance, compatibility, packaging

84. Supply-chain/dependency controls.
85. Security review/exception model.
86. Security/fuzz/negative tests.
87. Performance benchmark suite and baseline.
88. Compatibility/migration tests and public compatibility policy.
89. Packaging/installation.

## SPRINT-013 — Dogfood, documentation, beta, release automation

90. Generated publication and search/navigation.
91. Release CI, provenance, SBOM/signing as applicable.
92. Monad-on-Monad dogfooding and self-hosting gap closure.
93. Release documentation/changelog/user/maintainer guidance.
94. Beta/reference-user feedback and blocker resolution.

## SPRINT-014 — Release candidate

95. Release readiness/rollback/support evidence.
96. Clean-machine Release 1 reproducibility run.
97. Security/operability/performance/release-readiness reviews.
98. Final known limitations and migration/compatibility notes.
99. MVP Release 1 candidate acceptance and publication.

## Post-MVP order

After Release 1, prioritize EPIC-017 (plugins/adapters/registry) before EPIC-018 (remote/team/hosted) unless user evidence requires remote collaboration earlier. EPIC-019 (enterprise/commercial ecosystem) remains future until the local product demonstrates repeat use and sustainable operational demand.

## Reordering triggers

Reorder immediately when a discovered correctness/security defect invalidates downstream work, a required architecture decision is unresolved, user evidence falsifies an assumption, the implementation reveals a lower-cost vertical slice, or an external dependency makes the current path infeasible. Record material changes in Sprint/PI planning rather than silently editing history.
