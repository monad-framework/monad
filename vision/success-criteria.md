# Success Criteria

Success is a decision supported by a balanced set of outcome, adoption,
quality, safety, and operational evidence. Activity metrics may explain a
result but cannot substitute for one.

## Decision scorecard

| Dimension | Primary measure | Initial success threshold | Guardrail |
| --- | --- | --- | --- |
| Outcome | Successful completion of the primary job | Material improvement over measured baseline | No decline in result quality |
| Effort | Active user time and avoidable handoffs | Lower median and tail effort | No hidden transfer to operators |
| Adoption | Eligible users completing repeat use | Sustained use across the target cohort | No coercive or accidental use |
| Usability | Unassisted task completion | Representative users finish the core path | Accessibility conformance maintained |
| Reliability | Successful valid requests and journey completion | Meets published service objectives | Recovery paths pass exercises |
| Security | Open high-severity findings and control evidence | No unaccepted critical or high risk | Data use stays within declared purpose |
| Operability | Detection, diagnosis, deployment, and restoration | Meets operational budgets | Alert load remains actionable |
| Economics | Cost per successful outcome | Within the approved unit-cost budget | No unsafe quality reduction |

Exact numeric targets are baselined from discovery data and approved in the
first increment record. Any later target change requires a rationale and must
preserve the original value for comparison.

## Evidence sources

- instrumented journey events with documented semantics;
- representative usability and accessibility studies;
- acceptance, performance, security, and recovery test results;
- incident, support, and operator-workload records;
- cohort-based retention and repeat-use analysis;
- direct qualitative research linked to participant and sampling notes;
- cost allocation tied to successful outcomes rather than raw requests.

## Measurement rules

1. Define the denominator before collecting results.
2. Separate eligible attempts, user cancellations, invalid requests, product
   failures, and dependency failures.
3. Report median and tail distributions where averages can hide harm.
4. Segment by supported persona, environment, accessibility mode, and other
   relevant factors without collecting unnecessary sensitive data.
5. Record instrumentation gaps and confidence limits.
6. Do not remove inconvenient observations from the reporting window.

## Decision cadence

Review leading indicators each work cycle, operational health continuously,
product outcomes monthly during pilots, and strategic success quarterly. Each
review ends with one explicit decision: continue, correct, narrow, expand,
pause, pivot, or stop.

## Stop conditions

Pause expansion when a critical safety or security risk is uncontained, the
primary outcome cannot be verified, users cannot provide informed control, the
operating cost exceeds its approved bound without a credible correction, or
evidence shows that the product is not solving the validated problem.
