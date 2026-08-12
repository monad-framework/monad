---
artifact_id: "GOV-RACI-0001"
title: "Human ChatGPT Codex GitHub Responsibility Model"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# Human / ChatGPT / Codex / GitHub Responsibility Model

## Human

The human is the final project authority.

Responsibilities:

- define intent and values;
- resolve ambiguous product or business questions;
- approve or reject major scope and architectural decisions;
- authorize implementation gates;
- accept material risk;
- approve releases or irreversible external actions.

The human should not be forced to manually perform mechanical consistency work
that tools can verify.

## ChatGPT

ChatGPT is the primary reasoning, synthesis, planning, and review collaborator.

Responsibilities:

- analyze `idea.md`;
- extract terminology, assumptions, goals, constraints, and open questions;
- draft and reconcile project artifacts;
- identify contradictions and missing decisions;
- propose architecture based on requirements and quality attributes;
- maintain cross-artifact traceability;
- define PIs, WCs, and WPs;
- review Codex output against governing artifacts;
- recommend whether gates should pass.

ChatGPT may propose decisions, but major decisions remain subject to human
authority.

## Codex

Codex is the repository-local implementation and verification agent.

Responsibilities:

- inspect the current repository state before changing files;
- implement bounded work packets;
- modify only authorized scope;
- run tests, formatters, linters, builds, and validation;
- report exact changed files and verification evidence;
- prepare commits and pull requests when authorized;
- surface conflicts instead of inventing new product or architecture policy.

Codex should not silently redefine requirements or architecture to make an
implementation easier.

## GitHub

GitHub is the durable collaboration, history, review, and integration system.

Responsibilities:

- canonical Git remote;
- immutable commit history;
- branches and pull requests;
- issue / work packet tracking;
- project and milestone visibility;
- review record;
- CI and policy enforcement;
- releases and tags;
- durable audit trail.

## Default Handoff

`Human intent -> ChatGPT definition/review -> Codex implementation -> GitHub
history/CI/review -> ChatGPT conformance review -> Human gate decision`

## Automation Principle

Automate deterministic mechanics. Preserve explicit human authority over
mission, risk acceptance, major tradeoffs, and irreversible actions.
