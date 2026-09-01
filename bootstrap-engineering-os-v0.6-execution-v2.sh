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

MANAGED_BACKUP_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
MANAGED_BACKUP_ROOT=".eos/history/managed/$MANAGED_BACKUP_STAMP"

write_managed_file() {
  local path="$1"
  local tmp
  tmp="$(mktemp)"
  cat >"$tmp"
  mkdir -p "$(dirname "$path")"

  if [[ -e "$path" ]]; then
    if cmp -s "$tmp" "$path"; then
      rm -f "$tmp"
      return
    fi
    local backup="$MANAGED_BACKUP_ROOT/$path"
    mkdir -p "$(dirname "$backup")"
    cp -a "$path" "$backup"
    mv "$tmp" "$path"
    log "Updated EOS-managed file: $path (backup: $backup)"
  else
    mv "$tmp" "$path"
    log "Created EOS-managed file: $path"
  fi
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
  ".eos/schemas"
  ".eos/state-machines"
  ".eos/policies"
  ".eos/cache"
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

## Execution Scope

EOSE blocks Git/EOS internals and governed-artifact changes by default. Add
`allowed-path`, `forbidden-path`, or `allowed-governed-path` directives when this
work packet requires a more explicit machine-enforced file boundary.

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
# EOS canonical domain model, schemas, declarative state machines, event ledger
# ------------------------------------------------------------------------------

PREVIOUS_EOS_TOOL_VERSION=""
if [[ -f .eos/version.json ]] && command -v python3 >/dev/null 2>&1; then
  PREVIOUS_EOS_TOOL_VERSION="$(
    python3 - <<'PY' 2>/dev/null || true
import json
from pathlib import Path
try:
    print(json.loads(Path(".eos/version.json").read_text()).get("eos_tool_version", ""))
except Exception:
    pass
PY
  )"
fi
export EOS_PREVIOUS_TOOL_VERSION="$PREVIOUS_EOS_TOOL_VERSION"


write_managed_file ".eos/version.json" <<'EOF'
{
  "eos_tool_version": "0.6.0",
  "eos_schema_version": "1.0.0",
  "event_schema_version": "1.0.0",
  "state_machine_version": "1.0.0"
}
EOF

write_managed_file ".eos/domain-model.json" <<'EOF'
{
  "schema_version": "1.0.0",
  "description": "Canonical EOS engineering domain model.",
  "identity": {
    "immutable_ids": true,
    "reuse_forbidden": true,
    "namespaces": {
      "PI": "^PI-[0-9]{3}$",
      "WC": "^WC-[0-9]{4}$",
      "WP": "^WP(?:-[A-Z][A-Z0-9]{1,15})?-[0-9]{4}$",
      "CR": "^CR-[0-9]{4}$",
      "MNT": "^MNT-[0-9]{4}$",
      "REL": "^REL-[0-9]+\\.[0-9]+\\.[0-9]+$",
      "EXEC": "^EXEC-[0-9]{4}$",
      "REQ": "^REQ-[A-Z0-9][A-Z0-9-]*$",
      "CAP": "^CAP-[A-Z0-9][A-Z0-9-]*$",
      "QA": "^QA-[A-Z0-9][A-Z0-9-]*$",
      "ADR": "^ADR-[0-9]{4}$",
      "SPEC": "^SPEC-[A-Z0-9][A-Z0-9-]*$",
      "RISK": "^RISK-[0-9]{3,4}$"
    }
  },
  "entities": {
    "PI": {
      "name": "Program Increment",
      "registry": ".eos/program-increments.tsv",
      "schema": ".eos/schemas/pi.schema.json",
      "state_machine": ".eos/state-machines/pi.json",
      "parent": null
    },
    "WC": {
      "name": "Work Cycle",
      "registry": ".eos/work-cycles.tsv",
      "schema": ".eos/schemas/wc.schema.json",
      "state_machine": ".eos/state-machines/wc.json",
      "parent": "PI"
    },
    "WP": {
      "name": "Work Packet",
      "registry": ".eos/work-packets.tsv",
      "schema": ".eos/schemas/wp.schema.json",
      "state_machine": ".eos/state-machines/wp.json",
      "parent": "WC"
    },
    "CR": {
      "name": "Change Request",
      "registry": ".eos/change-requests.tsv",
      "schema": ".eos/schemas/cr.schema.json",
      "state_machine": ".eos/state-machines/cr.json",
      "parent": null
    },
    "MNT": {
      "name": "Maintenance Item",
      "registry": ".eos/maintenance.tsv",
      "schema": ".eos/schemas/mnt.schema.json",
      "state_machine": ".eos/state-machines/mnt.json",
      "parent": null
    },
    "REL": {
      "name": "Release",
      "registry": ".eos/releases.tsv",
      "schema": ".eos/schemas/rel.schema.json",
      "state_machine": ".eos/state-machines/rel.json",
      "parent": null
    },
    "EXEC": {
      "name": "Execution Session",
      "registry": ".eos/executions.tsv",
      "schema": ".eos/schemas/exec.schema.json",
      "state_machine": ".eos/state-machines/exec.json",
      "parent": "WP"
    }
  },
  "authority": {
    "human": "Final authority for mission, material risk acceptance, authorization gates, and irreversible external actions.",
    "chatgpt": "Reasoning, synthesis, planning, artifact drafting, conformance analysis, and review recommendation.",
    "codex": "Bounded repository-local implementation and deterministic validation under an authorized execution contract.",
    "github": "Canonical remote collaboration surface, Git history mirror, CI/review integration, issue/project/release projection.",
    "git": "Authoritative version history for tracked repository files."
  },
  "canonical_state": {
    "event_ledger": ".eos/events.jsonl",
    "operational_projection": "TSV lifecycle registries",
    "human_projection": "governed Markdown front matter and State line",
    "rule": "Lifecycle mutations must be represented as append-only events and then projected atomically to registries and governed artifacts."
  }
}
EOF

# JSON Schema files intentionally use a small, dependency-free subset that the
# EOS stdlib validator understands while remaining valid JSON Schema documents.
write_managed_file ".eos/schemas/pi.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "eos://schemas/pi/1.0.0",
  "type": "object",
  "required": ["id", "path", "title", "status", "created", "updated"],
  "properties": {
    "id": {"type": "string", "pattern": "^PI-[0-9]{3}$"},
    "path": {"type": "string", "minLength": 1},
    "title": {"type": "string", "minLength": 1},
    "status": {"type": "string"},
    "created": {"type": "string", "minLength": 1},
    "updated": {"type": "string", "minLength": 1},
    "github_url": {"type": "string"}
  },
  "additionalProperties": false
}
EOF

write_managed_file ".eos/schemas/wc.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "eos://schemas/wc/1.0.0",
  "type": "object",
  "required": ["id", "path", "title", "status", "pi", "created", "updated"],
  "properties": {
    "id": {"type": "string", "pattern": "^WC-[0-9]{4}$"},
    "path": {"type": "string", "minLength": 1},
    "title": {"type": "string", "minLength": 1},
    "status": {"type": "string"},
    "pi": {"type": "string", "pattern": "^PI-[0-9]{3}$"},
    "created": {"type": "string", "minLength": 1},
    "updated": {"type": "string", "minLength": 1},
    "github_url": {"type": "string"}
  },
  "additionalProperties": false
}
EOF

write_managed_file ".eos/schemas/wp.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "eos://schemas/wp/1.0.0",
  "type": "object",
  "required": ["id", "path", "title", "status", "pi", "wc", "domain", "created", "updated"],
  "properties": {
    "id": {"type": "string", "pattern": "^WP(?:-[A-Z][A-Z0-9]{1,15})?-[0-9]{4}$"},
    "path": {"type": "string", "minLength": 1},
    "title": {"type": "string", "minLength": 1},
    "status": {"type": "string"},
    "pi": {"type": "string", "pattern": "^PI-[0-9]{3}$"},
    "wc": {"type": "string", "pattern": "^WC-[0-9]{4}$"},
    "domain": {"type": "string"},
    "created": {"type": "string", "minLength": 1},
    "updated": {"type": "string", "minLength": 1},
    "github_url": {"type": "string"}
  },
  "additionalProperties": false
}
EOF

write_managed_file ".eos/schemas/cr.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "eos://schemas/cr/1.0.0",
  "type": "object",
  "required": ["id", "path", "target", "summary", "status", "created", "updated"],
  "properties": {
    "id": {"type": "string", "pattern": "^CR-[0-9]{4}$"},
    "path": {"type": "string", "minLength": 1},
    "target": {"type": "string", "minLength": 1},
    "summary": {"type": "string", "minLength": 1},
    "status": {"type": "string"},
    "created": {"type": "string", "minLength": 1},
    "updated": {"type": "string", "minLength": 1},
    "github_url": {"type": "string"}
  },
  "additionalProperties": false
}
EOF

write_managed_file ".eos/schemas/mnt.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "eos://schemas/mnt/1.0.0",
  "type": "object",
  "required": ["id", "path", "type", "summary", "status", "created", "updated"],
  "properties": {
    "id": {"type": "string", "pattern": "^MNT-[0-9]{4}$"},
    "path": {"type": "string", "minLength": 1},
    "type": {"type": "string", "minLength": 1},
    "summary": {"type": "string", "minLength": 1},
    "status": {"type": "string"},
    "created": {"type": "string", "minLength": 1},
    "updated": {"type": "string", "minLength": 1},
    "github_url": {"type": "string"}
  },
  "additionalProperties": false
}
EOF

write_managed_file ".eos/schemas/rel.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "eos://schemas/rel/1.0.0",
  "type": "object",
  "required": ["id", "path", "version", "status", "created", "updated"],
  "properties": {
    "id": {"type": "string", "pattern": "^REL-[0-9]+\\.[0-9]+\\.[0-9]+$"},
    "path": {"type": "string", "minLength": 1},
    "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
    "status": {"type": "string"},
    "created": {"type": "string", "minLength": 1},
    "updated": {"type": "string", "minLength": 1},
    "github_url": {"type": "string"}
  },
  "additionalProperties": false
}
EOF

write_managed_file ".eos/schemas/exec.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "eos://schemas/exec/1.0.0",
  "type": "object",
  "required": ["id", "path", "target", "status", "branch", "worktree", "baseline_commit", "governing_hash", "contract_hash", "created", "updated"],
  "properties": {
    "id": {"type": "string", "pattern": "^EXEC-[0-9]{4}$"},
    "path": {"type": "string", "minLength": 1},
    "target": {"type": "string", "pattern": "^WP(?:-[A-Z][A-Z0-9]{1,15})?-[0-9]{4}$"},
    "status": {"type": "string"},
    "branch": {"type": "string"},
    "worktree": {"type": "string"},
    "baseline_commit": {"type": "string"},
    "governing_hash": {"type": "string"},
    "contract_hash": {"type": "string"},
    "result_path": {"type": "string"},
    "actor": {"type": "string"},
    "created": {"type": "string", "minLength": 1},
    "updated": {"type": "string", "minLength": 1}
  },
  "additionalProperties": false
}
EOF

write_managed_file ".eos/schemas/artifact.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "eos://schemas/artifact/1.0.0",
  "type": "object",
  "required": ["artifact_id", "title", "type", "version", "status", "authority", "created", "updated"],
  "properties": {
    "artifact_id": {"type": "string", "minLength": 1},
    "title": {"type": "string", "minLength": 1},
    "type": {"type": "string", "minLength": 1},
    "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
    "status": {"type": "string", "minLength": 1},
    "authority": {"type": "string", "minLength": 1},
    "created": {"type": "string", "minLength": 1},
    "updated": {"type": "string", "minLength": 1}
  }
}
EOF

write_managed_file ".eos/schemas/event.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "eos://schemas/event/1.0.0",
  "type": "object",
  "required": ["event_id", "schema_version", "timestamp", "event_type", "actor"],
  "properties": {
    "event_id": {"type": "string", "pattern": "^EVT-[0-9A-F]{32}$"},
    "schema_version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
    "timestamp": {"type": "string", "minLength": 1},
    "event_type": {"type": "string", "minLength": 1},
    "actor": {"type": "string", "minLength": 1},
    "target": {"type": "string"},
    "entity_kind": {"type": "string"},
    "action": {"type": "string"},
    "from_state": {"type": "string"},
    "to_state": {"type": "string"},
    "reason": {"type": "string"},
    "commit": {"type": "string"},
    "metadata": {"type": "object"}
  }
}
EOF

write_managed_file ".eos/schemas/override.schema.json" <<'EOF'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "eos://schemas/override/1.0.0",
  "type": "object",
  "required": ["id", "target", "gate", "status", "actor", "reason", "created", "expires", "consumed_at"],
  "properties": {
    "id": {"type": "string", "pattern": "^OVR-[0-9]{4}$"},
    "target": {"type": "string", "minLength": 1},
    "gate": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]+$"},
    "status": {"type": "string"},
    "actor": {"type": "string", "minLength": 1},
    "reason": {"type": "string", "minLength": 1},
    "created": {"type": "string", "minLength": 1},
    "expires": {"type": "string"},
    "consumed_at": {"type": "string"}
  },
  "additionalProperties": false
}
EOF

write_managed_file ".eos/policies/core.json" <<'EOF'
{
  "policy_version": "1.0.0",
  "description": "Core named EOS lifecycle gates. Checks are declarative references to deterministic built-in predicates.",
  "gates": {
    "PI_READY": [
      {"check": "state_is", "value": "DRAFT"},
      {"check": "artifact_complete"}
    ],
    "WC_READY": [
      {"check": "state_is", "value": "DRAFT"},
      {"check": "artifact_complete"}
    ],
    "WP_READY": [
      {"check": "state_is", "value": "DRAFT"},
      {"check": "artifact_complete"}
    ],
    "PI_AUTHORIZE": [
      {"check": "state_is", "value": "IN_REVIEW"},
      {"check": "artifact_complete"},
      {"check": "pi_readiness_review_accepted"}
    ],
    "WC_AUTHORIZE": [
      {"check": "state_is", "value": "READY"},
      {"check": "artifact_complete"},
      {"check": "parent_state", "values": ["AUTHORIZED", "ACTIVE"]}
    ],
    "WP_AUTHORIZE": [
      {"check": "state_is", "value": "READY"},
      {"check": "artifact_complete"},
      {"check": "parent_state", "values": ["AUTHORIZED", "ACTIVE"]}
    ],
    "WP_CLOSE": [
      {"check": "state_is", "value": "IN_REVIEW"},
      {"check": "artifact_complete"},
      {"check": "no_unchecked_items"},
      {"check": "review_accepted"}
    ],
    "WC_CLOSE": [
      {"check": "state_is", "value": "IN_REVIEW"},
      {"check": "artifact_complete"},
      {"check": "has_children"},
      {"check": "children_closed"},
      {"check": "review_accepted"}
    ],
    "PI_CLOSE": [
      {"check": "state_is", "value": "IN_REVIEW"},
      {"check": "artifact_complete"},
      {"check": "has_children"},
      {"check": "children_closed"},
      {"check": "pi_closeout_review_accepted"}
    ],
    "CR_APPROVE": [
      {"check": "state_is", "value": "PROPOSED"},
      {"check": "artifact_complete"},
      {"check": "change_decision_approved"}
    ],
    "MNT_CLOSE": [
      {"check": "state_is", "value": "VERIFYING"},
      {"check": "artifact_complete"},
      {"check": "no_unchecked_items"}
    ]
  }
}
EOF

write_managed_file ".eos/state-machines/pi.json" <<'EOF'
{
  "kind": "PI",
  "version": "1.0.0",
  "initial_state": "DRAFT",
  "terminal_states": ["CLOSED"],
  "states": ["DRAFT", "PLANNED", "IN_REVIEW", "AUTHORIZED", "ACTIVE", "BLOCKED", "CLOSED"],
  "transitions": {
    "DRAFT": ["PLANNED", "BLOCKED"],
    "PLANNED": ["IN_REVIEW", "BLOCKED"],
    "IN_REVIEW": ["AUTHORIZED", "CLOSED", "BLOCKED"],
    "AUTHORIZED": ["ACTIVE", "BLOCKED"],
    "ACTIVE": ["IN_REVIEW", "BLOCKED"],
    "BLOCKED": ["PLANNED", "IN_REVIEW", "AUTHORIZED", "ACTIVE"],
    "CLOSED": []
  }
}
EOF

write_managed_file ".eos/state-machines/wc.json" <<'EOF'
{
  "kind": "WC",
  "version": "1.0.0",
  "initial_state": "DRAFT",
  "terminal_states": ["CLOSED"],
  "states": ["DRAFT", "READY", "AUTHORIZED", "ACTIVE", "IN_REVIEW", "BLOCKED", "CLOSED"],
  "transitions": {
    "DRAFT": ["READY", "BLOCKED"],
    "READY": ["AUTHORIZED", "BLOCKED"],
    "AUTHORIZED": ["ACTIVE", "BLOCKED"],
    "ACTIVE": ["IN_REVIEW", "BLOCKED"],
    "IN_REVIEW": ["CLOSED", "BLOCKED"],
    "BLOCKED": ["READY", "AUTHORIZED", "ACTIVE", "IN_REVIEW"],
    "CLOSED": []
  }
}
EOF

write_managed_file ".eos/state-machines/wp.json" <<'EOF'
{
  "kind": "WP",
  "version": "1.0.0",
  "initial_state": "DRAFT",
  "terminal_states": ["CLOSED"],
  "states": ["DRAFT", "READY", "AUTHORIZED", "IN_PROGRESS", "VERIFYING", "IN_REVIEW", "BLOCKED", "CLOSED"],
  "transitions": {
    "DRAFT": ["READY", "BLOCKED"],
    "READY": ["AUTHORIZED", "BLOCKED"],
    "AUTHORIZED": ["IN_PROGRESS", "BLOCKED"],
    "IN_PROGRESS": ["VERIFYING", "BLOCKED"],
    "VERIFYING": ["IN_REVIEW", "BLOCKED"],
    "IN_REVIEW": ["CLOSED", "BLOCKED"],
    "BLOCKED": ["READY", "AUTHORIZED", "IN_PROGRESS", "VERIFYING", "IN_REVIEW"],
    "CLOSED": []
  }
}
EOF

write_managed_file ".eos/state-machines/exec.json" <<'EOF'
{
  "kind": "EXEC",
  "version": "1.0.0",
  "initial_state": "PREPARED",
  "terminal_states": ["CLOSED", "ABORTED", "FAILED", "INVALIDATED"],
  "states": ["PREPARED", "RUNNING", "RESULT_INGESTED", "VERIFIED", "BLOCKED", "FAILED", "INVALIDATED", "ABORTED", "CLOSED"],
  "transitions": {
    "PREPARED": ["RUNNING", "ABORTED", "INVALIDATED"],
    "RUNNING": ["RESULT_INGESTED", "BLOCKED", "FAILED", "ABORTED", "INVALIDATED"],
    "RESULT_INGESTED": ["VERIFIED", "BLOCKED", "FAILED", "INVALIDATED"],
    "VERIFIED": ["CLOSED", "INVALIDATED"],
    "BLOCKED": ["RUNNING", "ABORTED", "INVALIDATED"],
    "FAILED": [],
    "INVALIDATED": [],
    "ABORTED": [],
    "CLOSED": []
  }
}
EOF

write_managed_file ".eos/state-machines/cr.json" <<'EOF'
{
  "kind": "CR",
  "version": "1.0.0",
  "initial_state": "PROPOSED",
  "terminal_states": ["CLOSED", "REJECTED"],
  "states": ["DRAFT", "PROPOSED", "APPROVED", "APPLIED", "CLOSED", "REJECTED"],
  "transitions": {
    "DRAFT": ["PROPOSED", "REJECTED"],
    "PROPOSED": ["APPROVED", "REJECTED"],
    "APPROVED": ["APPLIED", "REJECTED"],
    "APPLIED": ["CLOSED"],
    "CLOSED": [],
    "REJECTED": []
  }
}
EOF

write_managed_file ".eos/state-machines/mnt.json" <<'EOF'
{
  "kind": "MNT",
  "version": "1.0.0",
  "initial_state": "OPEN",
  "terminal_states": ["CLOSED", "DEFERRED"],
  "states": ["OPEN", "PLANNED", "IN_PROGRESS", "VERIFYING", "CLOSED", "DEFERRED"],
  "transitions": {
    "OPEN": ["PLANNED", "DEFERRED"],
    "PLANNED": ["IN_PROGRESS", "DEFERRED"],
    "IN_PROGRESS": ["VERIFYING", "DEFERRED"],
    "VERIFYING": ["CLOSED", "IN_PROGRESS"],
    "CLOSED": [],
    "DEFERRED": ["PLANNED"]
  }
}
EOF

