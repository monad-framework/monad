# User Journeys

**Status:** Proposed stabilization baseline

## Journey J-01 — Understand before changing

1. Engineer clones or opens a repository.
2. `monad inspect` discovers repository/workspace identity and canonical artifacts.
3. Monad compiles/loads the semantic graph and reports unsupported or invalid knowledge.
4. Engineer queries the target capability/component/specification.
5. `monad explain` returns governing intent, dependencies, provenance, and relevant evidence.
6. Engineer decides whether the change is sufficiently understood to plan.

**Outcome:** the engineer reaches a trustworthy change context without manual repository archaeology.

## Journey J-02 — Plan and delegate bounded work

1. Product/engineering intent is decomposed into an authorized Work Packet.
2. Monad validates that required authority/specifications/acceptance fields are present.
3. ChatGPT assists with planning/review but does not silently expand scope.
4. `monad context <WP> --agent codex` selects the minimal graph neighborhood and canonical source needed for implementation.
5. Codex implements within the packet and returns commands/evidence.
6. Monad validates semantic integrity and required checks before PR review.

**Outcome:** AI acceleration occurs inside explicit engineering authority and traceability.

## Journey J-03 — Diagnose a semantic failure

1. Validation emits a stable diagnostic ID, severity, source, entity, rule, and remediation context.
2. Engineer requests explanation.
3. Monad shows the canonical artifacts and graph relationship causing the finding.
4. Engineer corrects source or explicitly changes the governing authority.
5. Re-validation proves resolution.

**Outcome:** failures are actionable and explainable rather than opaque tool errors.

## Journey J-04 — Review a proposed change

1. Monad compares base/head semantic state.
2. Review surfaces affected requirements/specifications/interfaces/tests and stale projections.
3. Native quality/security checks run for required scope.
4. Reviewer sees both implementation diff and engineering-knowledge impact.
5. Acceptance evidence is attached to PR/Work Packet.

**Outcome:** review evaluates changed meaning, not only changed text.

## Journey J-05 — Reproduce state

1. A second environment checks out the same revision and resolved toolchain/config.
2. Monad compiles canonical knowledge.
3. Semantic graph IDs, canonical serialization, and diagnostics match expected outputs.
4. Any permitted environmental variance is explicit and excluded from semantic identity.

**Outcome:** engineering knowledge is portable and auditable.