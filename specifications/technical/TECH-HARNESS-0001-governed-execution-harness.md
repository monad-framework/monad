# TECH-HARNESS-0001: Governed Execution Harness

**Status:** proposed  
**Version:** 0.1.0  
**Owner:** Monad Core / EOS  
**Related requirements:** pending harness requirements tranche  
**Governing ADRs:** ADR-0006, ADR-0007

## Purpose and scope

Defines the minimum normative behavior of Monad's Governed Execution Harness (GEH): compilation of governed work into an Execution Envelope, capability- and policy-mediated operation execution, run-state management, evidence/provenance capture, escalation, and verification-controlled completion.

This specification defines the stable execution-governance boundary. It does not prescribe model selection, prompting, internal reasoning/planning techniques, IDE behavior, or a particular third-party agent harness.

## Architectural invariant

**Monad governs agent execution but does not prescribe agent cognition.**

The harness governs observable intent, inputs, authority, capabilities, operations, effects, evidence, verification, and lifecycle transitions. An executor remains free to choose internal planning/reasoning behavior so long as it conforms to the governed boundary.

## Preconditions

A governed execution MAY begin only when:

1. a resolvable work subject/intent exists;
2. the governing EOS/canonical state is readable and passes the minimum integrity checks required by policy;
3. accountable actor/executor identity can be established;
4. applicable authority and policy can be resolved sufficiently to determine execution rights;
5. a versioned Execution Envelope can be compiled;
6. required approval gates that precede execution are satisfied.

If a precondition cannot be established, the harness MUST fail closed or route the execution to an explicit escalation state. It MUST NOT infer broader authority from missing data.

## Logical components

An implementation MUST provide behavior equivalent to the following logical components. Components MAY share a process/module and MAY be implemented incrementally.

1. **Context Compiler** — produces the minimum authoritative context projection required for the governed work.
2. **Authority Resolver** — resolves which artifacts/actors control disputed or consequential decisions.
3. **Policy Integration** — evaluates governing policies before operations and transitions.
4. **Capability Broker** — produces explicit least-privilege grants/prohibitions.
5. **Execution Envelope Compiler** — freezes the governed execution input contract.
6. **Tool Gateway** — mediates consequential executor operations.
7. **Run-State/Checkpoint Manager** — manages harness-local execution state without replacing EOS canonical lifecycle state.
8. **Approval/Escalation Controller** — routes cases that exceed delegated authority or policy.
9. **Evidence/Provenance Recorder** — captures attributable observable evidence.
10. **Verification Controller** — evaluates completion obligations and emits verification results.

## Execution Envelope

### Identity and immutability

Each envelope MUST have:

- a globally or repository-uniquely distinguishable `envelope_id`;
- a schema/version identifier;
- a `run_id` or execution identity when bound to a run;
- a creation timestamp or deterministic logical time reference as appropriate;
- identifiers/hashes sufficient to detect material governing-state drift.

After a run begins, the bound envelope MUST be immutable. A material governing-state change requiring different authority, policy, constraints, or acceptance obligations MUST cause one of:

1. run suspension and explicit recompilation into a new envelope/version;
2. escalation for authority review;
3. cancellation.

The harness MUST NOT silently mutate the envelope in place.

### Minimum envelope domains

The serialized schema SHALL be defined separately, but the envelope model MUST be able to represent at least:

#### Work

- intent;
- work subject(s);
- requested outcome;
- scope boundaries;
- dependencies/prerequisites when known.

#### Governance

- governing requirements;
- governing specifications;
- governing ADRs/decisions;
- applicable policies;
- accountable authority;
- unresolved decisions/claims that may affect execution;
- governing-state identity/digest.

#### Actor and capabilities

- initiating actor;
- executor identity/role;
- granted capabilities;
- explicit prohibitions;
- delegation constraints;
- approval authority and escalation targets where applicable.

#### Environment and tools

- allowed tool/interface identifiers;
- filesystem/workspace boundaries;
- process/network/service constraints;
- environment identity sufficient for reproducibility policy;
- secrets/credential references as capabilities, never raw secret values in the envelope unless explicitly required and policy-authorized.

