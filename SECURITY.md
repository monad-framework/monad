# Security Policy

MonadV2 treats coordinated vulnerability disclosure as a safety
process. Good-faith research performed within this policy will be handled
respectfully and investigated promptly.

## Supported versions

Until the first stable release, only the latest commit on the default branch is
supported. After stable releases begin, the current major version and the
immediately preceding major version receive security fixes unless a release
notice states otherwise.

## Private reporting

Send reports to **thomasjcarter613@gmail.com**. Do not disclose the issue publicly,
open a public ticket, or include sensitive evidence in third-party paste sites.
Encrypt the report when a public key is published by the project.

Include:

- affected version, commit, component, and deployment assumptions;
- vulnerability class and practical impact;
- reproducible steps or a minimal proof of concept;
- required privileges and user interaction;
- known mitigations and suggested remediation, if available;
- your preferred name and disclosure coordination needs.

## Response targets

| Event | Target |
| --- | --- |
| Receipt acknowledged | 3 business days |
| Initial triage and severity | 7 business days |
| Remediation plan or status update | 14 business days |
| Coordinated disclosure | Mutually agreed after a fix is available |

Targets may change for complex findings, but the reporter will receive a status
update at least every 14 days while the case remains open.

## Research boundaries

Do not access data that is not yours, degrade service, persist after proving the
issue, use social engineering, or test third-party systems without permission.
Stop immediately if personal data, secrets, or cross-tenant access is exposed.
Preserve only the minimum evidence needed for verification.

## Severity and remediation

The security owner assesses exploitability, impact, exposure, and available
controls. Critical issues can trigger an incident, release freeze, credential
rotation, or emergency patch. Fixes require regression tests and review by an
owner independent of the author whenever practical.

## Disclosure credit

The project will offer public credit when requested and legally permissible.
Do not promise bounties: no reward program exists unless separately announced.
