# Threat Model

## Scope and assumptions

This baseline covers the primary journey, application boundary, workflow and
domain state, evidence, external adapters, operator access, and software
delivery path. It assumes the client and network are untrusted, dependencies can
fail or be compromised, valid accounts may act maliciously, and mistakes are
more common than sophisticated attacks but can have equal impact.

## Assets

- authoritative domain and workflow integrity;
- confidential and restricted user or business data;
- user, administrator, operator, service, and release credentials;
- policy, configuration, and authorization decisions;
- evidence needed for accountability and incident response;
- source, dependencies, build identity, and release artifacts;
- service availability, capacity, cost budget, and user trust.

## Trust boundaries

1. User-controlled client to public application interface.
2. Application runtime to identity, secrets, and data stores.
3. Internal capability to another capability's owned contract.
4. Product runtime to external provider.
5. Operator workstation to privileged production control.
6. Pull-request or dependency input to protected build and release authority.

## Priority threats

| ID | Threat and consequence | Primary mitigations | Verification |
| --- | --- | --- | --- |
| T-001 | Account or session takeover enables unauthorized action | Strong authentication, secure sessions, reauthentication, revocation | Session and abuse tests |
| T-002 | Broken object authorization exposes another resource | Resource-owner authorization, deny by default, tenant and object tests | Negative authorization matrix |
| T-003 | Injection changes queries, commands, templates, or output | Typed validation, parameterization, encoding, constrained interpreters | Fuzzing and adversarial tests |
| T-004 | Duplicate or reordered request causes repeated effect | Idempotency keys, state invariants, concurrency control, reconciliation | Retry and race tests |
| T-005 | Sensitive data leaks through telemetry, export, cache, or error | Data minimization, field allow-list, redaction, access and retention | Data-flow and log inspection |
| T-006 | Privileged operator action exceeds intended scope | Separate roles, just-in-time access, confirmation, audit, dual control | Access review and admin tests |
| T-007 | Dependency or outbound request enables data theft or SSRF | Egress allow-list, URL validation, network isolation, response limits | Controlled malicious endpoint tests |
| T-008 | Resource abuse exhausts availability or cost | Authentication, quotas, rate and concurrency limits, backpressure | Abuse and saturation tests |
| T-009 | Build input steals release secrets or modifies artifact | Untrusted-job isolation, scoped tokens, pinned dependencies, provenance | Pipeline permission review |
| T-010 | Backup or restore path bypasses access and integrity | Separate credentials, encryption, immutable copies, restore verification | Quarterly recovery exercise |

## Abuse cases

- A valid user enumerates identifiers to access another user's result.
- An attacker submits payloads that expand, recurse, or consume unbounded work.
- A user repeats confirmation after a timeout to create duplicate effects.
- A compromised dependency attempts unexpected network or secret access.
- A maintainer's pull request executes with production deployment authority.
- An operator uses broad export or repair tooling without scoped approval.
- An error response or trace reveals secrets, internal topology, or private data.

## Residual risk

No control removes all risk. Residual risks receive an owner, exposure decision,
monitoring signal, contingency, review date, and treatment work. Critical and
high residual risk cannot be hidden in this document; it must appear in the
risk register and release decision.

## Review triggers

Update the model for a new actor, data class, trust boundary, integration,
privileged operation, execution engine, public endpoint, deployment authority,
or material incident. Validate the model against implementation and telemetry
before production exposure and at least annually.
