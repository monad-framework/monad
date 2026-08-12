#!/usr/bin/env bash
set -Eeuo pipefail

# ==============================================================================
# Project Bootstrap Scaffold
#
# Creates a documentation-first, architecture-first repository scaffold for a
# new software project.
#
# Usage:
#   ./bootstrap-project.sh <project-directory>
#
# Examples:
#   ./bootstrap-project.sh my-project
#   ./bootstrap-project.sh .
#
# Optional environment variables:
#   PROJECT_NAME="Monad" ./bootstrap-project.sh monad
#
# Design principles:
#   - Do not overwrite existing files.
#   - Preserve an existing idea.md.
#   - Establish project memory, governance, architecture, and engineering
#     structure before implementation structure.
#   - Keep the initial scaffold intentionally lean.
# ==============================================================================

readonly SCRIPT_NAME="$(basename "$0")"

log() {
  printf '==> %s\n' "$*"
}

warn() {
  printf 'WARNING: %s\n' "$*" >&2
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<EOF
Usage:
  $SCRIPT_NAME <project-directory>

Examples:
  $SCRIPT_NAME my-project
  $SCRIPT_NAME .

Optional:
  PROJECT_NAME="My Project" $SCRIPT_NAME my-project
EOF
}

# ------------------------------------------------------------------------------
# Arguments
# ------------------------------------------------------------------------------

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

TARGET_DIR="$1"

if [[ "$TARGET_DIR" == "/" ]]; then
  die "Refusing to scaffold the filesystem root."
fi

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

PROJECT_ROOT="$(pwd)"
DEFAULT_PROJECT_NAME="$(basename "$PROJECT_ROOT")"
PROJECT_NAME="${PROJECT_NAME:-$DEFAULT_PROJECT_NAME}"

log "Bootstrapping project: $PROJECT_NAME"
log "Project root: $PROJECT_ROOT"

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

create_dir() {
  local path="$1"

  if [[ ! -d "$path" ]]; then
    mkdir -p "$path"
    log "Created directory: $path"
  fi
}

create_file() {
  local path="$1"

  if [[ -e "$path" ]]; then
    warn "Skipping existing file: $path"
    return
  fi

  mkdir -p "$(dirname "$path")"
  touch "$path"
  log "Created file: $path"
}

write_file() {
  local path="$1"

  if [[ -e "$path" ]]; then
    warn "Skipping existing file: $path"
    cat >/dev/null
    return
  fi

  mkdir -p "$(dirname "$path")"
  cat >"$path"
  log "Created file: $path"
}

# ------------------------------------------------------------------------------
# Directory scaffold
# ------------------------------------------------------------------------------

directories=(
  "vision"
  "product"
  "architecture"
  "architecture/decisions"
  "architecture/explorations"
  "architecture/diagrams"
  "specifications"
  "specifications/functional"
  "specifications/technical"
  "specifications/interfaces"
  "specifications/data"
  "specifications/security"
  "specifications/operations"
  "engineering"
  "engineering/milestones"
  "engineering/increments"
  "engineering/work-cycles"
  "engineering/work-packets"
  "engineering/reviews"
  "engineering/risks"
  "research"
  "research/findings"
  "research/experiments"
  "research/references"
  "governance"
  "journal"
  ".github"
  ".github/ISSUE_TEMPLATE"
  ".github/workflows"
)

for directory in "${directories[@]}"; do
  create_dir "$directory"
done

# ------------------------------------------------------------------------------
# Inception artifact
# ------------------------------------------------------------------------------

if [[ ! -e "idea.md" ]]; then
  write_file "idea.md" <<EOF
# $PROJECT_NAME — Project Idea

**Status:** Inception  
**Authority:** Historical source artifact

## Idea

Describe the project thoroughly here.

## Problem

What problem should this project solve?

## Intended Users

Who should benefit from it?

## Desired Outcome

What should exist when this project succeeds?

## Constraints

What limitations, assumptions, or requirements are already known?

## Open Questions

