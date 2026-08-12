# Work Packets

A work packet is the smallest authorized unit of project work. It produces one
reviewable result, has a single accountable owner, and contains enough context
to execute without reconstructing decisions from chat or memory.

## Packet characteristics

- advances one increment outcome or retires one named risk;
- can normally complete within a few focused days;
- has explicit scope and exclusions;
- includes testable acceptance and evidence locations;
- names dependencies, reviewers, and required access;
- includes documentation, security, and operations impact;
- closes independently without hidden follow-up required for correctness.

## Lifecycle

`candidate → ready → active → review → done`

Exceptional states are `blocked`, `cancelled`, and `superseded`. Only ready
packets may enter a work cycle. Active packets appear in `active.md`; qualified
future packets appear in `backlog.md`. The packet record, not the index, holds
the complete execution contract.

## Naming

Use `WP-NNNN-short-result.md` with immutable sequential IDs. A title names the
finished result, such as `Durable workflow identity`, rather than an activity
such as `Work on database`.

## Sizing and splitting

Split by demonstrable behavior, business rule, failure path, data transition,
or risk experiment. Avoid horizontal packets that produce no integrated
evidence. When a packet grows during execution, preserve the essential outcome,
move optional scope to candidate packets, and re-review acceptance.

## Closure

The owner links acceptance evidence, records decisions and remaining risk,
updates affected sources of truth, and requests acceptance. A reviewer verifies
the result against the packet and Definition of Done. Closure date and final
state are then reflected in the relevant indexes.
