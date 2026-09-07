//! Live binding of a verified Codex provider-effect confinement result.
//!
//! Deterministic runtime conformance and a successful confinement certificate
//! are necessary but not sufficient for live activation. This layer reruns the
//! confinement fixture immediately before activation, then starts a fresh App
//! Server thread and proves that it is the same build/platform/profile/cwd
//! boundary before returning an activation binding.

use std::{error::Error, fmt, path::PathBuf};

use monad_codex_confinement::{
    CONFINEMENT_CERTIFICATE_VERSION, CONFINEMENT_PROFILE_EXTENSION,
    CodexConfinementCertificate, CodexConfinementVerifier, ConfinementProbePlan,
};
use monad_codex_runtime::{AppServerTransport, CodexRuntimeError};
use serde::Serialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

pub const LIVE_ACTIVATION_SCHEMA_VERSION: &str = "0.1.0";
pub const MONAD_WORKSPACE_READ_TOOL: &str = "monad_workspace_read_text";

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct LiveActivationPlan {
    pub profile_id: String,
    pub provider_runtime_cwd: PathBuf,
    pub forbidden_path: PathBuf,
    pub forbidden_marker: String,
}

impl LiveActivationPlan {
    pub fn new(
        profile_id: impl Into<String>,
        provider_runtime_cwd: impl Into<PathBuf>,
        forbidden_path: impl Into<PathBuf>,
        forbidden_marker: impl Into<String>,
    ) -> Self {
        Self {
            profile_id: profile_id.into(),
            provider_runtime_cwd: provider_runtime_cwd.into(),
            forbidden_path: forbidden_path.into(),
            forbidden_marker: forbidden_marker.into(),
        }
    }

