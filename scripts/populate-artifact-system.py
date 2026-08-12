#!/usr/bin/env python3
"""Populate the artifact-system catalog with deterministic substantive baselines.

The catalog describes artifact *contracts*. Generated catalog documents are Draft
and do not become project authority merely by existing. Remove the generation
marker from a document before manually taking ownership of its contents.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MARKER = "<!-- artifact-catalog-baseline:v1 -->"
MIN_SUBSTANTIVE_BYTES = 800

FAMILY_FOCUS = {
    "KIR": "the Kernel Intermediate Representation: canonical semantic lowering, identity, serialization, validation, compatibility, and deterministic interchange",
    "acceptance-and-review-artifacts": "formal evidence-bearing reviews that gate readiness, acceptance, closure, release, operability, and learning",
    "ai-and-agent-architecture": "bounded AI and software-agent participation, context, identity, permissions, provenance, review, escalation, and model independence",
    "api-and-protocol-artifacts": "stable interfaces and protocols, compatibility, errors, authority, versioning, and machine-verifiable contracts",
    "architecture": "system structure, boundaries, components, quality attributes, data/control flows, deployment concerns, and architectural constraints",
    "build-and-execution": "deterministic planning and execution, build graphs, native tool coordination, sandboxes, caching, failures, and reproducibility",
    "change-requests": "controlled changes discovered outside or across planned work, including scope, authority, impact, evidence, and disposition",
    "ci-cd": "continuous validation, integration, delivery, provenance, deployment gates, rollback, and local/CI parity",
    "cli-design": "Monad command-line information architecture, commands, output contracts, diagnostics, interaction, exit behavior, and automation safety",
    "community-open-source-planning": "open-source governance, contribution pathways, maintainership, RFC participation, support, security disclosure, and community health",
    "config-workspace-model": "workspace discovery, repository identity, monad configuration, precedence, profiles, environment handling, validation, and lock/state semantics",
    "decision-management": "decision capture, authority, options, evidence, dissent, lifecycle, supersession, and discoverability",
    "dependency-management": "dependency identity, ownership, constraints, provenance, update policy, compatibility, security, and lifecycle",
    "developer-experience": "installation, onboarding, feedback, local workflows, shell/IDE integration, diagnostics, discoverability, and low-friction safe operation",
    "documentation-and-publication-architecture": "canonical documentation, generated projections, publishing, navigation, search, versioning, freshness, and source provenance",
    "domain": "Monad domain concepts, bounded contexts, entities, values, invariants, events, ownership, and lifecycle semantics",
    "ecosystem-level-planning": "multi-repository evolution, SDKs, extensions, organization controls, ownership, shared schemas, and release coordination",
    "engineering-journal": "chronological engineering reasoning, discoveries, alternatives, failures, and promotion of durable conclusions into authoritative artifacts",
    "engineering-status-and-queues": "current-state reporting, ready/active/blocked/backlog/completed queues, WIP control, and evidence-based status",
    "financial-commercial-artifacts": "commercialization, packaging, cost, sustainability, pricing, support, hosted offerings, and business viability",
    "foundational-artifacts": "Monad's constitutional identity, mission, thesis, principles, language, scope, human authority, and long-term system intent",
    "github-project-management-artifacts": "GitHub Issues, Projects, labels, milestones, fields, views, automation, and projection of canonical engineering work",
    "historical-record": "immutable historical context, superseded states, release history, migrations, and provenance without accidental current authority",
    "lang-compiler-design": "the Monad specification language and compilation pipeline, parsing, semantic analysis, lowering, diagnostics, and deterministic compiler behavior",
    "legal-compliance-artifacts-if-applicable": "licensing, legal obligations, contribution terms, privacy/compliance mappings, evidence, and activation only when applicable",
    "milestones": "major outcome and release gates that group increments and prove meaningful project-level capability",
    "observability": "logs, traces, metrics, semantic execution evidence, diagnostics, privacy boundaries, and explainable system behavior",
    "operational-documentation": "installation, operation, troubleshooting, recovery, support, upgrade, migration, runbooks, and production readiness",
    "performance-planning": "measurable latency, startup, memory, throughput, repository scale, graph scale, benchmarks, profiling, and regression budgets",
    "persistence-and-schema-artifacts": "canonical schemas, storage ownership, migrations, durability, compatibility, recovery, indexes, and data integrity",
    "plugin-ecosystem-artifacts": "extension contracts, manifests, capability boundaries, discovery, isolation, permissions, signing, compatibility, and conformance",
    "privacy-and-data-governance": "data classification, purpose, minimization, retention, access, deletion, provenance, privacy boundaries, and governance evidence",
    "product-increments": "coherent delivery horizons that advance a Product Goal through accepted capability, evidence, review, and closure",
    "product": "user problems, personas, outcomes, capabilities, requirements, product strategy, roadmap, adoption, and measurable value",
    "program-management": "roadmaps, assumptions, constraints, dependencies, risks, sequencing, critical path, registers, and delivery governance",
    "registry-artifacts": "distribution and discovery of trusted schemas, plugins, policies, templates, metadata, signing, namespaces, retention, and federation",
    "release-engineering": "versioning, release candidates, manifests, signing, SBOM/provenance, compatibility, migrations, rollback, and release readiness",
    "reliability-and-quality-architecture": "failure models, resource limits, cancellation, recovery, graceful degradation, quality budgets, and resilient correctness",
    "repo-artifact-governance": "repository authority, contribution, branching, reviews, generated artifacts, compatibility, human/agent control, and change policy",
    "requests-for-comments-proposals": "structured proposals for material change, alternatives, evidence, community/owner review, disposition, and promotion into decisions",
    "research-artifacts": "questions, experiments, trade studies, benchmarks, findings, evidence quality, uncertainty, and decision recommendations",
    "risk-management": "risk identification, scoring, ownership, treatment, acceptance, escalation, residual risk, and evidence",
    "security-planning": "threats, trust, identity, permissions, secrets, supply chain, secure execution, incidents, and release security",
    "semantic-graph-planning": "Monad Semantic Graph ontology, nodes, relationships, identity, provenance, traversal, queries, persistence, validation, and semantic diff",
    "specifications": "normative requirements, templates, lifecycle, identifiers, dependency rules, conformance, registries, and traceability",
    "testing-strategy": "unit, integration, system, conformance, regression, determinism, property, security, performance, acceptance, and test data strategy",
    "toolchain-and-ecosystem-integration": "coordination of native language/build tools, adapters, discovery, capability detection, versioning, and toolchain reproducibility",
    "traceability-artifacts": "bidirectional evidence chains among intent, requirements, decisions, specifications, work, code, tests, releases, and observed results",
    "work-cycles": "short execution and learning windows that coordinate bounded work, review outcomes, risks, and adaptation",
    "work-packets": "the smallest authorized independently reviewable engineering units, including scope, authority, acceptance, validation, evidence, and closure",
}

TYPE_RULES = [
    (("policy",), "policy", "defines mandatory rules, permitted exceptions, authority, enforcement, and review triggers"),
    (("strategy", "roadmap"), "strategy", "defines desired outcomes, sequencing, trade-offs, measures, dependencies, and adaptation triggers"),
    (("charter",), "charter", "establishes purpose, authority, scope, participants, outcomes, constraints, and completion gates"),
    (("schema",), "schema", "defines machine-verifiable fields, types, invariants, versioning, validation, and compatibility behavior"),
    (("protocol",), "protocol", "defines participant roles, messages or operations, ordering, errors, retries, compatibility, and conformance"),
    (("contract",), "contract", "defines explicit obligations and guarantees at a boundary, including failures, evidence, and compatibility"),
    (("model",), "model", "defines concepts, relationships, ownership, invariants, state, boundaries, and interpretation rules"),
    (("architecture",), "architecture", "defines structure, responsibility boundaries, flows, quality attributes, constraints, and evolution rules"),
    (("specification", "spec"), "specification", "defines normative testable behavior, inputs, outputs, invariants, failure cases, and conformance"),
    (("review",), "review", "defines evidence, reviewers, findings, decision criteria, disposition, residual risk, and closure evidence"),
    (("register", "registry", "index", "catalog"), "register", "defines a controlled inventory, identifiers, ownership, state, update rules, and integrity checks"),
    (("template",), "template", "defines required sections, metadata, authoring rules, validation, and examples for consistent instantiated artifacts"),
    (("plan", "planning"), "plan", "defines objective, scope, sequence, dependencies, resources, risks, milestones, validation, and adaptation"),
    (("lifecycle",), "lifecycle", "defines states, transitions, authorities, invariants, evidence, migration, and terminal conditions"),
    (("workflow", "process"), "process", "defines ordered activities, inputs, outputs, responsibilities, gates, exceptions, and evidence"),
    (("principle", "principles"), "principles", "defines durable decision heuristics, rationale, tensions, and tests for consistent application"),
    (("requirement", "requirements"), "requirements", "defines identified testable obligations, priority, rationale, acceptance criteria, and traceability"),
    (("checklist",), "checklist", "defines repeatable verification items, evidence expectations, exceptions, and completion ownership"),
    (("guide", "handbook", "runbook"), "guide", "defines executable guidance, prerequisites, steps, expected outcomes, failures, recovery, and escalation"),
]

OWNER_BY_FAMILY = {
    "product": "Product Owner",
    "foundational-artifacts": "Project Steward",
    "security-planning": "Security Owner",
    "privacy-and-data-governance": "Security Owner",
    "operational-documentation": "Operations Owner",
    "observability": "Operations Owner",
    "release-engineering": "Engineering Owner",
    "financial-commercial-artifacts": "Project Steward",
    "legal-compliance-artifacts-if-applicable": "Project Steward",
}


def words(value: str) -> list[str]:
    value = value.removesuffix(".md").removesuffix(".md`")
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    return [part for part in re.split(r"[-_\s]+", value) if part]


def title_for(path: Path) -> str:
    parts = words(path.name)
    if not parts:
        return "Artifact Contract"
    preserve = {"AI", "API", "CLI", "CI", "CD", "KIR", "MKE", "PI", "RFC", "SDK", "SLA", "SLO", "SBOM", "ADR", "PR"}
    rendered = []
    for part in parts:
        up = part.upper()
        rendered.append(up if up in preserve else part.capitalize())
    return " ".join(rendered)


def classify(path: Path) -> tuple[str, str]:
    slug = "-".join(part.lower() for part in words(path.name))
    for needles, kind, explanation in TYPE_RULES:
        if any(needle in slug for needle in needles):
            return kind, explanation
    return "artifact contract", "defines the purpose, required information, authority, lifecycle, relationships, validation, and safe use of this engineering artifact"


def family_for(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    return rel.parts[0] if len(rel.parts) > 1 else "artifact-system"


def intent_phrase(title: str, family: str) -> str:
    subject = title.lower()
    return (
        f"The **{title}** artifact makes {subject} explicit and reviewable within Monad. "
        f"It exists to prevent important {family.replace('-', ' ')} decisions from living only in chat, memory, implementation detail, or tool-specific state."
    )


def required_content(kind: str) -> list[str]:
    common = [
        "stable identity, status, owner, scope, and review/activation state",
        "the problem or decision pressure that caused the artifact to exist",
        "explicit in-scope and out-of-scope boundaries",
        "links to governing requirements, decisions, specifications, risks, work, and evidence",
        "assumptions and unresolved questions that could change the result",
    ]
    specific = {
        "policy": ["normative rules using testable language", "exception authority and expiry", "enforcement and audit mechanism"],
        "strategy": ["target outcomes and measurable indicators", "ordered choices and dependencies", "review triggers and adaptation criteria"],
        "charter": ["mandate and delegated authority", "participants and decision rights", "exit or completion criteria"],
        "schema": ["field/type definitions and cardinality", "validation invariants", "schema/version migration and compatibility rules"],
        "protocol": ["participants and trust assumptions", "operation/message sequencing", "timeouts, errors, retries, idempotency, and conformance"],
        "contract": ["producer/consumer obligations", "success and failure guarantees", "compatibility and evidence requirements"],
        "model": ["defined concepts and relationships", "ownership and invariants", "state/lifecycle semantics and examples"],
        "architecture": ["components/boundaries and responsibilities", "data/control flows", "quality attributes, threats, trade-offs, and evolution constraints"],
        "specification": ["normative inputs, outputs, behavior, and invariants", "negative/boundary/failure behavior", "conformance examples and verification mapping"],
        "review": ["review scope and evidence set", "findings by severity", "decision/disposition, conditions, residual risks, and follow-ups"],
        "register": ["entry schema and stable identifiers", "state/ownership fields", "ordering, archival, integrity, and reconciliation rules"],
        "template": ["required and optional sections", "authoring guidance and anti-patterns", "validation rules and a representative example"],
        "plan": ["objective and measurable outcome", "sequence, dependencies, capacity and critical path", "risks, checkpoints, evidence and replanning triggers"],
        "lifecycle": ["states and transition table", "transition authority and required evidence", "invalid transitions, migration, retention, and terminal behavior"],
        "process": ["entry criteria and inputs", "ordered responsibilities and gates", "exception, escalation, outputs, evidence, and improvement loop"],
        "principles": ["principle statements and rationale", "trade-offs and counterexamples", "decision tests demonstrating correct application"],
        "requirements": ["stable requirement IDs and priority", "rationale and measurable acceptance", "dependencies, constraints, risks, and verification"],
        "checklist": ["ordered or grouped checks", "evidence or command for each check", "exception handling, owner, and completion result"],
        "guide": ["audience, prerequisites, and safety assumptions", "executable steps with expected results", "failure diagnosis, rollback/recovery, and escalation"],
        "artifact contract": ["required anatomy and semantics", "creation/update responsibilities", "verification and retirement rules"],
    }
    return common + specific.get(kind, specific["artifact contract"])


def render(path: Path, root: Path) -> str:
    family = family_for(path, root)
    focus = FAMILY_FOCUS.get(family, family.replace("-", " "))
    title = title_for(path)
    kind, kind_explanation = classify(path)
    owner = OWNER_BY_FAMILY.get(family, "Engineering Owner")
    rel = path.relative_to(root.parent).as_posix().removesuffix("`")
    reqs = required_content(kind)
    req_lines = "\n".join(f"- {item}." for item in reqs)

    return f"""{MARKER}
