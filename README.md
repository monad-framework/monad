# MonadV2

MonadV2 is organized as a documentation-first project: the problem,
product intent, architecture, specifications, delivery plan, controls, and
operating practices are versioned beside the implementation they govern. This
repository begins with an executable system of record rather than a loose set
of notes.

## Current state

The project is in **inception**. The initial objective is to validate the
problem and freeze enough of the product and architecture baseline to begin the
first implementation increment without hiding unresolved risk.

| Area | Source of truth | Initial decision gate |
| --- | --- | --- |
| Why the project exists | `vision/` | Vision review |
| What must be delivered | `product/` and `specifications/` | Product baseline |
| How the system is shaped | `architecture/` | Architecture review |
| How work is controlled | `engineering/` | Increment authorization |
| How change is governed | `governance/` | Change approval |
| How quality and safety are proven | `testing/` and `security/` | Release readiness |
| How the service is run | `operations/` | Operational readiness |

## Start here

1. Read [`idea.md`](idea.md) for the original hypothesis and validation plan.
2. Confirm the problem in [`vision/problem-statement.md`](vision/problem-statement.md).
3. Review the product baseline in [`product/product-requirements.md`](product/product-requirements.md).
4. Review the system shape in [`architecture/overview.md`](architecture/overview.md).
5. Select authorized work from [`engineering/work-packets/active.md`](engineering/work-packets/active.md).
6. Use [`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing a change.

## Repository map

- `vision/` — enduring intent, principles, goals, exclusions, and outcomes.
- `product/` — users, journeys, capabilities, requirements, and roadmap.
- `architecture/` — system context, boundaries, quality attributes, and ADRs.
- `specifications/` — testable functional and technical contracts.
- `engineering/` — milestones, increments, work cycles, packets, reviews, and risks.
- `research/` — questions, evidence, experiments, and references.
- `governance/` — authority, decisions, change control, lifecycle, and language.
- `operations/` — environments, delivery, telemetry, reliability, and incidents.
- `security/` — security objectives, threats, controls, and supply-chain policy.
- `testing/` — verification strategy, acceptance, performance, and quality gates.
- `docs/` — user and maintainer documentation intended for publication.
- `journal/` — chronological project narrative and rationale.
- `machine/` — generated JSON companions, manifest, graph, and section corpus
  for AI agents, search, validation, and automation.

## Working agreements

- Every material claim links to evidence or is labeled as an assumption.
- Every requirement has a stable identifier and verifiable acceptance criteria.
- Every irreversible or cross-cutting architecture choice receives an ADR.
- Work begins only when the Definition of Ready is met and closes only when the
  Definition of Done is satisfied.
- Security, operability, accessibility, and documentation are product work,
  not post-release cleanup.
- Decisions are changed by superseding records, never by silently rewriting
  history.
- Human-readable source files are canonical. Generated machine companions must
  pass `python3 scripts/sync-machine-docs.py --check` before merge.

## Contribution and support

Use issues for observable problems and bounded proposals. Use pull requests for
reviewable changes. Security reports must follow [`SECURITY.md`](SECURITY.md)
and must not be filed publicly. Project conduct is governed by
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## License

Copyright © 2026 Thomas Carter. Released under the MIT License; see
[`LICENSE`](LICENSE).

## Permanent EOS Operating Layers

EOSB is only project bootstrap. The Engineering Operating System remains active
throughout the project lifecycle:

- **EOSB — Bootstrap**
- **EOSP — Planning**
- **EOSE — Execution**
- **EOSV — Verification**
- **EOSR — Review**
- **EOSC — Change Control**
- **EOSL — Release Lifecycle**
- **EOSM — Maintenance**

Common permanent-lifecycle commands:

```bash
./scripts/eos plan PI-002
./scripts/eos create-wc --pi PI-002
./scripts/eos create-wp --wc WC-0002 --domain CORE
./scripts/eos authorize WP-CORE-0001
./scripts/eos start WP-CORE-0001
./scripts/eos codex WP-CORE-0001
./scripts/eos validate WP-CORE-0001
./scripts/eos review WP-CORE-0001
./scripts/eos close WP-CORE-0001
./scripts/eos close-cycle WC-0002
./scripts/eos close-pi PI-002
./scripts/eos trace REQ-0042
./scripts/eos impact ADR-0014
./scripts/eos github-sync
./scripts/eos release 0.1.0
```
