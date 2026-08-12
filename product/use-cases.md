# Use Cases

Use cases define supported actor-system contracts. Each includes a successful
path, controlled alternatives, and an observable postcondition.

## UC-001 — Complete the primary workflow

- **Primary actor:** Responsible Practitioner
- **Trigger:** The actor has a valid outcome to achieve and required authority.
- **Preconditions:** Identity is verified; required dependencies are available;
  input classification is supported.
- **Success postcondition:** A verified result and evidence record exist in a
  terminal successful state.

### Main flow

1. The actor states the intended outcome.
2. The system presents required inputs, constraints, and expected effect.
3. The actor supplies or selects inputs.
4. The system validates data, authorization, and applicable rules.
5. The actor reviews and confirms consequential action.
6. The system executes while exposing durable progress.
7. The system verifies the result and presents evidence and next actions.

### Alternate flows

- Invalid input returns field- or rule-specific correction guidance.
- A warning requires explicit acknowledgment without being misrepresented as a
  successful validation.
- A dependency interruption preserves safe state and offers retry or escalation.
- A duplicate request returns the existing result or safe status rather than
  repeating the effect.
- Unsupported conditions stop before commitment and identify the supported
  alternative or escalation path.

## UC-002 — Resume or recover a workflow

The practitioner locates an interrupted instance, reviews its last durable
state, and chooses an allowed retry, compensation, cancellation, or escalation.
Recovery must not require editing internal state or interpreting raw logs.

**Success postcondition:** the instance reaches a defined terminal state or is
assigned to an accountable escalation owner with preserved evidence.

## UC-003 — Review outcome and control evidence

The Accountable Owner filters authorized workflow outcomes by period, cohort,
status, or policy and examines aggregate measures and individual evidence.
Sensitive payloads remain minimized and access is audited.

**Success postcondition:** the owner can support an outcome or control decision
using consistent definitions and traceable evidence.

## UC-004 — Diagnose and restore service

The Service Operator receives a symptom tied to user impact, identifies the
affected journey and recent changes, applies a documented mitigation or
rollback, verifies recovery, and opens follow-up work.

**Success postcondition:** service returns to its defined safe state and the
incident timeline contains enough evidence for review.

## Use-case traceability

UC-001 maps to FR-001 through FR-008. UC-002 emphasizes FR-003 through FR-006.
UC-003 emphasizes FR-004 and FR-007. UC-004 maps to the reliability and
operability quality requirements. Acceptance suites should preserve these IDs.