# {title}

**Catalog path:** `{rel}`  
**Status:** Draft  
**Artifact class:** {kind}  
**Owner:** {owner}  
**Authority:** Describes an artifact contract; it is not automatically an instantiated or accepted project record.

## Purpose

{intent_phrase(title, family)}

Within the artifact catalog this document {kind_explanation}. Its family focuses on {focus}. The contract is deliberately independent of a particular implementation tool so humans, ChatGPT, Codex, CI, and future Monad automation can reason about the same engineering intent.

## Activation

Create or promote an instantiated {title} when an accepted decision, approved specification, active Work Packet, release gate, recurring operational need, or material risk requires a durable representation. Do not activate the artifact merely because the catalog contains this contract.

Before activation, identify the accountable owner, canonical repository location, stable identifier scheme, required reviewers, update triggers, and the validation that proves the artifact is current. If a simpler existing artifact can carry the same meaning without ambiguity, prefer reuse over duplication.

## Scope

This contract governs the structure, semantics, authority, lifecycle, traceability, and verification of {title} records used by Monad. It does not grant decision authority, approve an implementation, or supersede higher-order governance. Tool-specific UI fields are projections unless explicitly designated canonical.

Out of scope are informal brainstorming, transient chat, generated summaries without canonical provenance, and implementation details that do not affect the contract represented by this artifact.

