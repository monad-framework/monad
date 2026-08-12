# M-001 — MVP Release 1

**Status:** Forecast  
**Target release:** 2026-11-23  
**Product Goal:** deterministic local semantic engineering loop

## Outcome

A user can point Monad at a representative repository and, through a coherent local CLI, discover the workspace, compile canonical engineering knowledge into a deterministic MSG/KIR, validate/query/explain relationships, calculate conservative change impact, generate bounded AI-agent context, derive and inspect an execution plan, run native validation tools, and retain reproducible diagnostics/evidence.

## Included increments

- PI-002 — Semantic Kernel.
- PI-003 — Executable Engineering Loop.
- PI-004 — MVP Hardening and Release.

PI-001/M-000 are prerequisites.

## Acceptance

M-001 closes only when:

- all must-have Product Requirements have passing evidence;
- deterministic/reproducibility scenarios pass;
- affected-set safety guardrails pass;
- graph/KIR identity/provenance/conformance are stable enough for the declared Release 1 compatibility contract;
- agent context preserves authorization/privacy constraints;
- native execution runs only explicit plans and captures evidence;
- installation and rollback/recovery are documented/tested;
- security/supply-chain/performance/release-readiness reviews pass or contain explicitly accepted nonblocking limitations;
- Monad-on-Monad dogfooding produces useful evidence;
- release documentation and known limitations are published;
- Product Owner records the Release decision.

## Explicitly not required

Remote execution/cache, hosted collaboration, enterprise fleet governance, mature plugin marketplace/registry, commercial hosted offerings, autonomous high-consequence agents, and broad multi-repository federation.

## Release semantics

The target date is a forecast. If the candidate does not satisfy the release guardrails, M-001 remains open and Release 1 moves; the milestone is not declared complete because the calendar ended.
