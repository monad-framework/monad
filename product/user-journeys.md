# User Journeys

## Primary journey: intent to verified outcome

| Stage | User goal | Product responsibility | Evidence | Failure recovery |
| --- | --- | --- | --- | --- |
| Discover | Decide whether this product fits the job | State promise, supported scope, prerequisites, and limits | Eligibility decision | Direct unsupported users to a safe alternative |
| Prepare | Gather valid inputs and authority | Explain requirements and validate progressively | Validation result | Preserve valid work and identify corrections |
| Review | Understand the intended effect | Summarize inputs, rules, consequences, and reversibility | Confirmation record | Allow edit or cancellation before commitment |
| Execute | Complete without losing control | Expose durable progress and prevent duplicate effects | Correlated state transitions | Retry, compensate, pause, or escalate safely |
| Verify | Know whether the outcome is complete | Check postconditions and distinguish partial results | Verification status and result | Explain unresolved work and responsible owner |
| Retain | Retrieve evidence when needed | Apply retention, access, and export rules | Authorized evidence record | Provide recovery or support route |

## Emotional and cognitive requirements

At entry, the user may be uncertain whether they have everything required. The
experience should reduce uncertainty through progressive validation rather than
front-loading unexplained fields. During execution, status must prevent the
user from guessing whether retry is safe. At completion, the product should
communicate justified confidence, not celebration that hides caveats.

## Interruption journey

1. Detect disconnect, timeout, dependency failure, or user departure.
2. Persist the last valid state and correlation identifier.
3. On return, show what completed, what did not, and whether any external effect
   may have occurred.
4. Offer only transitions valid for that state.
5. Verify the result after retry or compensation.
6. Escalate with evidence when automated recovery is unsafe.

## First-use journey

First use adds concise orientation, safe sample data where appropriate, and
explanations of permissions and data use. It must not create a separate
workflow that masks the real product. A representative new user should reach
the same verified result without private coaching.

## Operator journey

The operator moves from user-impact signal to scoped diagnosis, mitigation,
verification, communication, and follow-up. Dashboards and runbooks use the
same journey, state, and error vocabulary that users see so support does not
translate between incompatible models.

## Journey measurement

Measure eligibility, start, validation failure, confirmation, durable progress,
successful verification, partial result, abandonment, recovery, and repeat use.
Event definitions belong in the data specifications and must avoid sensitive
payload capture. Funnel loss is investigated qualitatively before being treated
as a user-motivation problem.
