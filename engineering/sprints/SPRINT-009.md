# SPRINT-009 — Native Tool Execution and Evidence

**Status:** Forecast  
**Dates:** 2026-10-12 through 2026-10-18  
**Product Increment:** PI-003 — Executable Engineering Loop

## Sprint Goal

Execute approved local plans through real native-tool adapters with controlled process behavior, deterministic evidence capture, explicit failure/cancellation semantics, and the first verified-cache slice.

## Forecast PBIs

EN-007-06, US-010-03 through US-010-07.

## Forecast Work Packet

WP-EXEC-0001.

## Acceptance scenario

A user inspects a plan, runs it, and sees real native-tool commands execute in dependency order. Results capture tool identity/version, working directory, declared environment/input metadata, exit status, diagnostics, outputs/evidence, timing needed for performance analysis, and cache decision provenance.

## Key failure cases

Missing tool, unsupported version, non-zero exit, timeout, cancellation, downstream dependency skip, partial output, invalid/corrupt cache entry, and unknown subprocess result must have explicit behavior.

## Review evidence

Reference tool adapters, execution integration tests, subprocess isolation tests, cancellation/failure fixtures, cache verification tests, execution evidence schema, and a repeatable local run.

## Exit condition

SPRINT-010 can expose execution safely through the CLI and agent workflow without changing execution semantics at the interaction layer.
