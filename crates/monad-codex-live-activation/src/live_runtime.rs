use std::collections::VecDeque;

use monad_codex_confinement::{
    CONFINEMENT_CERTIFICATE_VERSION, CONFINEMENT_PROFILE_EXTENSION, CodexConfinementCertificate,
    CodexConfinementVerifier, ConfinementProbePlan,
};
use monad_codex_runtime::{
    AppServerTransport, CodexAppServerRuntime, CodexRuntimeError, CodexRuntimeSession,
    CodexServerIdentity, CodexTurnOutcome,
};
use monad_core::{
    harness::ExecutionEnvelope, harness_adapter::AdapterSessionId,
    harness_gateway::OperationGovernanceContext, harness_verification::VerificationEvidenceBundle,
    harness_workspace_read::WorkspaceReadBackend,
};
use serde::Serialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

use crate::{
    LIVE_ACTIVATION_SCHEMA_VERSION, LiveActivationBinding, LiveActivationError, LiveActivationPlan,
    MONAD_WORKSPACE_READ_TOOL,
};

#[derive(Clone, Debug, Eq, PartialEq)]
struct ActivationServerIdentity {
    user_agent: String,
    platform_family: Option<String>,
    platform_os: String,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ActivatedThread {
    thread_id: String,
    active_profile_id: String,
}

struct ActivationMaterial<T> {
    binding: LiveActivationBinding,
    transport: T,
    identity: ActivationServerIdentity,
    thread: ActivatedThread,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum AdoptionPhase {
    RuntimeInitialize,
    RuntimeInitialized,
    RuntimeThreadStart,
    Live,
}

/// Bridges the already-initialized and already-profile-bound App Server
/// connection into `CodexAppServerRuntime` without sending a second provider
/// initialize or `thread/start` request.
///
/// The bridge locally replays only the runtime bookkeeping messages required to
/// construct the existing deterministic runtime/session state. Once that state
/// is adopted, all subsequent messages are forwarded to the exact provider
/// connection that passed live activation.
pub struct ActivatedAppServerTransport<T: AppServerTransport> {
    inner: T,
    phase: AdoptionPhase,
    queued: VecDeque<Value>,
    identity: ActivationServerIdentity,
    thread: ActivatedThread,
    plan: LiveActivationPlan,
}

impl<T: AppServerTransport> ActivatedAppServerTransport<T> {
    fn new(
        inner: T,
        identity: ActivationServerIdentity,
        thread: ActivatedThread,
        plan: LiveActivationPlan,
    ) -> Self {
        Self {
            inner,
            phase: AdoptionPhase::RuntimeInitialize,
            queued: VecDeque::new(),
            identity,
            thread,
            plan,
        }
    }

    pub fn is_live(&self) -> bool {
        self.phase == AdoptionPhase::Live
    }

    pub fn provider_transport(&self) -> &T {
        &self.inner
    }

    fn reject(&self, diagnostic: impl Into<String>) -> CodexRuntimeError {
        CodexRuntimeError::Protocol(format!(
            "live activation adoption failed closed: {}",
            diagnostic.into()
        ))
    }

    fn replay_initialize(&mut self, message: &Value) -> Result<(), CodexRuntimeError> {
        if message.get("method").and_then(Value::as_str) != Some("initialize") {
            return Err(self.reject("runtime did not begin adoption with initialize"));
        }
        if message
            .pointer("/params/capabilities/experimentalApi")
            .and_then(Value::as_bool)
            != Some(true)
        {
            return Err(self.reject("runtime adoption did not request experimentalApi"));
        }
        let request_id = message
            .get("id")
            .cloned()
            .ok_or_else(|| self.reject("runtime initialize omitted request id"))?;
        self.queued.push_back(json!({
            "id": request_id,
            "result": {
                "userAgent": self.identity.user_agent,
                "platformFamily": self.identity.platform_family,
                "platformOs": self.identity.platform_os
            }
        }));
        self.phase = AdoptionPhase::RuntimeInitialized;
        Ok(())
    }

    fn replay_initialized(&mut self, message: &Value) -> Result<(), CodexRuntimeError> {
        if message.get("method").and_then(Value::as_str) != Some("initialized")
            || message.get("id").is_some()
        {
            return Err(self.reject("runtime adoption expected initialized notification"));
        }
        self.phase = AdoptionPhase::RuntimeThreadStart;
        Ok(())
    }