    fn validate(&self) -> Result<(), LiveActivationError> {
        if self.profile_id.trim().is_empty() {
            return Err(LiveActivationError::InvalidPlan(
                "profile id must be non-empty".into(),
            ));
        }
        if self.forbidden_marker.is_empty() {
            return Err(LiveActivationError::InvalidPlan(
                "forbidden marker must be non-empty".into(),
            ));
        }
        if !self.provider_runtime_cwd.is_absolute() || !self.forbidden_path.is_absolute() {
            return Err(LiveActivationError::InvalidPlan(
                "provider cwd and forbidden path must be absolute".into(),
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct LiveActivationBinding {
    pub schema_version: String,
    pub activated: bool,
    pub certificate_digest: String,
    pub certificate: CodexConfinementCertificate,
    pub activation_user_agent: String,
    pub activation_platform_family: Option<String>,
    pub activation_platform_os: String,
    pub profile_id: String,
    pub provider_runtime_cwd: String,
    pub thread_id: String,
    pub active_permission_profile_id: String,
    pub dynamic_tool_registered: String,
}

#[derive(Debug)]
pub enum LiveActivationError {
    Runtime(String),
    Confinement(String),
    InvalidPlan(String),
    Protocol(String),
    CertificateMismatch(String),
}

impl fmt::Display for LiveActivationError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Runtime(value) => write!(formatter, "Codex runtime error: {value}"),
            Self::Confinement(value) => write!(formatter, "Codex confinement failed: {value}"),
            Self::InvalidPlan(value) => write!(formatter, "invalid live activation plan: {value}"),
            Self::Protocol(value) => write!(formatter, "live activation protocol failed closed: {value}"),
            Self::CertificateMismatch(value) => write!(formatter, "live activation did not match confinement certificate: {value}"),
        }
    }
}

impl Error for LiveActivationError {}

impl From<CodexRuntimeError> for LiveActivationError {
    fn from(error: CodexRuntimeError) -> Self {
        Self::Runtime(error.to_string())
    }
}

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

pub fn certify_and_bind<C, A>(
    certification_transport: C,
    activation_transport: A,
    plan: &LiveActivationPlan,
) -> Result<LiveActivationBinding, LiveActivationError>
where
    C: AppServerTransport,
    A: AppServerTransport,
{
    plan.validate()?;

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

    let mut activation = ActivationProtocol::new(activation_transport);
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
    Ok(LiveActivationBinding {
        schema_version: LIVE_ACTIVATION_SCHEMA_VERSION.into(),
        activated: true,
        certificate_digest,
        activation_user_agent: identity.user_agent,
        activation_platform_family: identity.platform_family,
        activation_platform_os: identity.platform_os,
        profile_id: certificate.profile_id.clone(),
        provider_runtime_cwd: certificate.provider_runtime_cwd.clone(),
        thread_id: thread.thread_id,
        active_permission_profile_id: thread.active_profile_id,
        dynamic_tool_registered: MONAD_WORKSPACE_READ_TOOL.into(),
        certificate,
    })
}

fn validate_certificate(
    certificate: &CodexConfinementCertificate,
    plan: &LiveActivationPlan,
) -> Result<(), LiveActivationError> {
    if certificate.schema_version != CONFINEMENT_CERTIFICATE_VERSION {
        return Err(LiveActivationError::CertificateMismatch(format!(
            "unsupported certificate schema {:?}", certificate.schema_version
        )));
    }
    if certificate.extension != CONFINEMENT_PROFILE_EXTENSION {
        return Err(LiveActivationError::CertificateMismatch(format!(
            "unexpected confinement extension {:?}", certificate.extension
        )));
    }
    if !certificate.verified {
        return Err(LiveActivationError::CertificateMismatch(
            "certificate is not verified".into(),
        ));
    }
    if certificate.platform_os != "linux" {
        return Err(LiveActivationError::CertificateMismatch(format!(
            "initial live activation supports Linux only; certificate reports {:?}",
            certificate.platform_os
        )));
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
        return Err(LiveActivationError::CertificateMismatch(format!(
            "certificate registered unexpected dynamic tool {:?}",
            certificate.dynamic_tool_registered
        )));
    }
    Ok(())
}

fn validate_identity(
    certificate: &CodexConfinementCertificate,
    identity: &ActivationServerIdentity,
) -> Result<(), LiveActivationError> {
    if certificate.codex_user_agent != identity.user_agent {
        return Err(LiveActivationError::CertificateMismatch(format!(
            "App Server user agent changed between certification {:?} and activation {:?}",
            certificate.codex_user_agent, identity.user_agent
        )));
    }
    if certificate.platform_os != identity.platform_os {
        return Err(LiveActivationError::CertificateMismatch(format!(
            "platform OS changed between certification {:?} and activation {:?}",
            certificate.platform_os, identity.platform_os
        )));
    }
    if certificate.platform_family != identity.platform_family {
        return Err(LiveActivationError::CertificateMismatch(
            "platform family changed between certification and activation".into(),
        ));
    }
    Ok(())
}

struct ActivationProtocol<T: AppServerTransport> {
    transport: T,
    next_request_id: u64,
    initialized: bool,
}

impl<T: AppServerTransport> ActivationProtocol<T> {
    fn new(transport: T) -> Self {
        Self {
            transport,
            next_request_id: 1,
            initialized: false,
        }
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
                LiveActivationError::Protocol(
                    "thread/start omitted a non-empty thread.id".into(),
                )
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
    use std::{collections::VecDeque, fs, path::Path, time::{SystemTime, UNIX_EPOCH}};

    use super::*;

    #[derive(Default)]
    struct ScriptedTransport {
        incoming: VecDeque<Value>,
        sent: Vec<Value>,
    }

    impl ScriptedTransport {
        fn with_incoming(messages: Vec<Value>) -> Self {
            Self { incoming: messages.into(), sent: vec![] }
        }
    }

    impl AppServerTransport for ScriptedTransport {
        fn send(&mut self, message: &Value) -> Result<(), CodexRuntimeError> {
            self.sent.push(message.clone());
            Ok(())
        }

        fn receive(&mut self) -> Result<Value, CodexRuntimeError> {
            self.incoming.pop_front().ok_or_else(|| {
                CodexRuntimeError::Io("scripted live activation transport exhausted input".into())
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
                "monad-codex-live-activation-{}-{nonce}", std::process::id()
            ));
            fs::create_dir_all(root.join("provider")).expect("create provider cwd");
            fs::write(root.join("sentinel"), "FORBIDDEN_MARKER\n").expect("write sentinel");
            Self(root)
        }

        fn provider_cwd(&self) -> PathBuf { self.0.join("provider") }
        fn sentinel(&self) -> PathBuf { self.0.join("sentinel") }
    }

    impl Drop for TestBoundary {
        fn drop(&mut self) { let _ = fs::remove_dir_all(&self.0); }
    }

    fn plan(boundary: &TestBoundary) -> LiveActivationPlan {
        LiveActivationPlan::new(
            "monad-geh-confinement",
            boundary.provider_cwd(),
            boundary.sentinel(),
            "FORBIDDEN_MARKER",
        )
    }

    fn initialize_response(id: u64, user_agent: &str) -> Value {
        json!({
            "id": id,
            "result": {
                "userAgent": user_agent,
                "platformFamily": "unix",
                "platformOs": "linux"
            }
        })
    }

    fn certification_transport() -> ScriptedTransport {
        ScriptedTransport::with_incoming(vec![
            initialize_response(1, "codex-test/0.153.4"),
            json!({ "id": 2, "result": { "exitCode": 0, "stdout": "MONAD_CODEX_CONFINEMENT_CONTROL_V1\n", "stderr": "" } }),
            json!({ "id": 3, "result": { "exitCode": 1, "stdout": "", "stderr": "cat: permission denied\n" } }),
            json!({ "id": 4, "result": { "thread": { "id": "thr_cert" }, "activePermissionProfile": { "id": "monad-geh-confinement" } } }),
        ])
    }

    fn activation_transport(user_agent: &str, profile: &str) -> ScriptedTransport {
        ScriptedTransport::with_incoming(vec![
            initialize_response(1, user_agent),
            json!({
                "id": 2,
                "result": {
                    "thread": { "id": "thr_activation" },
                    "sandbox": { "type": "readOnly", "networkAccess": false },
                    "activePermissionProfile": { "id": profile }
                }
            }),
        ])
    }

    #[test]
    fn live_activation_recertifies_and_binds_same_build_profile_and_cwd() {
        let boundary = TestBoundary::new();
        let binding = certify_and_bind(
            certification_transport(),
            activation_transport("codex-test/0.153.4", "monad-geh-confinement"),
            &plan(&boundary),
        )
        .unwrap();
        assert!(binding.activated);
        assert!(binding.certificate.verified);
        assert_eq!(binding.profile_id, "monad-geh-confinement");
        assert_eq!(binding.active_permission_profile_id, binding.profile_id);
        assert_eq!(binding.activation_user_agent, binding.certificate.codex_user_agent);
        assert_eq!(binding.dynamic_tool_registered, MONAD_WORKSPACE_READ_TOOL);
        assert!(binding.certificate_digest.starts_with("sha256:"));
    }

    #[test]
    fn live_activation_rejects_build_identity_change_after_certification() {
        let boundary = TestBoundary::new();
        let error = certify_and_bind(
            certification_transport(),
            activation_transport("codex-test/changed", "monad-geh-confinement"),
            &plan(&boundary),
        )
        .unwrap_err();
        assert!(matches!(error, LiveActivationError::CertificateMismatch(_)));
    }

    #[test]
    fn live_activation_rejects_profile_substitution() {
        let boundary = TestBoundary::new();
        let error = certify_and_bind(
            certification_transport(),
            activation_transport("codex-test/0.153.4", "broader-profile"),
            &plan(&boundary),
        )
        .unwrap_err();
        assert!(matches!(error, LiveActivationError::CertificateMismatch(_)));
    }

    #[test]
    fn activation_thread_explicitly_selects_certified_profile_and_restricted_surfaces() {
        let boundary = TestBoundary::new();
        let mut protocol = ActivationProtocol::new(activation_transport(
            "codex-test/0.153.4",
            "monad-geh-confinement",
        ));
        protocol.initialize().unwrap();
        protocol.start_thread(&plan(&boundary)).unwrap();
        let sent = &protocol.transport.sent;
        assert_eq!(sent[2]["method"], "thread/start");
        assert_eq!(sent[2]["params"]["permissions"], "monad-geh-confinement");
        assert_eq!(sent[2]["params"]["runtimeWorkspaceRoots"], json!([]));
        assert_eq!(sent[2]["params"]["environments"], json!([]));
        assert_eq!(sent[2]["params"]["selectedCapabilityRoots"], json!([]));
        assert_eq!(sent[2]["params"]["dynamicTools"][0]["name"], MONAD_WORKSPACE_READ_TOOL);
        assert_eq!(sent[2]["params"]["config"]["features.shell_tool"], false);
        assert_eq!(sent[2]["params"]["config"]["web_search"], "disabled");
    }

    #[test]
    fn plan_requires_absolute_provider_and_forbidden_paths() {
        let plan = LiveActivationPlan::new("profile", Path::new("relative"), Path::new("sentinel"), "marker");
        assert!(matches!(plan.validate(), Err(LiveActivationError::InvalidPlan(_))));
    }
}
