#!/usr/bin/env bash
set -Eeuo pipefail

# ==============================================================================
# bootstrap-engineering-os.sh
#
# Documentation-first project bootstrap + Engineering Operating System (EOS).
#
# What it provides
# ----------------
# 1. Git version control for every repository file.
# 2. Semantic versions + retained snapshots for governed engineering artifacts.
# 3. A deterministic workflow from idea.md through:
#      inception -> vision -> requirements -> architecture -> specifications
#      -> PI-001 -> WC-0001 -> WP-0001 -> readiness review
# 4. Explicit Human / ChatGPT / Codex / GitHub responsibilities.
# 5. Local EOS commands for status, prompts, completion, versioning, rollback,
#    checkpoints, history, and integrity verification.
#
# Usage
# -----
#   chmod +x bootstrap-engineering-os.sh
#   ./bootstrap-engineering-os.sh my-project
#
# Existing project:
#   cd my-project
#   /path/to/bootstrap-engineering-os.sh .
#
# Optional:
#   PROJECT_NAME="My Project" ./bootstrap-engineering-os.sh .
#
# Safety
# ------
# - Existing files are never overwritten by the bootstrap.
# - Existing idea.md is preserved byte-for-byte.
# - Rollback never destroys history: restored content becomes a new version.
# ==============================================================================

readonly SCRIPT_NAME="$(basename "$0")"
NO_GIT=0
NEW_GIT_REPO=0
TARGET_DIR=""
PROJECT_NAME="${PROJECT_NAME:-}"

