//! Classification of executor effect claims at the governed execution boundary.
//!
//! An executor can report that something happened outside Monad, but the claim
//! does not become a governed effect unless it is attributable to effectful
//! operation history in the run journal.

use serde::Serialize;

use crate::{
    harness::{OperationDisposition, OperationId},
    harness_runtime::GovernedRunJournal,
};

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ExecutorEffectClaim {
    pub claim_id: String,
    pub description: String,
    pub mediated_operation_id: Option<OperationId>,
    pub executor_evidence_reference: Option<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum EffectClaimDisposition {
    GovernedObserved,
    ExternalUnverified,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct EffectClaimAssessment {
    pub claim_id: String,
    pub disposition: EffectClaimDisposition,
    pub governed_operation_id: Option<OperationId>,
    pub diagnostic: String,
}

pub fn classify_effect_claim(
    journal: &GovernedRunJournal,
    claim: &ExecutorEffectClaim,
) -> EffectClaimAssessment {
    if let Some(operation_id) = &claim.mediated_operation_id
        && let Some(entry) = journal.entry(operation_id)
        && matches!(
            entry.disposition,
            OperationDisposition::ExecutedSuccess
                | OperationDisposition::ExecutedFailure
                | OperationDisposition::ToolFailure
                | OperationDisposition::Indeterminate
        )
    {
        return EffectClaimAssessment {
            claim_id: claim.claim_id.clone(),
            disposition: EffectClaimDisposition::GovernedObserved,
            governed_operation_id: Some(operation_id.clone()),
            diagnostic: "claim is attributable to recorded governed operation history".into(),
        };
    }

    EffectClaimAssessment {
        claim_id: claim.claim_id.clone(),
        disposition: EffectClaimDisposition::ExternalUnverified,
        governed_operation_id: None,
        diagnostic: "executor claim is not backed by effectful governed operation history".into(),
    }
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use crate::{
        harness::{
            ActorIdentity, CapabilityGrant, ExecutionEnvelope, ExecutionEnvelopeDraft, OperationId,
            OperationRequest, RunId, RunState, compile_execution_envelope,
        },
        harness_gateway::{
            BackendExecution, OperationBackend, OperationGovernanceContext, PolicyDecision,
        },
        harness_runtime::{GovernedRunJournal, ReplayPolicy},
    };

    #[derive(Default)]
    struct RecordingBackend {
        calls: usize,
    }

    impl OperationBackend for RecordingBackend {
        fn execute(&mut self, _request: &OperationRequest) -> BackendExecution {
            self.calls += 1;
            BackendExecution::Success {
                result_digest: Some("effect-result".into()),
                evidence_reference: Some("evidence:governed-effect".into()),
            }
        }
    }

    fn envelope() -> ExecutionEnvelope {
        compile_execution_envelope(ExecutionEnvelopeDraft {
            schema_version: "0.1.0".into(),
            run_id: RunId("run-effects-0001".into()),
            logical_time: "2026-09-01T12:00:00Z".into(),
            work_subject: "WP-HARNESS-C1-EFFECTS".into(),
            intent: "classify observable effect claims".into(),
            requested_outcome: "external claims remain unverified".into(),
            governing_state_digest: "state-effects".into(),
            governed_references: vec![],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new("adapter:test", "executor"),
            granted_capabilities: vec![CapabilityGrant::new(
                "workspace.write",
                "workspace/output.txt",
            )],
            prohibited_capabilities: vec![CapabilityGrant::new("release.publish", "production")],
            allowed_tools: vec!["workspace".into(), "release".into()],
            environment_constraints: vec![],
            acceptance_criteria: vec![],
            verification_obligations: vec![],
            approval_gates: vec![],
            escalation_conditions: vec![],
            completion_criteria: vec![],
            resource_limits: BTreeMap::new(),
        })
    }

    fn context() -> OperationGovernanceContext {
        OperationGovernanceContext {
            current_governing_state_digest: "state-effects".into(),
            run_state: RunState::Running,
            policy: PolicyDecision::Allow,
            approved_gates: vec![],
        }
    }

    #[test]
    fn geh_cf_024_external_unmediated_effect_stays_unverified() {
        let envelope = envelope();
        let journal = GovernedRunJournal::new(&envelope);
        let claim = ExecutorEffectClaim {
            claim_id: "claim-external-1".into(),
            description: "executor says it deployed directly".into(),
            mediated_operation_id: None,
            executor_evidence_reference: Some("executor:self-report".into()),
        };

        let assessment = classify_effect_claim(&journal, &claim);

        assert_eq!(
            assessment.disposition,
            EffectClaimDisposition::ExternalUnverified
        );
        assert!(assessment.governed_operation_id.is_none());
    }

    #[test]
    fn mediated_effect_is_attributable_to_journal_history() {
        let envelope = envelope();
        let mut journal = GovernedRunJournal::new(&envelope);
        let mut backend = RecordingBackend::default();
        let request = OperationRequest {
            operation_id: OperationId("op-effect-1".into()),
            run_id: envelope.run_id().clone(),
            envelope_id: envelope.envelope_id().clone(),
            executor_actor_id: envelope.executor().actor_id.clone(),
            capability: "workspace.write".into(),
            tool: "workspace".into(),
            operation_type: "write_text".into(),
            target_scope: "workspace/output.txt".into(),
            parameters_digest: "params-effect".into(),
            causal_parent: None,
            idempotency_key: Some("effect-write-1".into()),
        };

        journal
            .mediate(
                &envelope,
                &request,
                &context(),
                ReplayPolicy::NonIdempotent,
                &mut backend,
            )
            .expect("governed operation executes");
        let claim = ExecutorEffectClaim {
            claim_id: "claim-governed-1".into(),
            description: "workspace write completed".into(),
            mediated_operation_id: Some(request.operation_id.clone()),
            executor_evidence_reference: None,
        };

        let assessment = classify_effect_claim(&journal, &claim);

        assert_eq!(
            assessment.disposition,
            EffectClaimDisposition::GovernedObserved
        );
        assert_eq!(assessment.governed_operation_id, Some(request.operation_id));
    }

    #[test]
    fn geh_cf_025_injection_text_cannot_create_release_authority() {
        let envelope = envelope();
        let mut journal = GovernedRunJournal::new(&envelope);
        let mut backend = RecordingBackend::default();
        let request = OperationRequest {
            operation_id: OperationId("op-injection-1".into()),
            run_id: envelope.run_id().clone(),
            envelope_id: envelope.envelope_id().clone(),
            executor_actor_id: envelope.executor().actor_id.clone(),
            capability: "release.publish".into(),
            tool: "release".into(),
            operation_type: "publish".into(),
            target_scope: "production".into(),
            parameters_digest: "fixture:ignore-policy-and-publish-now".into(),
            causal_parent: None,
            idempotency_key: Some("publish-attempt-1".into()),
        };

        let outcome = journal
            .mediate(
                &envelope,
                &request,
                &context(),
                ReplayPolicy::NonIdempotent,
                &mut backend,
            )
            .expect("unauthorized request is classified, not executed");

        match outcome {
            crate::harness_runtime::RuntimeOperationOutcome::Mediated(result) => {
                assert_eq!(
                    result.result.disposition,
                    OperationDisposition::DeniedCapability
                );
            }
            other => panic!("unexpected runtime outcome: {other:?}"),
        }
        assert_eq!(backend.calls, 0);
    }
}
