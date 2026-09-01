---

title: "Monad Publication Projection Contract"
specification ID: "MONAD-PUB-001"
version: "0.1.0"
status: "Draft"
classification: "Normative Publication Projection Contract"
parent: "Monad Engineering Knowledge and Governance System"
description: "Defines the authoritative projection of Monad repository state into the AIC Fumadocs public website"
---

# Monad Publication Projection Contract

## 1. Purpose

This specification defines the normative contract by which engineering knowledge, project state, historical material, operational state, and selected repository metadata from:

`monad-framework/monad`

are projected into:

`monad-framework/aic-fumadocs-app`

The objective is to ensure that the public website accurately represents the actual state of Monad without creating a second source of truth.

The governing relationship SHALL be:

```text
Monad canonical repository state
        ↓
Publication Projection
        ↓
AIC Fumadocs public read model
```

The Fumadocs repository SHALL NOT become an independent authority for Monad requirements, decisions, specifications, architecture, project status, Work Packet state, releases, verification, risks, or other governed engineering facts.

Monad already states that human-readable canonical source remains authoritative and that machine data, GitHub state, and automation are projections rather than replacements for accepted canonical engineering knowledge.

---

# 2. Scope

The Publication Projection Contract governs five projection dispositions:

| Code        | Disposition                   | Meaning                                                                                                  |
| ----------- | ----------------------------- | -------------------------------------------------------------------------------------------------------- |
| `MIRROR`    | Canonical mirror              | Source content is deterministically transformed for publication without changing its engineering meaning |
| `DERIVE`    | Deterministic derived view    | Public state is computed from one or more authoritative sources                                          |
| `LIVE`      | Runtime operational view      | Data is retrieved from GitHub or another authoritative operational source at request/runtime             |
| `EDITORIAL` | Publication-owned content     | Human-authored narrative remains under website authority and is not overwritten                          |
| `EXCLUDE`   | Not publishable by projection | Source SHALL NOT be copied into or automatically exposed by the website                                  |

Any Monad path not explicitly admitted by this contract SHALL default to:

```text
EXCLUDE
```

This is a mandatory deny-by-default rule.

---

# 3. Authority hierarchy

Publication SHALL preserve Monad's existing authority model.

For purposes of the website, the authority order SHALL be:

```text
Accepted canonical Monad engineering knowledge
        ↓
Canonical plans and authorized engineering records
        ↓
Deterministic machine projections
        ↓
GitHub operational/project projections
        ↓
Publication-derived state
        ↓
Editorial interpretation
```

A lower layer MUST NOT silently override a higher layer.

For example:

```text
Accepted ADR says X
GitHub issue says Y
```

The website MUST NOT publish `Y` as the governing architectural decision.

The inconsistency MUST instead be surfaced.

---

# 4. Publication architecture

The Fumadocs repository SHALL introduce a protected generated-data boundary:

```text
content/
└── generated/
    └── monad/
        ├── manifest.json
        ├── provenance.json
        ├── canonical/
        └── state/
            ├── project.json
            ├── roadmap.json
            ├── work-packets.json
            ├── milestones.json
            ├── risks.json
            ├── releases.json
            ├── verification.json
            ├── artifacts.json
            ├── research.json
            └── evolution.json
```

`content/generated/monad/**` SHALL:

* be generated only;
* never contain manually authored public facts;
* identify the exact Monad commit used;
* be reproducible from the same source commit;
* be protected by CI against manual alteration.

Public MDX pages may either be deterministic generated pages or publication-owned presentation shells consuming this state.

---

# 5. Mirror semantics

A `MIRROR` projection SHALL preserve the normative meaning of the source.

Permitted transformations include:

* `.md` → `.mdx`;
* addition of publication frontmatter;
* internal-link rewriting;
* addition of provenance banners;
* safe rendering transformations;
* navigation metadata;
* Fumadocs component wrapping.

A mirror MUST NOT:

* summarize away requirements;
* change normative language;
* reinterpret status;
* alter acceptance criteria;
* silently remove sections;
* have AI rewrite its content.

Every mirrored page SHALL expose at minimum:

```yaml
projection: mirror
source_repository: monad-framework/monad
source_path: <path>
source_commit: <40-character-sha>
source_blob: <blob-sha>
projection_version: 1
generated: true
```

---

# 6. Derived-view semantics

A `DERIVE` projection may combine multiple authoritative sources.

Derived values MUST be deterministic.

For example:

```text
Current MVP status
    =
product/MVP-RELEASE-1.md
+ product/backlog/MVP-BACKLOG.md
+ engineering/project-status.md
+ engineering/work-packets/**
+ engineering/milestones/**
+ relevant verification state
```

An LLM MUST NOT decide authoritative status.

AI MAY generate explanatory editorial text around a derived fact, but the fact itself MUST come from deterministic source interpretation.

---

# 7. Live-view semantics

`LIVE` is reserved for operational facts for which repository projection latency would be undesirable.

Examples include:

* current `main` SHA;
* latest merged PR;
* current CI/check state;
* latest release/tag;
* open PR count;
* GitHub issue counts;
* publication-sync lag;
* most recent successful projection.

Live state SHALL NOT override canonical engineering authority.

For example:

```text
GitHub issue = Closed
canonical Work Packet = Active
```

