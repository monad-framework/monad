# Problem Statement

**Status:** Proposed stabilization baseline

## Core problem

Software engineering systems contain critical knowledge that is fragmented across formats, repositories, tools, conversations, and human memory. Neither humans nor AI agents have a reliable canonical semantic view that connects intent, architecture, specifications, implementation, dependencies, work authorization, tests, evidence, releases, and operational consequences.

As a result, engineers repeatedly reconstruct context; automation executes more work than necessary; architectural and documentation drift is discovered late; agents act from incomplete or excessive context; and project status often becomes a manually maintained narrative disconnected from the system being built.

## Observable consequences

The fragmentation appears as:

- slow onboarding and codebase comprehension;
- duplicated analysis before routine changes;
- changes that violate decisions or specifications unintentionally;
- requirements with no implementation or tests;
- implementation with no identifiable governing intent;
- stale generated docs and project-management state;
- over-broad CI because semantic blast radius is unknown;
- weak provenance across requirements, PRs, tests, artifacts, and releases;
- AI hallucination/fabrication amplified by missing authoritative context;
- agent prompts that include secrets, irrelevant files, or conflicting guidance;
- difficulty explaining why a build/test/policy decision occurred; and
- increasing coordination cost as repositories, tools, contributors, and agents multiply.

## Jobs to be done

When an engineer or authorized agent needs to understand or change a software system, they need to identify the applicable engineering intent and constraints, understand semantic relationships and blast radius, execute only the necessary work, verify the result against explicit contracts, and preserve evidence so future participants do not have to reconstruct the same reasoning.

## Why existing tools are insufficient alone

Git records file history but does not model the meaning of every engineering artifact. Build systems understand execution graphs but usually not product requirements or ADR authority. Issue trackers understand planned work but not source semantics. Documentation systems publish prose but do not guarantee conformance. Code-intelligence tools model symbols but not the full engineering lifecycle. General AI can infer relationships but cannot be the deterministic source of truth.

Monad does not need to replace those tools. It needs to provide the semantic layer connecting them.

## Problem acceptance test

The problem is considered sufficiently validated for MVP when representative engineering repositories demonstrate recurring context/traceability/impact gaps, engineers can identify useful questions that existing local tools do not answer coherently, and a deterministic semantic prototype measurably reduces reconstruction effort or catches meaningful inconsistencies without requiring opaque model inference.

## Falsification

The product thesis should be narrowed or reconsidered if a semantic engineering model provides no material utility beyond ordinary search/build tooling, requires maintenance cost greater than the context it saves, cannot remain deterministic enough to trust, or cannot produce substantially better bounded agent context than straightforward repository selection.