    fn replay_thread_start(&mut self, message: &Value) -> Result<(), CodexRuntimeError> {
        if message.get("method").and_then(Value::as_str) != Some("thread/start") {
            return Err(self.reject("runtime adoption expected thread/start"));
        }
        let request_id = message
            .get("id")
            .cloned()
            .ok_or_else(|| self.reject("runtime thread/start omitted request id"))?;
        let params = message
            .get("params")
            .ok_or_else(|| self.reject("runtime thread/start omitted params"))?;
        let expected_cwd = self.plan.provider_runtime_cwd.to_str().ok_or_else(|| {
            self.reject("provider runtime cwd is not valid UTF-8 during adoption")
        })?;
        if params.get("cwd").and_then(Value::as_str) != Some(expected_cwd) {
            return Err(self.reject("runtime provider cwd differs from activated cwd"));
        }
        if params.get("ephemeral").and_then(Value::as_bool) != Some(true) {
            return Err(self.reject("runtime adoption thread is not ephemeral"));
        }
        if params.get("sandbox").and_then(Value::as_str) != Some("read-only") {
            return Err(self.reject("runtime adoption thread is not read-only"));
        }
        if params.get("approvalPolicy").and_then(Value::as_str) != Some("never") {
            return Err(self.reject("runtime adoption changed approval policy"));
        }
        require_empty_array(params, "runtimeWorkspaceRoots", self)?;
        require_empty_array(params, "environments", self)?;
        require_empty_array(params, "selectedCapabilityRoots", self)?;

        let dynamic_tools = params
            .get("dynamicTools")
            .and_then(Value::as_array)
            .ok_or_else(|| self.reject("runtime adoption omitted dynamicTools"))?;
        if dynamic_tools.len() != 1
            || dynamic_tools[0].get("name").and_then(Value::as_str)
                != Some(MONAD_WORKSPACE_READ_TOOL)
        {
            return Err(
                self.reject("runtime adoption must register only monad_workspace_read_text")
            );
        }
        let config = params
            .get("config")
            .ok_or_else(|| self.reject("runtime adoption omitted restricted config"))?;
        if config.get("features.shell_tool").and_then(Value::as_bool) != Some(false)
            || config.get("features.unified_exec").and_then(Value::as_bool) != Some(false)
            || config.get("web_search").and_then(Value::as_str) != Some("disabled")
            || config
                .get("mcp_servers")
                .and_then(Value::as_object)
                .is_none_or(|value| !value.is_empty())
        {
            return Err(self.reject("runtime adoption broadened a restricted provider surface"));
        }

        self.queued.push_back(json!({
            "id": request_id,
            "result": {
                "thread": { "id": self.thread.thread_id },
                "sandbox": { "type": "readOnly", "networkAccess": false },
                "activePermissionProfile": { "id": self.thread.active_profile_id }
            }
        }));
        self.phase = AdoptionPhase::Live;
        Ok(())
    }
}

impl<T: AppServerTransport> AppServerTransport for ActivatedAppServerTransport<T> {
    fn send(&mut self, message: &Value) -> Result<(), CodexRuntimeError> {
        match self.phase {
            AdoptionPhase::RuntimeInitialize => self.replay_initialize(message),
            AdoptionPhase::RuntimeInitialized => self.replay_initialized(message),
            AdoptionPhase::RuntimeThreadStart => self.replay_thread_start(message),
            AdoptionPhase::Live => self.inner.send(message),
        }
    }

    fn receive(&mut self) -> Result<Value, CodexRuntimeError> {
        if let Some(message) = self.queued.pop_front() {
            return Ok(message);
        }
        if self.phase == AdoptionPhase::Live {
            return self.inner.receive();
        }
        Err(self.reject("runtime requested a replay response before the expected setup message"))
    }
}

/// The only Codex runtime wrapper that may become live-dogfood eligible in the
/// initial profile. It owns the exact App Server transport and thread that were
/// immediately certified and activated.
pub struct LiveActivatedRuntime<T: AppServerTransport> {
    binding: LiveActivationBinding,
    runtime: CodexAppServerRuntime<ActivatedAppServerTransport<T>>,
    session: CodexRuntimeSession,
}

impl<T: AppServerTransport> LiveActivatedRuntime<T> {
    pub fn binding(&self) -> &LiveActivationBinding {
        &self.binding
    }

