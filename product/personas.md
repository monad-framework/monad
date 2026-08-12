# Personas

**Status:** Proposed stabilization baseline

Personas are hypotheses until validated with representative users.

## P-01 — Software Engineer

Needs to understand an unfamiliar or complex repository, make a bounded change, know what the change affects, and prove correctness without manually locating every relevant decision/spec/test.

Key jobs: inspect, query, explain, validate, impact analysis, run minimal checks.

## P-02 — AI-Assisted Engineer

Uses ChatGPT and Codex as collaborators but remains accountable for intent and acceptance. Needs agents to receive only relevant authority/context and return implementation evidence rather than unbounded changes.

Key jobs: plan work, produce Work Packets, generate context packages, constrain agent scope, verify resulting changes.

## P-03 — Technical/Architecture Lead

Needs to preserve system boundaries and decisions while enabling teams to change quickly. Wants traceability from architectural intent to implementation/tests and early warning of drift.

Key jobs: architecture query, policy/conformance review, semantic diff, decision impact, release review.

## P-04 — Maintainer / Repository Steward

Needs onboarding, dependency/toolchain state, reliable CI, reproducibility, diagnostics, and clear provenance for why repository artifacts exist.

Key jobs: doctor/inspect, dependency understanding, troubleshooting, release evidence, migration.

## P-05 — Engineering Organization (later horizon)

Needs cross-repository knowledge, ownership, policy, registries, reusable contexts, and organizational engineering intelligence without centralizing every development action in proprietary SaaS.

## Persona priority

MVP prioritizes P-01 and P-02, with enough P-03/P-04 behavior to make the result trustworthy. P-05 shapes extensibility but does not drive MVP scope.