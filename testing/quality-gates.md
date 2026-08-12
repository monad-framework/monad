# Quality Gates

Quality gates are explicit state-transition controls. A green pipeline is
necessary but not sufficient when required human, operational, or product
evidence is missing.

## Change gate

Required for every proposed merge:

- scoped issue or work packet and reviewed change;
- formatting, lint, type, schema, policy, and architecture checks;
- unit, property, contract, and affected integration tests;
- secret, dependency, source, and license checks;
- documentation and changelog impact addressed;
- no unresolved blocking review finding.

## Integration gate

Required on the protected branch:

- clean reproducible build from the merged revision;
- immutable artifact, checksum, SBOM, and provenance;
- integration and migration tests against supported dependencies;
- primary smoke journey and negative authorization checks;
- artifact vulnerability policy satisfied.

## Increment gate

Required before accepting an increment:

- all committed requirement and packet acceptance evidence;
- integrated primary and failure journeys;
- accessibility, security, performance, and recovery evidence appropriate to
  the increment;
- risk, architecture, specifications, operations, and user docs updated;
- incomplete work explicitly removed, re-planned, or accepted as risk.

## Release gate

Required before production exposure:

- product owner accepts outcome and scope;
- engineering accepts artifact and test integrity;
- security accepts threat, vulnerability, data, and provenance state;
- operations accepts service objectives, capacity, deployment, rollback,
  telemetry, backup, restore, runbooks, and support readiness;
- change approval and communication are complete;
- no unaccepted critical or high release-blocking risk remains.

## Post-deployment gate

Verify artifact identity, configuration, migrations, primary journey, error and
latency budgets, security signals, and user impact during the observation
window. Complete the release or roll back according to the deployment plan.

## Waiver control

Waivers are exceptional and never implicit. Each states the failed gate,
evidence, consequence, exposure, compensating control, approving authority,
expiration, and corrective packet. Critical integrity loss, active credential
exposure, unknown destructive state, or uncontained severe user harm cannot be
waived for ordinary release.
