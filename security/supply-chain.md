# Software Supply-Chain Security

## Objective

Every release should be traceable from reviewed source through controlled
dependencies and an isolated build to an immutable verified artifact. A
convenient pipeline is not trusted merely because it runs on a familiar
platform.

## Source controls

- Protect the default and release branches with required review and checks.
- Require independent approval for workflow, permission, dependency-source, and
  release-policy changes.
- Detect secrets before merge and respond as if committed secrets are exposed.
- Sign or otherwise verify release tags and preserve reviewer identity.
- Restrict force-push and deletion of protected history.

## Dependency controls

Use supported package sources, committed lockfiles, integrity verification, and
minimal direct dependencies. Review purpose, maintenance, license, transitive
risk, install scripts, network behavior, and exit cost before adding a strategic
dependency. Automated updates remain subject to tests and review.

## Build controls

Build from a clean, identified source revision in an ephemeral environment.
Separate untrusted pull-request checks from jobs holding write, signing, package,
or deployment authority. Scope tokens to the job, avoid persistent runners for
untrusted code, pin reusable workflow dependencies, and prevent artifact
substitution between build and release.

## Artifact controls

Produce an immutable artifact, checksum, software bill of materials, provenance,
test results, and vulnerability findings. Sign release artifacts when the
distribution path supports verification. Promote the same digest through
environments and verify it before deployment.

## Vulnerability management

Continuously scan direct and transitive dependencies, container or system
packages, source, and released artifacts. Triage exploitability and exposure,
not score alone. Critical exploitable findings trigger immediate containment;
other findings receive risk-based service targets, owners, and verification.

## Tool and action policy

Third-party build actions, generators, compilers, and package scripts execute
code and are dependencies. Pin immutable versions, minimize permissions, review
source and ownership, and replace abandoned or overly privileged tools.

## Release verification

A release gate verifies source revision, required approvals, protected workflow,
dependency integrity, SBOM, provenance, signatures or checksums, vulnerability
state, test evidence, and target artifact digest. Failure blocks promotion
unless handled by the explicit security risk-acceptance process.

## Response

For a compromised dependency, credential, build service, or artifact: stop
promotion, identify affected versions and consumers, revoke authority, preserve
evidence, rebuild from a trusted state, rotate exposed material, communicate
impact, and verify clean provenance before resuming releases.
