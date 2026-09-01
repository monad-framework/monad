//! Deterministic, side-effect-free contracts for governed execution.
//!
//! This module deliberately defines the stable Monad side of the harness
//! boundary without prescribing an executor's internal planning or reasoning
//! strategy. Effectful tool execution, policy evaluation, and adapter
//! transports are layered on top of these contracts.

use std::collections::BTreeMap;

use serde::Serialize;
use sha2::{Digest, Sha256};

const ENVELOPE_DIGEST_DOMAIN: &str = "monad.execution-envelope.v1";

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(transparent)]
pub struct EnvelopeId(pub String);

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(transparent)]
pub struct EnvelopeDigest(pub String);

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(transparent)]
pub struct RunId(pub String);

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(transparent)]
pub struct OperationId(pub String);

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct GovernedReference {
    pub kind: String,
    pub identifier: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub content_digest: Option<String>,
}

impl GovernedReference {
    pub fn new(kind: impl Into<String>, identifier: impl Into<String>) -> Self {
        Self {
            kind: kind.into(),
            identifier: identifier.into(),
            content_digest: None,
        }
    }

    pub fn with_content_digest(mut self, digest: impl Into<String>) -> Self {
        self.content_digest = Some(digest.into());
        self
    }
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct ActorIdentity {
    pub actor_id: String,
    pub role: String,
}

impl ActorIdentity {
    pub fn new(actor_id: impl Into<String>, role: impl Into<String>) -> Self {
        Self {
            actor_id: actor_id.into(),
            role: role.into(),
        }
    }
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct CapabilityGrant {
    pub capability: String,
    pub scope: String,
}

impl CapabilityGrant {
    pub fn new(capability: impl Into<String>, scope: impl Into<String>) -> Self {
        Self {
            capability: capability.into(),
            scope: scope.into(),
        }
    }
}

/// Runtime binding between an execution run and an immutable envelope.
///
/// Run identity and binding time are deliberately excluded from envelope
/// identity. Multiple runs may therefore consume the same governed contract
/// without manufacturing different content identities for equivalent
/// governance semantics.
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ExecutionRunBinding {
    pub run_id: RunId,
    pub envelope_id: EnvelopeId,
    pub bound_at: String,
}

impl ExecutionRunBinding {
    pub fn new(run_id: RunId, envelope_id: EnvelopeId, bound_at: impl Into<String>) -> Self {
        Self {
            run_id,
            envelope_id,
            bound_at: bound_at.into(),
        }
    }
}

/// Mutable input used only while compiling a governed execution envelope.
///
/// Compilation normalizes set-like collections and derives a deterministic
/// digest. The returned [`ExecutionEnvelope`] is the immutable governed
/// semantic contract that may then be bound to one or more execution runs.
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ExecutionEnvelopeDraft {
    pub schema_version: String,
    pub work_subject: String,
    pub intent: String,
    pub requested_outcome: String,
    pub scope_boundaries: Vec<String>,
    pub dependencies: Vec<GovernedReference>,
    pub governing_state_digest: String,
    pub governed_references: Vec<GovernedReference>,
    pub initiating_actor: ActorIdentity,
    pub executor: ActorIdentity,
    pub granted_capabilities: Vec<CapabilityGrant>,
    pub prohibited_capabilities: Vec<CapabilityGrant>,
    pub delegation_constraints: Vec<String>,
    pub allowed_tools: Vec<String>,
    pub environment_constraints: Vec<String>,
    pub acceptance_criteria: Vec<String>,
    pub verification_obligations: Vec<String>,
    pub evidence_obligations: Vec<String>,
    pub approval_gates: Vec<String>,
    pub escalation_conditions: Vec<String>,
    pub completion_criteria: Vec<String>,
    pub resource_limits: BTreeMap<String, String>,
}

/// Canonical, normalized governed work contract supplied to an executor.
///
/// Fields are private so a compiled envelope cannot be mutated directly by a
/// caller. A material governing-state or obligation change must produce a
/// newly compiled envelope rather than modifying this value in place.
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ExecutionEnvelope {
    envelope_id: EnvelopeId,
    envelope_digest: EnvelopeDigest,
    schema_version: String,
    work_subject: String,
    intent: String,
    requested_outcome: String,
    scope_boundaries: Vec<String>,
    dependencies: Vec<GovernedReference>,
    governing_state_digest: String,
    governed_references: Vec<GovernedReference>,
    initiating_actor: ActorIdentity,
    executor: ActorIdentity,
    granted_capabilities: Vec<CapabilityGrant>,
    prohibited_capabilities: Vec<CapabilityGrant>,
    delegation_constraints: Vec<String>,
    allowed_tools: Vec<String>,
    environment_constraints: Vec<String>,
    acceptance_criteria: Vec<String>,
    verification_obligations: Vec<String>,
    evidence_obligations: Vec<String>,
    approval_gates: Vec<String>,
    escalation_conditions: Vec<String>,
    completion_criteria: Vec<String>,
    resource_limits: BTreeMap<String, String>,
}

impl ExecutionEnvelope {
    pub fn envelope_id(&self) -> &EnvelopeId {
        &self.envelope_id
    }