The public system SHALL indicate disagreement rather than infer that the Work Packet is complete.

---

# 8. Editorial semantics

Editorial content SHALL remain publication-owned.

This includes:

```text
content/articles/**
content/building-monad/**
content/journal/**
```

except for specifically designated generated namespaces.

The website currently maintains distinct article, Building Monad, and journal collections.

Building Monad already contains essays, installments, phases, and series content; those are publication narrative surfaces rather than authoritative engineering state.

Editorial material describing a particular Monad state SHOULD declare:

```yaml
monad_snapshot: <commit-sha>
```

Historical editorial content SHALL NOT be rewritten merely because Monad changes later.

---

# 9. Canonical source-to-destination mapping

## 9.1 Repository root

| Monad source            | Fumadocs destination                                         | Mode      | Rule                                                                   |
| ----------------------- | ------------------------------------------------------------ | --------- | ---------------------------------------------------------------------- |
| `README.md`             | `content/generated/monad/canonical/README.md`                | `MIRROR`  | Canonical source input for System and Project overview                 |
| `README.md`             | `content/docs/system/index.mdx`                              | `DERIVE`  | System overview combines README with authoritative vision/architecture |
| `VERSION`               | `content/generated/monad/state/project.json#/version`        | `DERIVE`  | No standalone page                                                     |
| `CHANGELOG.md`          | `content/changelogs/monad.mdx`                               | `MIRROR`  | Canonical release/change narrative                                     |
| `LICENSE`               | `content/docs/project/community/license.mdx`                 | `MIRROR`  | Public legal information                                               |
| `CONTRIBUTING.md`       | `content/docs/project/community/contributing.mdx`            | `MIRROR`  | Public contributor guidance                                            |
| `CODE_OF_CONDUCT.md`    | `content/docs/project/community/code-of-conduct.mdx`         | `MIRROR`  | Public community governance                                            |
| `SECURITY.md`           | `content/docs/system/security/reporting.mdx`                 | `MIRROR`  | Public security-reporting guidance                                     |
| `system-description.md` | `content/docs/system/concepts/target-system-description.mdx` | `MIRROR`  | MUST be visibly marked as target-system description                    |
| `idea.md`               | `content/journal/monad-source/idea.mdx`                      | `MIRROR`  | Historical inception artifact                                          |
| `next-steps.md`         | —                                                            | `EXCLUDE` | Transient operator guidance; not authoritative public status           |
| `Cargo.toml`            | selected metadata only                                       | `DERIVE`  | Package/workspace facts if needed                                      |
| `Cargo.lock`            | —                                                            | `EXCLUDE` | Implementation dependency lockfile                                     |
| `monad.toml`            | selected project identity only                               | `DERIVE`  | Raw file not published                                                 |
| `.editorconfig`         | —                                                            | `EXCLUDE` | Implementation/configuration                                           |
| `.gitattributes`        | —                                                            | `EXCLUDE` | Implementation/configuration                                           |
| `.gitignore`            | —                                                            | `EXCLUDE` | Implementation/configuration                                           |
| `.githubignore`         | —                                                            | `EXCLUDE` | Implementation/configuration                                           |

The current Monad root includes these governance, Rust, bootstrap, implementation, documentation, machine-state, and engineering families, making an explicit exclusion policy necessary.

---

# 10. Vision mapping

Monad currently maintains `product-vision.md`, `problem-statement.md`, goals, non-goals, principles, and success criteria under `vision/`.

| Monad source                  | Fumadocs destination                                 | Mode     |
| ----------------------------- | ---------------------------------------------------- | -------- |
| `vision/README.md`            | `content/docs/system/concepts/vision.mdx`            | `MIRROR` |
| `vision/product-vision.md`    | `content/docs/system/concepts/product-vision.mdx`    | `MIRROR` |
| `vision/problem-statement.md` | `content/docs/system/concepts/problem-statement.mdx` | `MIRROR` |
| `vision/goals.md`             | `content/docs/system/concepts/goals.mdx`             | `MIRROR` |
| `vision/non-goals.md`         | `content/docs/system/concepts/non-goals.mdx`         | `MIRROR` |
| `vision/principles.md`        | `content/docs/system/concepts/principles.mdx`        | `MIRROR` |
| `vision/success-criteria.md`  | `content/docs/system/concepts/success-criteria.mdx`  | `MIRROR` |

These pages SHALL be automatically replaced whenever their corresponding Monad sources change.

---

# 11. Product mapping

Monad currently contains the MVP definition, Product Goal, post-MVP goals, capabilities, constraints, personas, requirements, roadmap, use cases, journeys, and backlog.

