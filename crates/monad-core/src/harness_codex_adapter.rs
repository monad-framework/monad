//! Concrete C2 adapter semantics for OpenAI Codex App Server.
//!
//! This module is intentionally narrower than a Codex process/runtime client.
//! It translates the untrusted, model-authored portion of App Server dynamic
//! tool requests into Monad-owned governed operation requests, binds them to an
//! already-negotiated C2 adapter session, and routes them through the C1 Tool
//! Gateway. Process launch, stdio transport, provider authentication, and model
//! inference remain outside `monad-core`.

use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};

use crate::{
    harness::{ExecutionEnvelope, OperationDisposition, OperationRequest},
    harness_adapter::{
        ADAPTER_INTERFACE_VERSION, AdapterCompleteRequest, AdapterCompletionResponse,
        AdapterDescriptor, AdapterExtensionRequirement, AdapterExtensionSupport, AdapterFeature,
        AdapterInitializationOutcome, AdapterInitializationRequest, AdapterObservation,
        AdapterOperationResponse, AdapterProtocolError, AdapterSession, AdapterSessionId,
        adapter_operation_response, handle_complete_request, initialize_adapter,
    },
    harness_gateway::OperationGovernanceContext,
    harness_verification::VerificationEvidenceBundle,
    harness_workspace_read::{
        WORKSPACE_READ_CAPABILITY, WORKSPACE_READ_TEXT_OPERATION, WORKSPACE_TOOL,
        WorkspaceReadBackend, mediate_workspace_read,
    },
};

pub const CODEX_ADAPTER_ID: &str = "adapter:openai-codex-app-server";
pub const CODEX_ADAPTER_VERSION: &str = "0.1.0";
pub const CODEX_HARNESS_FAMILY: &str = "openai-codex";
pub const CODEX_TRANSPORT_MODE: &str = "app-server-jsonl-stdio";
pub const CODEX_PROFILE_EXTENSION: &str = "org.monad.codex.app-server.dynamic-tools";
pub const CODEX_PROFILE_EXTENSION_VERSION: &str = "0.1.0";
pub const CODEX_WORKSPACE_READ_TOOL: &str = "monad_workspace_read_text";

const CODEX_OPERATION_ID_DOMAIN: &str = "monad.codex-adapter.operation.v1";
const CODEX_PARAMETERS_DIGEST_DOMAIN: &str = "monad.codex-adapter.parameters.v1";

/// Descriptor for the first concrete external-harness adapter profile.
///
/// The provider-specific extension is mandatory because the initial profile
/// depends on App Server `dynamicTools`, which is an experimental capability.
/// If a connected Codex version cannot provide it, C2 initialization must fail
/// rather than silently exposing Codex-native filesystem/process tools as a
/// substitute for GEH mediation.
pub fn codex_adapter_descriptor() -> AdapterDescriptor {
    AdapterDescriptor {
        adapter_id: CODEX_ADAPTER_ID.into(),
        adapter_version: CODEX_ADAPTER_VERSION.into(),
        harness_family: CODEX_HARNESS_FAMILY.into(),
        supported_interface_versions: vec![ADAPTER_INTERFACE_VERSION.into()],
        supported_envelope_versions: vec!["0.1.0".into()],
        supported_transport_modes: vec![CODEX_TRANSPORT_MODE.into()],
        supported_features: vec![
            AdapterFeature::CheckpointResume,
            AdapterFeature::Cancellation,
            AdapterFeature::Streaming,
        ],
        extensions: vec![AdapterExtensionSupport::new(
            CODEX_PROFILE_EXTENSION,
            vec![CODEX_PROFILE_EXTENSION_VERSION.into()],
        )],
        limitations: vec![
            "requires Codex App Server dynamicTools / experimentalApi support".into(),
            "initial profile exposes only GEH-mediated workspace.read_text".into(),
            "process launch and provider authentication are outside monad-core".into(),
        ],
    }
}

pub fn initialize_codex_adapter(
    envelope: &ExecutionEnvelope,
    session_id: AdapterSessionId,
) -> AdapterInitializationOutcome {
    initialize_adapter(
        &codex_adapter_descriptor(),
        envelope,
        AdapterInitializationRequest {
            session_id,
            run_id: envelope.run_id().clone(),
            envelope_id: envelope.envelope_id().clone(),
            interface_version: ADAPTER_INTERFACE_VERSION.into(),
            transport_mode: CODEX_TRANSPORT_MODE.into(),
            required_features: vec![
                AdapterFeature::CheckpointResume,
                AdapterFeature::Cancellation,
                AdapterFeature::Streaming,
            ],
            mandatory_extensions: vec![AdapterExtensionRequirement::new(
                CODEX_PROFILE_EXTENSION,
                CODEX_PROFILE_EXTENSION_VERSION,
            )],
        },
    )
}

