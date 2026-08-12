#!/usr/bin/env python3
"""Populate empty artifact-system Markdown files with substantive Draft baselines.

This tool is intentionally deterministic and standard-library only. It never
overwrites non-empty artifact documents unless --force is supplied.

Generated documents are substantive starting points, not approved authority.
They remain Draft until reviewed under governance/document-lifecycle.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path

TOOL_VERSION = "1.0.0"

CATEGORY_CONTEXT = {
    "KIR": (
        "Kernel Intermediate Representation",
        "the canonical, deterministic intermediate representation that bridges semantic engineering knowledge and downstream execution, publication, analysis, and interoperability",
        ["canonical semantics", "stable identity", "deterministic serialization", "compatibility", "validation"],
    ),
    "acceptance-and-review-artifacts": (
        "Acceptance and Review",
        "formal evidence used to decide readiness, acceptance, closure, operability, security, and learning outcomes",
        ["explicit criteria", "review authority", "evidence links", "dissent", "follow-up actions"],
    ),
    "ai-and-agent-architecture": (
        "AI and Agent Architecture",
        "bounded use of AI systems and software agents inside Monad while preserving human authority, provenance, least privilege, reproducibility, and inspectability",
        ["capabilities", "permissions", "context", "provenance", "human approval"],
    ),
    "api-and-protocol-artifacts": (
        "API and Protocol",
        "versioned contracts through which Monad components, tools, agents, plugins, services, and external systems exchange commands, events, state, and evidence",
        ["contract stability", "errors", "compatibility", "authentication", "observability"],
    ),
    "architecture": (
        "Architecture",
        "the structural model of Monad: its boundaries, components, planes, data flows, responsibilities, deployment shapes, and cross-cutting quality constraints",
        ["boundaries", "responsibility", "quality attributes", "trade-offs", "evolution"],
    ),
    "build-and-execution": (
        "Build and Execution",
        "deterministic planning and execution of native toolchain work, including tasks, dependencies, inputs, outputs, caching, isolation, retries, and explainability",
        ["execution plans", "fingerprints", "native tools", "isolation", "reproducibility"],
    ),
    "change-requests": (
        "Change Request",
        "controlled introduction of changes that arise outside an already-authorized work packet or that materially alter accepted scope, authority, risk, or compatibility",
        ["origin", "impact", "disposition", "authorization", "verification"],
    ),
    "ci-cd": (
        "CI/CD",
        "repeatable automated validation, integration, packaging, release, provenance, and deployment gates that reproduce local engineering evidence in controlled environments",
        ["local parity", "quality gates", "provenance", "least privilege", "release safety"],
    ),
    "cli-design": (
        "CLI Design",
        "the command-line interaction model through which users inspect, explain, validate, plan, execute, query, and operate Monad",
        ["command taxonomy", "stable output", "diagnostics", "configuration", "accessibility"],
    ),
    "community-open-source-planning": (
        "Community and Open Source",
        "the participation, contribution, maintenance, governance, release, support, and ecosystem practices required for a sustainable open-source project",
        ["maintainership", "contribution", "transparency", "security reporting", "sustainability"],
    ),
    "config-workspace-model": (
        "Configuration and Workspace",
        "the canonical model for discovering repositories, resolving workspace state, configuration precedence, profiles, lock state, environment boundaries, and local generated state",
        ["discovery", "precedence", "validation", "determinism", "migration"],
    ),
    "decision-management": (
        "Decision Management",
        "the lifecycle and traceability of material project and engineering decisions from question and evidence through approval, supersession, and review",
        ["decision rights", "evidence", "alternatives", "consequences", "supersession"],
    ),
    "dependency-management": (
        "Dependency Management",
        "inventory, ownership, selection, update, compatibility, licensing, security, and lifecycle controls for external and internal dependencies",
        ["ownership", "versioning", "supply chain", "compatibility", "exit strategy"],
    ),
    "developer-experience": (
        "Developer Experience",
        "the end-to-end experience of installing, learning, configuring, using, debugging, upgrading, and contributing to Monad",
        ["onboarding", "feedback", "errors", "discoverability", "migration"],
    ),
    "documentation-and-publication-architecture": (
        "Documentation and Publication",
        "the architecture that turns canonical engineering knowledge into trustworthy human-facing documentation, references, generated views, indexes, and searchable publications",
        ["source of truth", "projection", "versioning", "cross-reference", "quality"],
    ),
    "domain": (
        "Domain Model",
        "the ubiquitous language, bounded contexts, entities, value objects, aggregates, invariants, events, ownership, and lifecycle rules that define Monad's problem domain",
        ["language", "identity", "ownership", "invariants", "events"],
    ),
    "ecosystem-level": (
        "Ecosystem",
        "the repository, package, SDK, plugin, schema, release, and organizational relationships that allow Monad to evolve beyond a single repository without losing coherence",
        ["repository boundaries", "shared contracts", "release coordination", "ownership", "compatibility"],
    ),
    "financial-commercial": (
        "Financial and Commercial",
        "economic, packaging, support, licensing, hosted-service, and sustainability decisions that may accompany an open-source Monad ecosystem",
        ["sustainability", "cost", "packaging", "licensing", "service obligations"],
    ),
    "historical": (
        "Historical Record",
        "durable records that explain how Monad evolved, including superseded designs, releases, migrations, incidents, retrospectives, and rejected proposals",
        ["chronology", "provenance", "supersession", "lessons", "preservation"],
    ),
    "knowledge-engine": (
        "Knowledge Engine",
        "storage, indexing, querying, traversal, validation, provenance, and reasoning operations over Monad's canonical engineering knowledge",
        ["semantic identity", "query", "provenance", "indexing", "determinism"],
    ),
    "language-and-compiler": (
        "Language and Compiler",
        "the authoring, parsing, semantic analysis, normalization, resolution, lowering, diagnostics, and compatibility model for Monad's specification and knowledge compilation pipeline",
        ["syntax", "semantics", "resolution", "diagnostics", "lowering"],
    ),
    "legal-and-compliance": (
        "Legal and Compliance",
        "legal, licensing, privacy, trademark, contribution, export, and compliance obligations that constrain distribution and operation",
        ["obligations", "evidence", "ownership", "licensing", "review"],
    ),
    "observability": (
        "Observability",
        "structured logs, metrics, traces, diagnostics, execution records, and explainability evidence needed to understand Monad's behavior and failures",
        ["correlation", "structured signals", "privacy", "debugging", "retention"],
    ),
    "operations": (
        "Operations",
        "installation, deployment, maintenance, support, incident response, recovery, migration, troubleshooting, and service-operability practices",
        ["readiness", "recovery", "runbooks", "service objectives", "support"],
    ),
    "performance": (
        "Performance",
        "latency, throughput, memory, startup, graph scale, workspace scale, profiling, benchmarking, and performance-regression governance",
        ["budgets", "benchmarks", "representative load", "regression", "capacity"],
    ),
    "plugin-ecosystem": (
        "Plugin Ecosystem",
        "extension contracts, discovery, capabilities, permissions, sandboxing, compatibility, signing, publication, and certification for third-party integrations",
        ["manifest", "permissions", "isolation", "compatibility", "trust"],
    ),
    "product-strategy": (
        "Product Strategy",
        "the product thesis, users, jobs, positioning, capabilities, boundaries, roadmap, adoption, ecosystem, and success measures for Monad",
        ["user outcomes", "differentiation", "scope", "roadmap", "evidence"],
    ),
    "program-management": (
        "Program Management",
        "the hierarchy and controls used to translate product and architecture intent into milestones, increments, sprints or work cycles, work packets, risks, dependencies, and status",
        ["outcomes", "sequencing", "dependencies", "risk", "evidence"],
    ),
    "quality-and-reliability": (
        "Quality and Reliability",
        "correctness, determinism, reproducibility, resilience, degradation, recovery, concurrency, resource, and failure-model expectations",
        ["correctness", "determinism", "failure handling", "recovery", "evidence"],
    ),
    "registry": (
        "Registry",
        "discovery, metadata, trust, publication, mirroring, federation, compatibility, retention, and governance for distributed Monad ecosystem artifacts",
        ["namespace", "metadata", "trust", "discovery", "compatibility"],
    ),
    "release-engineering": (
        "Release Engineering",
        "versioning, release readiness, packaging, signing, SBOMs, attestations, notes, compatibility, migrations, rollback, and artifact publication",
        ["versioning", "provenance", "signing", "compatibility", "rollback"],
    ),
    "repository-and-artifact-governance": (
        "Repository and Artifact Governance",
        "repository structure, artifact authority, naming, versioning, branching, generated-content, contribution, and change-control conventions",
        ["authority", "naming", "lifecycle", "traceability", "review"],
    ),
    "research": (
        "Research",
        "questions, experiments, evaluations, benchmarks, trade studies, findings, and the controlled promotion of evidence into decisions and specifications",
        ["question", "method", "evidence", "limitations", "decision linkage"],
    ),
    "risk-management": (
        "Risk Management",
        "identification, analysis, ownership, treatment, triggers, contingencies, escalation, and closure of uncertainty that may affect Monad objectives",
        ["cause", "event", "consequence", "treatment", "trigger"],
    ),
    "security": (
        "Security",
        "threats, trust boundaries, identities, permissions, secrets, supply-chain controls, vulnerability management, sandboxing, and security evidence",
        ["least privilege", "trust", "secrets", "supply chain", "incident response"],
    ),
    "semantic-graph": (
        "Semantic Graph",
        "the graph representation of engineering entities and relationships that allows Monad to answer why, impact, ownership, provenance, dependency, and coverage questions",
        ["ontology", "identity", "edges", "invariants", "query"],
    ),
    "specification-system": (
        "Specification System",
        "authoring, lifecycle, normative terminology, dependencies, traceability, conformance, schemas, examples, compatibility, and publication of specifications",
        ["normative language", "lifecycle", "traceability", "conformance", "compatibility"],
    ),
    "testing": (
        "Testing",
        "unit, integration, system, acceptance, contract, conformance, property, fuzz, performance, security, compatibility, migration, and determinism verification",
        ["risk-based coverage", "repeatability", "fixtures", "evidence", "failure paths"],
    ),
    "traceability": (
        "Traceability",
        "end-to-end relationships from intent and requirements through decisions, specifications, work, implementation, tests, releases, diagnostics, and observed evidence",
        ["stable identifiers", "bidirectional links", "coverage", "provenance", "impact"],
    ),
}

KEYWORD_PURPOSE = {
    "charter": "defines mandate, boundaries, stakeholders, decision rights, and success conditions",
    "principle": "states durable rules used to evaluate choices and resolve ambiguity",
    "model": "defines entities, relationships, states, invariants, ownership, and allowed transitions",
    "schema": "defines machine-verifiable structure, required fields, constraints, and extensibility rules",
    "protocol": "defines ordered interactions, messages, state transitions, errors, retries, and compatibility",
    "policy": "defines mandatory or conditionally mandatory rules, enforcement points, exceptions, and evidence",
    "strategy": "defines objectives, sequencing, trade-offs, constraints, and measures used to guide execution",
    "architecture": "defines structural responsibilities, boundaries, flows, interfaces, deployment concerns, and trade-offs",
    "plan": "defines a sequenced, owned path from current state to an explicit outcome and decision gate",
    "roadmap": "orders outcomes over horizons while preserving uncertainty and dependency constraints",
    "lifecycle": "defines states, transition authority, review triggers, retention, deprecation, and retirement",
    "version": "defines version identifiers, compatibility meaning, change classification, and consumer obligations",
    "compatib": "defines which producers and consumers may interoperate and how incompatible change is detected and migrated",
    "migration": "defines safe transition from one supported representation or behavior to another with verification and rollback",
    "validation": "defines checks, failure classes, diagnostics, evidence, and the boundary between invalid and accepted state",
    "canonical": "defines canonical form so equivalent inputs converge on one deterministic representation",
    "hash": "defines stable fingerprint inputs, normalization, algorithm agility, collision handling, and provenance",
    "identity": "defines stable identity, scope, uniqueness, persistence, aliases, and change semantics",
    "serializ": "defines deterministic external encoding, ordering, normalization, round-trip, and compatibility behavior",
    "relationship": "defines allowed relationship types, direction, cardinality, invariants, and provenance",
    "entity": "defines entity classes, identity, ownership, lifecycle, attributes, and invariants",
    "permission": "defines capabilities, subjects, resources, scopes, delegation, denial semantics, and audit evidence",
    "capability": "defines an independently understandable ability, its boundaries, dependencies, inputs, outputs, and maturity",
    "provenance": "defines origin, transformation history, evidence linkage, integrity, and reconstruction requirements",
    "audit": "defines accountable event capture, integrity, access, retention, reconstruction, and privacy boundaries",
    "context": "defines how task-relevant knowledge is selected, minimized, ordered, bounded, and proven current",
    "review": "defines entry criteria, reviewers, evidence, findings, disposition, decision authority, and closure conditions",
    "acceptance": "defines observable conditions and evidence required before a result may be accepted",
    "readiness": "defines evidence and conditions required before a transition, implementation, release, or operation is authorized",
    "checklist": "defines a repeatable verification sequence whose completion produces auditable readiness evidence",
    "template": "defines a required document or record structure that preserves comparable evidence without implying completed content",
    "guide": "defines repeatable operating guidance, decision points, examples, cautions, and escalation paths",
    "catalog": "defines a discoverable inventory, stable identifiers, ownership, lifecycle, and metadata expectations",
    "registry": "defines authoritative registration, naming, discovery, metadata, trust, and lifecycle behavior",
    "index": "defines the authoritative navigation surface for a class of records and the rules for keeping it current",
    "matrix": "defines a cross-reference used to evaluate coverage, compatibility, ownership, or decision responsibility",
    "taxonomy": "defines controlled categories, classification rules, overlap handling, and extension governance",
    "register": "defines a controlled living record with stable IDs, ownership, state, review triggers, and closure criteria",
    "diagnostic": "defines structured failure or warning information, severity, provenance, remediation, and machine representation",
    "error": "defines error classes, stable codes, safe disclosure, retry semantics, and remediation",
    "query": "defines supported question shapes, semantics, result determinism, limits, and explainability",
    "cache": "defines cache identity, validity, invalidation, integrity, eviction, observability, and failure safety",
    "increment": "defines minimal recomputation from observed change while preserving correctness and explainability",
    "determin": "defines the invariants required for equivalent inputs and environment declarations to produce equivalent results",
    "reproduc": "defines the evidence and environment capture required to independently reproduce a result",
    "release": "defines the evidence, artifacts, compatibility, provenance, approval, publication, and rollback needed for release",
    "branch": "defines branch purpose, naming, lifetime, protection, synchronization, and merge expectations",
    "commit": "defines commit scope, message semantics, provenance, signing expectations, and review relationship",
    "pull-request": "defines the change-review contract, evidence, risk disclosure, acceptance, and merge conditions",
    "dependency": "defines inventory, ownership, version, risk, update, compatibility, and exit requirements",
    "api": "defines callable boundaries, requests, responses, errors, versioning, authentication, and observability",
    "event": "defines event identity, schema, ordering, delivery, compatibility, privacy, and consumer obligations",
    "data": "defines ownership, classification, lifecycle, quality, lineage, retention, access, and migration expectations",
    "storage": "defines persistence responsibilities, consistency, durability, backup, corruption handling, and migration",
    "plugin": "defines extension discovery, manifest, capability, permissions, lifecycle, compatibility, isolation, and trust",
    "agent": "defines bounded machine actor identity, authority, task scope, context, provenance, escalation, and review",
    "ai": "defines model-agnostic AI integration boundaries, safety, data handling, provenance, evaluation, cost, and human authority",
    "cli": "defines command-line information architecture, commands, flags, output, errors, compatibility, and automation use",
    "configuration": "defines configuration sources, precedence, validation, secrets boundaries, profiles, migration, and observability",
    "workspace": "defines repository discovery, ownership, package/component boundaries, identity, configuration, and local state",
    "observability": "defines logs, metrics, traces, correlation, privacy, retention, and operator workflows",
    "performance": "defines representative workloads, budgets, measurement, baselines, regression rules, and capacity evidence",
    "security": "defines threats, controls, ownership, verification, exceptions, and incident linkage",
    "threat": "defines assets, adversaries, attack paths, trust boundaries, controls, residual risk, and review triggers",
    "incident": "defines detection, command, containment, communication, recovery, evidence preservation, and learning",
    "risk": "defines cause-event-consequence, likelihood, impact, owner, treatment, trigger, contingency, and closure",
}

CATEGORY_EXTRA = {
    "ai-and-agent-architecture": [
        "Human authority is never inferred from model confidence. Agents act only within explicit capabilities and task scope.",
        "Context packages must be minimal, attributable, current, and reproducible enough for later review.",
        "AI-produced changes carry provenance and are reviewed under the same acceptance rules as human-produced changes.",
    ],
    "security": [
        "Controls follow least privilege and explicit trust boundaries; absence of a known exploit is not evidence of safety.",
        "Secrets and sensitive payloads must not be copied into diagnostics, generated documentation, or AI context without explicit authorization.",
        "Exceptions are time-bounded, owned, risk-assessed, and reviewed.",
    ],
    "build-and-execution": [
        "Execution delegates language-specific mechanics to native tools while Monad owns dependency reasoning, ordering, evidence, and explanation.",
        "Plans and fingerprints are serializable and explainable; hidden environment inputs are treated as correctness defects.",
        "Unknown commit or output state enters reconciliation rather than being represented as clean failure.",
    ],
    "semantic-graph": [
        "Graph identity must remain stable across traversal order and serialization order.",
        "Every derived edge retains provenance sufficient to explain why the relationship exists.",
        "Graph queries must distinguish absence of evidence from evidence of absence.",
    ],
    "KIR": [
        "KIR is machine-oriented but semantically reviewable; it is not an opaque cache format.",
        "Equivalent semantic input must canonicalize to equivalent KIR under the same declared schema version.",
        "Extensions cannot silently weaken core invariants or redefine existing field meaning.",
    ],
    "repository-and-artifact-governance": [
        "Canonical human-readable source remains the authority unless an approved artifact explicitly states otherwise.",
        "Generated derivatives are reproducible projections and must never become an independent editable source of truth.",
        "Authority changes are explicit and reviewable; history is superseded rather than silently rewritten.",
    ],
}


def slug_to_title(stem: str) -> str:
    raw = stem.replace("_", " ").replace("-", " ")
    words = []
    for token in raw.split():
        if token.upper() in {"AI", "API", "CLI", "CI", "CD", "KIR", "MKE", "MSL", "MSC", "SDK", "SBOM", "PI", "PR", "RFC"}:
            words.append(token.upper())
        elif token.lower() == "github":
            words.append("GitHub")
        elif token.lower() == "codex":
            words.append("Codex")
        elif token.lower() == "chatgpt":
            words.append("ChatGPT")
        else:
            words.append(token.capitalize())
    return " ".join(words) or stem


def normalize_category(category: str) -> str:
    if category in CATEGORY_CONTEXT:
        return category
    low = category.lower()
    aliases = [
        ("financial", "financial-commercial"),
        ("commercial", "financial-commercial"),
        ("histor", "historical"),
        ("knowledge", "knowledge-engine"),
        ("compiler", "language-and-compiler"),
        ("language", "language-and-compiler"),
        ("legal", "legal-and-compliance"),
        ("compliance", "legal-and-compliance"),
        ("observ", "observability"),
        ("operation", "operations"),
        ("perform", "performance"),
        ("plugin", "plugin-ecosystem"),
        ("product", "product-strategy"),
        ("program", "program-management"),
        ("reliab", "quality-and-reliability"),
        ("quality", "quality-and-reliability"),
        ("release", "release-engineering"),
        ("repository", "repository-and-artifact-governance"),
        ("govern", "repository-and-artifact-governance"),
        ("research", "research"),
        ("risk", "risk-management"),
        ("secur", "security"),
        ("graph", "semantic-graph"),
        ("spec", "specification-system"),
        ("test", "testing"),
        ("trace", "traceability"),
        ("registr", "registry"),
        ("ecosystem", "ecosystem-level"),
    ]
    for needle, replacement in aliases:
        if needle in low:
            return replacement
    return category


def category_context(category: str) -> tuple[str, str, list[str]]:
    normalized = normalize_category(category)
    if normalized in CATEGORY_CONTEXT:
        return CATEGORY_CONTEXT[normalized]
    title = slug_to_title(category)
    return (
        title,
        f"the {title.lower()} concern within Monad's engineering knowledge compilation and operating model",
        ["explicit scope", "stable identity", "traceability", "review", "verification"],
    )


def subject_purpose(stem: str) -> str:
    low = stem.lower()
    purposes = [value for key, value in KEYWORD_PURPOSE.items() if key in low]
    if not purposes:
        return "defines the stable responsibilities, rules, evidence, and change boundaries for this artifact"
    unique = []
    for item in purposes:
        if item not in unique:
            unique.append(item)
    if len(unique) == 1:
        return unique[0]
    return "; it also " + "; and ".join(unique[:3])


def artifact_kind(stem: str) -> str:
    low = stem.lower()
    ordered = [
        ("template", "Template"),
        ("checklist", "Checklist"),
        ("review", "Review Contract"),
        ("register", "Register"),
        ("registry", "Registry"),
        ("schema", "Schema Contract"),
        ("protocol", "Protocol"),
        ("policy", "Policy"),
        ("strategy", "Strategy"),
        ("roadmap", "Roadmap"),
        ("plan", "Plan"),
        ("architecture", "Architecture"),
        ("model", "Model"),
        ("lifecycle", "Lifecycle"),
        ("guide", "Guide"),
        ("charter", "Charter"),
        ("principle", "Principles"),
        ("rules", "Rules"),
        ("specification", "Specification"),
        ("matrix", "Matrix"),
        ("taxonomy", "Taxonomy"),
        ("catalog", "Catalog"),
        ("index", "Index"),
    ]
    for needle, label in ordered:
        if needle in low:
            return label
    return "Engineering Artifact"


def owner_for(category: str) -> str:
    low = category.lower()
    if "product" in low or "commercial" in low or "community" in low:
        return "Product Owner"
    if "security" in low or "risk" in low or "legal" in low:
        return "Security Owner"
    if "operation" in low or "observ" in low or "release" in low or "ci-cd" in low:
        return "Operations Owner"
    if "architecture" in low or "domain" in low or "kir" in low or "graph" in low or "knowledge" in low or "language" in low:
        return "Architecture Owner"
    return "Engineering Owner"


def review_roles(category: str) -> str:
    low = category.lower()
    roles = ["Engineering Owner"]
    if any(x in low for x in ["architecture", "domain", "kir", "graph", "language", "knowledge", "api", "plugin"]):
        roles.append("Architecture Owner")
    if any(x in low for x in ["security", "risk", "ai", "agent", "dependency", "supply", "legal"]):
        roles.append("Security Owner")
    if any(x in low for x in ["operation", "release", "ci-cd", "observ", "performance"]):
        roles.append("Operations Owner")
    if any(x in low for x in ["product", "community", "commercial", "developer-experience"]):
        roles.append("Product Owner")
    out = []
    for role in roles:
        if role not in out:
            out.append(role)
    return ", ".join(out)


def subject_rules(stem: str, category: str, subject: str) -> list[str]:
    low = stem.lower()
    rules = [
        f"{subject} has an explicit scope and must not silently absorb neighboring responsibilities.",
        "Every normative claim must be testable, reviewable, or linked to evidence that can be independently inspected.",
        "Stable identifiers are never reused for semantically different concepts or records.",
        "Changes that alter public behavior, compatibility, authority, security posture, or accepted risk require impact analysis before approval.",
        "Generated projections may summarize or index this artifact but may not silently redefine its meaning.",
    ]
    if "identity" in low:
        rules += [
            "Identity is stable within its declared namespace and lifetime.",
            "Renames and aliases preserve lineage; deletion does not authorize identifier reuse.",
        ]
    if "hash" in low:
        rules += [
            "The fingerprint input set and canonicalization procedure are part of the contract.",
            "Hash algorithm changes are versioned and preserve provenance across migrations.",
        ]
    if "serializ" in low or "canonical" in low:
        rules += [
            "Serialization order and irrelevant presentation differences cannot change canonical semantic meaning.",
            "Round-trip behavior is tested for supported representations and schema versions.",
        ]
    if "compatib" in low or "version" in low or "migration" in low:
        rules += [
            "Compatibility is declared, never assumed from matching version strings.",
            "Breaking transitions include migration guidance, detection, rollback or recovery behavior, and affected-consumer evidence.",
        ]
    if "permission" in low or "security" in low:
        rules += [
            "Default authorization is deny unless an approved capability grants the requested action.",
            "Privileges are scoped to subject, resource, action, environment, and duration where those dimensions apply.",
        ]
    if "agent" in low or "ai" in low:
        rules += [
            "Agents cannot expand their own authority, approve their own high-consequence work, or treat model confidence as authorization.",
            "Task context and produced changes retain enough provenance to reconstruct the instructions, governing artifacts, and validation used.",
        ]
    if "cache" in low:
        rules += [
            "A cache hit is valid only when every declared semantic input to the result matches the fingerprint contract.",
            "Corruption or uncertainty degrades to recomputation or explicit failure rather than serving unverified output.",
        ]
    if "query" in low:
        rules += [
            "Query semantics distinguish unknown, absent, filtered, unauthorized, and empty results where those states differ.",
            "Results that drive consequential decisions expose provenance and freshness sufficient for review.",
        ]
    if "review" in low or "acceptance" in low or "readiness" in low:
        rules += [
            "A review records the evidence considered, findings, dissent, conditions, decision authority, and unresolved follow-up.",
            "Silence, mergeability, or file existence is never equivalent to formal acceptance.",
        ]
    return rules


def specific_sections(stem: str, category: str, subject: str) -> list[tuple[str, list[str]]]:
    low = stem.lower()
    sections: list[tuple[str, list[str]]] = []
    if any(k in low for k in ["schema", "model", "entity", "relationship", "identity"]):
        sections.append(("Model contract", [
            f"The {subject.lower()} model defines named concepts, their stable identities, ownership, lifecycle, and invariants.",
            "Required and optional fields are distinguished explicitly. Defaults never introduce hidden authority or semantic meaning.",
            "Relationships define direction, cardinality, allowed endpoints, provenance, and whether absence is meaningful.",
            "Invalid states are rejected before they can become canonical or externally observable.",
        ]))
    if any(k in low for k in ["protocol", "api", "event", "command", "interface"]):
        sections.append(("Interaction contract", [
            "Interactions define preconditions, request or message identity, success outcomes, error classes, retry semantics, and observability.",
            "Consumers must be able to determine whether an operation was rejected before effect, committed, partially completed, cancelled, or left with unknown outcome.",
            "Compatibility changes are versioned and tested against representative producers and consumers.",
        ]))
    if any(k in low for k in ["policy", "rule", "validation", "diagnostic", "error"]):
        sections.append(("Evaluation and diagnostics", [
            "Evaluations produce stable machine-readable outcomes and a safe human explanation.",
            "Blocking errors, warnings, informational findings, and internal defects are distinct states.",
            "Diagnostics include a stable identifier, severity, source or entity location, cause context, remediation guidance, and provenance where available.",
        ]))
    if any(k in low for k in ["plan", "roadmap", "strategy", "program", "sprint", "increment", "work-packet"]):
        sections.append(("Planning semantics", [
            "Plans describe outcomes, dependencies, risks, assumptions, sequencing, and decision gates rather than equating activity with progress.",
            "Forecasts remain forecasts until work is explicitly authorized. Scope is refined as evidence changes.",
            "Blocked work names the dependency or decision, its owner, impact, and next escalation point.",
        ]))
    if any(k in low for k in ["review", "acceptance", "readiness", "retrospective", "lessons"]):
        sections.append(("Review record", [
            "The record captures scope reviewed, governing criteria, evidence references, findings, material dissent, decision, authority, date, conditions, and follow-up.",
            "Conditional acceptance names the condition, owner, deadline or trigger, and consequence of non-completion.",
            "Retrospective observations are informative until promoted through the appropriate decision or change-control mechanism.",
        ]))
    if any(k in low for k in ["release", "deployment", "rollback", "migration", "upgrade"]):
        sections.append(("Transition safety", [
            "The transition has an explicit entry condition, target state, verification procedure, failure handling, and rollback or forward-recovery path.",
            "Irreversible steps are identified before authorization and require stronger evidence proportional to consequence.",
            "Release and migration evidence is retained with the artifact version it proves.",
        ]))
    if any(k in low for k in ["security", "permission", "trust", "secret", "supply", "signature", "sbom"]):
        sections.append(("Security contract", [
            "Trust boundaries, privileged actors, sensitive data, secrets, external dependencies, and administrative actions are explicit.",
            "Controls are verified against named threats and failure modes; they are not accepted solely because a tool or vendor is present.",
            "Security-relevant events preserve enough integrity and attribution for authorized reconstruction without collecting unnecessary sensitive payloads.",
        ]))
    if any(k in low for k in ["performance", "benchmark", "capacity", "latency", "throughput"]):
        sections.append(("Measurement contract", [
            "Measurements identify workload, data scale, environment, tool versions, warm-up, repetitions, statistical treatment, and known sources of variance.",
            "A regression is evaluated against an approved baseline and user-visible or operational impact, not an isolated synthetic number.",
            "Performance optimization may not weaken correctness, determinism, security, or diagnosability without explicit approval.",
        ]))
    if any(k in low for k in ["context", "prompt", "agent", "ai", "model-provider", "token"]):
        sections.append(("AI and agent boundary", [
            "The artifact defines which information may enter model context, which actions an agent may propose or perform, and which decisions remain human-only.",
            "Provider-specific capabilities are isolated behind model-independent contracts where practical.",
            "Prompts, context selection, tool use, and generated changes are treated as engineering inputs with provenance rather than invisible implementation detail.",
        ]))
    return sections


def render(path: Path) -> str:
    rel = path.as_posix()
    parts = path.parts
    category = parts[1] if len(parts) > 2 else "repository-and-artifact-governance"
    normalized = normalize_category(category)
    cat_title, cat_desc, concerns = category_context(category)
    stem = path.stem
    subject = slug_to_title(stem)
    kind = artifact_kind(stem)
    owner = owner_for(normalized)
    reviewers = review_roles(normalized)
    purpose = subject_purpose(stem)
    concerns_md = ", ".join(concerns)
    extra = CATEGORY_EXTRA.get(normalized, [])
    rules = subject_rules(stem, normalized, subject)
    sections = specific_sections(stem, normalized, subject)

    out: list[str] = []
    out.append(f"# {subject}")
    out.append("")
    out.append("**Status:** Draft  ")
    out.append(f"**Artifact class:** {cat_title} / {kind}  ")
    out.append(f"**Owner:** {owner}  ")
    out.append(f"**Required reviewers:** {reviewers}  ")
    out.append("**Authority:** Proposed baseline; not authoritative until approved under the document lifecycle  ")
    out.append(f"**Generator baseline:** `populate-artifact-system.py` v{TOOL_VERSION}")
    out.append("")
    out.append("## Purpose")
    out.append("")
    if purpose.startswith(";"):
        purpose = "defines the core contract" + purpose
    out.append(
        f"This artifact {purpose}. It exists within Monad's {cat_title.lower()} concern, which covers "
        f"{cat_desc}. The document turns that concern into an explicit, reviewable engineering contract "
        "rather than leaving it in chat history, tribal knowledge, tool defaults, or implementation accidents."
    )
    out.append("")
    out.append("## Scope")
    out.append("")
    out.append(
        f"In scope are the semantics, responsibilities, evidence, lifecycle, and interfaces directly needed "
        f"to make **{subject}** dependable. The primary quality concerns are {concerns_md}."
    )
    out.append("")
    out.append(
        "Out of scope are unrelated implementation choices, vendor-specific behavior that does not affect the "
        "contract, and authority that belongs to a higher-level vision, governance, accepted ADR, or approved "
        "specification. This artifact may constrain implementation but must not silently expand project scope."
    )
    out.append("")
    out.append("## Governing principles")
    out.append("")
    for rule in rules:
        out.append(f"- {rule}")
    for line in extra:
        out.append(f"- {line}")
    out.append("")
    out.append("## Required inputs")
    out.append("")
    out.extend([
        "- the current approved product and architecture intent relevant to this concern;",
        "- applicable accepted ADRs and approved specifications;",
        "- known security, privacy, reliability, performance, and operational constraints;",
        "- stable identifiers for governed entities and related artifacts;",
        "- evidence from implementation, tests, research, incidents, or prior reviews when available;",
        "- explicit assumptions wherever evidence is incomplete.",
    ])
    out.append("")
    for heading, paras in sections:
        out.append(f"## {heading}")
        out.append("")
        for para in paras:
            out.append(para)
            out.append("")
    out.append("## Interfaces and traceability")
    out.append("")
    out.append(
        "This artifact participates in Monad's end-to-end traceability chain. It should link upward to the "
        "vision, requirement, decision, risk, or policy that justifies it and downward to the specifications, "
        "work packets, implementation, tests, generated artifacts, releases, or operational evidence that realize "
        "or verify it. Those links are semantic relationships, not decorative references."
    )
    out.append("")
    out.append(
        "When another artifact depends on this contract, the dependency should be machine-discoverable through "
        "stable identifiers or resolvable repository references. A change to this artifact must therefore include "
        "impact analysis for known consumers and must regenerate the machine-readable knowledge projection."
    )
    out.append("")
    out.append("## Failure and exception handling")
    out.append("")
    out.append(
        "A violation of this contract is represented explicitly. Invalid input, denied authority, incompatible "
        "version, missing evidence, transient dependency failure, permanent failure, and unknown outcome are not "
        "collapsed into a generic success/failure flag when they require different recovery or governance."
    )
    out.append("")
    out.append(
        "Exceptions are narrow, owned, justified by evidence, time- or trigger-bounded where practical, and recorded "
        "with the residual risk they introduce. An exception cannot silently redefine the underlying rule."
    )
    out.append("")
    out.append("## Lifecycle and change control")
    out.append("")
    out.extend([
        "1. **Draft:** authorship and evidence collection; not relied upon as approved authority.",
        "2. **Review:** scope and semantics are stable enough for designated reviewers to evaluate.",
        "3. **Approved:** the accountable authority accepts the contract within its stated scope.",
        "4. **Implemented:** delivered behavior and evidence conform where implementation status is meaningful.",
        "5. **Deprecated/Superseded/Retired:** transition is explicit, dependencies are migrated, and history is preserved.",
    ])
    out.append("")
    out.append(
        "Meaning-changing updates identify affected consumers, compatibility impact, migration needs, risk change, "
        "and verification changes. Accepted historical meaning is superseded rather than rewritten without trace."
    )
    out.append("")
    out.append("## Verification")
    out.append("")
    out.extend([
        "- Verify that the document's scope and terminology agree with higher-authority artifacts.",
        "- Verify that every mandatory rule has an observable conformance or review method.",
        "- Verify success, boundary, invalid, unauthorized, interrupted, and recovery behavior where applicable.",
        "- Verify compatibility and migration behavior for any externally consumed representation or protocol.",
        "- Verify security and privacy properties at every trust or data boundary introduced by this artifact.",
        "- Verify generated machine companions are synchronized with the canonical source.",
        "- Record evidence links in the implementing work packet, review, or release record.",
    ])
    out.append("")
    out.append("## Acceptance criteria")
    out.append("")
    out.extend([
        "- [ ] Purpose, scope, exclusions, and owner are explicit.",
        "- [ ] Terminology is consistent with `governance/terminology.md` or intentionally narrows it.",
        "- [ ] Governing decisions, requirements, risks, and dependent artifacts are linked.",
        "- [ ] Normative statements are testable or have a defined manual evidence path.",
        "- [ ] Compatibility, security, failure, and recovery concerns are addressed where applicable.",
        "- [ ] Reviewers can distinguish current evidence from assumptions and proposals.",
        "- [ ] Machine-readable projections regenerate without drift.",
        "- [ ] Approval, if granted, records authority, date, scope, conditions, and dissent.",
    ])
    out.append("")
    out.append("## Review trigger")
    out.append("")
    out.append(
        "Review this artifact when a governing requirement or ADR changes, an implementation or incident contradicts "
        "an assumption, compatibility or security impact changes, ownership changes, or a dependent artifact cannot "
        "be implemented or verified without reinterpretation."
    )
    out.append("")
    out.append("## Canonicality")
    out.append("")
    out.append(
        f"`{rel}` is the human-readable canonical source for this artifact once approved. Any representation under "
        "`machine/` is a deterministic derivative and must not be edited independently."
    )
    out.append("")
    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Fail if any artifact-system Markdown file is empty.")
    parser.add_argument("--force", action="store_true", help="Regenerate even non-empty artifact-system Markdown files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    artifact_root = root / "artifact-system"
    if not artifact_root.is_dir():
        raise SystemExit(f"artifact-system directory not found: {artifact_root}")

    files = sorted(p for p in artifact_root.rglob("*.md") if p.is_file())
    if not files:
        raise SystemExit("no artifact-system Markdown files found")

    empty = [p for p in files if not p.read_text(encoding="utf-8").strip()]
    if args.check:
        if empty:
            print(f"{len(empty)} artifact-system Markdown files are empty.")
            for path in empty[:50]:
                print(path.relative_to(root).as_posix())
            if len(empty) > 50:
                print(f"... and {len(empty)-50} more")
            return 1
        print(f"Artifact system is populated: {len(files)} Markdown files, 0 empty.")
        return 0

    targets = files if args.force else empty
    for path in targets:
        path.write_text(render(path.relative_to(root)), encoding="utf-8", newline="\n")
    print(f"Artifact system populated: {len(targets)} files written; {len(files)} total Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
