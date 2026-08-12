# Non-Goals

**Status:** Proposed stabilization baseline

Monad is intentionally not the following, especially for MVP Release 1.

## NG-001 — Replace Git

Git remains the version-control and source-history substrate. Monad models and reasons over engineering knowledge stored around it.

## NG-002 — Replace native compilers/build/test tools

Monad coordinates tools such as language compilers, test runners, package managers, formatters, linters, and infrastructure tools; it does not reimplement every ecosystem.

## NG-003 — Become a generic ticketing/project-management product

GitHub Issues/Projects or other systems remain collaboration surfaces. Monad may project engineering state into them and validate traceability.

## NG-004 — Make an LLM the semantic compiler

AI may interpret, draft, summarize, and propose. Canonical semantic compilation and validation must remain deterministic and reviewable for the same inputs.

## NG-005 — Autonomous high-impact engineering authority

Agents do not silently approve architecture, specifications, risk acceptance, release gates, or destructive operations.

## NG-006 — Universal platform completeness in MVP

Remote execution, hosted control planes, enterprise administration, marketplaces, every language, every IDE, and every integration are post-MVP unless proven necessary for the core value test.

## NG-007 — Premature microservices or repository fragmentation

Strong module boundaries are encouraged; independent deployment/repository boundaries require evidence of lifecycle, security, distribution, scale, or ownership need.

## NG-008 — Duplicate canonical sources

Machine companions, published documentation, Wiki pages, Issues, dashboards, and AI summaries must not become competing editable authorities when canonical Git artifacts exist.

## NG-009 — Hide uncertainty behind automation

Monad must surface ambiguity, unsupported constructs, missing provenance, and contradictions rather than manufacture certainty.

## NG-010 — Optimize feature count

Success is measured by trustworthy engineering outcomes—understanding, validation, bounded context, deterministic execution—not by the number of commands, integrations, or artifacts supported.