    pub fn envelope_digest(&self) -> &EnvelopeDigest {
        &self.envelope_digest
    }

    pub fn schema_version(&self) -> &str {
        &self.schema_version
    }

    pub fn work_subject(&self) -> &str {
        &self.work_subject
    }

    pub fn intent(&self) -> &str {
        &self.intent
    }

    pub fn requested_outcome(&self) -> &str {
        &self.requested_outcome
    }

    pub fn scope_boundaries(&self) -> &[String] {
        &self.scope_boundaries
    }

    pub fn dependencies(&self) -> &[GovernedReference] {
        &self.dependencies
    }

    pub fn governing_state_digest(&self) -> &str {
        &self.governing_state_digest
    }

    pub fn governed_references(&self) -> &[GovernedReference] {
        &self.governed_references
    }

    pub fn initiating_actor(&self) -> &ActorIdentity {
        &self.initiating_actor
    }

    pub fn executor(&self) -> &ActorIdentity {
        &self.executor
    }

    pub fn granted_capabilities(&self) -> &[CapabilityGrant] {
        &self.granted_capabilities
    }

    pub fn prohibited_capabilities(&self) -> &[CapabilityGrant] {
        &self.prohibited_capabilities
    }

    pub fn delegation_constraints(&self) -> &[String] {
        &self.delegation_constraints
    }

    pub fn allowed_tools(&self) -> &[String] {
        &self.allowed_tools
    }

    pub fn environment_constraints(&self) -> &[String] {
        &self.environment_constraints
    }

    pub fn acceptance_criteria(&self) -> &[String] {
        &self.acceptance_criteria
    }

    pub fn verification_obligations(&self) -> &[String] {
        &self.verification_obligations
    }

    pub fn evidence_obligations(&self) -> &[String] {
        &self.evidence_obligations
    }

    pub fn approval_gates(&self) -> &[String] {
        &self.approval_gates
    }

    pub fn escalation_conditions(&self) -> &[String] {
        &self.escalation_conditions
    }

    pub fn completion_criteria(&self) -> &[String] {
        &self.completion_criteria
    }

