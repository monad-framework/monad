# Vision System

The vision documents define the durable intent of MonadV2. They state
why the project deserves to exist, which outcomes matter, the principles that
constrain choices, and the evidence that would justify continued investment.
Implementation details must conform to this layer unless the vision is changed
through governance.

## Document set

| Document | Governs | Review trigger |
| --- | --- | --- |
| `product-vision.md` | Desired future and strategic position | Annual strategy review or material pivot |
| `problem-statement.md` | Validated problem and affected users | Contradictory research or changed market |
| `principles.md` | Decision rules and trade-off posture | Repeated exception or principle conflict |
| `goals.md` | Time-bounded outcomes | Quarterly outcome review |
| `non-goals.md` | Deliberate exclusions | New evidence or completed prerequisite |
| `success-criteria.md` | Measures, guardrails, and decision thresholds | Measurement failure or goal revision |

## Reading order

Read the problem first, then the future state, principles, goals, exclusions,
and success criteria. That order prevents a preferred solution from quietly
redefining the problem.

## Authority and change

Vision documents are **normative**. Conflicts are resolved in this order:
ethical and legal obligations, approved vision, baselined product requirements,
architecture decisions, specifications, then delivery plans. A proposed vision
change must include evidence, affected decisions, migration consequences, and
an explicit approval recorded through `governance/change-control.md`.

## Quality standard

A vision statement is useful only when it is specific enough to exclude
attractive alternatives. Claims must distinguish observations from assumptions.
Goals require measures and dates. Non-goals require rationale and a trigger for
reconsideration. Success criteria include guardrails so that one metric cannot
be improved by transferring harm elsewhere.
