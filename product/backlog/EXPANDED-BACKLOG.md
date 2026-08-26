# Monad Expanded Product Backlog

**Status:** Approved post-MVP rolling-wave baseline  
**Change authority:** CR-0002  
**Predecessor:** MVP Release 1 / PG-001  
**Schedule type:** aggressive evidence-based forecast, not a promise

## Scope rule

This backlog begins only after the MVP Release 1 acceptance boundary. `product/backlog/MVP-BACKLOG.md` remains the governing MVP forecast. Nothing below silently expands the currently active MVP Work Cycle or authorizes implementation.

## Post-MVP Product Goals

### PG-002 — Living Workspace Intelligence

Monad can maintain explainable engineering memory, measure workspace intelligence/health, orchestrate bounded agents through governed context, and improve from execution evidence without converting probabilistic output into canonical truth.

### PG-003 — Governed Autonomous Engineering

Monad can coordinate progressively autonomous agents and integrations under declarative policy, independent review, signed attestations, strong identity/security controls, change control, audit, and operational observability.

### PG-004 — Enterprise Ecosystem and Scale

Monad can deploy locally, air-gapped, on-premises, or in optional clouds; expose MCP/IDE/plugin/storage integration surfaces; clone/restore governed workspaces; and scale deterministic internal execution under measured performance profiles.

## Program Increment map

| Increment | Forecast | Product Goal | Milestone | Work Cycles | Work Packets |
| --- | --- | --- | --- | --- | --- |
| PI-EXP-001 — Living Intelligence | 2026-11-09 through 2026-12-13 | PG-002 | M-004 Living Intelligence Alpha | WC-EXP-0001–0005 | WP-EXP-0001–0012 |
| PI-EXP-002 — Governed Automation & Trust | 2026-12-14 through 2027-01-10 | PG-003 | M-005 Governed Automation Beta | WC-EXP-0006–0009 | WP-EXP-0013–0024 |
| PI-EXP-003 — Ecosystem, Deployment & Scale | 2027-01-11 through 2027-02-14 | PG-004 | M-006 Living Engineering OS Release 2 | WC-EXP-0010–0014 | WP-EXP-0025–0040 |

## Epic roadmap

| Epic | Outcome | Forecast |
| --- | --- | --- |
| EPIC-015 Workspace Intelligence & Memory | explainable workspace maturity, anti-hallucination memory, health, learning, vector/cache intelligence | WC-EXP-0001–0002 |
| EPIC-016 Autonomous Agent Orchestration | dependency-aware multi-agent execution with progressive autonomy, cross-review, routing, resilience | WC-EXP-0002–0004 |
| EPIC-017 Automation & Integration Ecosystem | governed resources/adapters, reactive workflows, broad integration growth, verified PR automation | WC-EXP-0004–0005 |
| EPIC-018 Security, Identity & Attestation | DSSE attestations, crypto agility, multi-party trust, RBAC/passkeys, agent/prompt security | WC-EXP-0006–0007 |
| EPIC-019 Policy, Change Control & Audit | declarative policy, governed resources, formal change/restore, immutable audit, readiness/done trust gates | WC-EXP-0007–0008 |
| EPIC-020 Observability, Analytics & Operations | OpenTelemetry, graph/workspace health, agent execution analytics, optional hosted usage analytics | WC-EXP-0008–0009 |
| EPIC-021 Deployment, Portability & Workspace Lifecycle | instant/shared deployment, clone/restore, air-gap/multi-cloud/on-prem, Docker/Nix, files/media | WC-EXP-0009–0011 |
| EPIC-022 Developer & Ecosystem Integration Surfaces | MCP, LSP/IDE, plugin SDK/registry/packs, pluggable storage, external runtime adapters | WC-EXP-0011–0012 |
| EPIC-023 Performance, Parallelism & Scale | deterministic parallel scheduling, throughput/finality benchmarks, distributed cache/isolation | WC-EXP-0013 |
| EPIC-024 Expanded Acceptance & Release | end-to-end intelligence/autonomy/enterprise acceptance, security/scale readiness, Release 2 | WC-EXP-0014 |

## Feature / Work Packet map

Each Feature is one forecast Work Packet. Story IDs are stable planning identifiers. Detailed implementation Tasks remain rolling-wave and MUST be created/refined before the corresponding Work Packet becomes Ready.

