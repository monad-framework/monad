# Success Criteria

**Status:** Proposed foundation baseline

The criteria below define evidence required to claim that Monad's foundation and MVP Release 1 are working. Activity, document count, issue closure, and generated code are not success measures by themselves.

## SC-01 — Deterministic semantic compilation

For a fixed supported repository state, Monad version, configuration, and declared toolchain, repeated compilation produces semantically equivalent graph and KIR output with stable identities and canonical ordering.

**MVP evidence:** deterministic fixture suite and repeated clean-machine runs produce identical canonical hashes.

## SC-02 — Explainable engineering graph

Representative graph nodes and edges expose provenance sufficient to answer why they exist and which canonical artifact or extraction rule produced them.

**MVP evidence:** sampled entities and relationships can be traced back to source locations and governing identifiers without manual inference.

## SC-03 — Useful change-impact analysis

For a representative change corpus, the affected-set engine identifies required dependent artifacts and validation conservatively and explains the path that caused inclusion.

**MVP evidence:** no known required validation is omitted in the acceptance corpus; over-inclusion is measured and bounded rather than hidden.

## SC-04 — Bounded AI-agent context

Monad can generate a task-specific context package containing governing artifacts, dependencies, constraints, acceptance criteria, and provenance without indiscriminately including the repository.

**MVP evidence:** controlled Codex tasks can be completed using generated context packages, and packages are independently reviewable and reproducible.

## SC-05 — Native execution orchestration

Monad derives an explicit execution plan and invokes real native tools rather than replacing their mechanics.

**MVP evidence:** at least one representative polyglot repository scenario executes a dependency-ordered validation plan with captured commands, inputs, outputs, exit status, and evidence.

## SC-06 — Actionable diagnostics

Invalid configuration, unresolved semantic references, graph invariant violations, unsupported states, and native-tool failures produce structured diagnostics with stable identity, severity, provenance, and remediation guidance.

**MVP evidence:** negative and boundary acceptance suites verify machine-readable and human-readable diagnostics.

## SC-07 — Human/machine synchronization

Generated companions, manifest, graph, and corpus cannot silently diverge from canonical human-readable source.

**MVP evidence:** CI fails on stale, missing, or orphaned generated outputs and passes after deterministic regeneration.

## SC-08 — Local-first operation

Core inspection, compilation, validation, query, context generation, plan generation, and local execution do not require a Monad-hosted service.

**MVP evidence:** release acceptance runs in an environment with Monad cloud access unavailable.

## SC-09 — CI reproducibility

The same declared validation used locally can be reproduced in GitHub Actions, with meaningful differences in environment captured rather than hidden.

**MVP evidence:** release-candidate validation passes from a clean checkout and records tool versions, inputs, and produced evidence.

## SC-10 — Coherent CLI experience

A new technical user can discover and use the MVP commands without private maintainer knowledge.

**MVP evidence:** documented scenarios successfully exercise `inspect`, `validate`, `graph`, `query`, `explain`, `affected`, `context`, `plan`, `run`, `doctor`, and `version` or an explicitly approved smaller Release 1 subset.

## Release guardrails

Release 1 is not accepted when any of the following is true:

- a known graph or KIR nondeterminism remains unexplained;
- a supported change scenario can omit required validation without a blocking uncertainty diagnostic;
- generated machine state can drift silently from canonical source;
- secrets or unnecessary sensitive data are included in agent context or diagnostics;
- execution can perform undeclared consequential commands outside the approved plan;
- release artifacts cannot be traced to source, toolchain, tests, and acceptance evidence;
- critical or high security/reliability risks remain neither mitigated nor explicitly accepted by the accountable authority.

## Post-MVP success

After Release 1, product success must be evaluated against real engineering outcomes: reduced context-reconstruction time, faster safe change review, lower unnecessary validation cost without missed impact, improved agent-task success and reviewability, lower architecture/documentation drift, and repeat use by developers who can choose alternatives.