write_managed_file ".eos/state-machines/rel.json" <<'EOF'
{
  "kind": "REL",
  "version": "1.0.0",
  "initial_state": "PROPOSED",
  "terminal_states": ["RELEASED", "WITHDRAWN"],
  "states": ["PROPOSED", "READY", "RELEASED", "WITHDRAWN"],
  "transitions": {
    "PROPOSED": ["READY", "WITHDRAWN"],
    "READY": ["RELEASED", "WITHDRAWN"],
    "RELEASED": [],
    "WITHDRAWN": []
  }
}
EOF

[[ -e .eos/events.jsonl ]] || : > .eos/events.jsonl

write_artifact "governance/canonical-state-model.md" "GOV-STATE-0001" "Canonical EOS State Model" "governance" "governance-authoritative" <<'EOF'
# Canonical EOS State Model

## Rule

EOS lifecycle state is changed through **append-only events** and projected into
human- and machine-readable representations.

## Representations

1. `.eos/events.jsonl` — append-only lifecycle/audit event ledger.
2. `.eos/*.tsv` lifecycle registries — current operational projections.
3. governed Markdown artifacts — human-readable projection with front-matter
   status and a visible `**State:**` line where applicable.
4. Git — authoritative repository version history.
5. GitHub — synchronized collaboration projection, never a silent replacement
   for EOS engineering meaning.

## Mutation Invariant

A lifecycle command must:

1. validate the requested transition against the declarative state machine;
2. append an event describing the mutation;
3. update the current registry projection;
4. update the governed artifact projection;
5. leave the repository in a state that `./scripts/eos verify --strict` can
   validate.

Direct manual edits to operational registries are discouraged because they
bypass the audit ledger.

## Reconstruction

`./scripts/eos rebuild-state` replays lifecycle events and compares the derived
state with current registries. `--apply` is an explicit repair operation.
EOF

write_artifact "governance/event-ledger.md" "GOV-EVENTS-0001" "EOS Event Ledger Policy" "governance" "governance-authoritative" <<'EOF'
# EOS Event Ledger Policy

`.eos/events.jsonl` is an append-only audit stream for lifecycle mutations.

Each event records:

- immutable event ID;
- schema version;
- timestamp;
- event type;
- actor;
- target;
- entity kind;
- action;
- prior state;
- resulting state;
- reason;
- Git commit when available;
- structured metadata.

Existing lines must never be rewritten as a normal lifecycle operation.
Corrections are represented by later events.

The event ledger complements Git rather than replacing Git.
EOF


write_artifact "governance/policy-engine.md" "GOV-POLICY-0001" "EOS Policy-as-Code and Gate Model" "governance" "governance-authoritative" <<'EOF'
# EOS Policy-as-Code and Gate Model

EOS lifecycle decisions are governed by **named gates** defined in
`.eos/policies/core.json`.

A gate consists of deterministic predicates such as:

- current lifecycle state;
- artifact completeness;
- parent authorization state;
- accepted review evidence;
- child closure state;
- unchecked acceptance items.

Use:

```bash
./scripts/eos policy list
./scripts/eos policy show WP_AUTHORIZE
./scripts/eos gate check WP_AUTHORIZE WP-CORE-0007
./scripts/eos gate explain WP_AUTHORIZE WP-CORE-0007
```

Gate failures must identify the exact failed predicate and evidence.

Policy files are versioned repository content. EOS does not evaluate arbitrary
code from policy definitions; policies reference a constrained built-in
predicate vocabulary.
EOF

write_artifact "governance/override-policy.md" "GOV-OVERRIDE-0001" "EOS Human Override Policy" "governance" "governance-authoritative" <<'EOF'
# EOS Human Override Policy

Human authority may accept a failed **gate**, but may not create an illegal
lifecycle transition.

Overrides are durable, explicit, scoped, and auditable.

Each override records:

- stable `OVR-*` ID;
- target;
- named gate;
- human actor;
- reason;
- creation time;
- optional expiration;
- consumption time.

Use:

```bash
./scripts/eos override create WP-CORE-0007 WP_AUTHORIZE \
  --by "Thomas Carter" \
  --reason "Explicitly accept the documented residual risk"

./scripts/eos override list
```

Legacy command `--force` remains available for convenience, but it creates and
consumes a durable override record and therefore requires an explicit reason.
It never bypasses the declarative state machine.
EOF

write_artifact "governance/traceability-graph.md" "GOV-TRACE-GRAPH-0001" "EOS Semantic Traceability Graph" "governance" "governance-authoritative" <<'EOF'
# EOS Semantic Traceability Graph

EOS maintains a typed, rebuildable engineering graph in
`.eos/trace-edges.tsv`.

## Core Edge Types

- `contains`
- `implements`
- `satisfies`
- `depends-on`
- `conforms-to`
- `constrained-by`
- `affects`
- `includes`
- `references`

Explicit Markdown relations may be declared as:

```markdown
- implements: REQ-0042
- depends-on: WP-CORE-0006
- conforms-to: ADR-0014
- satisfies: SPEC-CORE-0007
```

Where no explicit relation is present, EOS applies deterministic type inference
from the source and target artifact namespaces.

## Commands

```bash
./scripts/eos trace REQ-0042
./scripts/eos trace coverage
./scripts/eos impact ADR-0014
./scripts/eos stale list
```

When a governed artifact is versioned or rolled back, EOS marks known downstream
dependents stale for review. `verify --strict` fails while unresolved stale
records remain.
EOF

write_artifact "governance/planning-engine.md" "GOV-PLAN-0001" "EOS Planning and Dependency Engine" "governance" "governance-authoritative" <<'EOF'
# EOS Planning and Dependency Engine

EOSP treats PI/WC/WP planning as a dependency graph rather than a flat backlog.

Work-packet dependencies may be declared explicitly:

```markdown
- depends-on: WP-CORE-0006
```

## Commands

```bash
./scripts/eos planning check PI-002
./scripts/eos planning order PI-002
./scripts/eos planning critical-path PI-002
./scripts/eos planning graph PI-002 --format mermaid
./scripts/eos planning size WP-CORE-0007
```

## Planning Invariants

- work-packet dependency cycles are invalid;
- referenced dependency WPs must exist;
- dependency execution order must place prerequisites first;
- READY or later work packets must have bounded, non-TBD definitions;
- authorization state must be consistent with parent lifecycle state;
- oversized work packets should be decomposed before execution where practical.

Sizing is heuristic advisory evidence, not a substitute for engineering
judgment.
EOF

write_artifact "governance/execution-engine.md" "GOV-EXEC-0001" "EOSE Execution Engine" "governance" "governance-authoritative" <<'EOF'
# EOSE Execution Engine

EOSE Execution v2 turns an authorized work packet into a bounded, reproducible,
auditable implementation session.

## Execution Flow

`AUTHORIZED WP -> preflight -> isolated worktree/branch -> EXEC-* session ->
fingerprinted machine/human contracts -> bounded implementation -> result
 ingestion -> scope/concurrency checks -> verification evidence -> review`

## Invariants

- one active execution session per work packet unless policy explicitly changes;
- execution contracts are fingerprinted against governing inputs;
- governing-input drift invalidates a contract instead of being silently ignored;
- changed files must satisfy work-packet execution-scope rules;
- EOS and Git metadata are never authorized implementation scope;
- concurrent mutation of one WP/EXEC target is protected by EOS lock records;
- agent output is ingested as structured evidence, never trusted as the sole proof;
- the actual Git diff is compared with the agent-declared changed-file list;
- execution does not itself approve verification, review, closure, or release.

## Work Packet Scope Directives

Work packets may contain machine-readable list entries:

```text
- allowed-path: src/**
- allowed-path: tests/**
- forbidden-path: scripts/release/**
- allowed-governed-path: specifications/CORE/SPEC-CORE-0007.md
```

If no `allowed-path` is present, the execution engine permits repository files
by default but still blocks EOS/Git internals and flags governed-artifact
changes unless specifically authorized by `allowed-governed-path`.
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
[[ -e .eos/executions.tsv ]] || printf 'id\tpath\ttarget\tstatus\tbranch\tworktree\tbaseline_commit\tgoverning_hash\tcontract_hash\tresult_path\tactor\tcreated\tupdated\n' > .eos/executions.tsv
[[ -e .eos/decisions.tsv ]] || printf 'timestamp\ttarget\taction\toutcome\tactor\treason\n' > .eos/decisions.tsv
[[ -e .eos/overrides.tsv ]] || printf 'id\ttarget\tgate\tstatus\tactor\treason\tcreated\texpires\tconsumed_at\n' > .eos/overrides.tsv
[[ -e .eos/stale.tsv ]] || printf 'id\ttarget\tsource\treason\tstatus\tcreated\tcleared_at\tcleared_by\tclear_reason\n' > .eos/stale.tsv
[[ -e .eos/trace-edges.tsv ]] || printf 'source_id\ttarget_id\tedge_type\tsource_path\tevidence\n' > .eos/trace-edges.tsv

if [[ ! -e .eos/execution-policy.json ]]; then
  cat > .eos/execution-policy.json <<'EOF'
{
  "version": "1.0.0",
  "branch_prefix": "wp/",
  "worktree_root": "../.{repo}-worktrees",
  "require_clean_current_tree_for_no_worktree": true,
  "system_forbidden_paths": [".git", ".git/**", ".eos", ".eos/**"],
  "governed_paths": [
    "idea.md",
    "vision/**",
    "product/**",
    "architecture/**",
    "specifications/**",
    "governance/**",
    "engineering/increments/**",
    "engineering/work-cycles/**",
    "engineering/work-packets/**"
  ]
}
EOF
fi

if [[ ! -e .eos/environment.commands ]]; then
  cat > .eos/environment.commands <<'EOF'
# Optional safe version-reporting commands, one per line.
# These are captured as execution-environment evidence only.
# Examples:
# bun --version
# node --version
# cargo --version
EOF
fi

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
append_artifact_registry GOV-STATE-0001 governance/canonical-state-model.md governance governance-authoritative
append_artifact_registry GOV-EVENTS-0001 governance/event-ledger.md governance governance-authoritative
append_artifact_registry GOV-POLICY-0001 governance/policy-engine.md governance governance-authoritative
append_artifact_registry GOV-OVERRIDE-0001 governance/override-policy.md governance governance-authoritative
append_artifact_registry GOV-TRACE-GRAPH-0001 governance/traceability-graph.md governance governance-authoritative
append_artifact_registry GOV-PLAN-0001 governance/planning-engine.md governance governance-authoritative
append_artifact_registry GOV-EXEC-0001 governance/execution-engine.md governance governance-authoritative

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
- `executions.tsv` — EOSE execution-session state;
- `decisions.tsv` — gate/closure decision log;
- `overrides.tsv` — durable human policy-gate overrides;
- `stale.tsv` — downstream artifacts requiring reconciliation after governed changes;
- `events.jsonl` — append-only lifecycle/audit event ledger;
- `domain-model.json` — canonical EOS domain model;
- `schemas/` — machine-readable entity/event schemas;
- `state-machines/` — declarative legal lifecycle transitions;
- `policies/` — named policy-as-code gates;
- `version.json` — EOS tooling/schema compatibility versions;
- `trace-edges.tsv` — generated traceability graph;
- `contracts/` — fingerprinted Codex/agent and ChatGPT review contracts;
- `executions/` — machine-readable `EXEC-*` execution-session records;
- `locks/` — short-lived concurrency lock records;
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
./scripts/eos ready WP-CORE-0001
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
elif grep -q 'tools/eos/eos.py' scripts/eos 2>/dev/null || grep -q 'Engineering Operating System' scripts/eos 2>/dev/null; then
  EOS_CLI_CAN_UPGRADE=1
  mkdir -p .eos/history/tooling
  TOOLING_BACKUP=".eos/history/tooling/scripts-eos-pre-v0.6-$(date -u +%Y%m%dT%H%M%SZ).sh"
  cp scripts/eos "$TOOLING_BACKUP"
fi

if (( EOS_CLI_CAN_UPGRADE == 1 )); then
  cat > scripts/eos <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(git -C "$SCRIPT_ROOT" rev-parse --show-toplevel 2>/dev/null || printf '%s\n' "$SCRIPT_ROOT")"
export EOS_ROOT="$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  printf 'ERROR: python3 is required by the repository-local EOS control tooling.\n' >&2
  exit 127
fi

case "${1:-}" in
  preflight|worktree|execute|execution|contract|codex)
    exec python3 "$ROOT/tools/eos/execution_v2.py" "$@"
    ;;
  *)
    exec python3 "$ROOT/tools/eos/eos.py" "$@"
    ;;
esac
EOF
  chmod +x scripts/eos
else
  warn "Custom scripts/eos detected; preserving it. Full lifecycle engine is available at tools/eos/eos.py."
fi

if [[ -f tools/eos/eos.py ]]; then
  EOS_PY_BACKUP=".eos/history/tooling/eos-py-pre-v0.6-$(date -u +%Y%m%dT%H%M%SZ).py"
  mkdir -p "$(dirname "$EOS_PY_BACKUP")"
  cp tools/eos/eos.py "$EOS_PY_BACKUP"
fi

cat > tools/eos/eos.py <<'EOS_PY'
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import uuid
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
    r"REL-\d+\.\d+\.\d+|"
    r"EXEC-\d{4}"
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
    "EXEC": {"PREPARED", "RUNNING", "RESULT_INGESTED", "VERIFIED", "BLOCKED", "FAILED", "INVALIDATED", "ABORTED", "CLOSED"},
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
    "EXEC": ["id", "path", "target", "status", "branch", "worktree", "baseline_commit", "governing_hash", "contract_hash", "result_path", "actor", "created", "updated"],
}

