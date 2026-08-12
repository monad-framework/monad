---
artifact_id: "GOV-POLICY-0001"
title: "EOS Policy-as-Code and Gate Model"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

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
