# Work Packet Backlog

The backlog contains qualified candidate outcomes, ordered by risk reduction
and dependency—not a promise that every item will be delivered. A candidate
must pass the Definition of Ready before it can enter a work cycle.

## Ordering policy

1. Contain critical safety, security, privacy, or reliability risk.
2. Test assumptions that could invalidate the product or architecture.
3. Complete the thinnest end-to-end path to a verified user outcome.
4. Remove blockers and high-cost uncertainty.
5. Improve proven adoption, reliability, accessibility, or economics.

## Ordered candidates

| Order | Candidate result | Why next | Readiness gap |
| --- | --- | --- | --- |
| 1 | Approved primary-journey specification | Converts validated behavior into a testable contract | Awaiting WP-0001 findings |
| 2 | Accepted data classification and lifecycle | Determines safe prototype data handling | Data inventory and owner review |
| 3 | Walking-skeleton architecture decisions | Resolves identity, workflow state, persistence, and deployment choices | Quality baselines and exploration results |
| 4 | Protected repository quality path | Establishes repeatable review, test, secret, dependency, and artifact checks | Implementation stack selection |
| 5 | Authenticated vertical slice | Proves interface-to-domain-to-evidence path | First increment authorization |
| 6 | Durable idempotent workflow state | Retires duplicate-effect and interruption risk | State-model specification |
| 7 | Correlated journey observability | Enables outcome measurement and diagnosis | Event semantics and privacy review |
| 8 | Automated deployment and rollback evidence | Establishes safe delivery and recovery | Reference environment decision |
| 9 | Representative primary acceptance suite | Makes the product promise executable | Approved workflow and test data |
| 10 | Pilot operational readiness | Enables bounded external use | Completed journey and risk review |

## Candidate hygiene

Review the backlog each work cycle. Remove items that no longer advance an
authorized outcome, split oversized work, merge duplicates, and record new
evidence. Do not keep low-value work solely because effort was previously spent
describing it.
