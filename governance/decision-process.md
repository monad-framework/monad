# Decision Process

## Decision classes

### Class 1 — Local and reversible

Limited to one owned area, low consequence, easy to reverse, and compliant with
approved contracts. The responsible owner decides and records the result in the
work artifact or review.

### Class 2 — Cross-cutting or durable

Affects multiple owners, a public contract, architecture, data handling,
operability, cost, or meaningful migration. Use a decision record or ADR and
obtain affected-owner review.

### Class 3 — Strategic or high consequence

Changes vision, legal or ethical posture, high-severity risk, irreversible
commitment, production exposure, or business viability. Requires the accountable
authority, documented evidence, dissent, and explicit approval.

## Standard process

1. **Frame:** state the decision, owner, deadline, affected scope, and cost of
   delay.
2. **Establish drivers:** rank outcomes, constraints, risks, and quality needs.
3. **Gather evidence:** distinguish facts, assumptions, forecasts, and unknowns.
4. **Develop options:** include credible alternatives and the status quo.
5. **Evaluate:** compare benefits, harms, cost, failure modes, reversibility, and
   migration using the same criteria.
6. **Consult:** obtain input from affected owners and people bearing material
   consequences.
7. **Decide:** record choice, rationale, authority, conditions, and dissent.
8. **Implement and verify:** link work and evidence; review assumptions at the
   stated trigger.

## Decision record

A material record includes ID, status, date, owner, participants, question,
context, drivers, options, evidence, decision, consequences, risks, actions,
review trigger, and supersession links. Chat discussion may inform the record
but is not the authoritative decision.

## Consent and dissent

Consensus is useful but not mandatory. Required reviewers may approve, approve
with conditions, abstain, or object with evidence and impact. The accountable
owner resolves disagreement within their authority and preserves material
dissent so later reviews understand the uncertainty.

## Decision latency

Set a decision deadline proportional to consequence and cost of delay. If
evidence cannot be obtained in time, prefer the safest reversible option or
reduce exposure. Silence is not approval unless a documented process explicitly
defines it for low-risk changes.

## Reconsideration

Reopen a decision when its stated trigger fires, a key assumption fails,
consequence changes materially, or new evidence makes the accepted option
unsafe or clearly inferior. Supersede the prior record rather than erasing it.

## AI Participation in Decisions

AI MAY participate throughout the decision process by:

- framing questions;
- identifying missing information;
- gathering and organizing evidence;
- identifying assumptions and unknowns;
- generating credible alternatives;
- analyzing consequences and reversibility;
- recommending a decision;
- drafting a decision record;
- identifying reconsideration triggers.

AI participation does not itself constitute a decision.

A consequential AI recommendation MUST remain distinguishable from:

- the authoritative decision;
- approval;
- authorization;
- acceptance.

Material ambiguity MUST be surfaced rather than silently resolved by model
inference when different interpretations could materially affect product,
architecture, security, privacy, operations, legal posture, accepted risk,
irreversible commitments, authority, or acceptance.

Where governance requires a `DEC`, `APR`, ADR, CR, review, or other native
record, conversation history or model output alone is insufficient.

A governed denial is authoritative within its scope. AI MAY propose a materially
different conforming alternative or revisit the matter when new material
governed evidence exists, but MUST NOT repeatedly pressure for the same rejected
outcome merely to obtain a different answer.
