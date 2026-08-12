# SPRINT-013 — Dogfood, Documentation, Beta and Release Automation

**Status:** Forecast  
**Dates:** 2026-11-09 through 2026-11-15  
**Product Increment:** PI-004 — MVP Hardening and Release

## Sprint Goal

Use Monad against Monad, close high-value self-hosting gaps, complete Release 1 documentation/publication, incorporate bounded beta/reference feedback, and automate release provenance so the final Sprint can focus on readiness rather than feature construction.

## Forecast PBIs

US-015-02, US-015-03, US-016-03, US-016-04, US-016-05.

## Forecast Work Packets

WP-DOG-0001 and the first phase of WP-REL-0002.

## Dogfood expectations

Monad should inspect significant portions of its own repository, compile and query its own engineering knowledge, calculate impact for representative changes, generate at least one bounded agent context package, and execute a meaningful subset of its own validation plan. Dogfooding defects are product evidence, not exceptions to be hidden.

## Documentation expectations

- installation and first run;
- core concepts: Artifact, MSG, KIR, provenance, affected set, plan, context package;
- command reference and structured output;
- configuration and supported environments;
- troubleshooting/diagnostics;
- security/data/AI boundaries;
- contributor/maintainer workflow;
- compatibility, limitations, upgrade/rollback;
- generated architecture/specification/reference views where mature.

## Release automation expectations

Build/version/package checks, changelog/release notes, source/revision metadata, checksums, provenance, SBOM and signing/attestation where applicable, plus reproducible artifact verification.

## Review evidence

Dogfood report, beta/reference-user findings, documentation quality/link checks, release-pipeline dry run, generated artifact manifest/provenance, and remaining release blockers.

## Exit condition

The final Release Candidate Sprint does not depend on unfinished core features; remaining work is blocker resolution, final evidence, known-limitations documentation, and acceptance.
