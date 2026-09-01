//! Deterministic fail-closed mediation for governed execution operations.
//!
//! This module implements the first C1 governance-kernel slice. It evaluates
//! an [`OperationRequest`] against an immutable [`ExecutionEnvelope`] before a
//! backend is allowed to observe or execute the operation. Version 0.1 uses
//! exact capability-scope matching only; richer scope languages remain a
//! separate, explicitly versioned concern.

use serde::Serialize;

use crate::harness::{
    ExecutionEnvelope, OperationDisposition, OperationId, OperationRequest, OperationResult,
    RunState,
};

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum PolicyDecision {
    Allow,
    Deny { reason: String },
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct OperationGovernanceContext {
    pub current_governing_state_digest: String,
    pub run_state: RunState,
    pub policy: PolicyDecision,
    pub approved_gates: Vec<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum GovernanceCheckKind {
    RunBinding,
    EnvelopeBinding,
    ExecutorBinding,
    GoverningStateFreshness,
    RunState,
    ToolEligibility,
    CapabilityGrant,
    CapabilityProhibition,
    Scope,
    Policy,
    Approval,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum GovernanceCheckOutcome {
    Passed,
    Failed,
    Waiting,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct GovernanceCheckRecord {
    pub kind: GovernanceCheckKind,
    pub outcome: GovernanceCheckOutcome,
    pub detail: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct OperationDecisionEvidence {
    pub operation_id: OperationId,
    pub run_id: String,
    pub envelope_id: String,
    pub executor_actor_id: String,
    pub capability: String,
    pub tool: String,
    pub target_scope: String,
    pub disposition: OperationDisposition,
    pub checks: Vec<GovernanceCheckRecord>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct MediatedOperationResult {
    pub result: OperationResult,
    pub decision: OperationDecisionEvidence,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum BackendExecution {
    Success {
        result_digest: Option<String>,
        evidence_reference: Option<String>,
    },
    OperationFailure {
        diagnostic: String,
        evidence_reference: Option<String>,
    },
    ToolFailure {
        diagnostic: String,
    },
}

/// Effect boundary used only after all governance checks pass.
///
/// Implementations may wrap a filesystem operation, native tool, subprocess,
/// service, or deterministic test backend. The backend receives no authority
/// to reinterpret the envelope or governance decision.
pub trait OperationBackend {
    fn execute(&mut self, request: &OperationRequest) -> BackendExecution;
}

/// Evaluate and, only when allowed, execute a governed operation.
///
/// Every denial returns decision evidence and leaves the backend untouched.
pub fn mediate_operation<B: OperationBackend>(
    envelope: &ExecutionEnvelope,
    request: &OperationRequest,
    context: &OperationGovernanceContext,
    backend: &mut B,
) -> MediatedOperationResult {
    let mut checks = Vec::new();

    if request.run_id != *envelope.run_id() {
        return denied(
            request,
            OperationDisposition::DeniedPolicy,
            checks,
            GovernanceCheckKind::RunBinding,
            format!(
                "operation run {:?} does not match envelope run {:?}",
                request.run_id.0,
                envelope.run_id().0
            ),
        );
    }
    checks.push(passed(
        GovernanceCheckKind::RunBinding,
        "operation is bound to the envelope run",
    ));

    if request.envelope_id != *envelope.envelope_id() {
        return denied(
            request,
            OperationDisposition::DeniedPolicy,
            checks,
            GovernanceCheckKind::EnvelopeBinding,
            "operation references a different execution envelope",
        );
    }
    checks.push(passed(
        GovernanceCheckKind::EnvelopeBinding,
        "operation references the bound execution envelope",
    ));

    if request.executor_actor_id != envelope.executor().actor_id {
        return denied(
            request,
            OperationDisposition::DeniedPolicy,
            checks,
            GovernanceCheckKind::ExecutorBinding,
            "operation executor does not match the envelope executor",
        );
    }
    checks.push(passed(
        GovernanceCheckKind::ExecutorBinding,
        "operation executor matches the envelope executor",
    ));

    if context.current_governing_state_digest != envelope.governing_state_digest() {
        return denied(
            request,
            OperationDisposition::StaleEnvelope,
            checks,
            GovernanceCheckKind::GoverningStateFreshness,
            format!(
                "bound governing state {:?} differs from current state {:?}",
                envelope.governing_state_digest(),
                context.current_governing_state_digest
            ),
        );
    }
    checks.push(passed(
        GovernanceCheckKind::GoverningStateFreshness,
        "bound governing state is current",
    ));

    if context.run_state == RunState::Cancelled {
        return denied(
            request,
            OperationDisposition::Cancelled,
            checks,
            GovernanceCheckKind::RunState,
            "run is cancelled",
        );
    }

    if context.run_state != RunState::Running {
        return denied(
            request,
            OperationDisposition::DeniedPolicy,
            checks,
            GovernanceCheckKind::RunState,
            format!(
                "run state {:?} does not permit consequential operations",
                context.run_state
            ),
        );
    }
    checks.push(passed(
        GovernanceCheckKind::RunState,
        "run is in the running state",
    ));

    if !envelope
        .allowed_tools()
        .iter()
        .any(|tool| tool == &request.tool)
    {
        return denied(
            request,
            OperationDisposition::DeniedCapability,
            checks,
            GovernanceCheckKind::ToolEligibility,
            format!("tool {:?} is not allowed by the envelope", request.tool),
        );
    }
    checks.push(passed(
        GovernanceCheckKind::ToolEligibility,
        "requested tool is allowed by the envelope",
    ));

    if envelope
        .prohibited_capabilities()
        .iter()
        .any(|prohibition| {
            prohibition.capability == request.capability
                && prohibition.scope == request.target_scope
        })
    {
        return denied(
            request,
            OperationDisposition::DeniedCapability,
            checks,
            GovernanceCheckKind::CapabilityProhibition,
            "requested capability and exact target scope are explicitly prohibited",
        );
    }
    checks.push(passed(
        GovernanceCheckKind::CapabilityProhibition,
        "no exact capability prohibition applies",
    ));

    let matching_capability = envelope
        .granted_capabilities()
        .iter()
        .filter(|grant| grant.capability == request.capability)
        .collect::<Vec<_>>();

    if matching_capability.is_empty() {
        return denied(
            request,
            OperationDisposition::DeniedCapability,
            checks,
            GovernanceCheckKind::CapabilityGrant,
            format!(
                "capability {:?} is not granted by the envelope",
                request.capability
            ),
        );
    }
    checks.push(passed(
        GovernanceCheckKind::CapabilityGrant,
        "requested capability is explicitly granted",
    ));

    if !matching_capability
        .iter()
        .any(|grant| grant.scope == request.target_scope)
    {
        return denied(
            request,
            OperationDisposition::DeniedScope,
            checks,
            GovernanceCheckKind::Scope,
            format!(
                "target scope {:?} is not an exact granted scope for capability {:?}",
                request.target_scope, request.capability
            ),
        );
    }
    checks.push(passed(
        GovernanceCheckKind::Scope,
        "target scope exactly matches an explicit capability grant",
    ));

    match &context.policy {
        PolicyDecision::Allow => checks.push(passed(
            GovernanceCheckKind::Policy,
            "governing policy allows the operation",
        )),
        PolicyDecision::Deny { reason } => {
            return denied(
                request,
                OperationDisposition::DeniedPolicy,
                checks,
                GovernanceCheckKind::Policy,
                reason.clone(),
            );
        }
    }

    if let Some(missing_gate) = envelope.approval_gates().iter().find(|gate| {
        !context
            .approved_gates
            .iter()
            .any(|approved| approved == *gate)
    }) {
        return waiting_approval(
            request,
            checks,
            format!("required approval gate {missing_gate:?} is not satisfied"),
        );
    }
    checks.push(passed(
        GovernanceCheckKind::Approval,
        "all envelope approval gates are satisfied",
    ));

    let execution = backend.execute(request);
    let result = match execution {
        BackendExecution::Success {
            result_digest,
            evidence_reference,
        } => OperationResult {
            operation_id: request.operation_id.clone(),
            disposition: OperationDisposition::ExecutedSuccess,
            evidence_reference,
            result_digest,
            diagnostic: None,
        },
        BackendExecution::OperationFailure {
            diagnostic,
            evidence_reference,
        } => OperationResult {
            operation_id: request.operation_id.clone(),
            disposition: OperationDisposition::ExecutedFailure,
            evidence_reference,
            result_digest: None,
            diagnostic: Some(diagnostic),
        },
        BackendExecution::ToolFailure { diagnostic } => OperationResult {
            operation_id: request.operation_id.clone(),
            disposition: OperationDisposition::ToolFailure,
            evidence_reference: None,
            result_digest: None,
            diagnostic: Some(diagnostic),
        },
    };

    MediatedOperationResult {
        decision: OperationDecisionEvidence {
            operation_id: request.operation_id.clone(),
            run_id: request.run_id.0.clone(),
            envelope_id: request.envelope_id.0.clone(),
            executor_actor_id: request.executor_actor_id.clone(),
            capability: request.capability.clone(),
            tool: request.tool.clone(),
            target_scope: request.target_scope.clone(),
            disposition: result.disposition.clone(),
            checks,
        },
        result,
    }
}

fn denied(
    request: &OperationRequest,
    disposition: OperationDisposition,
    mut checks: Vec<GovernanceCheckRecord>,
    kind: GovernanceCheckKind,
    detail: impl Into<String>,
) -> MediatedOperationResult {
    let detail = detail.into();
    checks.push(GovernanceCheckRecord {
        kind,
        outcome: GovernanceCheckOutcome::Failed,
        detail: detail.clone(),
    });

    terminal_decision(request, disposition, checks, Some(detail))
}

fn waiting_approval(
    request: &OperationRequest,
    mut checks: Vec<GovernanceCheckRecord>,
    detail: impl Into<String>,
) -> MediatedOperationResult {
    let detail = detail.into();
    checks.push(GovernanceCheckRecord {
        kind: GovernanceCheckKind::Approval,
        outcome: GovernanceCheckOutcome::Waiting,
        detail: detail.clone(),
    });

    terminal_decision(
        request,
        OperationDisposition::WaitingApproval,
        checks,
        Some(detail),
    )
}

fn terminal_decision(
    request: &OperationRequest,
    disposition: OperationDisposition,
    checks: Vec<GovernanceCheckRecord>,
    diagnostic: Option<String>,
) -> MediatedOperationResult {
    MediatedOperationResult {
        result: OperationResult {
            operation_id: request.operation_id.clone(),
            disposition: disposition.clone(),
            evidence_reference: None,
            result_digest: None,
            diagnostic,
        },
        decision: OperationDecisionEvidence {
            operation_id: request.operation_id.clone(),
            run_id: request.run_id.0.clone(),
            envelope_id: request.envelope_id.0.clone(),
            executor_actor_id: request.executor_actor_id.clone(),
            capability: request.capability.clone(),
            tool: request.tool.clone(),
            target_scope: request.target_scope.clone(),
            disposition,
            checks,
        },
    }
}

fn passed(kind: GovernanceCheckKind, detail: impl Into<String>) -> GovernanceCheckRecord {
    GovernanceCheckRecord {
        kind,
        outcome: GovernanceCheckOutcome::Passed,
        detail: detail.into(),
    }
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use crate::harness::{
        ActorIdentity, CapabilityGrant, ExecutionEnvelopeDraft, GovernedReference, RunId,
        compile_execution_envelope,
    };

    #[derive(Default)]
    struct RecordingBackend {
        calls: Vec<OperationId>,
    }

    impl OperationBackend for RecordingBackend {
        fn execute(&mut self, request: &OperationRequest) -> BackendExecution {
            self.calls.push(request.operation_id.clone());
            BackendExecution::Success {
                result_digest: Some("result-sha256-example".into()),
                evidence_reference: Some(format!("evidence:{}", request.operation_id.0)),
            }
        }
    }

    fn envelope() -> ExecutionEnvelope {
        compile_execution_envelope(ExecutionEnvelopeDraft {
            schema_version: "0.1.0".into(),
            run_id: RunId("run-c1-0001".into()),
            logical_time: "2026-09-01T12:00:00Z".into(),
            work_subject: "WP-HARNESS-C1".into(),
            intent: "mediate one bounded local operation".into(),
            requested_outcome: "fail-closed operation decision".into(),
            governing_state_digest: "state-c1".into(),
            governed_references: vec![GovernedReference::new("spec", "TECH-HARNESS-0001")],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new("adapter:test", "executor"),
            granted_capabilities: vec![CapabilityGrant::new(
                "workspace.read",
                "workspace/README.md",
            )],
            prohibited_capabilities: vec![CapabilityGrant::new(
                "workspace.write",
                "workspace/README.md",
            )],
            allowed_tools: vec!["workspace".into()],
            environment_constraints: vec!["local-first".into()],
            acceptance_criteria: vec!["governance checks precede backend execution".into()],
            verification_obligations: vec!["cargo test -p monad-core harness_gateway".into()],
            approval_gates: vec![],
            escalation_conditions: vec!["governing state becomes stale".into()],
            completion_criteria: vec!["required C1 evidence passes".into()],
            resource_limits: BTreeMap::new(),
        })
    }

    fn request(envelope: &ExecutionEnvelope) -> OperationRequest {
        OperationRequest {
            operation_id: OperationId("op-c1-0001".into()),
            run_id: envelope.run_id().clone(),
            envelope_id: envelope.envelope_id().clone(),
            executor_actor_id: envelope.executor().actor_id.clone(),
            capability: "workspace.read".into(),
            tool: "workspace".into(),
            operation_type: "read_text".into(),
            target_scope: "workspace/README.md".into(),
            parameters_digest: "parameters-sha256-example".into(),
            causal_parent: None,
            idempotency_key: None,
        }
    }

    fn context() -> OperationGovernanceContext {
        OperationGovernanceContext {
            current_governing_state_digest: "state-c1".into(),
            run_state: RunState::Running,
            policy: PolicyDecision::Allow,
            approved_gates: vec![],
        }
    }

    #[test]
    fn geh_cf_010_granted_exact_scope_executes() {
        let envelope = envelope();
        let request = request(&envelope);
        let mut backend = RecordingBackend::default();

        let outcome = mediate_operation(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.result.disposition,
            OperationDisposition::ExecutedSuccess
        );
        assert_eq!(backend.calls, vec![request.operation_id]);
        assert!(!outcome.decision.checks.is_empty());
    }

    #[test]
    fn geh_cf_011_missing_capability_is_denied_without_effect() {
        let envelope = envelope();
        let mut request = request(&envelope);
        request.capability = "workspace.delete".into();
        let mut backend = RecordingBackend::default();

        let outcome = mediate_operation(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.result.disposition,
            OperationDisposition::DeniedCapability
        );
        assert!(backend.calls.is_empty());
    }

    #[test]
    fn geh_cf_012_explicit_prohibition_is_denied_without_effect() {
        let envelope = envelope();
        let mut request = request(&envelope);
        request.capability = "workspace.write".into();
        let mut backend = RecordingBackend::default();

        let outcome = mediate_operation(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.result.disposition,
            OperationDisposition::DeniedCapability
        );
        assert!(backend.calls.is_empty());
        assert!(outcome.decision.checks.iter().any(|check| {
            check.kind == GovernanceCheckKind::CapabilityProhibition
                && check.outcome == GovernanceCheckOutcome::Failed
        }));
    }

    #[test]
    fn geh_cf_013_outside_exact_scope_is_denied_without_effect() {
        let envelope = envelope();
        let mut request = request(&envelope);
        request.target_scope = "workspace/SECURITY.md".into();
        let mut backend = RecordingBackend::default();

        let outcome = mediate_operation(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.result.disposition,
            OperationDisposition::DeniedScope
        );
        assert!(backend.calls.is_empty());
    }

    #[test]
    fn geh_cf_014_missing_required_approval_waits_without_effect() {
        let envelope = compile_execution_envelope(base_draft_with_approval());
        let request = request_for(&envelope);
        let mut backend = RecordingBackend::default();

        let outcome = mediate_operation(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.result.disposition,
            OperationDisposition::WaitingApproval
        );
        assert!(backend.calls.is_empty());
    }

    #[test]
    fn geh_cf_015_satisfied_approval_allows_same_request() {
        let envelope = compile_execution_envelope(base_draft_with_approval());
        let request = request_for(&envelope);
        let mut approved = context();
        approved.approved_gates = vec!["human:read-sensitive".into()];
        let mut backend = RecordingBackend::default();

        let outcome = mediate_operation(&envelope, &request, &approved, &mut backend);

        assert_eq!(
            outcome.result.disposition,
            OperationDisposition::ExecutedSuccess
        );
        assert_eq!(backend.calls.len(), 1);
    }

    #[test]
    fn geh_cf_016_stale_governing_state_suspends_effect() {
        let envelope = envelope();
        let request = request(&envelope);
        let mut stale = context();
        stale.current_governing_state_digest = "state-c1-new".into();
        let mut backend = RecordingBackend::default();

        let outcome = mediate_operation(&envelope, &request, &stale, &mut backend);

        assert_eq!(
            outcome.result.disposition,
            OperationDisposition::StaleEnvelope
        );
        assert!(backend.calls.is_empty());
    }

    #[test]
    fn geh_cf_017_cancelled_run_rejects_new_effect() {
        let envelope = envelope();
        let request = request(&envelope);
        let mut cancelled = context();
        cancelled.run_state = RunState::Cancelled;
        let mut backend = RecordingBackend::default();

        let outcome = mediate_operation(&envelope, &request, &cancelled, &mut backend);

        assert_eq!(outcome.result.disposition, OperationDisposition::Cancelled);
        assert!(backend.calls.is_empty());
    }

    #[test]
    fn policy_denial_prevents_backend_execution() {
        let envelope = envelope();
        let request = request(&envelope);
        let mut denied_context = context();
        denied_context.policy = PolicyDecision::Deny {
            reason: "fixture policy denial".into(),
        };
        let mut backend = RecordingBackend::default();

        let outcome = mediate_operation(&envelope, &request, &denied_context, &mut backend);

        assert_eq!(
            outcome.result.disposition,
            OperationDisposition::DeniedPolicy
        );
        assert!(backend.calls.is_empty());
    }

    fn base_draft_with_approval() -> ExecutionEnvelopeDraft {
        ExecutionEnvelopeDraft {
            schema_version: "0.1.0".into(),
            run_id: RunId("run-c1-approval".into()),
            logical_time: "2026-09-01T12:00:00Z".into(),
            work_subject: "WP-HARNESS-C1".into(),
            intent: "require approval".into(),
            requested_outcome: "approval-gated operation".into(),
            governing_state_digest: "state-c1".into(),
            governed_references: vec![],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new("adapter:test", "executor"),
            granted_capabilities: vec![CapabilityGrant::new(
                "workspace.read",
                "workspace/README.md",
            )],
            prohibited_capabilities: vec![],
            allowed_tools: vec!["workspace".into()],
            environment_constraints: vec![],
            acceptance_criteria: vec![],
            verification_obligations: vec![],
            approval_gates: vec!["human:read-sensitive".into()],
            escalation_conditions: vec![],
            completion_criteria: vec![],
            resource_limits: BTreeMap::new(),
        }
    }

    fn request_for(envelope: &ExecutionEnvelope) -> OperationRequest {
        OperationRequest {
            operation_id: OperationId("op-c1-approval".into()),
            run_id: envelope.run_id().clone(),
            envelope_id: envelope.envelope_id().clone(),
            executor_actor_id: envelope.executor().actor_id.clone(),
            capability: "workspace.read".into(),
            tool: "workspace".into(),
            operation_type: "read_text".into(),
            target_scope: "workspace/README.md".into(),
            parameters_digest: "parameters-sha256-example".into(),
            causal_parent: None,
            idempotency_key: None,
        }
    }
}
