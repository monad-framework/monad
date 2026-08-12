# WP-STAB-0003 — Materialize the Artifact-System Corpus

**Status:** Review  
**Owner:** Engineering Owner  
**Program:** STAB-0001

## Objective

Eliminate empty Markdown placeholders from `artifact-system/` by creating substantive, explicitly non-authoritative Draft baselines for every artifact path while preserving already-authored content.

## Scope

### In scope

- deterministic materialization of empty `artifact-system/**/*.md` files;
- purpose, scope, principles, inputs, traceability, lifecycle, verification, acceptance, and category/filename-specific engineering rules;
- criticality/approval policy explaining taxonomy versus authority;
- repeatable `--check` validation.

### Out of scope

- bulk approving generated Drafts;
- overwriting authored non-empty content by default;
- treating the generator as the permanent source of artifact meaning;
- implementing the capabilities described by the artifact taxonomy.

## Acceptance criteria

- [ ] Zero artifact-system Markdown files remain empty after materialization.
- [ ] Every generated document declares Draft/proposed authority status.
- [ ] Existing authored non-empty files are unchanged unless explicitly forced.
- [ ] Generated content is category-aware and contains concrete verification/acceptance structure rather than a title-only stub.
- [ ] `python3 scripts/populate-artifact-system.py --check` passes.
- [ ] `artifact-system/README.md` explains criticality, approval, canonicality, and backlog relationship.
- [ ] Machine projection is regenerated after materialization.

## Validation

Run materializer in a clean checkout, rerun to prove idempotency, run `--check`, and inspect representative artifacts across KIR, AI/agent, security, execution, product, commercial, and future categories.

## Risks

Large generated Draft volume may be mistaken for design maturity. Mitigation is explicit status/authority metadata plus criticality-driven selective review.

## Completion evidence

Materializer source, generated artifact corpus, representative review samples, and successful artifact/machine synchronization workflow.
