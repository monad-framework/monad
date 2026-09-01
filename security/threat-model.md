# Threat Model

## Scope and assumptions

This baseline covers the primary journey, application boundary, workflow and domain state, evidence, external adapters, operator access, software delivery path, and Monad Governed Execution Harness (GEH). It assumes clients, repositories, model/provider output, agent harnesses, tool arguments, network responses, dependencies, and external services can be untrusted or compromised. Valid identities may act maliciously or mistakenly. A model or executor can propose work but does not become authoritative merely by producing plausible output.

For governed execution, Monad treats the Execution Envelope, resolved policy/authority state, explicit capability grants, mediated operation results, durable evidence, and verification results as security-relevant control data. Private model reasoning is neither trusted authority nor required audit evidence.

## Assets

- authoritative domain, engineering, governance, and EOS lifecycle integrity;
- Execution Envelope identity, governing-state binding, and immutability;
- capability grants, prohibitions, approval state, and policy decisions;
- operation/effect integrity and idempotency state;
- verification obligations, results, and completion authority;
- confidential and restricted user or business data;
- user, administrator, operator, service, agent, adapter, and release credentials;
- evidence needed for accountability, recovery, and incident response;
- source, dependencies, build identity, and release artifacts;
- service availability, capacity, cost budget, and user trust.

## Trust boundaries

1. User-controlled client to public application interface.
2. Application runtime to identity, secrets, and data stores.
3. Internal capability to another capability's owned contract.
4. Product runtime to external provider.
5. Operator workstation to privileged production control.
6. Pull-request or dependency input to protected build and release authority.
7. Canonical engineering/governance state to Execution Envelope compiler.
8. GEH to replaceable agent/executor harness adapter.
9. Agent/executor output to Monad Tool Gateway and operation mediation.
10. Tool Gateway to filesystem, process, network, service, deployment, or other effectful tools.
11. Candidate executor output/evidence to independent verification and EOS lifecycle authority.
12. Parent execution to delegated child/subagent execution.
13. Checkpoint/resume state to continued governed execution.

## Priority threats

| ID | Threat and consequence | Primary mitigations | Verification |
| --- | --- | --- | --- |
| T-001 | Account or session takeover enables unauthorized action | Strong authentication, secure sessions, reauthentication, revocation | Session and abuse tests |
| T-002 | Broken object authorization exposes another resource | Resource-owner authorization, deny by default, tenant and object tests | Negative authorization matrix |
| T-003 | Injection changes queries, commands, templates, tool arguments, or output | Typed validation, parameterization, encoding, constrained interpreters, Tool Gateway validation | Fuzzing and adversarial operation tests |
| T-004 | Duplicate or reordered request causes repeated effect | Idempotency keys, state invariants, causal ordering, concurrency control, reconciliation | Retry, replay, and race tests |
| T-005 | Sensitive data leaks through telemetry, context, provider projection, export, cache, or error | Data minimization, field allow-list, redaction, access and retention policy | Data-flow and log/context inspection |
| T-006 | Privileged operator action exceeds intended scope | Separate roles, just-in-time access, confirmation, audit, dual control | Access review and admin tests |
| T-007 | Dependency, tool, or outbound request enables data theft or SSRF | Egress allow-list, URL validation, capability-scoped network access, isolation, response limits | Controlled malicious endpoint tests |
| T-008 | Resource abuse exhausts availability or cost | Authentication, envelope budgets, quotas, rate/concurrency limits, backpressure | Abuse, budget, and saturation tests |
| T-009 | Build input steals release secrets or modifies artifact | Untrusted-job isolation, scoped tokens, pinned dependencies, provenance | Pipeline permission review |
| T-010 | Backup or restore path bypasses access and integrity | Separate credentials, encryption, immutable copies, restore verification | Recovery exercise |
| T-011 | Prompt/repository injection persuades an executor to broaden authority or bypass governance | Executor output is untrusted; capabilities resolved independently; consequential effects require GEH mediation | Injection fixtures attempting ungranted operations |
| T-012 | Forged, stale, replayed, or silently mutated Execution Envelope causes work under invalid authority | Content-derived identity, governing-state digest, immutable binding, freshness checks, explicit recompilation | Digest mismatch, stale-state, replay, and mutation tests |
| T-013 | Capability confusion or confused-deputy behavior lets an allowed tool act outside granted scope | Explicit capability+scope model, deny by default, target containment, separate sensitive capabilities | Scope-boundary and capability-conflict matrix |
| T-014 | Adapter/provider incompatibility silently drops mandatory governance semantics | Version negotiation, mandatory-feature declaration, fail-closed initialization | Incompatible adapter/envelope conformance fixtures |
| T-015 | Executor self-report, fabricated evidence, or reviewer consensus falsely marks work complete | Verification-controlled completion, attributable evidence, independent checks, EOS remains lifecycle authority | Completion-without-evidence and forged-evidence tests |
| T-016 | Delegation/subagents launder or amplify authority | Child identity, non-expanding grants, causal provenance, depth/budget policy | Delegation narrowing and recursive bypass tests |
| T-017 | Checkpoint/resume continues after authority/policy drift or hides prior effects | Envelope binding, checkpoint integrity, prior-effect ledger, drift validation before resume | Resume-after-drift and partial-effect recovery tests |
| T-018 | Unmediated external effect is falsely represented as Monad-governed execution | Explicit external/unverified classification; gateway evidence required for governed status | External-effect attribution tests |

