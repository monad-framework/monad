---
artifact_id: "EOSV-V2"
title: "EOSV Verification v2"
type: "lifecycle-extension"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# EOSV — Verification v2

## Purpose

Produce first-class, reproducible and independently auditable evidence rather
than treating a successful command exit as sufficient proof of correctness.

## Verification Model

`target -> validation profile -> typed validators -> EVID-* records -> coverage / staleness -> review gate`

## Evidence Properties

Every EVID record captures target, validator, result, source fingerprint,
environment fingerprint, artifact hash, explicit coverage links, and provenance.
Evidence is immutable as an observation; later source drift marks it STALE and
new evidence supersedes older evidence rather than rewriting history.

## Primary Commands

```bash
./scripts/eos validators list
./scripts/eos validation profiles
./scripts/eos validate WP-CORE-0001 --profile wp
./scripts/eos evidence list WP-CORE-0001
./scripts/eos evidence coverage WP-CORE-0001
./scripts/eos evidence audit
./scripts/eos security scan WP-CORE-0001
./scripts/eos supply-chain inventory WP-CORE-0001
./scripts/eos performance record graph_lookup 12.4 --unit ms --direction lower --tolerance 0.10
./scripts/eos performance check graph_lookup 12.8
./scripts/eos verify --strict
```
