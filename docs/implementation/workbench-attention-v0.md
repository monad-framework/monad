---
title: "Monad Workbench Attention v0"
status: "Implementation Candidate"
classification: "Implementation Specification"
description: "Defines the read-only Monad Workbench Attention projection, Attention Center, and autonomous-workstream surface."
---

# Monad Workbench Attention v0

## 1. Objective

The Workbench Attention capability exists to answer one operator question immediately and reliably:

> **Does anything in Monad require the operator's attention right now?**

This is not a generic notification subsystem.

Attention is a derived engineering projection over trusted source systems. It identifies actionable conditions, separates them from informational activity, and preserves enough provenance to explain why the condition exists and where the underlying fact came from.

Workbench remains read-only and non-authoritative.

## 2. Authority boundary

Attention records are projections.

They SHALL NOT become lifecycle authority for:

- Program Increments;
- Work Cycles;
- Work Packets;
- Executions;
- evidence or verification;
- releases;
- reviews;
- risks;
- Git/GitHub state;
- publication state;
- AI execution state.

A condition such as `FAILED`, `BLOCKED`, or `READY_FOR_INTEGRATION` MUST originate in a source or adapter that owns or faithfully projects that fact.

The Attention layer classifies, deduplicates, explains, and presents the fact. It does not create the fact.

## 3. Trust model

The initial provider set is intentionally local-first:

1. EOS canonical lifecycle/execution projection;
2. EOS verification/evidence projection;
3. Workbench Control projection.

Future providers MAY add:

- GitHub pull-request state;
- CI/check state;
- publication synchronization;
- governed execution harness/GEH state;
- release/integration services;
- other trusted engineering signals.

Future providers MUST implement the common Attention provider contract rather than extending the core domain with provider-specific fields.

## 4. Attention domain model

Each projected condition carries:

- stable Attention identifier;
- deterministic deduplication key;
- classification;
- normalized Attention state;
- severity;
- affected object identity and type;
- human-readable title;
- reason/explanation;
- provider identity;
- source path/system;
- source-kind/provenance class;
- observed timestamp when the source exposes one;
- current/historical state;
- freshness classification;
- optional navigation-only operator action.

### 4.1 Classifications

Attention distinguishes three classes:

`activity`
: informational engineering activity that is useful context but does not itself require intervention.

`attention`
: a current condition that deserves inspection but does not necessarily require a specific human gate.

`operator-action`
: a current condition whose source semantics indicate that a human/operator action or integration decision is required.

### 4.2 Normalized states

Attention v0 recognizes the following normalized states:

- `HUMAN_ACTION_REQUIRED`
- `BLOCKED`
- `FAILED`
- `READY_FOR_INTEGRATION`
- `RUNNING`
- `COMPLETED`
- `STALE`
- `DRIFTED`
- `INFORMATIONAL`

Providers MAY observe richer provider-native states. A state SHOULD only be normalized into one of these values when the mapping is deterministic.

Provider-native states that do not imply Attention semantics SHOULD remain part of workstream presentation rather than being forced into an Attention condition.

## 5. Lifecycle derivation

EOS canonical lifecycle state remains authoritative.

When a registry status differs from `.eos/state/current.json`, Workbench SHALL:

1. display the canonical lifecycle state as current;
2. preserve the registry status as projection provenance;
3. emit a `DRIFTED` Attention condition;
4. explain which source won and why.

Workbench SHALL NOT repair or rewrite the registry merely because Attention detected the mismatch.

## 6. Evidence derivation

Evidence Attention operates on the latest current evidence for a target and validator/kind combination.

Older repeated observations SHALL NOT produce duplicate active notifications.

Rules:

- `SUPERSEDED` evidence is not current Attention input;
- the latest non-superseded evidence wins for a target/validator key;
- latest current `FAILED` evidence projects `FAILED` operator action;
- latest current `STALE` evidence projects `STALE` attention;
- latest current `DRIFTED` evidence projects `DRIFTED` attention;
- a newer passing observation removes an older failure from active Attention.

This preserves verification authority while preventing notification storms caused by repeated evidence capture.

## 7. Control derivation

Workbench Control findings may project Attention when they represent current consistency problems.

Examples include:

- canonical lifecycle versus narrative drift;
- release state explicitly marked `READY_FOR_INTEGRATION`;
- risk/change state explicitly mapped to an Attention state.

Control content that is merely present is not automatically an Attention condition.

## 8. Autonomous Workstreams

Attention v0 adds an Autonomous Workstreams surface.

The workstream representation is provider-neutral and SHALL NOT hard-code named contemporary workstreams.

The initial EOS provider derives workstreams from non-terminal Work Packets and their latest execution.

Each workstream contains:

- stable workstream ID;
- logical group/domain;
- label/title;
- affected engineering object;
- current projected state;
- reason;
- trusted source;
- update timestamp when available;
- latest execution identifier when available;
- authorization projection when it can be derived safely.

### 8.1 Initial derived workstream states

The first EOS provider uses deterministic derived states including:

`RUNNING`
: active execution or canonical Work Packet `IN_PROGRESS` state.

`RECONCILING`
: latest execution is terminal while the Work Packet remains `IN_PROGRESS`.

