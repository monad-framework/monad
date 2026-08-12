---
artifact_id: "EOSV"
title: "EOSV Verification"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# EOSV — Verification

## Purpose

Produce reproducible evidence that work satisfies governing requirements,
specifications, quality attributes, and acceptance criteria.

## Evidence Sources

- EOS integrity checks;
- repository build/test/lint/type/security commands;
- work-packet-specific validation;
- CI results;
- automated traceability;
- benchmarks and operational evidence when required.

## Primary Commands

```bash
./scripts/eos validate WP-CORE-0001
./scripts/eos verify
./scripts/eos trace REQ-0042
```

Repository validation commands are configured in `.eos/validation.commands`.
