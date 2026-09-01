# Monad Website Publication Projection

This directory contains the executable policy governing publication of Monad engineering knowledge to the public AIC Fumadocs website.

The normative contract for this projection is:

* `MONAD-PUB-001 — Monad Publication Projection Contract`
* `specifications/publication/MONAD-PUB-001-publication-projection-contract.md`

## Purpose

Monad is the authority for its governed engineering knowledge.

The AIC Fumadocs website is a downstream publication surface. It must not independently determine Monad architecture, requirements, project status, lifecycle state, verification status, or other governed engineering facts.

This directory defines how authoritative Monad state is transformed into a deterministic public projection.

The intended relationship is:

```text
Canonical Monad engineering knowledge
            |
            v
MONAD-PUB-001
            |
            v
publication/website/projection.yaml
            |
            v
deterministic publication exporter
            |
            v
AIC Fumadocs publication projection
```

## Authority

`MONAD-PUB-001` is normative.

`projection.yaml` is executable policy implementing that specification.

If this configuration conflicts with the normative publication specification, the normative specification wins and this configuration must be corrected.

Neither this configuration nor the generated website projection may supersede canonical Monad engineering knowledge.

## Files

### `projection.yaml`

Defines:

* source repository identity;
* destination repository identity;
* publishable branch policy;
* publication dispositions;
* deterministic transformations;
* provenance requirements;
* generated-content ownership;
* explicit source-to-destination mappings;
* derived-state inputs and outputs;
* live-state boundaries;
* exclusion rules;
* reconciliation constraints;
* deletion behavior;
* conflict behavior;
* publication invariants.

The configuration follows a deny-by-default policy.

A source path that is not explicitly admitted is excluded from publication.

## Publication dispositions

Every source is assigned one of five dispositions.

### `MIRROR`

Publishes the engineering meaning of a canonical source artifact without changing that meaning.

Permitted transformations include:

* Markdown-to-MDX conversion;
* publication frontmatter injection;
* internal-link rewriting;
* provenance metadata;
* presentation wrappers;
* navigation metadata.

A mirror must not:

* rewrite normative meaning;
* change lifecycle state;
* summarize away requirements;
* reinterpret decisions;
* use AI to modify canonical engineering meaning.

### `DERIVE`

Produces deterministic state from one or more authoritative inputs.

Examples include:

* current project state;
* roadmap state;
* Work Packet summaries;
* milestone state;
* release state;
* verification state;
* artifact indexes;
* evolution state.

Derived state must be reproducible from declared inputs.

### `LIVE`

Retrieves bounded operational facts whose freshness matters independently of the static publication projection.

Examples include:

* current `main` commit;
* CI state;
* latest release;
* open pull-request count;
* publication lag.

Live operational state does not override canonical engineering state.

### `EDITORIAL`

Identifies content owned by the publication repository.

Examples include:

* articles;
* essays;
* Building Monad narrative;
* editorial engineering journal content.

The Monad publication process must not overwrite editorial content.

### `EXCLUDE`

Explicitly prevents a source from automatic publication.

Excluded sources may still contribute narrowly defined derived metadata when another rule explicitly authorizes that use.

## Generated state

The canonical machine-readable website projection is expected beneath:

```text
content/generated/monad/
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

Rendered mirror pages may also exist elsewhere under `content/docs/`, `content/changelogs/`, and the explicitly reserved `content/journal/monad-source/` namespace.

Any rendered file managed by the projection must be represented in the projection manifest even when its destination is outside `content/generated/monad/`.

## Provenance

Every generated mirror must be traceable to the exact source revision.

At minimum, generated mirror metadata records:

```yaml
projection: mirror
source_repository: monad-framework/monad
source_path: <path>
source_commit: <40-character-sha>
source_blob: <blob-sha>
projection_version: 1
generated: true
```

The publication manifest additionally records the generated content hash and destination path.

## Branch policy

Only the authoritative `main` branch may become current public Monad state.

Content from feature branches, pull requests, local worktrees, speculative branches, or other non-authoritative branches must not be presented as current Monad state.

Draft or proposed artifacts that exist on `main` may be published, but their actual lifecycle status must be preserved.

Publication does not imply acceptance.

## AI boundary

AI may assist with explaining published information.

AI must not determine:

* canonical status;
* lifecycle status;
* acceptance;
* authority;
* verification success;
* release readiness;
* project completion;
* requirement satisfaction.

Those facts must come from deterministic governed inputs.

## Generated-content ownership

Projection-managed files are machine-owned.

Manual changes to a projection-managed file are not merged with regenerated output.

They must instead fail drift verification and be corrected at the authoritative source or publication-policy layer.

Editorial files remain publication-owned and must not be modified by synchronization.

## Deletion and rename semantics

Projection output is inventory-based.

Every successful publication produces a complete manifest of projection-managed output.

If a previously generated artifact is absent from the next valid manifest because the authoritative source was removed, renamed, or reclassified, the obsolete generated destination must be removed.

Deletion is limited to files previously recorded as projection-managed.

Editorial files must never be deleted by this mechanism.

## Reconciliation

Event-driven synchronization is not sufficient by itself.

The eventual implementation must also support reconciliation that independently compares:

```text
latest publishable Monad main SHA
            vs.
currently projected Monad SHA
```

A missed repository event, failed workflow, temporary authentication failure, or interrupted deployment must therefore be recoverable without manual reconstruction of state.

## Implementation order

The publication system should be implemented in this order:

```text
MONAD-PUB-001
    ↓
projection.yaml
    ↓
publication-state schemas
    ↓
source exporter
    ↓
local deterministic verification
    ↓
Fumadocs consumer
    ↓
rendering and provenance UI
    ↓
cross-repository eventing
    ↓
reconciliation
    ↓
live operational state
```

GitHub automation should not become the semantic definition of the projection.

The mapping policy belongs here.

## Required invariants

The implementation must preserve the invariants established by `MONAD-PUB-001`:

1. Single authority.
2. Exact provenance.
3. Deterministic projection.
4. No silent conflict.
5. Deletion propagation.
6. Editorial preservation.
7. Deny by default.
8. No state regression.
9. Honest freshness.
10. No AI authority.
11. `main`-only current state.
12. Local reproducibility.

## Current implementation status

This directory initially establishes publication policy only.

The exporter, publication-state schemas, Fumadocs synchronization consumer, CI automation, reconciliation mechanism, and live-state endpoint are downstream implementation work and must conform to this policy.
