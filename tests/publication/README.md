# Publication Validation and Export Tests

This directory contains contract fixtures and executable tests for Monad's website publication projection.

## Schema fixtures

- `fixtures/valid/` contains instances that MUST validate.
- `fixtures/invalid/` contains instances that MUST be rejected.

The schema-validation entry point is:

```bash
python3 scripts/validate-publication.py
```

The validation harness also validates the real `publication/website/projection.yaml` and performs boundary mutations proving that the schema rejects a non-`main` current-state source branch and a non-deny default disposition.

Fixtures are intentionally small. They test schema contracts rather than attempting to model a complete real publication export.

## Deterministic exporter

`test-export-site-state.py` tests the publication exporter at two levels:

1. unit-level parsing, glob, frontmatter, and determinism-boundary behavior;
2. an integration export of the local `main` or `origin/main` revision.

Run:

```bash
python3 tests/publication/test-export-site-state.py
```

The integration test exports the same authoritative revision twice and requires the complete generated trees to be byte-identical. The exporter itself validates generated manifest, provenance, and site-state JSON against the publication schemas before reporting success.

The test intentionally exports a committed `main` revision rather than mutable working-tree content. This preserves the `MONAD-PUB-001` main-only current-state boundary even when the test itself is executed from a feature branch.
