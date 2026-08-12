---
artifact_id: "EOSE"
title: "EOSE Execution"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
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
