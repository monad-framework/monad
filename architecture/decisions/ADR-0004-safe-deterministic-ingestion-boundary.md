# ADR-0004: Safe Deterministic Canonical Ingestion Boundary

**Status:** Accepted  
**Date:** 2026-08-12  
**Decision scope:** MVP repository inspection and canonical artifact ingestion  
**Related:** FR-002, FR-009, QR-001, QR-003, QR-004

## Context

Monad consumes repositories that may contain arbitrary code, scripts, links, generated files, malformed text, symlinks, and potentially hostile content. Its semantic kernel must be trustworthy before any optional native-tool execution or agent execution occurs. Implicitly executing repository code or fetching remote references during discovery would make semantic state unsafe and non-reproducible.

## Decision

1. MVP canonical ingestion is a read-only local compilation phase. It MUST NOT execute repository scripts, build hooks, package managers, plugins, macros, shell substitutions, or arbitrary code.
2. Canonical ingestion performs no network access. Remote URLs may be recorded as unresolved/external references but are not dereferenced to establish semantic truth.
3. Files are eligible only through explicitly configured artifact roots and supported source kinds. Generated projections such as `machine/`, caches, VCS internals, and EOS machine/control state are excluded from canonical semantic input by default unless a later specification explicitly models them as evidence/projection sources.
4. Symlinks are resolved for containment. A candidate resolving outside the selected Monad root is rejected for canonical ingestion. Symlink cycles and ambiguous aliases produce diagnostics.
5. MVP text sources are UTF-8. Invalid encoding is a diagnostic; replacement-character decoding is not silently accepted as canonical content.
6. Parsing is deterministic and side-effect free. Parser output depends only on source bytes, declared schema/parser version, canonical configuration, and stable implementation version.
7. Malformed or unsupported input remains explicit. Parsers may recover enough structure to produce diagnostics, but recovered data MUST NOT be promoted to valid semantic state without a rule allowing it.
8. Markdown links/references and structured identifiers are extracted as candidates first; semantic resolution is a separate phase governed by specification.
9. Native tool execution, when later authorized, is a downstream execution/verification concern and must preserve the native result and invocation evidence; it is not part of ingestion.

## Consequences

- repository inspection is safe enough to run before trust is established;
- semantic compilation remains reproducible offline;
- remote or executable semantics require explicit later capabilities;
- some ecosystems whose metadata is discoverable only by running tools need adapters after MVP rather than implicit execution.

## Verification

Fixtures must include executable files, package hooks, command-looking text, external and cyclic symlinks, invalid UTF-8, network URLs, generated directories, malformed documents, and repeat-run equivalence. Tests must prove no repository command or network request is required for canonical ingestion.