#### Quality and completion

- acceptance criteria;
- verification obligations;
- required evidence classes;
- approval gates;
- escalation conditions;
- completion criteria.

#### Resource controls

Where policy requires, the envelope MUST represent applicable time, cost, token/model, operation-count, concurrency, storage, or other budgets/limits.

## Run lifecycle

A conforming harness MUST support the following conceptual lifecycle:

`requested -> compiling -> ready -> running -> {waiting_approval | waiting_input | verifying | suspended | failed | cancelled} -> {running | completed | failed | cancelled}`

Exact state names MAY differ, but the implementation MUST preserve distinguishable semantics for:

- envelope compilation;
- ready but not yet executing;
- active execution;
- waiting for external authority/input;
- verification;
- suspension/checkpoint;
- failure;
- cancellation;
- governed completion.

Harness run state MUST NOT replace Work Packet/EOS lifecycle state. The harness MAY project or request EOS transitions only through the existing governance boundary.

## Operation request model

An executor MUST request consequential effects through the Tool Gateway or an equivalent mediated operation interface when claiming governed execution.

Each governed operation request MUST be attributable to:

- `run_id`;
- envelope identity/version;
- executor/actor identity;
- requested capability/tool;
- operation type;
- target/resource scope;
- material parameters or a canonical digest of them;
- causal parent/delegation identity where applicable.

Before execution, the gateway MUST evaluate at minimum:

1. envelope validity and stale-state policy;
2. capability grant/prohibition;
3. applicable policy;
4. target/scope containment;
5. required approval state;
6. resource-budget constraints where applicable.

A denied operation MUST produce an attributable diagnostic/evidence record and MUST NOT be executed through the governed path.

## External and unmediated effects

Monad cannot guarantee mediation of effects performed outside a Monad-controlled boundary. If an executor performs or claims an external effect that cannot be verified through the gateway, the harness MUST classify it explicitly as external, unverified, partially verified, or equivalent according to evidence policy.

Such an effect MUST NOT be silently promoted to governed/verified status solely because the executor reports success.

## Context compilation

The Context Compiler MUST prefer authoritative, applicable, and sufficiently fresh governed knowledge over broad repository dumping.

Compilation SHOULD:

- select the minimum context needed to execute safely;
- preserve source identity and authority/provenance references;
- distinguish normative constraints from explanatory/non-authoritative material;
- expose unresolved conflicts rather than silently choosing a convenient source;
- minimize sensitive information before projection to external providers;
- produce a reproducible compilation record or digest where feasible.

The compiled context MAY be rendered differently for different adapters/models, but semantic governing obligations MUST remain equivalent.

## Capability semantics

Capabilities MUST be explicit and least-privilege.

1. Missing capability grants MUST be treated as denied.
2. A child/delegated execution MUST NOT receive broader capabilities than its parent unless a separate accountable authority explicitly grants them.
3. Capability checks MUST be independent of executor/model assertions.
4. Capability grants SHOULD be scoped by operation, target/resource, duration/run, environment, and other constraints needed to make the grant safe.
5. Secrets, network access, production effects, release/publish actions, destructive filesystem operations, and governance mutation SHOULD require separate high-sensitivity capabilities/policies.

## Approval and escalation

The harness MUST support explicit escalation without treating escalation as execution failure.

Escalation conditions MAY include:

- unresolved or contradictory governing authority;
- requested operation outside delegated capability;
- material scope expansion;
- policy-required human approval;
- high-risk or irreversible effect;
- stale governing state;
- failed verification requiring a decision rather than another retry;
- resource/budget threshold;
- executor uncertainty surfaced according to policy.

Approval MUST be attributable to an authorized actor and bound to the relevant run/envelope/decision scope.

## Evidence and provenance

The harness MUST record sufficient observable information to reconstruct governed execution without requiring storage of private model reasoning.

At minimum, evidence/provenance MUST support attribution of:

- envelope and governing-state identity;
- initiating actor and executor identity;
- approvals/escalations;
- consequential operation requests;
- policy/capability decision result;
- effect result/status;
- produced artifacts or artifact digests where applicable;
- verification inputs/results;
- terminal run state.

