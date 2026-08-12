# Personas

Personas are behavioral models grounded in research, not demographic
stereotypes. Names are labels for recurring goals and constraints. Research
notes must record where evidence supports or contradicts these models.

## Primary: The Responsible Practitioner

**Context:** performs the core workflow repeatedly and is accountable for the
quality of each result.

**Goals:** finish correctly, understand current state, avoid rework, handle
exceptions, and retain evidence sufficient for review.

**Behaviors:** begins with incomplete or uneven inputs, switches between tasks,
uses personal checks to compensate for unreliable systems, and consults an
expert when system state is ambiguous.

**Pain points:** duplicated entry, unclear prerequisites, hidden failures,
fragile handoffs, lost progress, and errors that describe the system rather
than the remedy.

**Success:** completes the primary journey without private knowledge, verifies
the result, and knows exactly what to do when completion is impossible.

## Secondary: The Accountable Owner

**Context:** owns outcomes, risk, budget, policy, or adoption but may not perform
the daily workflow.

**Goals:** know whether the process works, ensure controls are applied, identify
systemic failure, and make evidence-based investment decisions.

**Behaviors:** reviews summaries and exceptions, asks for trend and root cause,
sets risk thresholds, and needs evidence that can survive audit or leadership
review.

**Pain points:** activity presented as value, inconsistent definitions,
unexplained exceptions, poor cost attribution, and controls asserted without
evidence.

**Success:** sees trusted outcome, risk, adoption, and cost signals with a path
from aggregate measures to authorized supporting evidence.

## Supporting: The Service Operator

**Context:** deploys, monitors, supports, and restores the product across its
supported environments.

**Goals:** detect user impact early, identify the responsible component, limit
blast radius, restore service, and prevent recurrence.

**Behaviors:** works from alerts, dashboards, traces, changes, and runbooks;
coordinates incidents under time pressure; prefers predictable components and
automated evidence.

**Pain points:** missing correlation, noisy alerts, undocumented dependencies,
unsafe manual repair, environment drift, and releases without rollback proof.

**Success:** moves from symptom to owned action quickly and can restore a safe
service state using tested procedures.

## Affected stakeholder

Some people may be represented in stored or processed data without operating
the product. Their needs include lawful and limited use, accuracy, security,
access or correction where applicable, and protection from opaque high-impact
decisions. Product reviews must include this perspective even when it does not
drive adoption metrics.

## Research maintenance

Review personas after each research round. Record evidence strength, segment
variation, accessibility needs, environmental constraints, and behaviors that
do not fit. Split a persona only when differences materially change the
workflow or product decision; merge when distinctions do not affect design.