log()  { printf '==> %s\n' "$*"; }
warn() { printf 'WARNING: %s\n' "$*" >&2; }
die()  { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<EOF
Usage:
  $SCRIPT_NAME [--no-git] [--name "Project Name"] <project-directory>

Examples:
  $SCRIPT_NAME my-project
  $SCRIPT_NAME --name "Atlas" atlas
  $SCRIPT_NAME .
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-git)
      NO_GIT=1
      shift
      ;;
    --name)
      [[ $# -ge 2 ]] || die "--name requires a value"
      PROJECT_NAME="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      die "Unknown option: $1"
      ;;
    *)
      [[ -z "$TARGET_DIR" ]] || die "Only one project directory may be supplied"
      TARGET_DIR="$1"
      shift
      ;;
  esac
done

[[ -n "$TARGET_DIR" ]] || { usage; exit 1; }
[[ "$TARGET_DIR" != "/" ]] || die "Refusing to scaffold the filesystem root."

mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

PROJECT_ROOT="$(pwd)"
PROJECT_NAME="${PROJECT_NAME:-$(basename "$PROJECT_ROOT")}"
CURRENT_DATE="$(date +%Y-%m-%d)"

log "Project: $PROJECT_NAME"
log "Root:    $PROJECT_ROOT"

create_dir() {
  local path="$1"
  [[ -d "$path" ]] || {
    mkdir -p "$path"
    log "Created directory: $path"
  }
}

write_file() {
  local path="$1"
  if [[ -e "$path" ]]; then
    warn "Preserving existing file: $path"
    cat >/dev/null
    return
  fi
  mkdir -p "$(dirname "$path")"
  cat >"$path"
  log "Created file: $path"
}

write_artifact() {
  local path="$1"
  local artifact_id="$2"
  local title="$3"
  local artifact_type="$4"
  local authority="$5"
  local status="${6:-Draft}"

  if [[ -e "$path" ]]; then
    warn "Preserving existing file: $path"
    cat >/dev/null
    return
  fi

  mkdir -p "$(dirname "$path")"
  {
    cat <<EOF
---
artifact_id: "$artifact_id"
title: "$title"
type: "$artifact_type"
version: "0.1.0"
status: "$status"
authority: "$authority"
created: "$CURRENT_DATE"
updated: "$CURRENT_DATE"
---

EOF
    cat
  } >"$path"

  log "Created artifact: $path [$artifact_id v0.1.0]"
}

dirs=(
  ".eos"
  ".eos/history"
  ".eos/checkpoints"
  ".eos/prompts"
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
  "engineering/prompts"
  "research"
  "research/findings"
  "research/experiments"
  "research/references"
  "governance"
  "journal"
  "scripts"
  ".github"
  ".github/ISSUE_TEMPLATE"
  ".github/workflows"
)

for d in "${dirs[@]}"; do
  create_dir "$d"
done

# ------------------------------------------------------------------------------
# Root / inception
# ------------------------------------------------------------------------------

if [[ ! -e idea.md ]]; then
  write_artifact \
    "idea.md" \
    "INCEPT-IDEA-0001" \
    "$PROJECT_NAME Project Idea" \
    "inception-source" \
    "historical-source" \
    "Draft" <<EOF
# $PROJECT_NAME — Project Idea

## Purpose

Describe the project thoroughly.

## Problem

What meaningful problem should this project solve?

## Intended Users and Stakeholders

Who should benefit from or interact with the system?

## Desired Outcomes

What should be true when the project succeeds?

## Capabilities

What should the system eventually be capable of doing?

## Constraints

Record known technical, business, legal, financial, operational, security,
usability, portability, interoperability, and schedule constraints.

## Assumptions

What is currently believed to be true but has not yet been validated?

## Risks

What could materially prevent success?

## Open Questions

What requires investigation before design or implementation?
EOF
else
  log "Preserving existing idea.md exactly as supplied"
fi

write_file "VERSION" <<'EOF'
0.1.0
EOF

write_file "README.md" <<EOF
# $PROJECT_NAME

This repository is initialized as a **documentation-first Engineering Operating
System**. The implementation tree is intentionally deferred until the product,
architecture, and specification baseline justify it.

## Start Here

1. \`idea.md\`
2. \`engineering/project-status.md\`
3. \`governance/authority.md\`
4. \`governance/responsibility-model.md\`
5. \`.eos/workflow.tsv\`

## EOS CLI

\`\`\`bash
./scripts/eos status
./scripts/eos next
./scripts/eos prompt EOSB-001
./scripts/eos complete EOSB-001
./scripts/eos checkpoint "finish EOSB-001"
\`\`\`

## Versioning

**Every file in the repository is versioned by Git.**

Governed engineering artifacts also carry explicit semantic versions such as
\`0.1.0\`, and prior artifact bodies are retained beneath \`.eos/history/\`.

Use:

\`\`\`bash
./scripts/eos version path/to/artifact.md patch "reason for change"
./scripts/eos history path/to/artifact.md
./scripts/eos rollback path/to/artifact.md 0.2.0 "restore known-good content"
\`\`\`

Rollback is non-destructive: restored content becomes a **new** version.

## Project Flow

\`\`\`text
idea.md
  -> inception review
  -> terminology
  -> problem statement
  -> product vision
  -> goals / non-goals / principles
  -> users / use cases / journeys
  -> capabilities / requirements / constraints
  -> quality attributes
  -> system context and boundaries
  -> research questions / architecture explorations
  -> architectural decisions
  -> specification baseline
  -> PI-001
  -> WC-0001
  -> WP-0001
  -> implementation-readiness review
\`\`\`
EOF

write_file "CHANGELOG.md" <<EOF
# Changelog

All notable project-level changes should be recorded here.

The repository itself is versioned with Git. Governed artifact-level version
changes are recorded in \`.eos/artifact-changelog.tsv\`.

## [0.1.0] - $CURRENT_DATE

### Added

- Initial Engineering Operating System scaffold.
- Governed artifact versioning and rollback mechanism.
- Inception-to-first-work-packet workflow.
EOF

write_file "LICENSE" <<'EOF'
No project license has been selected yet.

Until an explicit license is adopted, no permissions are granted beyond those
provided by applicable law. Replace this file with the selected license before
public distribution.
EOF

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
.DS_Store
Thumbs.db
.idea/
.vscode/
*.swp
*.swo
.env
.env.*
!.env.example
*.log
tmp/
temp/
.cache/
build/
dist/
coverage/
EOF

# ------------------------------------------------------------------------------
# Vision
# ------------------------------------------------------------------------------

write_artifact "vision/README.md" "VIS-INDEX-0001" "Vision Index" "index" "informative" <<'EOF'
# Vision

Vision artifacts answer **why this project should exist** and what durable
outcomes it is intended to produce.

Authoritative vision artifacts are created and refined through the EOS
bootstrap workflow.
EOF

write_artifact "vision/problem-statement.md" "VIS-PROB-0001" "Problem Statement" "vision" "product-authoritative" <<'EOF'
# Problem Statement

## Current Situation

TBD from `idea.md`.

## Problem

TBD from `idea.md`.

## Who Experiences the Problem

TBD.

## Why Existing Approaches Are Insufficient

TBD.

## Evidence and Assumptions

Separate evidence from assumptions.

## Consequences of Inaction

TBD.

## Problem Boundaries

State what is and is not part of the problem.
EOF

write_artifact "vision/product-vision.md" "VIS-PROD-0001" "Product Vision" "vision" "product-authoritative" <<'EOF'
# Product Vision

## Vision Statement

TBD from the accepted problem statement and `idea.md`.

## Intended Future State

TBD.

## Value Proposition

TBD.

## Strategic Differentiators

TBD.

## Durable Constraints

TBD.

## Success Conditions

TBD.
EOF

write_artifact "vision/principles.md" "VIS-PRIN-0001" "Project Principles" "vision" "governance-authoritative" <<'EOF'
# Project Principles

Principles are durable decision rules used when requirements or tradeoffs are
ambiguous.

## Principles

TBD from `idea.md` and inception review.

Each principle should include:

- statement;
- rationale;
- expected behavior;
- anti-patterns;
- implications.
EOF

write_artifact "vision/goals.md" "VIS-GOAL-0001" "Project Goals" "vision" "product-authoritative" <<'EOF'
# Project Goals

Define measurable outcomes the project is explicitly intended to achieve.

## Goals

TBD.
EOF

write_artifact "vision/non-goals.md" "VIS-NOGOAL-0001" "Project Non-Goals" "vision" "product-authoritative" <<'EOF'
# Project Non-Goals

Explicitly identify attractive or adjacent concerns that the project will not
attempt to solve within the current mission or horizon.

## Non-Goals

TBD.
EOF

write_artifact "vision/success-criteria.md" "VIS-SUCCESS-0001" "Success Criteria" "vision" "product-authoritative" <<'EOF'
# Success Criteria

Define observable and measurable conditions indicating project, product, and
engineering success.

## Product Success

TBD.

## Engineering Success

TBD.

## Operational Success

TBD.
EOF

# ------------------------------------------------------------------------------
# Product
# ------------------------------------------------------------------------------

write_artifact "product/README.md" "PROD-INDEX-0001" "Product Index" "index" "informative" <<'EOF'
# Product

Product artifacts translate the vision into users, outcomes, capabilities,
constraints, journeys, and testable requirements.
EOF

write_artifact "product/personas.md" "PROD-PERS-0001" "Personas and Stakeholders" "product" "product-authoritative" <<'EOF'
# Personas and Stakeholders

## Primary Users

TBD.

## Secondary Users

TBD.

## Operators and Maintainers

TBD.

## External Stakeholders

TBD.

## Anti-Personas

Identify users or use patterns the product is not intended to serve.
EOF

write_artifact "product/use-cases.md" "PROD-USE-0001" "Use Cases" "product" "product-authoritative" <<'EOF'
# Use Cases

Each use case should identify:

- actor;
- intent;
- preconditions;
- trigger;
- normal flow;
- alternate flows;
- failure modes;
- postconditions;
- related requirements.
EOF

write_artifact "product/user-journeys.md" "PROD-JOURNEY-0001" "User Journeys" "product" "product-authoritative" <<'EOF'
# User Journeys

Model meaningful end-to-end experiences rather than isolated screens or
commands.

## Journey Template

### Journey

- Actor:
- Starting state:
- Desired outcome:
- Steps:
- Friction:
- Failure recovery:
- Completion signal:
EOF

write_artifact "product/capabilities.md" "PROD-CAP-0001" "Product Capabilities" "product" "product-authoritative" <<'EOF'
# Product Capabilities

Capabilities describe what the system can do without prematurely constraining
implementation.

## Capability Template

### CAP-XXXX

**Name:** TBD

**Statement:** The system can ...

**Users served:** TBD

**Related goals:** TBD

**Constraints:** TBD
EOF

write_artifact "product/product-requirements.md" "PROD-REQ-0001" "Product Requirements" "requirements" "requirements-authoritative" <<'EOF'
# Product Requirements

Requirements must be unambiguous, testable, traceable, and implementation
neutral unless implementation is itself a requirement.

## Requirement Template

### REQ-0001

**Statement:** The system MUST ...

**Rationale:** TBD

**Source:** TBD

**Priority:** TBD

**Acceptance evidence:** TBD

**Related capabilities:** TBD
EOF

write_artifact "product/constraints.md" "PROD-CON-0001" "Project and Product Constraints" "product" "product-authoritative" <<'EOF'
# Constraints

Record constraints separately from preferences and assumptions.

## Categories

- Technical
- Operational
- Security
- Privacy
- Compliance
- Financial
- Schedule
- Portability
- Interoperability
- Accessibility
- Maintainability
- Team / staffing
EOF

write_artifact "product/roadmap.md" "PROD-ROAD-0001" "Product Roadmap" "planning" "planning-authoritative" <<'EOF'
# Product Roadmap

The roadmap should describe outcome horizons rather than fabricate precision.

## Now

TBD.

## Next

TBD.

## Later

TBD.

## Explicitly Unscheduled

TBD.
EOF

# ------------------------------------------------------------------------------
# Architecture
# ------------------------------------------------------------------------------

write_artifact "architecture/README.md" "ARCH-INDEX-0001" "Architecture Index" "index" "informative" <<'EOF'
# Architecture

Architecture captures the accepted structural model and the quality attributes,
constraints, and decisions that shape it.

Technology choices should follow requirements and evidence rather than precede
them.
EOF

write_artifact "architecture/context.md" "ARCH-CTX-0001" "System Context" "architecture" "architecture-authoritative" <<'EOF'
# System Context

## System of Interest

TBD.

## Users and External Actors

TBD.

## External Systems

TBD.

## Trust Boundaries

TBD.

## Data Entering and Leaving the System

TBD.
EOF

write_artifact "architecture/system-boundaries.md" "ARCH-BOUND-0001" "System Boundaries" "architecture" "architecture-authoritative" <<'EOF'
# System Boundaries

## Inside the System

TBD.

## Outside the System

TBD.

## Managed Dependencies

TBD.

## External Dependencies

TBD.

## Boundary Rationale

TBD.
EOF

write_artifact "architecture/quality-attributes.md" "ARCH-QA-0001" "Quality Attributes" "architecture" "architecture-authoritative" <<'EOF'
# Quality Attributes

Quality attributes should be expressed as testable scenarios where practical.

Consider:

- correctness;
- security;
- reliability;
- availability;
- recoverability;
- performance;
- scalability;
- maintainability;
- modifiability;
- portability;
- interoperability;
- usability;
- accessibility;
- observability;
- reproducibility;
- testability;
- deployability;
- cost efficiency.

## Quality Attribute Scenario Template

### QA-0001

**Attribute:** TBD

**Source:** TBD

**Stimulus:** TBD

**Environment:** TBD

**Artifact:** TBD

**Response:** TBD

**Response measure:** TBD
EOF

write_artifact "architecture/overview.md" "ARCH-OVR-0001" "Architecture Overview" "architecture" "architecture-authoritative" <<'EOF'
# Architecture Overview

This document should summarize accepted architecture only after context,
boundaries, quality attributes, research, and major ADRs are sufficiently
mature.

## Context

TBD.

## Architectural Style

TBD.

## Major Components

TBD.

## Data and Control Flow

TBD.

## Deployment Model

TBD.

## Security Model

TBD.

## Key Decisions

TBD.

## Known Architectural Risks

TBD.
EOF

write_artifact "architecture/decisions/README.md" "ADR-INDEX-0001" "Architecture Decision Record Index" "index" "architecture-authoritative" <<'EOF'
# Architecture Decision Records

Naming:

`ADR-NNNN-short-description.md`

Lifecycle:

`Proposed -> Accepted -> Superseded | Deprecated | Rejected`

An accepted ADR records a significant architectural decision and its
consequences.
EOF

write_artifact "architecture/decisions/ADR-0000-template.md" "ADR-0000" "ADR Template" "template" "informative" <<'EOF'
# ADR-0000: Decision Title

## Context

What forces, constraints, requirements, or uncertainty require a decision?

## Decision

State the decision precisely.

## Alternatives Considered

Document credible alternatives.

## Rationale

Why is this decision preferable under the known constraints?

## Consequences

### Positive

- TBD

### Negative

- TBD

### Neutral / Tradeoffs

- TBD

## Validation

How will we know the decision remains appropriate?

## Related Artifacts

- Requirements:
- Quality attributes:
- Research:
- Specifications:
EOF

write_artifact "architecture/explorations/README.md" "ARCH-EXP-INDEX-0001" "Architecture Exploration Index" "index" "informative" <<'EOF'
# Architecture Explorations

Explorations are not decisions.

Preferred flow:

`question -> research -> experiment -> exploration -> decision -> ADR`
EOF

write_artifact "architecture/diagrams/README.md" "ARCH-DIAG-INDEX-0001" "Architecture Diagram Index" "index" "informative" <<'EOF'
# Architecture Diagrams

Prefer source-controlled, regenerable diagram definitions where practical.
Every diagram should identify which architecture version or decisions it
represents.
EOF

# ------------------------------------------------------------------------------
# Specifications
# ------------------------------------------------------------------------------

write_artifact "specifications/README.md" "SPEC-INDEX-0001" "Specification Index" "index" "specification-authoritative" <<'EOF'
# Specifications

Specifications bridge accepted product/architecture intent and implementation.

Initial taxonomy:

- `functional/`
- `technical/`
- `interfaces/`
- `data/`
- `security/`
- `operations/`

Specifications should have stable identifiers and explicit acceptance evidence.
EOF

write_artifact "specifications/baseline.md" "SPEC-BASE-0001" "Initial Specification Baseline" "specification" "specification-authoritative" <<'EOF'
# Initial Specification Baseline

## Purpose

Identify the minimum set of specifications required to authorize PI-001 and its
first work cycle.

## Governing Requirements

TBD.

## Required Specifications

TBD.

## Traceability Expectations

Every implementation work packet should identify the requirements,
specifications, ADRs, and quality attributes it satisfies.
EOF

# ------------------------------------------------------------------------------
# Engineering
# ------------------------------------------------------------------------------

write_artifact "engineering/README.md" "ENG-INDEX-0001" "Engineering Index" "index" "informative" <<'EOF'
# Engineering

Execution hierarchy:

`Project -> Milestone -> Program Increment -> Work Cycle -> Work Packet -> Tasks`

A work packet is the smallest independently governable implementation unit.
EOF

write_artifact "engineering/project-status.md" "ENG-STATUS-0001" "Project Status" "status" "planning-authoritative" <<EOF
# $PROJECT_NAME — Project Status

## Current Phase

Engineering Operating System bootstrap.

## Current Objective

Transform \`idea.md\` into a coherent, traceable, reviewable baseline that can
safely authorize the first implementation work packet.

## Implementation Status

Not authorized.

## Current Gate

Complete the EOSB workflow through the implementation-readiness review.

## Status Command

\`\`\`bash
./scripts/eos status
\`\`\`
EOF

write_artifact "engineering/definition-of-ready.md" "ENG-DOR-0001" "Definition of Ready" "governance" "governance-authoritative" <<'EOF'
# Definition of Ready

A work packet is Ready when:

- its objective is explicit;
- scope and exclusions are bounded;
- governing requirements are identified;
- governing specifications are identified;
- relevant ADRs are accepted or explicitly not required;
- dependencies are understood;
- risks are recorded;
- acceptance criteria are testable;
- required validation can be performed;
- unresolved questions do not block implementation.
EOF

write_artifact "engineering/definition-of-done.md" "ENG-DOD-0001" "Definition of Done" "governance" "governance-authoritative" <<'EOF'
# Definition of Done

Work is Done when:

- acceptance criteria are satisfied;
- required tests pass;
- static and dynamic quality gates pass;
- security requirements are satisfied;
- documentation is synchronized;
- traceability is preserved;
- review findings are resolved or formally deferred;
- no unexplained regression remains;
- completion evidence is recorded.
EOF

write_artifact "engineering/milestones/README.md" "ENG-MILE-INDEX-0001" "Milestone Index" "index" "planning-authoritative" <<'EOF'
# Milestones

Milestones represent meaningful project-level outcomes, not arbitrary dates.
EOF

write_artifact "engineering/increments/README.md" "ENG-PI-INDEX-0001" "Program Increment Index" "index" "planning-authoritative" <<'EOF'
# Program Increments

Program increments contain coherent sets of work cycles that advance a
measurable product or architecture outcome.
EOF

write_artifact "engineering/increments/PI-001.md" "PI-001" "Program Increment 001" "program-increment" "planning-authoritative" <<'EOF'
# PI-001 — Initial Implementation Increment

**State:** Draft / Not Authorized

## Objective

TBD after the initial specification baseline is accepted.

## Outcomes

TBD.

## Governing Artifacts

TBD.

## Included Work Cycles

- WC-0001 — TBD

## Exclusions

TBD.

## Risks

TBD.

## Entry Criteria

TBD.

## Exit Criteria

TBD.
EOF

write_artifact "engineering/work-cycles/README.md" "ENG-WC-INDEX-0001" "Work Cycle Index" "index" "planning-authoritative" <<'EOF'
# Work Cycles

A work cycle groups related work packets into a bounded execution and review
unit.
EOF

write_artifact "engineering/work-cycles/WC-0001.md" "WC-0001" "Work Cycle 0001" "work-cycle" "planning-authoritative" <<'EOF'
# WC-0001 — First Work Cycle

**State:** Draft / Not Authorized

## Objective

TBD from PI-001.

## Governing Program Increment

PI-001

## Included Work Packets

- WP-0001 — TBD

## Entry Criteria

TBD.

## Exit Criteria

TBD.

## Review

A work-cycle review is required before closure.
EOF

write_artifact "engineering/work-packets/README.md" "ENG-WP-INDEX-0001" "Work Packet Index" "index" "planning-authoritative" <<'EOF'
# Work Packets

A work packet is the smallest independently governable engineering unit.

A work packet should map cleanly to an implementation branch, issue, and pull
request whenever practical.
EOF

write_artifact "engineering/work-packets/WP-0001.md" "WP-0001" "First Work Packet" "work-packet" "planning-authoritative" <<'EOF'
# WP-0001 — First Implementation Work Packet

**State:** Draft / Not Authorized

## Objective

TBD.

## Parent

- PI: PI-001
- Work Cycle: WC-0001

## Scope

### In Scope

TBD.

### Out of Scope

TBD.

## Governing Artifacts

- Requirements: TBD
- Specifications: TBD
- ADRs: TBD
- Quality attributes: TBD

## Dependencies

TBD.

## Deliverables

TBD.

## Acceptance Criteria

- [ ] TBD

## Validation

TBD.

## Risks

TBD.

## Completion Evidence

TBD.
EOF

write_artifact "engineering/work-packets/template.md" "WP-TEMPLATE-0001" "Work Packet Template" "template" "informative" <<'EOF'
# WP-XXXX — Work Packet Title

## Objective

TBD.

## Parent

- PI:
- Work Cycle:

## Scope

### In Scope

### Out of Scope

## Governing Artifacts

## Dependencies

## Deliverables

## Acceptance Criteria

## Validation

## Risks

## Completion Evidence
EOF

write_artifact "engineering/reviews/INCEPTION-REVIEW.md" "REV-INCEPT-0001" "Inception Review" "review" "review-authoritative" <<'EOF'
# Inception Review

## Purpose

Evaluate `idea.md` without prematurely choosing implementation architecture.

## Summary of the Idea

TBD.

## Core Problem

TBD.

## Intended Users

TBD.

## Desired Outcomes

TBD.

## Assumptions

TBD.

## Constraints

TBD.

## Risks

TBD.

## Contradictions or Ambiguities

TBD.

## Missing Information

TBD.

## Recommended Next Steps

TBD.

## Review Decision

**Decision:** Pending
EOF

write_artifact "engineering/reviews/PI-001-READINESS-REVIEW.md" "REV-PI001-READY-0001" "PI-001 Implementation Readiness Review" "review" "review-authoritative" <<'EOF'
# PI-001 Implementation Readiness Review

## Question

Is there sufficient accepted product, architecture, specification, and
engineering definition to authorize WC-0001 and WP-0001?

## Evidence

### Vision

TBD.

### Requirements

TBD.

### Architecture

TBD.

### Specifications

TBD.

### Traceability

TBD.

### Risks

TBD.

## Blocking Findings

TBD.

## Non-Blocking Findings

TBD.

## Decision

**Authorization:** NOT YET GRANTED

Possible final values:

- AUTHORIZED
- AUTHORIZED WITH CONDITIONS
- NOT AUTHORIZED
EOF

write_artifact "engineering/risks/risk-register.md" "RISK-REG-0001" "Risk Register" "risk-register" "planning-authoritative" <<'EOF'
# Risk Register

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| RISK-001 | Inception risks have not yet been fully assessed | TBD | TBD | Complete EOSB inception and architecture analysis | Human | Open |
EOF

# ------------------------------------------------------------------------------
# Research
# ------------------------------------------------------------------------------

write_artifact "research/README.md" "RSRCH-INDEX-0001" "Research Index" "index" "informative" <<'EOF'
# Research

Research informs decisions but is not itself an accepted architectural
decision.
EOF

write_artifact "research/questions.md" "RSRCH-Q-0001" "Research Questions" "research" "informative" <<'EOF'
# Research Questions

Questions should be created from explicit uncertainty discovered during
inception, product, and architecture analysis.

## Template

### RQ-0001

**Question:** TBD

**Why it matters:** TBD

**Decision blocked by this question:** TBD

**Evidence required:** TBD

**Status:** Open
EOF

# ------------------------------------------------------------------------------
# Governance
# ------------------------------------------------------------------------------

write_artifact "governance/authority.md" "GOV-AUTH-0001" "Artifact Authority Model" "governance" "governance-authoritative" <<'EOF'
# Artifact Authority Model

When artifacts conflict, use the most authoritative applicable **accepted**
artifact.

Initial precedence:

1. Explicit human approval / governing project constitution
2. Accepted ADRs for architectural decisions
3. Accepted specifications
4. Accepted product requirements and constraints
5. Current architecture documentation
6. Approved engineering plans
7. Research findings and explorations
8. Journal entries and historical artifacts

`idea.md` is the inception source. It is historically important but may be
refined or superseded by later accepted artifacts.

Contradictions must be surfaced and reconciled explicitly.
EOF

write_artifact "governance/terminology.md" "GOV-TERM-0001" "Canonical Terminology" "governance" "governance-authoritative" <<'EOF'
# Canonical Terminology

Canonical terms should be extracted from `idea.md` before detailed architecture
or implementation begins.

## Term Template

### TERM

**Definition:** TBD

**Not synonymous with:** TBD

**Aliases:** TBD

**Notes:** TBD
EOF

write_artifact "governance/decision-process.md" "GOV-DEC-0001" "Decision Process" "governance" "governance-authoritative" <<'EOF'
# Decision Process

Preferred decision lifecycle:

`question -> research -> exploration -> proposal -> review -> decision -> accepted artifact`

Significant architectural decisions become ADRs.

Decisions should identify:

- decision owner;
- context;
- alternatives;
- evidence;
- rationale;
- consequences;
- review status;
- supersession relationship.
EOF

write_artifact "governance/change-control.md" "GOV-CHANGE-0001" "Change Control" "governance" "governance-authoritative" <<'EOF'
# Change Control

Authoritative artifacts are changed intentionally and traceably.

## Rules

1. Do not silently overwrite accepted decisions.
2. Version governed artifacts when their meaning changes.
3. Preserve prior versions.
4. Record the reason for the change.
5. Update dependent artifacts when required.
6. Prefer PR review for authoritative changes once collaboration begins.
7. Rollback restores old content as a **new** version instead of erasing
   intervening history.
EOF

write_artifact "governance/document-lifecycle.md" "GOV-DOC-0001" "Document Lifecycle" "governance" "governance-authoritative" <<'EOF'
# Document Lifecycle

Recommended states:

- Draft
- Proposed
- In Review
- Accepted
- Superseded
- Deprecated
- Rejected
- Historical

Version guidance:

- PATCH: clarification or correction without changing intent;
- MINOR: backward-compatible expansion or meaningful addition;
- MAJOR: change that invalidates or materially revises prior assumptions,
  interfaces, obligations, or decisions.
EOF

write_artifact "governance/responsibility-model.md" "GOV-RACI-0001" "Human ChatGPT Codex GitHub Responsibility Model" "governance" "governance-authoritative" <<'EOF'
# Human / ChatGPT / Codex / GitHub Responsibility Model

## Human

The human is the final project authority.

Responsibilities:

- define intent and values;
- resolve ambiguous product or business questions;
- approve or reject major scope and architectural decisions;
- authorize implementation gates;
- accept material risk;
- approve releases or irreversible external actions.

The human should not be forced to manually perform mechanical consistency work
that tools can verify.

## ChatGPT

ChatGPT is the primary reasoning, synthesis, planning, and review collaborator.

Responsibilities:

- analyze `idea.md`;
- extract terminology, assumptions, goals, constraints, and open questions;
- draft and reconcile project artifacts;
- identify contradictions and missing decisions;
- propose architecture based on requirements and quality attributes;
- maintain cross-artifact traceability;
- define PIs, WCs, and WPs;
- review Codex output against governing artifacts;
- recommend whether gates should pass.

ChatGPT may propose decisions, but major decisions remain subject to human
authority.

## Codex

Codex is the repository-local implementation and verification agent.

Responsibilities:

- inspect the current repository state before changing files;
- implement bounded work packets;
- modify only authorized scope;
- run tests, formatters, linters, builds, and validation;
- report exact changed files and verification evidence;
- prepare commits and pull requests when authorized;
- surface conflicts instead of inventing new product or architecture policy.

Codex should not silently redefine requirements or architecture to make an
implementation easier.

## GitHub

GitHub is the durable collaboration, history, review, and integration system.

Responsibilities:

- canonical Git remote;
- immutable commit history;
- branches and pull requests;
- issue / work packet tracking;
- project and milestone visibility;
- review record;
- CI and policy enforcement;
- releases and tags;
- durable audit trail.

## Default Handoff

`Human intent -> ChatGPT definition/review -> Codex implementation -> GitHub
history/CI/review -> ChatGPT conformance review -> Human gate decision`

## Automation Principle

Automate deterministic mechanics. Preserve explicit human authority over
mission, risk acceptance, major tradeoffs, and irreversible actions.
EOF

write_artifact "governance/versioning-policy.md" "GOV-VERSION-0001" "Repository and Artifact Versioning Policy" "governance" "governance-authoritative" <<'EOF'
# Repository and Artifact Versioning Policy

## Repository Files

Every tracked file is versioned by Git. Git history is the authoritative record
of repository state.

## Governed Artifacts

Governed Markdown artifacts additionally carry an explicit semantic `version`
in YAML front matter.

Before an artifact version is changed, the current version is copied to:

`.eos/history/<artifact-path>/v<version>.md`

The change is also recorded in:

`.eos/artifact-changelog.tsv`

## Rollback

Rollback does not erase history. The requested historical content is restored
and assigned a new version derived from the current version.

## Repository Checkpoints

Use:

`./scripts/eos checkpoint "message"`

This creates a Git commit and an annotated `eos/checkpoint-*` tag.

## Releases

Project release tags and artifact versions are separate concerns. Project
release policy should be established before the first external release.
EOF

write_artifact "governance/traceability.md" "GOV-TRACE-0001" "Traceability Model" "governance" "governance-authoritative" <<'EOF'
# Traceability Model

Desired chain:

`idea -> goal -> capability -> requirement -> quality attribute -> ADR /
specification -> PI -> WC -> WP -> commit -> PR -> test / evidence`

A work packet should identify its governing artifacts. A pull request should
identify its work packet. Validation evidence should identify the requirement or
acceptance criterion it proves.
EOF

# ------------------------------------------------------------------------------
# Journal
# ------------------------------------------------------------------------------

write_artifact "journal/README.md" "JRN-INDEX-0001" "Project Journal Index" "index" "historical" <<'EOF'
# Project Journal

The journal records how project understanding evolved. It is historical and
does not override accepted requirements, specifications, or decisions.
EOF

write_artifact "journal/0001-project-inception.md" "JRN-0001" "Project Inception" "journal" "historical" <<EOF
# 0001 — Project Inception

## Date

$CURRENT_DATE

## Starting Point

The project begins with a thoroughly described \`idea.md\`.

## Engineering Principle

Implementation structure will emerge from accepted project definition and
architecture rather than being chosen prematurely.

## Versioning Principle

Git preserves every repository file. Governed artifacts additionally use
semantic artifact versions and retained historical snapshots.

## Bootstrap Goal

Drive the project through a controlled inception sequence until PI-001,
WC-0001, and WP-0001 are defined and reviewed for implementation readiness.
EOF

# ------------------------------------------------------------------------------
# EOS registry / workflow
# ------------------------------------------------------------------------------

write_file ".eos/README.md" <<'EOF'
# .eos

Internal Engineering Operating System state.

- `workflow.tsv` — ordered bootstrap workflow
- `artifacts.tsv` — governed artifact registry
- `artifact-changelog.tsv` — semantic artifact version changes
- `history/` — retained prior governed artifact bodies
- `checkpoints/` — checkpoint metadata
- `prompts/` — generated prompt material

This directory is intentionally committed to Git except for ephemeral files.
EOF

write_file ".eos/artifact-changelog.tsv" <<'EOF'
timestamp	artifact_id	path	from_version	to_version	change_type	message
EOF

write_file ".eos/artifacts.tsv" <<'EOF'
artifact_id	path	type	authority
INCEPT-IDEA-0001	idea.md	inception-source	historical-source
REV-INCEPT-0001	engineering/reviews/INCEPTION-REVIEW.md	review	review-authoritative
GOV-TERM-0001	governance/terminology.md	governance	governance-authoritative
VIS-PROB-0001	vision/problem-statement.md	vision	product-authoritative
VIS-PROD-0001	vision/product-vision.md	vision	product-authoritative
VIS-PRIN-0001	vision/principles.md	vision	governance-authoritative
VIS-GOAL-0001	vision/goals.md	vision	product-authoritative
VIS-NOGOAL-0001	vision/non-goals.md	vision	product-authoritative
PROD-PERS-0001	product/personas.md	product	product-authoritative
PROD-USE-0001	product/use-cases.md	product	product-authoritative
PROD-JOURNEY-0001	product/user-journeys.md	product	product-authoritative
PROD-CAP-0001	product/capabilities.md	product	product-authoritative
PROD-REQ-0001	product/product-requirements.md	requirements	requirements-authoritative
PROD-CON-0001	product/constraints.md	product	product-authoritative
ARCH-QA-0001	architecture/quality-attributes.md	architecture	architecture-authoritative
ARCH-CTX-0001	architecture/context.md	architecture	architecture-authoritative
ARCH-BOUND-0001	architecture/system-boundaries.md	architecture	architecture-authoritative
RSRCH-Q-0001	research/questions.md	research	informative
ARCH-OVR-0001	architecture/overview.md	architecture	architecture-authoritative
SPEC-BASE-0001	specifications/baseline.md	specification	specification-authoritative
PI-001	engineering/increments/PI-001.md	program-increment	planning-authoritative
WC-0001	engineering/work-cycles/WC-0001.md	work-cycle	planning-authoritative
WP-0001	engineering/work-packets/WP-0001.md	work-packet	planning-authoritative
REV-PI001-READY-0001	engineering/reviews/PI-001-READINESS-REVIEW.md	review	review-authoritative
EOF

write_file ".eos/workflow.tsv" <<'EOF'
order	stage	phase	primary_output	lead	reviewer	gate	status	completed_at
001	EOSB-001	inception	engineering/reviews/INCEPTION-REVIEW.md	ChatGPT	Human	inception-understood	PENDING	-
002	EOSB-002	inception	governance/terminology.md	ChatGPT	Human	canonical-language	PENDING	-
003	EOSB-003	vision	vision/problem-statement.md	ChatGPT	Human	problem-defined	PENDING	-
004	EOSB-004	vision	vision/product-vision.md	ChatGPT	Human	vision-defined	PENDING	-
005	EOSB-005	vision	vision/principles.md	ChatGPT	Human	principles-defined	PENDING	-
006	EOSB-006	vision	vision/goals.md	ChatGPT	Human	goals-and-non-goals	PENDING	-
007	EOSB-007	product	product/personas.md	ChatGPT	Human	users-understood	PENDING	-
008	EOSB-008	product	product/capabilities.md	ChatGPT	Human	capabilities-defined	PENDING	-
009	EOSB-009	requirements	product/product-requirements.md	ChatGPT	Human	requirements-baseline	PENDING	-
010	EOSB-010	requirements	product/constraints.md	ChatGPT	Human	constraints-baseline	PENDING	-
011	EOSB-011	architecture	architecture/quality-attributes.md	ChatGPT	Human	quality-baseline	PENDING	-
012	EOSB-012	architecture	architecture/context.md	ChatGPT	Human	context-and-boundaries	PENDING	-
013	EOSB-013	research	research/questions.md	ChatGPT	Human	uncertainty-explicit	PENDING	-
014	EOSB-014	architecture	architecture/overview.md	ChatGPT	Human	architecture-proposed	PENDING	-
015	EOSB-015	architecture	architecture/decisions/README.md	ChatGPT	Human	major-decisions-recorded	PENDING	-
016	EOSB-016	specifications	specifications/baseline.md	ChatGPT	Human	specification-baseline	PENDING	-
017	EOSB-017	planning	engineering/increments/PI-001.md	ChatGPT	Human	pi-defined	PENDING	-
018	EOSB-018	planning	engineering/work-cycles/WC-0001.md	ChatGPT	Human	wc-defined	PENDING	-
019	EOSB-019	planning	engineering/work-packets/WP-0001.md	ChatGPT	Human	wp-ready	PENDING	-
020	EOSB-020	readiness	engineering/reviews/PI-001-READINESS-REVIEW.md	ChatGPT	Human	implementation-authorization	PENDING	-
EOF

# ------------------------------------------------------------------------------
# Prompt catalog
# ------------------------------------------------------------------------------

write_file "engineering/prompts/README.md" <<'EOF'
# EOS Prompt Catalog

The EOS CLI renders stage prompts with current project context.

Use:

`./scripts/eos prompt EOSB-001`

The generated prompt intentionally asks ChatGPT to produce or review a specific
governed artifact while respecting already accepted higher-authority material.
EOF

write_file ".eos/prompts/EOSB-001.md" <<'EOF'
Perform a rigorous inception review of idea.md. Extract the core problem,
intended users, desired outcomes, capabilities, assumptions, constraints,
risks, contradictions, ambiguity, and missing information. Do not select an
implementation architecture yet. Update engineering/reviews/INCEPTION-REVIEW.md.
EOF

write_file ".eos/prompts/EOSB-002.md" <<'EOF'
Extract and normalize canonical project terminology from idea.md and the
accepted inception review. Define ambiguous terms precisely, identify aliases,
and explicitly separate terms that must not be used synonymously. Update
governance/terminology.md.
EOF

write_file ".eos/prompts/EOSB-003.md" <<'EOF'
Create a precise problem statement from idea.md, the inception review, and
canonical terminology. Separate evidence from assumptions, identify who
experiences the problem, explain consequences, and define problem boundaries.
Update vision/problem-statement.md.
EOF

write_file ".eos/prompts/EOSB-004.md" <<'EOF'
Derive the product vision from the accepted problem statement and inception
source. Define intended future state, value proposition, strategic
differentiators, durable constraints, and success conditions. Update
vision/product-vision.md.
EOF

write_file ".eos/prompts/EOSB-005.md" <<'EOF'
Derive durable project and engineering principles. Each principle must include
rationale, behavioral implications, anti-patterns, and tradeoff guidance.
Update vision/principles.md.
EOF

write_file ".eos/prompts/EOSB-006.md" <<'EOF'
Define measurable goals, explicit non-goals, and success criteria. Keep goals
outcome-oriented and non-goals strong enough to prevent scope creep. Update
vision/goals.md, vision/non-goals.md, and vision/success-criteria.md.
EOF

write_file ".eos/prompts/EOSB-007.md" <<'EOF'
Identify primary and secondary users, operators, maintainers, external
stakeholders, and anti-personas. Derive important use cases and end-to-end user
journeys. Update product/personas.md, product/use-cases.md, and
product/user-journeys.md.
EOF

write_file ".eos/prompts/EOSB-008.md" <<'EOF'
Define product capabilities at an implementation-neutral level. Trace each
capability to users and goals. Avoid prematurely turning architecture choices
into capabilities. Update product/capabilities.md.
EOF

write_file ".eos/prompts/EOSB-009.md" <<'EOF'
Produce a testable product requirements baseline. Use stable requirement IDs,
normative MUST/SHOULD/MAY language where appropriate, rationale, source,
priority, and acceptance evidence. Trace requirements to capabilities and
goals. Update product/product-requirements.md.
EOF

write_file ".eos/prompts/EOSB-010.md" <<'EOF'
Extract and classify project constraints. Separate constraints from
preferences, assumptions, and architectural choices. Include technical,
operational, security, privacy, compliance, financial, schedule, portability,
interoperability, accessibility, maintainability, and team constraints where
applicable. Update product/constraints.md.
EOF

write_file ".eos/prompts/EOSB-011.md" <<'EOF'
Define the architecture-driving quality attributes as measurable scenarios.
Prioritize only those that materially shape architecture. Trace them to
requirements, constraints, and risks. Update architecture/quality-attributes.md.
EOF

write_file ".eos/prompts/EOSB-012.md" <<'EOF'
Define the system context and explicit system boundaries. Identify users,
external systems, trust boundaries, managed and unmanaged dependencies, and
data/control crossing boundaries. Update architecture/context.md and
architecture/system-boundaries.md.
EOF

write_file ".eos/prompts/EOSB-013.md" <<'EOF'
Enumerate unresolved technical and product uncertainties that materially block
architecture or implementation. Convert them into research questions with
decision relevance and required evidence. Update research/questions.md. Create
architecture explorations only where uncertainty warrants them.
EOF

write_file ".eos/prompts/EOSB-014.md" <<'EOF'
Propose an architecture derived from accepted requirements, constraints,
quality attributes, context, research, and project principles. Explain major
components, boundaries, data/control flow, deployment model, security model,
tradeoffs, and known risks. Do not present unresolved major choices as settled.
Update architecture/overview.md.
EOF

write_file ".eos/prompts/EOSB-015.md" <<'EOF'
Identify every architecture choice significant enough to require a durable ADR.
Create numbered ADR files for decisions that are ready. For unresolved choices,
create architecture explorations instead of fabricating decisions. Update the
ADR index.
EOF

write_file ".eos/prompts/EOSB-016.md" <<'EOF'
Define the minimum specification baseline required for the first implementation
increment. Identify required functional, technical, interface, data, security,
and operations specifications. Establish traceability from requirements and
ADRs. Update specifications/baseline.md and create the concrete specifications
needed for PI-001.
EOF

write_file ".eos/prompts/EOSB-017.md" <<'EOF'
Define PI-001 as the smallest coherent program increment that produces a
meaningful, verifiable project outcome from the accepted specification
baseline. Identify scope, exclusions, governing artifacts, risks, entry
criteria, exit criteria, and intended work cycles. Update
engineering/increments/PI-001.md.
EOF

write_file ".eos/prompts/EOSB-018.md" <<'EOF'
Define WC-0001 from PI-001. Keep it bounded and reviewable. Identify objective,
included work packets, dependencies, entry criteria, exit criteria, validation,
and review expectations. Update engineering/work-cycles/WC-0001.md.
EOF

write_file ".eos/prompts/EOSB-019.md" <<'EOF'
Define WP-0001 as the smallest independently governable implementation unit
that advances WC-0001. Specify exact scope, exclusions, dependencies,
deliverables, acceptance criteria, validation, risks, and governing artifacts.
It must be executable by Codex without requiring Codex to invent product or
architecture policy. Update engineering/work-packets/WP-0001.md.
EOF

write_file ".eos/prompts/EOSB-020.md" <<'EOF'
Perform a formal implementation-readiness review for PI-001 / WC-0001 /
WP-0001. Verify product, architecture, specification, traceability, risk,
acceptance, and validation sufficiency. Identify blocking and non-blocking
findings. Recommend AUTHORIZED, AUTHORIZED WITH CONDITIONS, or NOT AUTHORIZED.
Only the human grants final implementation authorization. Update
engineering/reviews/PI-001-READINESS-REVIEW.md.
EOF

# ------------------------------------------------------------------------------
# EOS CLI
# ------------------------------------------------------------------------------

write_file "scripts/eos" <<'EOS_SCRIPT'
#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

WORKFLOW=".eos/workflow.tsv"
REGISTRY=".eos/artifacts.tsv"
CHANGELOG=".eos/artifact-changelog.tsv"

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
warn() { printf 'WARNING: %s\n' "$*" >&2; }
now_iso() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

usage() {
  cat <<'EOF'
Engineering Operating System

Usage:
  ./scripts/eos status
  ./scripts/eos next
  ./scripts/eos prompt <EOSB-NNN>
  ./scripts/eos complete <EOSB-NNN>
  ./scripts/eos reopen <EOSB-NNN>
  ./scripts/eos version <artifact.md> <patch|minor|major> <message>
  ./scripts/eos history <artifact.md>
  ./scripts/eos rollback <artifact.md> <version> <message>
  ./scripts/eos checkpoint <message>
  ./scripts/eos verify
  ./scripts/eos responsibilities
EOF
}

frontmatter_value() {
  local file="$1"
  local key="$2"
  awk -F': ' -v k="$key" '
    NR <= 40 && $1 == k {
      v=$2
      gsub(/^"/, "", v)
      gsub(/"$/, "", v)
      print v
      exit
    }
  ' "$file"
}

replace_frontmatter_value() {
  local file="$1"
  local key="$2"
  local value="$3"
  local tmp
  tmp="$(mktemp)"
  awk -v k="$key" -v v="$value" '
    BEGIN { changed=0 }
    NR <= 40 && index($0, k ":") == 1 && changed == 0 {
      print k ": \"" v "\""
      changed=1
      next
    }
    { print }
  ' "$file" >"$tmp"
  mv "$tmp" "$file"
}

bump_version() {
  local current="$1"
  local kind="$2"
  local major minor patch
  IFS='.' read -r major minor patch <<<"$current"
  [[ "$major" =~ ^[0-9]+$ && "$minor" =~ ^[0-9]+$ && "$patch" =~ ^[0-9]+$ ]] \
    || die "Invalid semantic version: $current"

  case "$kind" in
    patch) patch=$((patch + 1)) ;;
    minor) minor=$((minor + 1)); patch=0 ;;
    major) major=$((major + 1)); minor=0; patch=0 ;;
    *) die "Version type must be patch, minor, or major" ;;
  esac

  printf '%s.%s.%s\n' "$major" "$minor" "$patch"
}

artifact_id_for() {
  local path="$1"
  local id
  id="$(frontmatter_value "$path" artifact_id || true)"
  if [[ -z "$id" && -f "$REGISTRY" ]]; then
    id="$(awk -F'\t' -v p="$path" 'NR > 1 && $2 == p {print $1; exit}' "$REGISTRY")"
  fi
  printf '%s\n' "${id:-UNREGISTERED}"
}

snapshot_path_for() {
  local path="$1"
  local version="$2"
  local noext="${path%.*}"
  local ext="${path##*.}"
  printf '.eos/history/%s/v%s.%s\n' "$noext" "$version" "$ext"
}

cmd_status() {
  printf '\nEOS WORKFLOW\n'
  printf '%-8s %-12s %-16s %-10s %s\n' "ORDER" "STAGE" "PHASE" "STATUS" "OUTPUT"
  awk -F'\t' 'NR > 1 {
    printf "%-8s %-12s %-16s %-10s %s\n", $1, $2, $3, $8, $4
  }' "$WORKFLOW"

  printf '\nNEXT\n'
  awk -F'\t' 'NR > 1 && $8 != "COMPLETE" {
    printf "%s — %s — %s\n", $2, $3, $4
    exit
  }' "$WORKFLOW"

  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf '\nGIT\n'
    git status --short
    [[ -n "$(git status --short)" ]] || printf 'clean\n'
  fi
}

cmd_next() {
  local row
  row="$(awk -F'\t' 'NR > 1 && $8 != "COMPLETE" {print; exit}' "$WORKFLOW")"
  if [[ -z "$row" ]]; then
    printf 'All EOS bootstrap stages are complete.\n'
    return
  fi

  IFS=$'\t' read -r order stage phase output lead reviewer gate status completed <<<"$row"
  cat <<EOF
Stage:      $stage
Order:      $order
Phase:      $phase
Output:     $output
Lead:       $lead
Reviewer:   $reviewer
Gate:       $gate
Status:     $status

Render the stage prompt with:

  ./scripts/eos prompt $stage
EOF
}

cmd_prompt() {
  local stage="${1:-}"
  [[ -n "$stage" ]] || die "prompt requires a stage such as EOSB-001"

  local prompt=".eos/prompts/${stage}.md"
  [[ -f "$prompt" ]] || die "No prompt registered for $stage"

  local row
  row="$(awk -F'\t' -v s="$stage" 'NR > 1 && $2 == s {print; exit}' "$WORKFLOW")"
  [[ -n "$row" ]] || die "Stage not found: $stage"

  IFS=$'\t' read -r order _ phase output lead reviewer gate status completed <<<"$row"

  cat <<EOF
# Engineering Operating System Task — $stage

You are operating inside a governed software-engineering repository.

## Responsibility Model

- Human: final authority and gate approval.
- ChatGPT: reasoning, synthesis, artifact drafting, consistency, traceability,
  architecture and planning review.
- Codex: bounded repository-local implementation and validation only after
  authorization.
- GitHub: canonical remote history, PR review, CI, issues, milestones, and
  integration record.

## Current Stage

- Phase: $phase
- Primary output: $output
- Lead: $lead
- Reviewer: $reviewer
- Gate: $gate
- Current status: $status

## Stage Instruction

EOF
  cat "$prompt"

  cat <<'EOF'

## Governing Rules

1. Read idea.md first.
2. Respect accepted higher-authority artifacts.
3. Surface contradictions instead of silently choosing one side.
4. Do not invent implementation decisions unless the stage explicitly requires
   them.
5. Preserve stable identifiers.
6. Update the designated artifacts completely, not as empty stubs.
7. Preserve traceability to source goals, requirements, constraints, ADRs, and
   specifications.
8. Mark unresolved uncertainty explicitly.
9. Recommend decisions; do not impersonate human approval.
10. When an accepted governed artifact materially changes, use the EOS
    versioning mechanism and record why.

## Primary Inception Source

EOF
  cat idea.md
}

update_stage_status() {
  local stage="$1"
  local new_status="$2"
  local completed_at="$3"
  local tmp
  tmp="$(mktemp)"
  awk -F'\t' -v OFS='\t' -v s="$stage" -v st="$new_status" -v ts="$completed_at" '
    NR == 1 { print; next }
    $2 == s { $8=st; $9=ts; found=1 }
    { print }
    END { if (!found) exit 42 }
  ' "$WORKFLOW" >"$tmp" || {
    rm -f "$tmp"
    die "Stage not found: $stage"
  }
  mv "$tmp" "$WORKFLOW"
}

cmd_complete() {
  local stage="${1:-}"
  [[ -n "$stage" ]] || die "complete requires a stage"
  update_stage_status "$stage" "COMPLETE" "$(now_iso)"
  printf 'Marked %s COMPLETE.\n' "$stage"
  printf 'Consider checkpointing the resulting coherent state:\n'
  printf '  ./scripts/eos checkpoint "complete %s"\n' "$stage"
}

cmd_reopen() {
  local stage="${1:-}"
  [[ -n "$stage" ]] || die "reopen requires a stage"
  update_stage_status "$stage" "PENDING" "-"
  printf 'Reopened %s.\n' "$stage"
}

cmd_version() {
  local path="${1:-}"
  local kind="${2:-}"
  shift 2 || true
  local message="${*:-}"

  [[ -n "$path" && -f "$path" ]] || die "Artifact file not found: $path"
  [[ -n "$kind" ]] || die "Specify patch, minor, or major"
  [[ -n "$message" ]] || die "A change message is required"

  local current id next snapshot ts
  current="$(frontmatter_value "$path" version)"
  [[ -n "$current" ]] || die "$path has no governed artifact version"
  id="$(artifact_id_for "$path")"
  next="$(bump_version "$current" "$kind")"
  snapshot="$(snapshot_path_for "$path" "$current")"
  ts="$(now_iso)"

  if [[ ! -e "$snapshot" ]]; then
    mkdir -p "$(dirname "$snapshot")"
    cp "$path" "$snapshot"
  fi

  replace_frontmatter_value "$path" version "$next"
  replace_frontmatter_value "$path" updated "${ts%%T*}"

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$ts" "$id" "$path" "$current" "$next" "$kind" "$message" >>"$CHANGELOG"

  printf '%s: %s -> %s (%s)\n' "$path" "$current" "$next" "$message"
}

cmd_history() {
  local path="${1:-}"
  [[ -n "$path" ]] || die "history requires an artifact path"

  local id
  id="$(artifact_id_for "$path")"
  printf 'Artifact: %s\nPath: %s\n\n' "$id" "$path"

  printf 'Semantic artifact history:\n'
  awk -F'\t' -v p="$path" '
    NR > 1 && $3 == p {
      printf "  %s  %s -> %s  %-6s  %s\n", $1, $4, $5, $6, $7
    }
  ' "$CHANGELOG"

  printf '\nRetained snapshots:\n'
  local base=".eos/history/${path%.*}"
  if [[ -d "$base" ]]; then
    find "$base" -maxdepth 1 -type f -print | sort | sed 's/^/  /'
  else
    printf '  none yet\n'
  fi

  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf '\nGit history:\n'
    git log --oneline --follow -- "$path" 2>/dev/null | sed 's/^/  /' || true
  fi
}

cmd_rollback() {
  local path="${1:-}"
  local target="${2:-}"
  shift 2 || true
  local message="${*:-}"

  [[ -f "$path" ]] || die "Current artifact not found: $path"
  [[ -n "$target" ]] || die "rollback requires a target version"
  [[ -n "$message" ]] || die "rollback requires a message"

  target="${target#v}"

  local current current_snapshot target_snapshot id next ts tmp
  current="$(frontmatter_value "$path" version)"
  [[ -n "$current" ]] || die "$path is not a governed versioned artifact"

  current_snapshot="$(snapshot_path_for "$path" "$current")"
  target_snapshot="$(snapshot_path_for "$path" "$target")"
  [[ -f "$target_snapshot" ]] || die "No retained snapshot for version $target"

  mkdir -p "$(dirname "$current_snapshot")"
  [[ -e "$current_snapshot" ]] || cp "$path" "$current_snapshot"

  next="$(bump_version "$current" patch)"
  id="$(artifact_id_for "$path")"
  ts="$(now_iso)"
  tmp="$(mktemp)"
  cp "$target_snapshot" "$tmp"
  mv "$tmp" "$path"

  replace_frontmatter_value "$path" version "$next"
  replace_frontmatter_value "$path" updated "${ts%%T*}"

  printf '%s\t%s\t%s\t%s\t%s\trollback\tRESTORE v%s: %s\n' \
    "$ts" "$id" "$path" "$current" "$next" "$target" "$message" >>"$CHANGELOG"

  printf 'Restored %s content from v%s as new version v%s.\n' "$path" "$target" "$next"
}

cmd_checkpoint() {
  local message="${*:-}"
  [[ -n "$message" ]] || die "checkpoint requires a message"
  command -v git >/dev/null 2>&1 || die "git is required for checkpoints"
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "Not inside a Git repository"

  local ts tag meta
  ts="$(date -u +"%Y%m%dT%H%M%SZ")"
  tag="eos/checkpoint-$ts"
  meta=".eos/checkpoints/$ts.txt"

  mkdir -p .eos/checkpoints
  {
    printf 'timestamp=%s\n' "$(now_iso)"
    printf 'message=%s\n' "$message"
  } >"$meta"

  git add -A

  if git diff --cached --quiet; then
    warn "No changes to commit; creating no checkpoint."
    rm -f "$meta"
    return
  fi

  git commit -m "checkpoint: $message"
  git tag -a "$tag" -m "$message"
  printf 'Created checkpoint %s at %s\n' "$tag" "$(git rev-parse --short HEAD)"
}

cmd_verify() {
  local failures=0

  [[ -f idea.md ]] || { printf 'FAIL missing idea.md\n'; failures=$((failures+1)); }
  [[ -f "$WORKFLOW" ]] || { printf 'FAIL missing %s\n' "$WORKFLOW"; failures=$((failures+1)); }
  [[ -f "$REGISTRY" ]] || { printf 'FAIL missing %s\n' "$REGISTRY"; failures=$((failures+1)); }

  printf 'Checking registered artifacts...\n'
  while IFS=$'\t' read -r id path type authority; do
    [[ "$id" == "artifact_id" ]] && continue
    if [[ ! -f "$path" ]]; then
      printf 'FAIL %-24s missing %s\n' "$id" "$path"
      failures=$((failures+1))
      continue
    fi

    local fm_id
    fm_id="$(frontmatter_value "$path" artifact_id || true)"
    if [[ -n "$fm_id" && "$fm_id" != "$id" ]]; then
      printf 'FAIL %-24s frontmatter id is %s in %s\n' "$id" "$fm_id" "$path"
      failures=$((failures+1))
    else
      printf 'OK   %-24s %s\n' "$id" "$path"
    fi
  done <"$REGISTRY"

  printf '\nChecking duplicate artifact IDs...\n'
  local dupes
  dupes="$(tail -n +2 "$REGISTRY" | cut -f1 | sort | uniq -d)"
  if [[ -n "$dupes" ]]; then
    printf 'FAIL duplicate artifact IDs:\n%s\n' "$dupes"
    failures=$((failures+1))
  else
    printf 'OK   no duplicate registered artifact IDs\n'
  fi

  printf '\nChecking workflow stage uniqueness...\n'
  dupes="$(tail -n +2 "$WORKFLOW" | cut -f2 | sort | uniq -d)"
  if [[ -n "$dupes" ]]; then
    printf 'FAIL duplicate workflow stages:\n%s\n' "$dupes"
    failures=$((failures+1))
  else
    printf 'OK   workflow stage IDs unique\n'
  fi

  if (( failures > 0 )); then
    printf '\nVerification FAILED with %d issue(s).\n' "$failures"
    exit 1
  fi

  printf '\nVerification PASSED.\n'
}

cmd_responsibilities() {
  cat governance/responsibility-model.md
}

cmd="${1:-}"
shift || true

case "$cmd" in
  status) cmd_status "$@" ;;
  next) cmd_next "$@" ;;
  prompt) cmd_prompt "$@" ;;
  complete) cmd_complete "$@" ;;
  reopen) cmd_reopen "$@" ;;
  version) cmd_version "$@" ;;
  history) cmd_history "$@" ;;
  rollback) cmd_rollback "$@" ;;
  checkpoint) cmd_checkpoint "$@" ;;
  verify) cmd_verify "$@" ;;
  responsibilities) cmd_responsibilities "$@" ;;
  -h|--help|help|"") usage ;;
  *) die "Unknown command: $cmd" ;;
esac
EOS_SCRIPT

chmod +x scripts/eos

# ------------------------------------------------------------------------------
# GitHub
# ------------------------------------------------------------------------------

write_file ".github/PULL_REQUEST_TEMPLATE.md" <<'EOF'
## Summary

Describe the change and why it exists.

## Governing Work

- PI:
- Work Cycle:
- Work Packet:
- Requirements:
- Specifications:
- ADRs:

## Scope

### In Scope

- TBD

### Out of Scope

- TBD

## Validation

- [ ] Acceptance criteria satisfied
- [ ] Tests pass
- [ ] Static analysis passes
- [ ] EOS integrity verification passes
- [ ] Documentation synchronized
- [ ] No unauthorized architecture changes introduced

## Risk

Describe remaining risk.

## Evidence

Record commands, test results, screenshots, benchmarks, or other completion
evidence.
EOF

write_file ".github/ISSUE_TEMPLATE/config.yml" <<'EOF'
blank_issues_enabled: true
EOF

write_file ".github/ISSUE_TEMPLATE/work-packet.yml" <<'EOF'
name: Work Packet
description: Track a governed implementation work packet
title: "WP: "
labels:
  - work-packet
body:
  - type: input
    id: artifact
    attributes:
      label: Work Packet Artifact
      placeholder: engineering/work-packets/WP-0001.md
    validations:
      required: true

  - type: textarea
    id: objective
    attributes:
      label: Objective
    validations:
      required: true

  - type: textarea
    id: scope
    attributes:
      label: Scope
    validations:
      required: true

  - type: textarea
    id: acceptance
    attributes:
      label: Acceptance Criteria
    validations:
      required: true

  - type: textarea
    id: traceability
    attributes:
      label: Governing Requirements / Specifications / ADRs
    validations:
      required: true
EOF

write_file ".github/workflows/eos-integrity.yml" <<'EOF'
name: EOS Integrity

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Verify Engineering Operating System
        run: ./scripts/eos verify
EOF

# ------------------------------------------------------------------------------
# Git initialization
# ------------------------------------------------------------------------------

if (( NO_GIT == 0 )); then
  if command -v git >/dev/null 2>&1; then
    if [[ ! -d .git ]]; then
      if git init -b main >/dev/null 2>&1; then
        :
      else
        git init >/dev/null
        git branch -m main >/dev/null 2>&1 || true
      fi
      NEW_GIT_REPO=1
      log "Initialized Git repository on main"
    else
      log "Existing Git repository detected"
    fi

    # Local repo-specific defaults only.
    git config core.autocrlf false

    # Seed an initial snapshot of all governed artifacts so v0.1.0 is directly
    # inspectable even before the first semantic version bump.
    while IFS=$'\t' read -r id path type authority; do
      [[ "$id" == "artifact_id" ]] && continue
      [[ -f "$path" ]] || continue
      version="$(awk -F': ' 'NR <= 40 && $1 == "version" {gsub(/"/,"",$2); print $2; exit}' "$path")"
      [[ -n "$version" ]] || continue
      noext="${path%.*}"
      ext="${path##*.}"
      snap=".eos/history/$noext/v$version.$ext"
      if [[ ! -e "$snap" ]]; then
        mkdir -p "$(dirname "$snap")"
        cp "$path" "$snap"
      fi
    done <.eos/artifacts.tsv

    log "Seeded initial governed-artifact snapshots"

    # For a brand-new repository only, create the initial immutable Git
    # baseline when the user's Git identity is already configured. Never sweep
    # unrelated changes into an automatic commit in an existing repository.
    if (( NEW_GIT_REPO == 1 )); then
      if [[ -n "$(git config user.name || true)" && -n "$(git config user.email || true)" ]]; then
        git add -A
        git commit -m "chore: bootstrap engineering operating system" >/dev/null
        git tag -a eos/bootstrap-v0.1.0 -m "Initial Engineering Operating System"
        log "Created initial Git commit and eos/bootstrap-v0.1.0 tag"
      else
        warn "Git user.name/user.email are not configured; initial files are not committed yet."
        warn "Configure your Git identity, then run the recommended first-commit commands below."
      fi
    fi
  else
    warn "git is not installed; files were created but repository versioning is not active"
  fi
fi

# ------------------------------------------------------------------------------
# Final verification
# ------------------------------------------------------------------------------

./scripts/eos verify

cat <<EOF

===============================================================================
Engineering Operating System bootstrap complete
===============================================================================

Project: $PROJECT_NAME
Root:    $PROJECT_ROOT

Versioning model
----------------
1. Git versions EVERY tracked file.
2. Governed artifacts carry semantic versions.
3. Previous governed artifact versions are retained under .eos/history/.
4. Rollback restores historical content as a new version.
5. EOS checkpoints create a commit + annotated Git tag.

Start the project-definition workflow
-------------------------------------
  ./scripts/eos status
  ./scripts/eos next
  ./scripts/eos prompt EOSB-001

After completing/reviewing a stage
----------------------------------
  ./scripts/eos version engineering/reviews/INCEPTION-REVIEW.md minor \
    "Complete initial inception review"
  ./scripts/eos complete EOSB-001
  ./scripts/eos checkpoint "complete EOSB-001 inception review"

Inspect / restore history
-------------------------
  ./scripts/eos history vision/product-vision.md
  ./scripts/eos rollback vision/product-vision.md 0.1.0 \
    "Restore earlier product vision after rejected revision"

Recommended first commit if this is a new repository
----------------------------------------------------
  git add -A
  git commit -m "chore: bootstrap engineering operating system"
  git tag -a eos/bootstrap-v0.1.0 -m "Initial Engineering Operating System"

Then begin with EOSB-001.
===============================================================================
EOF

# ==============================================================================
# FULL-LIFECYCLE EOS EXTENSION
# ==============================================================================
# EOSB remains the project bootstrap sequence. The following permanent operating
# layers remain active for the lifetime of the repository:
#   EOSB — Bootstrap
#   EOSP — Planning
#   EOSE — Execution
#   EOSV — Verification
#   EOSR — Review
#   EOSC — Change Control
#   EOSL — Release Lifecycle
#   EOSM — Maintenance
# ==============================================================================

log "Extending bootstrap into the permanent full-lifecycle EOS"

for directory in \
  engineering/lifecycle \
  engineering/changes \
  engineering/releases \
  engineering/maintenance \
  tools/eos \
  .eos/contracts \
  .eos/evidence \
  .eos/decisions \
  .eos/sync; do
  create_dir "$directory"
done

if [[ ! -e ".eos/VERSION" ]]; then
  printf '1.0.0\n' > .eos/VERSION
fi

write_artifact "engineering/lifecycle/README.md" "EOS-LIFECYCLE-0001" "Engineering Operating System Lifecycle" "governance" "governance-authoritative" <<'EOF'
# Engineering Operating System Lifecycle

EOSB is the bootstrap layer, not the entire system.

After EOSB-020, the Engineering Operating System remains active for the lifetime
of the project through eight permanent, interlocking operating layers:

1. **EOSB — Bootstrap**
2. **EOSP — Planning**
3. **EOSE — Execution**
4. **EOSV — Verification**
5. **EOSR — Review**
6. **EOSC — Change Control**
7. **EOSL — Release Lifecycle**
8. **EOSM — Maintenance**

These layers are not a rigid waterfall. Work can move between them when evidence
requires replanning, controlled change, renewed verification, or maintenance.

## Normal Delivery Loop

`EOSP -> EOSE -> EOSV -> EOSR`

Successful review can close a WP/WC/PI or feed the next planning cycle.

## Controlled Evolution Loop

`EOSE/EOSV/EOSR -> EOSC -> EOSP/EOSE -> EOSV -> EOSR`

A discovered contradiction or required requirement/architecture/specification
change is governed rather than silently absorbed into implementation.

## Delivery / Operations Loop

`EOSR -> EOSL -> EOSM -> EOSC/EOSP as needed`
EOF

write_artifact "engineering/lifecycle/EOSB-bootstrap.md" "EOSB" "EOSB Bootstrap" "lifecycle-layer" "governance-authoritative" <<'EOF'
# EOSB — Bootstrap

## Purpose

Transform a developed `idea.md` into a governed, implementation-ready
engineering program.

## Entry

- project idea exists;
- repository is initialized.

## Responsibilities

- inception analysis;
- terminology;
- vision;
- users/capabilities/requirements;
- constraints and quality attributes;
- context/boundaries;
- research and ADR baseline;
- specification baseline;
- PI-001 / WC-0001 / WP-0001;
- implementation-readiness review.

## Exit

EOSB-020 is complete and the human has made the implementation gate decision.
EOSB then becomes historical bootstrap state; the permanent lifecycle continues.
EOF

write_artifact "engineering/lifecycle/EOSP-planning.md" "EOSP" "EOSP Planning" "lifecycle-layer" "governance-authoritative" <<'EOF'
# EOSP — Planning

## Purpose

Convert accepted product, architecture, and specification intent into bounded,
traceable execution units.

## Managed Objects

- milestones;
- program increments;
- work cycles;
- work packets;
- dependencies;
- risks;
- sequencing;
- readiness gates.

## Primary Commands

```bash
./scripts/eos plan PI-002
./scripts/eos create-wc --pi PI-002
./scripts/eos create-wp --wc WC-0002 --domain CORE
./scripts/eos authorize PI-002
./scripts/eos authorize WC-0002
./scripts/eos authorize WP-CORE-0001
```
EOF

write_artifact "engineering/lifecycle/EOSE-execution.md" "EOSE" "EOSE Execution" "lifecycle-layer" "governance-authoritative" <<'EOF'
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
EOF

write_artifact "engineering/lifecycle/EOSV-verification.md" "EOSV" "EOSV Verification" "lifecycle-layer" "governance-authoritative" <<'EOF'
# EOSV — Verification

## Purpose

Produce reproducible evidence that work satisfies governing requirements,
specifications, quality attributes, and acceptance criteria.

## Evidence Sources

- EOS integrity checks;
- repository build/test/lint/type/security commands;
- work-packet-specific validation;
- CI results;
- automated traceability;
- benchmarks and operational evidence when required.

## Primary Commands

```bash
./scripts/eos validate WP-CORE-0001
./scripts/eos verify
./scripts/eos trace REQ-0042
```

Repository validation commands are configured in `.eos/validation.commands`.
EOF

write_artifact "engineering/lifecycle/EOSR-review.md" "EOSR" "EOSR Review" "lifecycle-layer" "governance-authoritative" <<'EOF'
# EOSR — Review

## Purpose

Determine whether work conforms to its governing intent and whether it may
advance, close, release, or must return to planning/change control.

## Review Levels

- work packet;
- work cycle;
- program increment;
- architecture/change;
- release readiness;
- maintenance closure.

## Primary Commands

```bash
./scripts/eos review WP-CORE-0001
./scripts/eos close WP-CORE-0001
./scripts/eos close-cycle WC-0003
./scripts/eos close-pi PI-002
```

Deterministic checks are automated. Human authority is retained for final gates
that require risk acceptance or material tradeoffs.
EOF

write_artifact "engineering/lifecycle/EOSC-change-control.md" "EOSC" "EOSC Change Control" "lifecycle-layer" "governance-authoritative" <<'EOF'
# EOSC — Change Control

## Purpose

Allow requirements, architecture, specifications, plans, and scope to evolve
without silently rewriting history or invalidating downstream work.

## Flow

`discovery -> impact analysis -> change request -> review -> approval ->
versioned artifact updates -> dependent replanning/reverification -> closure`

## Primary Commands

```bash
./scripts/eos impact ADR-0014
./scripts/eos change create ADR-0014 "Revise persistence boundary"
./scripts/eos change approve CR-0001
./scripts/eos change close CR-0001
```
EOF

write_artifact "engineering/lifecycle/EOSL-release-lifecycle.md" "EOSL" "EOSL Release Lifecycle" "lifecycle-layer" "governance-authoritative" <<'EOF'
# EOSL — Release Lifecycle

## Purpose

Turn accepted engineering output into a reproducible, reviewable, traceable
release.

## Flow

`candidate -> readiness evidence -> readiness review -> version -> commit ->
annotated tag -> optional GitHub Release -> post-release evidence`

## Primary Command

```bash
./scripts/eos release 0.1.0
```

The first invocation prepares release/readiness artifacts when necessary. Final
tagging remains gated on readiness approval unless a human records an explicit
override. `--publish` performs the external GitHub publication step.
EOF

write_artifact "engineering/lifecycle/EOSM-maintenance.md" "EOSM" "EOSM Maintenance" "lifecycle-layer" "governance-authoritative" <<'EOF'
# EOSM — Maintenance

## Purpose

Govern long-lived defects, technical debt, security findings, dependencies,
operations, performance, and documentation maintenance.

## Categories

- bug;
- debt;
- security;
- dependency;
- operations;
- performance;
- documentation.

## Primary Commands

```bash
./scripts/eos maintain create debt "Refactor graph cache ownership"
./scripts/eos maintain close MNT-0001
```

Material maintenance that changes governing behavior or architecture enters
EOSC. Larger bodies of work can be promoted into EOSP.
EOF

write_artifact "engineering/lifecycle/state-machine.md" "EOS-STATE-0001" "EOS Lifecycle State Machine" "governance" "governance-authoritative" <<'EOF'
# EOS Lifecycle State Machine

## Program Increment

`DRAFT -> PLANNED -> AUTHORIZED -> ACTIVE -> IN_REVIEW -> CLOSED`

Exceptional state: `BLOCKED`.

## Work Cycle

`DRAFT -> READY -> AUTHORIZED -> ACTIVE -> IN_REVIEW -> CLOSED`

Exceptional state: `BLOCKED`.

## Work Packet

`DRAFT -> READY -> AUTHORIZED -> IN_PROGRESS -> VERIFYING -> IN_REVIEW -> CLOSED`

Exceptional state: `BLOCKED`.

## Change Request

`DRAFT -> PROPOSED -> APPROVED -> APPLIED -> CLOSED`

Alternative terminal state: `REJECTED`.

## Maintenance Item

`OPEN -> PLANNED -> IN_PROGRESS -> VERIFYING -> CLOSED`

Alternative state: `DEFERRED`.

## Release

`PROPOSED -> READY -> RELEASED`

Alternative terminal state: `WITHDRAWN`.

## Gate Principle

Transitions implying authorization, acceptance, closure, release, or risk
acceptance leave durable evidence and a decision record.
EOF

write_artifact "governance/github-integration.md" "GOV-GITHUB-0001" "GitHub Integration Model" "governance" "governance-authoritative" <<'EOF'
# GitHub Integration Model

Git remains the authoritative version history. GitHub is the canonical remote
collaboration and integration surface when configured.

## Mapping

| EOS object | GitHub object |
|---|---|
| Program Increment | tracking issue / milestone |
| Work Cycle | tracking issue |
| Work Packet | issue + branch + pull request |
| Change Request | issue / pull request |
| Verification | GitHub Actions checks + evidence artifacts |
| Review | pull-request review + repository review artifact |
| Release | Git tag + GitHub Release |
| Maintenance | issue + WP/change request when required |

## Synchronization

`./scripts/eos github-sync` is dry-run by default.

`./scripts/eos github-sync --apply` may create/reconcile EOS labels and tracking
issues using the authenticated GitHub CLI. External writes are explicit and are
never side effects of local status, trace, review, or verification commands.
EOF

# ------------------------------------------------------------------------------
# Permanent lifecycle registries
# ------------------------------------------------------------------------------

if [[ ! -e .eos/layers.tsv ]]; then
  cat > .eos/layers.tsv <<'EOF'
code	name	purpose
EOSB	Bootstrap	Transform idea.md into an implementation-ready governed engineering baseline.
EOSP	Planning	Define and authorize program increments, work cycles, work packets, dependencies, risks, and sequencing.
EOSE	Execution	Execute bounded authorized work through repository-local implementation contracts.
EOSV	Verification	Produce reproducible evidence through tests, CI, quality gates, traceability, and validation.
EOSR	Review	Assess conformance, findings, acceptance, closure, and readiness at WP/WC/PI/change/release levels.
EOSC	Change Control	Govern requirement, architecture, specification, scope, and plan changes with impact analysis and retained history.
EOSL	Release Lifecycle	Prepare, review, version, tag, publish, and validate releases.
EOSM	Maintenance	Govern defects, debt, dependencies, security, operations, performance, and long-lived maintenance.
EOF
fi

if [[ ! -e .eos/program-increments.tsv ]]; then
  cat > .eos/program-increments.tsv <<EOF
id	path	title	status	created	updated	github_url
PI-001	engineering/increments/PI-001.md	Program Increment 001	DRAFT	${CURRENT_DATE}T00:00:00Z	${CURRENT_DATE}T00:00:00Z	
EOF
fi

if [[ ! -e .eos/work-cycles.tsv ]]; then
  cat > .eos/work-cycles.tsv <<EOF
id	path	title	status	pi	created	updated	github_url
WC-0001	engineering/work-cycles/WC-0001.md	Work Cycle 0001	DRAFT	PI-001	${CURRENT_DATE}T00:00:00Z	${CURRENT_DATE}T00:00:00Z	
EOF
fi

if [[ ! -e .eos/work-packets.tsv ]]; then
  cat > .eos/work-packets.tsv <<EOF
id	path	title	status	pi	wc	domain	created	updated	github_url
WP-0001	engineering/work-packets/WP-0001.md	First Work Packet	DRAFT	PI-001	WC-0001		${CURRENT_DATE}T00:00:00Z	${CURRENT_DATE}T00:00:00Z	
EOF
fi

[[ -e .eos/change-requests.tsv ]] || printf 'id\tpath\ttarget\tsummary\tstatus\tcreated\tupdated\tgithub_url\n' > .eos/change-requests.tsv
[[ -e .eos/maintenance.tsv ]] || printf 'id\tpath\ttype\tsummary\tstatus\tcreated\tupdated\tgithub_url\n' > .eos/maintenance.tsv
[[ -e .eos/releases.tsv ]] || printf 'id\tpath\tversion\tstatus\tcreated\tupdated\tgithub_url\n' > .eos/releases.tsv
[[ -e .eos/decisions.tsv ]] || printf 'timestamp\ttarget\taction\toutcome\tactor\treason\n' > .eos/decisions.tsv
[[ -e .eos/trace-edges.tsv ]] || printf 'source_id\ttarget_id\tsource_path\n' > .eos/trace-edges.tsv

if [[ ! -e .eos/validation.commands ]]; then
  cat > .eos/validation.commands <<'EOF'
# One repository-local validation command per line.
# Add these only after the implementation toolchain is selected.
#
# Examples:
# bun test
# bun run lint
# cargo test --workspace
# go test ./...
EOF
fi

# Add permanent lifecycle artifacts to the governed registry without duplicating
# entries on a re-run.
append_artifact_registry() {
  local id="$1" path="$2" type="$3" authority="$4"
  grep -qE "^${id}[[:space:]]" .eos/artifacts.tsv 2>/dev/null && return 0
  printf '%s\t%s\t%s\t%s\n' "$id" "$path" "$type" "$authority" >> .eos/artifacts.tsv
}

append_artifact_registry EOS-LIFECYCLE-0001 engineering/lifecycle/README.md governance governance-authoritative
append_artifact_registry EOSB engineering/lifecycle/EOSB-bootstrap.md lifecycle-layer governance-authoritative
append_artifact_registry EOSP engineering/lifecycle/EOSP-planning.md lifecycle-layer governance-authoritative
append_artifact_registry EOSE engineering/lifecycle/EOSE-execution.md lifecycle-layer governance-authoritative
append_artifact_registry EOSV engineering/lifecycle/EOSV-verification.md lifecycle-layer governance-authoritative
append_artifact_registry EOSR engineering/lifecycle/EOSR-review.md lifecycle-layer governance-authoritative
append_artifact_registry EOSC engineering/lifecycle/EOSC-change-control.md lifecycle-layer governance-authoritative
append_artifact_registry EOSL engineering/lifecycle/EOSL-release-lifecycle.md lifecycle-layer governance-authoritative
append_artifact_registry EOSM engineering/lifecycle/EOSM-maintenance.md lifecycle-layer governance-authoritative
append_artifact_registry EOS-STATE-0001 engineering/lifecycle/state-machine.md governance governance-authoritative
append_artifact_registry GOV-GITHUB-0001 governance/github-integration.md governance governance-authoritative

# Extend .eos/README.md once.
if ! grep -q 'program-increments.tsv' .eos/README.md 2>/dev/null; then
  cat >> .eos/README.md <<'EOF'

## Permanent Lifecycle State

- `layers.tsv` — EOSB/EOSP/EOSE/EOSV/EOSR/EOSC/EOSL/EOSM;
- `program-increments.tsv` — PI state;
- `work-cycles.tsv` — WC state;
- `work-packets.tsv` — WP state;
- `change-requests.tsv` — EOSC state;
- `maintenance.tsv` — EOSM state;
- `releases.tsv` — EOSL state;
- `decisions.tsv` — gate/closure decision log;
- `trace-edges.tsv` — generated traceability graph;
- `contracts/` — Codex and ChatGPT review contracts;
- `evidence/` — verification/review evidence;
- `sync/` — GitHub sync records.
EOF
fi

# Extend the root README once.
if ! grep -q '## Permanent EOS Operating Layers' README.md 2>/dev/null; then
  cat >> README.md <<'EOF'

## Permanent EOS Operating Layers

EOSB is only project bootstrap. The Engineering Operating System remains active
throughout the project lifecycle:

- **EOSB — Bootstrap**
- **EOSP — Planning**
- **EOSE — Execution**
- **EOSV — Verification**
- **EOSR — Review**
- **EOSC — Change Control**
- **EOSL — Release Lifecycle**
- **EOSM — Maintenance**

Common permanent-lifecycle commands:

```bash
./scripts/eos plan PI-002
./scripts/eos create-wc --pi PI-002
./scripts/eos create-wp --wc WC-0002 --domain CORE
./scripts/eos authorize WP-CORE-0001
./scripts/eos start WP-CORE-0001
./scripts/eos codex WP-CORE-0001
./scripts/eos validate WP-CORE-0001
./scripts/eos review WP-CORE-0001
./scripts/eos close WP-CORE-0001
./scripts/eos close-cycle WC-0002
./scripts/eos close-pi PI-002
./scripts/eos trace REQ-0042
./scripts/eos impact ADR-0014
./scripts/eos github-sync
./scripts/eos release 0.1.0
```
EOF
fi

# ------------------------------------------------------------------------------
# Full-lifecycle EOS command engine
# ------------------------------------------------------------------------------

write_file "tools/eos/README.md" <<'EOF'
# EOS Control Tooling

`tools/eos/eos.py` implements the permanent Engineering Operating System control
plane using only the Python standard library.

This is a repository tooling choice. It does **not** choose or constrain the
product implementation language, runtime, architecture, or deployment model.

The stable user interface is always:

```bash
./scripts/eos ...
```
EOF

# Preserve an earlier generated bootstrap-only CLI before upgrading it. A custom
# user-owned scripts/eos is never overwritten silently.
EOS_CLI_CAN_UPGRADE=0
if [[ ! -e scripts/eos ]]; then
  EOS_CLI_CAN_UPGRADE=1
elif grep -q 'Engineering Operating System' scripts/eos 2>/dev/null; then
  EOS_CLI_CAN_UPGRADE=1
  mkdir -p .eos/history/tooling
  cp scripts/eos .eos/history/tooling/scripts-eos-bootstrap-only.sh
fi

if (( EOS_CLI_CAN_UPGRADE == 1 )); then
  cat > scripts/eos <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd))"

if ! command -v python3 >/dev/null 2>&1; then
  printf 'ERROR: python3 is required by the repository-local EOS control tooling.\n' >&2
  exit 127
fi

exec python3 "$ROOT/tools/eos/eos.py" "$@"
EOF
  chmod +x scripts/eos
else
  warn "Custom scripts/eos detected; preserving it. Full lifecycle engine is available at tools/eos/eos.py."
fi

cat > tools/eos/eos.py <<'EOS_PY'
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import textwrap
from collections import deque
from pathlib import Path
from typing import Iterable

UTC = dt.timezone.utc

ID_RE = re.compile(
    r"\b(?:"
    r"REQ-[A-Z0-9][A-Z0-9-]*|"
    r"CAP-[A-Z0-9][A-Z0-9-]*|"
    r"QA-[A-Z0-9][A-Z0-9-]*|"
    r"ADR-\d{4}|"
    r"SPEC-[A-Z0-9][A-Z0-9-]*|"
    r"PI-\d{3}|"
    r"WC-\d{4}|"
    r"WP(?:-[A-Z][A-Z0-9]*)?-\d{4}|"
    r"CR-\d{4}|"
    r"MNT-\d{4}|"
    r"RISK-\d{3,4}|"
    r"REL-\d+\.\d+\.\d+"
    r")\b"
)

LAYER_ORDER = ("EOSB", "EOSP", "EOSE", "EOSV", "EOSR", "EOSC", "EOSL", "EOSM")

VALID_STATES = {
    "PI": {"DRAFT", "PLANNED", "AUTHORIZED", "ACTIVE", "IN_REVIEW", "CLOSED", "BLOCKED"},
    "WC": {"DRAFT", "READY", "AUTHORIZED", "ACTIVE", "IN_REVIEW", "CLOSED", "BLOCKED"},
    "WP": {
        "DRAFT",
        "READY",
        "AUTHORIZED",
        "IN_PROGRESS",
        "VERIFYING",
        "IN_REVIEW",
        "CLOSED",
        "BLOCKED",
    },
    "CR": {"DRAFT", "PROPOSED", "APPROVED", "APPLIED", "CLOSED", "REJECTED"},
    "MNT": {"OPEN", "PLANNED", "IN_PROGRESS", "VERIFYING", "CLOSED", "DEFERRED"},
    "REL": {"PROPOSED", "READY", "RELEASED", "WITHDRAWN"},
}

REGISTRY_FIELDS = {
    "PI": ["id", "path", "title", "status", "created", "updated", "github_url"],
    "WC": ["id", "path", "title", "status", "pi", "created", "updated", "github_url"],
    "WP": [
        "id",
        "path",
        "title",
        "status",
        "pi",
        "wc",
        "domain",
        "created",
        "updated",
        "github_url",
    ],
    "CR": ["id", "path", "target", "summary", "status", "created", "updated", "github_url"],
    "MNT": ["id", "path", "type", "summary", "status", "created", "updated", "github_url"],
    "REL": ["id", "path", "version", "status", "created", "updated", "github_url"],
}

REGISTRY_PATHS = {
    "PI": ".eos/program-increments.tsv",
    "WC": ".eos/work-cycles.tsv",
    "WP": ".eos/work-packets.tsv",
    "CR": ".eos/change-requests.tsv",
    "MNT": ".eos/maintenance.tsv",
    "REL": ".eos/releases.tsv",
}


class EosError(RuntimeError):
    pass


def now_iso() -> str:
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return dt.date.today().isoformat()


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        check=check,
        capture_output=capture,
    )


def discover_root() -> Path:
    try:
        result = run(["git", "rev-parse", "--show-toplevel"])
        return Path(result.stdout.strip()).resolve()
    except Exception:
        return Path.cwd().resolve()


ROOT = discover_root()
EOS = ROOT / ".eos"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def ensure_dirs() -> None:
    for d in (
        EOS,
        EOS / "history",
        EOS / "checkpoints",
        EOS / "prompts",
        EOS / "contracts",
        EOS / "evidence",
        EOS / "decisions",
        EOS / "sync",
        ROOT / "engineering" / "reviews",
        ROOT / "engineering" / "increments",
        ROOT / "engineering" / "work-cycles",
        ROOT / "engineering" / "work-packets",
        ROOT / "engineering" / "changes",
        ROOT / "engineering" / "releases",
        ROOT / "engineering" / "maintenance",
    ):
        d.mkdir(parents=True, exist_ok=True)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    tmp.replace(path)


def registry(kind: str) -> list[dict[str, str]]:
    kind = kind.upper()
    return read_tsv(ROOT / REGISTRY_PATHS[kind])


def save_registry(kind: str, rows: list[dict[str, str]]) -> None:
    kind = kind.upper()
    write_tsv(ROOT / REGISTRY_PATHS[kind], REGISTRY_FIELDS[kind], rows)


def find_row(kind: str, target: str) -> dict[str, str] | None:
    for row in registry(kind):
        if row["id"] == target:
            return row
    return None


def update_row(kind: str, target: str, **updates: str) -> dict[str, str]:
    rows = registry(kind)
    for row in rows:
        if row["id"] == target:
            row.update(updates)
            row["updated"] = now_iso()
            save_registry(kind, rows)
            return row
    raise EosError(f"{target} is not registered as {kind}")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, body


def write_frontmatter(path: Path, data: dict[str, str], body: str) -> None:
    ordered = (
        "artifact_id",
        "title",
        "type",
        "version",
        "status",
        "authority",
        "created",
        "updated",
    )
    lines = ["---"]
    seen = set()
    for key in ordered:
        if key in data:
            lines.append(f'{key}: "{data[key]}"')
            seen.add(key)
    for key, value in data.items():
        if key not in seen:
            lines.append(f'{key}: "{value}"')
    lines.append("---")
    path.write_text("\n".join(lines) + "\n\n" + body.lstrip("\n"), encoding="utf-8")


def set_frontmatter(path: Path, key: str, value: str) -> None:
    data, body = parse_frontmatter(path)
    if not data:
        raise EosError(f"{rel(path)} has no EOS YAML front matter")
    data[key] = value
    if key != "updated":
        data["updated"] = today()
    write_frontmatter(path, data, body)


def create_artifact(
    path: Path,
    artifact_id: str,
    title: str,
    artifact_type: str,
    authority: str,
    body: str,
    *,
    status: str = "Draft",
) -> None:
    if path.exists():
        raise EosError(f"Refusing to overwrite existing artifact: {rel(path)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "artifact_id": artifact_id,
        "title": title,
        "type": artifact_type,
        "version": "0.1.0",
        "status": status,
        "authority": authority,
        "created": today(),
        "updated": today(),
    }
    write_frontmatter(path, data, body)
    seed_snapshot(path)


def seed_snapshot(path: Path) -> None:
    data, _ = parse_frontmatter(path)
    version = data.get("version")
    if not version:
        return
    snap = snapshot_path(path, version)
    if not snap.exists():
        snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, snap)


def snapshot_path(path: Path, version: str) -> Path:
    rp = rel(path)
    p = Path(rp)
    return EOS / "history" / p.with_suffix("") / f"v{version}{p.suffix}"


def bump_semver(current: str, kind: str) -> str:
    try:
        major, minor, patch = map(int, current.split("."))
    except ValueError as exc:
        raise EosError(f"Invalid semantic version: {current}") from exc
    if kind == "patch":
        patch += 1
    elif kind == "minor":
        minor += 1
        patch = 0
    elif kind == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise EosError("Version change must be patch, minor, or major")
    return f"{major}.{minor}.{patch}"


def append_tsv(path: Path, fields: list[str], row: dict[str, str]) -> None:
    rows = read_tsv(path)
    rows.append(row)
    write_tsv(path, fields, rows)


def kind_for_id(target: str) -> str:
    if re.fullmatch(r"PI-\d{3}", target):
        return "PI"
    if re.fullmatch(r"WC-\d{4}", target):
        return "WC"
    if re.fullmatch(r"WP(?:-[A-Z][A-Z0-9]*)?-\d{4}", target):
        return "WP"
    if re.fullmatch(r"CR-\d{4}", target):
        return "CR"
    if re.fullmatch(r"MNT-\d{4}", target):
        return "MNT"
    if re.fullmatch(r"REL-\d+\.\d+\.\d+", target):
        return "REL"
    raise EosError(f"Unsupported lifecycle target: {target}")


def row_for_target(target: str) -> tuple[str, dict[str, str]]:
    kind = kind_for_id(target)
    row = find_row(kind, target)
    if row is None:
        raise EosError(f"{target} is not registered")
    return kind, row


def artifact_path_for_id(target: str) -> Path | None:
    try:
        _, row = row_for_target(target)
        return ROOT / row["path"]
    except EosError:
        pass

    artifacts = read_tsv(EOS / "artifacts.tsv")
    for row in artifacts:
        if row.get("artifact_id") == target:
            return ROOT / row.get("path", "")

    # Common filename-based fallback for ADRs/REQs/etc.
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts or ".eos/history" in path.as_posix():
            continue
        data, _ = parse_frontmatter(path) if path.suffix == ".md" else ({}, "")
        if data.get("artifact_id") == target:
            return path
        if target in path.name:
            return path
    return None


def next_number(kind: str, width: int, *, prefix: str | None = None) -> int:
    rows = registry(kind)
    nums: list[int] = []
    if kind == "WP" and prefix:
        pattern = re.compile(rf"^WP-{re.escape(prefix)}-(\d{{4}})$")
    elif kind == "WP":
        pattern = re.compile(r"^WP-(\d{4})$")
    elif kind == "PI":
        pattern = re.compile(r"^PI-(\d{3})$")
    elif kind == "WC":
        pattern = re.compile(r"^WC-(\d{4})$")
    elif kind == "CR":
        pattern = re.compile(r"^CR-(\d{4})$")
    elif kind == "MNT":
        pattern = re.compile(r"^MNT-(\d{4})$")
    else:
        raise EosError(f"Cannot allocate ID for kind {kind}")
    for row in rows:
        match = pattern.match(row["id"])
        if match:
            nums.append(int(match.group(1)))
    return max(nums, default=0) + 1


def state_line(path: Path) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("**State:**"):
            return line.split(":", 1)[1].strip()
    return None


def replace_state_line(path: Path, new_state: str) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("**State:**"):
            lines[i] = f"**State:** {new_state}"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    # No state line: insert after first heading.
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines.insert(i + 1, "")
            lines.insert(i + 2, f"**State:** {new_state}")
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return


def sync_artifact_state(path: Path, state: str) -> None:
    if not path.exists():
        return
    replace_state_line(path, state)
    data, _ = parse_frontmatter(path) if path.suffix == ".md" else ({}, "")
    if data:
        set_frontmatter(path, "status", state)


def set_lifecycle_state(target: str, state: str) -> None:
    kind, row = row_for_target(target)
    if state not in VALID_STATES[kind]:
        raise EosError(f"Invalid {kind} state: {state}")
    update_row(kind, target, status=state)
    path = ROOT / row["path"]
    sync_artifact_state(path, state)


def normalize_decision(text: str) -> str:
    return text.strip().upper().replace(" ", "_")


def review_path(target: str) -> Path:
    return ROOT / "engineering" / "reviews" / f"{target}-REVIEW.md"


def review_decision(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    patterns = (
        r"\*\*Decision:\*\*\s*([A-Za-z _-]+)",
        r"\*\*Authorization:\*\*\s*([A-Za-z _-]+)",
        r"^Decision:\s*([A-Za-z _-]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.M)
        if match:
            return normalize_decision(match.group(1))
    return ""


def is_review_accepted(path: Path) -> bool:
    decision = review_decision(path)
    return decision in {
        "ACCEPTED",
        "APPROVED",
        "AUTHORIZED",
        "AUTHORIZED_WITH_CONDITIONS",
        "ACCEPTED_WITH_FOLLOW_UP",
        "CLOSED",
        "PASS",
        "PASSED",
    }


def accepted_review_complete(path: Path) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not path.exists():
        return False, [f"missing review {rel(path)}"]
    if not is_review_accepted(path):
        reasons.append(f"review decision is not accepted: {rel(path)}")
    complete, issues = artifact_is_complete_enough(path)
    if not complete:
        reasons.extend(f"review {rel(path)}: {issue}" for issue in issues)
    return not reasons, reasons


def artifact_is_complete_enough(path: Path) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not path.exists():
        return False, [f"missing artifact {rel(path)}"]
    text = path.read_text(encoding="utf-8")
    if re.search(r"\bTBD\b", text):
        reasons.append("artifact still contains TBD markers")
    if len(text.strip()) < 300:
        reasons.append("artifact appears unusually short")
    return not reasons, reasons


def record_decision(
    target: str,
    action: str,
    outcome: str,
    actor: str,
    reason: str,
) -> None:
    fields = ["timestamp", "target", "action", "outcome", "actor", "reason"]
    append_tsv(
        EOS / "decisions.tsv",
        fields,
        {
            "timestamp": now_iso(),
            "target": target,
            "action": action,
            "outcome": outcome,
            "actor": actor,
            "reason": reason,
        },
    )


def git_available() -> bool:
    return shutil.which("git") is not None


def git_clean() -> bool:
    if not git_available():
        return False
    try:
        return not run(["git", "status", "--porcelain"], cwd=ROOT).stdout.strip()
    except Exception:
        return False


def git_status() -> str:
    if not git_available():
        return "git unavailable"
    try:
        out = run(["git", "status", "--short"], cwd=ROOT).stdout.strip()
        return out or "clean"
    except Exception as exc:
        return f"git status unavailable: {exc}"


def current_branch() -> str:
    try:
        return run(["git", "branch", "--show-current"], cwd=ROOT).stdout.strip()
    except Exception:
        return ""


def commit_sha() -> str:
    try:
        return run(["git", "rev-parse", "HEAD"], cwd=ROOT).stdout.strip()
    except Exception:
        return ""


def latest_active(kind: str) -> dict[str, str] | None:
    rows = registry(kind)
    closed = {"CLOSED", "RELEASED", "REJECTED", "WITHDRAWN"}
    for row in reversed(rows):
        if row.get("status") not in closed:
            return row
    return None


def cmd_layers(_: argparse.Namespace) -> None:
    rows = read_tsv(EOS / "layers.tsv")
    print("PERMANENT EOS OPERATING LAYERS\n")
    for row in rows:
        print(f"{row['code']} — {row['name']}")
        print(f"  {row['purpose']}")
        print()


def cmd_status(_: argparse.Namespace) -> None:
    print("ENGINEERING OPERATING SYSTEM\n")
    print("Permanent layers:")
    for row in read_tsv(EOS / "layers.tsv"):
        print(f"  {row['code']:<5} {row['name']:<20} {row['purpose']}")

    workflow = read_tsv(EOS / "workflow.tsv")
    next_stage = next((row for row in workflow if row.get("status") != "COMPLETE"), None)
    print("\nBootstrap:")
    if next_stage:
        print(
            f"  next={next_stage['stage']} phase={next_stage['phase']} "
            f"output={next_stage['primary_output']}"
        )
    else:
        print("  EOSB bootstrap complete; permanent operating lifecycle is active.")

    for kind, label in (("PI", "Program increments"), ("WC", "Work cycles"), ("WP", "Work packets")):
        print(f"\n{label}:")
        rows = registry(kind)
        if not rows:
            print("  none")
        for row in rows[-20:]:
            parent = ""
            if kind == "WC":
                parent = f" pi={row.get('pi','')}"
            elif kind == "WP":
                parent = f" wc={row.get('wc','')} pi={row.get('pi','')}"
            print(f"  {row['id']:<16} {row['status']:<12}{parent} {row['title']}")

    print("\nGit:")
    print(textwrap.indent(git_status(), "  "))


def cmd_next(_: argparse.Namespace) -> None:
    workflow = read_tsv(EOS / "workflow.tsv")
    row = next((r for r in workflow if r.get("status") != "COMPLETE"), None)
    if row:
        print(f"{row['stage']} — {row['phase']} — {row['primary_output']}")
        print(f"./scripts/eos prompt {row['stage']}")
        return

    active_wp = latest_active("WP")
    active_wc = latest_active("WC")
    active_pi = latest_active("PI")
    if active_wp and active_wp["status"] not in {"CLOSED"}:
        print(f"Permanent lifecycle: continue {active_wp['id']} ({active_wp['status']})")
        print(f"./scripts/eos codex {active_wp['id']}")
    elif active_wc and active_wc["status"] not in {"CLOSED"}:
        print(f"Permanent lifecycle: decompose {active_wc['id']} into the next work packet")
        print(f"./scripts/eos create-wp --wc {active_wc['id']}")
    elif active_pi and active_pi["status"] not in {"CLOSED"}:
        print(f"Permanent lifecycle: create/continue a work cycle for {active_pi['id']}")
        print(f"./scripts/eos create-wc --pi {active_pi['id']}")
    else:
        print("Permanent lifecycle: plan the next program increment")
        print("./scripts/eos plan")


def cmd_prompt(args: argparse.Namespace) -> None:
    prompt = EOS / "prompts" / f"{args.stage}.md"
    if not prompt.exists():
        raise EosError(f"No prompt registered for {args.stage}")
    workflow = read_tsv(EOS / "workflow.tsv")
    row = next((r for r in workflow if r.get("stage") == args.stage), None)
    if not row:
        raise EosError(f"Stage not found: {args.stage}")

    print(f"# Engineering Operating System Task — {args.stage}\n")
    print("## Permanent Responsibility Model\n")
    print("- Human: final authority and gate approval.")
    print("- ChatGPT: reasoning, synthesis, architecture, planning, traceability, and review.")
    print("- Codex: bounded repository-local implementation and validation after authorization.")
    print("- GitHub: canonical remote history, issues, PRs, CI, releases, and audit trail.\n")
    print("## Stage\n")
    print(f"- Phase: {row['phase']}")
    print(f"- Primary output: {row['primary_output']}")
    print(f"- Lead: {row['lead']}")
    print(f"- Reviewer: {row['reviewer']}")
    print(f"- Gate: {row['gate']}\n")
    print("## Instruction\n")
    print(prompt.read_text(encoding="utf-8").rstrip())
    print("\n## Governing Rules\n")
    print("1. Read idea.md first.")
    print("2. Respect accepted higher-authority artifacts.")
    print("3. Surface contradictions rather than silently choosing.")
    print("4. Preserve stable identifiers and traceability.")
    print("5. Do not impersonate human approval.")
    print("6. Version materially changed accepted artifacts.\n")
    idea = ROOT / "idea.md"
    if idea.exists():
        print("## Primary Inception Source\n")
        print(idea.read_text(encoding="utf-8"))


def update_bootstrap_stage(stage: str, status: str) -> None:
    path = EOS / "workflow.tsv"
    rows = read_tsv(path)
    found = False
    for row in rows:
        if row["stage"] == stage:
            row["status"] = status
            row["completed_at"] = now_iso() if status == "COMPLETE" else "-"
            found = True
            break
    if not found:
        raise EosError(f"Stage not found: {stage}")
    fields = [
        "order",
        "stage",
        "phase",
        "primary_output",
        "lead",
        "reviewer",
        "gate",
        "status",
        "completed_at",
    ]
    write_tsv(path, fields, rows)


def cmd_complete(args: argparse.Namespace) -> None:
    update_bootstrap_stage(args.stage, "COMPLETE")
    print(f"Marked {args.stage} COMPLETE.")
    print(f'Checkpoint suggestion: ./scripts/eos checkpoint "complete {args.stage}"')


def cmd_reopen(args: argparse.Namespace) -> None:
    update_bootstrap_stage(args.stage, "PENDING")
    print(f"Reopened {args.stage}.")


def cmd_version(args: argparse.Namespace) -> None:
    path = (ROOT / args.path).resolve()
    if not path.exists():
        raise EosError(f"Artifact not found: {args.path}")
    data, body = parse_frontmatter(path)
    current = data.get("version")
    if not current:
        raise EosError(f"{args.path} has no governed artifact version")
    snap = snapshot_path(path, current)
    if not snap.exists():
        snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, snap)
    new = bump_semver(current, args.kind)
    data["version"] = new
    data["updated"] = today()
    write_frontmatter(path, data, body)

    fields = [
        "timestamp",
        "artifact_id",
        "path",
        "from_version",
        "to_version",
        "change_type",
        "message",
    ]
    append_tsv(
        EOS / "artifact-changelog.tsv",
        fields,
        {
            "timestamp": now_iso(),
            "artifact_id": data.get("artifact_id", "UNREGISTERED"),
            "path": rel(path),
            "from_version": current,
            "to_version": new,
            "change_type": args.kind,
            "message": args.message,
        },
    )
    print(f"{rel(path)}: {current} -> {new} ({args.message})")


def cmd_history(args: argparse.Namespace) -> None:
    path = (ROOT / args.path).resolve()
    data, _ = parse_frontmatter(path) if path.exists() else ({}, "")
    print(f"Artifact: {data.get('artifact_id', 'UNREGISTERED')}")
    print(f"Path: {rel(path)}\n")
    print("Semantic artifact history:")
    for row in read_tsv(EOS / "artifact-changelog.tsv"):
        if row.get("path") == rel(path):
            print(
                f"  {row['timestamp']} {row['from_version']} -> {row['to_version']} "
                f"{row['change_type']} {row['message']}"
            )
    base = EOS / "history" / Path(rel(path)).with_suffix("")
    print("\nRetained snapshots:")
    if base.exists():
        for p in sorted(base.glob("*")):
            print(f"  {rel(p)}")
    else:
        print("  none")
    if git_available():
        print("\nGit history:")
        result = run(["git", "log", "--oneline", "--follow", "--", rel(path)], cwd=ROOT, check=False)
        print(textwrap.indent(result.stdout.strip() or "none", "  "))


def cmd_rollback(args: argparse.Namespace) -> None:
    path = (ROOT / args.path).resolve()
    if not path.exists():
        raise EosError(f"Current artifact not found: {args.path}")
    data, _ = parse_frontmatter(path)
    current = data.get("version")
    if not current:
        raise EosError(f"{args.path} is not a governed artifact")
    target = args.version.removeprefix("v")
    target_path = snapshot_path(path, target)
    if not target_path.exists():
        raise EosError(f"No retained snapshot for {args.path} v{target}")

    current_snap = snapshot_path(path, current)
    if not current_snap.exists():
        current_snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, current_snap)

    restored_data, restored_body = parse_frontmatter(target_path)
    new_version = bump_semver(current, "patch")
    restored_data["version"] = new_version
    restored_data["updated"] = today()
    write_frontmatter(path, restored_data, restored_body)

    fields = [
        "timestamp",
        "artifact_id",
        "path",
        "from_version",
        "to_version",
        "change_type",
        "message",
    ]
    append_tsv(
        EOS / "artifact-changelog.tsv",
        fields,
        {
            "timestamp": now_iso(),
            "artifact_id": restored_data.get("artifact_id", "UNREGISTERED"),
            "path": rel(path),
            "from_version": current,
            "to_version": new_version,
            "change_type": "rollback",
            "message": f"RESTORE v{target}: {args.message}",
        },
    )
    print(f"Restored v{target} content as new version v{new_version}.")


def cmd_checkpoint(args: argparse.Namespace) -> None:
    if not git_available():
        raise EosError("git is required for checkpoints")
    stamp = dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    meta = EOS / "checkpoints" / f"{stamp}.txt"
    meta.write_text(f"timestamp={now_iso()}\nmessage={args.message}\n", encoding="utf-8")
    run(["git", "add", "-A"], cwd=ROOT)
    diff = run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
    if diff.returncode == 0:
        meta.unlink(missing_ok=True)
        print("No changes to checkpoint.")
        return
    run(["git", "commit", "-m", f"checkpoint: {args.message}"], cwd=ROOT, capture=False)
    tag = f"eos/checkpoint-{stamp}"
    run(["git", "tag", "-a", tag, "-m", args.message], cwd=ROOT, capture=False)
    print(f"Created {tag} at {commit_sha()[:12]}")


def pi_body(pi_id: str, title: str, objective: str) -> str:
    return f"""# {pi_id} — {title}

**State:** DRAFT

## Objective

{objective}

## Intended Outcomes

TBD.

## Governing Artifacts

TBD.

## Included Work Cycles

TBD.

## Scope

### In Scope

TBD.

### Out of Scope

TBD.

## Dependencies

TBD.

## Risks

TBD.

## Entry Criteria

- [ ] Governing requirements are accepted.
- [ ] Architecture/specification deltas are understood.
- [ ] Dependencies are identified.
- [ ] PI readiness review is accepted.

## Exit Criteria

- [ ] Included work cycles are closed.
- [ ] PI acceptance evidence is complete.
- [ ] PI closeout review is accepted.
"""


def cmd_plan(args: argparse.Namespace) -> None:
    if args.pi:
        if not re.fullmatch(r"PI-\d{3}", args.pi):
            raise EosError("PI id must look like PI-002")
        pi_id = args.pi
    else:
        pi_id = f"PI-{next_number('PI', 3):03d}"
    if find_row("PI", pi_id):
        raise EosError(f"{pi_id} already exists")

    title = args.title or f"Program Increment {pi_id.split('-')[1]}"
    objective = args.objective or "TBD."
    path = ROOT / "engineering" / "increments" / f"{pi_id}.md"
    create_artifact(path, pi_id, title, "program-increment", "planning-authoritative", pi_body(pi_id, title, objective))
    rows = registry("PI")
    rows.append(
        {
            "id": pi_id,
            "path": rel(path),
            "title": title,
            "status": "DRAFT",
            "created": now_iso(),
            "updated": now_iso(),
            "github_url": "",
        }
    )
    save_registry("PI", rows)
    print(f"Created {pi_id}: {rel(path)}")
    print(f"Next: complete the PI definition, then ./scripts/eos review {pi_id}")


def wc_body(wc_id: str, title: str, pi: str) -> str:
    return f"""# {wc_id} — {title}

**State:** DRAFT

## Objective

TBD.

## Parent Program Increment

- {pi}

## Included Work Packets

TBD.

## Scope

### In Scope

TBD.

### Out of Scope

TBD.

## Dependencies

TBD.

## Entry Criteria

- [ ] Parent PI is authorized.
- [ ] Scope is bounded.
- [ ] Required work packets can be defined.

## Exit Criteria

- [ ] All included work packets are closed.
- [ ] Work-cycle review is accepted.
"""


def cmd_create_wc(args: argparse.Namespace) -> None:
    pi = args.pi
    if not pi:
        row = latest_active("PI")
        if not row:
            raise EosError("No active PI; create one with ./scripts/eos plan")
        pi = row["id"]
    pi_row = find_row("PI", pi)
    if not pi_row:
        raise EosError(f"Unknown parent PI: {pi}")
    wc_id = f"WC-{next_number('WC', 4):04d}"
    title = args.title or f"Work Cycle {wc_id.split('-')[1]}"
    path = ROOT / "engineering" / "work-cycles" / f"{wc_id}.md"
    create_artifact(path, wc_id, title, "work-cycle", "planning-authoritative", wc_body(wc_id, title, pi))
    rows = registry("WC")
    rows.append(
        {
            "id": wc_id,
            "path": rel(path),
            "title": title,
            "status": "DRAFT",
            "pi": pi,
            "created": now_iso(),
            "updated": now_iso(),
            "github_url": "",
        }
    )
    save_registry("WC", rows)
    print(f"Created {wc_id} under {pi}: {rel(path)}")


def wp_body(wp_id: str, title: str, pi: str, wc: str) -> str:
    return f"""# {wp_id} — {title}

**State:** DRAFT

## Objective

TBD.

## Parent

- PI: {pi}
- Work Cycle: {wc}

## Scope

### In Scope

TBD.

### Out of Scope

TBD.

## Governing Artifacts

- Requirements: TBD
- Specifications: TBD
- ADRs: TBD
- Quality attributes: TBD

## Dependencies

TBD.

## Deliverables

TBD.

## Acceptance Criteria

- [ ] TBD

## Validation

TBD.

## Risks

TBD.

## Completion Evidence

TBD.
"""


def cmd_create_wp(args: argparse.Namespace) -> None:
    wc = args.wc
    if not wc:
        row = latest_active("WC")
        if not row:
            raise EosError("No active work cycle; create one with ./scripts/eos create-wc")
        wc = row["id"]
    wc_row = find_row("WC", wc)
    if not wc_row:
        raise EosError(f"Unknown parent work cycle: {wc}")
    pi = wc_row["pi"]

    domain = args.domain.upper() if args.domain else ""
    if domain and not re.fullmatch(r"[A-Z][A-Z0-9]{1,15}", domain):
        raise EosError("Domain must be 2-16 uppercase alphanumeric characters")
    number = next_number("WP", 4, prefix=domain or None)
    wp_id = f"WP-{domain}-{number:04d}" if domain else f"WP-{number:04d}"
    title = args.title or f"Work Packet {wp_id}"
    path = ROOT / "engineering" / "work-packets" / f"{wp_id}.md"
    create_artifact(path, wp_id, title, "work-packet", "planning-authoritative", wp_body(wp_id, title, pi, wc))
    rows = registry("WP")
    rows.append(
        {
            "id": wp_id,
            "path": rel(path),
            "title": title,
            "status": "DRAFT",
            "pi": pi,
            "wc": wc,
            "domain": domain,
            "created": now_iso(),
            "updated": now_iso(),
            "github_url": "",
        }
    )
    save_registry("WP", rows)
    print(f"Created {wp_id} under {wc}/{pi}: {rel(path)}")


def gate_authorization(target: str) -> list[str]:
    kind, row = row_for_target(target)
    reasons: list[str] = []
    path = ROOT / row["path"]
    complete, issues = artifact_is_complete_enough(path)
    if not complete:
        reasons.extend(issues)

    if kind == "WP":
        wc = find_row("WC", row["wc"])
        if not wc or wc["status"] not in {"AUTHORIZED", "ACTIVE"}:
            reasons.append(f"parent {row['wc']} is not authorized/active")
    elif kind == "WC":
        pi = find_row("PI", row["pi"])
        if not pi or pi["status"] not in {"AUTHORIZED", "ACTIVE"}:
            reasons.append(f"parent {row['pi']} is not authorized/active")
    elif kind == "PI":
        readiness = ROOT / "engineering" / "reviews" / f"{target}-READINESS-REVIEW.md"
        generic = review_path(target)
        bootstrap_rpath = ROOT / "engineering" / "reviews" / "PI-001-READINESS-REVIEW.md"
        candidates = [readiness, generic]
        if target == "PI-001":
            candidates.append(bootstrap_rpath)
        accepted_complete = [
            candidate for candidate in candidates
            if accepted_review_complete(candidate)[0]
        ]
        if not accepted_complete:
            reasons.append(
                "PI readiness review is not accepted and complete: "
                + " or ".join(rel(candidate) for candidate in candidates)
            )
    return reasons


def cmd_authorize(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind not in {"PI", "WC", "WP"}:
        raise EosError("authorize currently applies to PI, WC, or WP")
    reasons = gate_authorization(args.target)
    if reasons and not args.force:
        raise EosError(
            "Authorization gate failed:\n- " + "\n- ".join(reasons) +
            "\nUse --force --reason '...' only for an explicit human override."
        )
    actor = args.by or os.environ.get("USER") or "human"
    reason = args.reason or ("human authorization" if not reasons else "human override")
    set_lifecycle_state(args.target, "AUTHORIZED")
    record_decision(args.target, "authorize", "AUTHORIZED", actor, reason)
    print(f"{args.target} AUTHORIZED by {actor}.")
    if reasons:
        print("Override findings retained:")
        for item in reasons:
            print(f"  - {item}")


def cmd_start(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    current = row["status"]
    if kind == "PI":
        allowed, new = {"AUTHORIZED", "ACTIVE"}, "ACTIVE"
    elif kind == "WC":
        allowed, new = {"AUTHORIZED", "ACTIVE"}, "ACTIVE"
    elif kind == "WP":
        allowed, new = {"AUTHORIZED", "IN_PROGRESS"}, "IN_PROGRESS"
    elif kind == "MNT":
        allowed, new = {"OPEN", "PLANNED", "IN_PROGRESS"}, "IN_PROGRESS"
    else:
        raise EosError(f"start is not supported for {kind}")
    if current not in allowed:
        raise EosError(f"{args.target} cannot start from state {current}")
    set_lifecycle_state(args.target, new)
    print(f"{args.target} -> {new}")


def referenced_ids(path: Path) -> list[str]:
    if not path.exists():
        return []
    ids = sorted(set(ID_RE.findall(path.read_text(encoding="utf-8", errors="ignore"))))
    data, _ = parse_frontmatter(path) if path.suffix == ".md" else ({}, "")
    own = data.get("artifact_id")
    return [x for x in ids if x != own]


def cmd_codex(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "WP":
        raise EosError("Codex execution contracts are generated for work packets")
    if row["status"] not in {"AUTHORIZED", "IN_PROGRESS", "VERIFYING"} and not args.force:
        raise EosError(
            f"{args.target} is {row['status']}; authorize it before generating an execution contract"
        )
    path = ROOT / row["path"]
    refs = referenced_ids(path)
    related: list[Path] = []
    for rid in refs:
        p = artifact_path_for_id(rid)
        if p and p.exists():
            related.append(p)
    for parent in (row.get("pi"), row.get("wc")):
        if parent:
            p = artifact_path_for_id(parent)
            if p and p.exists():
                related.append(p)

    contract = EOS / "contracts" / f"{args.target}.codex.md"
    parts = [
        f"# Codex Execution Contract — {args.target}",
        "",
        f"Generated: {now_iso()}",
        f"Repository: {ROOT}",
        f"Branch: {current_branch() or '(detached/unknown)'}",
        f"HEAD: {commit_sha() or '(no commit yet)'}",
        "",
        "## Authority",
        "",
        "This contract authorizes bounded implementation only. Codex must not invent or",
        "silently modify product requirements, architecture policy, specifications,",
        "security policy, or scope to make implementation easier.",
        "",
        "## Work Packet",
        "",
        path.read_text(encoding="utf-8"),
        "",
        "## Governing / Related Artifacts",
        "",
    ]
    for p in sorted(set(related), key=lambda x: rel(x)):
        parts.extend([f"### {rel(p)}", "", p.read_text(encoding="utf-8"), ""])
    parts.extend(
        [
            "## Required Operating Procedure",
            "",
            "1. Inspect repository state before modifying files.",
            "2. Create or use a branch scoped to this work packet.",
            "3. Modify only the authorized scope.",
            "4. Preserve identifiers and traceability.",
            "5. Run all repository-prescribed validation plus WP-specific validation.",
            "6. Run `./scripts/eos verify`.",
            "7. Report exact changed files, commands, results, and unresolved findings.",
            "8. Stop and escalate if implementation requires changing governing policy.",
            "",
            "## Required Completion Report",
            "",
            "- Changed files",
            "- Implementation summary",
            "- Acceptance criteria mapping",
            "- Validation commands and results",
            "- Risks / unresolved issues",
            "- Proposed commit message",
            "- Proposed PR title/body",
            "",
        ]
    )
    contract.write_text("\n".join(parts), encoding="utf-8")
    print(contract.read_text(encoding="utf-8"))
    print(f"\nContract persisted to {rel(contract)}", file=sys.stderr)


def run_validation_commands() -> list[tuple[str, int, str]]:
    config = EOS / "validation.commands"
    results: list[tuple[str, int, str]] = []
    if not config.exists():
        return results
    for raw in config.read_text(encoding="utf-8").splitlines():
        cmd = raw.strip()
        if not cmd or cmd.startswith("#"):
            continue
        proc = subprocess.run(
            ["bash", "-lc", cmd],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        output = (proc.stdout + proc.stderr).strip()
        results.append((cmd, proc.returncode, output))
    return results


def cmd_validate(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind == "WP" and row["status"] in {"AUTHORIZED", "IN_PROGRESS"}:
        set_lifecycle_state(args.target, "VERIFYING")
    verify_ok, verify_report = verify_all()
    custom = run_validation_commands()
    stamp = dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    evidence = EOS / "evidence" / f"{args.target}-{stamp}.md"
    lines = [
        f"# Verification Evidence — {args.target}",
        "",
        f"Generated: {now_iso()}",
        f"HEAD: {commit_sha() or '(none)'}",
        "",
        "## EOS Integrity",
        "",
        "```text",
        verify_report,
        "```",
        "",
        "## Repository Validation Commands",
        "",
    ]
    if custom:
        for command, rc, output in custom:
            lines += [
                f"### `{command}`",
                "",
                f"Exit code: {rc}",
                "",
                "```text",
                output[:20000],
                "```",
                "",
            ]
    else:
        lines.append("No additional commands configured in `.eos/validation.commands`.")
    evidence.write_text("\n".join(lines) + "\n", encoding="utf-8")
    failures = [cmd for cmd, rc, _ in custom if rc != 0]
    print(f"Verification evidence: {rel(evidence)}")
    if not verify_ok or failures:
        raise EosError("Verification failed; inspect the evidence artifact.")
    print("Verification passed.")


