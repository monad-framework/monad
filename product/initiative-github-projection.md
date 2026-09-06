# Initiative GitHub Projection

**Status:** Proposed coordination projection
**Canonical initiative source:** `product/initiatives.md`

GitHub Issues and GitHub Projects are coordination surfaces. They do not redefine canonical product, engineering, EOS lifecycle, or verification truth.

## Initiative issue map

| Initiative | GitHub issue |
| --- | --- |
| `INIT-001` | `#270` |
| `INIT-002` | `#271` |
| `INIT-003` | `#272` |
| `INIT-004` | `#273` |
| `INIT-005` | `#274` |
| `INIT-006` | `#275` |

## Epic to initiative mapping

| Epic | Initiative |
| --- | --- |
| `EPIC-001` | `INIT-001` |
| `EPIC-002` | `INIT-002` |
| `EPIC-003` | `INIT-002` |
| `EPIC-004` | `INIT-002` |
| `EPIC-005` | `INIT-002` |
| `EPIC-006` | `INIT-003` |
| `EPIC-007` | `INIT-003` |
| `EPIC-008` | `INIT-004` |
| `EPIC-009` | `INIT-004` |
| `EPIC-010` | `INIT-005` |
| `EPIC-011` | `INIT-005` |
| `EPIC-012` | `INIT-005` |
| `EPIC-013` | `INIT-006` |
| `EPIC-014` | `INIT-006` |

## Recommended GitHub Project views

1. Program — Initiative and overall progress.
2. MVP Roadmap — Initiative → Epic → Feature.
3. Current Work — Ready, Authorized, Running, Review, and Blocked items.
4. Next Up — Ready and dependency-unblocked work.
5. Work Cycles — grouped by `WC-MVP-*`.
6. By Initiative — grouped by Initiative.
7. By Epic — grouped by Epic.
8. Work Packets — all WP-backed Features.
9. Defects — EOS/control-plane and product defects.
10. Release 1 — all work contributing to `PG-001`.
11. Dogfooding — Monad-on-Monad work.
12. AI / Agents — AI context, governance, and agent interaction work.
13. Semantic Core — workspace, ingestion, identity, graph, KIR, diagnostics, and query.
14. Recently Completed — recent closed/verified work.

## Recommended Project fields

Keep the GitHub Project projection intentionally small:

- `Type`: Initiative, Epic, Feature, Story, Enabler, Defect.
- `Initiative`: INIT-001 through INIT-006.
- `Epic`: EPIC-001 through EPIC-014.
- `Product Goal`: PG-001 through PG-004 as later horizons enter the projection.
- `Work Cycle`: WC identifier.
- `Work Packet`: WP identifier.
- `Lifecycle`: Backlog, Refining, Ready, Authorized, Running, Review, Verified, Closed, Blocked.
- `Domain`: orthogonal capability/domain classification.

Planning readiness, execution authorization, and verification/completion must not be collapsed into one ambiguous status when doing so would lose governed lifecycle semantics.
