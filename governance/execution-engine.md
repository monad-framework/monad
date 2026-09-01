---
artifact_id: "GOV-EXEC-0001"
title: "EOSE Execution Engine"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# EOSE Execution Engine

EOSE Execution v2 turns an authorized work packet into a bounded, reproducible,
auditable implementation session.

## Execution Flow

`AUTHORIZED WP -> preflight -> isolated worktree/branch -> EXEC-* session ->
fingerprinted machine/human contracts -> bounded implementation -> result
 ingestion -> scope/concurrency checks -> verification evidence -> review`

## Invariants

- one active execution session per work packet unless policy explicitly changes;
- execution contracts are fingerprinted against governing inputs;
- governing-input drift invalidates a contract instead of being silently ignored;
- changed files must satisfy work-packet execution-scope rules;
- EOS and Git metadata are never authorized implementation scope;
- concurrent mutation of one WP/EXEC target is protected by EOS lock records;
- agent output is ingested as structured evidence, never trusted as the sole proof;
- the actual Git diff is compared with the agent-declared changed-file list;
- execution does not itself approve verification, review, closure, or release.

## Work Packet Scope Directives

Work packets may contain machine-readable list entries:

```text
- allowed-path: src/**
- allowed-path: tests/**
- forbidden-path: scripts/release/**
- allowed-governed-path: specifications/CORE/SPEC-CORE-0007.md
```

If no `allowed-path` is present, the execution engine permits repository files
by default but still blocks EOS/Git internals and flags governed-artifact
changes unless specifically authorized by `allowed-governed-path`.
