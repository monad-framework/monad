# Work Packets

A Work Packet is the smallest authorized unit of project work. It produces one reviewable result, has a single accountable owner, and contains enough context to execute without reconstructing decisions from chat or memory.

## Packet characteristics

- advances one Increment/Product Goal outcome or retires one named risk;
- can normally complete within one Work Cycle;
- has explicit scope and exclusions;
- includes testable acceptance and evidence locations;
- names dependencies, governing ADRs/specifications/policies, reviewers, required access, and capability boundaries;
- includes documentation, security, privacy, operations, audit, and provenance impact as applicable;
- has enough bounded Task/test/evidence decomposition to execute without guessing;
- closes independently without hidden follow-up required for correctness.

## Lifecycle

`candidate → ready → authorized → active → verifying/review → closed`

Exceptional states include `blocked`, `cancelled`, and `superseded`. Ready does not imply authorized; authorized does not imply active; merged code does not imply closed. The packet record and EOS evidence, not an index or GitHub projection, hold the authoritative execution/closure contract.

## Namespaces

- `WP-MVP-*` — MVP Release 1 implementation Work Packets.
- `WP-EXP-*` — CR-0002 post-MVP expansion Work Packets.
- historical bootstrap IDs remain preserved but do not become competing active namespaces.

The expanded roadmap initially records WP-EXP identities in `WP-EXP-PI-*-FORECAST.md` catalogs. A forecast entry is split into its own detailed canonical Work Packet artifact during rolling-wave refinement before it can become Ready.

## Sizing and splitting

Split by demonstrable behavior, business/engineering rule, failure path, data/state transition, security/privacy boundary, integration contract, or risk experiment. Avoid horizontal packets that produce no integrated evidence. When a packet grows during execution, preserve the essential outcome, move optional scope to candidate packets, and re-review acceptance.

## Tasks

Tasks are execution decomposition beneath a Work Packet/Story, not a project-wide speculative inventory. Formal Tasks are created/refined when the Work Packet approaches Ready and must cover implementation, tests, negative/boundary cases, migration, documentation, security/privacy, observability, and evidence as relevant. Later-roadmap Tasks are intentionally absent until the governing contracts make them meaningful.

## Closure

The owner links acceptance evidence, records decisions and remaining risk, updates affected sources of truth, completes required security/privacy/audit/attestation evidence, and requests acceptance. A reviewer verifies the result against the packet and Definition of Done. Closure date and final state are then reflected in canonical lifecycle state and relevant projections.
