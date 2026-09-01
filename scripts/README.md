# Repository Scripts

This directory contains maintained automation for repeatable project actions
such as bootstrap, validation, generation, migration, release evidence, and
operational checks. Scripts are productized interfaces for contributors and
automation—not undocumented personal shortcuts.

## Script requirements

- Use a portable interpreter or declare and verify the required runtime.
- Enable strict error handling appropriate to the language.
- Provide `--help`, documented inputs, meaningful exit codes, and actionable
  errors for user-facing scripts.
- Quote paths and inputs; avoid unsafe word splitting, globbing, and command
  construction.
- Validate targets before mutation and reject broad or ambiguous destructive
  paths.
- Prefer dry-run, preview, confirmation, backup, or transactional behavior for
  consequential actions.
- Never print secrets or accept them as ordinary command-line arguments when a
  safer channel exists.
- Produce deterministic output where practical and identify generated files.
- Include automated tests for parsing, failure, rerun, and boundary behavior.

## Naming

Use action-oriented lowercase names such as `check-docs`, `verify-release`, or
`migrate-schema`. Platform-specific extensions are allowed. Avoid names that
hide consequence, such as `cleanup`, when the script deletes or rewrites data.

## Ownership and review

Every script has a clear owner through CODEOWNERS or its related capability.
Changes to build, release, credentials, production access, migration, or
destructive operations require elevated review. Pin and review external tools
downloaded or executed by scripts.

## Human/machine document synchronization

`sync-machine-docs.py` treats UTF-8 files outside `machine/` as canonical and
generates deterministic semantic companions, a manifest, a knowledge graph, and
a section corpus. After changing a canonical file, run:

```bash
python3 scripts/sync-machine-docs.py --write
python3 scripts/sync-machine-docs.py --check
```

Commit canonical and generated changes together. The check mode performs no
writes and is enforced by `.github/workflows/document-sync.yml`. Generated
companions are never the direct edit target.

## Website publication projection

`validate-publication.py` validates the publication policy, publication JSON
Schemas, and positive/negative contract fixtures:

```bash
python3 scripts/validate-publication.py
```

`export-site-state.py` compiles an exact committed Monad `main` revision into a
deterministic staging tree for the website publication projection. It reads
source content from Git rather than from the mutable working tree, performs no
network I/O, derives `generatedAt` from the source commit timestamp, validates
generated JSON against the publication schemas, and records exact manifest and
provenance information.

From a synchronized repository:

```bash
python3 scripts/export-site-state.py \
  --ref main \
  --output .tmp/publication-export \
  --clean \
  --verify-determinism
```

The staging tree uses paths relative to the destination Fumadocs repository.
Nothing under `.tmp/` is committed. Cross-repository synchronization is a
separate downstream concern and must not become the semantic definition of the
projection.

Run the exporter regression tests with:

```bash
python3 tests/publication/test-export-site-state.py
```

The test exports the same committed `main` revision twice and requires the
complete generated trees to be byte-identical.

## Generated artifacts

Document source, destination, reproducibility, overwrite behavior, and whether
generated output is committed. CI should detect drift when committed generated
files must match their source.
