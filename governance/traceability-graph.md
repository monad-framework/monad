---
artifact_id: "GOV-TRACE-GRAPH-0001"
title: "EOS Semantic Traceability Graph"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

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
