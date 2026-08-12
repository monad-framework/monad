# MVP Release 1

**ID:** REL-MVP-0001  
**Status:** Proposed  
**Product:** Monad  
**Owner:** Product Owner

## Product goal

Prove that Monad can deterministically transform canonical engineering knowledge in a real repository into a stable semantic representation that a human or bounded AI agent can validate, query, explain, and use to obtain minimal trustworthy engineering context.

## User outcome

A software engineer can point Monad at a supported repository and answer, with provenance:

- what engineering artifacts exist;
- what they mean and how they relate;
- which requirements, decisions, specifications, and work records govern a target;
- what changed semantically;
- what context an implementation agent is authorized to use; and
- whether the repository satisfies the MVP's structural and semantic invariants.

## Required MVP capabilities

### MVP-C01 — Repository discovery

Discover supported canonical engineering artifacts deterministically and identify them with stable IDs.

### MVP-C02 — Knowledge parsing and normalization

Parse supported Markdown/YAML configuration and normalize metadata, references, identifiers, and sections without opaque model inference.

### MVP-C03 — Semantic graph

Construct a deterministic graph of artifacts, identifiers, and typed relationships with source provenance.

### MVP-C04 — Validation and diagnostics

Evaluate structural and semantic invariants and emit stable, actionable, machine-readable diagnostics.

### MVP-C05 — Query and explanation

Support bounded queries such as governing artifacts, references, dependents, unresolved identifiers, and "why does this artifact exist?" with provenance.

### MVP-C06 — Agent context package

Produce a minimal, deterministic context package for a bounded Work Packet or engineering target, including authority, constraints, relevant graph neighborhood, and validation commands.

### MVP-C07 — CLI vertical slice

Expose the MVP through a coherent local CLI capable of inspect, validate, graph/query, explain, and context operations.

### MVP-C08 — Reproducibility and evidence

Given the same canonical inputs, Monad version, and configuration, produce equivalent semantic outputs and validation evidence.

## Explicit exclusions

MVP Release 1 does not require:

- hosted SaaS or multi-tenant control plane;
- remote execution;
- a public plugin marketplace;
- broad IDE integrations;
- multi-agent autonomous orchestration;
- enterprise SSO/RBAC beyond what is needed for local repository governance;
- universal language/build-system support;
- general-purpose project management replacement; or
- automatic implementation without human authorization.

## Release acceptance

MVP Release 1 is accepted only when:

1. a clean reference repository can be inspected end-to-end;
2. identical inputs produce deterministic semantic outputs;
3. graph relationships retain canonical-source provenance;
4. malformed or contradictory inputs produce actionable diagnostics;
5. query/explain responses can cite the governing canonical artifacts;
6. a Work Packet context package excludes unrelated repository material by default;
7. unit, integration, conformance, determinism, security, and end-to-end tests pass;
8. installation and first-run documentation are executable by a new user;
9. release artifacts are versioned, checksummed, and reproducibly traceable to source; and
10. the Product Owner accepts the demonstrated outcome against this goal.

## Scope control

A proposed capability enters MVP only if it is necessary to prove the product goal or retire a release-blocking correctness, security, operability, or adoption risk. Everything else is ordered into post-MVP backlog.