## Required content

An instantiated artifact MUST make the following reviewable:

{req_lines}

Unknown information MUST be labeled as unknown, assumption, proposal, or deferred work rather than fabricated to make the record appear complete.

## Normative rules

1. The canonical artifact MUST identify its status and owner when reliance on it affects engineering action.
2. Meaning-changing edits MUST preserve history through version control and, for Approved material, follow the applicable change-control or supersession process.
3. The artifact MUST NOT silently contradict a higher-authority accepted decision, approved specification, or legal/security obligation.
4. Claims used to authorize consequential work MUST link to evidence or clearly state the evidence gap.
5. Stable identifiers MUST NOT be reused for a different meaning after publication.
6. Machine-generated projections MUST retain canonical source identity and MUST NOT become a competing editable source of truth.
7. Automation MAY validate, index, summarize, or project the artifact, but approval remains with the accountable human authority unless governance explicitly delegates a bounded mechanical decision.

## Relationships and traceability

At minimum, record upstream authority and downstream consumers that materially depend on this artifact. Prefer typed relationships such as `governed-by`, `implements`, `specified-by`, `depends-on`, `verifies`, `blocks`, `supersedes`, `generated-from`, or `evidenced-by` rather than untyped prose references.

When the Monad semantic graph supports this artifact class, its stable identity and relationships SHOULD be machine-queryable. A reviewer should be able to move from product intent to this artifact and from this artifact to authorized work, implementation evidence, and release disposition without reconstructing history from conversation.