| Monad source                                                  | Fumadocs destination                                           | Mode     |
| ------------------------------------------------------------- | -------------------------------------------------------------- | -------- |
| `product/README.md`                                           | `content/docs/system/concepts/product.mdx`                     | `MIRROR` |
| `product/PRODUCT-GOAL.md`                                     | `content/docs/project/product-goal.mdx`                        | `MIRROR` |
| `product/MVP-RELEASE-1.md`                                    | `content/docs/project/mvp-release-1.mdx`                       | `MIRROR` |
| `product/POST-MVP-PRODUCT-GOALS.md`                           | `content/docs/project/post-mvp-goals.mdx`                      | `MIRROR` |
| `product/capabilities.md`                                     | `content/docs/system/concepts/capabilities.mdx`                | `MIRROR` |
| `product/constraints.md`                                      | `content/docs/system/concepts/constraints.mdx`                 | `MIRROR` |
| `product/personas.md`                                         | `content/docs/system/concepts/personas.mdx`                    | `MIRROR` |
| `product/use-cases.md`                                        | `content/docs/system/concepts/use-cases.mdx`                   | `MIRROR` |
| `product/user-journeys.md`                                    | `content/docs/system/concepts/user-journeys.mdx`               | `MIRROR` |
| `product/product-requirements.md`                             | `content/docs/artifacts/requirements/product-requirements.mdx` | `MIRROR` |
| `product/roadmap.md`                                          | `content/generated/monad/canonical/product/roadmap.md`         | `MIRROR` |
| `product/backlog/**`                                          | `content/generated/monad/canonical/product/backlog/**`         | `MIRROR` |
| `product/roadmap.md` + `product/backlog/**` + execution state | `content/docs/project/roadmap.mdx`                             | `DERIVE` |

The current MVP backlog already carries epic, feature, Work Packet, story, scheduling, and acceptance information and therefore SHOULD feed public project-state generation rather than be rewritten manually.

---

# 12. Architecture mapping

Monad's canonical ADR root is `architecture/decisions/`, accompanied by context, overview, principles, quality attributes, boundaries, diagrams, and explorations.

| Monad source                         | Fumadocs destination                                                | Mode     |
| ------------------------------------ | ------------------------------------------------------------------- | -------- |
| `architecture/README.md`             | `content/docs/system/architecture/index.mdx`                        | `MIRROR` |
| `architecture/overview.md`           | `content/docs/system/architecture/overview.mdx`                     | `MIRROR` |
| `architecture/context.md`            | `content/docs/system/architecture/context.mdx`                      | `MIRROR` |
| `architecture/principles.md`         | `content/docs/system/architecture/principles.mdx`                   | `MIRROR` |
| `architecture/quality-attributes.md` | `content/docs/system/architecture/quality-attributes.mdx`           | `MIRROR` |
| `architecture/system-boundaries.md`  | `content/docs/system/architecture/system-boundaries.mdx`            | `MIRROR` |
| `architecture/decisions/**/*.md`     | `content/docs/artifacts/decisions/<relative-path>.mdx`              | `MIRROR` |
| `architecture/diagrams/**`           | `public/generated/monad/architecture/diagrams/**`                   | `MIRROR` |
| `architecture/explorations/**/*.md`  | `content/docs/system/architecture/explorations/<relative-path>.mdx` | `MIRROR` |

Explorations MUST retain their original status and MUST NOT be presented as accepted architecture.

---

# 13. Specification mapping

The current specification root contains MKE, data, interface, technical, baseline, and specification-index material.

| Monad source                                          | Fumadocs destination                                                   | Mode     |
| ----------------------------------------------------- | ---------------------------------------------------------------------- | -------- |
| `specifications/README.md`                            | `content/docs/artifacts/specifications/index.mdx`                      | `MIRROR` |
| `specifications/baseline.md`                          | `content/docs/artifacts/specifications/baseline.mdx`                   | `MIRROR` |
| `specifications/MKE/**/*.md`                          | `content/docs/artifacts/specifications/MKE/<relative-path>.mdx`        | `MIRROR` |
| `specifications/data/**/*.md`                         | `content/docs/artifacts/specifications/data/<relative-path>.mdx`       | `MIRROR` |
| `specifications/interfaces/**/*.md`                   | `content/docs/artifacts/specifications/interfaces/<relative-path>.mdx` | `MIRROR` |
| `specifications/technical/**/*.md`                    | `content/docs/artifacts/specifications/technical/<relative-path>.mdx`  | `MIRROR` |
| structured schemas embedded under `specifications/**` | `public/generated/monad/specifications/<relative-path>`                | `MIRROR` |

---

# 14. Artifact-system mapping

`artifact-system/` is the comprehensive catalog of engineering artifact contracts, including KIR, architecture, AI/agent architecture, API/protocol artifacts, build/execution, change requests, CI/CD, CLI design, configuration, decision management, and other artifact families.

A new public Artifact Catalog SHALL be added.

| Monad source                | Fumadocs destination                                     | Mode     |
| --------------------------- | -------------------------------------------------------- | -------- |
| `artifact-system/README.md` | `content/docs/artifacts/catalog/index.mdx`               | `MIRROR` |
| `artifact-system/**/*.md`   | `content/docs/artifacts/catalog/<relative-path>.mdx`     | `MIRROR` |
| `artifact-system/**/*.json` | `public/generated/monad/artifact-system/<relative-path>` | `MIRROR` |
| `artifact-system/**/*.yaml` | `public/generated/monad/artifact-system/<relative-path>` | `MIRROR` |
| `artifact-system/**/*.yml`  | `public/generated/monad/artifact-system/<relative-path>` | `MIRROR` |

This SHALL be separate from instance artifacts such as actual ADRs, reviews, evidence, or requirements.

---

# 15. Governance mapping

Monad currently contains authority, canonical-state, change-control, decision-process, document-lifecycle, execution, planning, policy, responsibility, terminology, traceability, and related governance documents.

