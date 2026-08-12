# Architecture Diagrams

This directory contains version-controlled diagrams that explain views not
communicated efficiently by prose. Diagrams complement decisions and
specifications; they do not replace responsibilities, contracts, or measurable
behavior.

## Required views

- system context: people, external systems, trust boundaries, and data flows;
- container or deployable view: runtime responsibilities and communication;
- component view: internal boundaries for the primary deployable;
- primary sequence: intent through verification;
- recovery sequence: interruption, retry, compensation, and reconciliation;
- deployment view: environments, ingress, state, secrets, and telemetry;
- threat or data-flow view when security analysis requires it.

## Source standard

Prefer Mermaid stored directly in Markdown when it communicates the view
clearly. Store editable source beside any exported image. Do not commit an image
without its source, owner, and last-reviewed date. Use short identifiers that
match architecture and terminology documents.

## Diagram header

Every diagram document states:

- purpose and intended audience;
- scope and level of abstraction;
- authoritative sources and related ADRs;
- assumptions and omitted concerns;
- owner, status, and last review date.

## Review checklist

Confirm that responsibilities have one owner, arrows have direction and
meaning, trust and data boundaries are visible, sync versus async interaction
is unambiguous, failure paths are represented where material, and names match
the current architecture. Remove obsolete diagrams rather than preserving
misleading history outside version control.
