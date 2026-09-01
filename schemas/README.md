# Monad Schema Catalog

This directory contains machine-validatable representations of normative Monad data contracts.

## Authority

Schemas do **not** define the domain model by themselves. The governing requirements, ADRs, and specifications define semantics; schemas encode the serializable constraints needed for machine validation.

When a schema and its governing specification appear to disagree, the disagreement is a defect that MUST be reconciled deliberately. Implementations MUST NOT silently treat whichever representation is easiest to consume as authoritative.

## Conventions

- JSON Schemas use JSON Schema Draft 2020-12 unless a schema explicitly declares otherwise.
- File names use `<concept>.schema.json`.
- Each schema declares a stable `$id` and version-specific contract semantics.
- Breaking serialization or semantic changes require an intentional compatibility/version decision in the governing specification.
- Generated examples/fixtures, if added, are evidence of conformance rather than independent semantic authority.

## Current schemas

- `execution-envelope.schema.json` — machine representation of `DATA-HARNESS-0001`.