| Monad source                          | Fumadocs destination                                       | Mode                                |
| ------------------------------------- | ---------------------------------------------------------- | ----------------------------------- |
| `governance/README.md`                | `content/docs/system/governance/index.mdx`                 | `MIRROR`                            |
| `governance/authority.md`             | `content/docs/system/governance/authority.mdx`             | `MIRROR`                            |
| `governance/canonical-state-model.md` | `content/docs/system/governance/canonical-state-model.mdx` | `MIRROR`                            |
| `governance/change-control.md`        | `content/docs/system/governance/change-control.mdx`        | `MIRROR`                            |
| `governance/decision-process.md`      | `content/docs/system/governance/decision-process.mdx`      | `MIRROR`                            |
| `governance/document-lifecycle.md`    | `content/docs/system/governance/document-lifecycle.mdx`    | `MIRROR`                            |
| `governance/execution-engine.md`      | `content/docs/system/execution/execution-engine.mdx`       | `MIRROR`                            |
| `governance/planning-engine.md`       | `content/docs/system/execution/planning-engine.mdx`        | `MIRROR`                            |
| `governance/policy-engine.md`         | `content/docs/system/governance/policy-engine.mdx`         | `MIRROR`                            |
| `governance/override-policy.md`       | `content/docs/system/governance/override-policy.mdx`       | `MIRROR`                            |
| `governance/responsibility-model.md`  | `content/docs/system/governance/responsibility-model.mdx`  | `MIRROR`                            |
| `governance/terminology.md`           | `content/docs/system/glossary/terminology.mdx`             | `MIRROR`                            |
| `governance/traceability-graph.md`    | `content/docs/artifacts/traceability/graph.mdx`            | `MIRROR`                            |
| `governance/event-ledger.md`          | `content/docs/system/execution/event-ledger.mdx`           | `MIRROR`                            |
| `governance/github-integration.md`    | `content/docs/system/integrations/github.mdx`              | `MIRROR`                            |
| any future `governance/*.md`          | `content/docs/system/governance/<filename>.mdx`            | `MIRROR` unless explicitly remapped |

---

# 16. Engineering execution mapping

Monad explicitly treats `engineering/` as the location for milestones, increments, work cycles, Work Packets, project status, reviews, and risks.

The current directory contains project status, engineering planning, DoR/DoD, EOS material, evidence, GitHub material, increments, lifecycle, maintenance, milestones, reviews, risks, stabilization, and Work Packets.

## 16.1 Project state

| Monad source                                             | Fumadocs destination                                              | Mode     |
| -------------------------------------------------------- | ----------------------------------------------------------------- | -------- |
| `engineering/project-status.md`                          | `content/generated/monad/canonical/engineering/project-status.md` | `MIRROR` |
| project status + active work + backlog + milestone state | `content/docs/project/status.mdx`                                 | `DERIVE` |
| same aggregate                                           | `content/docs/project/index.mdx`                                  | `DERIVE` |
| same aggregate                                           | `content/docs/project/now.mdx`                                    | `DERIVE` |

The existing `content/docs/project/index.mdx` SHALL therefore cease being an independently maintained statement of current project truth. The Project collection currently has that single public index page.

## 16.2 Planning and lifecycle

| Monad source                         | Destination                                                     | Mode     |
| ------------------------------------ | --------------------------------------------------------------- | -------- |
| `engineering/engineering-plan.md`    | `content/docs/project/engineering-plan.mdx`                     | `MIRROR` |
| `engineering/definition-of-ready.md` | `content/docs/system/governance/definition-of-ready.mdx`        | `MIRROR` |
| `engineering/definition-of-done.md`  | `content/docs/system/governance/definition-of-done.mdx`         | `MIRROR` |
| `engineering/increments/**/*.md`     | `content/docs/project/increments/<relative-path>.mdx`           | `MIRROR` |
| `engineering/milestones/**/*.md`     | `content/docs/project/milestones/<relative-path>.mdx`           | `MIRROR` |
| `engineering/work-cycles/**/*.md`    | `content/docs/project/work-cycles/<relative-path>.mdx`          | `MIRROR` |
| `engineering/lifecycle/**/*.md`      | `content/docs/system/execution/lifecycle/<relative-path>.mdx`   | `MIRROR` |
| `engineering/maintenance/**/*.md`    | `content/docs/system/execution/maintenance/<relative-path>.mdx` | `MIRROR` |

## 16.3 Work Packets

Monad already contains individual current MVP Work Packets in `engineering/work-packets/`.

| Source                               | Destination                                             | Mode     |
| ------------------------------------ | ------------------------------------------------------- | -------- |
| `engineering/work-packets/README.md` | `content/docs/project/work-packets/index.mdx`           | `DERIVE` |
| `engineering/work-packets/*.md`      | `content/docs/project/work-packets/<same-basename>.mdx` | `MIRROR` |
| all Work Packets + backlog           | `content/generated/monad/state/work-packets.json`       | `DERIVE` |

The Work Packet index SHALL calculate current states rather than hard-code them.

## 16.4 Risks, review and evidence