/// Provider-specific binding that remains subordinate to the generic C2
/// session. A Codex thread is opaque adapter state; it does not become a Monad
/// run identity or EOS lifecycle authority.
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct CodexAdapterSession {
    session: AdapterSession,
    thread_id: String,
}

impl CodexAdapterSession {
    pub fn session(&self) -> &AdapterSession {
        &self.session
    }

    pub fn thread_id(&self) -> &str {
        &self.thread_id
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum CodexAdapterError {
    ThreadIdRequired,
    ThreadBindingMismatch,
    TurnIdRequired,
    CallIdRequired,
    UnsupportedDynamicTool { tool: String },
    MalformedArguments { diagnostic: String },
    AdapterProtocol { diagnostic: String },
}

impl From<AdapterProtocolError> for CodexAdapterError {
    fn from(error: AdapterProtocolError) -> Self {
        Self::AdapterProtocol {
            diagnostic: format!("{error:?}"),
        }
    }
}

pub fn bind_codex_thread(
    session: AdapterSession,
    thread_id: impl Into<String>,
) -> Result<CodexAdapterSession, CodexAdapterError> {
    let thread_id = thread_id.into();
    if thread_id.trim().is_empty() {
        return Err(CodexAdapterError::ThreadIdRequired);
    }
    Ok(CodexAdapterSession { session, thread_id })
}

/// Untrusted `item/tool/call` params received from Codex App Server.
///
/// Run, envelope, executor, capability, scope semantics, and operation type are
/// deliberately absent. The executor is allowed to request only a named tool
/// with model-authored arguments; Monad reconstructs all authority-bearing
/// fields from the bound C2 session and immutable Execution Envelope.
#[derive(Clone, Debug, Eq, PartialEq, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct CodexDynamicToolCallDocument {
    pub thread_id: String,
    pub turn_id: String,
    pub call_id: String,
    pub tool: String,
    pub arguments: Value,
}

#[derive(Clone, Debug, Eq, PartialEq, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct WorkspaceReadArguments {
    path: String,
}

/// The transient response payload returned to Codex for an
/// `item/tool/call` request. It is executor-facing transport data, not an
/// automatic durable evidence record.
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct CodexDynamicToolResponse {
    pub content_items: Vec<CodexDynamicToolContentItem>,
    pub success: bool,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(tag = "type", rename_all = "camelCase")]
pub enum CodexDynamicToolContentItem {
    InputText { text: String },
}

/// Complete result of one Codex dynamic tool request at the adapter boundary.
/// `adapter_response` preserves the authoritative governed disposition while
/// `codex_response` is a transient provider-facing rendering.
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct CodexMediatedToolCall {
    pub adapter_response: AdapterOperationResponse,
    pub codex_response: CodexDynamicToolResponse,
}

pub fn compile_codex_operation_request(
    binding: &CodexAdapterSession,
    envelope: &ExecutionEnvelope,
    call: &CodexDynamicToolCallDocument,
) -> Result<OperationRequest, CodexAdapterError> {
    validate_call_identity(binding, call)?;
    if binding.session.run_id() != envelope.run_id()
        || binding.session.envelope_id() != envelope.envelope_id()
    {
        return Err(CodexAdapterError::AdapterProtocol {
            diagnostic: "Codex adapter session does not match execution envelope".into(),
        });
    }
    if call.tool != CODEX_WORKSPACE_READ_TOOL {
        return Err(CodexAdapterError::UnsupportedDynamicTool {
            tool: call.tool.clone(),
        });
    }

    let arguments: WorkspaceReadArguments = serde_json::from_value(call.arguments.clone())
        .map_err(|error| CodexAdapterError::MalformedArguments {
            diagnostic: error.to_string(),
        })?;

    let canonical_arguments = serde_json::to_vec(&arguments).map_err(|error| {
        CodexAdapterError::MalformedArguments {
            diagnostic: error.to_string(),
        }
    })?;

    Ok(OperationRequest {
        operation_id: crate::harness::OperationId(format!(
            "op-codex-v1-{}",
            domain_digest(
                CODEX_OPERATION_ID_DOMAIN,
                &[
                    binding.session.session_id().0.as_bytes(),
                    call.thread_id.as_bytes(),
                    call.turn_id.as_bytes(),
                    call.call_id.as_bytes(),
                ],
            )
        )),
        run_id: envelope.run_id().clone(),
        envelope_id: envelope.envelope_id().clone(),
        executor_actor_id: envelope.executor().actor_id.clone(),
        capability: WORKSPACE_READ_CAPABILITY.into(),
        tool: WORKSPACE_TOOL.into(),
        operation_type: WORKSPACE_READ_TEXT_OPERATION.into(),
        target_scope: arguments.path,
        parameters_digest: domain_digest(
            CODEX_PARAMETERS_DIGEST_DOMAIN,
            &[canonical_arguments.as_slice()],
        ),
        causal_parent: None,
        idempotency_key: Some(format!(
            "codex:{}:{}:{}",
            call.thread_id, call.turn_id, call.call_id
        )),
    })
}

