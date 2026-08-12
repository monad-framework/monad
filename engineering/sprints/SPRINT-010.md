# SPRINT-010 — CLI and AI-Agent Context

**Status:** Forecast  
**Dates:** 2026-10-19 through 2026-10-25  
**Product Increment:** PI-003 — Executable Engineering Loop

## Sprint Goal

Expose the integrated semantic/execution loop through a coherent human/automation CLI and generate deterministic bounded context packages for authorized Codex/AI-agent tasks without granting agents implicit authority.

## Forecast PBIs

US-011-01 through US-011-07; US-012-01 through US-012-06; EN-013-03 and EN-013-04.

## Forecast Work Packets

WP-CLI-0001 and WP-AGENT-0001.

## Acceptance scenario

A maintainer can use the Release 1 CLI flow to inspect, validate, query/explain, calculate impact, generate context, inspect a plan, execute it, and diagnose the environment. Separately, a Work Packet can be transformed into a bounded Codex context package containing governing artifacts, relevant dependencies, constraints, acceptance criteria, validation, provenance, and explicit exclusions/capabilities.

## Security and authority rules

- context selection minimizes repository disclosure;
- secrets/sensitive material are not included because of graph reachability alone;
- agents cannot expand their capabilities or approve high-consequence work;
- machine-readable and text output have stable contracts;
- noninteractive automation never depends on TUI behavior.

## Review evidence

CLI command/help/exit-code/structured-output tests, end-to-end local scenario, context-package golden fixtures, context minimization tests, exclusion/secret tests, Codex task demonstration, and AI provenance/audit review.

## PI-003 exit

A user can progress from repository/task/change through semantic understanding, affected set, bounded context, inspectable plan, native execution, and evidence through stable product interfaces.