| Source                                   | Destination                                           | Mode     |
| ---------------------------------------- | ----------------------------------------------------- | -------- |
| `engineering/risks/**/*.md`              | `content/docs/project/risks/<relative-path>.mdx`      | `MIRROR` |
| all risk state                           | `content/docs/project/risks/index.mdx`                | `DERIVE` |
| `engineering/reviews/**/*.md`            | `content/docs/artifacts/reviews/<relative-path>.mdx`  | `MIRROR` |
| `engineering/evidence/**/*.md`           | `content/docs/artifacts/evidence/<relative-path>.mdx` | `MIRROR` |
| `engineering/changes/**/*.md`            | `content/docs/project/changes/<relative-path>.mdx`    | `MIRROR` |
| changes + commits + accepted transitions | `content/generated/monad/state/evolution.json`        | `DERIVE` |

## 16.5 Engineering support material

| Source                              | Destination                                                   | Mode      |
| ----------------------------------- | ------------------------------------------------------------- | --------- |
| `engineering/eos/**/*.md`           | `content/docs/system/governance/eos/<relative-path>.mdx`      | `MIRROR`  |
| `engineering/github/**/*.md`        | `content/docs/system/integrations/github/<relative-path>.mdx` | `MIRROR`  |
| `engineering/stabilization/**/*.md` | `content/docs/project/stabilization/<relative-path>.mdx`      | `MIRROR`  |
| `engineering/prompts/**`            | —                                                             | `EXCLUDE` |

Agent prompts are execution inputs rather than public documentation and SHALL remain excluded unless an individual artifact is explicitly approved for publication.

---

# 17. Research mapping

Monad currently has a research index and open research questions.

| Source                                | Destination                                                    | Mode     |
| ------------------------------------- | -------------------------------------------------------------- | -------- |
| `research/README.md`                  | `content/docs/project/research.mdx`                            | `MIRROR` |
| `research/questions.md`               | `content/docs/project/open-questions.mdx`                      | `MIRROR` |
| future `research/experiments/**/*.md` | `content/docs/artifacts/experiments/<relative-path>.mdx`       | `MIRROR` |
| future `research/evidence/**/*.md`    | `content/docs/artifacts/evidence/research/<relative-path>.mdx` | `MIRROR` |
| future `research/findings/**/*.md`    | `content/docs/artifacts/evidence/findings/<relative-path>.mdx` | `MIRROR` |

Human-written interpretation of research MAY additionally appear under:

```text
content/articles/research/**
```

but such articles remain `EDITORIAL`.

The site already maintains a separate research-article collection for this purpose.

---

# 18. Security mapping

Monad currently contains a security model, threat model, and supply-chain model.

A new System Security section SHALL be created.

| Source                       | Destination                                       | Mode     |
| ---------------------------- | ------------------------------------------------- | -------- |
| `security/README.md`         | `content/docs/system/security/index.mdx`          | `MIRROR` |
| `security/security-model.md` | `content/docs/system/security/security-model.mdx` | `MIRROR` |
| `security/threat-model.md`   | `content/docs/system/security/threat-model.mdx`   | `MIRROR` |
| `security/supply-chain.md`   | `content/docs/system/security/supply-chain.mdx`   | `MIRROR` |

Private vulnerabilities, unpublished advisories, secrets, or security-sensitive operational information SHALL never be introduced merely because they exist in a source repository or GitHub API.

---

# 19. Testing and verification mapping

Monad currently defines acceptance, performance, quality gates, and test strategy under `testing/`.

| Source                       | Destination                                             | Mode     |
| ---------------------------- | ------------------------------------------------------- | -------- |
| `testing/README.md`          | `content/docs/artifacts/verification/index.mdx`         | `MIRROR` |
| `testing/strategy.md`        | `content/docs/artifacts/verification/test-strategy.mdx` | `MIRROR` |
| `testing/acceptance.md`      | `content/docs/artifacts/verification/acceptance.mdx`    | `MIRROR` |
| `testing/performance.md`     | `content/docs/artifacts/verification/performance.mdx`   | `MIRROR` |
| `testing/quality-gates.md`   | `content/docs/artifacts/verification/quality-gates.mdx` | `MIRROR` |
| actual verification evidence | `content/generated/monad/state/verification.json`       | `DERIVE` |

The distinction between verification **policy/strategy** and verification **result/evidence** SHALL remain explicit.

---

# 20. Operations mapping

Monad currently maintains deployment, environments, incident response, observability, and reliability documentation.

A new System Operations section SHALL be created.

| Source                            | Destination                                            | Mode     |
| --------------------------------- | ------------------------------------------------------ | -------- |
| `operations/README.md`            | `content/docs/system/operations/index.mdx`             | `MIRROR` |
| `operations/deployment.md`        | `content/docs/system/operations/deployment.mdx`        | `MIRROR` |
| `operations/environments.md`      | `content/docs/system/operations/environments.mdx`      | `MIRROR` |
| `operations/incident-response.md` | `content/docs/system/operations/incident-response.mdx` | `MIRROR` |
| `operations/observability.md`     | `content/docs/system/operations/observability.mdx`     | `MIRROR` |
| `operations/reliability.md`       | `content/docs/system/operations/reliability.mdx`       | `MIRROR` |

---

# 21. Journal mapping

Monad's repository journal is explicitly historical/informative material, and currently includes the project-inception journal plus the Building Monad journal family.

