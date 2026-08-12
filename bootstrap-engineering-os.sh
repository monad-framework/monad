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
