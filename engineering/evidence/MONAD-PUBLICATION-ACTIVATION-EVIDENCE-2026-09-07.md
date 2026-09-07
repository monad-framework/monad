# Monad Publication Projection Activation — Implementation Evidence

- **Date:** 2026-09-07
- **Initial source baseline exercised:** `913517ced543d6a244e4d15a1ec5ec197eae6053`
- **Final reconciled source baseline exercised:** `fd7c015ed7fb85efd2b80ba1a6e691d5bea47840`
- **Destination baseline exercised:** `3a03f68ff0753652a5fdc5ac2be0feac841a036e`
- **Evidence state:** local implementation evidence; destination PR CI and independent review pending

## Verified locally

- exact-SHA export generated 1,445 files (1,443 manifest artifacts plus manifest and provenance);
- repeated exact-SHA export was byte deterministic;
- publication policy, schemas, positive fixtures, and negative fixtures validated;
- destination manifest/provenance verification passed for all 1,443 artifacts;
- eight destination synchronization tests covered no-op, SHA mismatch, stale attempts, invalid hashes/provenance, forbidden/protected paths, editorial conflict, hash-pinned adoption, manifest deletion, drift/partial-state repair, repeat reconciliation, and duplicate manifest entries;
- the real Fumadocs MDX corpus compiled after deterministic title and HTML-comment compatibility transforms;
- a pre-existing nullable AI-search context type defect discovered by the production gate was corrected in the destination branch.
- the final reconciled export produced 1,469 files (1,467 manifest artifacts plus manifest and provenance), and the destination production build generated 4,659 static/dynamic route outputs successfully.

## EOS governance scope

`MONAD-PUB-001` is the governing publication contract. No new Work Packet lifecycle state was asserted: the canonical EOS state already had `WP-MVP-0005` in progress during implementation, and this workstream was explicitly prohibited from modifying or competing with it. `./scripts/eos state status` remained consistent and `./scripts/eos verify --strict` passed. Independent review and lifecycle acceptance remain pending.

## Pending external evidence

The GitHub App is not yet configured, so repository dispatch, automated PR create/update, destination-hosted CI, normal merge, and deployed-site observation remain pending. No claim of acceptance, release, or public activation is made by this evidence record.