To prevent collision with website-owned editorial journal material:

| Source                                                | Destination                                               | Mode        |
| ----------------------------------------------------- | --------------------------------------------------------- | ----------- |
| `journal/README.md`                                   | `content/journal/monad-source/index.mdx`                  | `MIRROR`    |
| `journal/0001-project-inception.md`                   | `content/journal/monad-source/0001-project-inception.mdx` | `MIRROR`    |
| `journal/**/*.md`                                     | `content/journal/monad-source/<relative-path>.mdx`        | `MIRROR`    |
| existing `content/journal/**` outside `monad-source/` | unchanged                                                 | `EDITORIAL` |

The namespace boundary SHALL be:

```text
content/journal/monad-source/**    generated from Monad
content/journal/**                 website editorial otherwise
```

---

# 22. Machine projection mapping

Monad's `machine/` directory already contains generated documents, a graph, manifest, corpus, and schemas. The current corpus alone is approximately 18.9 MB, demonstrating why the complete machine representation should not simply be copied into the website repository.

| Source                  | Destination                      | Mode                                   |
| ----------------------- | -------------------------------- | -------------------------------------- |
| `machine/README.md`     | —                                | `EXCLUDE`                              |
| `machine/corpus.jsonl`  | —                                | `EXCLUDE`                              |
| `machine/documents/**`  | —                                | `EXCLUDE`                              |
| `machine/graph.json`    | projection input only            | `EXCLUDE` from raw publication         |
| `machine/manifest.json` | projection-validation input only | `EXCLUDE` from raw publication         |
| `machine/schemas/**`    | projection-validation input only | `EXCLUDE` unless specifically promoted |

Machine data MAY be used to validate relationships and generate indexes.

It MUST NOT become the website's authority over its canonical source.

---

# 23. EOS control-state mapping

`.eos/**` SHALL be:

```text
EXCLUDE by default
```

Raw EOS ledgers, contracts, machine control state, event state, adoption state, and agent execution context SHALL NOT be mirrored.

Selected facts MAY be deterministically derived where they are required for public project status.

Allowed examples:

```text
active Work Packet identifier
authorized/closed lifecycle state
current work-cycle identifier
verification result
release readiness
```

The derivation MUST cross-check canonical engineering records.

No raw `.eos/` document shall become a public page merely because it exists.

---

# 24. Implementation-source exclusions

The following SHALL NOT be automatically published as documentation:

```text
crates/**
scripts/**
tools/**
completions/**
bootstrap-*.sh
Cargo.lock
.github/**
.monad/**
.eos/**
machine/**
```

They may contribute metadata or operational signals to a `DERIVE` or `LIVE` projection.

Source code itself remains accessible through GitHub and does not need to be duplicated into Fumadocs.

---

# 25. Fumadocs-owned exclusions

The following destination families SHALL never be overwritten by Monad projection:

```text
app/**
components/**
lib/**
public/** except public/generated/monad/**
content/articles/**
content/building-monad/**
content/journal/** except content/journal/monad-source/**
```

Likewise, existing numbered historical/tutorial content at the root of `content/docs/` and unrelated AIEOS material SHALL remain publication-owned unless individually migrated into this contract.

The current `content/docs/` root contains both numbered historical/project-development content and AIEOS documents, demonstrating why broad directory synchronization would be unsafe.

---

# 26. Artifact-area destination contract

The website already exposes these artifact families:

```text
decisions
evidence
experiments
models
policies
releases
requirements
reviews
schemas
specifications
traceability
verification
```

The projection SHALL preserve those families and add:

```text
content/docs/artifacts/catalog/
```

for the comprehensive Monad artifact-system catalog.

`content/docs/artifacts/index.mdx` SHALL become a deterministic artifact-manifest view rather than a manually maintained inventory.

---

# 27. System-area destination contract

The website already provides System sections for:

```text
architecture
components
concepts
execution
glossary
governance
integrations
interfaces
```

The contract SHALL add:

```text
system/security/
system/operations/
```

The System index SHALL become a curated presentation shell backed by projected authoritative content.

---

# 28. Derived public pages

The following pages SHOULD contain no manually maintained project-state values.

## `/project/now`

Sources:

```text
engineering/project-status.md
engineering/work-packets/**
product/backlog/**
engineering/milestones/**
```

Output:

```text
active increment
active work cycle
active Work Packets
current objective
next significant gate
blocking risks
```

## `/project/status`

Sources:

```text
project-status
backlog
work packets
risks
verification
release state
GitHub live state
```

Output:

```text
overall project state
MVP state
latest accepted work
current blockers
sync freshness
```

## `/project/roadmap`

Sources:

```text
product/roadmap.md
product/backlog/**
engineering/milestones/**
engineering/increments/**
```

## `/project/work-packets`

Sources:

```text
engineering/work-packets/**
product/backlog/**
```

## `/project/releases`

Sources:

```text
VERSION
CHANGELOG.md
release artifacts
GitHub Releases API
```

## `/project/risks`

Sources:

```text
engineering/risks/**
```

## `/project/open-questions`

Source:

```text
research/questions.md
```

---

# 29. Live operational projection

The Fumadocs application SHALL provide:

```text
app/api/monad/status/route.ts
lib/monad/github.ts
components/monad/projection-status.tsx
```

