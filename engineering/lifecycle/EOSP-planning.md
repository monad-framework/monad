---
artifact_id: "EOSP"
title: "EOSP Planning"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# EOSP — Planning

## Purpose

Convert accepted product, architecture, and specification intent into bounded,
traceable execution units.

## Managed Objects

- milestones;
- program increments;
- work cycles;
- work packets;
- dependencies;
- risks;
- sequencing;
- readiness gates.

## Primary Commands

```bash
./scripts/eos plan PI-002
./scripts/eos create-wc --pi PI-002
./scripts/eos create-wp --wc WC-0002 --domain CORE
./scripts/eos authorize PI-002
./scripts/eos authorize WC-0002
./scripts/eos authorize WP-CORE-0001
```
