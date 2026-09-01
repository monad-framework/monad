//! Independent verification-controlled completion for governed execution.
//!
//! Executor completion is advisory. Governed completion is derived from
//! verifier-produced obligation evidence bound to the immutable Execution
//! Envelope and from satisfied approval gates.

use std::collections::{BTreeMap, BTreeSet};

use serde::Serialize;

use crate::harness::ExecutionEnvelope;

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum ObligationDisposition {
    Passed,
    Failed,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ObligationEvidence {
    pub obligation: String,
    pub disposition: ObligationDisposition,
    pub evidence_reference: String,
}

#[derive(Clone, Debug, Default, Eq, PartialEq, Serialize)]
pub struct VerificationEvidenceBundle {
    pub acceptance: Vec<ObligationEvidence>,
    pub verification: Vec<ObligationEvidence>,
    pub completion: Vec<ObligationEvidence>,
    pub approved_gates: Vec<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum CompletionDisposition {
    Complete,
    Incomplete,
    Failed,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct CompletionAssessment {
    pub executor_reported_complete: bool,
    pub disposition: CompletionDisposition,
    pub missing_acceptance_criteria: Vec<String>,
    pub failed_acceptance_criteria: Vec<String>,
    pub missing_verification_obligations: Vec<String>,
    pub failed_verification_obligations: Vec<String>,
    pub missing_completion_criteria: Vec<String>,
    pub failed_completion_criteria: Vec<String>,
    pub missing_approval_gates: Vec<String>,
    pub evidence_references: Vec<String>,
}

/// Assess completion independently of the executor's terminal claim.
///
/// The evidence bundle is expected to come from trusted verification and
/// approval controllers. This function does not accept private model reasoning
/// as evidence and does not infer success from absent obligations.
pub fn assess_completion(
    envelope: &ExecutionEnvelope,
    executor_reported_complete: bool,
    evidence: &VerificationEvidenceBundle,
) -> CompletionAssessment {
    let acceptance = evidence_map(&evidence.acceptance);
    let verification = evidence_map(&evidence.verification);
    let completion = evidence_map(&evidence.completion);
    let approved_gates = evidence.approved_gates.iter().collect::<BTreeSet<_>>();

    let (missing_acceptance_criteria, failed_acceptance_criteria) =
        evaluate_obligations(envelope.acceptance_criteria(), &acceptance);
    let (missing_verification_obligations, failed_verification_obligations) =
        evaluate_obligations(envelope.verification_obligations(), &verification);
    let (missing_completion_criteria, failed_completion_criteria) =
        evaluate_obligations(envelope.completion_criteria(), &completion);
    let missing_approval_gates = envelope
        .approval_gates()
        .iter()
        .filter(|gate| !approved_gates.contains(gate))
        .cloned()
        .collect::<Vec<_>>();

    let has_failure = !failed_acceptance_criteria.is_empty()
        || !failed_verification_obligations.is_empty()
        || !failed_completion_criteria.is_empty();
    let has_missing = !missing_acceptance_criteria.is_empty()
        || !missing_verification_obligations.is_empty()
        || !missing_completion_criteria.is_empty()
        || !missing_approval_gates.is_empty();

    let disposition = if has_failure {
        CompletionDisposition::Failed
    } else if has_missing {
        CompletionDisposition::Incomplete
    } else {
        CompletionDisposition::Complete
    };

    let mut evidence_references = evidence
        .acceptance
        .iter()
        .chain(&evidence.verification)
        .chain(&evidence.completion)
        .map(|item| item.evidence_reference.clone())
        .collect::<Vec<_>>();
    evidence_references.sort();
    evidence_references.dedup();

    CompletionAssessment {
        executor_reported_complete,
        disposition,
        missing_acceptance_criteria,
        failed_acceptance_criteria,
        missing_verification_obligations,
        failed_verification_obligations,
        missing_completion_criteria,
        failed_completion_criteria,
        missing_approval_gates,
        evidence_references,
    }
}

fn evidence_map(evidence: &[ObligationEvidence]) -> BTreeMap<&str, &ObligationEvidence> {
    evidence
        .iter()
        .map(|item| (item.obligation.as_str(), item))
        .collect()
}

fn evaluate_obligations(
    required: &[String],
    evidence: &BTreeMap<&str, &ObligationEvidence>,
) -> (Vec<String>, Vec<String>) {
    let mut missing = Vec::new();
    let mut failed = Vec::new();

    for obligation in required {
        match evidence.get(obligation.as_str()) {
            Some(item) if item.disposition == ObligationDisposition::Passed => {}
            Some(_) => failed.push(obligation.clone()),
            None => missing.push(obligation.clone()),
        }
    }

    (missing, failed)
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use crate::harness::{
        ActorIdentity, ExecutionEnvelopeDraft, RunId, compile_execution_envelope,
    };

    fn envelope() -> ExecutionEnvelope {
        compile_execution_envelope(ExecutionEnvelopeDraft {
            schema_version: "0.1.0".into(),
            run_id: RunId("run-verification-0001".into()),
            logical_time: "2026-09-01T12:00:00Z".into(),
            work_subject: "WP-HARNESS-C1-VERIFY".into(),
            intent: "verify completion independently of executor claims".into(),
            requested_outcome: "governed completion assessment".into(),
            governing_state_digest: "state-verification".into(),
            governed_references: vec![],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new("adapter:test", "executor"),
            granted_capabilities: vec![],
            prohibited_capabilities: vec![],
            allowed_tools: vec![],
            environment_constraints: vec![],
            acceptance_criteria: vec!["artifact exists".into()],
            verification_obligations: vec!["tests pass".into()],
            approval_gates: vec!["review-approved".into()],
            escalation_conditions: vec![],
            completion_criteria: vec!["evidence linked".into()],
            resource_limits: BTreeMap::new(),
        })
    }

    fn passed(obligation: &str, evidence: &str) -> ObligationEvidence {
        ObligationEvidence {
            obligation: obligation.into(),
            disposition: ObligationDisposition::Passed,
            evidence_reference: evidence.into(),
        }
    }

    #[test]
    fn geh_cf_021_executor_completion_without_evidence_remains_incomplete() {
        let assessment = assess_completion(
            &envelope(),
            true,
            &VerificationEvidenceBundle::default(),
        );

        assert_eq!(assessment.disposition, CompletionDisposition::Incomplete);
        assert!(assessment.executor_reported_complete);
        assert_eq!(assessment.missing_acceptance_criteria, vec!["artifact exists"]);
        assert_eq!(assessment.missing_verification_obligations, vec!["tests pass"]);
        assert_eq!(assessment.missing_completion_criteria, vec!["evidence linked"]);
        assert_eq!(assessment.missing_approval_gates, vec!["review-approved"]);
    }

    #[test]
    fn geh_cf_022_failed_verification_prevents_completion() {
        let evidence = VerificationEvidenceBundle {
            acceptance: vec![passed("artifact exists", "evidence:artifact")],
            verification: vec![ObligationEvidence {
                obligation: "tests pass".into(),
                disposition: ObligationDisposition::Failed,
                evidence_reference: "evidence:test-failure".into(),
            }],
            completion: vec![passed("evidence linked", "evidence:link")],
            approved_gates: vec!["review-approved".into()],
        };

        let assessment = assess_completion(&envelope(), true, &evidence);

        assert_eq!(assessment.disposition, CompletionDisposition::Failed);
        assert_eq!(
            assessment.failed_verification_obligations,
            vec!["tests pass"]
        );
    }

    #[test]
    fn geh_cf_023_all_obligations_satisfied_allows_completion() {
        let evidence = VerificationEvidenceBundle {
            acceptance: vec![passed("artifact exists", "evidence:artifact")],
            verification: vec![passed("tests pass", "evidence:tests")],
            completion: vec![passed("evidence linked", "evidence:link")],
            approved_gates: vec!["review-approved".into()],
        };

        let assessment = assess_completion(&envelope(), true, &evidence);

        assert_eq!(assessment.disposition, CompletionDisposition::Complete);
        assert!(assessment.missing_acceptance_criteria.is_empty());
        assert!(assessment.failed_verification_obligations.is_empty());
        assert_eq!(
            assessment.evidence_references,
            vec!["evidence:artifact", "evidence:link", "evidence:tests"]
        );
    }

    #[test]
    fn evidence_can_establish_completion_even_if_executor_does_not_self_report() {
        let evidence = VerificationEvidenceBundle {
            acceptance: vec![passed("artifact exists", "evidence:artifact")],
            verification: vec![passed("tests pass", "evidence:tests")],
            completion: vec![passed("evidence linked", "evidence:link")],
            approved_gates: vec!["review-approved".into()],
        };

        let assessment = assess_completion(&envelope(), false, &evidence);

        assert_eq!(assessment.disposition, CompletionDisposition::Complete);
        assert!(!assessment.executor_reported_complete);
    }
}