    pub fn thread_id(&self) -> &str {
        self.session.thread_id()
    }

    pub fn provider_transport(&self) -> &T {
        self.runtime.transport().provider_transport()
    }

    pub fn require_live_governed_dogfood_eligibility(&self) -> Result<(), LiveActivationError> {
        if !self.binding.activated {
            return Err(LiveActivationError::CertificateMismatch(
                "live activation binding is not marked activated".into(),
            ));
        }
        if !self.runtime.transport().is_live() {
            return Err(LiveActivationError::Protocol(
                "activation transport has not completed runtime adoption".into(),
            ));
        }
        if self.binding.thread_id != self.session.thread_id() {
            return Err(LiveActivationError::CertificateMismatch(
                "runtime session thread differs from activated thread".into(),
            ));
        }
        if self.binding.active_permission_profile_id != self.binding.profile_id {
            return Err(LiveActivationError::CertificateMismatch(
                "activation binding does not retain the certified permission profile".into(),
            ));
        }
        Ok(())
    }

    pub fn run_turn(
        &mut self,
        envelope: &ExecutionEnvelope,
        prompt: &str,
        governance: &OperationGovernanceContext,
        backend: &mut WorkspaceReadBackend,
        evidence: &VerificationEvidenceBundle,
    ) -> Result<CodexTurnOutcome, LiveActivationError> {
        self.require_live_governed_dogfood_eligibility()?;
        let session = &self.session;
        let runtime = &mut self.runtime;
        runtime
            .run_turn(session, envelope, prompt, governance, backend, evidence)
            .map_err(LiveActivationError::from)
    }

    pub fn interrupt_turn(&mut self, turn_id: &str) -> Result<(), LiveActivationError> {
        self.require_live_governed_dogfood_eligibility()?;
        self.runtime
            .interrupt_turn(self.session.thread_id(), turn_id)
            .map_err(LiveActivationError::from)
    }
}

/// Rerun provider-effect confinement and bind the resulting proof directly to
/// the exact App Server connection/thread that the governed runtime will use.
/// No new provider connection or thread is opened after this function returns.
pub fn certify_and_activate_runtime<C, A>(
    certification_transport: C,
    activation_transport: A,
    plan: &LiveActivationPlan,
    envelope: &ExecutionEnvelope,
    session_id: AdapterSessionId,
) -> Result<LiveActivatedRuntime<A>, LiveActivationError>
where
    C: AppServerTransport,
    A: AppServerTransport,
{
    validate_plan(plan)?;
    let material = certify_material(certification_transport, activation_transport, plan)?;
    let binding = material.binding;
    let bridge = ActivatedAppServerTransport::new(
        material.transport,
        material.identity,
        material.thread,
        plan.clone(),
    );
    let mut runtime = CodexAppServerRuntime::new(bridge);
    let adopted_identity = runtime.initialize_connection()?;
    validate_adopted_identity(&binding, &adopted_identity)?;
    let session = runtime.start_read_only_session(
        envelope,
        session_id,
        plan.provider_runtime_cwd.as_path(),
    )?;
    if session.thread_id() != binding.thread_id {
        return Err(LiveActivationError::CertificateMismatch(format!(
            "runtime adopted thread {:?}; activation bound {:?}",
            session.thread_id(),
            binding.thread_id
        )));
    }
    let activated = LiveActivatedRuntime {
        binding,
        runtime,
        session,
    };
    activated.require_live_governed_dogfood_eligibility()?;
    Ok(activated)
}

fn certify_material<C, A>(
    certification_transport: C,
    activation_transport: A,
    plan: &LiveActivationPlan,
) -> Result<ActivationMaterial<A>, LiveActivationError>
where
    C: AppServerTransport,
    A: AppServerTransport,
{
    let confinement_plan = ConfinementProbePlan::linux_file_read(
        plan.profile_id.clone(),
        plan.provider_runtime_cwd.clone(),
        plan.forbidden_path.clone(),
        plan.forbidden_marker.clone(),
    );
    let mut verifier = CodexConfinementVerifier::new(certification_transport);
    verifier
        .initialize()
        .map_err(|error| LiveActivationError::Confinement(error.to_string()))?;
    let certificate = verifier
        .certify(&confinement_plan)
        .map_err(|error| LiveActivationError::Confinement(error.to_string()))?;
    validate_certificate(&certificate, plan)?;

    let mut activation = LiveActivationProtocol::new(activation_transport);
    let identity = activation.initialize()?;
    validate_identity(&certificate, &identity)?;
    let thread = activation.start_thread(plan)?;
    if thread.active_profile_id != certificate.profile_id {
        return Err(LiveActivationError::CertificateMismatch(format!(
            "activation thread selected profile {:?}; certificate binds {:?}",
            thread.active_profile_id, certificate.profile_id
        )));
    }
    let certificate_digest = digest_json(&certificate)?;
    let binding = LiveActivationBinding {
        schema_version: LIVE_ACTIVATION_SCHEMA_VERSION.into(),
        activated: true,
        certificate_digest,
        activation_user_agent: identity.user_agent.clone(),
        activation_platform_family: identity.platform_family.clone(),
        activation_platform_os: identity.platform_os.clone(),
        profile_id: certificate.profile_id.clone(),
        provider_runtime_cwd: certificate.provider_runtime_cwd.clone(),
        thread_id: thread.thread_id.clone(),
        active_permission_profile_id: thread.active_profile_id.clone(),
        dynamic_tool_registered: MONAD_WORKSPACE_READ_TOOL.into(),
        certificate,
    };
    Ok(ActivationMaterial {
        binding,
        transport: activation.into_transport(),
        identity,
        thread,
    })
}

struct LiveActivationProtocol<T: AppServerTransport> {
    transport: T,
    next_request_id: u64,
    initialized: bool,
}

impl<T: AppServerTransport> LiveActivationProtocol<T> {
    fn new(transport: T) -> Self {
        Self {
            transport,
            next_request_id: 1,
            initialized: false,
        }
    }

