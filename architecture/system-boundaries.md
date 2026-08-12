# System Boundaries

**Status:** Proposed stabilization baseline

## Monad owns

- repository/workspace knowledge discovery rules;
- Monad configuration/manifest resolution;
- supported engineering-artifact parsing/normalization;
- semantic identity and graph relationship rules;
- KIR contracts when activated;
- Monad diagnostics/conformance semantics;
- query/explain behavior over the semantic model;
- context-package selection/explanation;
- execution-plan semantics and adapter protocol where implemented;
- provenance of Monad-derived results.

## Monad does not own

- Git object/history semantics;
- language compiler correctness;
- package-manager dependency resolution outside explicit captured interfaces;
- native test-framework semantics;
- IDE editing state;
- GitHub's canonical PR/permission mechanics;
- cloud/provider correctness;
- an LLM provider's output semantics.

## Boundary invariants

1. Canonical repository reading MUST NOT execute repository code merely to discover meaning unless the user explicitly invokes an execution capability.
2. Adapter failures MUST remain distinguishable from Monad semantic failures.
3. Native tool failure MUST NOT be translated into semantic success.
4. Generated state MUST be rebuildable from canonical inputs or explicitly identified external evidence.
5. Agent context membership MUST NOT grant authority absent from the governing Work Packet/policy.
6. Remote/AI transmission MUST be an explicit boundary with context/data minimization.
7. Public stable boundaries MUST have versioning/compatibility rules before external consumers are promised stability.

## MVP boundary

MVP stops at local compilation/intelligence/context and bounded invocation needed for validation. Hosted collaboration, marketplace/registry scale, remote scheduling, organization-wide data planes, and autonomous deployment are external future concerns.