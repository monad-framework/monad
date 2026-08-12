# Problem Statement

**Status:** Proposed foundation baseline

## Context

Modern software systems are governed by a web of engineering knowledge distributed across source code, requirements, architecture decisions, specifications, configuration, dependency metadata, tests, issues, pull requests, build definitions, security controls, releases, runbooks, incident history, and human reasoning.

The tools that store those artifacts generally understand only their local representation. Git tracks file history but not why a file exists. Issue trackers represent work but not the full architecture they affect. Build systems know dependency mechanics but rarely the product or governance reason a check matters. Documentation describes intent but often drifts from implementation. AI assistants can read large amounts of text but are frequently given context without a reliable model of authority, provenance, relationships, or current validity.

## Core problem

Software engineers, maintainers, reviewers, and AI agents cannot reliably answer consequential questions about a project without manually reconstructing context from fragmented sources.

They must infer:

- which artifacts are authoritative;
- how concepts and components relate;
- why a decision or file exists;
- what a proposed change affects;
- which tests and validation are required;
- which assumptions are current;
- what an AI agent is authorized to change;
- whether generated documentation or cached results are still valid;
- how a release result can be reproduced.

This reconstruction is repetitive, expensive, inconsistent, and increasingly difficult as repositories become polyglot, multi-tool, AI-assisted, and organizationally distributed.

## Who is affected

### Individual engineers

Spend time locating context, tracing dependencies, determining commands, rereading architectural history, and manually checking whether a change is safe.

### Maintainers and architects

Must detect drift between architecture, specifications, code, tests, and documentation while reviewing changes under limited time and incomplete context.

### AI-assisted development workflows

Agents can make fast repository changes but may lack the minimum authoritative context needed to understand intent, prohibited changes, blast radius, or acceptance evidence. More context is not automatically better context.

### CI and release systems

Often execute broad predefined pipelines rather than semantically minimal, explainable validation tied to the actual affected engineering graph.

### Tool and ecosystem authors

Lack a common semantic substrate for interoperating over project meaning, provenance, policy, and engineering relationships.

## Observable consequences

The problem appears as:

- repeated repository archaeology before meaningful work begins;
- architecture and documentation drift;
- overbroad or incomplete CI execution;
- duplicated or contradictory engineering records;
- difficult impact analysis;
- fragile AI-agent prompting and oversized context windows;
- tests that exist without clear requirement coverage;
- requirements or decisions with no observable implementation evidence;
- build and release results that are hard to reproduce or explain;
- maintainers becoming irreplaceable stores of project context.

## Jobs to be done

When changing or evaluating a software system, an engineer needs to understand the relevant project knowledge, determine the semantic impact of the proposed work, identify the governing constraints and required verification, execute the correct native tools, and retain evidence of the result without reconstructing the project from scratch.

When delegating work to an AI agent, a human needs to provide the smallest sufficient authoritative context, bounded permissions, acceptance criteria, and validation plan so the resulting change is reviewable and does not gain authority from model confidence alone.

## Existing alternatives

Current alternatives include repository search, README files, architecture docs, ADRs, code ownership, monorepo/build systems, dependency graphs, IDE indexes, static analysis, knowledge bases, issue trackers, CI configuration, RAG systems, agent instruction files, and experienced maintainers.

Monad should integrate with and learn from these tools rather than dismiss them. Its differentiation must come from compiling the relationships among engineering artifacts into one deterministic semantic model that can drive both understanding and execution.

## Problem acceptance tests

The problem is sufficiently validated for MVP implementation when representative engineering tasks demonstrate that:

1. meaningful context is distributed across several artifact classes rather than available from source code alone;
2. maintainers spend nontrivial effort reconstructing that context or validating change impact;
3. a deterministic semantic model can answer at least some high-value questions more reliably than ad hoc search;
4. bounded semantic context improves at least one controlled human/AI engineering workflow;
5. native-tool execution can be planned from semantic impact without sacrificing correctness.

## Falsification conditions

Monad should narrow, pivot, or stop if repository studies show that the semantic graph cannot be kept accurate enough for consequential use; if the explicit knowledge needed to feed the system imposes more cost than it saves; if affected-set computation cannot be made conservative and explainable; if bounded semantic context does not improve AI-assisted work; or if existing tools already provide the combined value with materially lower complexity.
