# Publication Validation Fixtures

This directory contains contract fixtures for Monad's publication projection schemas.

## Structure

- `fixtures/valid/` contains instances that MUST validate.
- `fixtures/invalid/` contains instances that MUST be rejected.

The validation entry point is:

```bash
python3 scripts/validate-publication.py
```

The harness also validates the real `publication/website/projection.yaml` and performs
boundary mutations proving that the schema rejects a non-`main` current-state source
branch and a non-deny default disposition.

Fixtures are intentionally small. They test schema contracts rather than attempting
to model a complete real publication export. Real exporter output will later become
an additional validation target.