def review_body(target: str, row: dict[str, str], verify_ok: bool, report: str) -> str:
    return f"""# {target} — Engineering Review

**Decision:** PENDING

## Target

- Artifact: `{row['path']}`
- State at review start: {row['status']}
- Review generated: {now_iso()}
- Git HEAD: {commit_sha() or '(none)'}

## Deterministic Verification

**Result:** {'PASS' if verify_ok else 'FAIL'}

```text
{report}
```

## Scope Conformance

TBD.

## Requirements / Specification Conformance

TBD.

## Architecture Conformance

TBD.

## Acceptance Criteria Evidence

TBD.

## Test / Validation Evidence

TBD.

## Security / Reliability Findings

TBD.

## Traceability Findings

TBD.

## Blocking Findings

TBD.

## Non-Blocking Findings

TBD.

## Decision

Set the top-level `**Decision:**` to one of:

- ACCEPTED
- ACCEPTED_WITH_FOLLOW_UP
- REJECTED
- BLOCKED
"""


def cmd_review(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    verify_ok, report = verify_all()
    path = review_path(args.target)
    if not path.exists():
        create_artifact(
            path,
            f"REV-{args.target}",
            f"{args.target} Engineering Review",
            "review",
            "review-authoritative",
            review_body(args.target, row, verify_ok, report),
            status="In Review",
        )
    else:
        # Preserve human content; add a deterministic evidence companion instead.
        stamp = dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        evidence = EOS / "evidence" / f"{args.target}-review-{stamp}.md"
        evidence.write_text(report + "\n", encoding="utf-8")
    if kind in {"PI", "WC", "WP"}:
        set_lifecycle_state(args.target, "IN_REVIEW")
    contract = EOS / "contracts" / f"{args.target}.review.md"
    target_path = ROOT / row["path"]
    contract.write_text(
        f"""# ChatGPT Review Contract — {args.target}

Review the target against all applicable accepted higher-authority artifacts.

## Target

{target_path.read_text(encoding='utf-8')}

## Required Review Dimensions

- scope conformance;
- requirements and specification conformance;
- architecture conformance;
- acceptance criteria;
- deterministic validation evidence;
- security/reliability risk;
- traceability completeness;
- unresolved findings;
- recommendation: ACCEPTED / ACCEPTED_WITH_FOLLOW_UP / REJECTED / BLOCKED.

Do not impersonate final human authorization where the governance model reserves
that decision to the human.
""",
        encoding="utf-8",
    )
    print(f"Review artifact: {rel(path)}")
    print(f"Review contract: {rel(contract)}")
    print(f"Deterministic verification: {'PASS' if verify_ok else 'FAIL'}")


def unchecked_boxes(path: Path) -> int:
    if not path.exists():
        return 0
    return len(re.findall(r"^- \[ \]", path.read_text(encoding="utf-8"), flags=re.M))


def cmd_close(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "WP":
        raise EosError("Use close-cycle or close-pi for WC/PI")
    path = ROOT / row["path"]
    reasons: list[str] = []
    if row["status"] != "IN_REVIEW":
        reasons.append(f"work packet state is {row['status']}, expected IN_REVIEW")
    complete, issues = artifact_is_complete_enough(path)
    if not complete:
        reasons.extend(issues)
    if unchecked_boxes(path):
        reasons.append(f"{unchecked_boxes(path)} unchecked acceptance/exit item(s) remain")
    rpath = review_path(args.target)
    review_ok, review_issues = accepted_review_complete(rpath)
    if not review_ok:
        reasons.extend(review_issues)
    if reasons and not args.force:
        raise EosError("Closure gate failed:\n- " + "\n- ".join(reasons))
    set_lifecycle_state(args.target, "CLOSED")
    actor = args.by or os.environ.get("USER") or "human"
    record_decision(args.target, "close", "CLOSED", actor, args.reason or "work packet closure")
    print(f"{args.target} CLOSED.")


def cmd_close_cycle(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "WC":
        raise EosError("close-cycle requires a WC id")
    children = [wp for wp in registry("WP") if wp.get("wc") == args.target]
    open_children = [wp["id"] for wp in children if wp["status"] != "CLOSED"]
    reasons: list[str] = []
    if row["status"] != "IN_REVIEW":
        reasons.append(f"work cycle state is {row['status']}, expected IN_REVIEW")
    complete, issues = artifact_is_complete_enough(ROOT / row["path"])
    if not complete:
        reasons.extend(issues)
    if not children:
        reasons.append("work cycle has no registered work packets")
    if open_children:
        reasons.append("open work packets: " + ", ".join(open_children))
    rpath = review_path(args.target)
    review_ok, review_issues = accepted_review_complete(rpath)
    if not review_ok:
        reasons.extend(review_issues)
    if reasons and not args.force:
        raise EosError("Work-cycle closure gate failed:\n- " + "\n- ".join(reasons))
    set_lifecycle_state(args.target, "CLOSED")
    actor = args.by or os.environ.get("USER") or "human"
    record_decision(args.target, "close-cycle", "CLOSED", actor, args.reason or "work cycle closure")
    print(f"{args.target} CLOSED.")


def cmd_close_pi(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "PI":
        raise EosError("close-pi requires a PI id")
    children = [wc for wc in registry("WC") if wc.get("pi") == args.target]
    open_children = [wc["id"] for wc in children if wc["status"] != "CLOSED"]
    reasons: list[str] = []
    if row["status"] != "IN_REVIEW":
        reasons.append(f"program increment state is {row['status']}, expected IN_REVIEW")
    complete, issues = artifact_is_complete_enough(ROOT / row["path"])
    if not complete:
        reasons.extend(issues)
    if not children:
        reasons.append("program increment has no registered work cycles")
    if open_children:
        reasons.append("open work cycles: " + ", ".join(open_children))
    rpath = review_path(args.target)
    closeout = ROOT / "engineering" / "reviews" / f"{args.target}-CLOSEOUT-REVIEW.md"
    closeout_ok, closeout_issues = accepted_review_complete(closeout)
    generic_ok, generic_issues = accepted_review_complete(rpath)
    if not (closeout_ok or generic_ok):
        reasons.append(
            f"PI closeout review is not accepted and complete: {rel(closeout)} or {rel(rpath)}"
        )
        # Keep the most useful details without duplicating missing-review messages.
        reasons.extend(closeout_issues if closeout.exists() else generic_issues)
    if reasons and not args.force:
        raise EosError("PI closure gate failed:\n- " + "\n- ".join(reasons))
    set_lifecycle_state(args.target, "CLOSED")
    actor = args.by or os.environ.get("USER") or "human"
    record_decision(args.target, "close-pi", "CLOSED", actor, args.reason or "program increment closure")
    print(f"{args.target} CLOSED.")


def candidate_trace_files() -> Iterable[Path]:
    # Trace governing/project artifacts, not generated EOS state, contracts,
    # templates, tooling, or documentation examples. This keeps impact analysis
    # semantically useful instead of treating example IDs as real dependencies.
    allowed = {".md", ".yml", ".yaml", ".toml"}
    excluded_prefixes = (
        ".git/",
        ".eos/",
        "tools/",
        "engineering/lifecycle/",
        "engineering/prompts/",
    )
    excluded_names = {
        "README.md",
        "template.md",
        "ADR-0000-template.md",
    }
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        rp = rel(path)
        if rp in excluded_names or path.name in excluded_names:
            continue
        if rp.startswith(excluded_prefixes):
            continue
        yield path


def source_id_for(path: Path) -> str:
    if path.suffix == ".md":
        data, _ = parse_frontmatter(path)
        if data.get("artifact_id"):
            return data["artifact_id"]
    stem = path.stem
    m = ID_RE.search(stem)
    return m.group(0) if m else f"FILE:{rel(path)}"


def rebuild_trace() -> list[dict[str, str]]:
    edges: dict[tuple[str, str, str], dict[str, str]] = {}
    for path in candidate_trace_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        source = source_id_for(path)
        for target in set(ID_RE.findall(text)):
            if target == source:
                continue
            key = (source, target, rel(path))
            edges[key] = {
                "source_id": source,
                "target_id": target,
                "source_path": rel(path),
            }
    fields = ["source_id", "target_id", "source_path"]
    rows = sorted(edges.values(), key=lambda r: (r["source_id"], r["target_id"], r["source_path"]))
    write_tsv(EOS / "trace-edges.tsv", fields, rows)
    return rows


def cmd_trace(args: argparse.Namespace) -> None:
    edges = rebuild_trace()
    target = args.target
    path = artifact_path_for_id(target)
    print(f"TRACE — {target}")
    print(f"Artifact: {rel(path) if path else '(not directly located)'}\n")

    outgoing = [e for e in edges if e["source_id"] == target]
    incoming = [e for e in edges if e["target_id"] == target]

    print("Depends on / references:")
    if outgoing:
        for e in outgoing:
            print(f"  {e['target_id']:<20} via {e['source_path']}")
    else:
        print("  none discovered")

    print("\nReferenced by:")
    if incoming:
        for e in incoming:
            print(f"  {e['source_id']:<20} via {e['source_path']}")
    else:
        print("  none discovered")


def cmd_impact(args: argparse.Namespace) -> None:
    edges = rebuild_trace()
    reverse: dict[str, set[str]] = {}
    locations: dict[tuple[str, str], set[str]] = {}
    for e in edges:
        reverse.setdefault(e["target_id"], set()).add(e["source_id"])
        locations.setdefault((e["target_id"], e["source_id"]), set()).add(e["source_path"])

    queue = deque([(args.target, 0)])
    seen = {args.target}
    results: list[tuple[int, str, str]] = []
    while queue:
        node, depth = queue.popleft()
        for dependent in sorted(reverse.get(node, set())):
            if dependent in seen:
                continue
            seen.add(dependent)
            results.append((depth + 1, dependent, ", ".join(sorted(locations.get((node, dependent), set())))))
            queue.append((dependent, depth + 1))

    print(f"IMPACT ANALYSIS — {args.target}\n")
    if not results:
        print("No downstream references discovered.")
        return
    for depth, entity, paths in results:
        print(f"{'  ' * (depth - 1)}- {entity}  [{paths}]")


def gh_repo() -> str:
    if shutil.which("gh"):
        proc = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], cwd=ROOT, check=False)
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    if git_available():
        proc = run(["git", "remote", "get-url", "origin"], cwd=ROOT, check=False)
        url = proc.stdout.strip()
        m = re.search(r"github\.com[:/]([^/]+/[^/.]+)(?:\.git)?$", url)
        if m:
            return m.group(1)
    raise EosError("Cannot determine GitHub repository. Configure origin or authenticate gh.")


def gh_label_ensure(repo: str, name: str, description: str, apply: bool) -> None:
    if not apply:
        print(f"DRY-RUN label {name}: {description}")
        return
    proc = run(["gh", "label", "create", name, "--repo", repo, "--description", description], cwd=ROOT, check=False)
    if proc.returncode != 0 and "already exists" not in (proc.stderr or ""):
        # Attempt edit to keep description current.
        run(["gh", "label", "edit", name, "--repo", repo, "--description", description], cwd=ROOT, check=False)


def github_milestone_ensure(repo: str, title: str, apply: bool) -> str:
    if not apply:
        print(f"DRY-RUN milestone: {title}")
        return title
    import json
    proc = run(
        ["gh", "api", f"repos/{repo}/milestones?state=all&per_page=100"],
        cwd=ROOT,
        check=False,
    )
    if proc.returncode == 0:
        try:
            for item in json.loads(proc.stdout or "[]"):
                if item.get("title") == title:
                    return title
        except Exception:
            pass
    run(
        ["gh", "api", "--method", "POST", f"repos/{repo}/milestones", "-f", f"title={title}"],
        cwd=ROOT,
        check=True,
    )
    return title


def github_issue_for(
    repo: str,
    title: str,
    body_file: Path,
    labels: list[str],
    milestone: str,
    apply: bool,
) -> str:
    if not apply:
        print(
            f"DRY-RUN issue: {title} labels={','.join(labels)} "
            f"milestone={milestone or '-'} body={rel(body_file)}"
        )
        return ""
    search = run(
        ["gh", "issue", "list", "--repo", repo, "--state", "all", "--search", f'"{title}" in:title', "--json", "title,url"],
        cwd=ROOT,
        check=False,
    )
    if search.returncode == 0:
        import json
        try:
            for item in json.loads(search.stdout or "[]"):
                if item.get("title") == title:
                    return item.get("url", "")
        except Exception:
            pass
    args = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body-file", str(body_file)]
    for label in labels:
        args += ["--label", label]
    if milestone:
        args += ["--milestone", milestone]
    proc = run(args, cwd=ROOT, check=True)
    return proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""


def github_issue_sync(
    url: str,
    body_file: Path,
    labels: list[str],
    milestone: str,
    status: str,
    *,
    apply: bool,
    project: str,
    owner: str,
) -> None:
    if not url:
        return
    if not apply:
        print(
            f"DRY-RUN update: {url} status={status} milestone={milestone or '-'} "
            f"project={project or '-'}"
        )
        return
    args = ["gh", "issue", "edit", url, "--body-file", str(body_file)]
    for label in labels:
        args += ["--add-label", label]
    if milestone:
        args += ["--milestone", milestone]
    run(args, cwd=ROOT, check=False)
    if status == "CLOSED":
        run(["gh", "issue", "close", url, "--reason", "completed"], cwd=ROOT, check=False)
    if project:
        run(
            ["gh", "project", "item-add", project, "--owner", owner, "--url", url],
            cwd=ROOT,
            check=False,
        )


def update_github_url(kind: str, target: str, url: str) -> None:
    if url:
        update_row(kind, target, github_url=url)


def cmd_github_sync(args: argparse.Namespace) -> None:
    if args.apply and not shutil.which("gh"):
        raise EosError("GitHub CLI `gh` is required for --apply")
    repo = gh_repo()
    owner = args.owner or repo.split("/", 1)[0]
    print(f"GitHub repository: {repo}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    if args.project:
        print(f"GitHub Project: {owner}/{args.project}")
    print()

    labels = {
        "eos": "Managed by the Engineering Operating System",
        "program-increment": "Program increment tracking",
        "work-cycle": "Work cycle tracking",
        "work-packet": "Work packet tracking",
        "change-request": "Governed change request",
        "maintenance": "Maintenance work",
        "release": "Release lifecycle",
        "authorized": "Authorized for execution",
        "blocked": "Blocked by a gate or dependency",
    }
    for name, desc in labels.items():
        gh_label_ensure(repo, name, desc, args.apply)

    milestones: dict[str, str] = {}
    for pi in registry("PI"):
        milestones[pi["id"]] = github_milestone_ensure(repo, pi["id"], args.apply)

    for kind, label in (("PI", "program-increment"), ("WC", "work-cycle"), ("WP", "work-packet"), ("CR", "change-request"), ("MNT", "maintenance")):
        rows = registry(kind)
        for row in rows:
            path = ROOT / row["path"]
            if not path.exists():
                continue
            title = f"{row['id']}: {row.get('title') or row.get('summary') or row['id']}"
            issue_labels = ["eos", label]
            if row.get("status") == "AUTHORIZED":
                issue_labels.append("authorized")
            if row.get("status") == "BLOCKED":
                issue_labels.append("blocked")
            pi_id = row["id"] if kind == "PI" else row.get("pi", "")
            milestone = milestones.get(pi_id, "")
            url = row.get("github_url", "")
            if not url:
                url = github_issue_for(repo, title, path, issue_labels, milestone, args.apply)
                if args.apply and url:
                    update_github_url(kind, row["id"], url)
                    print(f"SYNCED {row['id']} -> {url}")
            if url:
                github_issue_sync(
                    url,
                    path,
                    issue_labels,
                    milestone,
                    row.get("status", ""),
                    apply=args.apply,
                    project=args.project,
                    owner=owner,
                )

    stamp = dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    (EOS / "sync" / f"github-{stamp}.txt").write_text(
        f"timestamp={now_iso()}\nrepo={repo}\nmode={'apply' if args.apply else 'dry-run'}\n",
        encoding="utf-8",
    )
    if not args.apply:
        print("\nNo GitHub changes were made. Re-run with --apply to synchronize.")


def cmd_change_create(args: argparse.Namespace) -> None:
    cr_id = f"CR-{next_number('CR', 4):04d}"
    title = args.summary
    path = ROOT / "engineering" / "changes" / f"{cr_id}.md"
    body = f"""# {cr_id} — {title}

**State:** PROPOSED

## Target

{args.target}

## Summary

{args.summary}

## Motivation

{args.reason or 'TBD.'}

## Proposed Change

TBD.

## Impact Analysis

Run:

`./scripts/eos impact {args.target}`

Then summarize affected artifacts and implementation.

## Alternatives

TBD.

## Risks

TBD.

## Migration / Rollback

TBD.

## Decision

**Decision:** PENDING
"""
    create_artifact(path, cr_id, title, "change-request", "governance-authoritative", body, status="Proposed")
    rows = registry("CR")
    rows.append(
        {
            "id": cr_id,
            "path": rel(path),
            "target": args.target,
            "summary": args.summary,
            "status": "PROPOSED",
            "created": now_iso(),
            "updated": now_iso(),
            "github_url": "",
        }
    )
    save_registry("CR", rows)
    print(f"Created {cr_id}: {rel(path)}")


def cmd_change_approve(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "CR":
        raise EosError("change approve requires CR-NNNN")
    path = ROOT / row["path"]
    if not is_review_accepted(path) and not args.force:
        # Change request uses its own Decision field; ACCEPTED/APPROVED counts.
        decision = review_decision(path)
        if decision not in {"APPROVED", "ACCEPTED"}:
            raise EosError(
                "Change request decision is not APPROVED/ACCEPTED. "
                "Update the artifact or use --force with an explicit reason."
            )
    update_row("CR", args.target, status="APPROVED")
    sync_artifact_state(path, "APPROVED")
    actor = args.by or os.environ.get("USER") or "human"
    record_decision(args.target, "change-approve", "APPROVED", actor, args.reason or "change approved")
    print(f"{args.target} APPROVED.")


def cmd_change_close(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "CR":
        raise EosError("change close requires CR-NNNN")
    update_row("CR", args.target, status="CLOSED")
    sync_artifact_state(ROOT / row["path"], "CLOSED")
    print(f"{args.target} CLOSED.")


def cmd_maintain_create(args: argparse.Namespace) -> None:
    mnt_id = f"MNT-{next_number('MNT', 4):04d}"
    path = ROOT / "engineering" / "maintenance" / f"{mnt_id}.md"
    body = f"""# {mnt_id} — {args.summary}

**State:** OPEN

## Type

{args.type}

## Summary

{args.summary}

## Context

{args.context or 'TBD.'}

## Affected Artifacts / Components

TBD.

## Risk if Deferred

TBD.

## Proposed Resolution

TBD.

## Validation

TBD.

## Closure Evidence

TBD.
"""
    create_artifact(path, mnt_id, args.summary, "maintenance", "planning-authoritative", body, status="Open")
    rows = registry("MNT")
    rows.append(
        {
            "id": mnt_id,
            "path": rel(path),
            "type": args.type,
            "summary": args.summary,
            "status": "OPEN",
            "created": now_iso(),
            "updated": now_iso(),
            "github_url": "",
        }
    )
    save_registry("MNT", rows)
    print(f"Created {mnt_id}: {rel(path)}")


def cmd_maintain_close(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "MNT":
        raise EosError("maintain close requires MNT-NNNN")
    path = ROOT / row["path"]
    if unchecked_boxes(path) and not args.force:
        raise EosError("Maintenance artifact still has unchecked completion items")
    update_row("MNT", args.target, status="CLOSED")
    sync_artifact_state(path, "CLOSED")
    print(f"{args.target} CLOSED.")


def release_artifact(version: str) -> tuple[str, Path]:
    rel_id = f"REL-{version}"
    path = ROOT / "engineering" / "releases" / f"{rel_id}.md"
    return rel_id, path


def release_readiness_path(version: str) -> Path:
    return ROOT / "engineering" / "reviews" / f"REL-{version}-READINESS-REVIEW.md"


def prepare_release(version: str) -> tuple[str, Path, Path]:
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise EosError("Release version must be semantic version X.Y.Z")
    rel_id, path = release_artifact(version)
    if not path.exists():
        body = f"""# {rel_id} — Release {version}

**State:** PROPOSED

## Release Objective

TBD.

## Included Program Increments / Work

TBD.

## User-Visible Changes

TBD.

## Compatibility / Migration

TBD.

## Security and Supply-Chain Evidence

TBD.

## Verification Evidence

TBD.

## Known Limitations

TBD.

## Rollback / Recovery

TBD.

## Release Notes

TBD.
"""
        create_artifact(path, rel_id, f"Release {version}", "release", "release-authoritative", body, status="Proposed")
        rows = registry("REL")
        rows.append(
            {
                "id": rel_id,
                "path": rel(path),
                "version": version,
                "status": "PROPOSED",
                "created": now_iso(),
                "updated": now_iso(),
                "github_url": "",
            }
        )
        save_registry("REL", rows)

    review = release_readiness_path(version)
    if not review.exists():
        body = f"""# {rel_id} — Release Readiness Review

**Decision:** PENDING

## Release Artifact

- `{rel(path)}`

## Integrity

TBD.

## Included Work Closed

TBD.

## Test / Verification Evidence

TBD.

## Security / Supply Chain

TBD.

## Documentation / Migration

TBD.

## Rollback Readiness

TBD.

## Blocking Findings

TBD.

## Decision

Set `**Decision:**` to APPROVED only when the release may be tagged/published.
"""
        create_artifact(review, f"REV-{rel_id}", f"{rel_id} Release Readiness Review", "review", "review-authoritative", body, status="In Review")
    return rel_id, path, review


def cmd_release(args: argparse.Namespace) -> None:
    rel_id, path, review = prepare_release(args.version)
    verify_ok, report = verify_all()
    print(report)
    if not verify_ok and not args.force:
        raise EosError("EOS verification failed; release blocked.")

    release_complete, release_issues = artifact_is_complete_enough(path)
    review_complete, review_issues = accepted_review_complete(review)
    release_gate_issues = []
    if not release_complete:
        release_gate_issues.extend(release_issues)
    if not review_complete:
        release_gate_issues.extend(review_issues)
    if release_gate_issues and not args.force:
        print(f"\nPrepared release artifacts:")
        print(f"  {rel(path)}")
        print(f"  {rel(review)}")
        raise EosError(
            "Release gate is not complete:\n- " + "\n- ".join(release_gate_issues)
        )

    if not git_available():
        raise EosError("git is required to finalize a release")
    if not git_clean() and not args.force:
        raise EosError("Working tree must be clean before final release execution")

    tag = f"v{args.version}"
    existing = run(["git", "tag", "--list", tag], cwd=ROOT).stdout.strip()
    if existing:
        print(f"{tag} already exists.")
    else:
        # Update lifecycle state before tagging; commit the release state.
        update_row("REL", rel_id, status="RELEASED")
        sync_artifact_state(path, "RELEASED")
        run(["git", "add", rel(path), rel(review), REGISTRY_PATHS["REL"]], cwd=ROOT)
        staged = run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, check=False)
        if staged.returncode != 0:
            run(["git", "commit", "-m", f"release: {tag}"], cwd=ROOT, capture=False)
        run(["git", "tag", "-a", tag, "-m", f"Release {args.version}"], cwd=ROOT, capture=False)
        print(f"Created annotated release tag {tag}")

    if args.publish:
        if not shutil.which("gh"):
            raise EosError("gh CLI is required for --publish")
        repo = gh_repo()
        run(["git", "push", "origin", "HEAD", tag], cwd=ROOT, capture=False)
        proc = run(
            ["gh", "release", "view", tag, "--repo", repo],
            cwd=ROOT,
            check=False,
        )
        if proc.returncode != 0:
            run(
                ["gh", "release", "create", tag, "--repo", repo, "--title", f"Release {args.version}", "--notes-file", str(path)],
                cwd=ROOT,
                capture=False,
            )
        print(f"Published {tag} to GitHub repository {repo}")


def verify_all() -> tuple[bool, str]:
    failures: list[str] = []
    warnings: list[str] = []
    lines: list[str] = []

    required = [
        ROOT / "idea.md",
        EOS / "layers.tsv",
        EOS / "workflow.tsv",
        EOS / "artifacts.tsv",
        ROOT / "governance" / "responsibility-model.md",
    ]
    for path in required:
        if not path.exists():
            failures.append(f"missing required file: {rel(path)}")

    # Permanent layers.
    layers = read_tsv(EOS / "layers.tsv")
    layer_codes = [r.get("code", "") for r in layers]
    if layer_codes != list(LAYER_ORDER):
        failures.append(
            "permanent layer registry must contain EOSB, EOSP, EOSE, EOSV, EOSR, EOSC, EOSL, EOSM in order"
        )

    # Artifact registry.
    artifacts = read_tsv(EOS / "artifacts.tsv")
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for row in artifacts:
        aid = row.get("artifact_id", "")
        p = row.get("path", "")
        if aid in seen_ids:
            failures.append(f"duplicate artifact id: {aid}")
        seen_ids.add(aid)
        if p in seen_paths:
            warnings.append(f"duplicate artifact path in registry: {p}")
        seen_paths.add(p)
        path = ROOT / p
        if not path.exists():
            failures.append(f"registered artifact missing: {aid} -> {p}")
            continue
        if path.suffix == ".md":
            data, _ = parse_frontmatter(path)
            fm_id = data.get("artifact_id")
            if fm_id and fm_id != aid:
                failures.append(f"artifact id mismatch: registry {aid}, frontmatter {fm_id}, path {p}")

    # Lifecycle registries and parent integrity.
    all_pi = {r["id"]: r for r in registry("PI")}
    all_wc = {r["id"]: r for r in registry("WC")}
    all_wp = {r["id"]: r for r in registry("WP")}
    for kind, rows in (("PI", all_pi.values()), ("WC", all_wc.values()), ("WP", all_wp.values()), ("CR", registry("CR")), ("MNT", registry("MNT")), ("REL", registry("REL"))):
        ids: set[str] = set()
        for row in rows:
            rid = row["id"]
            if rid in ids:
                failures.append(f"duplicate {kind} id: {rid}")
            ids.add(rid)
            if row["status"] not in VALID_STATES[kind]:
                failures.append(f"{rid} has invalid state {row['status']}")
            path = ROOT / row["path"]
            if not path.exists():
                failures.append(f"{rid} path missing: {row['path']}")
        if kind == "WC":
            for row in rows:
                if row.get("pi") not in all_pi:
                    failures.append(f"{row['id']} references missing parent PI {row.get('pi')}")
        if kind == "WP":
            for row in rows:
                wc = all_wc.get(row.get("wc", ""))
                if not wc:
                    failures.append(f"{row['id']} references missing parent WC {row.get('wc')}")
                elif wc.get("pi") != row.get("pi"):
                    failures.append(
                        f"{row['id']} parent mismatch: registry pi={row.get('pi')} but {wc['id']} belongs to {wc.get('pi')}"
                    )

    # Bootstrap stages.
    workflow = read_tsv(EOS / "workflow.tsv")
    stages = [r.get("stage") for r in workflow]
    if len(stages) != len(set(stages)):
        failures.append("duplicate EOSB workflow stage IDs")

    # Trace graph can be rebuilt as a verification side effect.
    try:
        edges = rebuild_trace()
        lines.append(f"trace edges: {len(edges)}")
    except Exception as exc:
        failures.append(f"trace rebuild failed: {exc}")

    lines.insert(0, f"registered artifacts: {len(artifacts)}")
    lines.append(f"program increments: {len(all_pi)}")
    lines.append(f"work cycles: {len(all_wc)}")
    lines.append(f"work packets: {len(all_wp)}")

    if warnings:
        lines.append("warnings:")
        lines.extend(f"  WARN {w}" for w in warnings)
    if failures:
        lines.append("failures:")
        lines.extend(f"  FAIL {f}" for f in failures)
        lines.append(f"RESULT: FAIL ({len(failures)} failure(s))")
        return False, "\n".join(lines)
    lines.append("RESULT: PASS")
    return True, "\n".join(lines)


def cmd_verify(_: argparse.Namespace) -> None:
    ok, report = verify_all()
    print(report)
    if not ok:
        raise EosError("EOS verification failed")


def cmd_doctor(_: argparse.Namespace) -> None:
    print("EOS DOCTOR\n")
    checks = [
        ("python3", shutil.which("python3") or ""),
        ("git", shutil.which("git") or ""),
        ("gh (optional)", shutil.which("gh") or ""),
        ("bash", shutil.which("bash") or ""),
    ]
    for name, value in checks:
        print(f"{name:<16} {'OK ' + value if value else 'MISSING'}")
    print(f"\nroot: {ROOT}")
    print(f"branch: {current_branch() or '(unknown)'}")
    print(f"HEAD: {commit_sha() or '(none)'}")
    print(f"git: {git_status()}")


TOP_LEVEL_COMPLETION_COMMANDS = (
    "layers", "status", "next", "prompt", "complete", "reopen", "version",
    "history", "rollback", "checkpoint", "plan", "create-wc", "create-wp",
    "authorize", "start", "codex", "validate", "review", "close",
    "close-cycle", "close-pi", "trace", "impact", "github-sync", "change",
    "maintain", "release", "verify", "doctor", "responsibilities", "completion",
)

COMMAND_COMPLETION_OPTIONS = {
    "plan": ("--title", "--objective"),
    "create-wc": ("--pi", "--title"),
    "create-wp": ("--wc", "--domain", "--title"),
    "authorize": ("--force", "--reason", "--by"),
    "codex": ("--force",),
    "close": ("--force", "--reason", "--by"),
    "close-cycle": ("--force", "--reason", "--by"),
    "close-pi": ("--force", "--reason", "--by"),
    "github-sync": ("--apply", "--project", "--owner"),
    "release": ("--publish", "--force"),
}


def completion_artifact_ids() -> list[str]:
    values: set[str] = set()
    for row in read_tsv(EOS / "artifacts.tsv"):
        if row.get("artifact_id"):
            values.add(row["artifact_id"])
    for kind in REGISTRY_PATHS:
        for row in registry(kind):
            if row.get("id"):
                values.add(row["id"])
    for base in (
        ROOT / "vision", ROOT / "product", ROOT / "architecture",
        ROOT / "specifications", ROOT / "engineering", ROOT / "research",
        ROOT / "governance", ROOT / "journal",
    ):
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            try:
                data, _ = parse_frontmatter(path)
            except OSError:
                continue
            if data.get("artifact_id"):
                values.add(data["artifact_id"])
    return sorted(values)


def completion_artifact_paths() -> list[str]:
    values: set[str] = set()
    for row in read_tsv(EOS / "artifacts.tsv"):
        if row.get("path"):
            values.add(row["path"])
    for kind in REGISTRY_PATHS:
        for row in registry(kind):
            if row.get("path"):
                values.add(row["path"])
    return sorted(v for v in values if (ROOT / v).exists())


def completion_ids(*kinds: str, states: set[str] | None = None) -> list[str]:
    out: list[str] = []
    for kind in kinds:
        for row in registry(kind):
            if states is None or row.get("status") in states:
                out.append(row["id"])
    return sorted(out)


def completion_stages() -> list[str]:
    return sorted(
        row.get("stage", "")
        for row in read_tsv(EOS / "workflow.tsv")
        if row.get("stage")
    )


def completion_snapshot_versions(path_text: str) -> list[str]:
    path = Path(path_text)
    base = EOS / "history" / path.with_suffix("")
    if not base.exists():
        return []
    suffix = path.suffix
    versions: list[str] = []
    for snap in base.glob(f"v*{suffix}"):
        name = snap.name
        if name.startswith("v") and name.endswith(suffix):
            versions.append(name[1 : -len(suffix)] if suffix else name[1:])
    return sorted(set(versions), key=lambda x: tuple(int(p) if p.isdigit() else 0 for p in x.split(".")))


def completion_release_versions() -> list[str]:
    versions: set[str] = set()
    for row in registry("REL"):
        if row.get("version"):
            versions.add(row["version"])
    version_file = ROOT / "VERSION"
    current = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "0.1.0"
    try:
        major, minor, patch = map(int, current.split("."))
        versions.update({
            f"{major}.{minor}.{patch + 1}",
            f"{major}.{minor + 1}.0",
            f"{major + 1}.0.0",
        })
    except ValueError:
        pass
    return sorted(versions)


def completion_domains() -> list[str]:
    defaults = {"CORE", "CLI", "API", "ENGINE", "UI", "DATA", "SECURITY", "OPS", "DOCS", "TOOLING"}
    for row in registry("WP"):
        if row.get("domain"):
            defaults.add(row["domain"].upper())
    return sorted(defaults)


def filter_completion(values: Iterable[str], prefix: str) -> list[str]:
    return sorted({v for v in values if v and v.startswith(prefix)})


def completion_candidates(words: list[str]) -> list[str]:
    if not words:
        return list(TOP_LEVEL_COMPLETION_COMMANDS)

    current = words[-1]
    if len(words) == 1:
        return filter_completion(TOP_LEVEL_COMPLETION_COMMANDS, current)

    command = words[0]
    args = words[1:]
    current = args[-1] if args else ""
    prior = args[:-1] if args else []

    if command == "change" and len(args) == 1:
        return filter_completion(("create", "approve", "close"), current)
    if command == "maintain" and len(args) == 1:
        return filter_completion(("create", "close"), current)
    if command == "completion" and len(args) == 1:
        return filter_completion(("bash", "zsh", "fish", "write", "install"), current)

    previous = prior[-1] if prior else ""
    if previous == "--pi":
        return filter_completion(completion_ids("PI"), current)
    if previous == "--wc":
        return filter_completion(completion_ids("WC"), current)
    if previous == "--domain":
        return filter_completion(completion_domains(), current.upper())
    if command == "completion" and args and args[0] == "install" and len(args) <= 2:
        return filter_completion(("bash", "zsh", "fish", "all"), current)

    if current.startswith("-") or (current == "" and command in COMMAND_COMPLETION_OPTIONS):
        options = [o for o in COMMAND_COMPLETION_OPTIONS.get(command, ()) if o not in args]
        if command == "change" and args:
            subcmd = args[0]
            if subcmd == "create":
                options += [o for o in ("--reason",) if o not in args]
            elif subcmd == "approve":
                options += [o for o in ("--force", "--reason", "--by") if o not in args]
        elif command == "maintain" and args:
            subcmd = args[0]
            if subcmd == "create":
                options += [o for o in ("--context",) if o not in args]
            elif subcmd == "close":
                options += [o for o in ("--force",) if o not in args]
        return filter_completion(options, current)

    if command in {"prompt", "complete", "reopen"}:
        return filter_completion(completion_stages(), current)
    if command == "version":
        positional = [a for a in args if not a.startswith("-")]
        if len(positional) <= 1:
            return filter_completion(completion_artifact_paths(), current)
        if len(positional) == 2:
            return filter_completion(("patch", "minor", "major"), current)
        return []
    if command == "history":
        return filter_completion(completion_artifact_paths(), current)
    if command == "rollback":
        positional = [a for a in args if not a.startswith("-")]
        if len(positional) <= 1:
            return filter_completion(completion_artifact_paths(), current)
        if len(positional) == 2:
            path_arg = next((a for a in args[:-1] if not a.startswith("-")), "")
            return filter_completion(completion_snapshot_versions(path_arg), current)
        return []
    if command == "plan":
        if not current.startswith("-") and not prior:
            next_id = f"PI-{next_number('PI', 3):03d}"
            return filter_completion([next_id], current)
        return []
    if command == "authorize":
        return filter_completion(completion_ids("PI", "WC", "WP"), current)
    if command == "start":
        return filter_completion(completion_ids("PI", "WC", "WP", "MNT"), current)
    if command == "codex":
        return filter_completion(completion_ids("WP"), current)
    if command in {"validate", "review"}:
        return filter_completion(completion_ids("PI", "WC", "WP", "CR", "MNT", "REL"), current)
    if command == "close":
        return filter_completion(completion_ids("WP"), current)
    if command == "close-cycle":
        return filter_completion(completion_ids("WC"), current)
    if command == "close-pi":
        return filter_completion(completion_ids("PI"), current)
    if command in {"trace", "impact"}:
        return filter_completion(completion_artifact_ids(), current)
    if command == "release":
        if not current.startswith("-") and not prior:
            return filter_completion(completion_release_versions(), current)
        return []

    if command == "change" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "create" and len(subargs) <= 1:
            return filter_completion(completion_artifact_ids(), subcurrent)
        if subcmd in {"approve", "close"} and len(subargs) <= 1:
            return filter_completion(completion_ids("CR"), subcurrent)
        return []

    if command == "maintain" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "create" and len(subargs) <= 1:
            return filter_completion(
                ("bug", "debt", "security", "dependency", "operations", "performance", "documentation"),
                subcurrent,
            )
        if subcmd == "close" and len(subargs) <= 1:
            return filter_completion(completion_ids("MNT"), subcurrent)
        return []

    return []


BASH_COMPLETION = r"""# Bash completion for repository-local EOS.
_eos_complete() {
  local cmd="${COMP_WORDS[0]}"
  local -a args
  local line
  COMPREPLY=()
  args=("${COMP_WORDS[@]:1}")
  while IFS= read -r line; do
    [[ -n "$line" ]] && COMPREPLY+=("$line")
  done < <("$cmd" completion candidates -- "${args[@]}" 2>/dev/null)
  if type compopt >/dev/null 2>&1; then
    compopt -o nosort 2>/dev/null || true
  fi
}
complete -o default -F _eos_complete eos ./scripts/eos scripts/eos
"""

ZSH_COMPLETION = r"""#compdef eos
# Zsh completion for repository-local EOS.
_eos() {
  local cmd="${words[1]}"
  local -a candidates argv_words
  argv_words=("${words[@]:1}")
  candidates=("${(@f)$("$cmd" completion candidates -- "${argv_words[@]}" 2>/dev/null)}")
  compadd -Q -- "${candidates[@]}"
}
compdef _eos eos
"""

FISH_COMPLETION = r"""# Fish completion for repository-local EOS.
function __eos_dynamic_complete
    set -l tokens (commandline -opc)
    set -l current (commandline -ct)
    if test (count $tokens) -eq 0
        return
    end
    set -l cmd $tokens[1]
    set -e tokens[1]
    command $cmd completion candidates -- $tokens $current 2>/dev/null
end
complete -c eos -f -a '(__eos_dynamic_complete)'
"""


def completion_script(shell: str) -> str:
    scripts = {"bash": BASH_COMPLETION, "zsh": ZSH_COMPLETION, "fish": FISH_COMPLETION}
    try:
        return scripts[shell]
    except KeyError as exc:
        raise EosError(f"Unsupported shell completion: {shell}") from exc


def write_completion_files() -> list[Path]:
    files = {
        ROOT / "completions" / "bash" / "eos": BASH_COMPLETION,
        ROOT / "completions" / "zsh" / "_eos": ZSH_COMPLETION,
        ROOT / "completions" / "fish" / "eos.fish": FISH_COMPLETION,
    }
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    readme = ROOT / "completions" / "README.md"
    readme.write_text(
        "# EOS Shell Completion\n\n"
        "The EOS provides dynamic completion for Bash, Zsh, and Fish. Candidate IDs "
        "are read from the live repository registries, so newly created PI/WC/WP, "
        "change, maintenance, release, and artifact IDs appear automatically.\n\n"
        "## Install\n\n"
        "```bash\n./scripts/eos completion install\n```\n\n"
        "The shell is inferred from `$SHELL`, or choose it explicitly:\n\n"
        "```bash\n"
        "./scripts/eos completion install bash\n"
        "./scripts/eos completion install zsh\n"
        "./scripts/eos completion install fish\n"
        "./scripts/eos completion install all\n"
        "```\n",
        encoding="utf-8",
    )
    return [*files, readme]


def install_completion(shell: str) -> list[Path]:
    home = Path.home()
    shells = ("bash", "zsh", "fish") if shell == "all" else (shell,)
    installed: list[Path] = []
    for item in shells:
        if item == "bash":
            dest = home / ".local" / "share" / "bash-completion" / "completions" / "eos"
        elif item == "zsh":
            dest = home / ".zfunc" / "_eos"
        elif item == "fish":
            dest = home / ".config" / "fish" / "completions" / "eos.fish"
        else:
            raise EosError(f"Unsupported shell: {item}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(completion_script(item), encoding="utf-8")
        installed.append(dest)
    return installed


def cmd_completion(args: argparse.Namespace) -> None:
    action = args.completion_command
    if action in {"bash", "zsh", "fish"}:
        print(completion_script(action), end="")
        return
    if action == "write":
        for path in write_completion_files():
            print(rel(path))
        return
    if action == "install":
        shell = args.shell
        if not shell:
            shell = Path(os.environ.get("SHELL", "")).name
            if shell not in {"bash", "zsh", "fish"}:
                raise EosError("Could not infer shell; specify bash, zsh, fish, or all")
        for path in install_completion(shell):
            print(f"Installed: {path}")
        if shell in {"zsh", "all"}:
            print("Zsh: ensure ~/.zfunc is in fpath before compinit, e.g. fpath=(~/.zfunc $fpath).")
        print("Start a new shell (or reload its completion system) to activate completion.")
        return
    if action == "candidates":
        words = list(args.words)
        if words and words[0] == "--":
            words = words[1:]
        for value in completion_candidates(words):
            print(value)
        return
    raise EosError(f"Unknown completion action: {action}")


def cmd_responsibilities(_: argparse.Namespace) -> None:
    print((ROOT / "governance" / "responsibility-model.md").read_text(encoding="utf-8"))


def add_override_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--force", action="store_true", help="Explicit human gate override")
    parser.add_argument("--reason", default="", help="Reason for action or override")
    parser.add_argument("--by", default="", help="Human actor/approver identity")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="./scripts/eos", description="Engineering Operating System")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("layers", help="Show permanent EOS operating layers")
    p.set_defaults(func=cmd_layers)

    p = sub.add_parser("status", help="Show bootstrap and permanent lifecycle status")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("next", help="Show the next recommended lifecycle action")
    p.set_defaults(func=cmd_next)

    p = sub.add_parser("prompt", help="Render an EOSB prompt with project context")
    p.add_argument("stage")
    p.set_defaults(func=cmd_prompt)

    p = sub.add_parser("complete", help="Mark an EOSB stage complete")
    p.add_argument("stage")
    p.set_defaults(func=cmd_complete)

    p = sub.add_parser("reopen", help="Reopen an EOSB stage")
    p.add_argument("stage")
    p.set_defaults(func=cmd_reopen)

    p = sub.add_parser("version", help="Version a governed artifact")
    p.add_argument("path")
    p.add_argument("kind", choices=("patch", "minor", "major"))
    p.add_argument("message")
    p.set_defaults(func=cmd_version)

    p = sub.add_parser("history", help="Show semantic and Git history for an artifact")
    p.add_argument("path")
    p.set_defaults(func=cmd_history)

    p = sub.add_parser("rollback", help="Restore historical content as a new version")
    p.add_argument("path")
    p.add_argument("version")
    p.add_argument("message")
    p.set_defaults(func=cmd_rollback)

    p = sub.add_parser("checkpoint", help="Commit and tag a coherent repository checkpoint")
    p.add_argument("message")
    p.set_defaults(func=cmd_checkpoint)

    p = sub.add_parser("plan", help="Create the next program increment")
    p.add_argument("pi", nargs="?")
    p.add_argument("--title", default="")
    p.add_argument("--objective", default="")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("create-wc", help="Create a work cycle")
    p.add_argument("--pi", default="")
    p.add_argument("--title", default="")
    p.set_defaults(func=cmd_create_wc)

    p = sub.add_parser("create-wp", help="Create a work packet")
    p.add_argument("--wc", default="")
    p.add_argument("--domain", default="")
    p.add_argument("--title", default="")
    p.set_defaults(func=cmd_create_wp)

    p = sub.add_parser("authorize", help="Authorize a PI, WC, or WP after gate checks")
    p.add_argument("target")
    add_override_args(p)
    p.set_defaults(func=cmd_authorize)

    p = sub.add_parser("start", help="Start authorized work")
    p.add_argument("target")
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("codex", help="Generate a bounded Codex execution contract")
    p.add_argument("target")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_codex)

    p = sub.add_parser("validate", help="Run deterministic verification for a target")
    p.add_argument("target")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("review", help="Generate review artifact + automated evidence")
    p.add_argument("target")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("close", help="Close an accepted work packet")
    p.add_argument("target")
    add_override_args(p)
    p.set_defaults(func=cmd_close)

    p = sub.add_parser("close-cycle", help="Close a work cycle after child/review gates")
    p.add_argument("target")
    add_override_args(p)
    p.set_defaults(func=cmd_close_cycle)

    p = sub.add_parser("close-pi", help="Close a program increment after child/review gates")
    p.add_argument("target")
    add_override_args(p)
    p.set_defaults(func=cmd_close_pi)

    p = sub.add_parser("trace", help="Show direct traceability for an artifact ID")
    p.add_argument("target")
    p.set_defaults(func=cmd_trace)

    p = sub.add_parser("impact", help="Show transitive downstream impact of an artifact")
    p.add_argument("target")
    p.set_defaults(func=cmd_impact)

    p = sub.add_parser("github-sync", help="Synchronize EOS planning state to GitHub")
    p.add_argument("--apply", action="store_true", help="Actually create/update GitHub objects")
    p.add_argument("--project", default="", help="Optional GitHub Project number to add synced issues to")
    p.add_argument("--owner", default="", help="GitHub organization/user owning --project (defaults to repo owner)")
    p.set_defaults(func=cmd_github_sync)

    change = sub.add_parser("change", help="Govern architecture/requirements/specification changes")
    change_sub = change.add_subparsers(dest="change_command", required=True)
    p = change_sub.add_parser("create")
    p.add_argument("target")
    p.add_argument("summary")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_change_create)
    p = change_sub.add_parser("approve")
    p.add_argument("target")
    add_override_args(p)
    p.set_defaults(func=cmd_change_approve)
    p = change_sub.add_parser("close")
    p.add_argument("target")
    p.set_defaults(func=cmd_change_close)

    maintain = sub.add_parser("maintain", help="Create/close maintenance work")
    maintain_sub = maintain.add_subparsers(dest="maintain_command", required=True)
    p = maintain_sub.add_parser("create")
    p.add_argument("type", choices=("bug", "debt", "security", "dependency", "operations", "performance", "documentation"))
    p.add_argument("summary")
    p.add_argument("--context", default="")
    p.set_defaults(func=cmd_maintain_create)
    p = maintain_sub.add_parser("close")
    p.add_argument("target")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_maintain_close)

    p = sub.add_parser("release", help="Prepare/finalize a governed release")
    p.add_argument("version")
    p.add_argument("--publish", action="store_true", help="Push and create GitHub Release")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_release)

    p = sub.add_parser("verify", help="Verify EOS registry/state/traceability integrity")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("doctor", help="Check local EOS dependencies and repository state")
    p.set_defaults(func=cmd_doctor)

    completion = sub.add_parser("completion", help="Generate/install dynamic shell tab completion")
    completion_sub = completion.add_subparsers(dest="completion_command", required=True)
    for shell_name in ("bash", "zsh", "fish"):
        p = completion_sub.add_parser(shell_name, help=f"Print {shell_name} completion script")
        p.set_defaults(func=cmd_completion)
    p = completion_sub.add_parser("write", help="Write repository-local completion files")
    p.set_defaults(func=cmd_completion)
    p = completion_sub.add_parser("install", help="Install completion into the user shell completion directory")
    p.add_argument("shell", nargs="?", choices=("bash", "zsh", "fish", "all"))
    p.set_defaults(func=cmd_completion)
    p = completion_sub.add_parser("candidates", help=argparse.SUPPRESS)
    p.add_argument("words", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_completion)

    p = sub.add_parser("responsibilities", help="Show Human/ChatGPT/Codex/GitHub responsibilities")
    p.set_defaults(func=cmd_responsibilities)

    return parser


def main() -> int:
    ensure_dirs()
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except EosError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: command failed ({exc.returncode}): {' '.join(exc.cmd)}", file=sys.stderr)
        if exc.stdout:
            print(exc.stdout, file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return exc.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
EOS_PY
chmod +x tools/eos/eos.py

# Generate repository-local dynamic shell completion scripts. Installation into
# the user's shell is intentionally explicit via `./scripts/eos completion install`.
if [[ -x scripts/eos ]] && grep -q 'tools/eos/eos.py' scripts/eos 2>/dev/null; then
  ./scripts/eos completion write >/dev/null
fi

# Seed initial semantic snapshots for newly introduced lifecycle artifacts.
while IFS=$'\t' read -r id path type authority; do
  [[ "$id" == "artifact_id" ]] && continue
  [[ -f "$path" ]] || continue
  version="$(awk -F': ' 'NR <= 40 && $1 == "version" {gsub(/"/,"",$2); print $2; exit}' "$path")"
  [[ -n "$version" ]] || continue
  noext="${path%.*}"
  ext="${path##*.}"
  snap=".eos/history/$noext/v$version.$ext"
  if [[ ! -e "$snap" ]]; then
    mkdir -p "$(dirname "$snap")"
    cp "$path" "$snap"
  fi
