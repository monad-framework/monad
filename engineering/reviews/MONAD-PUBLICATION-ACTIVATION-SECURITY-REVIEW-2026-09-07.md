# Monad Publication Projection Activation — Security Review

- **Date:** 2026-09-07
- **Scope:** cross-repository publication transport and destination synchronization
- **Source baseline:** `913517ced543d6a244e4d15a1ec5ec197eae6053`
- **Review state:** implementation self-review complete; independent acceptance pending

## Trust and authority

Monad Git/EOS state remains authoritative. The dispatch payload is identity-only and cannot introduce document content or lifecycle facts. The destination re-fetches the exact SHA, confirms it is still current main, reruns source validation/export, and binds the manifest and all artifact provenance to that SHA. No AI-produced state enters the projection.

## Authentication and privilege

The design uses a GitHub App installed only on the destination repository. Minimum permissions are Contents read/write and Pull requests read/write plus implicit metadata read. Source checkout uses the repository's read-only `GITHUB_TOKEN`; the App token exists only long enough to dispatch or update the controlled destination branch/PR. No token or private key is committed or printed.

## Write and deletion containment

The destination rejects traversal, absolute paths, backslashes, symbolic-link traversal, bundle extras, forbidden editorial roots, protected paths, and unowned existing-file collisions. Six contract-designated current-state pages have one-time adoption hashes pinned to the destination baseline. All later changes and deletions require ownership in the preceding valid manifest. No recursive generated-root wipe is used.

## Failure containment

Source, transport, destination validation, authentication, and build failures leave destination main unchanged. Stale/out-of-order events are ignored. Reconciliation repairs manifest-owned drift and missed events. Branch protection and destination CI remain the final integration boundary.

## Residual boundary

The GitHub App installation, key material, Actions variables/secrets, permission grant, and Actions pull-request setting require a human repository administrator. Independent review of the controlled adoption set and normal PR review remain pending; this document does not claim lifecycle acceptance or release completion.
