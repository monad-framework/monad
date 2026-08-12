# Contributing to MonadV2

Contributions are welcome when they preserve the repository's traceability,
quality, and safety guarantees. This guide defines the common path from an idea
to an accepted change.

## Before starting

1. Search issues, work packets, ADRs, and pull requests for related work.
2. Open an issue when the behavior, scope, or ownership is unclear.
3. Obtain an accepted work packet for changes that cross boundaries, alter a
   public contract, or require more than one focused pull request.
4. Read the relevant requirements, architecture decisions, and quality gates.
5. Never include credentials, production data, private keys, or personal data.

## Change workflow

1. Fork or branch from the current default branch.
2. Use a short branch name such as `feat/short-description` or
   `fix/issue-number-description`.
3. Make the smallest coherent change that satisfies the acceptance criteria.
4. Add or update tests and documentation in the same change.
5. Run all applicable local checks and review the diff for secrets and noise.
6. Open a pull request using the repository template.
7. Address review findings with new commits; avoid rewriting reviewed history
   unless a maintainer requests it.

## Commit standard

Use Conventional Commit subjects:

```text
<type>(optional-scope): concise imperative summary
```

Preferred types are `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`,
`ci`, `chore`, and `revert`. Explain the reason and consequences in the body.
Mark compatibility breaks with `!` and a `BREAKING CHANGE:` footer.

## Quality expectations

- Requirements and acceptance criteria are explicit and testable.
- New behavior includes positive, negative, and boundary tests.
- Public interfaces remain compatible or include an approved migration plan.
- Errors are actionable and do not reveal secrets or sensitive internals.
- Telemetry supports diagnosis without collecting unnecessary data.
- Documentation is accurate for users, operators, and maintainers.
- Generated or vendored changes are isolated and reproducible.

## Architecture and governance

Create an ADR before merging a decision that is costly to reverse, changes a
system boundary, introduces a strategic dependency, or modifies a quality
attribute. Use the change-control process for baselined documents. Reviewers
may return technically correct changes that lack required traceability.

## Review conduct

Review the work, not the person. Distinguish blocking correctness or safety
findings from optional suggestions. Authors should resolve every conversation
or state why no change is needed. Approval means the reviewer believes the
change is safe to merge within the evidence available.

## Reporting security issues

Do not open public issues for suspected vulnerabilities. Follow
[`SECURITY.md`](SECURITY.md) and report privately to thomasjcarter613@gmail.com.
