# Documentation

This directory contains publishable guidance for users, integrators, operators,
and maintainers. Governance, product, architecture, and engineering records
elsewhere in the repository are sources for decisions; documentation here
explains how to understand and use the resulting product.

## Information architecture

- `getting-started/` — prerequisites, installation, first successful outcome,
  and safe removal.
- `concepts/` — mental models, terminology, states, guarantees, and limitations.
- `guides/` — outcome-oriented procedures for supported tasks and recovery.
- `reference/` — precise commands, configuration, interfaces, errors, limits,
  and compatibility.
- `internals/` — maintainer explanations of implementation and extension points.

## Documentation standard

Every page identifies its audience, prerequisite knowledge, supported version,
and intended outcome. Procedures begin with prerequisites and safety effects,
use tested steps, show expected results, include recovery, and link reference
detail rather than duplicating it. Concept pages explain why; guides explain
how; reference states exact behavior.

## Style

Use direct language, active voice, descriptive headings, and consistent terms
from `governance/terminology.md`. Prefer concrete examples with synthetic data.
Do not imply guarantees the specifications do not provide. Label destructive,
irreversible, privileged, costly, or security-sensitive actions before the
step that performs them.

## Versioning

Documentation changes with the behavior it describes. Version-specific
differences and migration paths are explicit. Deprecation guidance states the
replacement, first deprecated version, removal target, and user action.

## Verification

Commands, code samples, links, interface examples, and primary procedures are
checked in the delivery pipeline where feasible. Manual reviews test the page
from a clean user perspective. A documentation defect that prevents safe or
successful use is prioritized like the corresponding product defect.

## Publishing

Published output must preserve accessible heading order, meaningful link text,
code language labels, alternative text, keyboard navigation, and readable
contrast. Generated sites or files are build artifacts and are not edited as
the source of truth.