Transcript storage MAY be configurable and MUST NOT be the sole evidence mechanism.

## Verification and completion

An executor's declaration that work is complete is advisory only.

A governed `completed` state MUST require the Verification Controller to establish that the envelope's completion and verification obligations have been satisfied to the level required by policy.

Verification MAY include deterministic tests, structural/semantic checks, review evidence, independent harness review, human approval, runtime observation, reproducibility checks, or other governed evidence.

If required verification cannot be performed, the run MUST remain incomplete, fail, or escalate according to policy. It MUST NOT default to success.

## Failure, retry, checkpoint, and recovery

The harness MUST distinguish operation failure, executor failure, verification failure, policy denial, stale-envelope suspension, cancellation, and escalation.

Retry behavior MUST NOT broaden capabilities or erase prior evidence.

Checkpoint/resume MUST preserve:

- original run/envelope identity or an explicit parent/successor relationship;
- previously executed consequential effects;
- evidence already produced;
- remaining budgets/limits where applicable;
- governing-state drift detection before resumed consequential work.

Cancellation MUST prevent new governed operations after the cancellation becomes authoritative, except operations explicitly required and authorized for safe rollback/recovery.

## Adapter neutrality

The GEH MUST NOT require a specific model provider or agent harness.

Adapters MAY optimize context presentation, streaming, tool-call transport, or session handling, but MUST NOT alter governing semantics.

Adapter-specific extensions MUST be namespaced/versioned and MUST NOT weaken core policy/capability/verification requirements.

## Local-first and backend-neutral operation

The core envelope compiler, policy/capability checks required for local governed work, operation mediation, evidence capture, and verification control SHOULD operate without mandatory dependence on a hosted Monad service.

Remote models, CI systems, cloud sandboxes, or provider APIs MAY be used as tools/environments when explicitly authorized.

## Security requirements

1. The gateway MUST treat executor/model output as untrusted input.
2. Tool arguments MUST be validated against capability and target constraints before execution.
3. Governing-state ambiguity MUST fail closed when it prevents a safe decision.
4. Sensitive context projection MUST honor policy and provider/network boundaries.
5. Secret material MUST be redacted from ordinary evidence records unless policy explicitly requires protected retention.
6. Evidence records MUST be tamper-evident or integrity-verifiable when required by governance policy.
7. Stale/replayed envelopes MUST be detectable.
8. Adapter identity/version and material executor configuration SHOULD be recorded when needed for reproducibility/accountability.

## Conformance verification

Initial conformance fixtures MUST cover:

1. deterministic envelope compilation from identical governed state;
2. stale governing-state detection;
3. denied ungranted capability;
4. denied explicitly prohibited operation;
5. scoped filesystem/tool success inside grant boundaries;
6. approval-gated operation pause and authorized resume;
7. failed verification preventing completion;
8. executor-reported success without evidence remaining incomplete;
9. cancellation preventing subsequent governed effects;
10. checkpoint/resume preserving prior effect/evidence history;
11. child delegation narrowing capabilities;
12. two distinct adapter implementations receiving semantically equivalent governing obligations;
13. local-first execution with no mandatory cloud control-plane dependency.

## Implementation sequence

Implementation SHOULD proceed in the following order:

1. define typed envelope/run/operation/result contracts;
2. implement deterministic envelope compilation and inspect/dry-run output;
3. implement capability/policy-mediated Tool Gateway for one bounded local operation family;
4. add run-state/checkpoint/cancellation semantics;
5. integrate evidence/provenance recording;
6. integrate verification-controlled completion;
7. implement one external harness adapter;
8. implement a second materially different adapter to validate portability;
9. add reference agent only after adapter conformance is proven;
10. add separate evaluation/conformance harness.

## Deferred specifications

The following are intentionally deferred to separate artifacts:

- serialized Execution Envelope schema;
- generic Agent Harness Adapter interface/protocol;
- tool/capability schema extensions;
- evidence/provenance event schema;
- evaluation benchmark format;
- provider-specific adapters;
- multi-agent delegation/orchestration policy.