    pub fn resource_limits(&self) -> &BTreeMap<String, String> {
        &self.resource_limits
    }
}

/// Compile a normalized, content-addressed execution envelope.
///
/// This function performs no I/O. Callers are responsible for resolving
/// authoritative governance inputs before constructing the draft.
pub fn compile_execution_envelope(mut draft: ExecutionEnvelopeDraft) -> ExecutionEnvelope {
    normalize(&mut draft.scope_boundaries);
    normalize(&mut draft.dependencies);
    normalize(&mut draft.governed_references);
    normalize(&mut draft.granted_capabilities);
    normalize(&mut draft.prohibited_capabilities);
    normalize(&mut draft.delegation_constraints);
    normalize(&mut draft.allowed_tools);
    normalize(&mut draft.environment_constraints);
    normalize(&mut draft.acceptance_criteria);
    normalize(&mut draft.verification_obligations);
    normalize(&mut draft.evidence_obligations);
    normalize(&mut draft.approval_gates);
    normalize(&mut draft.escalation_conditions);
    normalize(&mut draft.completion_criteria);

    let digest = digest_draft(&draft);
    let envelope_id = EnvelopeId(format!("env-v1-{digest}"));

    ExecutionEnvelope {
        envelope_id,
        envelope_digest: EnvelopeDigest(digest),
        schema_version: draft.schema_version,
        work_subject: draft.work_subject,
        intent: draft.intent,
        requested_outcome: draft.requested_outcome,
        scope_boundaries: draft.scope_boundaries,
        dependencies: draft.dependencies,
        governing_state_digest: draft.governing_state_digest,
        governed_references: draft.governed_references,
        initiating_actor: draft.initiating_actor,
        executor: draft.executor,
        granted_capabilities: draft.granted_capabilities,
        prohibited_capabilities: draft.prohibited_capabilities,
        delegation_constraints: draft.delegation_constraints,
        allowed_tools: draft.allowed_tools,
        environment_constraints: draft.environment_constraints,
        acceptance_criteria: draft.acceptance_criteria,
        verification_obligations: draft.verification_obligations,
        evidence_obligations: draft.evidence_obligations,
        approval_gates: draft.approval_gates,
        escalation_conditions: draft.escalation_conditions,
        completion_criteria: draft.completion_criteria,
        resource_limits: draft.resource_limits,
    }
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum RunState {
    Requested,
    Compiling,
    Ready,
    Running,
    WaitingApproval,
    WaitingInput,
    Verifying,
    Suspended,
    Failed,
    Cancelled,
    Completed,
}

impl RunState {
    pub fn is_terminal(&self) -> bool {
        matches!(self, Self::Failed | Self::Cancelled | Self::Completed)
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct OperationRequest {
    pub operation_id: OperationId,
    pub run_id: RunId,
    pub envelope_id: EnvelopeId,
    pub executor_actor_id: String,
    pub capability: String,
    pub tool: String,
    pub operation_type: String,
    pub target_scope: String,
    pub parameters_digest: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub causal_parent: Option<OperationId>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub idempotency_key: Option<String>,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum OperationDisposition {
    ExecutedSuccess,
    ExecutedFailure,
    DeniedPolicy,
    DeniedCapability,
    DeniedScope,
    WaitingApproval,
    StaleEnvelope,
    Cancelled,
    ToolFailure,
    Indeterminate,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct OperationResult {
    pub operation_id: OperationId,
    pub disposition: OperationDisposition,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub evidence_reference: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub result_digest: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub diagnostic: Option<String>,
}

fn normalize<T: Ord>(values: &mut Vec<T>) {
    values.sort();
    values.dedup();
}

fn digest_draft(draft: &ExecutionEnvelopeDraft) -> String {
    let mut writer = DigestWriter::new(ENVELOPE_DIGEST_DOMAIN);
    writer.string(&draft.schema_version);
    writer.string(&draft.work_subject);
    writer.string(&draft.intent);
    writer.string(&draft.requested_outcome);
    writer.strings(&draft.scope_boundaries);
    writer.references(&draft.dependencies);
    writer.string(&draft.governing_state_digest);
    writer.references(&draft.governed_references);

    writer.string(&draft.initiating_actor.actor_id);
    writer.string(&draft.initiating_actor.role);
    writer.string(&draft.executor.actor_id);
    writer.string(&draft.executor.role);

    writer.capabilities(&draft.granted_capabilities);
    writer.capabilities(&draft.prohibited_capabilities);
    writer.strings(&draft.delegation_constraints);
    writer.strings(&draft.allowed_tools);
    writer.strings(&draft.environment_constraints);
    writer.strings(&draft.acceptance_criteria);
    writer.strings(&draft.verification_obligations);
    writer.strings(&draft.evidence_obligations);
    writer.strings(&draft.approval_gates);
    writer.strings(&draft.escalation_conditions);
    writer.strings(&draft.completion_criteria);

    writer.usize(draft.resource_limits.len());
    for (key, value) in &draft.resource_limits {
        writer.string(key);
        writer.string(value);
    }

    writer.finish()
}

struct DigestWriter(Sha256);

impl DigestWriter {
    fn new(domain: &str) -> Self {
        let mut writer = Self(Sha256::new());
        writer.string(domain);
        writer
    }

    fn usize(&mut self, value: usize) {
        self.0.update((value as u64).to_be_bytes());
    }

    fn string(&mut self, value: &str) {
        self.0.update((value.len() as u64).to_be_bytes());
        self.0.update(value.as_bytes());
    }

    fn optional_string(&mut self, value: Option<&str>) {
        match value {
            Some(value) => {
                self.0.update([1]);
                self.string(value);
            }
            None => self.0.update([0]),
        }
    }

    fn strings(&mut self, values: &[String]) {
        self.usize(values.len());
        for value in values {
            self.string(value);
        }
    }

    fn references(&mut self, values: &[GovernedReference]) {
        self.usize(values.len());
        for value in values {
            self.string(&value.kind);
            self.string(&value.identifier);
            self.optional_string(value.content_digest.as_deref());
        }
    }

    fn capabilities(&mut self, values: &[CapabilityGrant]) {
        self.usize(values.len());
        for value in values {
            self.string(&value.capability);
            self.string(&value.scope);
        }
    }

    fn finish(self) -> String {
        hex_digest(self.0.finalize().as_slice())
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
    use super::*;

    fn draft() -> ExecutionEnvelopeDraft {
        ExecutionEnvelopeDraft {
            schema_version: "0.1.0".into(),
            work_subject: "WP-HARNESS-0001".into(),
            intent: "compile governed work into an execution envelope".into(),
            requested_outcome: "deterministic inspectable envelope".into(),
            scope_boundaries: vec!["specifications/**".into(), "crates/monad-core/**".into()],
            dependencies: vec![GovernedReference::new("adr", "ADR-0007")],
            governing_state_digest: "state-sha256-example".into(),
            governed_references: vec![
                GovernedReference::new("spec", "TECH-HARNESS-0001"),
                GovernedReference::new("spec", "DATA-HARNESS-0001"),
            ],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new("adapter:test", "executor"),
            granted_capabilities: vec![
                CapabilityGrant::new("fs.read", "workspace/**"),
                CapabilityGrant::new("fs.write", "crates/monad-core/**"),
            ],
            prohibited_capabilities: vec![CapabilityGrant::new("release.publish", "*")],
            delegation_constraints: vec!["child capabilities must not exceed parent".into()],
            allowed_tools: vec!["filesystem".into(), "test-runner".into()],
            environment_constraints: vec!["local-first".into()],
            acceptance_criteria: vec!["same governed input yields same envelope digest".into()],
            verification_obligations: vec!["cargo test -p monad-core".into()],
            evidence_obligations: vec!["record envelope and verification evidence".into()],
            approval_gates: vec!["human approval before publish".into()],
            escalation_conditions: vec!["governing state becomes stale".into()],
            completion_criteria: vec!["all verification obligations pass".into()],
            resource_limits: BTreeMap::from([("max_operations".into(), "100".into())]),
        }
    }

    #[test]
    fn compilation_is_deterministic_for_set_like_input_order() {
        let left = compile_execution_envelope(draft());
        let mut reordered = draft();
        reordered.allowed_tools.reverse();
        reordered.allowed_tools.push("filesystem".into());
        reordered.scope_boundaries.reverse();
        reordered.dependencies.push(GovernedReference::new("adr", "ADR-0007"));
        reordered.governed_references.reverse();
        let right = compile_execution_envelope(reordered);

        assert_eq!(left.envelope_id(), right.envelope_id());
        assert_eq!(left.envelope_digest(), right.envelope_digest());
        assert_eq!(left, right);
    }

    #[test]
    fn digest_algorithm_has_a_stable_golden_value() {
        let envelope = compile_execution_envelope(draft());

        assert_eq!(
            envelope.envelope_digest().0,
            "1172708be2273f289ff07970ff53df4cb9cdc1374ec4a577e69c54a692606f2f"
        );
        assert_eq!(
            envelope.envelope_id().0,
            "env-v1-1172708be2273f289ff07970ff53df4cb9cdc1374ec4a577e69c54a692606f2f"
        );
    }

    #[test]
    fn material_governing_change_changes_envelope_identity() {
        let before = compile_execution_envelope(draft());
        let mut changed = draft();
        changed.governing_state_digest = "different-state".into();
        let after = compile_execution_envelope(changed);

        assert_ne!(before.envelope_id(), after.envelope_id());
        assert_ne!(before.envelope_digest(), after.envelope_digest());
    }

    #[test]
    fn runtime_binding_is_not_part_of_envelope_identity() {
        let envelope = compile_execution_envelope(draft());
        let first = ExecutionRunBinding::new(
            RunId("run-0001".into()),
            envelope.envelope_id().clone(),
            "2026-09-01T12:00:00Z",
        );
        let second = ExecutionRunBinding::new(
            RunId("run-0002".into()),
            envelope.envelope_id().clone(),
            "2026-09-02T12:00:00Z",
        );

        assert_ne!(first.run_id, second.run_id);
        assert_ne!(first.bound_at, second.bound_at);
        assert_eq!(first.envelope_id, second.envelope_id);

        let serialized = serde_json::to_value(envelope).expect("serialize envelope");
        assert!(serialized.get("run_id").is_none());
        assert!(serialized.get("bound_at").is_none());
    }

    #[test]
    fn terminal_state_is_explicit() {
        assert!(RunState::Completed.is_terminal());
        assert!(RunState::Cancelled.is_terminal());
        assert!(RunState::Failed.is_terminal());
        assert!(!RunState::Verifying.is_terminal());
        assert!(!RunState::Running.is_terminal());
    }

    #[test]
    fn envelope_serialization_tracks_declared_schema_surface() {
        let envelope = compile_execution_envelope(draft());
        let value = serde_json::to_value(envelope).expect("serialize envelope");
        let schema: serde_json::Value = serde_json::from_str(include_str!(
            "../../../schemas/execution-envelope.schema.json"
        ))
        .expect("parse execution envelope schema");

        assert_eq!(value["schema_version"], "0.1.0");
        assert_eq!(value["work_subject"], "WP-HARNESS-0001");
        assert!(value["envelope_digest"].as_str().is_some());
        assert!(value["granted_capabilities"].is_array());
        assert!(value["evidence_obligations"].is_array());

        let required = schema["required"].as_array().expect("schema required array");
        for required_key in required {
            let required_key = required_key.as_str().expect("required key string");
            assert!(
                value.get(required_key).is_some(),
                "serialized envelope is missing required schema field {required_key}"
            );
        }

        let properties = schema["properties"]
            .as_object()
            .expect("schema properties object");
        for serialized_key in value
            .as_object()
            .expect("serialized envelope object")
            .keys()
        {
            assert!(
                properties.contains_key(serialized_key),
                "serialized envelope field {serialized_key} is absent from schema"
            );
        }

        assert_eq!(schema["properties"]["schema_version"]["const"], "0.1.0");
        assert_eq!(
            value["envelope_id"],
            format!("env-v1-{}", value["envelope_digest"].as_str().unwrap())
        );
    }
}
