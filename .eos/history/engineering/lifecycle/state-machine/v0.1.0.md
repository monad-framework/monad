---
artifact_id: "EOS-STATE-0001"
title: "EOS Lifecycle State Machine"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# EOS Lifecycle State Machine

## Program Increment

`DRAFT -> PLANNED -> AUTHORIZED -> ACTIVE -> IN_REVIEW -> CLOSED`

Exceptional state: `BLOCKED`.

## Work Cycle

`DRAFT -> READY -> AUTHORIZED -> ACTIVE -> IN_REVIEW -> CLOSED`

Exceptional state: `BLOCKED`.

## Work Packet

`DRAFT -> READY -> AUTHORIZED -> IN_PROGRESS -> VERIFYING -> IN_REVIEW -> CLOSED`

Exceptional state: `BLOCKED`.

## Change Request

`DRAFT -> PROPOSED -> APPROVED -> APPLIED -> CLOSED`

Alternative terminal state: `REJECTED`.

## Maintenance Item

`OPEN -> PLANNED -> IN_PROGRESS -> VERIFYING -> CLOSED`

Alternative state: `DEFERRED`.

## Release

`PROPOSED -> READY -> RELEASED`

Alternative terminal state: `WITHDRAWN`.

## Gate Principle

Transitions implying authorization, acceptance, closure, release, or risk
acceptance leave durable evidence and a decision record.
