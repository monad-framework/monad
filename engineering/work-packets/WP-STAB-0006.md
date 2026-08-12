# WP-STAB-0006 — Establish the GitHub Operating Surface

**Status:** Active  
**Owner:** Engineering Owner  
**Program:** STAB-0001

## Objective

Make GitHub a complete, trustworthy collaboration and project-projection layer for Monad without moving canonical product/architecture/work authority out of the repository.

## Scope

### In scope

- repository labels and milestones;
- Issue Forms and PR template;
- Epic/Feature/PBI/Sprint/Work Packet issue projection;
- organization Project field/view/iteration specification;
- Wiki source/projection;
- repository/ruleset/branch target settings;
- CODEOWNERS and required-review model;
- Actions permissions/pinning/security/dependency automation targets;
- idempotent setup/projection automation where available.

### Out of scope

- claiming Project v2, Wiki, rulesets, or organization settings are configured when the connected automation identity cannot mutate them;
- making GitHub Issues the canonical specification or Work Packet;
- duplicating every small implementation task as an Issue when it adds no collaboration value.

## Acceptance criteria

- [ ] Label taxonomy covers item type, status, priority, criticality, area, risk, and agent/execution needs without label explosion.
- [ ] MVP Milestone(s) and release target are defined and live where API permissions allow.
- [ ] Issue Forms exist for Epic, Feature, Story, Enabler, Bug, Spike, Task, Work Packet, Decision/Risk where useful.
- [ ] Canonical Epics and refinement-horizon items are projected into GitHub with stable IDs and no duplicate creation.
- [ ] Project fields/views/iterations are specified exactly enough for one-time UI/API setup and kept out of canonical authority.
- [ ] Wiki source pages exist and identify canonical source links.
- [ ] Target `main` branch protections/ruleset, required checks, merge strategy, branch deletion/update behavior, and CODEOWNERS expectations are documented.
- [ ] Security/dependency automation target includes pinned Actions, least-privilege workflow permissions, secret/dependency checks, and update policy.
- [ ] Any unautomatable GitHub setting is recorded as an explicit remaining setup action rather than implied complete.

## Validation

Compare live GitHub repository state with `.github/` setup artifacts and the canonical backlog. Re-run issue/setup automation to prove idempotency. Sample Issue→canonical ID→Feature/PBI/WP traceability in both directions.

## Risks

GitHub Projects v2 and Wiki/ruleset mutations can require organization-level scopes unavailable to normal repository tokens. The repository must preserve deterministic setup instructions so the missing permission does not become undocumented manual knowledge.

## Completion evidence

Live issues/milestones/labels where authorized, setup specifications, Wiki source, automation results, and GitHub operating-baseline review.