/// Translate and mediate the initial Codex dynamic tool profile.
///
/// The actual workspace read crosses the effect boundary only after the C1
/// Tool Gateway admits the reconstructed authoritative request. Codex cannot
/// smuggle run identity, capability grants, operation type, or wider scope into
/// the request because those fields are not accepted from provider input.
pub fn mediate_codex_dynamic_tool_call(
    binding: &CodexAdapterSession,
    envelope: &ExecutionEnvelope,
    call: &CodexDynamicToolCallDocument,
    context: &OperationGovernanceContext,
    backend: &mut WorkspaceReadBackend,
) -> Result<CodexMediatedToolCall, CodexAdapterError> {
    let request = compile_codex_operation_request(binding, envelope, call)?;
    let outcome = mediate_workspace_read(envelope, &request, context, backend);
    let observation = outcome.observation.map(AdapterObservation::from);
    let adapter_response = adapter_operation_response(
        &binding.session,
        envelope,
        codex_event_id(call),
        &request,
        outcome.mediated,
        observation,
    )?;
    let codex_response = render_codex_response(&adapter_response)?;

    Ok(CodexMediatedToolCall {
        adapter_response,
        codex_response,
    })
}

/// Map Codex turn completion to the existing generic completion request. A
/// provider turn ending is advisory executor state only; independent Monad
/// verification remains authoritative for governed completion.
pub fn handle_codex_turn_completed(
    binding: &CodexAdapterSession,
    envelope: &ExecutionEnvelope,
    thread_id: &str,
    turn_id: &str,
    evidence: &VerificationEvidenceBundle,
) -> Result<AdapterCompletionResponse, CodexAdapterError> {
    if thread_id != binding.thread_id {
        return Err(CodexAdapterError::ThreadBindingMismatch);
    }
    if turn_id.trim().is_empty() {
        return Err(CodexAdapterError::TurnIdRequired);
    }

    let request = AdapterCompleteRequest {
        event_id: format!("codex-turn-completed:{thread_id}:{turn_id}"),
        session_id: binding.session.session_id().clone(),
        run_id: envelope.run_id().clone(),
        envelope_id: envelope.envelope_id().clone(),
    };
    handle_complete_request(&binding.session, envelope, &request, evidence).map_err(Into::into)
}

fn validate_call_identity(
    binding: &CodexAdapterSession,
    call: &CodexDynamicToolCallDocument,
) -> Result<(), CodexAdapterError> {
    if call.thread_id != binding.thread_id {
        return Err(CodexAdapterError::ThreadBindingMismatch);
    }
    if call.turn_id.trim().is_empty() {
        return Err(CodexAdapterError::TurnIdRequired);
    }
    if call.call_id.trim().is_empty() {
        return Err(CodexAdapterError::CallIdRequired);
    }
    Ok(())
}

fn codex_event_id(call: &CodexDynamicToolCallDocument) -> String {
    format!(
        "codex-tool-call:{}:{}:{}",
        call.thread_id, call.turn_id, call.call_id
    )
}

fn render_codex_response(
    response: &AdapterOperationResponse,
) -> Result<CodexDynamicToolResponse, CodexAdapterError> {
    let governed_metadata = serde_json::to_string(&response.result).map_err(|error| {
        CodexAdapterError::AdapterProtocol {
            diagnostic: format!("cannot serialize governed operation result: {error}"),
        }
    })?;

    let mut content_items = vec![CodexDynamicToolContentItem::InputText {
        text: format!("MONAD_GOVERNED_OPERATION_RESULT {governed_metadata}"),
    }];

    if let Some(AdapterObservation::Utf8Text { text, .. }) = &response.observation {
        content_items.push(CodexDynamicToolContentItem::InputText { text: text.clone() });
    }

    Ok(CodexDynamicToolResponse {
        content_items,
        success: response.result.disposition == OperationDisposition::ExecutedSuccess,
    })
}

