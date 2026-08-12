# SPRINT-006 — Query, Explanation and First Change Impact

**Status:** Forecast  
**Dates:** 2026-09-21 through 2026-09-27  
**Product Increment:** PI-002 — Semantic Kernel

## Sprint Goal

Make the semantic model useful to a maintainer: inspect entities, traverse relationships, explain provenance/why, ingest a bounded Git change, and calculate the first conservative affected set.

## Forecast PBIs

US-008-01 through US-008-06, US-009-01, US-009-02.

## Forecast Work Packets

WP-QUERY-0001 and WP-IMPACT-0001.

## Acceptance scenario

Given a reference repository and a bounded change, a user can locate an entity, ask which requirements/decisions/specs/tests/components relate to it, explain why the relationships exist, and obtain an affected set with explicit dependency paths. Unknown or unsupported semantics remain visible.

## Key safety rule

False-negative required impact is the critical defect class. Where the graph cannot prove that a smaller affected set is complete, uncertainty expands the result or blocks optimization.

## Review evidence

Query fixtures, structured-output contract, provenance explanations, Git diff/change fixtures, affected-set corpus, and comparison against conservative full-validation expectations.

## PI-002 exit

PI-002 closes only when workspace→identity/provenance→MSG→KIR→query/explain→first affected-set works as one deterministic integrated semantic-kernel slice.
