# GitHub Owner Actions

These are the remaining actions that require organization/repository owner authority outside the connected repository-write surface.

## Preconditions

From a clone containing the accepted stabilization changes:

```bash
git fetch origin
git switch stabilization/mvp-foundation
git pull --ff-only
```

Install/authenticate GitHub CLI and ensure the token has repository administration plus Projects access. Then run:

```bash
./scripts/setup-github-owner.sh check
./scripts/setup-github-owner.sh project
./scripts/setup-github-owner.sh wiki
```

Do **not** apply the main ruleset until the stabilization PR is merged and stable CI check names are confirmed.

## Project UI finishing step

After `project` completes, open the organization Project **Monad Engineering Program** and create the views defined in `engineering/github/PROJECT-V2-CONFIGURATION.md`. View presentation is intentionally not treated as canonical engineering state.

## Wiki verification

Verify the Wiki contains the staged page set and that architecture/decision links point back to `architecture/decisions/` rather than the retired `adrs/` root.

## Ruleset application

After the stabilization PR is accepted and merged:

```bash
./scripts/setup-github-owner.sh ruleset
```

Then verify a normal direct push to `main` is rejected and a PR can still be created/merged through the intended workflow.

## Completion criteria

Owner setup is complete when:

- the organization Project exists exactly once and is linked to this repository;
- all current projected Issues are present in the Project;
- required custom fields exist;
- the prescribed Project views are created;
- Wiki pages are synchronized and informational-only;
- the main ruleset is active after PR/CI verification; and
- no owner/admin action introduced an alternative source of engineering truth.
