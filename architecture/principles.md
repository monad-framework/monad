# Architecture Principles

## AP-01 — Domain rules are independent of delivery technology

Business invariants depend on domain types and explicit ports, not frameworks,
transport protocols, databases, or vendor SDKs.

## AP-02 — One owner for authoritative state

Each fact has one authoritative owner. Other components consume contracts or
maintain clearly labeled derived views rather than writing shared tables.

## AP-03 — Dependencies point toward stable policy

User interfaces and infrastructure depend on application and domain contracts.
Stable policy does not import volatile implementation details.

## AP-04 — Contracts are explicit and versioned

Requests, responses, events, errors, compatibility rules, and deprecation paths
are specified and tested at every boundary.

## AP-05 — State transitions are deliberate

Long-running or consequential workflows use explicit states, allowed
transitions, idempotency, timeout behavior, and terminal outcomes.

## AP-06 — Failure is part of the contract

Every dependency and operation defines invalid, denied, transient, permanent,
partial, and unknown outcomes with safe retry and disclosure behavior.

## AP-07 — Secure at the protected resource

Edge checks improve efficiency but do not replace authorization and invariant
enforcement where the resource or effect is owned.

## AP-08 — Observability follows user journeys

Telemetry correlates a user-visible outcome across boundaries. Component health
without journey health is insufficient.

## AP-09 — Evolution precedes distribution

Begin with modular boundaries in the smallest practical deployment. Separate
runtime units only for measured scaling, isolation, availability, technology,
or ownership needs.

## AP-10 — Build for recovery

Data, deployments, configuration, workflows, and dependencies have tested
restore, rollback, reconciliation, or compensation paths.

## AP-11 — Configuration is validated and observable

Runtime configuration is externalized, typed, fail-fast, version-aware, and
reported without exposing secrets.

## AP-12 — Exceptions expire

Any violation of an architecture principle records scope, rationale, risk,
owner, mitigation, expiration, and removal work. Repeated exceptions trigger a
principle or architecture review.
