---
artifact_id: "GOV-VERSION-0001"
title: "Repository and Artifact Versioning Policy"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# Repository and Artifact Versioning Policy

## Repository Files

Every tracked file is versioned by Git. Git history is the authoritative record
of repository state.

## Governed Artifacts

Governed Markdown artifacts additionally carry an explicit semantic `version`
in YAML front matter.

Before an artifact version is changed, the current version is copied to:

`.eos/history/<artifact-path>/v<version>.md`

The change is also recorded in:

`.eos/artifact-changelog.tsv`

## Rollback

Rollback does not erase history. The requested historical content is restored
and assigned a new version derived from the current version.

## Repository Checkpoints

Use:

`./scripts/eos checkpoint "message"`

This creates a Git commit and an annotated `eos/checkpoint-*` tag.

## Releases

Project release tags and artifact versions are separate concerns. Project
release policy should be established before the first external release.
