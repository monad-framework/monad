---
artifact_id: "GOV-GITHUB-0001"
title: "GitHub Integration Model"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# GitHub Integration Model

Git remains the authoritative version history. GitHub is the canonical remote
collaboration and integration surface when configured.

## Mapping

| EOS object | GitHub object |
|---|---|
| Program Increment | tracking issue / milestone |
| Work Cycle | tracking issue |
| Work Packet | issue + branch + pull request |
| Change Request | issue / pull request |
| Verification | GitHub Actions checks + evidence artifacts |
| Review | pull-request review + repository review artifact |
| Release | Git tag + GitHub Release |
| Maintenance | issue + WP/change request when required |

## Synchronization

`./scripts/eos github-sync` is dry-run by default.

`./scripts/eos github-sync --apply` may create/reconcile EOS labels and tracking
issues using the authenticated GitHub CLI. External writes are explicit and are
never side effects of local status, trace, review, or verification commands.
