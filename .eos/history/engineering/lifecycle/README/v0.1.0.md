---
artifact_id: "EOS-LIFECYCLE-0001"
title: "Engineering Operating System Lifecycle"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# Engineering Operating System Lifecycle

EOSB is the bootstrap layer, not the entire system.

After EOSB-020, the Engineering Operating System remains active for the lifetime
of the project through eight permanent, interlocking operating layers:

1. **EOSB — Bootstrap**
2. **EOSP — Planning**
3. **EOSE — Execution**
4. **EOSV — Verification**
5. **EOSR — Review**
6. **EOSC — Change Control**
7. **EOSL — Release Lifecycle**
8. **EOSM — Maintenance**

These layers are not a rigid waterfall. Work can move between them when evidence
requires replanning, controlled change, renewed verification, or maintenance.

## Normal Delivery Loop

`EOSP -> EOSE -> EOSV -> EOSR`

Successful review can close a WP/WC/PI or feed the next planning cycle.

## Controlled Evolution Loop

`EOSE/EOSV/EOSR -> EOSC -> EOSP/EOSE -> EOSV -> EOSR`

A discovered contradiction or required requirement/architecture/specification
change is governed rather than silently absorbed into implementation.

## Delivery / Operations Loop

`EOSR -> EOSL -> EOSM -> EOSC/EOSP as needed`
