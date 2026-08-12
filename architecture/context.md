# System Context

**Status:** Proposed foundation baseline

## System of interest

Monad is the local-first Engineering Knowledge Compilation Platform. It observes canonical engineering artifacts and repository state, compiles them into a semantic model, exposes understanding and impact through deterministic interfaces, generates bounded AI-agent context, and executes explicit native-tool plans under human-controlled authority.

## Human actors

| Actor | Uses Monad to | Authority boundary |
| --- | --- | --- |
| Software Engineer / Maintainer | Inspect, query, change, validate, plan, and run engineering work | May act within repository/work authorization; material decisions remain governed |
| Product Owner / Project Steward | Define outcomes, order work, accept product scope and releases | Owns product acceptance and strategic direction |
| Architecture Owner | Define and review boundaries, contracts, semantic models, and strategic technical decisions | Accepts architecture/ADR decisions within delegated authority |
| Engineering Owner | Plan delivery, review implementation evidence, maintain integration quality | Authorizes engineering execution within approved product/architecture scope |
| Security / Operations Owner | Review trust, dependency, release, and operational risk | Owns delegated security/operability readiness decisions |
| Contributor / Plugin Author | Extend or integrate Monad through public contracts | No implicit authority over core semantics or release decisions |

One person may hold several roles in the current project, but the role distinction remains explicit so authority can scale without rewriting semantics.

## Machine actors

### Codex

Codex is an implementation agent. Monad should be able to provide it a bounded task/work-packet context containing objective, governing artifacts, authorized scope, dependencies, acceptance criteria, validation commands, prohibited changes, and provenance.

Codex is not an independent architecture or release authority.

### ChatGPT

ChatGPT is used for architecture, product/specification authoring, decomposition, backlog refinement, review preparation, governance, and cross-artifact reasoning. Finalized authoritative changes are persisted through Git/GitHub and the repository lifecycle; conversation text alone is not canonical project authority.

### CI automation

GitHub Actions and future CI systems reproduce validation, machine projection, tests, release gates, provenance, and publishing in a controlled environment. Automation enforces declared rules but does not own the rule or approval decision.

## External systems and resources

### Git and the filesystem

Primary local source/history boundary. Monad reads working-tree/index/commit state, canonical files, configuration, and repository topology. Repository content is untrusted input.

### Native ecosystem tools

Compilers, formatters, linters, test runners, package managers, infrastructure tools, containers, and documentation generators remain responsible for their mechanics. Monad discovers supported tools and invokes them through explicit adapters/plans.

### GitHub

Durable collaboration and projection system for repository source, issues, pull requests, project views, CI, releases, wiki, and community workflows. GitHub state may be modeled by Monad, but canonical engineering authority remains defined by repository governance.

### Optional AI providers

External model providers may assist explanation, drafting, navigation, or implementation. Context sent outside the local trust boundary is minimized, classified, explicitly authorized, and attributable. The deterministic kernel cannot require one provider.

### Future Monad registry and hosted services

May distribute schemas, plugins, adapters, policies, templates, metadata, remote cache/execution, or collaborative indexes. They are outside Release 1's required success path.

## Trust boundaries

1. **Repository input → Monad parser/adapter boundary.** Files, links, paths, symlinks, configuration, code snippets, and generated text are untrusted input.
2. **Knowledge Plane → Control Plane.** Semantic reachability or a declared command does not itself create execution authority.
3. **Control Plane → Execution Plane.** Only supported, explicit, inspectable plans may cause local side effects.
4. **Local process → native external tools.** Environment, working directory, inputs, outputs, exit status, timeouts, and tool identity are captured.
5. **Local repository → external AI/provider.** Only task-authorized minimal context crosses this boundary.
6. **Developer workstation → GitHub/remote collaboration.** Repository and evidence publication follow Git/GitHub credentials and project governance.
7. **Ordinary project data → secrets/sensitive data.** Sensitive material is excluded from generated context, diagnostics, and telemetry unless specifically required and authorized.

## Primary MVP flow

1. User invokes Monad in a repository.
2. Workspace discovery identifies root, configuration, artifact sources, components, toolchains, and Git state.
3. Adapters parse supported artifacts without causing side effects.
4. Identity/provenance normalization produces stable semantic inputs.
5. Monad constructs and validates the semantic graph and KIR.
6. User inspects, queries, explains, or supplies a bounded change/task.
7. Change-impact/context logic traverses relevant semantic relationships under policy/authority constraints.
8. Planner emits an explicit execution plan.
9. User or authorized automation inspects/approves execution as required.
10. Execution adapters invoke native tools and capture structured evidence.
11. Diagnostics/results are returned to the user and may update canonical project knowledge through normal review/change control.

## Data handling

Release 1 should not need a central project-content database. Canonical state remains in the repository; local indexes/caches are disposable derived state. Persistent machine representations are versioned projections when committed or deliberately exported.

Source content is not transmitted externally by default. Optional provider integration identifies purpose, selected context, data classification, and retention implications before transmission.

## Dependency policy

Every material external dependency or tool adapter must have a purpose, supported version/compatibility range, owner, failure behavior, security/supply-chain assessment proportional to risk, and exit/migration strategy where lock-in would affect the product. Vendor guarantees are never treated as an end-to-end Monad guarantee.