    fn into_transport(self) -> T {
        self.transport
    }

    fn initialize(&mut self) -> Result<ActivationServerIdentity, LiveActivationError> {
        if self.initialized {
            return Err(LiveActivationError::Protocol(
                "initialize may occur only once per activation connection".into(),
            ));
        }
        let result = self.request(
            "initialize",
            json!({
                "clientInfo": {
                    "name": "monad",
                    "title": "Monad Codex Live Activation",
                    "version": LIVE_ACTIVATION_SCHEMA_VERSION
                },
                "capabilities": { "experimentalApi": true }
            }),
        )?;
        self.transport
            .send(&json!({ "method": "initialized", "params": {} }))?;
        self.initialized = true;
        Ok(ActivationServerIdentity {
            user_agent: required_string(&result, "userAgent")?,
            platform_family: optional_string(&result, "platformFamily"),
            platform_os: required_string(&result, "platformOs")?,
        })
    }

    fn start_thread(
        &mut self,
        plan: &LiveActivationPlan,
    ) -> Result<ActivatedThread, LiveActivationError> {
        if !self.initialized {
            return Err(LiveActivationError::Protocol(
                "activation connection must be initialized before thread/start".into(),
            ));
        }
        let cwd = plan.provider_runtime_cwd.to_str().ok_or_else(|| {
            LiveActivationError::Protocol("provider cwd is not valid UTF-8".into())
        })?;
        let result = self.request(
            "thread/start",
            json!({
                "cwd": cwd,
                "runtimeWorkspaceRoots": [],
                "ephemeral": true,
                "permissions": plan.profile_id,
                "sandbox": "read-only",
                "approvalPolicy": "never",
                "environments": [],
                "selectedCapabilityRoots": [],
                "dynamicTools": [workspace_read_dynamic_tool_spec()],
                "config": restricted_thread_config(),
                "developerInstructions": "Use the Monad-provided dynamic tool for every governed workspace observation. Provider-native effects are not Monad authority."
            }),
        )?;
        let thread_id = result
            .pointer("/thread/id")
            .and_then(Value::as_str)
            .filter(|value| !value.trim().is_empty())
            .ok_or_else(|| {
                LiveActivationError::Protocol("thread/start omitted a non-empty thread.id".into())
            })?
            .to_owned();
        let active_profile_id = result
            .pointer("/activePermissionProfile/id")
            .and_then(Value::as_str)
            .filter(|value| !value.trim().is_empty())
            .ok_or_else(|| {
                LiveActivationError::Protocol(
                    "thread/start omitted activePermissionProfile.id".into(),
                )
            })?
            .to_owned();
        if active_profile_id != plan.profile_id {
            return Err(LiveActivationError::CertificateMismatch(format!(
                "activation thread selected profile {active_profile_id:?}; requested {:?}",
                plan.profile_id
            )));
        }
        if let Some(sandbox_type) = result.pointer("/sandbox/type").and_then(Value::as_str)
            && sandbox_type != "readOnly"
        {
            return Err(LiveActivationError::Protocol(format!(
                "activation thread returned unexpected sandbox type {sandbox_type:?}"
            )));
        }
        Ok(ActivatedThread {
            thread_id,
            active_profile_id,
        })
    }

