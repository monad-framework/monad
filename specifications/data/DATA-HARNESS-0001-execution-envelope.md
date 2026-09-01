# DATA-HARNESS-0001: Execution Envelope Data Contract

**Status:** proposed  
**Version:** 0.1.0  
**Owner:** Monad Core / EOS  
**Related requirements:** FR-007, FR-017, FR-023, FR-024, FR-029, FR-037, FR-038, FR-039, FR-040, FR-041, FR-042, QR-001, QR-003, QR-010, QR-014, QR-021, QR-022, QR-023  
**Governing ADRs:** ADR-0006, ADR-0007  
**Governing technical specification:** TECH-HARNESS-0001  
**Related interface:** IFC-HARNESS-0001

## Purpose and scope

Defines the canonical serialized data contract for a Monad Execution Envelope. The envelope is the immutable, inspectable contract that binds bounded work to the governing engineering state, actors, capabilities, tools, environment constraints, acceptance obligations, approvals, escalation rules, completion rules, and resource limits under which governed execution may occur.

This specification defines semantic fields, canonicalization, identity, compatibility, and validation. It does not define executor cognition, transport, provider-specific prompting, or the operation/evidence event formats that occur after a run begins.

## Core invariants

1. A bound Execution Envelope MUST be immutable.
2. The envelope MUST identify the exact governing state used to compile it.
3. Missing mandatory authority or capability data MUST NOT be interpreted as permission.
4. Set-like fields MUST have deterministic canonical ordering and duplicate elimination before identity is derived.
5. Equivalent serialized semantic content under the same schema version MUST yield the same envelope digest and identifier.
6. Any material change to an identity-bearing field MUST yield a different envelope digest and identifier.
7. Private model reasoning or chain-of-thought MUST NOT be a required envelope field.
8. Raw secrets SHOULD NOT appear in an envelope; secret access SHOULD be represented through governed capability/reference semantics.

## Canonical top-level object

Version `0.1.0` MUST support the following top-level members:

| Field | Type | Required | Semantics |
| --- | --- | --- | --- |
| `envelope_id` | string | yes | Content-derived envelope identifier. Version 0.1.0 uses `env-v1-<sha256-hex>`. |
| `envelope_digest` | string | yes | Lowercase SHA-256 hexadecimal digest of canonical identity-bearing content. |
| `schema_version` | string | yes | Execution Envelope schema version. |
| `run_id` | string | yes | Governed run identity to which this envelope is bound. |
| `logical_time` | string | yes | Governed logical/temporal binding used by the compiler. |
| `work_subject` | string | yes | Stable identifier of the bounded work subject. |
| `intent` | string | yes | Human/governance-legible statement of intended work. |
| `requested_outcome` | string | yes | Expected result of the bounded work. |
| `governing_state_digest` | string | yes | Digest/identity of the authoritative governing state used for compilation. |
| `governed_references` | array | yes | Applicable requirements, specifications, ADRs, policies, evidence, or other governed references. |
| `initiating_actor` | object | yes | Accountable actor that initiated/authorized the governed run. |
| `executor` | object | yes | Actor identity representing the bound executor/adapter role. |
| `granted_capabilities` | array | yes | Explicit positive grants. Absence of a grant is denial. |
| `prohibited_capabilities` | array | yes | Explicit prohibitions retained for audit and conflict detection. |
| `allowed_tools` | array[string] | yes | Tool/interface identifiers eligible for mediated use. |
| `environment_constraints` | array[string] | yes | Reproducibility, filesystem, network, process, service, or environment restrictions. |
| `acceptance_criteria` | array[string] | yes | Observable criteria governing candidate acceptance. |
| `verification_obligations` | array[string] | yes | Required verification checks/evidence classes. |
| `approval_gates` | array[string] | yes | Approvals required before defined effects/transitions. |
| `escalation_conditions` | array[string] | yes | Conditions requiring suspension/transfer to accountable authority. |
| `completion_criteria` | array[string] | yes | Conditions required before governed completion may be established. |
| `resource_limits` | object[string,string] | yes | Named execution budgets/limits expressed in canonical policy-defined units. |

An implementation MAY add optional fields in a backward-compatible schema revision only when their absence preserves existing authorization, verification, and identity semantics. Unknown mandatory semantics require an incompatible schema version or negotiated extension.

## Governed reference

Each `governed_references` entry MUST contain:

- `kind`: governed artifact/reference class;
- `identifier`: stable identifier within that class;
- optional `content_digest`: immutable content identity when available or required by policy.

A reference without a content digest MAY be valid when the governing state digest is sufficient to bind resolution, but policy MAY require per-reference digests for high-consequence execution.

## Actor identity

`initiating_actor` and `executor` MUST contain:

