# Active Work Packets

This index contains engineering work currently authorized inside the Foundation Stabilization Program. A Work Packet is engineering authority; a Product Backlog Item or GitHub Issue alone does not authorize implementation.

## Work-in-progress policy

- Prefer one actively implemented packet per execution owner/agent at a time.
- Review/integration work may overlap when it does not require conflicting edits or unresolved authority.
- A packet moves to Ready only when its governing decisions/specifications are sufficient for its scope.
- Blocked packets name the dependency/decision owner and next escalation point.
- Generated Draft documents are not treated as accepted prerequisites merely because they exist.

## Active / Review

| Work Packet | Status | Target | Outcome |
| --- | --- | --- | --- |
| WP-STAB-0001 | Review | STAB-0001 | Reconcile Monad product identity and MVP thesis across the C0 foundation. |
| WP-STAB-0002 | Review | STAB-0001 | Consolidate architectural-decision authority under `architecture/decisions/` and remove path/status contradictions. |
| WP-STAB-0003 | Review | STAB-0001 | Materialize every empty artifact-system Markdown file as a substantive non-authoritative Draft baseline. |
| WP-STAB-0004 | Review | STAB-0001 | Regenerate and verify the complete deterministic machine-readable knowledge layer. |
| WP-STAB-0005 | Active | STAB-0001 | Bootstrap complete MVP Epic/Feature/PBI/Sprint/PI/WP backlog and ordered release plan. |
| WP-STAB-0006 | Active | STAB-0001 | Establish the GitHub operating surface: issues, labels, milestones, project schema, wiki projection, repository settings target, and automation. |
| WP-STAB-0008 | Planned | STAB-0001 | Reconcile first-slice C1 architecture/specification authority for semantic-kernel implementation. |
| WP-STAB-0007 | Planned | STAB-0001 | Conduct stabilization readiness review after the other transition packets reach review-complete state. |

## Next Ready target

The first implementation packet should become **WP-WS-0001 — Workspace Root and Repository Identity** for SPRINT-002 only after SPRINT-001 accepts the minimum runtime/configuration/identity architecture and specification contracts it requires.

## Recently completed transition evidence

- ADR-0001 was moved into the canonical `architecture/decisions/` hierarchy and `.monad` was reconciled.
- Artifact-system Draft materialization is deterministic and does not overwrite authored non-empty files by default.
- Machine companions/manifest/graph/corpus have been regenerated on the stabilization branch and the synchronization workflow has passed.

These accomplishments remain subject to stabilization review; passing generation does not by itself approve the semantic content of every Draft artifact.
