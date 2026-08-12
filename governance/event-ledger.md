---
artifact_id: "GOV-EVENTS-0001"
title: "EOS Event Ledger Policy"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

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
