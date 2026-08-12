# Product and Project Principles

Principles are decision rules, not slogans. When two principles conflict, the
team documents the trade-off and gives priority to user safety, legal and
ethical obligations, correctness, and recoverability before convenience or
delivery speed.

## P-01 — Outcomes before output

Measure whether users achieve the intended result. Features, tickets, and code
volume are inputs, not evidence of value.

## P-02 — Evidence before confidence

Label assumptions and validate the riskiest ones early. Claims about value,
quality, security, and readiness require observable evidence.

## P-03 — One coherent path before breadth

Complete and harden the primary journey before adding adjacent workflows,
personas, integrations, or extensive configuration.

## P-04 — Explicit state and ownership

Users and operators should be able to determine what happened, what is true
now, who owns the next action, and which transition is allowed.

## P-05 — Safe failure and practical recovery

Prevent foreseeable harm, contain failures, preserve diagnostic evidence, and
provide a tested route to retry, compensate, restore, or escalate.

## P-06 — Least authority and least data

Collect, retain, and expose only what is necessary. Grant the narrowest
privilege for the shortest useful duration.

## P-07 — Stable contracts, replaceable internals

Protect user and component contracts while allowing implementation choices to
evolve behind clear boundaries.

## P-08 — Operability is part of design

Health signals, resource budgets, deployment, rollback, and incident response
are designed with the capability, not added after release.

## P-09 — Accessible by default

The primary workflow must work across supported input modes and assistive
technologies. Accessibility defects are product defects.

## P-10 — Reversible decisions when uncertain

Prefer low-cost experiments and reversible choices until evidence supports a
durable commitment. Irreversible choices require greater review and explicit
rationale.

## P-11 — Automation preserves accountability

Automate repeatable mechanics while keeping consequential authority, review,
and appeal visible. Automation must not make responsibility disappear.

## P-12 — Documentation is executable governance

Documents name owners, states, inputs, outputs, checks, and change paths. A
document that cannot guide a decision or test is rewritten or removed.