fn domain_digest(domain: &str, fields: &[&[u8]]) -> String {
    let mut hasher = Sha256::new();
    hash_field(&mut hasher, domain.as_bytes());
    for field in fields {
        hash_field(&mut hasher, field);
    }
    let digest = hasher.finalize();
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut output = String::with_capacity(digest.len() * 2);
    for byte in digest {
        output.push(HEX[(byte >> 4) as usize] as char);
        output.push(HEX[(byte & 0x0f) as usize] as char);
    }
    output
}

fn hash_field(hasher: &mut Sha256, value: &[u8]) {
    hasher.update((value.len() as u64).to_be_bytes());
    hasher.update(value);
}

#[cfg(test)]
mod tests {
    use std::{
        collections::BTreeMap,
        fs,
        path::{Path, PathBuf},
        time::{SystemTime, UNIX_EPOCH},
    };

    use super::*;
    use crate::{
        harness::{
            ActorIdentity, CapabilityGrant, ExecutionEnvelopeDraft, RunId, RunState,
            compile_execution_envelope,
        },
        harness_adapter::AdapterInitializationOutcome,
        harness_gateway::{OperationGovernanceContext, PolicyDecision},
        harness_verification::CompletionDisposition,
    };

    struct TestWorkspace(PathBuf);

    impl TestWorkspace {
        fn new(label: &str) -> Self {
            let nonce = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("clock after epoch")
                .as_nanos();
            let path = std::env::temp_dir().join(format!(
                "monad-harness-codex-adapter-{label}-{}-{nonce}",
                std::process::id()
            ));
            fs::create_dir_all(&path).expect("create test workspace");
            Self(path)
        }

        fn root(&self) -> &Path {
            &self.0
        }

        fn write(&self, relative: &str, text: &str) {
            let path = self.0.join(relative);
            if let Some(parent) = path.parent() {
                fs::create_dir_all(parent).expect("create parent");
            }
            fs::write(path, text).expect("write fixture");
        }
    }

    impl Drop for TestWorkspace {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    fn envelope(scope: &str) -> ExecutionEnvelope {
        compile_execution_envelope(ExecutionEnvelopeDraft {
            schema_version: "0.1.0".into(),
            run_id: RunId("run-codex-c2-0001".into()),
            logical_time: "2026-09-01T20:00:00Z".into(),
            work_subject: "WP-HARNESS-CODEX".into(),
            intent: "exercise a read-only external Codex adapter".into(),
            requested_outcome: "governed workspace observation returned to Codex".into(),
            governing_state_digest: "state-codex-c2".into(),
            governed_references: vec![],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new(CODEX_ADAPTER_ID, "executor"),
            granted_capabilities: vec![CapabilityGrant::new(WORKSPACE_READ_CAPABILITY, scope)],
            prohibited_capabilities: vec![],
            allowed_tools: vec![WORKSPACE_TOOL.into()],
            environment_constraints: vec!["read-only".into()],
            acceptance_criteria: vec!["only the governed file may be observed".into()],
            verification_obligations: vec!["adapter conformance passes".into()],
            approval_gates: vec![],
            escalation_conditions: vec![],
            completion_criteria: vec!["result remains attributable".into()],
            resource_limits: BTreeMap::new(),
        })
    }

    fn binding(envelope: &ExecutionEnvelope) -> CodexAdapterSession {
        let initialized = initialize_codex_adapter(
            envelope,
            AdapterSessionId("session-codex-c2-0001".into()),
        );
        let AdapterInitializationOutcome::Accepted(session) = initialized else {
            panic!("Codex adapter profile should initialize");
        };
        bind_codex_thread(session, "thr_monad_0001").expect("bind thread")
    }

    fn call(path: &str) -> CodexDynamicToolCallDocument {
        CodexDynamicToolCallDocument {
            thread_id: "thr_monad_0001".into(),
            turn_id: "turn_0001".into(),
            call_id: "call_0001".into(),
            tool: CODEX_WORKSPACE_READ_TOOL.into(),
            arguments: serde_json::json!({ "path": path }),
        }
    }

    fn context() -> OperationGovernanceContext {
        OperationGovernanceContext {
            current_governing_state_digest: "state-codex-c2".into(),
            run_state: RunState::Running,
            policy: PolicyDecision::Allow,
            approved_gates: vec![],
        }
    }

