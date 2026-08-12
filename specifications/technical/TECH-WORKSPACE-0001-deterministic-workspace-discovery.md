# TECH-WORKSPACE-0001: Deterministic Workspace Discovery

**Status:** approved  
**Version:** 1.0.0  
**Owner:** Monad Core  
**Related requirements:** FR-001, QR-001, QR-003  
**Governing ADRs:** ADR-0002, ADR-0004

## Purpose and scope

Defines discovery of canonical candidate files from the effective MVP configuration. It covers configured artifact roots, exclusions, ordering, containment, and discovery diagnostics; it does not parse artifact semantics.

## Preconditions

A valid Monad root and effective configuration satisfying IFC-WORKSPACE-0001 exist.

## Normative behavior

1. Discovery MUST enumerate only paths selected by configured artifact include patterns after configured exclusions.
2. `.git/`, `machine/`, `.eos/`, build outputs such as `target/`, and other configured exclusions MUST NOT become canonical source candidates by default.
3. Enumeration MUST NOT execute repository code, package-manager commands, plugins, or network requests.
4. A candidate path MUST be canonicalized lexically to a repository-relative `/`-separated path before ordering/identity processing.
5. Paths containing parent traversal or resolving outside root MUST be rejected.
6. Symlink candidates MUST be checked for root containment; external targets and cycles produce diagnostics and are not ingested.
7. Duplicate discovery of the same canonical repository path through overlapping patterns MUST yield one candidate with merged discovery provenance, not duplicate semantic sources.
8. Final candidate ordering MUST be ascending by canonical repository-relative path encoded as UTF-8 bytes, with source-kind tie-breaker where required.
9. Unsupported file/source kinds matched by a broad include MUST produce a deterministic unsupported-source diagnostic unless the configuration explicitly classifies them as ignored.
10. Discovery output MUST identify canonical path, matched artifact class/root, source-kind candidate, and enough pattern provenance to explain why the file was selected.

## Failure and recovery

Unreadable files, invalid symlinks, invalid UTF-8 path representations on a supported platform, and root-escape attempts are diagnostics. One invalid candidate MUST NOT reorder valid candidates. Fatal configuration/root errors prevent discovery entirely.

## Verification

Golden fixtures cover overlapping patterns, stable order under randomized filesystem enumeration, exclusions, nested directories, external/cyclic symlinks, duplicate matches, unsupported source kinds, and equivalent clean clones.