REGISTRY_PATHS = {
    "PI": ".eos/program-increments.tsv",
    "WC": ".eos/work-cycles.tsv",
    "WP": ".eos/work-packets.tsv",
    "CR": ".eos/change-requests.tsv",
    "MNT": ".eos/maintenance.tsv",
    "REL": ".eos/releases.tsv",
    "EXEC": ".eos/executions.tsv",
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
    explicit = os.environ.get("EOS_ROOT", "").strip()
    if explicit:
        return Path(explicit).resolve()
    try:
        result = run(["git", "rev-parse", "--show-toplevel"])
        return Path(result.stdout.strip()).resolve()
    except Exception:
        # When tools/eos/eos.py is invoked directly, use the repository layout
        # relative to this file before falling back to the caller's cwd.
        candidate = Path(__file__).resolve().parents[2]
        if (candidate / ".eos").exists() or (candidate / "scripts" / "eos").exists():
            return candidate
        return Path.cwd().resolve()


ROOT = discover_root()
EOS = ROOT / ".eos"
SCHEMA_DIR = EOS / "schemas"
STATE_MACHINE_DIR = EOS / "state-machines"
EVENTS_PATH = EOS / "events.jsonl"
EOS_VERSION_PATH = EOS / "version.json"
POLICY_PATH = EOS / "policies" / "core.json"
OVERRIDES_PATH = EOS / "overrides.tsv"
STALE_PATH = EOS / "stale.tsv"
EVENT_SCHEMA_VERSION = "1.0.0"
OVERRIDE_FIELDS = [
    "id", "target", "gate", "status", "actor", "reason", "created", "expires", "consumed_at"
]
STALE_FIELDS = [
    "id", "target", "source", "reason", "status", "created",
    "cleared_at", "cleared_by", "clear_reason"
]
EXPLICIT_RELATION_RE = re.compile(
    r"^\s*-\s*(contains|implements|satisfies|depends-on|conforms-to|constrained-by|affects|includes|references):\s*"
    r"(" + ID_RE.pattern.strip(r"\b") + r")\s*$",
    re.I,
)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EosError(f"Missing EOS definition: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise EosError(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def state_machine(kind: str) -> dict:
    path = STATE_MACHINE_DIR / f"{kind.lower()}.json"
    machine = load_json(path)
    if machine.get("kind") != kind:
        raise EosError(f"State machine kind mismatch in {rel(path)}")
    return machine


def valid_states(kind: str) -> set[str]:
    return set(state_machine(kind).get("states", []))


def transition_allowed(kind: str, current: str, new: str) -> bool:
    machine = state_machine(kind)
    return new in machine.get("transitions", {}).get(current, [])


def validate_simple_schema(schema: dict, instance: dict[str, str], *, label: str) -> list[str]:
    errors: list[str] = []
    if schema.get("type") == "object" and not isinstance(instance, dict):
        return [f"{label}: expected object"]
    required = schema.get("required", [])
    for key in required:
        if key not in instance:
            errors.append(f"{label}: missing required field {key}")
    props = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        extras = sorted(set(instance) - set(props))
        for key in extras:
            errors.append(f"{label}: unexpected field {key}")
    for key, rules in props.items():
        if key not in instance:
            continue
        value = instance[key]
        if rules.get("type") == "string" and not isinstance(value, str):
            errors.append(f"{label}.{key}: expected string")
            continue
        if isinstance(value, str):
            if "minLength" in rules and len(value) < int(rules["minLength"]):
                errors.append(f"{label}.{key}: shorter than minLength")
            pattern = rules.get("pattern")
            if pattern and not re.fullmatch(pattern, value):
                errors.append(f"{label}.{key}: value {value!r} does not match {pattern}")
            enum = rules.get("enum")
            if enum and value not in enum:
                errors.append(f"{label}.{key}: value {value!r} is not in enum")
    return errors


def actor_name(explicit: str = "") -> str:
    return explicit or os.environ.get("EOS_ACTOR") or os.environ.get("USER") or "unknown"


def read_events() -> list[dict]:
    if not EVENTS_PATH.exists():
        return []
    events: list[dict] = []
    for lineno, raw in enumerate(EVENTS_PATH.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise EosError(f"Malformed event ledger line {lineno}: {exc}") from exc
        if not isinstance(event, dict):
            raise EosError(f"Malformed event ledger line {lineno}: expected object")
        events.append(event)
    return events


def append_event(
    event_type: str,
    *,
    target: str = "",
    entity_kind: str = "",
    action: str = "",
    from_state: str = "",
    to_state: str = "",
    actor: str = "",
    reason: str = "",
    metadata: dict | None = None,
) -> dict:
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "event_id": "EVT-" + uuid.uuid4().hex.upper(),
        "schema_version": EVENT_SCHEMA_VERSION,
        "timestamp": now_iso(),
        "event_type": event_type,
        "actor": actor_name(actor),
        "target": target,
        "entity_kind": entity_kind,
        "action": action,
        "from_state": from_state,
        "to_state": to_state,
        "reason": reason,
        "commit": commit_sha() if "commit_sha" in globals() else "",
        "metadata": metadata or {},
    }
    schema_path = SCHEMA_DIR / "event.schema.json"
    if schema_path.exists():
        errors = validate_simple_schema(load_json(schema_path), event, label=event["event_id"])
        if errors:
            raise EosError("Event schema validation failed:\n- " + "\n- ".join(errors))
    line = json.dumps(event, sort_keys=True, separators=(",", ":"))
    with EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())
    return event


def ensure_event_ledger_seeded() -> None:
    if EVENTS_PATH.exists() and EVENTS_PATH.stat().st_size > 0:
        return
    append_event(
        "EOS_INITIALIZED",
        action="bootstrap",
        reason="initialize append-only EOS lifecycle event ledger",
        metadata={"root": str(ROOT)},
    )
    for kind in ("PI", "WC", "WP", "CR", "MNT", "REL", "EXEC"):
        for row in registry(kind):
            append_event(
                "ENTITY_IMPORTED",
                target=row.get("id", ""),
                entity_kind=kind,
                action="import",
                to_state=row.get("status", ""),
                reason="seed existing lifecycle registry into event ledger",
                metadata={"row": row},
            )


def record_tool_upgrade_if_needed() -> None:
    previous = os.environ.get("EOS_PREVIOUS_TOOL_VERSION", "").strip()
    if not previous or not EOS_VERSION_PATH.exists():
        return
    current = load_json(EOS_VERSION_PATH).get("eos_tool_version", "")
    if not current or current == previous:
        return
    # Avoid duplicate upgrade events in case bootstrap invokes more than one EOS
    # command under the same environment.
    for event in reversed(read_events()):
        if event.get("event_type") == "EOS_TOOL_UPGRADED":
            meta = event.get("metadata", {})
            if meta.get("from") == previous and meta.get("to") == current:
                return
    append_event(
        "EOS_TOOL_UPGRADED",
        action="upgrade",
        reason=f"EOS tooling upgraded from {previous} to {current}",
        metadata={"from": previous, "to": current},
    )


def event_projected_state() -> dict[tuple[str, str], str]:
    state: dict[tuple[str, str], str] = {}
    for event in read_events():
        kind = event.get("entity_kind", "")
        target = event.get("target", "")
        if not kind or not target:
            continue
        if event.get("event_type") in {"ENTITY_CREATED", "ENTITY_IMPORTED"}:
            initial = event.get("to_state") or event.get("metadata", {}).get("row", {}).get("status", "")
            if initial:
                state[(kind, target)] = initial
        elif event.get("event_type") == "STATE_TRANSITION":
            if event.get("to_state"):
                state[(kind, target)] = event["to_state"]
    return state


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
        EOS / "schemas",
        EOS / "state-machines",
        EOS / "policies",
        EOS / "cache",
        EOS / "sync",
        EOS / "executions",
        EOS / "locks",
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
    if re.fullmatch(r"EXEC-\d{4}", target):
        return "EXEC"
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
    elif kind == "EXEC":
        pattern = re.compile(r"^EXEC-(\d{4})$")
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
    if not path.exists() or path.suffix != ".md":
        return
    replace_state_line(path, state)
    data, _ = parse_frontmatter(path) if path.suffix == ".md" else ({}, "")
    if data:
        set_frontmatter(path, "status", state)


def set_lifecycle_state(
    target: str,
    state: str,
    *,
    action: str = "transition",
    actor: str = "",
    reason: str = "",
    force: bool = False,
) -> None:
    kind, row = row_for_target(target)
    current = row["status"]
    if state not in valid_states(kind):
        raise EosError(f"Invalid {kind} state: {state}")
    if current == state:
        return
    if not force and not transition_allowed(kind, current, state):
        allowed = state_machine(kind).get("transitions", {}).get(current, [])
        raise EosError(
            f"Illegal {kind} lifecycle transition {target}: {current} -> {state}. "
            f"Allowed from {current}: {', '.join(allowed) or '(none)'}"
        )

    # Append the durable mutation event first. Registry/artifact writes are
    # projections of this lifecycle mutation.
    append_event(
        "STATE_TRANSITION",
        target=target,
        entity_kind=kind,
        action=action,
        from_state=current,
        to_state=state,
        actor=actor,
        reason=reason,
        metadata={"path": row.get("path", "")},
    )
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
    try:
        entity_kind = kind_for_id(target)
    except EosError:
        entity_kind = ""
    append_event(
        "DECISION_RECORDED",
        target=target,
        entity_kind=entity_kind,
        action=action,
        actor=actor,
        reason=reason,
        metadata={"outcome": outcome},
    )



def policy_document() -> dict:
    return load_json(POLICY_PATH)


def policy_gate(name: str) -> list[dict]:
    gates = policy_document().get("gates", {})
    if name not in gates:
        raise EosError(f"Unknown policy gate: {name}")
    checks = gates[name]
    if not isinstance(checks, list):
        raise EosError(f"Policy gate {name} is malformed")
    return checks


def override_rows() -> list[dict[str, str]]:
    return read_tsv(OVERRIDES_PATH)


def save_overrides(rows: list[dict[str, str]]) -> None:
    write_tsv(OVERRIDES_PATH, OVERRIDE_FIELDS, rows)


def next_override_id() -> str:
    nums: list[int] = []
    for row in override_rows():
        match = re.fullmatch(r"OVR-(\d{4})", row.get("id", ""))
        if match:
            nums.append(int(match.group(1)))
    return f"OVR-{max(nums, default=0) + 1:04d}"


def override_expired(row: dict[str, str]) -> bool:
    expires = row.get("expires", "").strip()
    if not expires:
        return False
    try:
        return dt.date.fromisoformat(expires) < dt.date.today()
    except ValueError:
        return True


def active_override(target: str, gate: str) -> dict[str, str] | None:
    rows = override_rows()
    changed = False
    found: dict[str, str] | None = None
    for row in rows:
        if row.get("status") == "ACTIVE" and override_expired(row):
            row["status"] = "EXPIRED"
            changed = True
        if (
            row.get("target") == target
            and row.get("gate") == gate
            and row.get("status") == "ACTIVE"
            and not override_expired(row)
        ):
            found = row
    if changed:
        save_overrides(rows)
    return found


def create_override(
    target: str,
    gate: str,
    *,
    actor: str,
    reason: str,
    expires: str = "",
) -> dict[str, str]:
    if not reason.strip():
        raise EosError("A durable override requires an explicit --reason")
    policy_gate(gate)  # validate gate name
    if expires:
        try:
            dt.date.fromisoformat(expires)
        except ValueError as exc:
            raise EosError("--expires must be YYYY-MM-DD") from exc
    row = {
        "id": next_override_id(),
        "target": target,
        "gate": gate,
        "status": "ACTIVE",
        "actor": actor_name(actor),
        "reason": reason.strip(),
        "created": now_iso(),
        "expires": expires,
        "consumed_at": "",
    }
    rows = override_rows()
    rows.append(row)
    save_overrides(rows)
    append_event(
        "OVERRIDE_CREATED",
        target=target,
        action=gate,
        actor=row["actor"],
        reason=row["reason"],
        metadata={"override": row},
    )
    return row


def consume_override(row: dict[str, str]) -> None:
    rows = override_rows()
    for item in rows:
        if item.get("id") == row.get("id"):
            item["status"] = "CONSUMED"
            item["consumed_at"] = now_iso()
            save_overrides(rows)
            append_event(
                "OVERRIDE_CONSUMED",
                target=item.get("target", ""),
                action=item.get("gate", ""),
                actor=item.get("actor", ""),
                reason=item.get("reason", ""),
                metadata={"override_id": item.get("id", "")},
            )
            return
    raise EosError(f"Override {row.get('id')} disappeared before consumption")


def check_result(name: str, passed: bool, message: str, evidence: dict | None = None) -> dict:
    return {
        "check": name,
        "passed": bool(passed),
        "message": message,
        "evidence": evidence or {},
    }


def evaluate_policy_check(target: str, spec: dict) -> dict:
    kind, row = row_for_target(target)
    name = spec.get("check", "")
    path = ROOT / row["path"]

    if name == "state_is":
        expected = str(spec.get("value", ""))
        return check_result(
            name,
            row["status"] == expected,
            f"state is {row['status']}; required {expected}",
            {"actual": row["status"], "required": expected},
        )

    if name == "artifact_complete":
        passed, issues = artifact_is_complete_enough(path)
        return check_result(
            name,
            passed,
            "artifact is complete enough" if passed else "; ".join(issues),
            {"path": rel(path), "issues": issues},
        )

    if name == "parent_state":
        allowed = set(spec.get("values", []))
        parent_id = row.get("wc") if kind == "WP" else row.get("pi") if kind == "WC" else ""
        if not parent_id:
            return check_result(name, False, "entity has no applicable parent")
        p_kind, p_row = row_for_target(parent_id)
        passed = p_row["status"] in allowed
        return check_result(
            name,
            passed,
            f"parent {parent_id} is {p_row['status']}; allowed: {', '.join(sorted(allowed))}",
            {"parent": parent_id, "parent_kind": p_kind, "actual": p_row["status"], "allowed": sorted(allowed)},
        )

    if name == "review_accepted":
        rpath = review_path(target)
        passed, issues = accepted_review_complete(rpath)
        return check_result(
            name,
            passed,
            f"review accepted: {rel(rpath)}" if passed else "; ".join(issues),
            {"review": rel(rpath), "issues": issues},
        )

    if name == "pi_readiness_review_accepted":
        candidates = [
            ROOT / "engineering" / "reviews" / f"{target}-READINESS-REVIEW.md",
            review_path(target),
        ]
        if target == "PI-001":
            candidates.append(ROOT / "engineering" / "reviews" / "PI-001-READINESS-REVIEW.md")
        details = []
        for candidate in candidates:
            ok, issues = accepted_review_complete(candidate)
            details.append({"path": rel(candidate), "passed": ok, "issues": issues})
            if ok:
                return check_result(name, True, f"accepted readiness review: {rel(candidate)}", {"candidates": details})
        return check_result(name, False, "no accepted complete PI readiness review", {"candidates": details})

    if name == "pi_closeout_review_accepted":
        candidates = [
            ROOT / "engineering" / "reviews" / f"{target}-CLOSEOUT-REVIEW.md",
            review_path(target),
        ]
        details = []
        for candidate in candidates:
            ok, issues = accepted_review_complete(candidate)
            details.append({"path": rel(candidate), "passed": ok, "issues": issues})
            if ok:
                return check_result(name, True, f"accepted PI closeout review: {rel(candidate)}", {"candidates": details})
        return check_result(name, False, "no accepted complete PI closeout review", {"candidates": details})

    if name == "no_unchecked_items":
        count = unchecked_boxes(path)
        return check_result(
            name,
            count == 0,
            "no unchecked items" if count == 0 else f"{count} unchecked item(s) remain",
            {"count": count, "path": rel(path)},
        )

    if name == "has_children":
        if kind == "WC":
            children = [r for r in registry("WP") if r.get("wc") == target]
        elif kind == "PI":
            children = [r for r in registry("WC") if r.get("pi") == target]
        else:
            children = []
        return check_result(
            name,
            bool(children),
            f"{len(children)} child object(s) registered",
            {"children": [r["id"] for r in children]},
        )

    if name == "children_closed":
        if kind == "WC":
            children = [r for r in registry("WP") if r.get("wc") == target]
        elif kind == "PI":
            children = [r for r in registry("WC") if r.get("pi") == target]
        else:
            children = []
        open_ids = [r["id"] for r in children if r.get("status") != "CLOSED"]
        return check_result(
            name,
            not open_ids,
            "all children closed" if not open_ids else "open children: " + ", ".join(open_ids),
            {"open": open_ids},
        )

    if name == "change_decision_approved":
        decision = review_decision(path)
        passed = decision in {"APPROVED", "ACCEPTED"}
        return check_result(
            name,
            passed,
            f"change decision is {decision or '(unset)'}; required APPROVED/ACCEPTED",
            {"decision": decision},
        )

    raise EosError(f"Unsupported policy predicate: {name}")


def evaluate_gate(name: str, target: str) -> dict:
    results = [evaluate_policy_check(target, spec) for spec in policy_gate(name)]
    failures = [r for r in results if not r["passed"]]
    override = active_override(target, name)
    return {
        "gate": name,
        "target": target,
        "passed": not failures,
        "effective_pass": not failures or override is not None,
        "checks": results,
        "failures": failures,
        "override": override,
    }


def format_gate(result: dict) -> str:
    lines = [
        f"Gate:   {result['gate']}",
        f"Target: {result['target']}",
        f"Result: {'PASS' if result['passed'] else 'FAIL'}",
    ]
    if result.get("override"):
        lines.append(
            f"Override: {result['override']['id']} ACTIVE by {result['override']['actor']}"
        )
    lines.append("Checks:")
    for item in result["checks"]:
        lines.append(
            f"  {'PASS' if item['passed'] else 'FAIL'}  "
            f"{item['check']}: {item['message']}"
        )
    return "\n".join(lines)


def enforce_gate(
    name: str,
    target: str,
    *,
    force: bool = False,
    actor: str = "",
    reason: str = "",
) -> dict[str, str] | None:
    result = evaluate_gate(name, target)
    if result["passed"]:
        return None

    override = result.get("override")
    if override:
        return override

    if force:
        override = create_override(
            target,
            name,
            actor=actor_name(actor),
            reason=reason,
        )
        return override

    failures = "\n- ".join(item["message"] for item in result["failures"])
    raise EosError(
        f"{name} gate failed for {target}:\n- {failures}\n"
        f"Inspect with: ./scripts/eos gate explain {name} {target}\n"
        "An explicit human override may be created only with a recorded reason."
    )


def cmd_policy_list(_: argparse.Namespace) -> None:
    doc = policy_document()
    for name in sorted(doc.get("gates", {})):
        print(name)


def cmd_policy_show(args: argparse.Namespace) -> None:
    print(json.dumps({"gate": args.gate, "checks": policy_gate(args.gate)}, indent=2, sort_keys=True))


def cmd_gate(args: argparse.Namespace) -> None:
    result = evaluate_gate(args.gate, args.target)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(format_gate(result))
    if not result["effective_pass"]:
        raise EosError("Gate did not pass")


def cmd_override_create(args: argparse.Namespace) -> None:
    row = create_override(
        args.target,
        args.gate,
        actor=args.by,
        reason=args.reason,
        expires=args.expires,
    )
    print(
        f"Created {row['id']} for {row['target']} gate {row['gate']} "
        f"by {row['actor']}"
    )


def cmd_override_list(args: argparse.Namespace) -> None:
    rows = override_rows()
    if args.target:
        rows = [r for r in rows if r.get("target") == args.target]
    if args.active:
        rows = [r for r in rows if r.get("status") == "ACTIVE" and not override_expired(r)]
    for row in rows:
        print(
            f"{row['id']}  {row['status']:<9}  {row['target']:<20} "
            f"{row['gate']:<20} {row['actor']}  {row['reason']}"
        )


def cmd_override_expire(args: argparse.Namespace) -> None:
    rows = override_rows()
    for row in rows:
        if row.get("id") == args.override_id:
            if row.get("status") != "ACTIVE":
                raise EosError(f"{args.override_id} is {row.get('status')}, not ACTIVE")
            row["status"] = "EXPIRED"
            save_overrides(rows)
            append_event(
                "OVERRIDE_EXPIRED",
                target=row.get("target", ""),
                action=row.get("gate", ""),
                actor=actor_name(),
                reason="override explicitly expired",
                metadata={"override_id": args.override_id},
            )
            print(f"{args.override_id} EXPIRED.")
            return
    raise EosError(f"Unknown override: {args.override_id}")


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
    source_id = data.get("artifact_id", "UNREGISTERED")
    stale_created = mark_dependents_stale(
        source_id,
        f"{source_id} changed {current} -> {new}: {args.message}",
    )
    print(f"{rel(path)}: {current} -> {new} ({args.message})")
    if stale_created:
        print(f"Marked {len(stale_created)} downstream artifact(s) stale: {', '.join(stale_created)}")


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
    source_id = restored_data.get("artifact_id", "UNREGISTERED")
    stale_created = mark_dependents_stale(
        source_id,
        f"{source_id} rollback restored v{target} as v{new_version}: {args.message}",
    )
    print(f"Restored v{target} content as new version v{new_version}.")
    if stale_created:
        print(f"Marked {len(stale_created)} downstream artifact(s) stale: {', '.join(stale_created)}")


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
    append_event(
        "ENTITY_CREATED",
        target=pi_id,
        entity_kind="PI",
        action="plan",
        to_state="DRAFT",
        reason="program increment created",
        metadata={"row": rows[-1]},
    )
    print(f"Created {pi_id}: {rel(path)}")
    print(f"Next: complete the PI definition, then ./scripts/eos ready {pi_id}")


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
    append_event(
        "ENTITY_CREATED",
        target=wc_id,
        entity_kind="WC",
        action="create-wc",
        to_state="DRAFT",
        reason="work cycle created",
        metadata={"row": rows[-1]},
    )
    print(f"Created {wc_id} under {pi}: {rel(path)}")
    print(f"Next: complete the work-cycle definition, then ./scripts/eos ready {wc_id}")


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

## Execution Scope

EOSE blocks Git/EOS internals and governed-artifact changes by default. Add
`allowed-path`, `forbidden-path`, or `allowed-governed-path` directives when this
work packet requires a more explicit machine-enforced file boundary.

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
    append_event(
        "ENTITY_CREATED",
        target=wp_id,
        entity_kind="WP",
        action="create-wp",
        to_state="DRAFT",
        reason="work packet created",
        metadata={"row": rows[-1]},
    )
    print(f"Created {wp_id} under {wc}/{pi}: {rel(path)}")
    print(f"Next: complete the work-packet definition, then ./scripts/eos ready {wp_id}")



def cmd_ready(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind not in {"PI", "WC", "WP"}:
        raise EosError("ready applies to PI, WC, or WP")

    destination = {"PI": "PLANNED", "WC": "READY", "WP": "READY"}[kind]
    gate_name = f"{kind}_READY"
    override = enforce_gate(
        gate_name,
        args.target,
        actor=getattr(args, "by", ""),
        reason=getattr(args, "reason", ""),
    )
    set_lifecycle_state(
        args.target,
        destination,
        action="ready",
        actor=actor_name(getattr(args, "by", "")),
        reason=getattr(args, "reason", "") or "definition complete enough for next gate",
    )
    if override:
        consume_override(override)
    print(f"{args.target} -> {destination}")



def cmd_authorize(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind not in {"PI", "WC", "WP"}:
        raise EosError("authorize currently applies to PI, WC, or WP")
    gate_name = f"{kind}_AUTHORIZE"
    actor = args.by or os.environ.get("USER") or "human"
    if args.force and not args.reason.strip():
        raise EosError("--force requires an explicit --reason so a durable override can be recorded")
    reason = args.reason or "human authorization"
    override = enforce_gate(
        gate_name,
        args.target,
        force=args.force,
        actor=actor,
        reason=reason if args.force else args.reason,
    )
    set_lifecycle_state(
        args.target,
        "AUTHORIZED",
        action="authorize",
        actor=actor,
        reason=reason if not override else f"authorized under {override['id']}: {override['reason']}",
    )
    if override:
        consume_override(override)
    record_decision(args.target, "authorize", "AUTHORIZED", actor, reason)
    print(f"{args.target} AUTHORIZED by {actor}.")



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
    set_lifecycle_state(
        args.target,
        new,
        action="start",
        actor=actor_name(),
        reason="authorized execution started",
    )
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
    if kind == "WP":
        if row["status"] == "AUTHORIZED":
            raise EosError(
                f"{args.target} is AUTHORIZED; start it first with ./scripts/eos start {args.target}"
            )
        if row["status"] == "IN_PROGRESS":
            set_lifecycle_state(
                args.target,
                "VERIFYING",
                action="validate",
                actor=actor_name(),
                reason="deterministic verification started",
            )
        elif row["status"] != "VERIFYING":
            raise EosError(
                f"{args.target} must be IN_PROGRESS or VERIFYING before validation; "
                f"current state is {row['status']}"
            )
    verify_ok, verify_report = verify_all(strict=True)
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
        set_lifecycle_state(
            args.target,
            "IN_REVIEW",
            action="review",
            actor=actor_name(),
            reason="engineering review started",
        )
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
    actor = args.by or os.environ.get("USER") or "human"
    override = enforce_gate(
        "WP_CLOSE",
        args.target,
        force=args.force,
        actor=actor,
        reason=args.reason,
    )
    set_lifecycle_state(
        args.target,
        "CLOSED",
        action="close",
        actor=actor,
        reason=args.reason or (
            f"closure under {override['id']}" if override else "closure gate satisfied"
        ),
    )
    if override:
        consume_override(override)
    record_decision(args.target, "close", "CLOSED", actor, args.reason or "work packet closure")
    print(f"{args.target} CLOSED.")



def cmd_close_cycle(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "WC":
        raise EosError("close-cycle requires a WC id")
    actor = args.by or os.environ.get("USER") or "human"
    override = enforce_gate(
        "WC_CLOSE",
        args.target,
        force=args.force,
        actor=actor,
        reason=args.reason,
    )
    set_lifecycle_state(
        args.target,
        "CLOSED",
        action="close-cycle",
        actor=actor,
        reason=args.reason or (
            f"closure under {override['id']}" if override else "work-cycle closure gate satisfied"
        ),
    )
    if override:
        consume_override(override)
    record_decision(args.target, "close-cycle", "CLOSED", actor, args.reason or "work cycle closure")
    print(f"{args.target} CLOSED.")



def cmd_close_pi(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "PI":
        raise EosError("close-pi requires a PI id")
    actor = args.by or os.environ.get("USER") or "human"
    override = enforce_gate(
        "PI_CLOSE",
        args.target,
        force=args.force,
        actor=actor,
        reason=args.reason,
    )
    set_lifecycle_state(
        args.target,
        "CLOSED",
        action="close-pi",
        actor=actor,
        reason=args.reason or (
            f"closure under {override['id']}" if override else "program-increment closure gate satisfied"
        ),
    )
    if override:
        consume_override(override)
    record_decision(args.target, "close-pi", "CLOSED", actor, args.reason or "program increment closure")
    print(f"{args.target} CLOSED.")




def stale_rows() -> list[dict[str, str]]:
    return read_tsv(STALE_PATH)


def save_stale(rows: list[dict[str, str]]) -> None:
    write_tsv(STALE_PATH, STALE_FIELDS, rows)


def next_stale_id() -> str:
    nums: list[int] = []
    for row in stale_rows():
        match = re.fullmatch(r"STL-(\d{4})", row.get("id", ""))
        if match:
            nums.append(int(match.group(1)))
    return f"STL-{max(nums, default=0) + 1:04d}"


def strip_fenced_code(text: str) -> str:
    """Remove fenced Markdown code blocks so documentation examples do not become graph edges."""
    out: list[str] = []
    in_fence = False
    fence = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            token = stripped[:3]
            if not in_fence:
                in_fence = True
                fence = token
            elif token == fence:
                in_fence = False
                fence = ""
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def stale_relevant_target(target: str) -> bool:
    path = artifact_path_for_id(target)
    if path and path.suffix == ".md":
        data, _ = parse_frontmatter(path)
        authority = data.get("authority", "")
        artifact_type = data.get("type", "")
        if authority in {"historical", "informative", "historical-source"}:
            return False
        if artifact_type in {"journal", "index", "template"}:
            return False
    return not target.startswith("FILE:")


def infer_edge_type(source: str, target: str) -> str:
    if source.startswith("WP-"):
        if target.startswith("REQ-"):
            return "implements"
        if target.startswith("SPEC-"):
            return "satisfies"
        if target.startswith(("ADR-", "QA-")):
            return "conforms-to"
    if source.startswith("SPEC-"):
        if target.startswith(("REQ-", "CAP-")):
            return "satisfies"
        if target.startswith(("ADR-", "QA-")):
            return "constrained-by"
    if source.startswith("ADR-"):
        if target.startswith(("REQ-", "QA-", "SPEC-")):
            return "constrains"
    if source.startswith("CR-"):
        return "affects"
    if source.startswith("MNT-"):
        return "affects"
    if source.startswith("REL-"):
        return "includes"
    return "references"


def impacted_entities(source_id: str, *, transitive: bool = True) -> list[dict[str, str]]:
    edges = rebuild_trace()
    reverse: dict[str, list[dict[str, str]]] = {}
    for edge in edges:
        reverse.setdefault(edge["target_id"], []).append(edge)

    queue = deque([(source_id, 0)])
    seen = {source_id}
    out: list[dict[str, str]] = []
    while queue:
        node, depth = queue.popleft()
        for edge in sorted(
            reverse.get(node, []),
            key=lambda e: (e["source_id"], e["edge_type"], e["source_path"]),
        ):
            dependent = edge["source_id"]
            if dependent in seen:
                continue
            seen.add(dependent)
            row = dict(edge)
            row["depth"] = str(depth + 1)
            out.append(row)
            if transitive:
                queue.append((dependent, depth + 1))
    return out


def mark_dependents_stale(source_id: str, reason: str) -> list[str]:
    if not source_id or source_id in {"UNREGISTERED", "INCEPT-IDEA-0001"}:
        return []
    impacts = impacted_entities(source_id, transitive=True)
    rows = stale_rows()
    open_pairs = {(r.get("target"), r.get("source")) for r in rows if r.get("status") == "OPEN"}
    created: list[str] = []
    for impact in impacts:
        target = impact["source_id"]
        if target == source_id or not stale_relevant_target(target):
            continue
        pair = (target, source_id)
        if pair in open_pairs:
            continue
        stale_id = next_stale_id()
        # next_stale_id() reads disk, so account for rows not yet persisted.
        if created:
            stale_id = f"STL-{int(created[-1].split('-')[1]) + 1:04d}"
        row = {
            "id": stale_id,
            "target": target,
            "source": source_id,
            "reason": reason,
            "status": "OPEN",
            "created": now_iso(),
            "cleared_at": "",
            "cleared_by": "",
            "clear_reason": "",
        }
        rows.append(row)
        open_pairs.add(pair)
        created.append(stale_id)
        append_event(
            "DEPENDENT_MARKED_STALE",
            target=target,
            action="trace-stale",
            reason=reason,
            metadata={
                "stale_id": stale_id,
                "source": source_id,
                "depth": impact.get("depth", ""),
                "edge_type": impact.get("edge_type", ""),
            },
        )
    if created:
        save_stale(rows)
    return created


def cmd_stale_list(args: argparse.Namespace) -> None:
    rows = stale_rows()
    if not args.all:
        rows = [r for r in rows if r.get("status") == "OPEN"]
    if args.target:
        rows = [r for r in rows if r.get("target") == args.target or r.get("source") == args.target]
    if not rows:
        print("No matching stale records.")
        return
    for row in rows:
        print(
            f"{row['id']}  {row['status']:<7}  target={row['target']:<20} "
            f"source={row['source']:<20} {row['reason']}"
        )


def cmd_stale_clear(args: argparse.Namespace) -> None:
    rows = stale_rows()
    matched = False
    for row in rows:
        if row.get("id") == args.stale_id:
            matched = True
            if row.get("status") != "OPEN":
                raise EosError(f"{args.stale_id} is {row.get('status')}, not OPEN")
            if not args.reason.strip():
                raise EosError("Clearing stale state requires --reason")
            row["status"] = "CLEARED"
            row["cleared_at"] = now_iso()
            row["cleared_by"] = actor_name(args.by)
            row["clear_reason"] = args.reason.strip()
            append_event(
                "STALE_CLEARED",
                target=row.get("target", ""),
                action="stale-clear",
                actor=row["cleared_by"],
                reason=row["clear_reason"],
                metadata={"stale_id": row["id"], "source": row.get("source", "")},
            )
            break
    if not matched:
        raise EosError(f"Unknown stale record: {args.stale_id}")
    save_stale(rows)
    print(f"{args.stale_id} CLEARED.")



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
    edges: dict[tuple[str, str, str, str], dict[str, str]] = {}

    # Structural lifecycle edges are authoritative and do not depend on prose.
    for wc in registry("WC"):
        key = (wc["pi"], wc["id"], "contains", wc["path"])
        edges[key] = {
            "source_id": wc["pi"],
            "target_id": wc["id"],
            "edge_type": "contains",
            "source_path": wc["path"],
            "evidence": "lifecycle-registry",
        }
    for wp in registry("WP"):
        key = (wp["wc"], wp["id"], "contains", wp["path"])
        edges[key] = {
            "source_id": wp["wc"],
            "target_id": wp["id"],
            "edge_type": "contains",
            "source_path": wp["path"],
            "evidence": "lifecycle-registry",
        }
    for cr in registry("CR"):
        target = cr.get("target", "")
        if target:
            key = (cr["id"], target, "affects", cr["path"])
            edges[key] = {
                "source_id": cr["id"],
                "target_id": target,
                "edge_type": "affects",
                "source_path": cr["path"],
                "evidence": "change-registry",
            }

    for path in candidate_trace_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        source = source_id_for(path)
        scan_text = strip_fenced_code(text) if path.suffix == ".md" else text
        explicit_pairs: set[tuple[str, str]] = set()

        for lineno, line in enumerate(scan_text.splitlines(), start=1):
            m = EXPLICIT_RELATION_RE.match(line)
            if not m:
                continue
            edge_type = m.group(1).lower()
            target = m.group(2)
            if target == source:
                continue
            explicit_pairs.add((source, target))
            key = (source, target, edge_type, rel(path))
            edges[key] = {
                "source_id": source,
                "target_id": target,
                "edge_type": edge_type,
                "source_path": rel(path),
                "evidence": f"explicit-line:{lineno}",
            }

        for target in set(ID_RE.findall(scan_text)):
            if target == source or (source, target) in explicit_pairs:
                continue
            edge_type = infer_edge_type(source, target)
            key = (source, target, edge_type, rel(path))
            edges[key] = {
                "source_id": source,
                "target_id": target,
                "edge_type": edge_type,
                "source_path": rel(path),
                "evidence": "inferred-reference",
            }

    fields = ["source_id", "target_id", "edge_type", "source_path", "evidence"]
    rows = sorted(
        edges.values(),
        key=lambda r: (r["source_id"], r["target_id"], r["edge_type"], r["source_path"]),
    )
    write_tsv(EOS / "trace-edges.tsv", fields, rows)
    return rows


def trace_coverage_report() -> dict:
    edges = rebuild_trace()
    nodes: set[str] = set()
    for edge in edges:
        nodes.add(edge["source_id"])
        nodes.add(edge["target_id"])
    for kind in ("PI", "WC", "WP", "CR", "MNT", "REL"):
        nodes.update(row["id"] for row in registry(kind))

    requirements = sorted(n for n in nodes if n.startswith("REQ-"))
    specifications = sorted(n for n in nodes if n.startswith("SPEC-"))
    work_packets = sorted(row["id"] for row in registry("WP"))

    incoming: dict[str, list[dict[str, str]]] = {}
    outgoing: dict[str, list[dict[str, str]]] = {}
    for edge in edges:
        incoming.setdefault(edge["target_id"], []).append(edge)
        outgoing.setdefault(edge["source_id"], []).append(edge)

    req_uncovered = [
        req
        for req in requirements
        if not any(
            e["source_id"].startswith(("SPEC-", "WP-"))
            and e["edge_type"] in {"implements", "satisfies", "references"}
            for e in incoming.get(req, [])
        )
    ]
    spec_untraced = [
        spec
        for spec in specifications
        if not any(e["target_id"].startswith(("REQ-", "CAP-", "ADR-", "QA-")) for e in outgoing.get(spec, []))
    ]
    wp_untraced = [
        wp
        for wp in work_packets
        if not any(
            e["target_id"].startswith(("REQ-", "SPEC-", "ADR-", "QA-"))
            for e in outgoing.get(wp, [])
        )
    ]
    closed_without_evidence = []
    for row in registry("WP"):
        if row["status"] != "CLOSED":
            continue
        if not list((EOS / "evidence").glob(f"{row['id']}-*")):
            closed_without_evidence.append(row["id"])

    total = len(requirements) + len(specifications) + len(work_packets)
    gaps = len(req_uncovered) + len(spec_untraced) + len(wp_untraced)
    score = 100.0 if total == 0 else max(0.0, 100.0 * (total - gaps) / total)

    return {
        "score": round(score, 1),
        "requirements": len(requirements),
        "specifications": len(specifications),
        "work_packets": len(work_packets),
        "requirement_gaps": req_uncovered,
        "specification_gaps": spec_untraced,
        "work_packet_gaps": wp_untraced,
        "closed_wp_without_evidence": closed_without_evidence,
    }


def cmd_trace(args: argparse.Namespace) -> None:
    if args.target.lower() == "coverage":
        report = trace_coverage_report()
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
            return
        print(f"TRACEABILITY COVERAGE — {report['score']:.1f}%")
        print(
            f"requirements={report['requirements']} "
            f"specifications={report['specifications']} "
            f"work_packets={report['work_packets']}"
        )
        for label, key in (
            ("Requirements without implementation/spec trace", "requirement_gaps"),
            ("Specifications without governing trace", "specification_gaps"),
            ("Work packets without governing trace", "work_packet_gaps"),
            ("Closed work packets without evidence", "closed_wp_without_evidence"),
        ):
            values = report[key]
            print(f"\n{label}:")
            if values:
                for value in values:
                    print(f"  - {value}")
            else:
                print("  none")
        return

    edges = rebuild_trace()
    target = args.target
    path = artifact_path_for_id(target)
    outgoing = [e for e in edges if e["source_id"] == target]
    incoming = [e for e in edges if e["target_id"] == target]

    if args.json:
        print(
            json.dumps(
                {
                    "target": target,
                    "artifact": rel(path) if path else "",
                    "outgoing": outgoing,
                    "incoming": incoming,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return

    print(f"TRACE — {target}")
    print(f"Artifact: {rel(path) if path else '(not directly located)'}\n")

    print("Outgoing relationships:")
    if outgoing:
        for e in outgoing:
            print(
                f"  {e['edge_type']:<16} {e['target_id']:<20} "
                f"via {e['source_path']} ({e['evidence']})"
            )
    else:
        print("  none discovered")

    print("\nIncoming relationships:")
    if incoming:
        for e in incoming:
            print(
                f"  {e['source_id']:<20} {e['edge_type']:<16} "
                f"via {e['source_path']} ({e['evidence']})"
            )
    else:
        print("  none discovered")


def impact_class(edge_type: str, entity: str) -> str:
    if edge_type in {"implements", "satisfies"} or entity.startswith("WP-"):
        return "implementation"
    if edge_type in {"conforms-to", "constrained-by", "constrains"} or entity.startswith(("ADR-", "SPEC-")):
        return "architecture/specification"
    if edge_type == "contains" or entity.startswith(("PI-", "WC-")):
        return "planning"
    if edge_type in {"affects", "includes"}:
        return "change/release"
    return "reference"


def cmd_impact(args: argparse.Namespace) -> None:
    results = impacted_entities(args.target, transitive=True)
    enriched = [
        {
            **row,
            "impact_class": impact_class(row["edge_type"], row["source_id"]),
        }
        for row in results
    ]

    if args.json:
        print(json.dumps({"target": args.target, "impacts": enriched}, indent=2, sort_keys=True))
        return

    print(f"IMPACT ANALYSIS — {args.target}\n")
    if not enriched:
        print("No downstream references discovered.")
        return
    for row in enriched:
        depth = int(row["depth"])
        print(
            f"{'  ' * (depth - 1)}- {row['source_id']} "
            f"[{row['impact_class']}; {row['edge_type']}; {row['source_path']}]"
        )




def pi_work_packets(pi_id: str) -> list[dict[str, str]]:
    return [row for row in registry("WP") if row.get("pi") == pi_id]


def wp_dependency_map(pi_id: str) -> tuple[dict[str, set[str]], list[str]]:
    wps = {row["id"]: row for row in pi_work_packets(pi_id)}
    deps: dict[str, set[str]] = {wp_id: set() for wp_id in wps}
    errors: list[str] = []
    for edge in rebuild_trace():
        if edge["edge_type"] != "depends-on":
            continue
        source = edge["source_id"]
        target = edge["target_id"]
        if source not in wps:
            continue
        if not target.startswith("WP-"):
            errors.append(f"{source} depends-on non-WP target {target}")
            continue
        if not find_row("WP", target):
            errors.append(f"{source} depends on unknown work packet {target}")
            continue
        deps[source].add(target)
    return deps, errors


def topological_wp_order(pi_id: str) -> tuple[list[str], list[str]]:
    deps, errors = wp_dependency_map(pi_id)
    if errors:
        return [], errors
    nodes = set(deps)
    # Include cross-PI dependencies as prerequisite nodes for cycle detection
    # only when they are themselves in the requested PI; external dependencies
    # are reported separately by planning checks.
    indegree = {node: 0 for node in nodes}
    dependents: dict[str, set[str]] = {node: set() for node in nodes}
    for source, targets in deps.items():
        for target in targets:
            if target not in nodes:
                continue
            indegree[source] += 1
            dependents[target].add(source)

    ready = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    order: list[str] = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for dependent in sorted(dependents.get(node, set())):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)

    if len(order) != len(nodes):
        cyclic = sorted(node for node, degree in indegree.items() if degree > 0)
        errors.append("work-packet dependency cycle detected involving: " + ", ".join(cyclic))
        return [], errors
    return order, errors


def critical_path_for_pi(pi_id: str) -> tuple[list[str], list[str]]:
    order, errors = topological_wp_order(pi_id)
    if errors:
        return [], errors
    deps, _ = wp_dependency_map(pi_id)
    in_pi = set(order)
    distance: dict[str, int] = {}
    predecessor: dict[str, str] = {}
    for node in order:
        local_deps = [dep for dep in deps.get(node, set()) if dep in in_pi]
        if not local_deps:
            distance[node] = 1
            continue
        best = max(local_deps, key=lambda dep: distance.get(dep, 1))
        distance[node] = distance.get(best, 1) + 1
        predecessor[node] = best

    if not distance:
        return [], []
    end = max(distance, key=distance.get)
    path = [end]
    while end in predecessor:
        end = predecessor[end]
        path.append(end)
    path.reverse()
    return path, []


def wp_size_analysis(wp_id: str) -> dict:
    kind, row = row_for_target(wp_id)
    if kind != "WP":
        raise EosError("planning size requires a work-packet ID")
    path = ROOT / row["path"]
    text = path.read_text(encoding="utf-8")
    refs = referenced_ids(path)
    acceptance = len(re.findall(r"^- \[[ xX]\]", text, flags=re.M))
    headings = len(re.findall(r"^#{2,4}\s+", text, flags=re.M))
    deps, _ = wp_dependency_map(row["pi"])
    dependency_count = len(deps.get(wp_id, set()))
    score = 0
    reasons: list[str] = []

    if len(text) > 6000:
        score += 3
        reasons.append("artifact text exceeds 6000 characters")
    elif len(text) > 3500:
        score += 2
        reasons.append("artifact text exceeds 3500 characters")
    elif len(text) > 2200:
        score += 1
        reasons.append("artifact text exceeds 2200 characters")

    if acceptance > 10:
        score += 3
        reasons.append(f"{acceptance} acceptance/exit checklist items")
    elif acceptance > 6:
        score += 2
        reasons.append(f"{acceptance} acceptance/exit checklist items")
    elif acceptance > 3:
        score += 1
        reasons.append(f"{acceptance} acceptance/exit checklist items")

    if len(refs) > 10:
        score += 2
        reasons.append(f"{len(refs)} governing/reference IDs")
    elif len(refs) > 6:
        score += 1
        reasons.append(f"{len(refs)} governing/reference IDs")

    if dependency_count > 4:
        score += 2
        reasons.append(f"{dependency_count} work-packet dependencies")
    elif dependency_count > 2:
        score += 1
        reasons.append(f"{dependency_count} work-packet dependencies")

    if headings > 16:
        score += 1
        reasons.append(f"{headings} subsections suggest broad scope")

    if score <= 2:
        size = "SMALL"
    elif score <= 5:
        size = "MEDIUM"
    elif score <= 8:
        size = "LARGE"
    else:
        size = "OVERSIZED"

    return {
        "wp": wp_id,
        "size": size,
        "score": score,
        "characters": len(text),
        "acceptance_items": acceptance,
        "references": len(refs),
        "dependencies": dependency_count,
        "subheadings": headings,
        "reasons": reasons,
    }


def planning_check(pi_id: str) -> dict:
    pi = find_row("PI", pi_id)
    if not pi:
        raise EosError(f"Unknown program increment: {pi_id}")

    failures: list[str] = []
    warnings: list[str] = []
    order, dep_errors = topological_wp_order(pi_id)
    failures.extend(dep_errors)

    wcs = [row for row in registry("WC") if row.get("pi") == pi_id]
    wps = pi_work_packets(pi_id)
    if not wcs:
        warnings.append(f"{pi_id} has no work cycles")
    if not wps:
        warnings.append(f"{pi_id} has no work packets")

    for wc in wcs:
        children = [wp for wp in wps if wp.get("wc") == wc["id"]]
        if not children:
            warnings.append(f"{wc['id']} has no work packets")
        if wc["status"] in {"AUTHORIZED", "ACTIVE", "IN_REVIEW", "CLOSED"}:
            parent = find_row("PI", wc["pi"])
            if parent and parent["status"] not in {"AUTHORIZED", "ACTIVE", "IN_REVIEW", "CLOSED"}:
                failures.append(
                    f"{wc['id']} is {wc['status']} while parent {wc['pi']} is {parent['status']}"
                )

    deps, _ = wp_dependency_map(pi_id)
    for wp in wps:
        if wp["status"] in {"READY", "AUTHORIZED", "IN_PROGRESS", "VERIFYING", "IN_REVIEW", "CLOSED"}:
            complete, issues = artifact_is_complete_enough(ROOT / wp["path"])
            if not complete:
                failures.extend(f"{wp['id']}: {issue}" for issue in issues)
        wc = find_row("WC", wp["wc"])
        if wp["status"] in {"AUTHORIZED", "IN_PROGRESS", "VERIFYING", "IN_REVIEW", "CLOSED"}:
            if wc and wc["status"] not in {"AUTHORIZED", "ACTIVE", "IN_REVIEW", "CLOSED"}:
                failures.append(
                    f"{wp['id']} is {wp['status']} while parent {wp['wc']} is {wc['status']}"
                )
        for dep in deps.get(wp["id"], set()):
            dep_row = find_row("WP", dep)
            if dep_row and dep_row.get("pi") != pi_id:
                warnings.append(
                    f"{wp['id']} has cross-PI dependency {dep} in {dep_row.get('pi')}"
                )

        size = wp_size_analysis(wp["id"])
        if size["size"] == "OVERSIZED":
            warnings.append(
                f"{wp['id']} sizing heuristic is OVERSIZED (score {size['score']}); consider decomposition"
            )

    return {
        "pi": pi_id,
        "passed": not failures,
        "failures": failures,
        "warnings": warnings,
        "order": order,
        "work_cycles": [wc["id"] for wc in wcs],
        "work_packets": [wp["id"] for wp in wps],
    }


def cmd_planning_check(args: argparse.Namespace) -> None:
    report = planning_check(args.pi)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"PLANNING CHECK — {args.pi}")
        print(f"Result: {'PASS' if report['passed'] else 'FAIL'}")
        if report["order"]:
            print("Execution order: " + " -> ".join(report["order"]))
        if report["warnings"]:
            print("\nWarnings:")
            for item in report["warnings"]:
                print(f"  WARN {item}")
        if report["failures"]:
            print("\nFailures:")
            for item in report["failures"]:
                print(f"  FAIL {item}")
    if not report["passed"]:
        raise EosError("Planning feasibility check failed")


def cmd_planning_order(args: argparse.Namespace) -> None:
    order, errors = topological_wp_order(args.pi)
    if errors:
        raise EosError("\n- ".join(["Planning dependency error:", *errors]))
    if args.json:
        print(json.dumps({"pi": args.pi, "order": order}, indent=2))
    elif order:
        for index, wp in enumerate(order, start=1):
            print(f"{index:03d}  {wp}")
    else:
        print("No work packets in the requested PI.")


def cmd_planning_critical_path(args: argparse.Namespace) -> None:
    path, errors = critical_path_for_pi(args.pi)
    if errors:
        raise EosError("\n- ".join(["Critical path unavailable:", *errors]))
    if args.json:
        print(json.dumps({"pi": args.pi, "critical_path": path, "length": len(path)}, indent=2))
    else:
        print(f"CRITICAL PATH — {args.pi}")
        print(f"Length: {len(path)} work packet(s)")
        print(" -> ".join(path) if path else "(none)")


def cmd_planning_graph(args: argparse.Namespace) -> None:
    deps, errors = wp_dependency_map(args.pi)
    if errors:
        raise EosError("\n- ".join(["Planning graph error:", *errors]))
    if args.format == "mermaid":
        print("graph TD")
        emitted = False
        for source in sorted(deps):
            if not deps[source]:
                print(f"  {source.replace('-', '_')}[\"{source}\"]")
                emitted = True
            for target in sorted(deps[source]):
                print(
                    f"  {source.replace('-', '_')}[\"{source}\"] "
                    f"--> |depends on| {target.replace('-', '_')}[\"{target}\"]"
                )
                emitted = True
        if not emitted:
            print("  EMPTY[\"No work packets\"]")
        return
    for source in sorted(deps):
        targets = sorted(deps[source])
        print(f"{source}: {', '.join(targets) if targets else '(no WP dependencies)'}")


def cmd_planning_size(args: argparse.Namespace) -> None:
    result = wp_size_analysis(args.wp)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print(f"WORK PACKET SIZE — {args.wp}")
    print(f"Classification: {result['size']} (score {result['score']})")
    print(
        f"characters={result['characters']} acceptance={result['acceptance_items']} "
        f"references={result['references']} dependencies={result['dependencies']} "
        f"subheadings={result['subheadings']}"
    )
    if result["reasons"]:
        print("Signals:")
        for reason in result["reasons"]:
            print(f"  - {reason}")



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
        row = find_row(kind, target)
        old_url = row.get("github_url", "") if row else ""
        update_row(kind, target, github_url=url)
        if old_url != url:
            append_event(
                "ENTITY_PATCHED",
                target=target,
                entity_kind=kind,
                action="github-sync",
                reason="GitHub projection URL updated",
                metadata={"field": "github_url", "from": old_url, "to": url},
            )


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
    append_event(
        "ENTITY_CREATED",
        target=cr_id,
        entity_kind="CR",
        action="change-create",
        to_state="PROPOSED",
        reason=args.reason or "change request created",
        metadata={"row": rows[-1]},
    )
    print(f"Created {cr_id}: {rel(path)}")


def cmd_change_approve(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "CR":
        raise EosError("change approve requires CR-NNNN")
    actor = args.by or os.environ.get("USER") or "human"
    override = enforce_gate(
        "CR_APPROVE",
        args.target,
        force=args.force,
        actor=actor,
        reason=args.reason,
    )
    set_lifecycle_state(
        args.target,
        "APPROVED",
        action="change-approve",
        actor=actor,
        reason=args.reason or (
            f"change approved under {override['id']}" if override else "change approved"
        ),
    )
    if override:
        consume_override(override)
    record_decision(args.target, "change-approve", "APPROVED", actor, args.reason or "change approved")
    print(f"{args.target} APPROVED.")



def cmd_change_apply(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "CR":
        raise EosError("change apply requires CR-NNNN")
    set_lifecycle_state(
        args.target,
        "APPLIED",
        action="change-apply",
        actor=actor_name(),
        reason="approved change has been applied to governed artifacts/implementation",
    )
    print(f"{args.target} APPLIED.")


def cmd_change_close(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "CR":
        raise EosError("change close requires CR-NNNN")
    set_lifecycle_state(
        args.target,
        "CLOSED",
        action="change-close",
        actor=actor_name(),
        reason="change implementation and required verification are complete",
    )
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
    append_event(
        "ENTITY_CREATED",
        target=mnt_id,
        entity_kind="MNT",
        action="maintenance-create",
        to_state="OPEN",
        reason="maintenance item created",
        metadata={"row": rows[-1]},
    )
    print(f"Created {mnt_id}: {rel(path)}")
    print(f"Next: ./scripts/eos maintain plan {mnt_id}")


def cmd_maintain_plan(args: argparse.Namespace) -> None:
    kind, _ = row_for_target(args.target)
    if kind != "MNT":
        raise EosError("maintain plan requires MNT-NNNN")
    set_lifecycle_state(
        args.target,
        "PLANNED",
        action="maintenance-plan",
        actor=actor_name(),
        reason="maintenance resolution has been planned",
    )
    print(f"{args.target} PLANNED.")


def cmd_maintain_start(args: argparse.Namespace) -> None:
    kind, _ = row_for_target(args.target)
    if kind != "MNT":
        raise EosError("maintain start requires MNT-NNNN")
    set_lifecycle_state(
        args.target,
        "IN_PROGRESS",
        action="maintenance-start",
        actor=actor_name(),
        reason="maintenance execution started",
    )
    print(f"{args.target} IN_PROGRESS.")


def cmd_maintain_verify(args: argparse.Namespace) -> None:
    kind, _ = row_for_target(args.target)
    if kind != "MNT":
        raise EosError("maintain verify requires MNT-NNNN")
    set_lifecycle_state(
        args.target,
        "VERIFYING",
        action="maintenance-verify",
        actor=actor_name(),
        reason="maintenance verification started",
    )
    print(f"{args.target} VERIFYING.")


def cmd_maintain_close(args: argparse.Namespace) -> None:
    kind, row = row_for_target(args.target)
    if kind != "MNT":
        raise EosError("maintain close requires MNT-NNNN")
    override = enforce_gate(
        "MNT_CLOSE",
        args.target,
        force=args.force,
        actor=actor_name(),
        reason=getattr(args, "reason", ""),
    )
    set_lifecycle_state(
        args.target,
        "CLOSED",
        action="maintenance-close",
        actor=actor_name(),
        reason=(
            f"maintenance closure under {override['id']}"
            if override
            else "maintenance completion verified"
        ),
    )
    if override:
        consume_override(override)
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
        append_event(
            "ENTITY_CREATED",
            target=rel_id,
            entity_kind="REL",
            action="release-prepare",
            to_state="PROPOSED",
            reason="release candidate prepared",
            metadata={"row": rows[-1]},
        )

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
    verify_ok, report = verify_all(strict=True)
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
        # Advance through the declarative release state machine before tagging.
        current_rel = find_row("REL", rel_id)
        if current_rel and current_rel["status"] == "PROPOSED":
            set_lifecycle_state(
                rel_id,
                "READY",
                action="release-ready",
                actor=actor_name(),
                reason="release readiness gate satisfied",
                    )
        set_lifecycle_state(
            rel_id,
            "RELEASED",
            action="release",
            actor=actor_name(),
            reason=f"release {args.version} finalized",
            )
        run(
            ["git", "add", rel(path), rel(review), REGISTRY_PATHS["REL"], rel(EVENTS_PATH)],
            cwd=ROOT,
        )
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



def cmd_events(args: argparse.Namespace) -> None:
    events = read_events()
    if args.target:
        events = [event for event in events if event.get("target") == args.target]
    if args.limit:
        events = events[-args.limit :]
    if args.json:
        print(json.dumps(events, indent=2, sort_keys=True))
        return
    for event in events:
        print(
            f"{event.get('timestamp','')}  {event.get('event_type',''):<18} "
            f"{event.get('target',''):<20} "
            f"{event.get('from_state','') or '-'} -> {event.get('to_state','') or '-'}  "
            f"{event.get('actor','')}"
        )


def cmd_state_machine(args: argparse.Namespace) -> None:
    target = args.target.upper()
    try:
        kind = kind_for_id(target)
    except EosError:
        kind = target
    if kind not in REGISTRY_PATHS:
        raise EosError("State machine target must be PI, WC, WP, CR, MNT, REL, or an entity ID")
    machine = state_machine(kind)
    if args.json:
        print(json.dumps(machine, indent=2, sort_keys=True))
        return
    print(f"{kind} state machine v{machine.get('version','?')}")
    print(f"initial: {machine.get('initial_state')}")
    print(f"terminal: {', '.join(machine.get('terminal_states', [])) or '(none)'}")
    print("transitions:")
    for source in machine.get("states", []):
        destinations = machine.get("transitions", {}).get(source, [])
        print(f"  {source:<14} -> {', '.join(destinations) or '(terminal)'}")


def cmd_schema(args: argparse.Namespace) -> None:
    name = args.name.lower()
    aliases = {
        "pi": "pi", "wc": "wc", "wp": "wp", "cr": "cr", "mnt": "mnt",
        "rel": "rel", "exec": "exec", "artifact": "artifact", "event": "event",
    }
    if name not in aliases:
        raise EosError("Schema must be one of PI, WC, WP, CR, MNT, REL, EXEC, artifact, event")
    schema = load_json(SCHEMA_DIR / f"{aliases[name]}.schema.json")
    print(json.dumps(schema, indent=2, sort_keys=True))


def cmd_rebuild_state(args: argparse.Namespace) -> None:
    projected = event_projected_state()
    mismatches: list[tuple[str, str, str, str]] = []
    for kind in ("PI", "WC", "WP", "CR", "MNT", "REL", "EXEC"):
        for row in registry(kind):
            key = (kind, row["id"])
            if key not in projected:
                continue
            expected = projected[key]
            actual = row["status"]
            if expected != actual:
                mismatches.append((kind, row["id"], actual, expected))

    if not mismatches:
        print("Lifecycle registry projections match the event ledger.")
        return

    print("Lifecycle state mismatches:")
    for kind, target, actual, expected in mismatches:
        print(f"  {target}: registry={actual} event-ledger={expected}")

    if not args.apply:
        raise EosError("Run with --apply to repair registry/artifact lifecycle state from the event ledger.")

    for kind, target, actual, expected in mismatches:
        row = find_row(kind, target)
        if not row:
            continue
        update_row(kind, target, status=expected)
        sync_artifact_state(ROOT / row["path"], expected)
        append_event(
            "PROJECTION_REPAIRED",
            target=target,
            entity_kind=kind,
            action="rebuild-state",
            from_state=actual,
            to_state=expected,
            actor=actor_name(),
            reason="registry/artifact projection repaired from append-only event ledger",
        )
        print(f"  repaired {target} -> {expected}")


def verify_all(*, strict: bool = False) -> tuple[bool, str]:
    failures: list[str] = []
    warnings: list[str] = []
    lines: list[str] = []

    required = [
        ROOT / "idea.md",
        EOS / "layers.tsv",
        EOS / "workflow.tsv",
        EOS / "artifacts.tsv",
        EOS / "domain-model.json",
        EOS / "version.json",
        EOS / "events.jsonl",
        EOS / "policies" / "core.json",
        EOS / "overrides.tsv",
        ROOT / "governance" / "responsibility-model.md",
        ROOT / "governance" / "canonical-state-model.md",
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
            artifact_schema_path = SCHEMA_DIR / "artifact.schema.json"
            if data and artifact_schema_path.exists():
                failures.extend(
                    validate_simple_schema(
                        load_json(artifact_schema_path),
                        data,
                        label=f"artifact:{aid}",
                    )
                )
            elif not data and p != "idea.md":
                warnings.append(f"registered Markdown artifact has no EOS front matter: {p}")

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
            try:
                states = valid_states(kind)
            except EosError as exc:
                failures.append(str(exc))
                states = set()
            if row["status"] not in states:
                failures.append(f"{rid} has invalid state {row['status']}")
            schema_path = SCHEMA_DIR / f"{kind.lower()}.schema.json"
            if schema_path.exists():
                failures.extend(
                    validate_simple_schema(
                        load_json(schema_path),
                        row,
                        label=f"{kind}:{rid}",
                    )
                )
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

    # Declarative state-machine integrity.
    for kind in ("PI", "WC", "WP", "CR", "MNT", "REL", "EXEC"):
        try:
            machine = state_machine(kind)
            states = set(machine.get("states", []))
            initial = machine.get("initial_state")
            if initial not in states:
                failures.append(f"{kind} state machine initial_state {initial!r} is not declared")
            for terminal in machine.get("terminal_states", []):
                if terminal not in states:
                    failures.append(f"{kind} state machine terminal state {terminal!r} is not declared")
            transitions = machine.get("transitions", {})
            for source in states:
                if source not in transitions:
                    failures.append(f"{kind} state machine missing transition entry for {source}")
                    continue
                for dest in transitions.get(source, []):
                    if dest not in states:
                        failures.append(f"{kind} state machine {source} references unknown destination {dest}")
        except EosError as exc:
            failures.append(str(exc))

    # Append-only event ledger syntax/schema + projection consistency.
    try:
        event_schema = load_json(SCHEMA_DIR / "event.schema.json")
        events = read_events()
        event_ids: set[str] = set()
        for i, event in enumerate(events, start=1):
            event_id = event.get("event_id", "")
            if event_id in event_ids:
                failures.append(f"duplicate event id: {event_id}")
            event_ids.add(event_id)
            failures.extend(
                validate_simple_schema(event_schema, event, label=f"event-line-{i}")
            )
            kind = event.get("entity_kind", "")
            frm = event.get("from_state", "")
            to = event.get("to_state", "")
            if event.get("event_type") == "STATE_TRANSITION" and kind in REGISTRY_PATHS:
                if not transition_allowed(kind, frm, to):
                    failures.append(
                        f"illegal recorded transition in {event_id}: {kind} {frm} -> {to}"
                    )
        projected = event_projected_state()
        for kind in ("PI", "WC", "WP", "CR", "MNT", "REL", "EXEC"):
            for row in registry(kind):
                expected = projected.get((kind, row["id"]))
                if expected and expected != row["status"]:
                    failures.append(
                        f"{row['id']} projection drift: registry={row['status']} event-ledger={expected}"
                    )
        lines.append(f"events: {len(events)}")
    except EosError as exc:
        failures.append(str(exc))

    # Policy-as-code definitions and override registry.
    try:
        policy = policy_document()
        gates = policy.get("gates", {})
        if not gates:
            failures.append("policy document contains no gates")
        for gate_name, checks in gates.items():
            if not re.fullmatch(r"[A-Z][A-Z0-9_]+", gate_name):
                failures.append(f"invalid policy gate name: {gate_name}")
            if not isinstance(checks, list) or not checks:
                failures.append(f"policy gate {gate_name} has no checks")
            for spec in checks if isinstance(checks, list) else []:
                if not isinstance(spec, dict) or not spec.get("check"):
                    failures.append(f"policy gate {gate_name} contains malformed check")
    except EosError as exc:
        failures.append(str(exc))

    try:
        override_schema = load_json(SCHEMA_DIR / "override.schema.json")
        seen_overrides: set[str] = set()
        for row in override_rows():
            oid = row.get("id", "")
            if oid in seen_overrides:
                failures.append(f"duplicate override id: {oid}")
            seen_overrides.add(oid)
            failures.extend(validate_simple_schema(override_schema, row, label=f"override:{oid}"))
            if row.get("status") not in {"ACTIVE", "CONSUMED", "EXPIRED"}:
                failures.append(f"{oid} has invalid override status {row.get('status')}")
            if row.get("gate") and row.get("gate") not in policy_document().get("gates", {}):
                failures.append(f"{oid} references unknown policy gate {row.get('gate')}")
        lines.append(f"overrides: {len(seen_overrides)}")
    except EosError as exc:
        failures.append(str(exc))

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

    open_stale = [row for row in stale_rows() if row.get("status") == "OPEN"]
    lines.append(f"open stale records: {len(open_stale)}")
    if open_stale:
        messages = [
            f"{row['id']} target={row['target']} source={row['source']}"
            for row in open_stale
        ]
        if strict:
            failures.extend(f"unresolved stale dependency: {message}" for message in messages)
        else:
            warnings.extend(f"unresolved stale dependency: {message}" for message in messages)

    coverage = trace_coverage_report()
    lines.append(f"trace coverage: {coverage['score']:.1f}%")
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


def cmd_verify(args: argparse.Namespace) -> None:
    ok, report = verify_all(strict=args.strict)
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
    if EOS_VERSION_PATH.exists():
        versions = load_json(EOS_VERSION_PATH)
        print(
            f"\nEOS tool/schema: "
            f"{versions.get('eos_tool_version','?')} / {versions.get('eos_schema_version','?')}"
        )
    print(f"root: {ROOT}")
    print(f"branch: {current_branch() or '(unknown)'}")
    print(f"HEAD: {commit_sha() or '(none)'}")
    print(f"git: {git_status()}")


TOP_LEVEL_COMPLETION_COMMANDS = (
    "layers", "status", "next", "prompt", "complete", "reopen", "version",
    "history", "rollback", "checkpoint", "plan", "create-wc", "create-wp",
    "ready", "authorize", "start", "preflight", "worktree", "execute", "execution", "contract", "codex", "validate", "review", "close",
    "close-cycle", "close-pi", "trace", "impact", "github-sync", "change",
    "maintain", "release", "planning", "policy", "gate", "override", "stale", "events",
    "state-machine", "schema", "rebuild-state", "verify", "doctor",
    "responsibilities", "completion",
)

COMMAND_COMPLETION_OPTIONS = {
    "plan": ("--title", "--objective"),
    "create-wc": ("--pi", "--title"),
    "create-wp": ("--wc", "--domain", "--title"),
    "ready": ("--reason", "--by"),
    "authorize": ("--force", "--reason", "--by"),
    "codex": ("--force", "--no-worktree", "--base", "--actor", "--json"),
    "preflight": ("--no-worktree", "--base", "--json"),
    "execute": ("--no-worktree", "--base", "--actor", "--json"),
    "worktree": ("--base", "--path", "--force"),
    "execution": ("--target", "--json", "--reason", "--by"),
    "contract": ("--json",),
    "close": ("--force", "--reason", "--by"),
    "close-cycle": ("--force", "--reason", "--by"),
    "close-pi": ("--force", "--reason", "--by"),
    "github-sync": ("--apply", "--project", "--owner"),
    "release": ("--publish", "--force"),
    "events": ("--limit", "--json"),
    "state-machine": ("--json",),
    "rebuild-state": ("--apply",),
    "verify": ("--strict",),
    "trace": ("--json",),
    "impact": ("--json",),
    "stale": ("--all", "--by", "--reason"),
    "planning": ("--json", "--format"),
    "gate": ("--json",),
    "override": ("--active", "--by", "--reason", "--expires"),
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
    previous = prior[-1] if prior else ""

    # Subcommand discovery.
    if command == "worktree" and len(args) == 1:
        return filter_completion(("create", "list", "remove"), current)
    if command == "execution" and len(args) == 1:
        return filter_completion(("list", "show", "ingest", "check", "close", "abort", "environment"), current)
    if command == "contract" and len(args) == 1:
        return filter_completion(("verify", "show"), current)
    if command == "change" and len(args) == 1:
        return filter_completion(("create", "approve", "apply", "close"), current)
    if command == "maintain" and len(args) == 1:
        return filter_completion(("create", "plan", "start", "verify", "close"), current)
    if command == "planning" and len(args) == 1:
        return filter_completion(("check", "order", "critical-path", "graph", "size"), current)
    if command == "policy" and len(args) == 1:
        return filter_completion(("list", "show"), current)
    if command == "gate" and len(args) == 1:
        return filter_completion(("check", "explain"), current)
    if command == "override" and len(args) == 1:
        return filter_completion(("create", "list", "expire"), current)
    if command == "stale" and len(args) == 1:
        return filter_completion(("list", "clear"), current)
    if command == "completion" and len(args) == 1:
        return filter_completion(("bash", "zsh", "fish", "write", "install"), current)

    # Values for preceding options.
    if previous == "--pi":
        return filter_completion(completion_ids("PI"), current)
    if previous == "--wc":
        return filter_completion(completion_ids("WC"), current)
    if previous == "--domain":
        return filter_completion(completion_domains(), current.upper())
    if previous == "--format" and command == "planning":
        return filter_completion(("text", "mermaid"), current)
    if command == "completion" and args and args[0] == "install" and len(args) <= 2:
        return filter_completion(("bash", "zsh", "fish", "all"), current)

    # Context-sensitive options.
    if current.startswith("-"):
        options = [o for o in COMMAND_COMPLETION_OPTIONS.get(command, ()) if o not in args]
        if command == "change" and args:
            if args[0] == "create":
                options += [o for o in ("--reason",) if o not in args]
            elif args[0] == "approve":
                options += [o for o in ("--force", "--reason", "--by") if o not in args]
        elif command == "maintain" and args:
            if args[0] == "create":
                options += [o for o in ("--context",) if o not in args]
            elif args[0] == "close":
                options += [o for o in ("--force", "--reason") if o not in args]
        elif command == "override" and args:
            if args[0] == "create":
                options += [o for o in ("--by", "--reason", "--expires") if o not in args]
            elif args[0] == "list":
                options += [o for o in ("--active",) if o not in args]
        elif command == "gate" and args:
            options += [o for o in ("--json",) if o not in args]
        elif command == "stale" and args:
            if args[0] == "list":
                options += [o for o in ("--all",) if o not in args]
            elif args[0] == "clear":
                options += [o for o in ("--by", "--reason") if o not in args]
        elif command == "planning" and args:
            if args[0] in {"check", "order", "critical-path", "size"}:
                options += [o for o in ("--json",) if o not in args]
            elif args[0] == "graph":
                options += [o for o in ("--format",) if o not in args]
        return filter_completion(options, current)

    # Bootstrap/versioning commands.
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

    # Planning/execution lifecycle.
    if command == "plan":
        if not current.startswith("-") and not prior:
            next_id = f"PI-{next_number('PI', 3):03d}"
            return filter_completion([next_id], current)
        return []
    if command == "ready":
        return filter_completion(completion_ids("PI", "WC", "WP"), current)
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
    if command == "trace":
        return filter_completion(["coverage", *completion_artifact_ids()], current)
    if command in {"impact", "events"}:
        return filter_completion(completion_artifact_ids(), current)
    if command == "state-machine":
        values = ["PI", "WC", "WP", "CR", "MNT", "REL", "EXEC"] + completion_ids(
            "PI", "WC", "WP", "CR", "MNT", "REL", "EXEC"
        )
        return filter_completion(values, current.upper())
    if command == "schema":
        return filter_completion(
            ("PI", "WC", "WP", "CR", "MNT", "REL", "EXEC", "artifact", "event", "override"),
            current,
        )
    if command == "release":
        if not current.startswith("-") and not prior:
            return filter_completion(completion_release_versions(), current)
        return []

    if command == "planning" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd in {"check", "order", "critical-path", "graph"} and len(subargs) <= 1:
            return filter_completion(completion_ids("PI"), subcurrent)
        if subcmd == "size" and len(subargs) <= 1:
            return filter_completion(completion_ids("WP"), subcurrent)
        return []

    # Policy/gates/overrides.
    if command == "policy" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "show" and len(subargs) <= 1:
            return filter_completion(sorted(policy_document().get("gates", {}).keys()), subcurrent.upper())
        return []

    if command == "gate" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd in {"check", "explain"}:
            if len(subargs) <= 1:
                return filter_completion(sorted(policy_document().get("gates", {}).keys()), subcurrent.upper())
            if len(subargs) == 2:
                return filter_completion(completion_ids("PI", "WC", "WP", "CR", "MNT", "REL"), subcurrent)
        return []

    if command == "override" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "create":
            if len(subargs) <= 1:
                return filter_completion(completion_ids("PI", "WC", "WP", "CR", "MNT", "REL"), subcurrent)
            if len(subargs) == 2:
                return filter_completion(sorted(policy_document().get("gates", {}).keys()), subcurrent.upper())
        if subcmd == "list" and len(subargs) <= 1:
            return filter_completion(completion_ids("PI", "WC", "WP", "CR", "MNT", "REL"), subcurrent)
        if subcmd == "expire" and len(subargs) <= 1:
            return filter_completion(
                [r["id"] for r in override_rows() if r.get("status") == "ACTIVE"],
                subcurrent.upper(),
            )
        return []

    if command == "stale" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "list" and len(subargs) <= 1:
            values = sorted({r["target"] for r in stale_rows()} | {r["source"] for r in stale_rows()})
            return filter_completion(values, subcurrent)
        if subcmd == "clear" and len(subargs) <= 1:
            values = [r["id"] for r in stale_rows() if r.get("status") == "OPEN"]
            return filter_completion(values, subcurrent.upper())
        return []

    # EOSE Execution v2 subcommands.
    if command in {"preflight", "execute", "codex"}:
        return filter_completion(completion_ids("WP"), current)

    if command == "worktree" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd in {"create", "remove"} and len(subargs) <= 1:
            return filter_completion(completion_ids("WP"), subcurrent)
        return []

    if command == "execution" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd in {"show", "ingest", "check", "close", "abort", "environment"} and len(subargs) <= 1:
            return filter_completion(completion_ids("EXEC"), subcurrent)
        return []

    if command == "contract" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd in {"verify", "show"} and len(subargs) <= 1:
            return filter_completion(completion_ids("EXEC"), subcurrent)
        return []

    # Change/maintenance subcommands.
    if command == "change" and args:
        subcmd = args[0]
        subargs = args[1:]
        subcurrent = subargs[-1] if subargs else ""
        if subcmd == "create" and len(subargs) <= 1:
            return filter_completion(completion_artifact_ids(), subcurrent)
        if subcmd in {"approve", "apply", "close"} and len(subargs) <= 1:
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
        if subcmd in {"plan", "start", "verify", "close"} and len(subargs) <= 1:
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

    p = sub.add_parser("ready", help="Declare a PI/WC/WP definition ready for its next gate")
    p.add_argument("target")
    p.add_argument("--reason", default="")
    p.add_argument("--by", default="")
    p.set_defaults(func=cmd_ready)

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

    p = sub.add_parser("trace", help="Show typed traceability or coverage")
    p.add_argument("target", help="Artifact ID or literal 'coverage'")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_trace)

    p = sub.add_parser("impact", help="Show typed transitive downstream impact of an artifact")
    p.add_argument("target")
    p.add_argument("--json", action="store_true")
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
    p = change_sub.add_parser("apply")
    p.add_argument("target")
    p.set_defaults(func=cmd_change_apply)
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
    p = maintain_sub.add_parser("plan")
    p.add_argument("target")
    p.set_defaults(func=cmd_maintain_plan)
    p = maintain_sub.add_parser("start")
    p.add_argument("target")
    p.set_defaults(func=cmd_maintain_start)
    p = maintain_sub.add_parser("verify")
    p.add_argument("target")
    p.set_defaults(func=cmd_maintain_verify)
    p = maintain_sub.add_parser("close")
    p.add_argument("target")
    p.add_argument("--force", action="store_true")
    p.add_argument("--reason", default="")
    p.set_defaults(func=cmd_maintain_close)

    p = sub.add_parser("release", help="Prepare/finalize a governed release")
    p.add_argument("version")
    p.add_argument("--publish", action="store_true", help="Push and create GitHub Release")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_release)

    planning = sub.add_parser("planning", help="Analyze PI/WC/WP dependency feasibility and execution order")
    planning_sub = planning.add_subparsers(dest="planning_command", required=True)
    p = planning_sub.add_parser("check")
    p.add_argument("pi")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_planning_check)
    p = planning_sub.add_parser("order")
    p.add_argument("pi")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_planning_order)
    p = planning_sub.add_parser("critical-path")
    p.add_argument("pi")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_planning_critical_path)
    p = planning_sub.add_parser("graph")
    p.add_argument("pi")
    p.add_argument("--format", choices=("text", "mermaid"), default="text")
    p.set_defaults(func=cmd_planning_graph)
    p = planning_sub.add_parser("size")
    p.add_argument("wp")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_planning_size)

    policy = sub.add_parser("policy", help="Inspect policy-as-code gate definitions")
    policy_sub = policy.add_subparsers(dest="policy_command", required=True)
    p = policy_sub.add_parser("list")
    p.set_defaults(func=cmd_policy_list)
    p = policy_sub.add_parser("show")
    p.add_argument("gate")
    p.set_defaults(func=cmd_policy_show)

    gate = sub.add_parser("gate", help="Evaluate/explain a named policy gate")
    gate_sub = gate.add_subparsers(dest="gate_command", required=True)
    for gate_action in ("check", "explain"):
        p = gate_sub.add_parser(gate_action)
        p.add_argument("gate")
        p.add_argument("target")
        p.add_argument("--json", action="store_true")
        p.set_defaults(func=cmd_gate)

    override = sub.add_parser("override", help="Create/list/expire durable human gate overrides")
    override_sub = override.add_subparsers(dest="override_command", required=True)
    p = override_sub.add_parser("create")
    p.add_argument("target")
    p.add_argument("gate")
    p.add_argument("--by", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--expires", default="")
    p.set_defaults(func=cmd_override_create)
    p = override_sub.add_parser("list")
    p.add_argument("target", nargs="?")
    p.add_argument("--active", action="store_true")
    p.set_defaults(func=cmd_override_list)
    p = override_sub.add_parser("expire")
    p.add_argument("override_id")
    p.set_defaults(func=cmd_override_expire)

    stale = sub.add_parser("stale", help="Inspect/clear stale dependency records")
    stale_sub = stale.add_subparsers(dest="stale_command", required=True)
    p = stale_sub.add_parser("list")
    p.add_argument("target", nargs="?")
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_stale_list)
    p = stale_sub.add_parser("clear")
    p.add_argument("stale_id")
    p.add_argument("--by", required=True)
    p.add_argument("--reason", required=True)
    p.set_defaults(func=cmd_stale_clear)

    p = sub.add_parser("events", help="Inspect the append-only EOS lifecycle event ledger")
    p.add_argument("target", nargs="?")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_events)

    p = sub.add_parser("state-machine", help="Inspect declarative lifecycle transitions")
    p.add_argument("target")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_state_machine)

    p = sub.add_parser("schema", help="Inspect an EOS entity/event schema")
    p.add_argument("name")
    p.set_defaults(func=cmd_schema)

    p = sub.add_parser("rebuild-state", help="Compare/repair lifecycle projections from the event ledger")
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_rebuild_state)

    p = sub.add_parser("verify", help="Verify EOS registry/schema/state/event/traceability integrity")
    p.add_argument("--strict", action="store_true")
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
    ensure_event_ledger_seeded()
    record_tool_upgrade_if_needed()
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

if [[ -f tools/eos/execution_v2.py ]]; then
  EOSE_PY_BACKUP=".eos/history/tooling/execution-v2-pre-v0.6-$(date -u +%Y%m%dT%H%M%SZ).py"
  mkdir -p "$(dirname "$EOSE_PY_BACKUP")"
  cp tools/eos/execution_v2.py "$EOSE_PY_BACKUP"
fi

cat > tools/eos/execution_v2.py <<'EOSE_PY'
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import fnmatch
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

UTC = dt.timezone.utc
EXEC_FIELDS = [
    "id", "path", "target", "status", "branch", "worktree", "baseline_commit",
    "governing_hash", "contract_hash", "result_path", "actor", "created", "updated",
]
ACTIVE_EXEC_STATES = {"PREPARED", "RUNNING", "RESULT_INGESTED", "VERIFIED", "BLOCKED"}
TERMINAL_EXEC_STATES = {"CLOSED", "ABORTED", "FAILED", "INVALIDATED"}
SYSTEM_FORBIDDEN_DEFAULT = [".git", ".git/**", ".eos", ".eos/**"]
GOVERNED_DEFAULT = [
    "idea.md", "vision/**", "product/**", "architecture/**", "specifications/**",
    "governance/**", "engineering/increments/**", "engineering/work-cycles/**",
    "engineering/work-packets/**",
]


class EoseError(RuntimeError):
    pass


def now_iso() -> str:
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(args: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


def discover_root() -> Path:
    explicit = os.environ.get("EOS_ROOT", "").strip()
    if explicit:
        return Path(explicit).resolve()
    candidate = Path(__file__).resolve().parents[2]
    if (candidate / ".eos").exists():
        return candidate
    try:
        return Path(run(["git", "rev-parse", "--show-toplevel"]).stdout.strip()).resolve()
    except Exception:
        return candidate


ROOT = discover_root()
EOS = ROOT / ".eos"
REGISTRY = EOS / "executions.tsv"
EVENTS = EOS / "events.jsonl"
POLICY = EOS / "execution-policy.json"
LOCKS = EOS / "locks"
EXEC_DIR = EOS / "executions"
CONTRACTS = EOS / "contracts"
EVIDENCE = EOS / "evidence"
CORE = ROOT / "tools" / "eos" / "eos.py"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def actor_name(explicit: str = "") -> str:
    return explicit or os.environ.get("EOS_ACTOR") or os.environ.get("USER") or "unknown"


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
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def rows() -> list[dict[str, str]]:
    return read_tsv(REGISTRY)


def find_exec(exec_id: str) -> dict[str, str]:
    for row in rows():
        if row.get("id") == exec_id:
            return row
    raise EoseError(f"Unknown execution session: {exec_id}")


def update_exec(exec_id: str, **updates: str) -> dict[str, str]:
    all_rows = rows()
    for row in all_rows:
        if row.get("id") == exec_id:
            row.update(updates)
            row["updated"] = now_iso()
            write_tsv(REGISTRY, EXEC_FIELDS, all_rows)
            sync_session_json(row)
            return row
    raise EoseError(f"Unknown execution session: {exec_id}")


def append_event(event_type: str, *, target: str = "", action: str = "", from_state: str = "", to_state: str = "", actor: str = "", reason: str = "", metadata: dict | None = None) -> None:
    event = {
        "event_id": "EVT-" + uuid.uuid4().hex.upper(),
        "schema_version": "1.0.0",
        "timestamp": now_iso(),
        "event_type": event_type,
        "actor": actor_name(actor),
        "target": target,
        "entity_kind": "EXEC" if target.startswith("EXEC-") else "",
        "action": action,
        "from_state": from_state,
        "to_state": to_state,
        "reason": reason,
        "commit": git_head(ROOT),
        "metadata": metadata or {},
    }
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())


def load_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        if default is not None:
            return dict(default)
        raise EoseError(f"Missing {rel(path)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EoseError(f"Invalid JSON in {rel(path)}: {exc}") from exc
    if not isinstance(value, dict):
        raise EoseError(f"Expected object in {rel(path)}")
    return value


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def governing_content_hash(path: Path) -> str:
    """Hash semantic governed content while ignoring operational lifecycle metadata."""
    if path.suffix.lower() != ".md":
        return sha256_file(path)
    text = path.read_text(encoding="utf-8", errors="strict")
    lines = text.splitlines()
    normalized: list[str] = []
    in_frontmatter = bool(lines and lines[0].strip() == "---")
    frontmatter_closed = not in_frontmatter
    for i, line in enumerate(lines):
        if in_frontmatter and i == 0:
            normalized.append(line); continue
        if in_frontmatter and not frontmatter_closed:
            if line.strip() == "---":
                frontmatter_closed = True; normalized.append(line); continue
            if re.match(r"^(status|updated):\s*", line):
                continue
            normalized.append(line); continue
        if re.match(r"^\*\*State:\*\*\s*", line):
            continue
        normalized.append(line)
    return sha256_bytes(("\n".join(normalized).rstrip() + "\n").encode("utf-8"))


def git_head(cwd: Path) -> str:
    try:
        return run(["git", "rev-parse", "HEAD"], cwd=cwd).stdout.strip()
    except Exception:
        return ""


def git_branch(cwd: Path) -> str:
    try:
        return run(["git", "branch", "--show-current"], cwd=cwd).stdout.strip()
    except Exception:
        return ""


def git_status(cwd: Path) -> str:
    try:
        return run(["git", "status", "--porcelain"], cwd=cwd).stdout
    except Exception:
        return ""


def non_eos_dirty_paths(cwd: Path) -> list[str]:
    dirty: list[str] = []
    for line in git_status(cwd).splitlines():
        if len(line) < 4:
            continue
        raw = line[3:].strip()
        # Rename status uses `old -> new`; inspect the destination path.
        path = raw.split(" -> ")[-1]
        if path == ".eos" or path.startswith(".eos/"):
            continue
        dirty.append(path)
    return sorted(set(dirty))


def core(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["EOS_ROOT"] = str(ROOT)
    return subprocess.run([sys.executable, str(CORE), *args], cwd=ROOT, env=env, text=True, capture_output=True, check=check)


def wp_row(target: str) -> dict[str, str]:
    for row in read_tsv(EOS / "work-packets.tsv"):
        if row.get("id") == target:
            return row
    raise EoseError(f"Unknown work packet: {target}")


def artifact_registry() -> list[dict[str, str]]:
    return read_tsv(EOS / "artifacts.tsv")


def artifact_path_for_id(target: str) -> Path | None:
    for table in ("program-increments.tsv", "work-cycles.tsv", "work-packets.tsv", "change-requests.tsv", "maintenance.tsv", "releases.tsv"):
        for row in read_tsv(EOS / table):
            if row.get("id") == target and row.get("path"):
                p = ROOT / row["path"]
                if p.exists():
                    return p
    for row in artifact_registry():
        if row.get("artifact_id") == target and row.get("path"):
            p = ROOT / row["path"]
            if p.exists():
                return p
    return None


ID_RE = re.compile(r"\b(?:REQ-[A-Z0-9][A-Z0-9-]*|CAP-[A-Z0-9][A-Z0-9-]*|QA-[A-Z0-9][A-Z0-9-]*|ADR-\d{4}|SPEC-[A-Z0-9][A-Z0-9-]*|PI-\d{3}|WC-\d{4}|WP(?:-[A-Z][A-Z0-9]*)?-\d{4}|RISK-\d{3,4})\b")


def referenced_ids(path: Path) -> list[str]:
    if not path.exists():
        return []
    own = ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'^artifact_id:\s*["\']?([^"\'\n]+)', text, flags=re.M)
    if m:
        own = m.group(1).strip()
    return sorted(x for x in set(ID_RE.findall(text)) if x != own)


def governing_paths(target: str) -> list[Path]:
    wp = wp_row(target)
    wp_path = ROOT / wp["path"]
    ids = set(referenced_ids(wp_path))
    for parent_key in ("pi", "wc"):
        if wp.get(parent_key):
            ids.add(wp[parent_key])
    paths: set[Path] = {wp_path}
    for rid in ids:
        p = artifact_path_for_id(rid)
        if p and p.exists():
            paths.add(p)
    return sorted(paths, key=lambda p: rel(p))


def governing_manifest(target: str, *, root: Path = ROOT) -> list[dict[str, str]]:
    manifest: list[dict[str, str]] = []
    for source in governing_paths(target):
        rp = rel(source)
        p = root / rp
        if not p.exists():
            manifest.append({"path": rp, "sha256": "MISSING"})
        else:
            manifest.append({"path": rp, "sha256": governing_content_hash(p)})
    return manifest


def manifest_hash(manifest: list[dict[str, str]]) -> str:
    return sha256_bytes(canonical_bytes(manifest))


def execution_policy() -> dict:
    default = {
        "branch_prefix": "wp/",
        "worktree_root": f"../.{ROOT.name}-worktrees",
        "require_clean_current_tree_for_no_worktree": True,
        "system_forbidden_paths": SYSTEM_FORBIDDEN_DEFAULT,
        "governed_paths": GOVERNED_DEFAULT,
    }
    value = load_json(POLICY, default)
    for k, v in default.items():
        value.setdefault(k, v)
    return value


def scope_directives(target: str) -> dict[str, list[str]]:
    path = ROOT / wp_row(target)["path"]
    text = path.read_text(encoding="utf-8", errors="ignore")
    out = {"allowed": [], "forbidden": [], "allowed_governed": []}
    patterns = {
        "allowed-path": "allowed",
        "forbidden-path": "forbidden",
        "allowed-governed-path": "allowed_governed",
    }
    for raw in text.splitlines():
        m = re.match(r"^\s*-\s*(allowed-path|forbidden-path|allowed-governed-path):\s*`?([^`#]+?)`?\s*$", raw)
        if m:
            out[patterns[m.group(1)]].append(m.group(2).strip())
    if not out["allowed"]:
        out["allowed"] = ["*", "**/*"]
    return out


def normalize_repo_path(path: str) -> str:
    return path[2:] if path.startswith("./") else path


def path_matches(path: str, patterns: list[str]) -> bool:
    normalized = normalize_repo_path(path)
    return any(fnmatch.fnmatchcase(normalized, normalize_repo_path(p)) for p in patterns)


def scope_check(target: str, changed_files: list[str]) -> dict:
    directives = scope_directives(target)
    policy = execution_policy()
    system_forbidden = list(policy.get("system_forbidden_paths", SYSTEM_FORBIDDEN_DEFAULT))
    governed = list(policy.get("governed_paths", GOVERNED_DEFAULT))
    violations: list[dict[str, str]] = []
    for raw in sorted(set(changed_files)):
        path = normalize_repo_path(raw)
        if path_matches(path, system_forbidden):
            violations.append({"path": path, "reason": "EOS/Git internal path is never implementation scope"})
            continue
        if not path_matches(path, directives["allowed"]):
            violations.append({"path": path, "reason": "not matched by any allowed-path directive"})
            continue
        if path_matches(path, directives["forbidden"]):
            violations.append({"path": path, "reason": "matched forbidden-path directive"})
            continue
        if path_matches(path, governed) and not path_matches(path, directives["allowed_governed"]):
            violations.append({"path": path, "reason": "governed artifact changed without allowed-governed-path authorization"})
    return {"passed": not violations, "directives": directives, "violations": violations}


def branch_for(target: str) -> str:
    prefix = str(execution_policy().get("branch_prefix", "wp/"))
    suffix = target.removeprefix("WP-").lower().replace("_", "-")
    return prefix + suffix


def worktree_root() -> Path:
    raw = str(execution_policy().get("worktree_root", f"../.{ROOT.name}-worktrees"))
    raw = raw.replace("{repo}", ROOT.name)
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (ROOT / p).resolve()
    return p


def worktree_for(target: str) -> Path:
    return worktree_root() / target.lower()


def git_worktrees() -> list[dict[str, str]]:
    try:
        raw = run(["git", "worktree", "list", "--porcelain"], cwd=ROOT).stdout
    except Exception:
        return []
    out: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in raw.splitlines() + [""]:
        if not line:
            if current:
                out.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    return out


def create_worktree(target: str, *, base: str = "HEAD", custom_path: str = "") -> tuple[str, Path]:
    branch = branch_for(target)
    path = Path(custom_path).expanduser().resolve() if custom_path else worktree_for(target)
    if path.exists() and any(Path(w.get("worktree", "")).resolve() == path for w in git_worktrees() if w.get("worktree")):
        return branch, path
    if path.exists() and any(path.iterdir()):
        raise EoseError(f"Worktree destination is not empty: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    branch_exists = run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=ROOT, check=False).returncode == 0
    base_commit = run(["git", "rev-parse", "--verify", f"{base}^{{commit}}"], cwd=ROOT).stdout.strip()
    if branch_exists:
        branch_head = run(["git", "rev-parse", branch], cwd=ROOT).stdout.strip()
        if branch_head != base_commit:
            already_integrated = run(["git", "merge-base", "--is-ancestor", branch_head, base_commit], cwd=ROOT, check=False).returncode == 0
            if not already_integrated:
                raise EoseError(f"Existing execution branch {branch} contains unmerged/divergent work ({branch_head}); refusing to reset it to {base_commit}")
            run(["git", "branch", "-f", branch, base_commit], cwd=ROOT)
        run(["git", "worktree", "add", str(path), branch], cwd=ROOT)
    else:
        run(["git", "worktree", "add", "-b", branch, str(path), base_commit], cwd=ROOT)
    append_event("WORKTREE_CREATED", target=target, action="worktree-create", reason="isolated execution worktree created", metadata={"branch": branch, "worktree": str(path), "base": base})
    return branch, path


def remove_worktree(target: str, *, force: bool = False) -> None:
    active = active_exec_for(target)
    if active and not force:
        raise EoseError(f"Cannot remove worktree while active execution exists: {', '.join(r['id'] for r in active)}")
    candidates = [r for r in rows() if r.get("target") == target and r.get("worktree")]
    path = Path(candidates[-1]["worktree"]) if candidates else worktree_for(target)
    if path.exists():
        args = ["git", "worktree", "remove"]
        if force:
            args.append("--force")
        args.append(str(path))
        run(args, cwd=ROOT)
        append_event("WORKTREE_REMOVED", target=target, action="worktree-remove", reason="execution worktree removed", metadata={"worktree": str(path), "force": force})


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


@contextmanager
def target_lock(target: str, action: str):
    LOCKS.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", target)
    path = LOCKS / f"{safe}.lock.json"
    payload = {"target": target, "action": action, "pid": os.getpid(), "host": socket.gethostname(), "actor": actor_name(), "created": now_iso()}
    fd = None
    for attempt in range(2):
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            break
        except FileExistsError:
            try:
                existing = load_json(path)
            except Exception:
                existing = {}
            if attempt == 0 and existing.get("host") == socket.gethostname() and not process_alive(int(existing.get("pid", 0) or 0)):
                path.unlink(missing_ok=True)
                continue
            raise EoseError(f"Concurrent EOS mutation lock exists for {target}: {path} ({existing})")
    assert fd is not None
    try:
        os.write(fd, canonical_bytes(payload))
        os.fsync(fd)
        os.close(fd)
        fd = None
        yield
    finally:
        if fd is not None:
            os.close(fd)
        path.unlink(missing_ok=True)


def stale_for(target: str) -> list[dict[str, str]]:
    return [r for r in read_tsv(EOS / "stale.tsv") if r.get("target") == target and r.get("status") == "OPEN"]


def active_exec_for(target: str) -> list[dict[str, str]]:
    return [r for r in rows() if r.get("target") == target and r.get("status") in ACTIVE_EXEC_STATES]


def preflight(target: str, *, no_worktree: bool = False, base: str = "HEAD") -> dict:
    checks: list[dict[str, object]] = []
    try:
        wp = wp_row(target)
        checks.append({"check": "work_packet_registered", "passed": True, "detail": wp.get("path", "")})
    except EoseError as exc:
        return {"target": target, "passed": False, "checks": [{"check": "work_packet_registered", "passed": False, "detail": str(exc)}]}
    checks.append({"check": "state_authorized", "passed": wp.get("status") in {"AUTHORIZED", "IN_PROGRESS"}, "detail": wp.get("status", "")})
    git_ok = (ROOT / ".git").exists() or run(["git", "rev-parse", "--git-dir"], cwd=ROOT, check=False).returncode == 0
    checks.append({"check": "git_repository", "passed": git_ok, "detail": str(ROOT)})
    head = git_head(ROOT)
    checks.append({"check": "baseline_commit", "passed": bool(head), "detail": head or "no HEAD commit"})
    dirty = non_eos_dirty_paths(ROOT)
    governing_rel = {item["path"] for item in governing_manifest(target)}
    dirty_governing = sorted(set(dirty) & governing_rel)
    other_dirty = sorted(set(dirty) - governing_rel)
    checks.append({"check": "governing_baseline_committed", "passed": not dirty_governing, "detail": ", ".join(dirty_governing) or "all governing inputs committed"})
    checks.append({"check": "other_uncommitted_project_state", "passed": True, "detail": ("warning: not included in isolated worktree baseline: " + ", ".join(other_dirty)) if other_dirty else "none"})
    stale = stale_for(target)
    checks.append({"check": "no_open_stale_dependencies", "passed": not stale, "detail": ", ".join(r.get("id", "") for r in stale) or "none"})
    active = active_exec_for(target)
    checks.append({"check": "single_active_execution", "passed": not active, "detail": ", ".join(r.get("id", "") for r in active) or "none"})
    gov = governing_manifest(target)
    missing = [x["path"] for x in gov if x["sha256"] == "MISSING"]
    checks.append({"check": "governing_inputs_present", "passed": not missing, "detail": ", ".join(missing) or f"{len(gov)} input(s)"})
    base_proc = run(["git", "rev-parse", "--verify", f"{base}^{{commit}}"], cwd=ROOT, check=False)
    base_ok = base_proc.returncode == 0
    base_commit = base_proc.stdout.strip() if base_ok else ""
    checks.append({"check": "base_ref_resolves", "passed": base_ok, "detail": f"{base} -> {base_commit}" if base_ok else base})
    if no_worktree:
        clean = not bool(git_status(ROOT).strip())
        required = bool(execution_policy().get("require_clean_current_tree_for_no_worktree", True))
        checks.append({"check": "current_tree_clean", "passed": clean or not required, "detail": "clean" if clean else "dirty"})
    else:
        path = worktree_for(target)
        linked = next((w for w in git_worktrees() if w.get("worktree") and Path(w["worktree"]).resolve() == path.resolve()), None)
        if linked:
            wt_clean = not bool(git_status(path).strip())
            wt_head = git_head(path)
            wt_branch = git_branch(path)
            expected_branch = branch_for(target)
            reusable = wt_clean and base_ok and wt_head == base_commit and wt_branch == expected_branch
            detail = f"{path}; branch={wt_branch}; head={wt_head}; clean={wt_clean}; expected_branch={expected_branch}; expected_head={base_commit}"
            checks.append({"check": "existing_worktree_reusable", "passed": reusable, "detail": detail})
        else:
            conflict = path.exists() and any(path.iterdir())
            checks.append({"check": "worktree_destination_available", "passed": not conflict, "detail": str(path)})
            expected_branch = branch_for(target)
            branch_exists = run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{expected_branch}"], cwd=ROOT, check=False).returncode == 0
            if branch_exists and base_ok:
                branch_head = run(["git", "rev-parse", expected_branch], cwd=ROOT).stdout.strip()
                integrated = branch_head == base_commit or run(["git", "merge-base", "--is-ancestor", branch_head, base_commit], cwd=ROOT, check=False).returncode == 0
                checks.append({"check": "existing_branch_safe_to_reuse", "passed": integrated, "detail": f"branch={expected_branch}; branch_head={branch_head}; base={base_commit}; integrated={integrated}"})
    return {"target": target, "passed": all(bool(c["passed"]) for c in checks), "checks": checks, "governing_hash": manifest_hash(gov), "governing_inputs": gov}


def format_preflight(report: dict) -> str:
    lines = [f"EOSE PREFLIGHT — {report['target']}", ""]
    for c in report["checks"]:
        lines.append(f"{'PASS' if c['passed'] else 'FAIL':<4}  {c['check']:<34} {c['detail']}")
    lines += ["", f"RESULT: {'PASS' if report['passed'] else 'FAIL'}"]
    return "\n".join(lines)


def next_exec_id() -> str:
    nums = []
    for row in rows():
        m = re.fullmatch(r"EXEC-(\d{4})", row.get("id", ""))
        if m:
            nums.append(int(m.group(1)))
    return f"EXEC-{max(nums, default=0) + 1:04d}"


def environment_snapshot(cwd: Path) -> dict:
    tools: dict[str, str] = {}
    candidates = [
        ("git", ["git", "--version"]), ("python3", ["python3", "--version"]),
        ("bash", ["bash", "--version"]), ("node", ["node", "--version"]),
        ("bun", ["bun", "--version"]), ("go", ["go", "version"]),
        ("rustc", ["rustc", "--version"]), ("cargo", ["cargo", "--version"]),
    ]
    for name, cmd in candidates:
        if not shutil.which(cmd[0]):
            continue
        try:
            p = run(cmd, cwd=cwd, check=False)
            line = (p.stdout or p.stderr).splitlines()[0] if (p.stdout or p.stderr).splitlines() else ""
            tools[name] = line[:500]
        except Exception:
            continue
    custom: list[dict[str, object]] = []
    config = EOS / "environment.commands"
    if config.exists():
        for raw in config.read_text(encoding="utf-8").splitlines():
            cmd = raw.strip()
            if not cmd or cmd.startswith("#"):
                continue
            # Environment capture is intentionally shell-based only for user-authored
            # local commands, never values produced by an agent/result file.
            p = subprocess.run(["bash", "-lc", cmd], cwd=cwd, text=True, capture_output=True)
            custom.append({"command": cmd, "exit_code": p.returncode, "output": (p.stdout + p.stderr)[:4000]})
    locks: list[dict[str, str]] = []
    names = {"bun.lock", "bun.lockb", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.lock", "go.sum", "uv.lock", "poetry.lock", "Pipfile.lock"}
    for p in cwd.iterdir():
        if p.is_file() and (p.name in names or p.name.startswith("requirements") and p.suffix == ".txt"):
            locks.append({"path": p.name, "sha256": sha256_file(p)})
    return {
        "captured": now_iso(), "host": socket.gethostname(), "platform": platform.platform(),
        "python": sys.version.splitlines()[0], "shell": os.environ.get("SHELL", ""),
        "branch": git_branch(cwd), "head": git_head(cwd), "tools": tools,
        "lockfiles": sorted(locks, key=lambda x: x["path"]), "custom": custom,
    }


def contract_payload(exec_id: str, target: str, branch: str, worktree: Path, baseline: str, actor: str) -> dict:
    manifest = governing_manifest(target, root=worktree)
    payload = {
        "schema_version": "2.0.0",
        "execution_id": exec_id,
        "target": target,
        "generated": now_iso(),
        "actor": actor_name(actor),
        "repository": str(ROOT),
        "branch": branch,
        "worktree": str(worktree),
        "baseline_commit": baseline,
        "governing_inputs": manifest,
        "governing_hash": manifest_hash(manifest),
        "scope": scope_directives(target),
        "system_forbidden_paths": list(execution_policy().get("system_forbidden_paths", SYSTEM_FORBIDDEN_DEFAULT)),
        "governed_paths": list(execution_policy().get("governed_paths", GOVERNED_DEFAULT)),
        "environment": environment_snapshot(worktree),
        "required_result_schema": {
            "execution_id": exec_id,
            "target": target,
            "status": "completed|blocked|failed",
            "summary": "string",
            "changed_files": ["path"],
            "validation": [{"command": "string", "exit_code": 0, "summary": "string"}],
            "acceptance_criteria": [{"criterion": "string", "status": "passed|failed|not-run", "evidence": "string"}],
            "risks": ["string"],
            "unresolved_issues": ["string"],
            "proposed_commit_message": "string"
        },
    }
    payload["contract_hash"] = sha256_bytes(canonical_bytes(payload))
    return payload


def markdown_contract(payload: dict) -> str:
    target = payload["target"]
    wp_path = ROOT / wp_row(target)["path"]
    lines = [
        f"# Codex Execution Contract v2 — {target}", "",
        f"Execution: {payload['execution_id']}", f"Generated: {payload['generated']}",
        f"Branch: `{payload['branch']}`", f"Worktree: `{payload['worktree']}`",
        f"Baseline: `{payload['baseline_commit']}`", f"Governing hash: `{payload['governing_hash']}`",
        f"Contract hash: `{payload['contract_hash']}`", "",
        "## Authority", "",
        "This contract authorizes bounded implementation only. It does not authorize changes to product/architecture/specification policy unless the work packet explicitly lists the exact governed path with `allowed-governed-path`.", "",
        "## Concurrency / Freshness", "",
        "Before finalizing work, verify this contract with `./scripts/eos contract verify " + payload['execution_id'] + "`. If governing inputs drift, stop: the execution contract is invalid.", "",
        "## Execution Scope", "",
    ]
    for p in payload["scope"]["allowed"]:
        lines.append(f"- allowed-path: `{p}`")
    for p in payload["scope"]["forbidden"]:
        lines.append(f"- forbidden-path: `{p}`")
    for p in payload["scope"]["allowed_governed"]:
        lines.append(f"- allowed-governed-path: `{p}`")
    lines += ["", "## Work Packet", "", wp_path.read_text(encoding="utf-8"), "", "## Governing Input Fingerprints", ""]
    for item in payload["governing_inputs"]:
        lines.append(f"- `{item['path']}` — `{item['sha256']}`")
    lines += [
        "", "## Required Operating Procedure", "",
        "1. Work only inside the assigned worktree and branch.",
        "2. Do not edit `.eos/` or Git internals.",
        "3. Do not expand product/architecture/specification scope to make implementation easier.",
        "4. Preserve stable IDs and traceability references.",
        "5. Run repository-prescribed validation and WP-specific validation.",
        "6. Compare actual Git changes against execution scope.",
        "7. Produce the structured JSON completion result described below.",
        "8. Stop and report BLOCKED if a governing decision must change.",
        "", "## Required Completion Result", "",
        f"Write JSON matching the contract to `.eos-result-{payload['execution_id']}.json` in the worktree, then ingest it from the main repository:", "",
        f"`./scripts/eos execution ingest {payload['execution_id']} <path-to-result.json>`", "",
        "The result is a claim. EOS independently compares it with the real Git diff and contract fingerprint.", "",
    ]
    return "\n".join(lines) + "\n"


def sync_session_json(row: dict[str, str]) -> None:
    path = ROOT / row["path"]
    existing = load_json(path, {}) if path.exists() else {}
    existing.setdefault("schema_version", "1.0.0")
    existing["registry"] = {k: row.get(k, "") for k in EXEC_FIELDS}
    tmp = path.with_suffix(".json.tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def transition_exec(exec_id: str, new_state: str, *, action: str, reason: str = "", actor: str = "") -> dict[str, str]:
    row = find_exec(exec_id)
    machine = load_json(EOS / "state-machines" / "exec.json")
    current = row["status"]
    allowed = machine.get("transitions", {}).get(current, [])
    if new_state != current and new_state not in allowed:
        raise EoseError(f"Illegal EXEC transition {exec_id}: {current} -> {new_state}; allowed: {', '.join(allowed) or '(none)'}")
    append_event("STATE_TRANSITION", target=exec_id, action=action, from_state=current, to_state=new_state, actor=actor, reason=reason, metadata={"target_wp": row.get("target", "")})
    return update_exec(exec_id, status=new_state)


def create_session(target: str, *, no_worktree: bool = False, base: str = "HEAD", actor: str = "") -> tuple[dict[str, str], dict]:
    with target_lock(target, "execute"):
        report = preflight(target, no_worktree=no_worktree, base=base)
        if not report["passed"]:
            raise EoseError("Execution preflight failed:\n" + format_preflight(report))
        wp = wp_row(target)
        if wp["status"] == "AUTHORIZED":
            p = core("start", target, check=False)
            if p.returncode != 0:
                raise EoseError((p.stderr or p.stdout).strip())
        baseline = git_head(ROOT)
        if no_worktree:
            branch, wt = git_branch(ROOT), ROOT
        else:
            branch, wt = create_worktree(target, base=base)
        exec_id = next_exec_id()
        actor_v = actor_name(actor)
        payload = contract_payload(exec_id, target, branch, wt, baseline, actor_v)
        md_path = CONTRACTS / f"{exec_id}-{target}.codex.md"
        json_path = CONTRACTS / f"{exec_id}-{target}.codex.json"
        CONTRACTS.mkdir(parents=True, exist_ok=True)
        md_path.write_text(markdown_contract(payload), encoding="utf-8")
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        session_path = EXEC_DIR / f"{exec_id}.json"
        EXEC_DIR.mkdir(parents=True, exist_ok=True)
        session = {
            "schema_version": "1.0.0", "execution_id": exec_id, "target": target,
            "contract": {"markdown": rel(md_path), "json": rel(json_path), "hash": payload["contract_hash"]},
            "governing_inputs": payload["governing_inputs"], "scope": payload["scope"],
            "environment": payload["environment"], "created": now_iso(), "result": None,
        }
        session_path.write_text(json.dumps(session, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        row = {
            "id": exec_id, "path": rel(session_path), "target": target, "status": "PREPARED",
            "branch": branch, "worktree": str(wt), "baseline_commit": baseline,
            "governing_hash": payload["governing_hash"], "contract_hash": payload["contract_hash"],
            "result_path": "", "actor": actor_v, "created": now_iso(), "updated": now_iso(),
        }
        all_rows = rows(); all_rows.append(row); write_tsv(REGISTRY, EXEC_FIELDS, all_rows)
        append_event("ENTITY_CREATED", target=exec_id, action="prepare", to_state="PREPARED", actor=actor_v, reason="execution session prepared", metadata={"row": row, "wp": target})
        row = transition_exec(exec_id, "RUNNING", action="execute-start", reason="execution session started", actor=actor_v)
        return row, payload


def contract_for_exec(exec_id: str) -> tuple[dict[str, str], dict]:
    row = find_exec(exec_id)
    session = load_json(ROOT / row["path"])
    contract_path = ROOT / session["contract"]["json"]
    return row, load_json(contract_path)


def verify_contract(exec_id: str) -> dict:
    row, contract = contract_for_exec(exec_id)
    wt = Path(row["worktree"] or ROOT)
    checks: list[dict[str, object]] = []
    original_hash = contract.get("contract_hash", "")
    copy = dict(contract); copy.pop("contract_hash", None)
    calculated = sha256_bytes(canonical_bytes(copy))
    checks.append({"check": "contract_hash", "passed": calculated == original_hash == row.get("contract_hash"), "detail": f"expected={original_hash} calculated={calculated}"})
    worktree_manifest = []
    canonical_manifest = []
    for item in contract.get("governing_inputs", []):
        wp = wt / item["path"]
        cp = ROOT / item["path"]
        worktree_manifest.append({"path": item["path"], "sha256": governing_content_hash(wp) if wp.exists() else "MISSING"})
        canonical_manifest.append({"path": item["path"], "sha256": governing_content_hash(cp) if cp.exists() else "MISSING"})
    worktree_gov = manifest_hash(worktree_manifest)
    canonical_gov = manifest_hash(canonical_manifest)
    checks.append({"check": "worktree_governing_inputs_unchanged", "passed": worktree_manifest == contract.get("governing_inputs", []), "detail": f"expected={row.get('governing_hash','')} worktree={worktree_gov}"})
    checks.append({"check": "canonical_governing_inputs_unchanged", "passed": canonical_manifest == contract.get("governing_inputs", []), "detail": f"expected={row.get('governing_hash','')} canonical={canonical_gov}"})
    head = git_head(wt)
    base = row.get("baseline_commit", "")
    ancestor = bool(base) and run(["git", "merge-base", "--is-ancestor", base, head], cwd=wt, check=False).returncode == 0
    checks.append({"check": "baseline_is_ancestor", "passed": ancestor, "detail": f"baseline={base} head={head}"})
    branch_ok = git_branch(wt) == row.get("branch", "")
    checks.append({"check": "expected_branch", "passed": branch_ok, "detail": f"expected={row.get('branch','')} actual={git_branch(wt)}"})
    result = {"execution_id": exec_id, "target": row["target"], "passed": all(bool(c["passed"]) for c in checks), "checks": checks, "worktree_governing_hash": worktree_gov, "canonical_governing_hash": canonical_gov}
    if not result["passed"] and row["status"] not in TERMINAL_EXEC_STATES and row["status"] != "INVALIDATED":
        transition_exec(exec_id, "INVALIDATED", action="contract-verify", reason="contract freshness/concurrency invariant failed")
        append_event("EXECUTION_CONTRACT_INVALIDATED", target=exec_id, action="contract-verify", reason="execution contract no longer matches governing/baseline state", metadata=result)
    return result


def changed_files(row: dict[str, str]) -> list[str]:
    wt = Path(row["worktree"] or ROOT)
    base = row["baseline_commit"]
    p = run(["git", "diff", "--name-only", base, "--"], cwd=wt, check=False)
    values = {x.strip() for x in p.stdout.splitlines() if x.strip()}
    q = run(["git", "ls-files", "--others", "--exclude-standard"], cwd=wt, check=False)
    values.update(x.strip() for x in q.stdout.splitlines() if x.strip())
    # The structured agent result is an EOSE control artifact, not product work.
    # It is intentionally ignored by scope/diff checks when placed at worktree root.
    values = {v for v in values if not re.fullmatch(r"\.eos-result-EXEC-\d{4}\.json", v)}
    return sorted(values)


def validate_result(data: dict, exec_id: str, target: str) -> list[str]:
    errors: list[str] = []
    if data.get("execution_id") != exec_id: errors.append("execution_id mismatch")
    if data.get("target") != target: errors.append("target mismatch")
    if data.get("status") not in {"completed", "blocked", "failed"}: errors.append("status must be completed, blocked, or failed")
    if not isinstance(data.get("summary", ""), str): errors.append("summary must be a string")
    for key in ("changed_files", "validation", "acceptance_criteria", "risks", "unresolved_issues"):
        if key in data and not isinstance(data[key], list): errors.append(f"{key} must be a list")
    return errors


def ingest_result(exec_id: str, result_path: Path) -> dict:
    with target_lock(exec_id, "ingest"):
        row = find_exec(exec_id)
        if row["status"] != "RUNNING":
            raise EoseError(f"{exec_id} must be RUNNING to ingest a result; current={row['status']}")
        freshness = verify_contract(exec_id)
        if not freshness["passed"]:
            raise EoseError("Execution contract is invalid; result cannot be ingested")
        data = load_json(result_path)
        errors = validate_result(data, exec_id, row["target"])
        if errors:
            raise EoseError("Invalid execution result:\n- " + "\n- ".join(errors))
        actual = changed_files(row)
        declared = sorted(set(str(x) for x in data.get("changed_files", [])))
        scope = scope_check(row["target"], actual)
        comparison = {
            "actual_changed_files": actual, "declared_changed_files": declared,
            "undeclared_actual": sorted(set(actual) - set(declared)),
            "declared_but_not_actual": sorted(set(declared) - set(actual)),
            "scope": scope,
        }
        dest = EVIDENCE / f"{exec_id}-result.json"
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps({"agent_result": data, "eos_observation": comparison, "ingested": now_iso()}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        session = load_json(ROOT / row["path"])
        session["result"] = {"path": rel(dest), "ingested": now_iso(), "agent_status": data["status"], "scope_passed": scope["passed"]}
        (ROOT / row["path"]).write_text(json.dumps(session, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        update_exec(exec_id, result_path=rel(dest))
        if data["status"] == "blocked":
            transition_exec(exec_id, "BLOCKED", action="result-ingest", reason="agent reported blocked")
        elif data["status"] == "failed":
            transition_exec(exec_id, "FAILED", action="result-ingest", reason="agent reported failed")
        else:
            transition_exec(exec_id, "RESULT_INGESTED", action="result-ingest", reason="structured agent result ingested")
        append_event("EXECUTION_RESULT_INGESTED", target=exec_id, action="ingest", reason="structured agent result stored and compared with actual diff", metadata=comparison)
        return {"execution_id": exec_id, "agent_status": data["status"], **comparison}


def check_execution(exec_id: str, *, advance: bool = True) -> dict:
    with target_lock(exec_id, "check"):
        row = find_exec(exec_id)
        freshness = verify_contract(exec_id)
        actual = changed_files(row)
        scope = scope_check(row["target"], actual)
        result_claim = load_json(ROOT / row["result_path"]) if row.get("result_path") and (ROOT / row["result_path"]).exists() else {}
        agent_result = result_claim.get("agent_result", {}) if result_claim else {}
        declared = sorted(set(str(x) for x in agent_result.get("changed_files", [])))
        diff_match = set(actual) == set(declared) if agent_result else False
        env_now = environment_snapshot(Path(row["worktree"] or ROOT))
        session = load_json(ROOT / row["path"])
        env_before = session.get("environment", {})
        environment_drift = {
            "head_changed": env_before.get("head") != env_now.get("head"),
            "tool_changes": {k: {"before": env_before.get("tools", {}).get(k), "after": env_now.get("tools", {}).get(k)} for k in sorted(set(env_before.get("tools", {})) | set(env_now.get("tools", {}))) if env_before.get("tools", {}).get(k) != env_now.get("tools", {}).get(k)},
            "lockfiles_changed": env_before.get("lockfiles", []) != env_now.get("lockfiles", []),
        }
        checks = {
            "contract_valid": freshness["passed"], "scope_passed": scope["passed"],
            "result_ingested": bool(agent_result), "declared_diff_matches_actual": diff_match,
        }
        passed = all(checks.values())
        evidence = {
            "execution_id": exec_id, "target": row["target"], "checked": now_iso(),
            "passed": passed, "checks": checks, "contract": freshness, "scope": scope,
            "actual_changed_files": actual, "declared_changed_files": declared,
            "environment_drift": environment_drift,
        }
        path = EVIDENCE / f"{exec_id}-execution-check.json"
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if passed and advance and row["status"] == "RESULT_INGESTED":
            transition_exec(exec_id, "VERIFIED", action="execution-check", reason="contract, scope, result, and diff invariants passed")
        append_event("EXECUTION_CHECKED", target=exec_id, action="check", reason="EOSE execution invariants evaluated", metadata={"passed": passed, "evidence": rel(path)})
        return evidence


def print_json_or_text(value: dict, *, as_json: bool, title: str = "") -> None:
    if as_json:
        print(json.dumps(value, indent=2, sort_keys=True))
        return
    if title: print(title); print()
    for key, val in value.items():
        if isinstance(val, (dict, list)):
            print(f"{key}: {json.dumps(val, indent=2, sort_keys=True)}")
        else:
            print(f"{key}: {val}")


def cmd_preflight(args: argparse.Namespace) -> None:
    report = preflight(args.target, no_worktree=args.no_worktree, base=args.base)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else format_preflight(report))
    if not report["passed"]:
        raise EoseError("preflight failed")


def cmd_execute(args: argparse.Namespace) -> None:
    row, payload = create_session(args.target, no_worktree=args.no_worktree, base=args.base, actor=args.actor)
    output = {"execution_id": row["id"], "target": row["target"], "status": row["status"], "branch": row["branch"], "worktree": row["worktree"], "baseline_commit": row["baseline_commit"], "governing_hash": row["governing_hash"], "contract_hash": row["contract_hash"], "contract_markdown": f".eos/contracts/{row['id']}-{row['target']}.codex.md", "contract_json": f".eos/contracts/{row['id']}-{row['target']}.codex.json"}
    print_json_or_text(output, as_json=args.json, title="EOSE EXECUTION SESSION CREATED")


def cmd_codex(args: argparse.Namespace) -> None:
    if args.force:
        raise EoseError("--force cannot bypass EOSE v2 authorization/preflight. Use the governed authorization override mechanism before execution.")
    active = active_exec_for(args.target)
    if active:
        row = active[-1]
        session = load_json(ROOT / row["path"])
        contract = ROOT / session["contract"]["markdown"]
    else:
        row, _ = create_session(args.target, no_worktree=args.no_worktree, base=args.base, actor=args.actor)
        contract = CONTRACTS / f"{row['id']}-{row['target']}.codex.md"
    if args.json:
        session = load_json(ROOT / row["path"])
        print((ROOT / session["contract"]["json"]).read_text(encoding="utf-8"), end="")
    else:
        print(contract.read_text(encoding="utf-8"), end="")
        print(f"\nContract: {rel(contract)}", file=sys.stderr)


def cmd_worktree(args: argparse.Namespace) -> None:
    if args.worktree_command == "list":
        print(json.dumps(git_worktrees(), indent=2, sort_keys=True) if args.json else "\n".join(f"{w.get('worktree','')}\t{w.get('branch','')}" for w in git_worktrees()))
        return
    if args.worktree_command == "create":
        report = preflight(args.target, no_worktree=False, base=args.base)
        if not report["passed"] and not args.force:
            raise EoseError("worktree preflight failed:\n" + format_preflight(report))
        branch, path = create_worktree(args.target, base=args.base, custom_path=args.path)
        print(f"branch: {branch}\nworktree: {path}")
        return
    if args.worktree_command == "remove":
        remove_worktree(args.target, force=args.force)
        print(f"Removed worktree for {args.target}.")
        return


def cmd_execution(args: argparse.Namespace) -> None:
    sub = args.execution_command
    if sub == "list":
        selected = [r for r in rows() if not args.target or r.get("target") == args.target]
        if args.json: print(json.dumps(selected, indent=2, sort_keys=True)); return
        for r in selected: print(f"{r['id']}\t{r['target']}\t{r['status']}\t{r['branch']}\t{r['worktree']}")
        return
    if sub == "show":
        r = find_exec(args.execution_id); session = load_json(ROOT / r["path"])
        print(json.dumps({"registry": r, "session": session}, indent=2, sort_keys=True) if args.json else json.dumps({"registry": r, "session": session}, indent=2, sort_keys=True))
        return
    if sub == "ingest":
        result = ingest_result(args.execution_id, Path(args.result).expanduser().resolve())
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"Ingested result for {args.execution_id}. scope={'PASS' if result['scope']['passed'] else 'FAIL'}")
        if result.get("agent_status") == "completed" and not result["scope"]["passed"]:
            raise EoseError("execution result ingested, but actual changes violate scope")
        return
    if sub == "check":
        result = check_execution(args.execution_id)
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"{args.execution_id}: {'PASS' if result['passed'] else 'FAIL'}\nEvidence: .eos/evidence/{args.execution_id}-execution-check.json")
        if not result["passed"]: raise EoseError("execution checks failed")
        return
    if sub == "close":
        with target_lock(args.execution_id, "close"):
            r = find_exec(args.execution_id)
            if r["status"] != "VERIFIED": raise EoseError(f"{args.execution_id} must be VERIFIED before close; current={r['status']}")
            transition_exec(args.execution_id, "CLOSED", action="close", reason=args.reason or "execution session closed", actor=args.by)
            print(f"{args.execution_id} CLOSED.")
        return
    if sub == "abort":
        with target_lock(args.execution_id, "abort"):
            r = find_exec(args.execution_id)
            if r["status"] in TERMINAL_EXEC_STATES: raise EoseError(f"{args.execution_id} is already terminal: {r['status']}")
            if not args.reason.strip(): raise EoseError("abort requires --reason")
            transition_exec(args.execution_id, "ABORTED", action="abort", reason=args.reason, actor=args.by)
            print(f"{args.execution_id} ABORTED.")
        return
    if sub == "environment":
        r = find_exec(args.execution_id)
        print(json.dumps(environment_snapshot(Path(r["worktree"] or ROOT)), indent=2, sort_keys=True))
        return


def cmd_contract(args: argparse.Namespace) -> None:
    if args.contract_command == "verify":
        result = verify_contract(args.execution_id)
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else "\n".join(f"{'PASS' if c['passed'] else 'FAIL'} {c['check']}: {c['detail']}" for c in result["checks"]))
        if not result["passed"]: raise EoseError("contract verification failed")
        return
    if args.contract_command == "show":
        r, contract = contract_for_exec(args.execution_id)
        if args.json: print(json.dumps(contract, indent=2, sort_keys=True))
        else:
            session = load_json(ROOT / r["path"])
            print((ROOT / session["contract"]["markdown"]).read_text(encoding="utf-8"), end="")
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="./scripts/eos", description="EOSE Execution v2")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("preflight", help="Check whether a WP is safe to execute")
    p.add_argument("target"); p.add_argument("--no-worktree", action="store_true"); p.add_argument("--base", default="HEAD"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_preflight)

    p = sub.add_parser("execute", help="Create isolated execution session, worktree, branch, and contracts")
    p.add_argument("target"); p.add_argument("--no-worktree", action="store_true"); p.add_argument("--base", default="HEAD"); p.add_argument("--actor", default=""); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_execute)

    p = sub.add_parser("codex", help="Create/reuse an EOSE v2 execution session and render its Codex contract")
    p.add_argument("target"); p.add_argument("--force", action="store_true", help=argparse.SUPPRESS); p.add_argument("--no-worktree", action="store_true"); p.add_argument("--base", default="HEAD"); p.add_argument("--actor", default="codex"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_codex)

    w = sub.add_parser("worktree", help="Manage governed execution worktrees"); ws = w.add_subparsers(dest="worktree_command", required=True)
    p = ws.add_parser("create"); p.add_argument("target"); p.add_argument("--base", default="HEAD"); p.add_argument("--path", default=""); p.add_argument("--force", action="store_true"); p.set_defaults(func=cmd_worktree)
    p = ws.add_parser("list"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_worktree)
    p = ws.add_parser("remove"); p.add_argument("target"); p.add_argument("--force", action="store_true"); p.set_defaults(func=cmd_worktree)

    e = sub.add_parser("execution", help="Inspect and govern EXEC-* sessions"); es = e.add_subparsers(dest="execution_command", required=True)
    p = es.add_parser("list"); p.add_argument("--target", default=""); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_execution)
    p = es.add_parser("show"); p.add_argument("execution_id"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_execution)
    p = es.add_parser("ingest"); p.add_argument("execution_id"); p.add_argument("result"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_execution)
    p = es.add_parser("check"); p.add_argument("execution_id"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_execution)
    p = es.add_parser("close"); p.add_argument("execution_id"); p.add_argument("--reason", default=""); p.add_argument("--by", default=""); p.set_defaults(func=cmd_execution)
    p = es.add_parser("abort"); p.add_argument("execution_id"); p.add_argument("--reason", required=True); p.add_argument("--by", default=""); p.set_defaults(func=cmd_execution)
    p = es.add_parser("environment"); p.add_argument("execution_id"); p.set_defaults(func=cmd_execution)

    c = sub.add_parser("contract", help="Show/verify fingerprinted execution contracts"); cs = c.add_subparsers(dest="contract_command", required=True)
    p = cs.add_parser("verify"); p.add_argument("execution_id"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_contract)
    p = cs.add_parser("show"); p.add_argument("execution_id"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_contract)
    return parser


def main() -> int:
    for d in (EXEC_DIR, CONTRACTS, EVIDENCE, LOCKS): d.mkdir(parents=True, exist_ok=True)
    parser = build_parser(); args = parser.parse_args()
    try:
        args.func(args); return 0
    except EoseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: command failed ({exc.returncode}): {' '.join(exc.cmd)}", file=sys.stderr)
        if exc.stdout: print(exc.stdout, file=sys.stderr)
        if exc.stderr: print(exc.stderr, file=sys.stderr)
        return exc.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
EOSE_PY
chmod +x tools/eos/execution_v2.py

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
  ./scripts/eos state-machine WP
  ./scripts/eos policy list
  ./scripts/eos gate explain WP_AUTHORIZE WP-0001
  ./scripts/eos planning check PI-001
  ./scripts/eos planning order PI-001
  ./scripts/eos preflight WP-0001
  ./scripts/eos execute WP-0001 --actor codex
  ./scripts/eos execution list
  ./scripts/eos contract verify EXEC-0001
  ./scripts/eos trace coverage
  ./scripts/eos stale list
  ./scripts/eos events --limit 20
  ./scripts/eos status
  ./scripts/eos next

Enable dynamic tab completion (Bash/Zsh/Fish):

  ./scripts/eos completion install

Or inspect/source repository-local completion files under `completions/`.

After EOSB-020, continue directly into the permanent lifecycle, for example:

  ./scripts/eos plan PI-002
  ./scripts/eos create-wc --pi PI-002
  ./scripts/eos create-wp --wc WC-0002 --domain CORE
  ./scripts/eos ready WP-CORE-0001
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
