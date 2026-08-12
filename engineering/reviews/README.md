# Engineering Reviews

Reviews are decision records supported by evidence. They determine whether an
artifact, packet, increment, milestone, release, incident follow-up, or risk is
acceptable for its next lifecycle state.

## Review types

- **Design review:** verifies drivers, boundaries, trade-offs, and validation.
- **Packet review:** accepts a completed work result against its criteria.
- **Cycle review:** inspects integrated progress, flow, risk, and forecast.
- **Increment review:** accepts or redirects an integrated product advance.
- **Release review:** evaluates product, quality, security, operational, and
  change evidence before exposure.
- **Post-incident review:** identifies contributing system conditions and owned
  corrective work without blame.

## Record format

Name records `<TYPE>-NNNN-YYYY-MM-DD-short-subject.md` and include scope,
participants and roles, evidence reviewed, findings by severity, decisions,
conditions, dissent, accepted risks, action owners and dates, and follow-up
review. Link source evidence rather than copying mutable summaries.

## Finding severity

- **Blocking:** safety, correctness, security, compatibility, or acceptance
  failure that prevents the requested state transition.
- **Required follow-up:** acceptable within current exposure only with an owner
  and date.
- **Advisory:** improvement that does not block the reviewed outcome.

## Independence and closure

Authors may explain and demonstrate but should not be the sole acceptance
authority for consequential work. A reviewer declares conflicts and recuses
when impartiality is compromised. Every finding is resolved, accepted with
explicit authority, converted to owned work, or rejected with rationale before
the review closes.
