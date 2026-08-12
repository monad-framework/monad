# Change Control

Change control ensures that modifications to baselined behavior, architecture,
data, operations, or governance are evaluated, approved, implemented, and
verified at the level their consequence requires.

## Change classes

- **Standard:** pre-authorized, repeatable, low-risk change with tested procedure
  and rollback.
- **Normal:** planned change requiring scoped impact analysis and designated
  approval.
- **Major:** cross-cutting, irreversible, public-contract, sensitive-data,
  strategic, or high-risk change requiring formal review.
- **Emergency:** minimum change needed to contain active harm or restore service,
  followed by retrospective control completion.

## Change request content

Every normal or major change states purpose, scope, affected requirements and
systems, user impact, dependencies, security and privacy impact, data and
migration behavior, service risk, test and observability evidence, deployment
plan, rollback or compensation, communication, owner, window, and approvers.

## Workflow

1. Submit and classify the change.
2. Identify affected owners and source-of-truth documents.
3. Evaluate impact, failure modes, compatibility, capacity, cost, and timing.
4. Produce required decision, test, security, and operational evidence.
5. Approve, reject, or approve with explicit conditions.
6. Implement through the protected delivery path.
7. Verify technical health and user outcome during the observation window.
8. Close with evidence, update records, or initiate rollback and incident
   handling.

## Emergency changes

The incident commander may authorize the smallest reversible mitigation when
delay increases harm. Record who authorized it, what is changing, affected
scope, expected result, verification, and rollback. Do not bundle unrelated
improvements. Complete review, testing gaps, documentation, and durable repair
within the follow-up window set by incident severity.

## Failure and rollback

Stop when preconditions fail, unexpected impact exceeds threshold, verification
cannot establish safe state, or rollback capacity is lost. A rollback is a
planned change with its own verification. When data or external effects are not
reversible, use a tested forward fix or compensation and communicate residual
impact.

## Audit evidence

Retain the request, approval, artifact identity, provenance, deployment actor,
times, environment, automated and manual checks, observed result, rollback if
used, and linked incident or follow-up. Evidence access and retention follow
classification policy.
