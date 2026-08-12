# Architecture Explorations

Explorations reduce uncertainty before a durable decision. They are time-boxed,
evidence-producing investigations, not an alternate backlog or a place for
unowned prototypes.

## When to explore

Use an exploration when a decision depends on uncertain performance,
compatibility, operability, security, developer experience, migration, or cost.
Do not use one when primary documentation or a small local test already answers
the question.

## Exploration record

Name files `EXP-NNNN-short-question.md` and include:

- the decision or risk the work informs;
- falsifiable question and current hypothesis;
- scope, exclusions, time and resource budget;
- representative data, load, environment, and success measures;
- procedure sufficient for another person to reproduce;
- observations separated from interpretation;
- limitations, threats to validity, and unexpected results;
- recommendation and required next decision.

Code or configuration produced by an exploration is disposable unless it passes
normal production review. Label it clearly and never route production traffic
through an unapproved experiment.

## Completion

An exploration ends with one of four outcomes: evidence supports an option,
evidence rejects an option, evidence is inconclusive with a bounded next test,
or the underlying decision is no longer needed. Link the result from the
related ADR, specification, risk, or work packet and archive obsolete artifacts.