`PREPARING`
: Work Packet is `READY` without an active execution.

Other trusted provider-native states MAY be displayed directly.

`RECONCILING` and `PREPARING` are workstream presentation states, not new EOS lifecycle states.

## 9. Deduplication

Repeated observations of the same underlying condition SHALL collapse into one active Attention record.

Deduplication keys are deterministic and describe the semantic condition, not the observation instance.

Examples:

- lifecycle drift for a specific object;
- latest failed evidence for target + validator;
- a specific Control consistency finding.

When several observations share a deduplication key, the newest current observation wins.

Stable Attention IDs are derived from deduplication keys so browser-local presentation state remains associated across refreshes.

## 10. Local UI state

Workbench MAY persist presentation-only state in browser `localStorage`:

- read timestamp;
- dismissed timestamp;
- snooze-until timestamp;
- selected Attention Center view;
- whether locally hidden conditions are shown.

This local state SHALL NOT:

- modify canonical source files;
- mutate EOS lifecycle;
- mark verification/evidence as resolved;
- merge or close GitHub PRs;
- change release/integration status;
- grant authorization;
- execute AI work.

Dismissing or snoozing a condition means only "do not show this projected condition prominently to this browser user right now."

## 11. Shell status

The Workbench top bar includes an explicit Attention status control.

The shell status prioritizes:

1. operator action required;
2. other active attention;
3. autonomous running work;
4. clear/no-current-attention state.

The shell SHALL use meaningful text/counts in addition to an icon.

A generic bell icon alone is insufficient.

## 12. Attention Center UX

The `/attention` route provides:

- operator-action count;
- other-attention count;
- visible unread count;
- autonomous-running count;
- active condition list;
- Autonomous Workstreams surface;
- historical/informational activity view;
- source/provenance list;
- local read/dismiss/snooze controls;
- navigation to affected Workbench objects.

The UI SHALL clearly separate active conditions from historical/informational activity.

## 13. Empty-state semantics

An empty Attention Center means:

> No trusted provider currently projects a visible active condition requiring operator attention.

It does NOT mean:

- there is no engineering work;
- the repository is perfect;
- all future integrations are healthy;
- no external system has an issue that Workbench cannot currently observe.

The UI SHALL communicate this distinction.

## 14. Provider contract

An Attention provider receives an immutable projection context and returns:

- zero or more Attention observations;
- zero or more autonomous workstreams;
- zero or more source/provenance identifiers.

Providers SHALL NOT mutate repository state.

Provider-specific network/authentication code SHOULD remain outside the core Attention model.

Future provider adapters SHOULD translate trusted provider state into common Attention observations at the boundary.

## 15. GitHub / CI / publication integration

GitHub, CI, publication, and GEH states are intentionally not hard-coded into Attention v0.

Their future adapters should be able to represent conditions such as:

- PR ready for integration;
- required check failed;
- review/human gate required;
- publication blocked by environment or credential requirement;
- governed execution blocked;
- integration deferred;
- synchronization drift.

Until Workbench has a trusted adapter/query contract for those systems, the Attention core SHALL NOT infer their state from incomplete local heuristics.

## 16. Security and safety

Attention v0 SHALL remain read-only.

Navigation links are permitted.

The following are out of scope:

- EOS transitions;
- Git/GitHub writes;
- merge buttons;
- approval buttons that alter governance;
- evidence mutation;
- credential changes;
- arbitrary shell execution;
- unrestricted AI execution.

## 17. Accessibility

Attention v0 SHALL provide:

- textual state labels in addition to color;
- accessible shell Attention label;
- semantic headings/sections;
- `aria-pressed` state for view/filter controls;
- button labels that describe local-only actions;
- keyboard-accessible links and controls;
- meaningful empty states.

## 18. Validation

Workbench Attention v0 SHALL pass the normal Workbench gate:

```bash
bun run check
```

Regression coverage SHALL include at minimum:

1. canonical lifecycle drift detection;
2. workstream reconciliation derivation;
3. repeated evidence deduplication;
4. newer passing evidence clearing older failure attention;
5. blocked execution classification;
6. Control consistency-finding projection.

## 19. Integration discipline

Attention implementation changes SHOULD remain inside:

- `apps/workbench`;
- Workbench-owned tests;
- this Attention implementation specification;
- directly relevant Workbench documentation.

The authored Attention branch SHALL NOT regenerate shared EOS, trace, or `machine/*` projections solely to complete feature authoring.

The branch completion state is:

`READY_FOR_INTEGRATION`

At that point the authored source, tests, docs, and UI are complete, but integration/merge coordination remains separate from feature authoring.

## 20. Completion criteria

Attention v0 is complete when Workbench can answer, from trusted current projections:

1. whether any active condition requires operator action;
2. whether any current condition deserves attention;
3. which object is affected;
4. why the condition exists;
5. where the fact came from;
6. when the fact was observed where available;
7. whether the condition is current or historical;
8. what navigation-only next action is available;
9. which autonomous workstreams are currently observable;
10. whether repeated observations have been deduplicated;
11. whether local read/dismiss/snooze state remains non-authoritative.
