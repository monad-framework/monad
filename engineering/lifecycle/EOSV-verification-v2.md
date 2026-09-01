---
artifact_id: "EOSV-V2"
title: "EOSV Verification v2"
type: "lifecycle-extension"
version: "0.1.0"
status: "Accepted"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# EOSV — Verification v2

## Purpose

Produce first-class, reproducible, independently auditable verification evidence rather than treating a successful command exit as sufficient proof of correctness.

## Verification Model

`target -> validation profile -> typed validators -> EVID-* records -> coverage / staleness -> review gate`

## Evidence Properties

Every `EVID-*` record captures its target, validator, result, source fingerprint, environment fingerprint, artifact hash, explicit coverage links, and provenance. Evidence is retained as an observation; later source drift marks current evidence stale, and new evidence supersedes older evidence rather than rewriting historical proof.

## EOSV v2 Capabilities

- typed validator registry and validation profiles;
- first-class `EVID-*` schema, state machine, registry, and audit events;
- acceptance-criterion-to-evidence mapping using stable `AC-*` identifiers;
- evidence coverage reporting for acceptance criteria and governing artifacts;
- source/environment fingerprinting and stale-evidence detection;
- cryptographic tamper detection for machine evidence;
- execution-result acceptance evidence integration with `EXEC-*`;
- repository-specific validation commands;
- reproducibility validation by repeated normalized execution;
- governed performance baselines and tolerance checks;
- high-confidence secret scanning;
- supply-chain manifest/lockfile inventory and hashing;
- strict project verification that blocks unresolved stale or corrupt evidence;
- dynamic CLI help and shell completion for EOSV commands.

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

## Evidence Lifecycle

`CAPTURED -> VALIDATED | FAILED`

Validated evidence may later become `STALE` when its subject-under-test changes, or `SUPERSEDED` when newer evidence replaces it. Failed or stale evidence is never silently rewritten into a passing observation.

## Validation Profiles

The initial profiles are `default`, `wp`, `security`, `release`, `reproducibility`, and `performance`. Project-specific validators may be added in `.eos/validators.local.json` without modifying the EOS-managed validator catalog.

## Security and Supply Chain Boundary

The built-in security validator intentionally performs only high-confidence secret-pattern detection. The built-in supply-chain validator inventories and fingerprints package manifests and lockfiles. Full vulnerability analysis, SBOM generation, SAST, license policy, provenance verification, and ecosystem-specific scanners belong in subsequent validators or project-local validator integrations rather than being falsely claimed by this baseline.

## Gate Implication

EOSV evidence is intended to become the machine-verifiable input to EOSR Review v2. A claimed implementation completion is not sufficient: the relevant acceptance criteria, governing artifacts, and required validation profiles must have current, untampered evidence before review or closure gates may rely on them.
