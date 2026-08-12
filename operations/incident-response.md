# Incident Response

An incident is an unplanned event that harms or credibly threatens users,
security, data, compliance, or a committed service outcome. Response prioritizes
people, containment, safe restoration, and clear evidence.

## Severity

- **SEV-1 Critical:** widespread or severe user harm, confirmed sensitive-data
  exposure, loss of control, or unsafe system state. Immediate response.
- **SEV-2 High:** significant degradation or contained serious risk with no
  acceptable routine workaround. Urgent coordinated response.
- **SEV-3 Moderate:** limited impact with a viable workaround or low expansion
  risk. Managed during normal support with an owner.
- **SEV-4 Low:** minor defect or operational observation with negligible current
  impact. Track through ordinary work.

## Roles

The Incident Commander owns coordination and decisions; Operations Lead owns
technical mitigation; Communications Lead provides accurate audience updates;
Scribe preserves timeline, evidence, decisions, and actions. One person may hold
multiple roles in a small response, but command remains explicit.

## Response flow

1. Detect or receive the report and open an incident record.
2. Assess current and potential impact, severity, affected scope, and safety.
3. Establish command, communication channel, evidence handling, and update
   cadence.
4. Contain spread or exposure using the least risky effective action.
5. Diagnose from correlated evidence while preserving forensic value.
6. Mitigate or restore; verify authoritative state and user outcomes.
7. Communicate resolution, residual impact, and user actions.
8. Monitor for recurrence and close active response deliberately.
9. Review contributing conditions and authorize corrective work.

## Communication

State known impact, start time, current status, action underway, workaround if
safe, and next update. Separate confirmed fact from investigation. Never expose
personal data, exploit detail, credentials, or unsupported attribution.

## Evidence and security

Preserve relevant logs, traces, configuration, artifact identity, access
records, timeline, commands, and decisions under appropriate access and
retention. A suspected security incident follows the same command structure
with restricted information and legal or privacy escalation as required.

## Post-incident review

Hold a blameless review proportional to impact. Identify technical,
organizational, and detection conditions; what helped; where response struggled;
and which controls should prevent, limit, or detect recurrence. Every corrective
action has an owner, priority, due date, and verification. Track recurring
themes across incidents rather than closing isolated symptoms.