- `actor_id`: stable attributable actor identity;
- `role`: role under which the actor participates in this run.

Actor identity does not itself grant authority. Authority and capabilities are independently resolved by Monad governance.

## Capability grant

Each capability entry MUST contain:

- `capability`: versioned capability identifier;
- `scope`: canonical scope expression.

A capability entry MUST NOT be interpreted more broadly than its declared scope. If a capability appears in both granted and prohibited collections for an overlapping scope, the compiler or pre-execution validator MUST fail closed unless an explicit precedence rule in governing policy resolves the conflict.

## Canonicalization and identity

Version `0.1.0` uses the domain separator `monad.execution-envelope.v1` and SHA-256.

Before digest derivation, the compiler MUST normalize these set-like fields by deterministic ascending order and duplicate elimination:

- `governed_references`;
- `granted_capabilities`;
- `prohibited_capabilities`;
- `allowed_tools`;
- `environment_constraints`;
- `acceptance_criteria`;
- `verification_obligations`;
- `approval_gates`;
- `escalation_conditions`;
- `completion_criteria`.

`resource_limits` MUST be traversed in deterministic key order.

The identity-bearing sequence for version `0.1.0` is:

1. `schema_version`;
2. `run_id`;
3. `logical_time`;
4. `work_subject`;
5. `intent`;
6. `requested_outcome`;
7. `governing_state_digest`;
8. normalized governed references including optional content digests;
9. initiating actor identity and role;
10. executor identity and role;
11. normalized granted capabilities;
12. normalized prohibited capabilities;
13. normalized allowed tools;
14. normalized environment constraints;
15. normalized acceptance criteria;
16. normalized verification obligations;
17. normalized approval gates;
18. normalized escalation conditions;
19. normalized completion criteria;
20. deterministically ordered resource limits.

The compiler MUST length-frame strings/collections or use an equivalently unambiguous canonical encoding. The digest MUST NOT be calculated from ordinary pretty-printed JSON whose whitespace, object-key order, or serializer settings can vary.

`envelope_digest` and `envelope_id` are derived outputs and MUST NOT participate recursively in their own digest calculation.

## Validation

An envelope is invalid for governed execution when any of the following holds:

- required field missing or malformed;
- unsupported schema version;
- envelope identifier does not match the derived digest;
- governing state cannot be resolved or fails applicable freshness policy;
- required governed reference cannot be resolved;
- actor/executor identity cannot be established;
- contradictory capability state cannot be safely resolved;
- mandatory acceptance, verification, approval, or completion obligation cannot be represented;
- resource-limit syntax cannot be interpreted under applicable policy;
- adapter cannot support mandatory envelope semantics.

Invalid envelopes MUST fail closed before consequential governed effects.

## Immutability and succession

A bound envelope MUST NOT be edited in place. Material change requires compilation of a new envelope.

When a run is suspended and later resumes under a replacement envelope, durable execution evidence MUST preserve the predecessor/successor relationship and identify which operations occurred under each envelope.

## Serialization

The default interchange representation SHOULD be UTF-8 JSON using snake_case field names matching this specification. Other representations MAY be supported if they preserve all semantics and round-trip to the same canonical identity-bearing values.

Serialization intended for human inspection MAY include presentation-only metadata, but presentation metadata MUST be explicitly non-authoritative and MUST NOT silently affect the envelope digest.

## Compatibility

Schema versions are independent from provider, adapter, and model versions.

Backward-compatible revisions MAY add optional representational conveniences whose absence cannot weaken governance. Any change that alters field meaning, digest semantics, authority/capability interpretation, verification meaning, or mandatory obligations requires explicit compatibility treatment and normally a new incompatible schema version/domain separator.

## Security and privacy

- Treat all executor/provider-originated data as untrusted.
- Never infer capability from the presence of a tool alone.
- Minimize sensitive context before serialization to external adapters/providers.
- Prefer opaque secret/capability references over secret values.
- Detect stale or replayed envelopes before consequential effects.
- Preserve integrity-verifiable envelope identity in execution evidence.

## Verification

Conformance MUST demonstrate:

1. deterministic identity for equivalent normalized inputs;
2. identity change after every material identity-bearing field change;
3. order/duplicate normalization for set-like fields;
4. deterministic resource-limit ordering;
5. identifier/digest mismatch rejection;
6. unsupported schema-version rejection;
7. stale governing-state rejection/suspension according to policy;
8. contradictory capability state fails closed;
9. secret references can be represented without embedding raw secret material;
10. JSON round-trip preserves semantic values and identity;
11. two conforming adapter implementations can consume semantically equivalent envelope obligations;
12. private chain-of-thought is not required to compile, execute, verify, or audit an envelope.
