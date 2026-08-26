# Forecast Work Packets — PI-EXP-003

**Status:** Forecast catalog  
**Change authority:** CR-0002

These Work Packets are forecast placeholders. They are not Ready or authorized. Each is split into its own canonical Work Packet artifact when rolling-wave refinement reaches it; until then this catalog plus `product/backlog/EXPANDED-BACKLOG.md` defines the forecast identity and scope intent.

## WP-EXP-0025 — Workspace cloning & restore

- **Epic:** EPIC-021
- **Feature:** F-021-02
- **Work Cycle / Sprint:** WC-EXP-0010
- **Product Goal:** PG-004
- **Planned stories:** US-187 one-action full workspace clone/template; US-188 version-history restore; US-189 clone/restore provenance
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0026 — Enterprise deployment modes

- **Epic:** EPIC-021
- **Feature:** F-021-03
- **Work Cycle / Sprint:** WC-EXP-0010
- **Product Goal:** PG-004
- **Planned stories:** US-190 air-gapped/no-exfiltration; US-191 AWS/GCP/Azure profiles; US-192 on-premises profile; US-193 boundary audit controls
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0027 — Reproducible environments

- **Epic:** EPIC-021
- **Feature:** F-021-04
- **Work Cycle / Sprint:** WC-EXP-0010
- **Product Goal:** PG-004
- **Planned stories:** US-194 Docker/container support; US-195 Nix support; US-196 reproducible environment manifest/evidence
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0028 — Governed files & media

- **Epic:** EPIC-021
- **Feature:** F-021-05
- **Work Cycle / Sprint:** WC-EXP-0011
- **Product Goal:** PG-004
- **Planned stories:** US-197 upload/storage/reference; US-198 content hashing/provenance; US-199 classification/retention/AI-processing policy
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0029 — MCP server

- **Epic:** EPIC-022
- **Feature:** F-022-01
- **Work Cycle / Sprint:** WC-EXP-0011
- **Product Goal:** PG-004
- **Planned stories:** US-200 MCP tools/resources; US-201 scoped authority/context; US-202 external MCP-client interoperability
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0030 — LSP/IDE integrations

- **Epic:** EPIC-022
- **Feature:** F-022-02
- **Work Cycle / Sprint:** WC-EXP-0011
- **Product Goal:** PG-004
- **Planned stories:** US-203 LSP semantic contract; US-204 VS Code/JetBrains/Zed integration profiles; US-205 diagnostics/navigation/explain/context actions
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0031 — Plugin SDK, registry & packs

- **Epic:** EPIC-022
- **Feature:** F-022-03
- **Work Cycle / Sprint:** WC-EXP-0012
- **Product Goal:** PG-004
- **Planned stories:** US-206 plugin SDK; US-207 registry/discovery; US-208 curated packs; US-209 plugin provenance/signature/permission policy
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0032 — Pluggable storage backends

- **Epic:** EPIC-022
- **Feature:** F-022-04
- **Work Cycle / Sprint:** WC-EXP-0012
- **Product Goal:** PG-004
- **Planned stories:** US-210 graph/vector backend contracts; US-211 Neo4j/Neptune/JanusGraph adapters; US-212 pgvector/Pinecone/Weaviate adapters; US-213 local-first default
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0033 — External runtime compatibility profiles

- **Epic:** EPIC-022
- **Feature:** F-022-05
- **Work Cycle / Sprint:** WC-EXP-0012
- **Product Goal:** PG-004
- **Planned stories:** US-214 adapter-defined runtime/bytecode compatibility; US-215 optional EVM bytecode profile; US-216 isolation/no-core-semantic-dependency
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0034 — Parallel execution scheduler

- **Epic:** EPIC-023
- **Feature:** F-023-01
- **Work Cycle / Sprint:** WC-EXP-0013
- **Product Goal:** PG-004
- **Planned stories:** US-217 parallel independent work; US-218 dependency/conflict detection; US-219 deterministic result/evidence commit ordering
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0035 — High-throughput benchmark profile

- **Epic:** EPIC-023
- **Feature:** F-023-02
- **Work Cycle / Sprint:** WC-EXP-0013
- **Product Goal:** PG-004
- **Planned stories:** US-220 declared reference benchmark; US-221 10,000+ lightweight internal operations/second stretch target; US-222 regression budgets
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0036 — Fast local state finalization

- **Epic:** EPIC-023
- **Feature:** F-023-03
- **Work Cycle / Sprint:** WC-EXP-0013
- **Product Goal:** PG-004
- **Planned stories:** US-223 400 ms p95 eligible local transition target; US-224 timeout/failure semantics; US-225 benchmark evidence
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0037 — Scale-out cache & isolation

- **Epic:** EPIC-023
- **Feature:** F-023-04
- **Work Cycle / Sprint:** WC-EXP-0013
- **Product Goal:** PG-004
- **Planned stories:** US-226 distributed-cache abstraction; US-227 tenant/workspace cache isolation; US-228 cache provenance/invalidation
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0038 — End-to-end expanded acceptance

- **Epic:** EPIC-024
- **Feature:** F-024-01
- **Work Cycle / Sprint:** WC-EXP-0014
- **Product Goal:** PG-004
- **Planned stories:** US-229 living-intelligence journey; US-230 governed-autonomy journey; US-231 enterprise/offline journey
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0039 — Security & scale readiness

- **Epic:** EPIC-024
- **Feature:** F-024-02
- **Work Cycle / Sprint:** WC-EXP-0014
- **Product Goal:** PG-004
- **Planned stories:** US-232 attestation/crypto readiness; US-233 prompt/secret/sandbox acceptance; US-234 performance/scale evidence acceptance
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.

## WP-EXP-0040 — Release 2 packaging & migration

- **Epic:** EPIC-024
- **Feature:** F-024-03
- **Work Cycle / Sprint:** WC-EXP-0014
- **Product Goal:** PG-004
- **Planned stories:** US-235 MVP-to-expanded migration; US-236 release provenance/notes/artifacts; US-237 PG-002/003/004 acceptance and release disposition
- **Readiness:** Planned only; concrete ADR/specification/dependency/task/test/evidence boundaries are required before Ready.
