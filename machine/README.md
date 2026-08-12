# Machine-Readable Documentation

This directory is the generated semantic projection of the repository's
human-readable source files. It supports AI agents, search, retrieval-augmented
generation, validation, dependency analysis, and knowledge-graph construction
without making generated output a second source of truth.

## Canonicality

Files outside `machine/` are canonical. Files inside `machine/documents/`,
`manifest.json`, `graph.json`, and `corpus.jsonl` are deterministic derivatives.
Never edit a generated derivative directly. Edit its `source.path`, then run:

```bash
python3 scripts/sync-machine-docs.py --write
```

Verify that all generated material is current without changing files:

```bash
python3 scripts/sync-machine-docs.py --check
```

The CI workflow runs the check and fails when a companion is missing, stale, or
orphaned.

## Generated layout

- `documents/<source-path>.json` mirrors every UTF-8 source file outside the
  excluded and generated directories.
- `manifest.json` lists source hashes, companion paths, semantic metadata, and a
  deterministic source-tree hash.
- `graph.json` contains document and stable-identifier nodes plus `references`
  and `declares` edges.
- `corpus.jsonl` contains one independently ingestible record per document
  section for search, embeddings, or RAG indexing.
- `schemas/` defines the companion and manifest contracts.

## Companion semantics

Each companion includes a stable path-derived document ID, canonical source
path and SHA-256, media type, language, byte and line counts, title, summary,
document classification, normative status, full source content, parsed Markdown
sections, links, stable identifiers, resolved local-document relations, and
generator identity.

For non-Markdown text, the full file is represented as one section. No meaning
is invented by an opaque model during synchronization; extraction is local,
deterministic, reviewable, and uses only the Python standard library.

## AI editing protocol

1. Read `machine/manifest.json` to locate relevant documents and verify hashes.
2. Use companions or `corpus.jsonl` for structured retrieval and navigation.
3. Read the canonical source before proposing a meaning-changing edit.
4. Edit only the canonical source file.
5. Run `--write`, then `--check`, tests, and the applicable review process.
6. Commit source and generated changes together.

An AI tool must not treat a stale companion as authority. A companion is valid
only when `source.sha256` matches the canonical source and the sync check passes.

## Determinism and conflict handling

Outputs contain no wall-clock generation timestamp. Sorting, JSON formatting,
section anchors, hashes, and graph order are deterministic. Concurrent changes
are resolved in canonical source; derivatives are regenerated after the source
merge. This eliminates bidirectional merge policy and prevents silent conflict
resolution between human and machine representations.

## Security boundary

The synchronizer excludes common secret files, private-key formats, generated
outputs, VCS internals, dependency trees, caches, and build artifacts. Exclusion
is defense in depth, not permission to commit secrets. Companions repeat source
content and therefore inherit its classification, access controls, retention,
and review requirements.