## Lifecycle

The default lifecycle is **Draft -> Review -> Approved -> Implemented**, followed when necessary by **Deprecated**, **Superseded**, or **Retired**. Not every artifact needs every state; the instantiated contract must state deviations.

Drafts may change freely within branch review. Approval records who accepted the artifact and its effective scope. Implemented means required behavior or controls are demonstrably present, not merely that a document was merged. Superseded and retired records remain discoverable for historical provenance.

## Security, privacy, and agent use

Store no secret, credential, private key, unnecessary personal data, or restricted operational payload merely to make the artifact self-contained. Reference controlled evidence when detail belongs elsewhere. Security-sensitive exceptions and authority changes require explicit review.

AI agents may use this artifact for context only when they can identify the canonical source and status. An agent MUST distinguish Draft guidance from Approved authority, MUST surface contradictions instead of choosing silently, and MUST keep generated recommendations separate from human approval.

## Verification

Verification for an instantiated {title} includes:

- structural validation of required metadata and sections;
- link/identifier integrity and relationship resolution;
- consistency with governing decisions and specifications;
- evidence that required reviewers and approvals are present;
- checks that generated machine companions match canonical source; and
- domain-specific conformance tests where the artifact defines executable behavior.

A review passes only when omissions are either resolved or explicitly accepted by an authority permitted to accept the residual risk.

