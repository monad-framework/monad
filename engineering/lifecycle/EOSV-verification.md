---
artifact_id: "EOSV"
title: "EOSV Verification"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-09-05"
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

## AI-Driven Verification Participation

AI MAY assist EOSV by:

- recommending validators or validation profiles;
- invoking authorized validators;
- analyzing failures;
- identifying likely causes;
- recommending additional evidence;
- interpreting verification results.

AI interpretation is not verification authority.

An AI participant MUST NOT:

- fabricate verification evidence;
- rewrite failed evidence into passing evidence;
- promote stale evidence to current;
- override deterministic validator results because the model disagrees;
- use executor self-report as sufficient independent proof where independent
  evidence is required.

Verification evidence retains its actual provenance, freshness, validator,
scope, and result.

Evidence MAY influence replanning while remaining evidence rather than silently
becoming requirements, policy, architecture, or approval.
