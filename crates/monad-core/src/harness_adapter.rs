//! Transport-neutral C2 adapter session and protocol semantics for governed execution.
//!
//! This module implements the Monad-owned side of IFC-HARNESS-0001 without
//! prescribing a provider SDK or executor cognition strategy. Adapter sessions
//! negotiate compatibility, remain bound to one immutable execution envelope,
//! preserve protocol errors separately from governed operation outcomes, and
//! reuse C1 runtime/verification authorities for resume and completion.

use serde::Serialize;

use crate::{
    harness::{
        EnvelopeId, ExecutionEnvelope, OperationRequest, OperationResult, RunId,
    },
    harness_gateway::{
        MediatedOperationResult, OperationBackend, OperationGovernanceContext, mediate_operation,
    },
    harness_runtime::{ExecutionCheckpoint, GovernedRunJournal, ResumeDisposition},
    harness_verification::{
        CompletionAssessment, VerificationEvidenceBundle, assess_completion,
    },
    harness_workspace_read::WorkspaceTextObservation,
};

pub const ADAPTER_INTERFACE_VERSION: &str = "0.1.0";

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(transparent)]
pub struct AdapterSessionId(pub String);

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum AdapterFeature {
    CheckpointResume,
    Cancellation,
    Streaming,
    Delegation,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct AdapterExtensionSupport {
    pub namespace: String,
    pub versions: Vec<String>,
}

impl AdapterExtensionSupport {
    pub fn new(namespace: impl Into<String>, versions: Vec<String>) -> Self {
        Self {
            namespace: namespace.into(),
            versions,
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct AdapterDescriptor {
    pub adapter_id: String,
    pub adapter_version: String,
    pub harness_family: String,
    pub supported_interface_versions: Vec<String>,
    pub supported_envelope_versions: Vec<String>,
    pub supported_transport_modes: Vec<String>,
    pub supported_features: Vec<AdapterFeature>,
    pub extensions: Vec<AdapterExtensionSupport>,
    pub limitations: Vec<String>,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct AdapterExtensionRequirement {
    pub namespace: String,
    pub version: String,
}

impl AdapterExtensionRequirement {
    pub fn new(namespace: impl Into<String>, version: impl Into<String>) -> Self {
        Self {
            namespace: namespace.into(),
            version: version.into(),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct AdapterInitializationRequest {
    pub session_id: AdapterSessionId,
    pub run_id: RunId,
    pub envelope_id: EnvelopeId,
    pub interface_version: String,
    pub transport_mode: String,
    pub required_features: Vec<AdapterFeature>,
    pub mandatory_extensions: Vec<AdapterExtensionRequirement>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum AdapterInitializationRejection {
    InvalidSessionId,
    RunBindingMismatch,
    EnvelopeBindingMismatch,
    UnsupportedInterfaceVersion { requested: String },
    UnsupportedEnvelopeVersion { requested: String },
    UnsupportedTransportMode { requested: String },
    MissingMandatoryFeature { feature: AdapterFeature },
    MissingMandatoryExtension { namespace: String, version: String },
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum AdapterSessionState {
    Active,
    Disconnected,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct AdapterSession {
    session_id: AdapterSessionId,
    adapter_id: String,
    adapter_version: String,
    harness_family: String,
    run_id: RunId,
    envelope_id: EnvelopeId,
    interface_version: String,
    envelope_version: String,
    transport_mode: String,
    supported_features: Vec<AdapterFeature>,
    negotiated_extensions: Vec<AdapterExtensionRequirement>,
    state: AdapterSessionState,
}

impl AdapterSession {
    pub fn session_id(&self) -> &AdapterSessionId {
        &self.session_id
    }

    pub fn adapter_id(&self) -> &str {
        &self.adapter_id
    }

    pub fn adapter_version(&self) -> &str {
        &self.adapter_version
    }

    pub fn harness_family(&self) -> &str {
        &self.harness_family
    }

    pub fn run_id(&self) -> &RunId {
        &self.run_id
    }

    pub fn envelope_id(&self) -> &EnvelopeId {
        &self.envelope_id
    }

    pub fn interface_version(&self) -> &str {
        &self.interface_version
    }

    pub fn envelope_version(&self) -> &str {
        &self.envelope_version
    }

    pub fn transport_mode(&self) -> &str {
        &self.transport_mode
    }

    pub fn supported_features(&self) -> &[AdapterFeature] {
        &self.supported_features
    }

    pub fn negotiated_extensions(&self) -> &[AdapterExtensionRequirement] {
        &self.negotiated_extensions
    }

    pub fn state(&self) -> &AdapterSessionState {
        &self.state
    }

    pub fn disconnect(&mut self) {
        self.state = AdapterSessionState::Disconnected;
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum AdapterInitializationOutcome {
    Accepted(AdapterSession),
    Rejected(AdapterInitializationRejection),
}

/// Negotiate and bind an adapter session to one immutable execution envelope.
///
/// The requested interface/envelope/transport semantics are exact in v0.1.0.
/// Unsupported mandatory features or extensions fail initialization explicitly;
/// absence never means unconstrained execution.
pub fn initialize_adapter(
    descriptor: &AdapterDescriptor,
    envelope: &ExecutionEnvelope,
    mut request: AdapterInitializationRequest,
) -> AdapterInitializationOutcome {
    if request.session_id.0.trim().is_empty() {
        return AdapterInitializationOutcome::Rejected(
            AdapterInitializationRejection::InvalidSessionId,
        );
    }
    if request.run_id != *envelope.run_id() {
        return AdapterInitializationOutcome::Rejected(
            AdapterInitializationRejection::RunBindingMismatch,
        );
    }
    if request.envelope_id != *envelope.envelope_id() {
        return AdapterInitializationOutcome::Rejected(
            AdapterInitializationRejection::EnvelopeBindingMismatch,
        );
    }
    if !descriptor
        .supported_interface_versions
        .iter()
        .any(|version| version == &request.interface_version)
    {
        return AdapterInitializationOutcome::Rejected(
            AdapterInitializationRejection::UnsupportedInterfaceVersion {
                requested: request.interface_version,
            },
        );
    }
    if !descriptor
        .supported_envelope_versions
        .iter()
        .any(|version| version == envelope.schema_version())
    {
        return AdapterInitializationOutcome::Rejected(
            AdapterInitializationRejection::UnsupportedEnvelopeVersion {
                requested: envelope.schema_version().to_owned(),
            },
        );
    }
    if !descriptor
        .supported_transport_modes
        .iter()
        .any(|mode| mode == &request.transport_mode)
    {
        return AdapterInitializationOutcome::Rejected(
            AdapterInitializationRejection::UnsupportedTransportMode {
                requested: request.transport_mode,
            },
        );
    }

    request.required_features.sort();
    request.required_features.dedup();
    for feature in &request.required_features {
        if !descriptor.supported_features.contains(feature) {
            return AdapterInitializationOutcome::Rejected(
                AdapterInitializationRejection::MissingMandatoryFeature {
                    feature: feature.clone(),
                },
            );
        }
    }

    request.mandatory_extensions.sort();
    request.mandatory_extensions.dedup();
    for extension in &request.mandatory_extensions {
        let supported = descriptor.extensions.iter().any(|available| {
            available.namespace == extension.namespace
                && available
                    .versions
                    .iter()
                    .any(|version| version == &extension.version)
        });
        if !supported {
            return AdapterInitializationOutcome::Rejected(
                AdapterInitializationRejection::MissingMandatoryExtension {
                    namespace: extension.namespace.clone(),
                    version: extension.version.clone(),
                },
            );
        }
    }

    let mut supported_features = descriptor.supported_features.clone();
    supported_features.sort();
    supported_features.dedup();

    AdapterInitializationOutcome::Accepted(AdapterSession {
        session_id: request.session_id,
        adapter_id: descriptor.adapter_id.clone(),
        adapter_version: descriptor.adapter_version.clone(),
        harness_family: descriptor.harness_family.clone(),
        run_id: request.run_id,
        envelope_id: request.envelope_id,
        interface_version: request.interface_version,
        envelope_version: envelope.schema_version().to_owned(),
        transport_mode: request.transport_mode,
        supported_features,
        negotiated_extensions: request.mandatory_extensions,
        state: AdapterSessionState::Active,
    })
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum AdapterObservation {
    Utf8Text {
        resource: String,
        text: String,
        byte_length: u64,
        content_digest: String,
    },
}

impl From<WorkspaceTextObservation> for AdapterObservation {
    fn from(observation: WorkspaceTextObservation) -> Self {
        Self::Utf8Text {
            resource: observation.relative_path,
            text: observation.text,
            byte_length: observation.byte_length,
            content_digest: observation.content_digest,
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct AdapterOperationResponse {
    pub event_id: String,
    pub session_id: AdapterSessionId,
    pub result: OperationResult,
    /// Transient executor-facing tool output. This is transport data, not an
    /// automatic durable evidence record.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub observation: Option<AdapterObservation>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum AdapterProtocolError {
    EventIdRequired,
    SessionNotActive,
    SessionBindingMismatch,
    OperationBindingMismatch,
}

fn validate_active_session(
    session: &AdapterSession,
    envelope: &ExecutionEnvelope,
) -> Result<(), AdapterProtocolError> {
    if session.state != AdapterSessionState::Active {
        return Err(AdapterProtocolError::SessionNotActive);
    }
    if session.run_id != *envelope.run_id() || session.envelope_id != *envelope.envelope_id() {
        return Err(AdapterProtocolError::SessionBindingMismatch);
    }
    Ok(())
}

fn validate_operation_binding(
    session: &AdapterSession,
    request: &OperationRequest,
) -> Result<(), AdapterProtocolError> {
    if request.run_id != session.run_id || request.envelope_id != session.envelope_id {
        return Err(AdapterProtocolError::OperationBindingMismatch);
    }
    Ok(())
}

/// Convert a mediated governed result into an adapter-facing operation result.
///
/// Protocol validation occurs before transport. Governed denials remain normal
/// operation responses and are never collapsed into protocol/tool errors.
pub fn adapter_operation_response(
    session: &AdapterSession,
    envelope: &ExecutionEnvelope,
    event_id: impl Into<String>,
    request: &OperationRequest,
    mediated: MediatedOperationResult,
    observation: Option<AdapterObservation>,
) -> Result<AdapterOperationResponse, AdapterProtocolError> {
    validate_active_session(session, envelope)?;
    validate_operation_binding(session, request)?;
    let event_id = event_id.into();
    if event_id.trim().is_empty() {
        return Err(AdapterProtocolError::EventIdRequired);
    }

    Ok(AdapterOperationResponse {
        event_id,
        session_id: session.session_id.clone(),
        result: mediated.result,
        observation,
    })
}

/// Mediate an adapter operation through the C1 Tool Gateway and return the
/// governed outcome unchanged at the protocol boundary.
pub fn mediate_adapter_operation<B: OperationBackend>(
    session: &AdapterSession,
    envelope: &ExecutionEnvelope,
    event_id: impl Into<String>,
    request: &OperationRequest,
    context: &OperationGovernanceContext,
    backend: &mut B,
) -> Result<AdapterOperationResponse, AdapterProtocolError> {
    validate_active_session(session, envelope)?;
    validate_operation_binding(session, request)?;
    let mediated = mediate_operation(envelope, request, context, backend);
    adapter_operation_response(session, envelope, event_id, request, mediated, None)
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct AdapterCompleteRequest {
    pub event_id: String,
    pub session_id: AdapterSessionId,
    pub run_id: RunId,
    pub envelope_id: EnvelopeId,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct AdapterCompletionResponse {
    pub event_id: String,
    pub session_id: AdapterSessionId,
    pub assessment: CompletionAssessment,
}

/// Treat executor completion as a verification request, never as lifecycle
/// authority. This function does not mutate run or EOS completion state.
pub fn handle_complete_request(
    session: &AdapterSession,
    envelope: &ExecutionEnvelope,
    request: &AdapterCompleteRequest,
    evidence: &VerificationEvidenceBundle,
) -> Result<AdapterCompletionResponse, AdapterProtocolError> {
    validate_active_session(session, envelope)?;
    if request.event_id.trim().is_empty() {
        return Err(AdapterProtocolError::EventIdRequired);
    }
    if request.session_id != session.session_id
        || request.run_id != session.run_id
        || request.envelope_id != session.envelope_id
    {
        return Err(AdapterProtocolError::SessionBindingMismatch);
    }

    Ok(AdapterCompletionResponse {
        event_id: request.event_id.clone(),
        session_id: session.session_id.clone(),
        assessment: assess_completion(envelope, true, evidence),
    })
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum AdapterResumeDisposition {
    Allowed,
    SessionNotDisconnected,
    SessionBindingMismatch,
    UnsupportedFeature,
    RuntimeRejected { disposition: ResumeDisposition },
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct AdapterResumeOutcome {
    pub disposition: AdapterResumeDisposition,
    pub diagnostic: Option<String>,
}

/// Rebind a disconnected adapter only after C1 checkpoint, history, and
/// governing-state validation succeeds.
pub fn resume_adapter_session(
    session: &mut AdapterSession,
    envelope: &ExecutionEnvelope,
    journal: &GovernedRunJournal,
    checkpoint: &ExecutionCheckpoint,
    current_governing_state_digest: &str,
) -> AdapterResumeOutcome {
    if session.state != AdapterSessionState::Disconnected {
        return AdapterResumeOutcome {
            disposition: AdapterResumeDisposition::SessionNotDisconnected,
            diagnostic: Some("adapter session must be disconnected before resume".into()),
        };
    }
    if session.run_id != *envelope.run_id() || session.envelope_id != *envelope.envelope_id() {
        return AdapterResumeOutcome {
            disposition: AdapterResumeDisposition::SessionBindingMismatch,
            diagnostic: Some("adapter session does not match the execution envelope".into()),
        };
    }
    if !session
        .supported_features
        .contains(&AdapterFeature::CheckpointResume)
    {
        return AdapterResumeOutcome {
            disposition: AdapterResumeDisposition::UnsupportedFeature,
            diagnostic: Some("adapter does not support checkpoint/resume".into()),
        };
    }

    let runtime = journal.validate_resume(envelope, checkpoint, current_governing_state_digest);
    if runtime.disposition != ResumeDisposition::Allowed {
        return AdapterResumeOutcome {
            disposition: AdapterResumeDisposition::RuntimeRejected {
                disposition: runtime.disposition,
            },
            diagnostic: runtime.diagnostic,
        };
    }

    session.state = AdapterSessionState::Active;
    AdapterResumeOutcome {
        disposition: AdapterResumeDisposition::Allowed,
        diagnostic: None,
    }
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;
    use crate::{
        harness::{
            ActorIdentity, CapabilityGrant, ExecutionEnvelopeDraft, OperationDisposition,
            OperationId, RunState, compile_execution_envelope,
        },
        harness_gateway::{BackendExecution, OperationGovernanceContext, PolicyDecision},
        harness_verification::CompletionDisposition,
    };

    #[derive(Default)]
    struct RecordingBackend {
        calls: Vec<OperationId>,
        fail: bool,
    }

    impl OperationBackend for RecordingBackend {
        fn execute(&mut self, request: &OperationRequest) -> BackendExecution {
            self.calls.push(request.operation_id.clone());
            if self.fail {
                BackendExecution::ToolFailure {
                    diagnostic: "simulated tool failure".into(),
                }
            } else {
                BackendExecution::Success {
                    result_digest: Some("result-digest".into()),
                    evidence_reference: Some("evidence:operation".into()),
                }
            }
        }
    }

    fn descriptor() -> AdapterDescriptor {
        AdapterDescriptor {
            adapter_id: "adapter:test".into(),
            adapter_version: "1.0.0".into(),
            harness_family: "deterministic-test".into(),
            supported_interface_versions: vec![ADAPTER_INTERFACE_VERSION.into()],
            supported_envelope_versions: vec!["0.1.0".into()],
            supported_transport_modes: vec!["embedded".into()],
            supported_features: vec![
                AdapterFeature::CheckpointResume,
                AdapterFeature::Cancellation,
            ],
            extensions: vec![AdapterExtensionSupport::new(
                "org.monad.test",
                vec!["1.0.0".into()],
            )],
            limitations: vec![],
        }
    }

    fn envelope(grant_read: bool) -> ExecutionEnvelope {
        compile_execution_envelope(ExecutionEnvelopeDraft {
            schema_version: "0.1.0".into(),
            run_id: RunId("run-c2-0001".into()),
            logical_time: "2026-09-01T19:00:00Z".into(),
            work_subject: "WP-HARNESS-C2".into(),
            intent: "validate adapter protocol semantics".into(),
            requested_outcome: "bound transport-neutral adapter session".into(),
            governing_state_digest: "state-c2".into(),
            governed_references: vec![],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new("adapter:test", "executor"),
            granted_capabilities: if grant_read {
                vec![CapabilityGrant::new("workspace.read", "README.md")]
            } else {
                vec![]
            },
            prohibited_capabilities: vec![],
            allowed_tools: vec!["workspace".into()],
            environment_constraints: vec!["local-first".into()],
            acceptance_criteria: vec!["candidate output exists".into()],
            verification_obligations: vec!["verification passes".into()],
            approval_gates: vec![],
            escalation_conditions: vec![],
            completion_criteria: vec!["evidence is attributable".into()],
            resource_limits: BTreeMap::new(),
        })
    }

    fn init_request(envelope: &ExecutionEnvelope) -> AdapterInitializationRequest {
        AdapterInitializationRequest {
            session_id: AdapterSessionId("session-c2-0001".into()),
            run_id: envelope.run_id().clone(),
            envelope_id: envelope.envelope_id().clone(),
            interface_version: ADAPTER_INTERFACE_VERSION.into(),
            transport_mode: "embedded".into(),
            required_features: vec![AdapterFeature::CheckpointResume],
            mandatory_extensions: vec![],
        }
    }

    fn session(envelope: &ExecutionEnvelope) -> AdapterSession {
        match initialize_adapter(&descriptor(), envelope, init_request(envelope)) {
            AdapterInitializationOutcome::Accepted(session) => session,
            AdapterInitializationOutcome::Rejected(reason) => {
                panic!("compatible adapter rejected: {reason:?}")
            }
        }
    }

    fn request(envelope: &ExecutionEnvelope) -> OperationRequest {
        OperationRequest {
            operation_id: OperationId("op-c2-0001".into()),
            run_id: envelope.run_id().clone(),
            envelope_id: envelope.envelope_id().clone(),
            executor_actor_id: envelope.executor().actor_id.clone(),
            capability: "workspace.read".into(),
            tool: "workspace".into(),
            operation_type: "read_text".into(),
            target_scope: "README.md".into(),
            parameters_digest: "parameters-c2".into(),
            causal_parent: None,
            idempotency_key: None,
        }
    }

    fn context(state: RunState) -> OperationGovernanceContext {
        OperationGovernanceContext {
            current_governing_state_digest: "state-c2".into(),
            run_state: state,
            policy: PolicyDecision::Allow,
            approved_gates: vec![],
        }
    }

    #[test]
    fn geh_cf_030_compatible_adapter_initialization_binds_session() {
        let envelope = envelope(true);
        let outcome = initialize_adapter(&descriptor(), &envelope, init_request(&envelope));

        let AdapterInitializationOutcome::Accepted(session) = outcome else {
            panic!("compatible adapter should initialize");
        };
        assert_eq!(session.run_id(), envelope.run_id());
        assert_eq!(session.envelope_id(), envelope.envelope_id());
        assert_eq!(session.interface_version(), ADAPTER_INTERFACE_VERSION);
        assert_eq!(session.state(), &AdapterSessionState::Active);
    }

    #[test]
    fn geh_cf_031_missing_mandatory_feature_rejects_initialization() {
        let envelope = envelope(true);
        let mut descriptor = descriptor();
        descriptor
            .supported_features
            .retain(|feature| feature != &AdapterFeature::CheckpointResume);

        let outcome = initialize_adapter(&descriptor, &envelope, init_request(&envelope));

        assert_eq!(
            outcome,
            AdapterInitializationOutcome::Rejected(
                AdapterInitializationRejection::MissingMandatoryFeature {
                    feature: AdapterFeature::CheckpointResume,
                }
            )
        );
    }

    #[test]
    fn geh_cf_032_governed_denial_is_distinct_from_tool_failure() {
        let denied_envelope = envelope(false);
        let denied_session = session(&denied_envelope);
        let denied_request = request(&denied_envelope);
        let mut denied_backend = RecordingBackend::default();

        let denied = mediate_adapter_operation(
            &denied_session,
            &denied_envelope,
            "event-denied",
            &denied_request,
            &context(RunState::Running),
            &mut denied_backend,
        )
        .unwrap();
        assert_eq!(denied.result.disposition, OperationDisposition::DeniedCapability);
        assert!(denied_backend.calls.is_empty());

        let allowed_envelope = envelope(true);
        let allowed_session = session(&allowed_envelope);
        let allowed_request = request(&allowed_envelope);
        let mut failing_backend = RecordingBackend {
            calls: vec![],
            fail: true,
        };
        let failed = mediate_adapter_operation(
            &allowed_session,
            &allowed_envelope,
            "event-tool-failure",
            &allowed_request,
            &context(RunState::Running),
            &mut failing_backend,
        )
        .unwrap();
        assert_eq!(failed.result.disposition, OperationDisposition::ToolFailure);
        assert_eq!(failing_backend.calls, vec![allowed_request.operation_id]);
    }

    #[test]
    fn geh_cf_033_complete_request_invokes_verification_not_direct_completion() {
        let envelope = envelope(true);
        let session = session(&envelope);
        let request = AdapterCompleteRequest {
            event_id: "event-complete".into(),
            session_id: session.session_id().clone(),
            run_id: envelope.run_id().clone(),
            envelope_id: envelope.envelope_id().clone(),
        };

        let response = handle_complete_request(
            &session,
            &envelope,
            &request,
            &VerificationEvidenceBundle::default(),
        )
        .unwrap();

        assert!(response.assessment.executor_reported_complete);
        assert_eq!(
            response.assessment.disposition,
            CompletionDisposition::Incomplete
        );
        assert_eq!(session.state(), &AdapterSessionState::Active);
    }

    #[test]
    fn geh_cf_034_disconnect_resume_requires_runtime_revalidation() {
        let envelope = envelope(true);
        let mut session = session(&envelope);
        let journal = GovernedRunJournal::new(&envelope);
        let checkpoint = journal.checkpoint();
        session.disconnect();

        let resumed = resume_adapter_session(
            &mut session,
            &envelope,
            &journal,
            &checkpoint,
            envelope.governing_state_digest(),
        );
        assert_eq!(resumed.disposition, AdapterResumeDisposition::Allowed);
        assert_eq!(session.state(), &AdapterSessionState::Active);

        session.disconnect();
        let drifted = resume_adapter_session(
            &mut session,
            &envelope,
            &journal,
            &checkpoint,
            "different-governing-state",
        );
        assert_eq!(
            drifted.disposition,
            AdapterResumeDisposition::RuntimeRejected {
                disposition: ResumeDisposition::GoverningStateDrift,
            }
        );
        assert_eq!(session.state(), &AdapterSessionState::Disconnected);
    }

    #[test]
    fn geh_cf_035_missing_mandatory_extension_rejects_initialization() {
        let envelope = envelope(true);
        let mut request = init_request(&envelope);
        request.mandatory_extensions = vec![AdapterExtensionRequirement::new(
            "org.example.required",
            "1.0.0",
        )];

        let outcome = initialize_adapter(&descriptor(), &envelope, request);

        assert_eq!(
            outcome,
            AdapterInitializationOutcome::Rejected(
                AdapterInitializationRejection::MissingMandatoryExtension {
                    namespace: "org.example.required".into(),
                    version: "1.0.0".into(),
                }
            )
        );
    }

    #[test]
    fn geh_cf_036_cancelled_run_rejects_adapter_operation_as_governed_outcome() {
        let envelope = envelope(true);
        let session = session(&envelope);
        let request = request(&envelope);
        let mut backend = RecordingBackend::default();

        let response = mediate_adapter_operation(
            &session,
            &envelope,
            "event-after-cancel",
            &request,
            &context(RunState::Cancelled),
            &mut backend,
        )
        .unwrap();

        assert_eq!(response.result.disposition, OperationDisposition::Cancelled);
        assert!(backend.calls.is_empty());
    }
}
