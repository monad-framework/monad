---
artifact_id: "EOSE"
title: "EOSE Execution"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-09-05"
---
# EOSE — Execution

## Purpose

Execute authorized work without allowing implementation convenience to redefine
product or architecture policy.

## Work Packet Contract

```bash
./scripts/eos start WP-CORE-0001
./scripts/eos codex WP-CORE-0001
```

The Codex contract includes the authorized work packet, related governing
artifacts, repository state, scope constraints, validation requirements, and the
required completion report.

## Escalation Rule

If implementation requires changing a governing requirement, specification,
ADR, security constraint, or authorized scope, execution stops and enters EOSC.

## AI-Driven Execution Participation

AI-driven engineering does not alter EOSE authority boundaries.

An AI executor MAY progress authorized work without synchronous human
intervention only inside the applicable scope, authority, capability, policy,
environment, resource, and autonomy boundaries.

An executor MUST NOT:

- infer execution authority from a pathway proposal;
- self-grant capabilities or stronger autonomy;
- broaden authorized Work Packet scope;
- treat tool availability as permission;
- silently continue under materially stale governing inputs;
- treat its own completion claim as verified or accepted completion.

When execution depends on governing context, material governing-input drift
invalidates or suspends the affected execution authority and requires
recompilation, reauthorization, replanning, EOSC, or another explicit governed
disposition.

Consequential execution requested by an AI participant MUST hand off through
the applicable governed execution boundary rather than treating participant
initiative as execution authority.