done < .eos/artifacts.tsv

# The full-lifecycle engine supersedes the earlier bootstrap-only verification.
if [[ -x scripts/eos ]] && grep -q 'tools/eos/eos.py' scripts/eos 2>/dev/null; then
  ./scripts/eos verify
fi

cat <<'EOF'

===============================================================================
Permanent Engineering Operating System enabled
===============================================================================

EOSB — Bootstrap
EOSP — Planning
EOSE — Execution
EOSV — Verification
EOSR — Review
EOSC — Change Control
EOSL — Release Lifecycle
EOSM — Maintenance

Inspect the complete control plane:

  ./scripts/eos doctor
  ./scripts/eos layers
  ./scripts/eos status
  ./scripts/eos next

Enable dynamic tab completion (Bash/Zsh/Fish):

  ./scripts/eos completion install

Or inspect/source repository-local completion files under `completions/`.

After EOSB-020, continue directly into the permanent lifecycle, for example:

  ./scripts/eos plan PI-002
  ./scripts/eos create-wc --pi PI-002
  ./scripts/eos create-wp --wc WC-0002 --domain CORE
  ./scripts/eos authorize WP-CORE-0001
  ./scripts/eos start WP-CORE-0001
  ./scripts/eos codex WP-CORE-0001
  ./scripts/eos validate WP-CORE-0001
  ./scripts/eos review WP-CORE-0001
  ./scripts/eos close WP-CORE-0001
  ./scripts/eos trace REQ-0042
  ./scripts/eos impact ADR-0014
  ./scripts/eos github-sync
  ./scripts/eos release 0.1.0

Git remains the authoritative history for every tracked file.
===============================================================================
EOF