What remains unclear?
EOF
else
  log "Preserving existing idea.md"
fi

# ------------------------------------------------------------------------------
# Root README
# ------------------------------------------------------------------------------

write_file "README.md" <<EOF
# $PROJECT_NAME

> Project-definition and engineering repository.

## Status

**Phase:** Project inception / pre-implementation

This repository intentionally begins with project definition, architecture,
specification, research, governance, and engineering planning before committing
to an implementation structure.

## Start Here

1. [idea.md](./idea.md)
2. [vision/README.md](./vision/README.md)
3. [product/README.md](./product/README.md)
4. [architecture/README.md](./architecture/README.md)
5. [engineering/project-status.md](./engineering/project-status.md)

## Repository Structure

| Directory | Purpose |
|---|---|
| \`vision/\` | Why the project should exist |
| \`product/\` | What users need the system to do |
| \`architecture/\` | How the system is conceptually structured |
| \`specifications/\` | Precise behavioral and technical requirements |
| \`engineering/\` | How the project will be planned and delivered |
| \`research/\` | Questions, investigations, experiments, and findings |
| \`governance/\` | Authority, terminology, decisions, and change control |
| \`journal/\` | Historical record of project evolution |

## Implementation

No implementation structure has been selected yet.

Directories such as \`src/\`, \`apps/\`, \`packages/\`, \`services/\`,
\`crates/\`, or \`cmd/\` should emerge from accepted architectural decisions
rather than be assumed at project inception.
EOF

# ------------------------------------------------------------------------------
# Vision
# ------------------------------------------------------------------------------

write_file "vision/README.md" <<'EOF'
# Vision

This directory defines **why the project should exist**.

Expected artifacts may eventually include:

- `product-vision.md`
- `problem-statement.md`
- `principles.md`
- `goals.md`
- `non-goals.md`
- `success-criteria.md`

The vision layer should remain relatively stable and should not contain detailed
implementation decisions.
EOF

# ------------------------------------------------------------------------------
# Product
# ------------------------------------------------------------------------------

write_file "product/README.md" <<'EOF'
# Product

This directory defines **what the system must accomplish for its users**.

Expected artifacts may eventually include:

- `product-requirements.md`
- `personas.md`
- `use-cases.md`
- `user-journeys.md`
- `capabilities.md`
- `constraints.md`
- `roadmap.md`
EOF

# ------------------------------------------------------------------------------
# Architecture
# ------------------------------------------------------------------------------

write_file "architecture/README.md" <<'EOF'
# Architecture

This directory defines the current architectural understanding of the system.

Architecture should emerge from:

- product requirements;
- system constraints;
- quality attributes;
- research;
- experiments;
- explicit architectural decisions.

Avoid selecting technologies merely because they are familiar or fashionable.
EOF

write_file "architecture/decisions/README.md" <<'EOF'
# Architecture Decision Records

Architecture Decision Records (ADRs) document significant architectural
decisions.

Naming convention:

    ADR-0001-short-description.md

Lifecycle:

    Proposed -> Accepted -> Superseded / Deprecated

Accepted ADRs are authoritative architectural records.
EOF

write_file "architecture/decisions/ADR-0000-template.md" <<'EOF'
# ADR-0000: Decision Title

**Status:** Proposed  
**Date:** YYYY-MM-DD  
**Decision Owners:** TBD

## Context

Describe the problem, forces, constraints, and circumstances requiring a
decision.

## Decision

State the decision clearly and precisely.

## Alternatives Considered

### Alternative 1

Describe the alternative.

### Alternative 2

Describe the alternative.

## Rationale

Explain why the selected decision is preferred.

## Consequences

### Positive

- TBD

### Negative

- TBD

### Neutral

- TBD

## Risks

- TBD

## Follow-up

- TBD
EOF

write_file "architecture/explorations/README.md" <<'EOF'
# Architecture Explorations

This directory contains architectural questions and investigations that have
not yet become accepted decisions.

Typical lifecycle:

    Question
       ↓
    Research
       ↓
    Exploration
       ↓
    Decision
       ↓
    ADR

Explorations are informative, not authoritative.
EOF

write_file "architecture/diagrams/README.md" <<'EOF'
# Architecture Diagrams

Store architecture diagrams and their source representations here.

Prefer diagrams that can be regenerated from source where practical.
EOF

# ------------------------------------------------------------------------------
# Specifications
# ------------------------------------------------------------------------------

write_file "specifications/README.md" <<'EOF'
# Specifications

Specifications translate product and architectural intent into precise,
testable system requirements.

Initial categories:

- `functional/`
- `technical/`
- `interfaces/`
- `data/`
- `security/`
- `operations/`

The taxonomy may evolve as stable system boundaries emerge.
EOF

# ------------------------------------------------------------------------------
# Engineering
# ------------------------------------------------------------------------------

write_file "engineering/README.md" <<'EOF'
# Engineering

This directory defines how the project is planned, executed, reviewed, and
tracked.

Suggested hierarchy:

    Project
      ↓
    Milestone
      ↓
    Program Increment
      ↓
    Work Cycle
      ↓
    Work Packet
      ↓
    Implementation Tasks

Implementation work should trace back to accepted requirements,
specifications, or architectural decisions.
EOF

write_file "engineering/project-status.md" <<EOF
# $PROJECT_NAME — Project Status

**Phase:** Project Inception  
**Implementation Status:** Not started

## Current Objective

Transform \`idea.md\` into an authoritative project definition.

## Current Work

- [ ] Extract canonical terminology
- [ ] Define the problem statement
- [ ] Define product vision
- [ ] Identify users and stakeholders
- [ ] Define goals
- [ ] Define explicit non-goals
- [ ] Identify constraints
- [ ] Identify major capabilities
- [ ] Identify quality attributes
- [ ] Identify major system boundaries
- [ ] Enumerate architectural questions
- [ ] Conduct required research
- [ ] Record architectural decisions
- [ ] Establish initial specifications
- [ ] Define the first engineering increment

## Implementation Gate

Implementation should not begin until the minimum architectural and
specification baseline required for the first work packet is accepted.
EOF

write_file "engineering/definition-of-ready.md" <<'EOF'
# Definition of Ready

A work packet is ready for implementation when:

- its objective is explicit;
- scope is bounded;
- dependencies are identified;
- governing specifications are identified;
- relevant architectural decisions are accepted;
- acceptance criteria are testable;
- known risks are documented;
- unresolved questions do not prevent implementation.
EOF

write_file "engineering/definition-of-done.md" <<'EOF'
# Definition of Done

Work is complete when:

- implementation satisfies its acceptance criteria;
- required tests pass;
- static analysis and quality gates pass;
- documentation is updated;
- architectural or specification changes are recorded;
- no unexplained regressions remain;
- review findings are resolved or explicitly deferred;
- traceability to the governing work packet is preserved.
EOF

write_file "engineering/work-packets/README.md" <<'EOF'
# Work Packets

A work packet is the smallest independently governable engineering unit.

Recommended naming convention:

    WP-<DOMAIN>-NNNN.md

Examples:

    WP-CORE-0001.md
    WP-CLI-0001.md
    WP-API-0001.md
EOF

write_file "engineering/work-packets/template.md" <<'EOF'
# WP-XXXX-0000: Work Packet Title

**Status:** Draft  
**Owner:** TBD  
**Milestone:** TBD  
**Program Increment:** TBD  
**Work Cycle:** TBD

## Objective

State the engineering outcome this work packet must produce.

## Context

Explain why the work is necessary.

## Scope

### In Scope

- TBD

### Out of Scope

- TBD

## Governing Artifacts

- Requirement: TBD
- Specification: TBD
- ADR: TBD

## Dependencies

- TBD

## Deliverables

- TBD

## Acceptance Criteria

- [ ] TBD

## Validation

Describe how correctness will be demonstrated.

## Risks

- TBD

## Completion Evidence

Record tests, commits, pull requests, review artifacts, or other evidence here.
EOF

write_file "engineering/work-packets/active.md" <<'EOF'
# Active Work Packets

No work packets are currently active.
EOF

write_file "engineering/work-packets/backlog.md" <<'EOF'
# Work Packet Backlog

No work packets have been scheduled.
EOF

write_file "engineering/milestones/README.md" <<'EOF'
# Milestones

Milestones represent significant project-level outcomes.
EOF

write_file "engineering/increments/README.md" <<'EOF'
# Program Increments

Program increments group coherent bodies of engineering work toward a
measurable project outcome.
EOF

write_file "engineering/work-cycles/README.md" <<'EOF'
# Work Cycles

Work cycles group related work packets into bounded execution and review units.
EOF

write_file "engineering/reviews/README.md" <<'EOF'
# Engineering Reviews

Store architecture reviews, increment reviews, work-cycle reviews, readiness
reviews, and other formal engineering assessments here.
EOF

write_file "engineering/risks/risk-register.md" <<'EOF'
# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Status |
|---|---|---:|---:|---|---|
| RISK-001 | Initial project risks not yet assessed | TBD | TBD | Perform inception risk review | Open |
EOF

# ------------------------------------------------------------------------------
# Research
# ------------------------------------------------------------------------------

write_file "research/README.md" <<'EOF'
# Research

Research is deliberately separated from authoritative architecture and
specifications.

This directory contains:

- open questions;
- investigations;
- experiments;
- findings;
- references.

Research may inform a decision, but research itself does not constitute an
architectural decision.
EOF

write_file "research/questions.md" <<'EOF'
# Research Questions

## RQ-001

**Question:** What important technical or product uncertainty must be resolved
before architecture is finalized?

**Status:** Open
EOF

# ------------------------------------------------------------------------------
# Governance
# ------------------------------------------------------------------------------

write_file "governance/authority.md" <<'EOF'
# Artifact Authority

This document defines the initial project authority model.

When artifacts conflict, use the most authoritative applicable accepted source.

Initial precedence:

1. Accepted architectural decisions
2. Accepted specifications
3. Current architecture documentation
4. Current product requirements
5. Engineering plans
6. Research and explorations
7. Journal entries and historical artifacts

`idea.md` is the inception source, but later accepted artifacts may refine or
supersede its assumptions.

Contradictions should be resolved explicitly rather than silently ignored.
EOF

write_file "governance/terminology.md" <<'EOF'
# Canonical Terminology

This document defines the project's authoritative vocabulary.

Terms should be added as soon as ambiguity appears.

## Term Template

### Term

**Definition:**  
Precise definition.

**Not synonymous with:**  
Terms that must not be used interchangeably.

**Notes:**  
Additional context.
EOF

write_file "governance/decision-process.md" <<'EOF'
# Decision Process

Significant project decisions should follow this general lifecycle:

    Question
       ↓
    Research
       ↓
    Exploration
       ↓
    Proposal
       ↓
    Review
       ↓
    Decision
       ↓
    Authoritative Artifact

Architectural decisions should normally be recorded as ADRs.
EOF

write_file "governance/change-control.md" <<'EOF'
# Change Control

Changes to authoritative project artifacts should be:

1. intentional;
2. reviewable;
3. traceable;
4. version controlled;
5. reconciled with dependent artifacts.

Accepted decisions should not be silently rewritten in a manner that destroys
their historical context.
EOF

write_file "governance/document-lifecycle.md" <<'EOF'
# Document Lifecycle

Recommended document states:

- Draft
- Proposed
- In Review
- Accepted
- Superseded
- Deprecated
- Historical

Documents should identify their status when authority matters.
EOF

# ------------------------------------------------------------------------------
# Journal
# ------------------------------------------------------------------------------

CURRENT_DATE="$(date +%Y-%m-%d)"

write_file "journal/README.md" <<'EOF'
# Project Journal

The journal records how project understanding evolves over time.

Journal entries are historical records. They are not authoritative
specifications or architectural decisions.
EOF

write_file "journal/0001-project-inception.md" <<EOF
# 0001 — Project Inception

**Date:** $CURRENT_DATE

## Context

The project begins with a developed idea captured in \`idea.md\`.

The repository has intentionally been initialized as a project-definition and
engineering-control environment before an implementation architecture is
selected.

## Initial Principle

The source tree should emerge from accepted architecture rather than force the
architecture to conform to a prematurely selected source tree.

## Next Step

Transform \`idea.md\` into:

1. canonical terminology;
2. problem statement;
3. product vision;
4. goals and non-goals;
5. constraints;
6. capabilities;
7. quality attributes;
8. architecture questions.
EOF

# ------------------------------------------------------------------------------
# GitHub
# ------------------------------------------------------------------------------

write_file ".github/PULL_REQUEST_TEMPLATE.md" <<'EOF'
## Summary

Describe the change.

## Governing Work

- Work Packet:
- Specification:
- ADR:

## Changes

- TBD

## Validation

- [ ] Tests pass
- [ ] Static analysis passes
- [ ] Documentation updated
- [ ] Acceptance criteria satisfied

## Risks

Describe any remaining risks or follow-up work.
EOF

write_file ".github/ISSUE_TEMPLATE/config.yml" <<'EOF'
blank_issues_enabled: true
EOF

write_file ".github/ISSUE_TEMPLATE/work-packet.yml" <<'EOF'
name: Work Packet
description: Track an engineering work packet
title: "WP: "
labels:
  - work-packet
body:
  - type: textarea
    id: objective
    attributes:
      label: Objective
      description: What engineering outcome must this work produce?
    validations:
      required: true

  - type: textarea
    id: scope
    attributes:
      label: Scope
      description: What is included and excluded?
    validations:
      required: true

  - type: textarea
    id: acceptance
    attributes:
      label: Acceptance Criteria
      description: How will completion be demonstrated?
    validations:
      required: true
EOF

# ------------------------------------------------------------------------------
# Repository configuration
# ------------------------------------------------------------------------------

write_file ".editorconfig" <<'EOF'
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
trim_trailing_whitespace = false

[*.{yml,yaml}]
indent_style = space
indent_size = 2
EOF

write_file ".gitattributes" <<'EOF'
* text=auto eol=lf
EOF

write_file ".gitignore" <<'EOF'
# Operating systems
.DS_Store
Thumbs.db

# Editors
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.env.*
!.env.example

# Logs
*.log

# Temporary files
tmp/
temp/
.cache/

# Build output
build/
dist/
coverage/
EOF

# ------------------------------------------------------------------------------
# Git initialization
# ------------------------------------------------------------------------------

if [[ ! -d ".git" ]]; then
  if command -v git >/dev/null 2>&1; then
    git init >/dev/null
    log "Initialized Git repository"
  else
    warn "Git is not installed; repository was not initialized."
  fi
else
  log "Existing Git repository detected"
fi

# ------------------------------------------------------------------------------
# Completion summary
# ------------------------------------------------------------------------------

cat <<EOF

==============================================================================
Bootstrap complete
==============================================================================

Project:
  $PROJECT_NAME

Root:
  $PROJECT_ROOT

Recommended next sequence:

  01. Review idea.md
  02. Populate governance/terminology.md
  03. Create vision/problem-statement.md
  04. Create vision/product-vision.md
  05. Define goals and non-goals
  06. Identify product capabilities
  07. Identify constraints
  08. Define architecture quality attributes
  09. Enumerate architecture questions
  10. Conduct required research and explorations
  11. Record initial ADRs
  12. Establish initial specifications
  13. Define PI-001
  14. Define WC-0001
  15. Define the first work packet
  16. Only then introduce implementation structure

Suggested first commit:

  git add .
  git commit -m "chore: bootstrap project engineering structure"

==============================================================================
EOF