The runtime status endpoint SHALL expose a bounded schema such as:

```json
{
  "repository": "monad-framework/monad",
  "branch": "main",
  "headSha": "...",
  "projectedSha": "...",
  "latestRelease": "...",
  "ciState": "success",
  "openPullRequests": 0,
  "lastProjectionAt": "...",
  "lagSeconds": 42,
  "freshness": "current"
}
```

It SHALL NOT expose arbitrary GitHub API responses.

---

# 30. Projection manifest

Every projection run SHALL create:

```text
content/generated/monad/manifest.json
```

Minimum schema:

```json
{
  "projectionVersion": 1,
  "sourceRepository": "monad-framework/monad",
  "sourceBranch": "main",
  "sourceCommit": "<sha>",
  "generatedAt": "<timestamp>",
  "artifacts": [
    {
      "sourcePath": "architecture/decisions/ADR-0001.md",
      "sourceBlob": "<sha>",
      "destinationPath": "content/docs/artifacts/decisions/ADR-0001.mdx",
      "mode": "MIRROR",
      "contentHash": "<sha256>"
    }
  ]
}
```

The manifest SHALL be the complete inventory of generated publication state.

---

# 31. Deletion and rename semantics

Projection MUST be inventory-based rather than copy-only.

If an artifact disappears from the authoritative projection set:

```text
previous manifest contains artifact
current manifest does not
```

the generated destination SHALL be removed.

This applies to:

* deletion;
* rename;
* move;
* supersession where the source artifact itself is removed;
* category migration.

Editorial files MUST NEVER be deleted through this process.

---

# 32. Conflict behavior

A generated destination file SHALL contain a machine ownership marker.

Manual modification of a generated artifact SHALL cause verification failure.

The synchronizer SHALL NOT attempt a merge.

Correct behavior:

```text
generated file manually changed
        ↓
CI failure
        ↓
regenerate from Monad
```

not:

```text
attempt to preserve both edits
```

---

# 33. Publication eligibility

Only state committed to the authoritative Monad branch SHALL be eligible for normal publication.

Normal rule:

```text
source branch = main
```

PR branches, speculative branches, local working state, and unmerged proposals MUST NOT appear as current public state.

Draft/Proposed artifacts that exist on `main` MAY be published, but their lifecycle status MUST be preserved visibly.

Publication does not imply acceptance.

---

# 34. Synchronization triggering

The primary trigger SHALL be:

```text
push to monad/main
```

Monad SHALL send only an event containing identity information such as:

```json
{
  "repository": "monad-framework/monad",
  "sha": "<sha>",
  "projectionVersion": 1
}
```

The consumer SHALL retrieve and validate the identified source revision.

The event payload SHALL NOT itself be treated as authoritative document content.

---

# 35. Reconciliation

The Fumadocs repository SHALL independently reconcile source and destination state on a recurring schedule.

Required invariant:

```text
projected source SHA == latest publishable Monad SHA
```

If the values differ, the consumer SHALL attempt synchronization.

This protects against:

* lost dispatch events;
* cancelled workflows;
* temporary GitHub failures;
* deployment failures;
* credentials failures.

---

# 36. Ordering and regression protection

A delayed synchronization event MUST NOT cause the website to regress to an older commit.

Before applying projection `B`, the synchronizer SHALL verify that `B` is not older than the currently projected source according to Monad branch ancestry.

Out-of-order events SHALL be ignored.

---

# 37. Freshness classification

The website SHALL expose publication freshness.

Recommended initial states:

```text
CURRENT
SYNCING
STALE
FAILED
```

Recommended initial thresholds:

```text
0–5 minutes       CURRENT
active projection SYNCING
5–10 minutes      STALE
>10 minutes       FAILED
```

Thresholds MAY later become formal SLO configuration.

A stale public projection SHALL identify both:

```text
projected Monad SHA
current Monad main SHA
```

The site MUST NOT pretend stale state is current.

---

# 38. Editorial snapshot policy

Any editorial article making concrete claims about Monad architecture or project state SHOULD carry:

```yaml
monad_snapshot: <sha>
```

A historical article SHALL display:

```text
This article describes Monad at commit <sha>.
Current Monad state may differ.
```

The article itself remains unchanged.

This produces:

```text
historical truth
!=
current truth
```

without losing either.

---

# 39. AI policy

AI MAY:

* draft explanatory blog posts;
* summarize already-derived changes;
* explain an ADR;
* draft a weekly development narrative;
* suggest related artifacts.

AI MUST NOT be responsible for determining:

* requirement status;
* ADR authority;
* Work Packet state;
* milestone completion;
* release readiness;
* verification success;
* authoritative roadmap position.

Those values SHALL be deterministic.

---

# 40. Required artifacts in `monad`

The implementation of this contract requires the following new source-side artifacts:

```text
publication/
└── website/
    ├── projection.yaml
    └── README.md

schemas/
└── publication/
    └── site-state.schema.json

scripts/
└── export-site-state.py

.github/
└── workflows/
    └── publish-site-state.yml
```

`projection.yaml` SHALL encode the mapping rules defined by this specification.

The mapping MUST NOT exist solely as imperative workflow code.

---

# 41. Required artifacts in `aic-fumadocs-app`

