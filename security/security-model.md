# Security Model

## Objectives

- Only authenticated and authorized actors perform protected actions.
- Domain and workflow integrity is preserved across retries, failures, and
  administrative intervention.
- Sensitive data is collected and exposed only for declared purposes.
- Service and data remain available within approved resilience objectives.
- Security-relevant actions are attributable and reviewable.
- Compromise of one actor, component, tenant, dependency, or environment is
  contained to the smallest practical scope.

## Identity classes

| Identity | Purpose | Key controls |
| --- | --- | --- |
| End user | Perform supported product actions | Strong session handling, resource authorization, rate protection |
| Administrator | Manage bounded product configuration | Separate role, stronger authentication, audited purpose |
| Operator | Deploy, diagnose, and restore | Just-in-time privilege, environment scoping, command evidence |
| Workload | Call another component or dependency | Unique service identity, short-lived credentials, audience restriction |
| Build/release | Produce and promote artifacts | Protected workflow, isolated secrets, provenance, environment approval |

Authentication proves an identity under stated assurance. Authorization is a
separate decision using actor, action, resource, context, and policy version.
Edge authorization may reject early, but the resource owner enforces the final
decision.

## Data classification

- **Public:** approved for unrestricted disclosure.
- **Internal:** non-public project information with limited harm if exposed.
- **Confidential:** business, customer, personal, or operational data requiring
  explicit access and lifecycle controls.
- **Restricted:** credentials, high-impact personal data, cryptographic material,
  or data whose exposure creates severe harm.

Every data element has an owner, purpose, classification, source, allowed use,
retention, deletion, and export rule. Derived data inherits the strongest
relevant classification unless a reviewed transformation proves otherwise.

## Control baseline

### Access

Default deny; least privilege; separation of user, admin, operator, and service
roles; periodic access review; session expiration; revocation; and evidence for
privileged action.

### Input and output

Validate type, length, format, range, relationship, authorization, and business
invariants. Use parameterized data access and context-appropriate output
encoding. Treat files, URLs, redirects, templates, and serialized objects as
untrusted.

### Secrets and cryptography

Secrets come from an approved store, are scoped and rotated, and never appear in
source or telemetry. Use maintained standard cryptographic libraries and
approved protocols; do not design custom cryptography. Key access, rotation,
backup, and destruction match data consequence.

### Network and dependency access

Allow only required ingress and egress. Authenticate sensitive service calls,
validate peer and destination, bound time and size, and contain dependency
failure. Do not trust internal network location as identity.

### Evidence and detection

Record authentication, authorization denial, privileged change, sensitive data
administration, policy change, security control failure, and suspicious abuse
signals. Protect evidence integrity and access while minimizing payloads.

## Administrative safety

Administrative operations show target, scope, effect, and reversibility; require
explicit confirmation; use bounded batch sizes; and provide dry-run or preview
for destructive or broad actions where feasible. Emergency access is time-
limited, separately approved when possible, and reviewed after use.

## Verification

Security evidence includes unit and integration tests for controls, negative
authorization tests, abuse and rate tests, dependency and secret scanning,
threat-model review, artifact provenance, recovery exercises, and targeted
independent assessment before material production exposure.
