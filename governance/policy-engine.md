---
artifact_id: "GOV-POLICY-0001"
title: "EOS Policy-as-Code and Gate Model"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-09-05"
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

## AI-Driven Policy Obligations

AI-driven engineering uses the existing EOS policy and gate model.

It does not create a separate probabilistic policy engine.

Policy and gate evaluation MAY govern:

- autonomy profile;
- capability availability;
- delegation;
- approval requirements;
- review independence;
- execution eligibility;
- sensitive-resource access;
- governing-input freshness;
- resource limits;
- escalation requirements.

For protected actions, missing, stale, contradictory, expired, revoked,
unresolvable, or denied authority MUST NOT be interpreted as permission.

A model recommendation MUST NOT override a deterministic gate result merely
because the model believes the action is safe or appropriate.

Where an AI proposes a lifecycle transition, approval, capability grant, or
effect, the applicable EOS policy is evaluated by the authoritative control
plane before the requested governed mutation occurs.

Future machine-enforced autonomy and authority predicates MUST extend the
existing constrained policy vocabulary or another separately approved
deterministic governance mechanism rather than creating hidden executor-owned
policy.
