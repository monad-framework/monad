# GitHub Operating Surface

**Status:** Proposed for Foundation Stabilization  
**Canonical scope:** GitHub projection/configuration for `monad-framework/monad`

GitHub is Monad's durable collaboration, review, and coordination surface. It does not replace canonical product, architectural, specification, governance, or engineering authority stored in Git.

## Projection model

```text
Canonical Git artifacts
        ↓
GitHub synchronization
        ↓
Issues / sub-issues / milestones / labels
        ↓
Organization Project views
        ↓
PR / CI / acceptance evidence
```

The repository automatically projects the MVP backlog into Issues through `scripts/sync-github-tracking.py`. Owner/admin-only surfaces are configured through `scripts/setup-github-owner.sh` and the plans in this directory.

## Canonical documents

- `PROJECT-V2-CONFIGURATION.md` — organization Project model, fields, and views.
- `WIKI-PLAN.md` — informational Wiki contract and page set.
- `RULESET-PLAN.md` — intended `main` branch/repository ruleset.
- `OWNER-ACTIONS.md` — exact one-time owner actions and verification.
- `wiki/` — canonical source for GitHub Wiki pages.
- `rulesets/main.json` — staged ruleset payload; do not apply before the stabilization PR is accepted.

## Authority

GitHub Issues, Project fields, milestones, labels, Wiki pages, and automation state are projections. A Project field, Issue body, or Wiki page cannot silently override an Accepted ADR, Approved specification, canonical Work Packet, or explicitly approved engineering plan.

## Synchronization

Repository-scoped tracking is automated by `.github/workflows/github-tracking-sync.yml` and requires only the repository `GITHUB_TOKEN` with Issues write permission. Organization Project, Wiki repository, and repository ruleset mutations require owner/admin authority and therefore remain explicit owner operations.
