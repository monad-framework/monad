# GitHub Project Projection Invariants

**Status:** Proposed  
**Parent:** `engineering/github/PROJECT-V2-CONFIGURATION.md`

## Authority

The Monad Engineering Program GitHub Project is a coordination/read-model projection. It is not an authority source for engineering lifecycle, execution state, Work Packet state, planning identity, verification truth, or other governed engineering facts.

Canonical Git/EOS records remain authoritative. In particular, when a projected Issue references a Work Packet registered in `.eos/work-packets.tsv`, the registered Work Packet state controls the projected execution metadata.

## Lifecycle precedence

Lifecycle projection MUST apply the following authority order:

1. If an Issue references a registered Work Packet and that Work Packet has a recognized canonical EOS status, the EOS status determines the projected `Lifecycle`.
2. Otherwise, if the GitHub Issue itself is closed, the projected `Lifecycle` is `Closed`.
3. Otherwise, lifecycle labels such as `status:ready`, `status:active`, or `status:blocked` may provide fallback coordination state.
4. Otherwise, recognized lifecycle statements in the Issue body may provide the final fallback.

GitHub Issue closure therefore cannot override authoritative registered Work Packet state, but stale lifecycle labels cannot keep an unregistered closed Issue in an active or backlog projection.

## Issue coverage verification

Project completion MUST verify coverage by repository Issue identity, using the exact repository Issue URL set.

A raw Project item count is not sufficient because a Project can also contain pull requests, drafts, or Issues from other repositories. Verification MUST:

- collect every repository Issue URL for the target repository;
- collect only Project items that are Issues belonging to that same repository;
- fail when any repository Issue URL is absent from the Project;
- ignore extra pull requests, drafts, and items from other repositories when determining repository-Issue coverage.

## Managed projection fields

Only explicitly projection-managed fields are written or cleared by metadata synchronization:

- `Item Type`
- `Product Goal`
- `Initiative`
- `Epic`
- `Feature`
- `Priority`
- `Product Area`
- `Domain`
- `Increment`
- `Work Cycle`
- `Work Packet`
- `Lifecycle`
- `Target Release`

Other Project fields, including user-owned or operational presentation fields such as `Risk`, `Executor`, `Story Points`, GitHub Status, and Assignees, are outside this projection write contract unless separately governed by another explicit automation.

## Stale-value clearing

Full synchronization is convergent rather than append-only.

If a repository Issue previously projected recognized planning metadata but later loses its recognized `[Type]` prefix or another derivable managed value, the Issue MUST remain in the full synchronization pass. The synchronizer MUST send null/empty values for projection-managed fields that are no longer derivable so stale Project metadata is removed.

The lightweight core synchronization may continue to restrict processing to hierarchy-first Item Types; the full synchronization is the convergence boundary for clearing stale managed metadata.

Unmanaged fields MUST NOT be cleared as a side effect of projection convergence.

## Idempotence

Repeated execution of the same projection against unchanged canonical Git/EOS and Issue inputs MUST converge to the same Project state.

`project-complete` MUST therefore be safe to repeat without creating duplicate fields, duplicate field options, duplicate Project items, duplicate named views, or accumulating stale managed values. Repeated metadata derivation for unchanged inputs must produce the same managed-field values.

## Acceptance

A completed Project projection is acceptable only when all of the following hold:

- required Project fields and required single-select options exist;
- all required named views exist;
- every repository Issue is represented in the Project by exact Issue identity;
- Product Goal → Initiative → Epic → Feature → Story/Enabler → Task relationships are projected where derivable;
- canonical Work Cycle and Work Packet metadata are projected;
- registered EOS Work Packet lifecycle state wins over GitHub fallback state;
- unregistered closed Issues project as `Closed` before lifecycle-label/body fallback;
- stale projection-managed values are cleared during full convergence;
- unmanaged Project fields remain untouched;
- Task is a supported Item Type;
- representative Initiative, MVP, Task, and Running-work queries return expected results;
- repeated execution remains idempotent.