    fn request(&mut self, method: &str, params: Value) -> Result<Value, LiveActivationError> {
        let request_id = self.next_request_id;
        self.next_request_id = self
            .next_request_id
            .checked_add(1)
            .ok_or_else(|| LiveActivationError::Protocol("request id exhausted".into()))?;
        self.transport.send(&json!({
            "method": method,
            "id": request_id,
            "params": params
        }))?;
        loop {
            let message = self.transport.receive()?;
            if message.get("id") == Some(&json!(request_id)) {
                if let Some(error) = message.get("error") {
                    return Err(LiveActivationError::Protocol(format!(
                        "{method} returned JSON-RPC error {error}"
                    )));
                }
                return message.get("result").cloned().ok_or_else(|| {
                    LiveActivationError::Protocol(format!(
                        "{method} response omitted both result and error"
                    ))
                });
            }
            if message.get("id").is_some() && message.get("method").is_some() {
                return Err(LiveActivationError::Protocol(format!(
                    "unexpected App Server request while awaiting {method}"
                )));
            }
        }
    }
}

fn validate_plan(plan: &LiveActivationPlan) -> Result<(), LiveActivationError> {
    if plan.profile_id.trim().is_empty() {
        return Err(LiveActivationError::InvalidPlan(
            "profile id must be non-empty".into(),
        ));
    }
    if plan.forbidden_marker.is_empty() {
        return Err(LiveActivationError::InvalidPlan(
            "forbidden marker must be non-empty".into(),
        ));
    }
    if !plan.provider_runtime_cwd.is_absolute() || !plan.forbidden_path.is_absolute() {
        return Err(LiveActivationError::InvalidPlan(
            "provider cwd and forbidden path must be absolute".into(),
        ));
    }
    Ok(())
}

fn validate_certificate(
    certificate: &CodexConfinementCertificate,
    plan: &LiveActivationPlan,
) -> Result<(), LiveActivationError> {
    if certificate.schema_version != CONFINEMENT_CERTIFICATE_VERSION {
        return Err(LiveActivationError::CertificateMismatch(format!(
            "unsupported certificate schema {:?}",
            certificate.schema_version
        )));
    }
    if certificate.extension != CONFINEMENT_PROFILE_EXTENSION {
        return Err(LiveActivationError::CertificateMismatch(format!(
            "unexpected confinement extension {:?}",
            certificate.extension
        )));
    }
    if !certificate.verified || certificate.platform_os != "linux" {
        return Err(LiveActivationError::CertificateMismatch(
            "certificate is not a verified Linux confinement proof".into(),
        ));
    }
    if certificate.profile_id != plan.profile_id
        || certificate.active_permission_profile_id != plan.profile_id
    {
        return Err(LiveActivationError::CertificateMismatch(
            "certificate does not bind the requested permission profile".into(),
        ));
    }
    if certificate.provider_runtime_cwd != plan.provider_runtime_cwd.to_string_lossy() {
        return Err(LiveActivationError::CertificateMismatch(
            "certificate provider cwd differs from activation cwd".into(),
        ));
    }
    if certificate.forbidden_path != plan.forbidden_path.to_string_lossy() {
        return Err(LiveActivationError::CertificateMismatch(
            "certificate forbidden path differs from activation boundary".into(),
        ));
    }
    if certificate.dynamic_tool_registered != MONAD_WORKSPACE_READ_TOOL {
        return Err(LiveActivationError::CertificateMismatch(
            "certificate registered an unexpected dynamic tool".into(),
        ));
    }
    Ok(())
}

fn validate_identity(
    certificate: &CodexConfinementCertificate,
    identity: &ActivationServerIdentity,
) -> Result<(), LiveActivationError> {
    if certificate.codex_user_agent != identity.user_agent
        || certificate.platform_os != identity.platform_os
        || certificate.platform_family != identity.platform_family
    {
        return Err(LiveActivationError::CertificateMismatch(
            "App Server identity/platform changed between certification and activation".into(),
        ));
    }
    Ok(())
}

fn validate_adopted_identity(
    binding: &LiveActivationBinding,
    identity: &CodexServerIdentity,
) -> Result<(), LiveActivationError> {
    if identity.user_agent.as_deref() != Some(binding.activation_user_agent.as_str())
        || identity.platform_os.as_deref() != Some(binding.activation_platform_os.as_str())
        || identity.platform_family.as_deref() != binding.activation_platform_family.as_deref()
    {
        return Err(LiveActivationError::CertificateMismatch(
            "runtime adopted an identity different from the activated App Server".into(),
        ));
    }
    Ok(())
}

fn require_empty_array<T: AppServerTransport>(
    params: &Value,
    key: &str,
    transport: &ActivatedAppServerTransport<T>,
) -> Result<(), CodexRuntimeError> {
    if params
        .get(key)
        .and_then(Value::as_array)
        .is_none_or(|value| !value.is_empty())
    {
        return Err(transport.reject(format!("runtime adoption requires empty {key}")));
    }
    Ok(())
}

fn workspace_read_dynamic_tool_spec() -> Value {
    json!({
        "type": "function",
        "name": MONAD_WORKSPACE_READ_TOOL,
        "description": "Read one exact repository-relative UTF-8 text file through Monad governed execution mediation.",
        "inputSchema": {
            "type": "object",
            "properties": { "path": { "type": "string" } },
            "required": ["path"],
            "additionalProperties": false
        },
        "deferLoading": false
    })
}

fn restricted_thread_config() -> Value {
    json!({
        "features.apps": false,
        "features.code_mode": false,
        "features.code_mode_only": false,
        "features.deferred_executor": false,
        "features.enable_fanout": false,
        "features.hooks": false,
        "features.image_generation": false,
        "features.memories": false,
        "features.multi_agent": false,
        "features.multi_agent_v2": false,
        "features.plugins": false,
        "features.request_permissions_tool": false,
        "features.shell_snapshot": false,
        "features.shell_tool": false,
        "features.standalone_web_search": false,
        "features.tool_suggest": false,
        "features.unified_exec": false,
        "features.view_image": false,
        "orchestrator.skills.enabled": false,
        "skills.include_instructions": false,
        "tools.experimental_request_user_input.enabled": false,
        "tools.update_plan.enabled": false,
        "web_search": "disabled",
        "mcp_servers": {}
    })
}

fn required_string(value: &Value, key: &str) -> Result<String, LiveActivationError> {
    value
        .get(key)
        .and_then(Value::as_str)
        .filter(|value| !value.trim().is_empty())
        .map(str::to_owned)
        .ok_or_else(|| {
            LiveActivationError::Protocol(format!(
                "response omitted required non-empty string {key:?}"
            ))
        })
}

fn optional_string(value: &Value, key: &str) -> Option<String> {
    value.get(key).and_then(Value::as_str).map(str::to_owned)
}

fn digest_json(value: &impl Serialize) -> Result<String, LiveActivationError> {
    let bytes = serde_json::to_vec(value)
        .map_err(|error| LiveActivationError::Protocol(error.to_string()))?;
    let mut hasher = Sha256::new();
    hasher.update(bytes);
    Ok(format!("sha256:{:x}", hasher.finalize()))
}

#[cfg(test)]
mod tests {
    use std::{
        collections::{BTreeMap, VecDeque},
        fs,
        path::PathBuf,
        time::{SystemTime, UNIX_EPOCH},
    };