## Governed-execution abuse cases

- A repository document contains instructions telling an agent to ignore Monad policy and publish credentials.
- An executor requests `fs.write` outside the scope granted in the bound envelope.
- A tool name is allowed but its requested target exceeds the capability scope.
- A denied operation is reformulated through another adapter/tool to obtain the same prohibited effect.
- An old valid envelope is replayed after policy, authority, acceptance criteria, or governing state changed.
- An adapter omits a mandatory approval gate because its provider API cannot express it.
- An executor reports tests as passing without attributable execution evidence.
- Multiple agent reviewers agree on completion even though a mandatory deterministic verification failed.
- A parent agent delegates to a child to obtain broader network, secret, release, or filesystem authority.
- A resumed checkpoint repeats a non-idempotent effect or continues under stale authority.
- A model/provider transcript includes sensitive context that was not necessary for execution.
- An external effect performed outside the Tool Gateway is presented as verified governed execution.

## Security invariants for GEH

1. Absence, ambiguity, expiry, staleness, or incompatibility of mandatory authority/capability state MUST fail closed or explicitly escalate.
2. An adapter, model, executor, prompt, repository artifact, or tool result MUST NOT create authority by assertion.
3. Consequential effects claiming governed status MUST pass the applicable mediated operation boundary.
4. A child/delegated run MUST NOT receive broader capabilities than its parent without a separate accountable grant.
5. Executor-reported completion MUST NOT directly create authoritative completion.
6. Required verification and evidence MUST remain independently evaluable from executor private reasoning.
7. Cancellation/suspension MUST prevent new governed effects except explicitly authorized recovery actions.
8. Secret access MUST be separately authorized and raw secret values SHOULD NOT be stored in ordinary envelopes/evidence.
9. The system MUST distinguish protocol failure, tool failure, policy denial, capability denial, verification failure, and indeterminate/unverified effects.

## Residual risk

Monad cannot prevent an executor from causing effects through channels outside Monad's control. The security claim is therefore scoped: Monad can label an effect governed only when the applicable GEH boundary and evidence requirements are satisfied. Effects observed outside that boundary remain external, unverified, partially verified, or equivalent until independently established.

No control removes all risk. Residual risks receive an owner, exposure decision, monitoring signal, contingency, review date, and treatment work. Critical and high residual risk cannot be hidden in this document; it must appear in the risk register and release decision.

## Review triggers

Update the model for a new actor, data class, trust boundary, integration, privileged operation, agent/executor harness, model/provider capability, Tool Gateway operation family, capability class, delegation mechanism, public endpoint, deployment authority, or material incident.

Before production activation of a new governed execution capability, verify its envelope semantics, capability boundaries, effect mediation, evidence model, failure/recovery path, and completion authority against this threat model. Validate the model against implementation and telemetry before production exposure and at least annually.
