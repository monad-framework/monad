//! Run-local history, checkpoint, resume, and replay controls for governed execution.
//!
//! The Execution Envelope remains immutable. Mutable operational history lives
//! in a run journal whose checkpoints bind back to the original run, envelope,
//! governing-state digest, and a deterministic digest of prior operation history.

use std::collections::BTreeMap;

use serde::Serialize;
use sha2::{Digest, Sha256};

use crate::{
    harness::{
        ExecutionEnvelope, OperationDisposition, OperationId, OperationRequest, OperationResult,
        RunId,
    },
    harness_gateway::{
        MediatedOperationResult, OperationBackend, OperationGovernanceContext, mediate_operation,
    },
};

const CHECKPOINT_DIGEST_DOMAIN: &str = "monad.execution-checkpoint.v1";
const JOURNAL_DIGEST_DOMAIN: &str = "monad.execution-journal.v1";

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum ReplayPolicy {
    /// The backend contract declares replay safe. Monad still records history,
    /// but an idempotency key is not mandatory.
    Idempotent,
    /// Duplicate execution could create a second effect. The request therefore
    /// requires an idempotency key and Monad suppresses a matching retry.
    NonIdempotent,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct OperationMaterial {
    pub run_id: String,
    pub envelope_id: String,
    pub executor_actor_id: String,
    pub capability: String,
    pub tool: String,
    pub operation_type: String,
    pub target_scope: String,
    pub parameters_digest: String,
    pub causal_parent: Option<String>,
}

impl From<&OperationRequest> for OperationMaterial {
    fn from(request: &OperationRequest) -> Self {
        Self {
            run_id: request.run_id.0.clone(),
            envelope_id: request.envelope_id.0.clone(),
            executor_actor_id: request.executor_actor_id.clone(),
            capability: request.capability.clone(),
            tool: request.tool.clone(),
            operation_type: request.operation_type.clone(),
            target_scope: request.target_scope.clone(),
            parameters_digest: request.parameters_digest.clone(),
            causal_parent: request
                .causal_parent
                .as_ref()
                .map(|operation| operation.0.clone()),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct OperationJournalEntry {
    pub operation_id: OperationId,
    pub idempotency_key: Option<String>,
    pub material: OperationMaterial,
    pub disposition: OperationDisposition,
    pub evidence_reference: Option<String>,
    pub result_digest: Option<String>,
    pub diagnostic: Option<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ExecutionCheckpoint {
    pub checkpoint_id: String,
    pub run_id: RunId,
    pub envelope_id: String,
    pub governing_state_digest: String,
    pub journal_entry_count: usize,
    pub journal_digest: String,
    pub last_operation_id: Option<OperationId>,
    pub evidence_references: Vec<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum ResumeDisposition {
    Allowed,
    EnvelopeMismatch,
    GoverningStateDrift,
    HistoryMismatch,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ResumeDecision {
    pub disposition: ResumeDisposition,
    pub diagnostic: Option<String>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum RuntimeOperationError {
    RunBindingMismatch,
    EnvelopeBindingMismatch,
    MissingIdempotencyKey,
    ReplayConflict {
        idempotency_key: String,
        prior_operation_id: OperationId,
    },
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub enum RuntimeOperationOutcome {
    Mediated(MediatedOperationResult),
    ReplaySuppressed {
        retry_operation_id: OperationId,
        original_operation_id: OperationId,
        original_result: OperationResult,
    },
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct GovernedRunJournal {
    run_id: RunId,
    envelope_id: String,
    governing_state_digest: String,
    entries: Vec<OperationJournalEntry>,
    effectful_operation_index: BTreeMap<OperationId, usize>,
    idempotency_index: BTreeMap<String, usize>,
}

impl GovernedRunJournal {
    pub fn new(envelope: &ExecutionEnvelope) -> Self {
        Self {
            run_id: envelope.run_id().clone(),
            envelope_id: envelope.envelope_id().0.clone(),
            governing_state_digest: envelope.governing_state_digest().to_owned(),
            entries: Vec::new(),
            effectful_operation_index: BTreeMap::new(),
            idempotency_index: BTreeMap::new(),
        }
    }

    pub fn entries(&self) -> &[OperationJournalEntry] {
        &self.entries
    }

    pub fn has_effectful_operation(&self, operation_id: &OperationId) -> bool {
        self.effectful_operation_index.contains_key(operation_id)
    }

    pub fn entry(&self, operation_id: &OperationId) -> Option<&OperationJournalEntry> {
        self.entries
            .iter()
            .find(|entry| &entry.operation_id == operation_id)
    }

    pub fn mediate<B: OperationBackend>(
        &mut self,
        envelope: &ExecutionEnvelope,
        request: &OperationRequest,
        context: &OperationGovernanceContext,
        replay_policy: ReplayPolicy,
        backend: &mut B,
    ) -> Result<RuntimeOperationOutcome, RuntimeOperationError> {
        self.validate_binding(envelope, request)?;

        if replay_policy == ReplayPolicy::NonIdempotent && request.idempotency_key.is_none() {
            return Err(RuntimeOperationError::MissingIdempotencyKey);
        }

        if let Some(index) = self.effectful_operation_index.get(&request.operation_id) {
            let prior = &self.entries[*index];
            if prior.material == OperationMaterial::from(request) {
                return Ok(RuntimeOperationOutcome::ReplaySuppressed {
                    retry_operation_id: request.operation_id.clone(),
                    original_operation_id: prior.operation_id.clone(),
                    original_result: result_from_entry(prior),
                });
            }

            return Err(RuntimeOperationError::ReplayConflict {
                idempotency_key: request
                    .idempotency_key
                    .clone()
                    .unwrap_or_else(|| format!("operation:{}", request.operation_id.0)),
                prior_operation_id: prior.operation_id.clone(),
            });
        }

        if let Some(key) = &request.idempotency_key
            && let Some(index) = self.idempotency_index.get(key)
        {
            let prior = &self.entries[*index];
            if prior.material == OperationMaterial::from(request) {
                return Ok(RuntimeOperationOutcome::ReplaySuppressed {
                    retry_operation_id: request.operation_id.clone(),
                    original_operation_id: prior.operation_id.clone(),
                    original_result: result_from_entry(prior),
                });
            }

            return Err(RuntimeOperationError::ReplayConflict {
                idempotency_key: key.clone(),
                prior_operation_id: prior.operation_id.clone(),
            });
        }

        let outcome = mediate_operation(envelope, request, context, backend);
        self.record(request, &outcome);
        Ok(RuntimeOperationOutcome::Mediated(outcome))
    }

    pub fn checkpoint(&self) -> ExecutionCheckpoint {
        let journal_digest = self.journal_digest(self.entries.len());
        let last_operation_id = self.entries.last().map(|entry| entry.operation_id.clone());
        let evidence_references = self
            .entries
            .iter()
            .filter_map(|entry| entry.evidence_reference.clone())
            .collect::<Vec<_>>();
        let checkpoint_id = checkpoint_id(
            &self.run_id,
            &self.envelope_id,
            &self.governing_state_digest,
            self.entries.len(),
            &journal_digest,
        );

        ExecutionCheckpoint {
            checkpoint_id,
            run_id: self.run_id.clone(),
            envelope_id: self.envelope_id.clone(),
            governing_state_digest: self.governing_state_digest.clone(),
            journal_entry_count: self.entries.len(),
            journal_digest,
            last_operation_id,
            evidence_references,
        }
    }

    pub fn validate_resume(
        &self,
        envelope: &ExecutionEnvelope,
        checkpoint: &ExecutionCheckpoint,
        current_governing_state_digest: &str,
    ) -> ResumeDecision {
        if checkpoint.run_id != self.run_id
            || checkpoint.run_id != *envelope.run_id()
            || checkpoint.envelope_id != self.envelope_id
            || checkpoint.envelope_id != envelope.envelope_id().0
        {
            return ResumeDecision {
                disposition: ResumeDisposition::EnvelopeMismatch,
                diagnostic: Some("checkpoint, journal, and envelope bindings differ".into()),
            };
        }

        if checkpoint.governing_state_digest != current_governing_state_digest
            || envelope.governing_state_digest() != current_governing_state_digest
        {
            return ResumeDecision {
                disposition: ResumeDisposition::GoverningStateDrift,
                diagnostic: Some(format!(
                    "checkpoint is bound to governing state {:?}, current state is {:?}",
                    checkpoint.governing_state_digest, current_governing_state_digest
                )),
            };
        }

        if checkpoint.journal_entry_count > self.entries.len()
            || checkpoint.journal_digest != self.journal_digest(checkpoint.journal_entry_count)
        {
            return ResumeDecision {
                disposition: ResumeDisposition::HistoryMismatch,
                diagnostic: Some(
                    "checkpoint operation/evidence history does not match journal".into(),
                ),
            };
        }

        ResumeDecision {
            disposition: ResumeDisposition::Allowed,
            diagnostic: None,
        }
    }

    fn validate_binding(
        &self,
        envelope: &ExecutionEnvelope,
        request: &OperationRequest,
    ) -> Result<(), RuntimeOperationError> {
        if self.run_id != *envelope.run_id() || self.run_id != request.run_id {
            return Err(RuntimeOperationError::RunBindingMismatch);
        }

        if self.envelope_id != envelope.envelope_id().0 || self.envelope_id != request.envelope_id.0
        {
            return Err(RuntimeOperationError::EnvelopeBindingMismatch);
        }

        Ok(())
    }

    fn record(&mut self, request: &OperationRequest, outcome: &MediatedOperationResult) {
        let entry = OperationJournalEntry {
            operation_id: request.operation_id.clone(),
            idempotency_key: request.idempotency_key.clone(),
            material: OperationMaterial::from(request),
            disposition: outcome.result.disposition.clone(),
            evidence_reference: outcome.result.evidence_reference.clone(),
            result_digest: outcome.result.result_digest.clone(),
            diagnostic: outcome.result.diagnostic.clone(),
        };
        let index = self.entries.len();
        let replay_sensitive = matches!(
            entry.disposition,
            OperationDisposition::ExecutedSuccess
                | OperationDisposition::ExecutedFailure
                | OperationDisposition::ToolFailure
                | OperationDisposition::Indeterminate
        );

        if replay_sensitive {
            self.effectful_operation_index
                .insert(entry.operation_id.clone(), index);
            if let Some(key) = &entry.idempotency_key {
                self.idempotency_index.insert(key.clone(), index);
            }
        }

        self.entries.push(entry);
    }

    fn journal_digest(&self, count: usize) -> String {
        let mut digest = Sha256::new();
        write_string(&mut digest, JOURNAL_DIGEST_DOMAIN);
        write_string(&mut digest, &self.run_id.0);
        write_string(&mut digest, &self.envelope_id);
        write_string(&mut digest, &self.governing_state_digest);
        digest.update((count as u64).to_be_bytes());

        for entry in self.entries.iter().take(count) {
            write_string(&mut digest, &entry.operation_id.0);
            write_optional_string(&mut digest, entry.idempotency_key.as_deref());
            write_string(&mut digest, &entry.material.run_id);
            write_string(&mut digest, &entry.material.envelope_id);
            write_string(&mut digest, &entry.material.executor_actor_id);
            write_string(&mut digest, &entry.material.capability);
            write_string(&mut digest, &entry.material.tool);
            write_string(&mut digest, &entry.material.operation_type);
            write_string(&mut digest, &entry.material.target_scope);
            write_string(&mut digest, &entry.material.parameters_digest);
            write_optional_string(&mut digest, entry.material.causal_parent.as_deref());
            write_string(&mut digest, disposition_name(&entry.disposition));
            write_optional_string(&mut digest, entry.evidence_reference.as_deref());
            write_optional_string(&mut digest, entry.result_digest.as_deref());
            write_optional_string(&mut digest, entry.diagnostic.as_deref());
        }

        hex_digest(digest.finalize().as_slice())
    }
}

fn result_from_entry(entry: &OperationJournalEntry) -> OperationResult {
    OperationResult {
        operation_id: entry.operation_id.clone(),
        disposition: entry.disposition.clone(),
        evidence_reference: entry.evidence_reference.clone(),
        result_digest: entry.result_digest.clone(),
        diagnostic: entry.diagnostic.clone(),
    }
}

fn checkpoint_id(
    run_id: &RunId,
    envelope_id: &str,
    governing_state_digest: &str,
    journal_entry_count: usize,
    journal_digest: &str,
) -> String {
    let mut digest = Sha256::new();
    write_string(&mut digest, CHECKPOINT_DIGEST_DOMAIN);
    write_string(&mut digest, &run_id.0);
    write_string(&mut digest, envelope_id);
    write_string(&mut digest, governing_state_digest);
    digest.update((journal_entry_count as u64).to_be_bytes());
    write_string(&mut digest, journal_digest);
    format!("checkpoint-v1-{}", hex_digest(digest.finalize().as_slice()))
}

fn disposition_name(disposition: &OperationDisposition) -> &'static str {
    match disposition {
        OperationDisposition::ExecutedSuccess => "executed_success",
        OperationDisposition::ExecutedFailure => "executed_failure",
        OperationDisposition::DeniedPolicy => "denied_policy",
        OperationDisposition::DeniedCapability => "denied_capability",
        OperationDisposition::DeniedScope => "denied_scope",
        OperationDisposition::WaitingApproval => "waiting_approval",
        OperationDisposition::StaleEnvelope => "stale_envelope",
        OperationDisposition::Cancelled => "cancelled",
        OperationDisposition::ToolFailure => "tool_failure",
        OperationDisposition::Indeterminate => "indeterminate",
    }
}

fn write_string(digest: &mut Sha256, value: &str) {
    digest.update((value.len() as u64).to_be_bytes());
    digest.update(value.as_bytes());
}

fn write_optional_string(digest: &mut Sha256, value: Option<&str>) {
    match value {
        Some(value) => {
            digest.update([1]);
            write_string(digest, value);
        }
        None => digest.update([0]),
    }
}

fn hex_digest(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut output = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        output.push(HEX[(byte >> 4) as usize] as char);
        output.push(HEX[(byte & 0x0f) as usize] as char);
    }
    output
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use crate::{
        harness::{
            ActorIdentity, CapabilityGrant, ExecutionEnvelopeDraft, OperationId, OperationRequest,
            RunState, compile_execution_envelope,
        },
        harness_gateway::{BackendExecution, OperationBackend, PolicyDecision},
    };

    #[derive(Default)]
    struct CountingBackend {
        calls: usize,
    }

    impl OperationBackend for CountingBackend {
        fn execute(&mut self, request: &OperationRequest) -> BackendExecution {
            self.calls += 1;
            BackendExecution::Success {
                result_digest: Some(format!("result:{}", request.parameters_digest)),
                evidence_reference: Some(format!("evidence:{}", request.operation_id.0)),
            }
        }
    }

    fn envelope() -> ExecutionEnvelope {
        compile_execution_envelope(ExecutionEnvelopeDraft {
            schema_version: "0.1.0".into(),
            run_id: RunId("run-runtime-0001".into()),
            logical_time: "2026-09-01T12:00:00Z".into(),
            work_subject: "WP-HARNESS-C1-RUNTIME".into(),
            intent: "preserve execution history across retry and resume".into(),
            requested_outcome: "deterministic run journal".into(),
            governing_state_digest: "state-runtime".into(),
            governed_references: vec![],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new("adapter:test", "executor"),
            granted_capabilities: vec![CapabilityGrant::new(
                "workspace.write",
                "workspace/output.txt",
            )],
            prohibited_capabilities: vec![],
            allowed_tools: vec!["workspace".into()],
            environment_constraints: vec![],
            acceptance_criteria: vec![],
            verification_obligations: vec![],
            approval_gates: vec![],
            escalation_conditions: vec![],
            completion_criteria: vec![],
            resource_limits: BTreeMap::new(),
        })
    }

    fn request(envelope: &ExecutionEnvelope, operation_id: &str) -> OperationRequest {
        OperationRequest {
            operation_id: OperationId(operation_id.into()),
            run_id: envelope.run_id().clone(),
            envelope_id: envelope.envelope_id().clone(),
            executor_actor_id: envelope.executor().actor_id.clone(),
            capability: "workspace.write".into(),
            tool: "workspace".into(),
            operation_type: "write_text".into(),
            target_scope: "workspace/output.txt".into(),
            parameters_digest: "params-write-v1".into(),
            causal_parent: None,
            idempotency_key: Some("write-output-v1".into()),
        }
    }

    fn context() -> OperationGovernanceContext {
        OperationGovernanceContext {
            current_governing_state_digest: "state-runtime".into(),
            run_state: RunState::Running,
            policy: PolicyDecision::Allow,
            approved_gates: vec![],
        }
    }

    #[test]
    fn geh_cf_018_checkpoint_resume_preserves_history() {
        let envelope = envelope();
        let mut journal = GovernedRunJournal::new(&envelope);
        let mut backend = CountingBackend::default();
        let request = request(&envelope, "op-runtime-1");

        journal
            .mediate(
                &envelope,
                &request,
                &context(),
                ReplayPolicy::NonIdempotent,
                &mut backend,
            )
            .expect("first operation is mediated");
        let checkpoint = journal.checkpoint();
        let resume = journal.validate_resume(&envelope, &checkpoint, "state-runtime");

        assert_eq!(resume.disposition, ResumeDisposition::Allowed);
        assert_eq!(checkpoint.journal_entry_count, 1);
        assert_eq!(checkpoint.last_operation_id, Some(request.operation_id));
        assert_eq!(checkpoint.evidence_references.len(), 1);
        assert_eq!(backend.calls, 1);
    }

    #[test]
    fn geh_cf_019_authority_drift_blocks_resume() {
        let envelope = envelope();
        let journal = GovernedRunJournal::new(&envelope);
        let checkpoint = journal.checkpoint();

        let resume = journal.validate_resume(&envelope, &checkpoint, "state-runtime-changed");

        assert_eq!(resume.disposition, ResumeDisposition::GoverningStateDrift);
    }

    #[test]
    fn geh_cf_020_non_idempotent_retry_is_suppressed() {
        let envelope = envelope();
        let mut journal = GovernedRunJournal::new(&envelope);
        let mut backend = CountingBackend::default();
        let first = request(&envelope, "op-runtime-1");
        let retry = request(&envelope, "op-runtime-2");

        journal
            .mediate(
                &envelope,
                &first,
                &context(),
                ReplayPolicy::NonIdempotent,
                &mut backend,
            )
            .expect("first operation executes");
        let retry_outcome = journal
            .mediate(
                &envelope,
                &retry,
                &context(),
                ReplayPolicy::NonIdempotent,
                &mut backend,
            )
            .expect("matching retry is safely classified");

        assert!(matches!(
            retry_outcome,
            RuntimeOperationOutcome::ReplaySuppressed { .. }
        ));
        assert_eq!(backend.calls, 1);
    }

    #[test]
    fn non_idempotent_operation_requires_replay_identity() {
        let envelope = envelope();
        let mut journal = GovernedRunJournal::new(&envelope);
        let mut backend = CountingBackend::default();
        let mut request = request(&envelope, "op-runtime-no-key");
        request.idempotency_key = None;

        let error = journal
            .mediate(
                &envelope,
                &request,
                &context(),
                ReplayPolicy::NonIdempotent,
                &mut backend,
            )
            .expect_err("non-idempotent operation without key must fail closed");

        assert_eq!(error, RuntimeOperationError::MissingIdempotencyKey);
        assert_eq!(backend.calls, 0);
    }

    #[test]
    fn reused_idempotency_key_with_changed_material_is_conflict() {
        let envelope = envelope();
        let mut journal = GovernedRunJournal::new(&envelope);
        let mut backend = CountingBackend::default();
        let first = request(&envelope, "op-runtime-1");
        let mut conflicting = request(&envelope, "op-runtime-2");
        conflicting.parameters_digest = "different-parameters".into();

        journal
            .mediate(
                &envelope,
                &first,
                &context(),
                ReplayPolicy::NonIdempotent,
                &mut backend,
            )
            .expect("first operation executes");
        let error = journal
            .mediate(
                &envelope,
                &conflicting,
                &context(),
                ReplayPolicy::NonIdempotent,
                &mut backend,
            )
            .expect_err("idempotency key cannot be reused for changed material");

        assert!(matches!(
            error,
            RuntimeOperationError::ReplayConflict { .. }
        ));
        assert_eq!(backend.calls, 1);
    }

    #[test]
    fn checkpoint_history_mismatch_blocks_resume() {
        let envelope = envelope();
        let mut journal = GovernedRunJournal::new(&envelope);
        let checkpoint = journal.checkpoint();
        let mut backend = CountingBackend::default();
        let request = request(&envelope, "op-after-checkpoint");

        journal
            .mediate(
                &envelope,
                &request,
                &context(),
                ReplayPolicy::NonIdempotent,
                &mut backend,
            )
            .expect("operation after checkpoint executes");

        let resume = journal.validate_resume(&envelope, &checkpoint, "state-runtime");

        assert_eq!(resume.disposition, ResumeDisposition::Allowed);
        assert_eq!(checkpoint.journal_entry_count, 0);
    }
}