    use monad_core::{
        harness::{
            ActorIdentity, CapabilityGrant, ExecutionEnvelopeDraft, RunId, RunState,
            compile_execution_envelope,
        },
        harness_codex_adapter::CODEX_ADAPTER_ID,
        harness_gateway::PolicyDecision,
        harness_verification::CompletionDisposition,
    };

    use super::*;

    #[derive(Default)]
    struct ScriptedTransport {
        incoming: VecDeque<Value>,
        sent: Vec<Value>,
    }

    impl ScriptedTransport {
        fn with_incoming(messages: Vec<Value>) -> Self {
            Self {
                incoming: messages.into(),
                sent: vec![],
            }
        }
    }

    impl AppServerTransport for ScriptedTransport {
        fn send(&mut self, message: &Value) -> Result<(), CodexRuntimeError> {
            self.sent.push(message.clone());
            Ok(())
        }

        fn receive(&mut self) -> Result<Value, CodexRuntimeError> {
            self.incoming.pop_front().ok_or_else(|| {
                CodexRuntimeError::Io("scripted live runtime transport exhausted input".into())
            })
        }
    }

    struct TestBoundary(PathBuf);

    impl TestBoundary {
        fn new() -> Self {
            let nonce = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("clock after epoch")
                .as_nanos();
            let root = std::env::temp_dir().join(format!(
                "monad-codex-live-runtime-{}-{nonce}",
                std::process::id()
            ));
            fs::create_dir_all(root.join("provider")).expect("create provider cwd");
            fs::create_dir_all(root.join("workspace/docs")).expect("create workspace");
            fs::write(root.join("sentinel"), "FORBIDDEN_MARKER\n").expect("write sentinel");
            fs::write(
                root.join("workspace/docs/input.txt"),
                "runtime governed observation\n",
            )
            .expect("write governed fixture");
            Self(root)
        }

