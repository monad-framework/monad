# Transition Register

**ID:** STAB-REGISTER-0001  
**Status:** Active  
**Owner:** Engineering Owner

This living register tracks known transitional inconsistencies. Entries close only with evidence, not by assumption.

| ID | Transition | Current state | Target state | Gate |
| --- | --- | --- | --- | --- |
| TR-001 | Product identity | Repository metadata says Engineering Knowledge Compilation Platform; several canonical drafts describe generic MonadV2 workflow software | One Monad engineering-knowledge thesis across product and architecture | Foundation reconciliation review |
| TR-002 | ADR root | Remote baseline contains both `adrs/` and `architecture/decisions/` | `architecture/decisions/` is the sole ADR root | ADR consistency check |
| TR-003 | ADR index | Accepted ADR-0001 exists while architecture decision index reports none accepted | Canonical index accurately lists all decisions | ADR consistency check |
| TR-004 | Machine layer | Generated manifest/corpus/companions are stale and incomplete | `sync-machine-docs.py --check` passes from clean checkout | CI |
| TR-005 | Artifact system | Large taxonomy exists as empty Markdown placeholders | Every artifact Markdown file contains substantive controlled content | Artifact audit |
| TR-006 | WP-0001 | Active index describes WP-0001 but no individual packet exists | Every active packet has a canonical packet record | Engineering audit |
| TR-007 | Planning | Milestone/increment/work-cycle structures exist but MVP plan is not instantiated | MVP Release 1 has traceable roadmap and rolling-wave backlog | Planning review |
| TR-008 | GitHub Issues | No live issues in new repository | Epics and ready-horizon execution work are projected into Issues | GitHub review |
| TR-009 | GitHub Project | Projects enabled but operational model not instantiated/verified | One canonical product-development project with fields/views/iterations | GitHub review |
| TR-010 | Wiki | Wiki enabled but current content/state not established | Wiki is an informational projection with canonical-source links | GitHub review |
| TR-011 | Branch governance | `main` is unprotected | Required review/check/merge controls documented and configured | Repository governance review |
| TR-012 | CI coverage | Only machine sync workflow presently exists and is red | Layered repository, semantic, test, security, and release gates are green | CI review |
| TR-013 | Artifact authority | Artifact taxonomy paths can be mistaken for current authority | Catalog semantics and lifecycle are explicit | Artifact audit |
| TR-014 | Naming | `Monad`, `MonadV2`, MKE, and product terms are inconsistent | Canonical terminology uses `Monad`; versioning belongs to releases, not product identity | Terminology review |

## Update rule

Add an entry whenever a material mismatch could cause an agent, reviewer, contributor, or automation to act on the wrong source. Closed entries retain their resolution evidence and date.