| Feature | Work Packet | Sprint | Stories |
| --- | --- | --- | --- |
| F-015-01 Intelligence score & maturity tiers | WP-EXP-0001 | WC-EXP-0001 | US-106 score model; US-107 maturity tiers; US-108 historical score tracking |
| F-015-02 Unified memory–intelligence–execution model | WP-EXP-0002 | WC-EXP-0001 | US-109 governed memory model; US-110 agent intelligence training/context adaptation; US-111 continuous learning loop; US-112 anti-hallucination reconciliation |
| F-015-03 Knowledge health & decay | WP-EXP-0003 | WC-EXP-0001 | US-113 stale/zombie detection; US-114 relationship decay indicators; US-115 health dashboard |
| F-015-04 Vector memory & intelligent caching | WP-EXP-0004 | WC-EXP-0002 | US-116 multi-vector semantic spaces; US-117 semantic cache; US-118 result-aware cache; US-119 isolation/provenance/invalidation |
| F-016-01 Autonomous dependency-aware orchestrator | WP-EXP-0005 | WC-EXP-0002 | US-120 dependency-graph dispatch; US-121 experimental autonomy gate; US-122 bounded concurrency/cancellation |
| F-016-02 Progressive autonomy & operator stewardship | WP-EXP-0006 | WC-EXP-0003 | US-123 advisory mode; US-124 evidence-based autonomy promotion; US-125 operator decision stewardship; US-126 demotion/revocation |
| F-016-03 Cross-harness review | WP-EXP-0007 | WC-EXP-0003 | US-127 parallel independent reviewers; US-128 disagreement synthesis; US-129 reviewer evidence/provenance |
| F-016-04 Cost/capability-aware model routing | WP-EXP-0008 | WC-EXP-0004 | US-130 multi-provider contract; US-131 cost/complexity/privacy routing; US-132 local-model profile |
| F-016-05 Agent resilience controls | WP-EXP-0009 | WC-EXP-0004 | US-133 circuit breakers; US-134 exponential backoff; US-135 retry/idempotency; US-136 execution budgets/timeouts |
| F-017-01 Integration adapter & resource framework | WP-EXP-0010 | WC-EXP-0004 | US-137 standard adapter contract; US-138 governed resource model/bindings; US-139 initial integration catalog; US-140 scalable path toward 100+ integrations |
| F-017-02 Intelligent automation workflows | WP-EXP-0011 | WC-EXP-0005 | US-141 event/reactive triggers; US-142 policy-bounded adaptive workflows; US-143 execution outcomes create durable memory/evidence |
| F-017-03 Autonomous PR lifecycle | WP-EXP-0012 | WC-EXP-0005 | US-144 verified PR creation; US-145 isolated worktree/branch execution; US-146 configurable rebase-first integration; US-147 Work Packet/execution/evidence trace |
| F-018-01 Signed attestations & crypto agility | WP-EXP-0013 | WC-EXP-0006 | US-148 DSSE-compatible attestations; US-149 protected-branch attestation gate; US-150 Ed25519/P-256/secp256k1 profiles; US-151 ML-DSA post-quantum profile |
| F-018-02 Multi-party trust & key lifecycle | WP-EXP-0014 | WC-EXP-0006 | US-152 multi-signature approval policy; US-153 key rotation/revocation; US-154 quantum-migration policy |
| F-018-03 RBAC & passkey identity | WP-EXP-0015 | WC-EXP-0006 | US-155 RBAC; US-156 WebAuthn/P-256 passkeys; US-157 password/session/access protection |
| F-018-04 AI/input security boundary | WP-EXP-0016 | WC-EXP-0007 | US-158 prompt-injection detection/containment; US-159 secret masking; US-160 capability sandboxing; US-161 least-authority execution |
| F-019-01 Declarative policy & resource governance | WP-EXP-0017 | WC-EXP-0007 | US-162 policy model/DSL; US-163 quality/autonomy/compliance policies; US-164 governed resources/ownership |
| F-019-02 Change control & restoration | WP-EXP-0018 | WC-EXP-0007 | US-165 submit/review/approve change; US-166 rollback/restore; US-167 versioned policy/workspace state |
| F-019-03 Immutable audit trail | WP-EXP-0019 | WC-EXP-0008 | US-168 audit event model; US-169 action/agent/decision/evidence linkage; US-170 tamper-evident export |
| F-019-04 Readiness/done trust gates | WP-EXP-0020 | WC-EXP-0008 | US-171 enforce Definition of Ready; US-172 Definition of Done attestation policy; US-173 progressive-trust evidence gate |
| F-020-01 OpenTelemetry & health telemetry | WP-EXP-0021 | WC-EXP-0008 | US-174 correlated traces; US-175 metrics; US-176 structured logs; US-177 operational/knowledge-health views |
| F-020-02 Agent execution analytics | WP-EXP-0022 | WC-EXP-0009 | US-178 execution history; US-179 context/diff/verification view; US-180 token/cost/duration/failure metrics |
| F-020-03 Hosted usage analytics | WP-EXP-0023 | WC-EXP-0009 | US-181 visitor/session tracking; US-182 traffic/geography/device metrics; US-183 privacy/opt-in/retention controls |
| F-021-01 Instant deployment & custom domains | WP-EXP-0024 | WC-EXP-0009 | US-184 one-action deployment; US-185 shareable links/custom domains/access control; US-186 optional gallery publication |
| F-021-02 Workspace cloning & restore | WP-EXP-0025 | WC-EXP-0010 | US-187 one-action full workspace clone/template; US-188 version-history restore; US-189 clone/restore provenance |
| F-021-03 Enterprise deployment modes | WP-EXP-0026 | WC-EXP-0010 | US-190 air-gapped/no-exfiltration; US-191 AWS/GCP/Azure profiles; US-192 on-premises profile; US-193 boundary audit controls |
| F-021-04 Reproducible environments | WP-EXP-0027 | WC-EXP-0010 | US-194 Docker/container support; US-195 Nix support; US-196 reproducible environment manifest/evidence |
| F-021-05 Governed files & media | WP-EXP-0028 | WC-EXP-0011 | US-197 upload/storage/reference; US-198 content hashing/provenance; US-199 classification/retention/AI-processing policy |
| F-022-01 MCP server | WP-EXP-0029 | WC-EXP-0011 | US-200 MCP tools/resources; US-201 scoped authority/context; US-202 external MCP-client interoperability |
| F-022-02 LSP/IDE integrations | WP-EXP-0030 | WC-EXP-0011 | US-203 LSP semantic contract; US-204 VS Code/JetBrains/Zed integration profiles; US-205 diagnostics/navigation/explain/context actions |
| F-022-03 Plugin SDK, registry & packs | WP-EXP-0031 | WC-EXP-0012 | US-206 plugin SDK; US-207 registry/discovery; US-208 curated packs; US-209 plugin provenance/signature/permission policy |
| F-022-04 Pluggable storage backends | WP-EXP-0032 | WC-EXP-0012 | US-210 graph/vector backend contracts; US-211 Neo4j/Neptune/JanusGraph adapters; US-212 pgvector/Pinecone/Weaviate adapters; US-213 local-first default |
| F-022-05 External runtime compatibility profiles | WP-EXP-0033 | WC-EXP-0012 | US-214 adapter-defined runtime/bytecode compatibility; US-215 optional EVM bytecode profile; US-216 isolation/no-core-semantic-dependency |
| F-023-01 Parallel execution scheduler | WP-EXP-0034 | WC-EXP-0013 | US-217 parallel independent work; US-218 dependency/conflict detection; US-219 deterministic result/evidence commit ordering |
| F-023-02 High-throughput benchmark profile | WP-EXP-0035 | WC-EXP-0013 | US-220 declared reference benchmark; US-221 10,000+ lightweight internal operations/second stretch target; US-222 regression budgets |
| F-023-03 Fast local state finalization | WP-EXP-0036 | WC-EXP-0013 | US-223 400 ms p95 eligible local transition target; US-224 timeout/failure semantics; US-225 benchmark evidence |
| F-023-04 Scale-out cache & isolation | WP-EXP-0037 | WC-EXP-0013 | US-226 distributed-cache abstraction; US-227 tenant/workspace cache isolation; US-228 cache provenance/invalidation |
| F-024-01 End-to-end expanded acceptance | WP-EXP-0038 | WC-EXP-0014 | US-229 living-intelligence journey; US-230 governed-autonomy journey; US-231 enterprise/offline journey |
| F-024-02 Security & scale readiness | WP-EXP-0039 | WC-EXP-0014 | US-232 attestation/crypto readiness; US-233 prompt/secret/sandbox acceptance; US-234 performance/scale evidence acceptance |
| F-024-03 Release 2 packaging & migration | WP-EXP-0040 | WC-EXP-0014 | US-235 MVP-to-expanded migration; US-236 release provenance/notes/artifacts; US-237 PG-002/003/004 acceptance and release disposition |

## Story acceptance convention

Every Story entering Ready must state observable acceptance, negative/boundary behavior, governing ADR/specification where applicable, verification method, security/privacy implications, and Work Packet ownership. Story points may support capacity learning but are not converted mechanically to hours or used as productivity targets.

## Task refinement

Formal implementation Tasks are intentionally not forecast across the full post-MVP horizon. Before each Work Packet becomes Ready, refinement MUST create the bounded task/test/evidence decomposition needed to implement it without guessing. At least two future Work Cycles should remain sufficiently refined. This preserves the existing Monad rolling-wave rule rather than manufacturing hundreds of stale speculative tasks.

## Ordering rule

Within a Work Cycle, prioritize:

1. release-blocking correctness/security/privacy risk;
2. dependency/critical-path enablement;
3. Product Goal value;
4. uncertainty/learning reduction;
5. interoperability and migration risk;
6. effort/reversibility.

Later items may move earlier only through governed replanning when evidence changes the critical path.
