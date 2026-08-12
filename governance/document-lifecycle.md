# Document Lifecycle

Project documents are controlled records when they govern behavior, decisions,
work, risk, or evidence. Control should make the current truth easy to find
without destroying historical context.

## Status model

- **Draft:** under authorship; not approved for reliance.
- **Review:** complete enough for designated review.
- **Approved:** authoritative within its stated scope.
- **Implemented:** approved intent is reflected in the delivered system where
  that distinction matters.
- **Deprecated:** still relevant during transition but scheduled for retirement.
- **Superseded:** replaced by an identified newer record.
- **Retired:** no longer applicable; retained only for history.

README indexes and operational status pages may be living records rather than
versioned approvals, but they still require an owner and current information.

## Required metadata

Normative documents identify title, stable ID where applicable, status, owner,
reviewers, effective or approval date, version, scope, related records, review
trigger, and supersession. Version-control history does not replace explicit
status when readers need to know which record governs.

## Review and approval

The owner verifies structure, traceability, terminology, and evidence before
review. Required reviewers evaluate their concerns and declare conditions or
dissent. Approval identifies the authority and effective scope. A missing
required review cannot be inferred from merge permission.

## Change types

- Editorial changes improve clarity without changing meaning.
- Minor changes add compatible detail within the approved intent.
- Major changes alter behavior, scope, control, authority, or accepted risk.

Minor and major changes update version and impact links. Major changes follow
change control and may require a superseding record.

## Review triggers

Review on the document's stated cadence and after conflicting evidence,
incident, regulatory or dependency change, architecture decision, repeated
exception, ownership change, or affected product change. Overdue review does
not automatically invalidate the document, but its status is made visible and
risk assessed.

## Retirement

Before retirement, verify that no current requirement, specification, decision,
work packet, runbook, or external reference depends on the record. Add the
replacement or reason, retirement date, and owner. Never reuse stable IDs.
