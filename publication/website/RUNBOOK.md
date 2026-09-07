# Monad publication activation runbook

The source workflow validates and reproduces the exact current Monad `main` revision, then sends only repository identity, source SHA, and projection version to `monad-framework/aic-fumadocs-app`. The destination retrieves and independently validates that revision, synchronizes manifest-owned files on `publication/monad-main`, and creates or updates a pull request. Destination main is never mutated directly.

## Required GitHub App boundary

Create one GitHub App for publication automation and install it only on `monad-framework/aic-fumadocs-app`. Grant repository metadata read (implicit), Contents read/write, and Pull requests read/write. Configure `MONAD_PUBLICATION_APP_ID` as an Actions repository variable and `MONAD_PUBLICATION_APP_PRIVATE_KEY` as an Actions secret in both repositories. Enable the destination repository setting that permits GitHub Actions to create pull requests, and require destination CI on protected `main`.

After configuration, rerun **Publish Monad site projection** in Monad with an empty `source_sha`, or run **Reconcile Monad publication** in the destination. An explicit SHA is accepted only when it is the current Monad main head.

## Failure and retry

- A stale event is ignored; the next main push or hourly reconciliation converges on current main.
- Invalid source policy, schema, state, MDX, links, types, or build output fails before a branch is pushed.
- A missing or invalid App credential fails at token creation without exposing the private key.
- An existing open publication PR is updated in place from the deterministic `publication/monad-main` branch.
- A no-change reconciliation creates no commit and no new PR.
- A failed destination CI check leaves only an unmerged branch/PR. Correct the source exporter or destination consumer and rerun.
- Manual drift in a manifest-owned file is detected by destination CI and repaired by reconciliation. Unowned/editorial collisions fail closed.
- Generated deletion is the set difference between the previous and next valid manifests; no broad directory deletion is used.

## Local reproduction

```bash
python3 scripts/validate-publication.py
python3 scripts/export-site-state.py --root . --ref <exact-main-sha> --output .tmp/publication-export --verify-determinism
```

Then, from a destination checkout:

```bash
bun scripts/sync-monad.ts --bundle <monad>/.tmp/publication-export --destination . --expected-source-sha <exact-main-sha> --current-main-sha <exact-main-sha> --source-repository <monad>
bun run monad:verify
```
