# DATA-HARNESS-0001: Execution Envelope Data Contract

**Status:** proposed  
**Version:** 0.1.0  
**Owner:** Monad Core / EOS  
**Related requirements:** FR-007, FR-009, FR-014, FR-015, FR-017, FR-023, FR-029, FR-037, FR-038, FR-039, FR-040, FR-041, QR-001, QR-003, QR-007, QR-010, QR-014, QR-021, QR-022, QR-023  
**Governing ADR:** ADR-0007  
**Governing technical specification:** TECH-HARNESS-0001

## Purpose

Defines the canonical serialized data model and identity semantics of a Monad Execution Envelope. The envelope is an immutable, content-addressed compilation of the governed engineering contract applicable to a bounded execution.

The envelope is deliberately distinct from execution-run state. A run binds to an envelope; run identity, binding time, checkpoints, transient adapter/session state, observations, and terminal run state are not part of the envelope's semantic identity.

## Core invariant

Equivalent governed execution semantics MUST compile to the same canonical envelope identity regardless of which run consumes the envelope or when that run is bound.

Consequently:

1. `run_id` MUST NOT be an Execution Envelope field;
2. wall-clock or binding timestamps MUST NOT be Execution Envelope fields;
3. executor session identifiers MUST NOT be Execution Envelope fields;
4. transient checkpoint/runtime state MUST NOT be Execution Envelope fields;
5. a run binding MUST refer to the immutable `envelope_id` rather than mutating the envelope.

## Canonical envelope model

Version `0.1.0` contains the following fields.

### Identity

- `envelope_id` — `env-v1-` followed by the lowercase hexadecimal `envelope_digest`;
- `envelope_digest` — lowercase SHA-256 digest produced by the versioned envelope digest algorithm;
- `schema_version` — serialized envelope contract version, initially `0.1.0`.

`envelope_id` and `envelope_digest` are derived fields. They MUST NOT themselves participate as inputs to the digest.

### Work contract

- `work_subject` — governed work/artifact subject identifier;
- `intent` — bounded statement of what the executor is authorized to attempt;
- `requested_outcome` — expected work product or state outcome.

### Governing state

- `governing_state_digest` — identity/digest of the canonical governing state from which the envelope was compiled;
- `governed_references` — normalized references to requirements, ADRs, specifications, policies, evidence, work artifacts, or other governed objects whose semantics apply to execution.

Each governed reference contains:

- `kind`;
- `identifier`;
- optional `content_digest` when content/freshness identity is required.

### Actors

- `initiating_actor` — accountable actor that initiated or authorized compilation/binding;
- `executor` — actor/executor identity against which capabilities and accountability are evaluated.

Each actor contains:

- `actor_id`;
- `role`.

An executor identity MAY identify an adapter/service/automation role rather than a model name. Provider/model/session identity belongs in run/evidence records when required and MUST NOT silently redefine the envelope's authority semantics.

### Capability contract

- `granted_capabilities` — explicit least-privilege grants;
- `prohibited_capabilities` — explicit denials/prohibitions.

Each capability entry contains:

- `capability` — capability identifier;
- `scope` — canonical scope expression.

Absence from `granted_capabilities` MUST NOT be interpreted as permission. Explicit prohibition takes precedence over a conflicting grant until accountable policy/authority recompiles a non-conflicting envelope.

### Tool and environment contract

- `allowed_tools` — tool/interface identifiers available to the governed execution;
- `environment_constraints` — canonical constraints that govern the execution environment.

Raw secret values MUST NOT appear in these fields. Secret access is represented through governed capability/reference mechanisms.

### Quality, approval, and completion contract

- `acceptance_criteria`;
- `verification_obligations`;
- `approval_gates`;
- `escalation_conditions`;
- `completion_criteria`.

These collections express obligations, not executor suggestions. Executor-reported completion cannot erase or satisfy them by assertion.

### Resource contract

- `resource_limits` — deterministic map from versioned policy/resource-limit key to canonical scalar value.

Version `0.1.0` intentionally uses string values so policy-specific units and richer typed limits can evolve without prematurely embedding one resource taxonomy into the core. A limit whose unit would otherwise be ambiguous MUST encode that unit in the key or canonical value according to the governing policy contract. A future typed limit model requires a schema-version change if serialization compatibility is broken.

## Canonical normalization

Before digest calculation and serialization as a compiled envelope:

1. `governed_references` MUST be sorted by `(kind, identifier, content_digest)` and exact duplicates removed;
2. capability collections MUST be sorted by `(capability, scope)` and exact duplicates removed;
3. `allowed_tools`, `environment_constraints`, `acceptance_criteria`, `verification_obligations`, `approval_gates`, `escalation_conditions`, and `completion_criteria` MUST be lexicographically sorted and exact duplicates removed;
4. `resource_limits` keys MUST be unique and serialized in lexical key order by canonical producers;
5. producers MUST preserve exact string bytes after any upstream domain-specific canonicalization; envelope compilation MUST NOT silently rewrite human meaning;
6. incidental source traversal order MUST NOT affect the resulting envelope.

