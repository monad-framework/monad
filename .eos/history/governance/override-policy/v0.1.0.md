---
artifact_id: "GOV-OVERRIDE-0001"
title: "EOS Human Override Policy"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

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