        fn provider_cwd(&self) -> PathBuf {
            self.0.join("provider")
        }

        fn sentinel(&self) -> PathBuf {
            self.0.join("sentinel")
        }

        fn workspace(&self) -> PathBuf {
            self.0.join("workspace")
        }
    }

    impl Drop for TestBoundary {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    fn plan(boundary: &TestBoundary) -> LiveActivationPlan {
        LiveActivationPlan::new(
            "monad-geh-confinement",
            boundary.provider_cwd(),
            boundary.sentinel(),
            "FORBIDDEN_MARKER",
        )
    }

    fn envelope(scope: &str) -> ExecutionEnvelope {
        compile_execution_envelope(ExecutionEnvelopeDraft {
            schema_version: "0.1.0".into(),
            run_id: RunId("run-live-activation-0001".into()),
            logical_time: "2026-09-07T15:30:00Z".into(),
            work_subject: "WP-HARNESS-CODEX-LIVE-ACTIVATION".into(),
            intent: "exercise the exact activated Codex connection".into(),
            requested_outcome: "one mediated workspace observation".into(),
            governing_state_digest: "state-live-activation".into(),
            governed_references: vec![],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new(CODEX_ADAPTER_ID, "executor"),
            granted_capabilities: vec![CapabilityGrant::new("workspace.read", scope)],
            prohibited_capabilities: vec![],
            allowed_tools: vec!["workspace".into()],
            environment_constraints: vec!["read-only".into()],
            acceptance_criteria: vec!["read remains exactly scoped".into()],
            verification_obligations: vec!["runtime remains attributable".into()],
            approval_gates: vec![],
            escalation_conditions: vec![],
            completion_criteria: vec!["verification controls completion".into()],
            resource_limits: BTreeMap::new(),
        })
    }

    fn governance() -> OperationGovernanceContext {
        OperationGovernanceContext {
            current_governing_state_digest: "state-live-activation".into(),
            run_state: RunState::Running,
            policy: PolicyDecision::Allow,
            approved_gates: vec![],
        }
    }

    fn initialize_response(id: u64) -> Value {
        json!({
            "id": id,
            "result": {
                "userAgent": "codex-test/0.153.4",
                "platformFamily": "unix",
                "platformOs": "linux"
            }
        })
    }

