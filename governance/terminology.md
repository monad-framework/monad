# Terminology

Shared language reduces ambiguity across product, architecture, engineering,
security, and operations. Terms use their definitions here unless a scoped
specification explicitly narrows them.

| Term | Definition |
| --- | --- |
| Acceptance criterion | Observable condition and evidence required to accept a bounded result. |
| Actor | A person, role, service, or system that interacts with a defined boundary. |
| Artifact | Versioned output such as code, document, package, image, evidence, or release. |
| Baseline | Approved reference state against which change or outcome is evaluated. |
| Capability | Durable ability required to produce an outcome, independent of implementation. |
| Contract | Explicit, testable agreement at a boundary, including success and failure behavior. |
| Control | Policy, process, or mechanism that changes the likelihood or impact of a risk. |
| Evidence | Verifiable information supporting a claim, decision, control, or acceptance. |
| Guardrail | Measure that prevents improvement of one outcome by causing unacceptable harm elsewhere. |
| Idempotent | Produces no additional consequential effect when the same operation is safely repeated. |
| Increment | Integrated, potentially releasable advance toward a milestone outcome. |
| Invariant | Condition that must remain true across all allowed states and transitions. |
| Milestone | Major outcome and decision gate composed of one or more increments. |
| Outcome | Observable change in user, system, risk, or operational state—not work performed. |
| Persona | Evidence-based behavioral model of users sharing material goals and constraints. |
| Policy | Versioned rule or set of rules governing a decision or allowed behavior. |
| Recovery | Return to a defined safe state through retry, restore, reconciliation, compensation, or escalation. |
| Requirement | Identified, testable product behavior or quality obligation. |
| Risk | Uncertainty that may affect objectives; represented by cause, event, and consequence. |
| Service objective | Target reliability or performance level used to manage a service. |
| Specification | Normative, testable detail implementing an approved requirement or contract. |
| Trust boundary | Crossing where identity, authority, data protection, or validation assumptions change. |
| Verified result | Outcome whose defined postconditions have been checked against authoritative evidence. |
| Work cycle | Fixed, short execution and learning window within an increment. |
| Work packet | Smallest authorized unit producing one independently reviewable result. |

## Usage rules

Avoid using `user` when a specific actor matters, `done` without its acceptance
scope, `real time` without a latency bound, `secure` without a threat and
control, `available` without a measurement window, or `compliant` without named
obligations and evidence. Add terms when inconsistent interpretation changes a
decision or test; do not expand the glossary with ordinary language.
