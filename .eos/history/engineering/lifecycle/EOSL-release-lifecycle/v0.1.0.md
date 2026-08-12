---
artifact_id: "EOSL"
title: "EOSL Release Lifecycle"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# EOSL — Release Lifecycle

## Purpose

Turn accepted engineering output into a reproducible, reviewable, traceable
release.

## Flow

`candidate -> readiness evidence -> readiness review -> version -> commit ->
annotated tag -> optional GitHub Release -> post-release evidence`

## Primary Command

```bash
./scripts/eos release 0.1.0
```

The first invocation prepares release/readiness artifacts when necessary. Final
tagging remains gated on readiness approval unless a human records an explicit
override. `--publish` performs the external GitHub publication step.
