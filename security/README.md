# Security

Security protects users, data, service integrity, and the project's ability to
operate. Controls are selected from explicit threats and obligations, then
verified as product behavior and operational evidence.

## Security documents

- `security-model.md` defines objectives, identities, data, and control
  expectations.
- `threat-model.md` identifies assets, boundaries, abuse cases, mitigations, and
  residual risk.
- `supply-chain.md` protects source, dependencies, build, artifacts, and release.
- Root `SECURITY.md` defines coordinated vulnerability reporting.

## Secure-delivery requirements

1. Model threats before exposing a new trust boundary or sensitive data flow.
2. Authenticate identities and authorize at the resource or effect owner.
3. Validate all untrusted input and encode output for its destination.
4. Keep secrets outside source, images, logs, tests, and ordinary configuration.
5. Protect data in transit and at rest according to classification.
6. Generate evidence for privileged, security-relevant, and consequential
   actions without recording prohibited payloads.
7. Scan source, dependencies, artifacts, infrastructure, and secret exposure in
   the protected delivery path.
8. Test denial, isolation, rate protection, recovery, and security monitoring.

## Release policy

Known exploitable critical findings block release. High findings block unless
the Security Owner and affected accountable owner accept a time-bounded risk
with exposure, compensating controls, monitoring, expiration, and remediation
work. Medium and low findings follow risk-based service targets.

## Security ownership

Every component owner owns secure implementation and response for that
component. The Security Owner sets policy, reviews elevated risk, coordinates
vulnerabilities, and may stop exposure when a credible critical condition is
uncontained. Security review does not transfer responsibility away from product,
engineering, or operations.