    #[test]
    fn geh_cf_037_codex_profile_negotiates_mandatory_dynamic_tools_extension() {
        let envelope = envelope("README.md");
        let outcome = initialize_codex_adapter(
            &envelope,
            AdapterSessionId("session-codex-c2-0001".into()),
        );

        let AdapterInitializationOutcome::Accepted(session) = outcome else {
            panic!("Codex adapter profile should initialize");
        };
        assert_eq!(session.adapter_id(), CODEX_ADAPTER_ID);
        assert_eq!(session.transport_mode(), CODEX_TRANSPORT_MODE);
        assert_eq!(
            session.negotiated_extensions(),
            &[AdapterExtensionRequirement::new(
                CODEX_PROFILE_EXTENSION,
                CODEX_PROFILE_EXTENSION_VERSION,
            )]
        );
    }

    #[test]
    fn geh_cf_038_codex_dynamic_tool_read_is_mediated_with_exact_scope() {
        let workspace = TestWorkspace::new("authorized");
        workspace.write("docs/input.txt", "governed Codex observation\n");
        let envelope = envelope("docs/input.txt");
        let binding = binding(&envelope);
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let mediated = mediate_codex_dynamic_tool_call(
            &binding,
            &envelope,
            &call("docs/input.txt"),
            &context(),
            &mut backend,
        )
        .unwrap();

        assert_eq!(
            mediated.adapter_response.result.disposition,
            OperationDisposition::ExecutedSuccess
        );
        assert!(mediated.codex_response.success);
        assert!(matches!(
            mediated.codex_response.content_items.get(1),
            Some(CodexDynamicToolContentItem::InputText { text })
                if text == "governed Codex observation\n"
        ));
    }

    #[test]
    fn geh_cf_038_codex_out_of_scope_request_cannot_broaden_authority() {
        let workspace = TestWorkspace::new("denied");
        workspace.write("allowed.txt", "allowed");
        workspace.write("other.txt", "other");
        let envelope = envelope("allowed.txt");
        let binding = binding(&envelope);
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let mediated = mediate_codex_dynamic_tool_call(
            &binding,
            &envelope,
            &call("other.txt"),
            &context(),
            &mut backend,
        )
        .unwrap();

        assert_eq!(
            mediated.adapter_response.result.disposition,
            OperationDisposition::DeniedScope
        );
        assert!(mediated.adapter_response.observation.is_none());
        assert!(!mediated.codex_response.success);
    }

    #[test]
    fn geh_cf_038_codex_arguments_cannot_smuggle_authority_fields() {
        let envelope = envelope("allowed.txt");
        let binding = binding(&envelope);
        let mut call = call("allowed.txt");
        call.arguments = serde_json::json!({
            "path": "allowed.txt",
            "capability": "workspace.write",
            "runId": "run-attacker",
            "operationType": "write_text"
        });

        let error = compile_codex_operation_request(&binding, &envelope, &call).unwrap_err();
        assert!(matches!(error, CodexAdapterError::MalformedArguments { .. }));
    }

    #[test]
    fn geh_cf_038_codex_operation_identity_is_adapter_derived_and_deterministic() {
        let envelope = envelope("README.md");
        let binding = binding(&envelope);
        let call = call("README.md");

        let first = compile_codex_operation_request(&binding, &envelope, &call).unwrap();
        let second = compile_codex_operation_request(&binding, &envelope, &call).unwrap();

        assert_eq!(first.operation_id, second.operation_id);
        assert_eq!(first.parameters_digest, second.parameters_digest);
        assert_eq!(first.run_id, *envelope.run_id());
        assert_eq!(first.envelope_id, *envelope.envelope_id());
        assert_eq!(first.executor_actor_id, envelope.executor().actor_id);
    }

    #[test]
    fn geh_cf_039_codex_turn_completion_is_only_a_verification_request() {
        let envelope = envelope("README.md");
        let binding = binding(&envelope);

        let response = handle_codex_turn_completed(
            &binding,
            &envelope,
            "thr_monad_0001",
            "turn_0001",
            &VerificationEvidenceBundle::default(),
        )
        .unwrap();

        assert!(response.assessment.executor_reported_complete);
        assert_eq!(
            response.assessment.disposition,
            CompletionDisposition::Incomplete
        );
    }

    #[test]
    fn codex_thread_binding_mismatch_fails_before_governed_operation_compilation() {
        let envelope = envelope("README.md");
        let binding = binding(&envelope);
        let mut call = call("README.md");
        call.thread_id = "thr_other".into();

        assert_eq!(
            compile_codex_operation_request(&binding, &envelope, &call),
            Err(CodexAdapterError::ThreadBindingMismatch)
        );
    }
}
