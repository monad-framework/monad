# Product Capabilities

Capabilities describe durable abilities independent of a particular interface
or component. They are the bridge between user outcomes and architecture.

## Capability map

### C-01 — Identity and access

Authenticate actors, establish session context, authorize actions and evidence,
and apply least privilege. Initial maturity: one supported identity authority
with explicit roles and resource checks.

### C-02 — Intent and input management

Capture the desired outcome and required inputs, preserve drafts, classify
data, and explain validation. Initial maturity: the primary workflow's bounded
input model and safe import path.

### C-03 — Policy and validation

Evaluate structural, semantic, authorization, and safety rules before effects
are committed. Rules must be versioned, explainable, and testable.

### C-04 — Workflow coordination

Create one traceable instance, enforce allowed transitions, coordinate work,
handle idempotency, and manage retry, compensation, and cancellation.

### C-05 — Result verification

Evaluate postconditions, distinguish complete and partial outcomes, associate
evidence, and communicate justified status.

### C-06 — Evidence and audit

Record minimum necessary actor, action, policy, state, and result facts; enforce
access and retention; support authorized reconstruction.

### C-07 — Experience delivery

Present accessible, responsive, and consistent user interactions across the
supported journey, including progress and recovery.

### C-08 — Operations and assurance

Measure health and cost, manage configuration and releases, detect threats and
failures, restore service, and produce quality-gate evidence.

## Capability dependencies

The primary journey composes all eight capabilities. Workflow coordination may
depend on identity, validation, and evidence contracts but should not embed
their policies. Experience delivery consumes stable contracts and does not own
authoritative workflow state. Operations observes every critical capability
without becoming a runtime dependency for ordinary success.

## Maturity scale

- **M0 Unproven:** intent exists without tested behavior.
- **M1 Bounded:** one supported path with manual exceptions.
- **M2 Reliable:** objectives, recovery, and ownership are demonstrated.
- **M3 Scalable:** capacity and repeatability are proven across expected load.
- **M4 Extensible:** controlled variation is supported through stable contracts.

The first release targets M2 for the primary path and at least M1 for supporting
administrative paths. A capability cannot claim maturity when its security,
operability, or recovery evidence is missing.