## MVP relevance

For MVP Release 1, activate this artifact only if it directly supports the core loop `canonical engineering knowledge -> semantic compilation -> graph/query/explain -> bounded agent context -> deterministic validation`, or if it retires a release-blocking correctness, security, operability, compatibility, or governance risk. Otherwise this Draft contract remains part of the long-term catalog.

## Evolution

Refine this baseline with evidence from actual use. Once manually specialized and reviewed, remove `{MARKER}` so the catalog population tool no longer owns the file. Major semantic changes to an Approved contract require impact analysis across its instantiated artifacts and machine schema/projection behavior.
"""


def candidate_paths(root: Path) -> list[Path]:
    artifact_root = root / "artifact-system"
    bad_support = artifact_root / "repo-artifact-governance" / "SUPPORT.md`"
    good_support = artifact_root / "repo-artifact-governance" / "SUPPORT.md"
    if bad_support.exists() and not good_support.exists():
        bad_support.rename(good_support)
    paths = [
        path
        for path in artifact_root.rglob("*.md")
        if path.is_file() and path != artifact_root / "README.md"
    ]
    return sorted(paths)


def expected_for(path: Path, root: Path) -> str | None:
    current = path.read_text(encoding="utf-8")
    if MARKER in current or len(current.strip().encode("utf-8")) < MIN_SUBSTANTIVE_BYTES:
        return render(path, root / "artifact-system")
    return None


def run(root: Path, write: bool) -> int:
    paths = candidate_paths(root)
    if not paths:
        print("error: no artifact-system Markdown files found", file=sys.stderr)
        return 2

    changed: list[str] = []
    underspecified: list[str] = []
    for path in paths:
        expected = expected_for(path, root)
        if expected is not None:
            current = path.read_text(encoding="utf-8")
            if current != expected:
                if write:
                    path.write_text(expected, encoding="utf-8")
                    changed.append(path.relative_to(root).as_posix())
                else:
                    underspecified.append(path.relative_to(root).as_posix())
        elif len(path.read_text(encoding="utf-8").strip().encode("utf-8")) < MIN_SUBSTANTIVE_BYTES:
            underspecified.append(path.relative_to(root).as_posix())

    if write:
        print(f"Artifact catalog populated: {len(paths)} Markdown files inspected, {len(changed)} changed.")
        return 0
    if underspecified:
        print("artifact catalog requires regeneration:", file=sys.stderr)
        for item in underspecified[:50]:
            print(f"  {item}", file=sys.stderr)
        if len(underspecified) > 50:
            print(f"  ... and {len(underspecified) - 50} more", file=sys.stderr)
        return 1
    print(f"Artifact catalog verified: {len(paths)} Markdown files are substantive/current.")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Populate generated Draft baselines.")
    mode.add_argument("--check", action="store_true", help="Fail when generated/tiny catalog files need population.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = args.root.resolve()
    return run(root, write=args.write or not args.check)


if __name__ == "__main__":
    raise SystemExit(main())
