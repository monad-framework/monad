# TECH-HARNESS-0002: Governed Workspace Read Backend

**Status:** proposed  
**Version:** 0.1.0  
**Owner:** Monad Core / EOS  
**Related requirements:** FR-022, FR-037, FR-038, FR-040, FR-041; QR-001, QR-003, QR-004, QR-007, QR-010, QR-021, QR-022, QR-023  
**Governing specifications:** TECH-HARNESS-0001, IFC-HARNESS-0001  
**Governing ADR:** ADR-0007

## Purpose

Defines the first concrete bounded local operation family executed through the Monad Governed Execution Harness (GEH): read-only UTF-8 file observation inside an explicitly governed workspace root.

The purpose of this backend is to prove that the deterministic C1 governance kernel can mediate a real local tool without granting write, process, network, release, deployment, or governance-mutation authority.

This backend does not constitute general filesystem capability.

## Operation family

Version 0.1.0 defines exactly one operation:

- tool: `workspace`;
- capability: `workspace.read`;
- operation type: `read_text`;
- target scope: one exact portable repository-relative file path.

The backend MUST reject any request that reaches it with a different tool, capability, or operation type.

The Tool Gateway remains authoritative for envelope/run/executor binding, governing-state freshness, capability/prohibition evaluation, exact scope containment, policy, approval, and cancellation. Backend validation is defense in depth and MUST NOT be interpreted as a substitute for gateway mediation.

## Path contract

A `read_text` target MUST be a portable repository-relative path represented with `/` separators.

Version 0.1.0 MUST reject:

- empty paths;
- absolute paths;
- empty path segments;
- `.` or `..` segments;
- backslash-separated paths;
- NUL-containing paths;
- drive/prefix-like segments containing `:`;
- any path containing a symbolic-link component;
- a target that resolves outside the canonical workspace root;
- non-regular-file targets, including directories, FIFOs, sockets, devices, and other special files.

These restrictions are intentionally narrower than a general host filesystem API. Broader path semantics require a versioned contract change rather than implicit relaxation.

## Read boundary

The backend MUST:

1. bind to a canonical existing workspace root at construction;
2. impose a non-zero maximum byte limit supplied by the caller or governing configuration;
3. inspect the resolved target metadata before opening and reject a non-regular target or a file whose observed size exceeds the limit;
4. only after that pre-open validation, open the target for reading;
5. inspect the opened file metadata again and reject a non-regular replacement or a size that now exceeds the limit;
6. bound the actual read to at most `max_bytes + 1` so concurrent growth cannot silently bypass the limit;
7. reject data exceeding the limit during the read;
8. accept UTF-8 text only in version 0.1.0;
9. compute a SHA-256 digest over the exact observed bytes;
10. return tool failure rather than partial/truncated success when the contract cannot be satisfied.

Pre-open file-type validation is required because opening some special files, such as a Unix FIFO without a writer, can block before post-open metadata can be inspected. The post-open metadata check remains required as defense against ordinary replacement races between validation and opening.

The backend MUST NOT write, create, delete, rename, execute, publish, deploy, contact a network service, or mutate governance state.

## Observation versus evidence

A successful file read produces two distinct outputs:

### Governed result/evidence metadata

The durable mediated result MAY contain:

- operation identity;
- executed-success disposition;
- content digest;
- target-relative evidence reference;
- gateway governance-check evidence.

Raw file contents MUST NOT be automatically embedded in the serialized mediated result or ordinary durable evidence merely because the operation succeeded.

### Transient observation

The executor-facing observation MAY contain:

- normalized relative path;
- UTF-8 text;
- byte length;
- content digest.

The observation is untrusted tool output. It does not grant authority, satisfy verification by itself, or become durable audit evidence unless a separate evidence-retention policy explicitly promotes it.

This separation implements the `IFC-HARNESS-0001` distinction between an observable `operation.result` and governed evidence/provenance retention.

## Failure semantics

Requests denied by the GEH gateway MUST NOT invoke the backend and MUST produce no workspace observation.

A request that passes governance but violates this backend contract MUST return `tool_failure` with an attributable diagnostic and no observation.

Backend failure MUST NOT be converted into capability denial, policy denial, or successful execution.

## Symlink and containment policy

Version 0.1.0 rejects symbolic-link components entirely, even when a symlink would currently resolve inside the workspace. This fail-closed rule avoids making symlink-following policy implicit.

The implementation MUST also canonicalize the final target and verify containment beneath the canonical workspace root as defense in depth.

Standard cross-platform path APIs cannot eliminate every hostile concurrent-filesystem time-of-check/time-of-use race. Pre-open and post-open metadata checks reduce avoidable blocking and replacement hazards but do not provide a race-free hostile-filesystem guarantee. Therefore this v0.1.0 backend is suitable for bounded local-first operation and conformance/dogfooding, but MUST NOT be represented as hardened against a concurrently malicious host filesystem. Production activation in such a threat model requires a handle-relative or equivalent race-resistant filesystem primitive and a corresponding contract revision/review.

## Resource and confidentiality constraints

The caller MUST provide a finite read-size bound appropriate to the run. Future integration SHOULD derive this bound from an explicit governed resource limit in the Execution Envelope rather than treating backend configuration as the only source.

File contents MAY contain secrets or sensitive information. Authorization to read a path does not automatically authorize durable retention or external-provider transmission of its contents. Adapter/context projection policy remains responsible for those boundaries.

## Conformance

The initial implementation MUST cover at least:

1. authorized exact-scope UTF-8 read returns the exact transient observation and matching digest;
2. raw observation content is absent from serialized governed result/evidence metadata;
3. gateway scope denial produces no observation;
4. parent traversal is rejected even if erroneously granted upstream;
5. absolute path is rejected even if erroneously granted upstream;
6. directory target is rejected;
7. byte limit is enforced;
8. non-UTF-8 data is rejected;
9. unsupported operation type is rejected without modifying the target;
10. symlink components are rejected on platforms supporting the fixture;
11. a pre-existing FIFO or equivalent blocking special file is rejected before opening on platforms supporting the fixture.

All existing C0 and C1 conformance MUST continue to pass.

## Activation boundary

Merging an implementation conforming to this specification authorizes only the existence of the bounded backend in Monad Core. It does not automatically grant any run `workspace.read`, does not authorize an external adapter, and does not activate a production execution policy.

A run may use the backend only when its immutable Execution Envelope, current governing state, capability grants, target scope, policy, approval state, and runtime state all permit the operation through the GEH gateway.