    fn certification_transport() -> ScriptedTransport {
        ScriptedTransport::with_incoming(vec![
            initialize_response(1),
            json!({ "id": 2, "result": { "exitCode": 0, "stdout": "MONAD_CODEX_CONFINEMENT_CONTROL_V1\n", "stderr": "" } }),
            json!({ "id": 3, "result": { "exitCode": 1, "stdout": "", "stderr": "cat: permission denied\n" } }),
            json!({ "id": 4, "result": { "thread": { "id": "thr_cert" }, "activePermissionProfile": { "id": "monad-geh-confinement" } } }),
        ])
    }

    fn activation_transport(include_turn: bool) -> ScriptedTransport {
        let mut incoming = vec![
            initialize_response(1),
            json!({
                "id": 2,
                "result": {
                    "thread": { "id": "thr_activation" },
                    "sandbox": { "type": "readOnly", "networkAccess": false },
                    "activePermissionProfile": { "id": "monad-geh-confinement" }
                }
            }),
        ];
        if include_turn {
            incoming.extend([
                json!({ "id": 3, "result": { "turn": { "id": "turn_activation" } } }),
                json!({
                    "method": "item/tool/call",
                    "id": 900,
                    "params": {
                        "threadId": "thr_activation",
                        "turnId": "turn_activation",
                        "callId": "call_activation",
                        "tool": MONAD_WORKSPACE_READ_TOOL,
                        "arguments": { "path": "docs/input.txt" }
                    }
                }),
                json!({
                    "method": "turn/completed",
                    "params": {
                        "threadId": "thr_activation",
                        "turn": { "id": "turn_activation", "status": "completed" }
                    }
                }),
            ]);
        }
        ScriptedTransport::with_incoming(incoming)
    }

    #[test]
    fn live_runtime_adopts_certified_connection_without_second_provider_handshake_or_thread() {
        let boundary = TestBoundary::new();
        let envelope = envelope("docs/input.txt");
        let runtime = certify_and_activate_runtime(
            certification_transport(),
            activation_transport(false),
            &plan(&boundary),
            &envelope,
            AdapterSessionId("session-live-activation-0001".into()),
        )
        .unwrap();

        runtime.require_live_governed_dogfood_eligibility().unwrap();
        assert_eq!(runtime.thread_id(), "thr_activation");
        let sent = &runtime.provider_transport().sent;
        assert_eq!(
            sent.iter()
                .filter(|message| message.get("method") == Some(&json!("initialize")))
                .count(),
            1
        );
        assert_eq!(
            sent.iter()
                .filter(|message| message.get("method") == Some(&json!("thread/start")))
                .count(),
            1
        );
        assert_eq!(
            sent.iter()
                .find(|message| message.get("method") == Some(&json!("thread/start")))
                .unwrap()["params"]["permissions"],
            "monad-geh-confinement"
        );
    }

    #[test]
    fn live_runtime_runs_turn_on_same_activated_thread_through_governed_workspace_read() {
        let boundary = TestBoundary::new();
        let envelope = envelope("docs/input.txt");
        let mut runtime = certify_and_activate_runtime(
            certification_transport(),
            activation_transport(true),
            &plan(&boundary),
            &envelope,
            AdapterSessionId("session-live-activation-0002".into()),
        )
        .unwrap();
        let workspace = boundary.workspace();
        let mut backend = WorkspaceReadBackend::new(workspace.as_path(), 4096).unwrap();

        let outcome = runtime
            .run_turn(
                &envelope,
                "Read docs/input.txt through the governed Monad tool.",
                &governance(),
                &mut backend,
                &VerificationEvidenceBundle::default(),
            )
            .unwrap();

        assert_eq!(outcome.thread_id, "thr_activation");
        assert_eq!(outcome.dynamic_tool_calls, 1);
        assert_eq!(
            outcome.completion.assessment.disposition,
            CompletionDisposition::Incomplete
        );
        let sent = &runtime.provider_transport().sent;
        assert_eq!(
            sent.iter()
                .filter(|message| message.get("method") == Some(&json!("thread/start")))
                .count(),
            1
        );
        let tool_response = sent
            .iter()
            .find(|message| message.get("id") == Some(&json!(900)))
            .expect("dynamic tool response");
        assert_eq!(tool_response["result"]["success"], true);
    }
}