Collections in version `0.1.0` are semantically set-like. If a future obligation requires sequencing, sequencing MUST be represented explicitly rather than inferred from array position.

## Digest algorithm v1

The v1 digest is domain-separated with the exact UTF-8 string:

`monad.execution-envelope.v1`

The digest input MUST encode fields in the following semantic order:

1. domain separator;
2. `schema_version`;
3. `work_subject`;
4. `intent`;
5. `requested_outcome`;
6. `governing_state_digest`;
7. normalized governed references;
8. initiating actor fields;
9. executor actor fields;
10. normalized granted capabilities;
11. normalized prohibited capabilities;
12. normalized allowed tools;
13. normalized environment constraints;
14. normalized acceptance criteria;
15. normalized verification obligations;
16. normalized approval gates;
17. normalized escalation conditions;
18. normalized completion criteria;
19. normalized resource-limit entries.

For v1, scalar strings are encoded as an unsigned 64-bit big-endian byte length followed by exact UTF-8 bytes. Collection sizes are encoded as unsigned 64-bit big-endian integers. Optional strings are prefixed by one byte (`0x00` absent, `0x01` present), followed by normal string encoding when present. The final digest is SHA-256 over this domain-separated byte stream.

`run_id`, binding/logical time, adapter session identity, checkpoints, operation results, evidence, and verification results MUST NOT participate in the envelope digest.

## Run binding

A governed execution run MUST bind the runtime execution identity to an immutable envelope through a separate run-binding/runtime record. At minimum, the runtime layer must be able to identify:

- `run_id`;
- `envelope_id`;
- binding/logical time where required;
- adapter/executor session identity where required;
- current run state;
- checkpoint/evidence/operation history according to the technical and interface specifications.

Rebinding to a materially different envelope MUST be an explicit successor/recompilation event. A runtime MUST NOT preserve a stale `envelope_id` while applying materially changed governing semantics.

## Serialization rules

1. The normative machine representation is JSON conforming to `schemas/execution-envelope.schema.json`.
2. Canonical producers MUST emit all required fields, including empty arrays/maps when no obligations of that category apply.
3. Unknown top-level fields are not permitted in schema version `0.1.0`.
4. Optional `content_digest` is omitted when absent rather than serialized as `null`.
5. Identifiers and digest strings are case-sensitive except where their own governing namespace states otherwise.
6. SHA-256 values defined by this contract use lowercase hexadecimal.
7. JSON object member order MUST NOT be used to infer semantics. Digest identity is defined by the algorithm above, not by hashing arbitrary serialized JSON bytes.

## Security and trust semantics

1. An envelope is authoritative only to the degree established by its provenance, governing-state validity, approvals, and applicable EOS policy; possession of a syntactically valid envelope is not itself authorization.
2. Consumers MUST treat executor/model-provided envelope fields as untrusted unless they are validated against Monad-compiled identity and governing state.
3. A consumer MUST reject an envelope when `envelope_id` does not correspond to `envelope_digest`.
4. A governed run MUST detect material stale-state conditions before consequential work according to TECH-HARNESS-0001.
5. An adapter MUST NOT reinterpret an absent grant, missing obligation, or schema incompatibility as relaxed authority.
6. Private model reasoning is outside this data contract and MUST NOT be required to reproduce or validate envelope identity.

## Compatibility and evolution

`schema_version` versions the serialized contract. Digest algorithm changes are independently visible through the `env-vN-` identity prefix/domain separator.

A backward-compatible schema revision MAY tighten descriptions or add constraints that do not reject previously conforming semantic values. Adding a required field, changing field meaning, changing normalization semantics, changing the digest byte stream, or changing authorization meaning requires an intentional compatibility decision and appropriate version transition.

Adapters MUST negotiate supported envelope versions as required by IFC-HARNESS-0001.

## Verification

Conformance tests MUST cover at least:

1. identical governed semantics produce identical `envelope_digest` and `envelope_id`;
2. different run IDs/binding times bound to the same envelope do not change envelope identity;
3. set-like input reordering/duplication does not change identity;
4. material governing-state change changes identity;
5. material authority/capability/acceptance/verification change changes identity;
6. serialized output conforms to `schemas/execution-envelope.schema.json`;
7. malformed envelope ID/digest combinations are rejected by semantic validation;
8. unknown schema-version incompatibility fails explicitly;
9. no runtime/session/checkpoint field is accepted as part of schema version `0.1.0`;
10. private executor reasoning is neither serialized nor required for identity reproduction.