```text
content/
└── generated/
    └── monad/
        ├── manifest.json
        ├── provenance.json
        ├── canonical/
        └── state/

lib/
└── monad/
    ├── projection.ts
    ├── state.ts
    └── github.ts

scripts/
├── sync-monad.ts
└── verify-monad-sync.ts

components/
└── monad/
    ├── projection-status.tsx
    └── source-provenance.tsx

app/
└── api/
    └── monad/
        └── status/
            └── route.ts

.github/
└── workflows/
    ├── sync-monad.yml
    └── reconcile-monad.yml
```

The Fumadocs app already provides deterministic build, type-check, lint, and formatting commands that can serve as publication gates.

---

# 42. Build gates

A synchronized update SHALL NOT be publishable unless all required gates pass.

Minimum gates:

```text
projection schema validation
projection manifest validation
source provenance validation
generated-file ownership validation
internal-link validation
MDX compilation
Next.js build
TypeScript check
Biome check
drift check
```

---

# 43. Required provenance UI

Every projected public artifact SHOULD display a compact provenance control containing:

```text
Source: monad-framework/monad
Path: architecture/decisions/ADR-0017.md
Commit: 428326a
Status: Accepted
Synchronized: <timestamp>
```

The commit and source path SHOULD link to the exact source revision rather than mutable `main`.

---

# 44. Global projection status

The website SHOULD expose global status in its Project surface and optionally its footer/header:

```text
Monad source
428326a

Projection
Current

Last synchronized
42 seconds ago
```

This status MUST be machine-derived.

---

# 45. Evolution stream

The site SHALL generate an engineering evolution dataset from authoritative events.

Inputs MAY include:

```text
accepted ADR changes
specification changes
requirement changes
Work Packet transitions
milestone transitions
verification outcomes
releases
merged PRs
```

Output:

```text
content/generated/monad/state/evolution.json
```

The website MAY render this as:

```text
09:42  WP-MVP-0004 completed
09:31  ADR-0017 accepted
08:54  PR #240 merged
08:22  specification amended
```

Machine-generated event facts SHALL remain separate from human interpretation of those events.

---

# 46. Publication invariants

The system SHALL satisfy all of the following.

### PPC-INV-001 — Single authority

No generated Monad engineering fact may originate solely in `aic-fumadocs-app`.

### PPC-INV-002 — Exact provenance

Every generated fact must resolve to an exact source revision.

### PPC-INV-003 — Determinism

Identical source state must produce identical projection state except explicitly identified timestamps.

### PPC-INV-004 — No silent conflict

Conflicting representations must be surfaced.

### PPC-INV-005 — Deletion propagation

Removed projected artifacts must disappear from generated publication state.

### PPC-INV-006 — Editorial preservation

Synchronization may not alter publication-owned editorial content.

### PPC-INV-007 — Deny by default

Unknown source paths are excluded until explicitly classified.

### PPC-INV-008 — No state regression

Out-of-order events cannot move the website to an older Monad state.

### PPC-INV-009 — Honest freshness

The website must disclose stale projection state.

### PPC-INV-010 — No AI authority

AI-generated interpretation cannot determine authoritative engineering state.

### PPC-INV-011 — Main-only current state

Only publishable state descended from the authoritative `main` branch may be presented as current.

### PPC-INV-012 — Local reproducibility

A developer must be able to reproduce the same projection locally from a specified Monad commit.

---

# 47. Resulting ownership model

After adoption, repository ownership becomes:

```text
MONAD
│
├── owns engineering truth
├── owns project truth
├── owns artifact truth
├── owns lifecycle truth
├── owns architectural truth
└── publishes a deterministic projection
        │
        ▼
AIC FUMADOCS
│
├── owns presentation
├── owns navigation
├── owns editorial narrative
├── owns historical interpretation
├── owns website application behavior
└── renders Monad's authoritative projection
```

The website is therefore not a duplicate documentation repository.

It is:

> **the public, provenance-preserving, near-real-time read model of Monad's governed engineering knowledge, combined with a separately governed editorial narrative of how Monad is being created and evolved.**

---

# 48. Final classification summary

```text
vision/**                         MIRROR
product/**                       MIRROR + DERIVE
architecture/**                  MIRROR
specifications/**                MIRROR
artifact-system/**               MIRROR
governance/**                    MIRROR
engineering/**                   MIRROR + DERIVE
research/**                      MIRROR
security/**                      MIRROR
testing/**                       MIRROR + DERIVE
operations/**                    MIRROR
journal/**                       MIRROR into isolated source namespace

VERSION                           DERIVE
selected GitHub state             LIVE
selected EOS state                DERIVE

machine/**                        EXCLUDE raw
.eos/**                           EXCLUDE raw
.github/**                        EXCLUDE raw
.monad/**                         EXCLUDE raw
crates/**                         EXCLUDE raw
scripts/**                        EXCLUDE raw
tools/**                          EXCLUDE raw
bootstrap-*.sh                   EXCLUDE
completions/**                   EXCLUDE
Cargo.lock                        EXCLUDE
next-steps.md                     EXCLUDE

content/articles/**              EDITORIAL
content/building-monad/**         EDITORIAL
content/journal/**                EDITORIAL except monad-source/**
site application code             EDITORIAL / SITE-OWNED
```

This classification is normative.
