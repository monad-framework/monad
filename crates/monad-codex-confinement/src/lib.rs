//! Machine-verifiable provider-effect confinement certification for Codex C2.
//!
//! This crate does not ask a model to behave. It probes the selected Codex App
//! Server's own sandbox enforcement directly through `command/exec`, then
//! verifies that a provider thread selects the exact same named permission
//! profile. A certificate proves only the tested build/profile/path boundary;
//! it does not grant Monad capability or establish governed completion.

use std::{error::Error, fmt, fs, path::PathBuf};

use monad_codex_runtime::{AppServerTransport, CodexRuntimeError};
use serde::Serialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

pub const CONFINEMENT_CERTIFICATE_VERSION: &str = "0.1.0";
pub const CONFINEMENT_PROFILE_EXTENSION: &str = "org.monad.codex.provider-effect-confinement";
pub const CONFINEMENT_CONTROL_MARKER: &str = "MONAD_CODEX_CONFINEMENT_CONTROL_V1";
pub const MONAD_WORKSPACE_READ_TOOL: &str = "monad_workspace_read_text";

#[derive(Debug)]
pub enum CodexConfinementError {
    Runtime(String),
    Protocol(String),
    InvalidPlan(String),
    UnsupportedPlatform { platform_os: String },
    HostSentinelUnreadable(String),
    HostSentinelMismatch,
    PositiveControlRejected(String),
    PositiveControlFailed { exit_code: i32, stdout: String, stderr: String },
    ForbiddenContentLeaked,
    DeniedProbeUnexpectedSuccess { stdout: String, stderr: String },
    ActiveProfileMismatch { requested: String, active: Option<String> },
}

impl fmt::Display for CodexConfinementError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Runtime(value) => write!(formatter, "Codex runtime error: {value}"),
            Self::Protocol(value) => write!(formatter, "Codex confinement protocol error: {value}"),
            Self::InvalidPlan(value) => write!(formatter, "invalid confinement plan: {value}"),
            Self::UnsupportedPlatform { platform_os } => write!(
                formatter,
                "initial Codex confinement profile supports Linux only; App Server reported {platform_os:?}"
            ),
            Self::HostSentinelUnreadable(value) => {
                write!(formatter, "host could not verify forbidden sentinel: {value}")
            }
            Self::HostSentinelMismatch => write!(
                formatter,
                "host forbidden path does not contain the expected forbidden marker"
            ),
            Self::PositiveControlRejected(value) => {
                write!(formatter, "positive sandbox control was rejected: {value}")
            }
            Self::PositiveControlFailed {
                exit_code,
                stdout,
                stderr,
            } => write!(
                formatter,
                "positive sandbox control failed with exit {exit_code}; stdout={stdout:?}; stderr={stderr:?}"
            ),
            Self::ForbiddenContentLeaked => write!(
                formatter,
                "provider-native confinement probe exposed forbidden sentinel content"
            ),
            Self::DeniedProbeUnexpectedSuccess { stdout, stderr } => write!(
                formatter,
                "provider-native forbidden read unexpectedly succeeded; stdout={stdout:?}; stderr={stderr:?}"
            ),
            Self::ActiveProfileMismatch { requested, active } => write!(
                formatter,
                "thread did not bind the certified permission profile {requested:?}; active={active:?}"
            ),
        }
    }
}

impl Error for CodexConfinementError {}

impl From<CodexRuntimeError> for CodexConfinementError {
    fn from(error: CodexRuntimeError) -> Self {
        Self::Runtime(error.to_string())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ConfinementProbePlan {
    pub profile_id: String,
    pub provider_runtime_cwd: PathBuf,
    pub forbidden_path: PathBuf,
    pub forbidden_marker: String,
    pub positive_command: Vec<String>,
    pub positive_marker: String,
    pub denied_read_command: Vec<String>,
}

impl ConfinementProbePlan {
    /// Initial Linux certification plan. The host first proves the sentinel and
    /// marker really exist; Codex then proves it can execute a harmless command
    /// under the named profile but cannot read that sentinel with `/bin/cat`.
    pub fn linux_file_read(
        profile_id: impl Into<String>,
        provider_runtime_cwd: impl Into<PathBuf>,
        forbidden_path: impl Into<PathBuf>,
        forbidden_marker: impl Into<String>,
    ) -> Self {
        let forbidden_path = forbidden_path.into();
        Self {
            profile_id: profile_id.into(),
            provider_runtime_cwd: provider_runtime_cwd.into(),
            forbidden_marker: forbidden_marker.into(),
            positive_command: vec!["/bin/echo".into(), CONFINEMENT_CONTROL_MARKER.into()],
            positive_marker: CONFINEMENT_CONTROL_MARKER.into(),
            denied_read_command: vec![
                "/bin/cat".into(),
                forbidden_path.to_string_lossy().into_owned(),
            ],
            forbidden_path,
        }
    }

    fn validate(&self) -> Result<(), CodexConfinementError> {
        if self.profile_id.trim().is_empty() {
            return Err(CodexConfinementError::InvalidPlan(
                "profile_id must be non-empty".into(),
            ));
        }
        if self.positive_command.is_empty() || self.denied_read_command.is_empty() {
            return Err(CodexConfinementError::InvalidPlan(
                "positive and denied commands must be non-empty".into(),
            ));
        }
        if self.positive_marker.is_empty() || self.forbidden_marker.is_empty() {
            return Err(CodexConfinementError::InvalidPlan(
                "positive and forbidden markers must be non-empty".into(),
            ));
        }
        if !self.provider_runtime_cwd.is_absolute() || !self.forbidden_path.is_absolute() {
            return Err(CodexConfinementError::InvalidPlan(
                "provider cwd and forbidden path must be absolute".into(),
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct CommandProbeResponse {
    pub exit_code: i32,
    pub stdout_digest: String,
    pub stderr_digest: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum DeniedProbeEvidence {
    ServerRejected { error_digest: String },
    NonzeroExit(CommandProbeResponse),
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct CodexConfinementCertificate {
    pub schema_version: String,
    pub extension: String,
    pub profile_id: String,
    pub codex_user_agent: String,
    pub platform_family: Option<String>,
    pub platform_os: String,
    pub provider_runtime_cwd: String,
    pub forbidden_path: String,
    pub positive_control: CommandProbeResponse,
    pub denied_probe: DeniedProbeEvidence,
    pub thread_id: String,
    pub active_permission_profile_id: String,
    pub dynamic_tool_registered: String,
    pub verified: bool,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ServerIdentity {
    user_agent: String,
    platform_family: Option<String>,
    platform_os: String,
}

#[derive(Clone, Debug, Eq, PartialEq)]
enum CommandProbeOutcome {
    Response {
        exit_code: i32,
        stdout: String,
        stderr: String,
    },
    Rejected {
        error: String,
    },
}

/// Direct App Server verifier used before a runtime/profile can be activated as
/// live governed execution. It intentionally owns a separate protocol session
/// and does not create Monad run authority.
pub struct CodexConfinementVerifier<T: AppServerTransport> {
    transport: T,
    next_request_id: u64,
    identity: Option<ServerIdentity>,
}

impl<T: AppServerTransport> CodexConfinementVerifier<T> {
    pub fn new(transport: T) -> Self {
        Self {
            transport,
            next_request_id: 1,
            identity: None,
        }
    }

    pub fn transport(&self) -> &T {
        &self.transport
    }

    pub fn initialize(&mut self) -> Result<(), CodexConfinementError> {
        if self.identity.is_some() {
            return Err(CodexConfinementError::Protocol(
                "initialize may occur only once per verifier connection".into(),
            ));
        }
        let result = self.require_success(
            "initialize",
            json!({
                "clientInfo": {
                    "name": "monad",
                    "title": "Monad Codex Confinement Verifier",
                    "version": CONFINEMENT_CERTIFICATE_VERSION
                },
                "capabilities": {
                    "experimentalApi": true
                }
            }),
        )?;
        self.transport
            .send(&json!({ "method": "initialized", "params": {} }))?;

        let user_agent = required_string(&result, "userAgent")?;
        let platform_os = required_string(&result, "platformOs")?;
        let platform_family = optional_string(&result, "platformFamily");
        self.identity = Some(ServerIdentity {
            user_agent,
            platform_family,
            platform_os,
        });
        Ok(())
    }

    pub fn certify(
        &mut self,
        plan: &ConfinementProbePlan,
    ) -> Result<CodexConfinementCertificate, CodexConfinementError> {
        plan.validate()?;
        let identity = self.identity.clone().ok_or_else(|| {
            CodexConfinementError::Protocol("verifier connection is not initialized".into())
        })?;
        if identity.platform_os != "linux" {
            return Err(CodexConfinementError::UnsupportedPlatform {
                platform_os: identity.platform_os,
            });
        }

        let host_sentinel = fs::read_to_string(&plan.forbidden_path)
            .map_err(|error| CodexConfinementError::HostSentinelUnreadable(error.to_string()))?;
        if !host_sentinel.contains(&plan.forbidden_marker) {
            return Err(CodexConfinementError::HostSentinelMismatch);
        }

        let positive = self.command_exec(
            &plan.profile_id,
            &plan.provider_runtime_cwd,
            &plan.positive_command,
        )?;
        let positive_control = match positive {
            CommandProbeOutcome::Rejected { error } => {
                return Err(CodexConfinementError::PositiveControlRejected(error));
            }
            CommandProbeOutcome::Response {
                exit_code,
                stdout,
                stderr,
            } => {
                if exit_code != 0 || !stdout.contains(&plan.positive_marker) {
                    return Err(CodexConfinementError::PositiveControlFailed {
                        exit_code,
                        stdout,
                        stderr,
                    });
                }
                CommandProbeResponse {
                    exit_code,
                    stdout_digest: digest_text(&stdout),
                    stderr_digest: digest_text(&stderr),
                }
            }
        };

        let denied = self.command_exec(
            &plan.profile_id,
            &plan.provider_runtime_cwd,
            &plan.denied_read_command,
        )?;
        let denied_probe = match denied {
            CommandProbeOutcome::Rejected { error } => {
                if error.contains(&plan.forbidden_marker) {
                    return Err(CodexConfinementError::ForbiddenContentLeaked);
                }
                DeniedProbeEvidence::ServerRejected {
                    error_digest: digest_text(&error),
                }
            }
            CommandProbeOutcome::Response {
                exit_code,
                stdout,
                stderr,
            } => {
                if stdout.contains(&plan.forbidden_marker)
                    || stderr.contains(&plan.forbidden_marker)
                {
                    return Err(CodexConfinementError::ForbiddenContentLeaked);
                }
                if exit_code == 0 {
                    return Err(CodexConfinementError::DeniedProbeUnexpectedSuccess {
                        stdout,
                        stderr,
                    });
                }
                DeniedProbeEvidence::NonzeroExit(CommandProbeResponse {
                    exit_code,
                    stdout_digest: digest_text(&stdout),
                    stderr_digest: digest_text(&stderr),
                })
            }
        };

        let thread = self.require_success(
            "thread/start",
            json!({
                "cwd": plan.provider_runtime_cwd,
                "runtimeWorkspaceRoots": [],
                "ephemeral": true,
                "permissions": plan.profile_id,
                "approvalPolicy": "never",
                "environments": [],
                "selectedCapabilityRoots": [],
                "dynamicTools": [workspace_read_dynamic_tool_spec()],
                "config": restricted_thread_config(),
                "developerInstructions": "Governed workspace observations are available only through the Monad dynamic tool."
            }),
        )?;
        let thread_id = thread
            .pointer("/thread/id")
            .and_then(Value::as_str)
            .filter(|value| !value.trim().is_empty())
            .ok_or_else(|| {
                CodexConfinementError::Protocol(
                    "thread/start response omitted a non-empty thread.id".into(),
                )
            })?
            .to_owned();
        let active = thread
            .pointer("/activePermissionProfile/id")
            .and_then(Value::as_str)
            .map(str::to_owned);
        if active.as_deref() != Some(plan.profile_id.as_str()) {
            return Err(CodexConfinementError::ActiveProfileMismatch {
                requested: plan.profile_id.clone(),
                active,
            });
        }

        Ok(CodexConfinementCertificate {
            schema_version: CONFINEMENT_CERTIFICATE_VERSION.into(),
            extension: CONFINEMENT_PROFILE_EXTENSION.into(),
            profile_id: plan.profile_id.clone(),
            codex_user_agent: identity.user_agent,
            platform_family: identity.platform_family,
            platform_os: identity.platform_os,
            provider_runtime_cwd: plan.provider_runtime_cwd.to_string_lossy().into_owned(),
            forbidden_path: plan.forbidden_path.to_string_lossy().into_owned(),
            positive_control,
            denied_probe,
            thread_id,
            active_permission_profile_id: plan.profile_id.clone(),
            dynamic_tool_registered: MONAD_WORKSPACE_READ_TOOL.into(),
            verified: true,
        })
    }

    fn command_exec(
        &mut self,
        profile_id: &str,
        cwd: &PathBuf,
        command: &[String],
    ) -> Result<CommandProbeOutcome, CodexConfinementError> {
        match self.request(
            "command/exec",
            json!({
                "command": command,
                "cwd": cwd,
                "permissionProfile": profile_id,
                "timeoutMs": 5000,
                "outputBytesCap": 16384
            }),
        )? {
            Ok(result) => {
                let exit_code = result
                    .get("exitCode")
                    .and_then(Value::as_i64)
                    .and_then(|value| i32::try_from(value).ok())
                    .ok_or_else(|| {
                        CodexConfinementError::Protocol(
                            "command/exec response omitted integer exitCode".into(),
                        )
                    })?;
                let stdout = required_string(&result, "stdout")?;
                let stderr = required_string(&result, "stderr")?;
                Ok(CommandProbeOutcome::Response {
                    exit_code,
                    stdout,
                    stderr,
                })
            }
            Err(error) => Ok(CommandProbeOutcome::Rejected {
                error: error.to_string(),
            }),
        }
    }

    fn require_success(
        &mut self,
        method: &str,
        params: Value,
    ) -> Result<Value, CodexConfinementError> {
        match self.request(method, params)? {
            Ok(result) => Ok(result),
            Err(error) => Err(CodexConfinementError::Protocol(format!(
                "{method} returned JSON-RPC error {error}"
            ))),
        }
    }

    fn request(
        &mut self,
        method: &str,
        params: Value,
    ) -> Result<Result<Value, Value>, CodexConfinementError> {
        let request_id = self.next_request_id;
        self.next_request_id = self
            .next_request_id
            .checked_add(1)
            .ok_or_else(|| CodexConfinementError::Protocol("request id exhausted".into()))?;
        self.transport.send(&json!({
            "method": method,
            "id": request_id,
            "params": params
        }))?;

        loop {
            let message = self.transport.receive()?;
            if message.get("id") == Some(&json!(request_id)) {
                if let Some(error) = message.get("error") {
                    return Ok(Err(error.clone()));
                }
                let result = message.get("result").cloned().ok_or_else(|| {
                    CodexConfinementError::Protocol(format!(
                        "{method} response omitted both result and error"
                    ))
                })?;
                return Ok(Ok(result));
            }
            if message.get("id").is_some() && message.get("method").is_some() {
                return Err(CodexConfinementError::Protocol(format!(
                    "unexpected server request while awaiting {method}"
                )));
            }
            // Notifications are non-authoritative progress at this boundary.
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
            "properties": {
                "path": { "type": "string" }
            },
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

fn required_string(value: &Value, key: &str) -> Result<String, CodexConfinementError> {
    value
        .get(key)
        .and_then(Value::as_str)
        .filter(|value| !value.trim().is_empty())
        .map(str::to_owned)
        .ok_or_else(|| {
            CodexConfinementError::Protocol(format!(
                "response omitted required non-empty string {key:?}"
            ))
        })
}

fn optional_string(value: &Value, key: &str) -> Option<String> {
    value.get(key).and_then(Value::as_str).map(str::to_owned)
}

fn digest_text(value: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(value.as_bytes());
    format!("sha256:{:x}", hasher.finalize())
}

#[cfg(test)]
mod tests {
    use std::{
        collections::VecDeque,
        fs,
        path::{Path, PathBuf},
        time::{SystemTime, UNIX_EPOCH},
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
                CodexRuntimeError::Io("scripted confinement transport exhausted input".into())
            })
        }
    }

    struct TestRoot(PathBuf);

    impl TestRoot {
        fn new(label: &str) -> Self {
            let nonce = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("clock after epoch")
                .as_nanos();
            let path = std::env::temp_dir().join(format!(
                "monad-codex-confinement-{label}-{}-{nonce}",
                std::process::id()
            ));
            fs::create_dir_all(&path).expect("create test root");
            Self(path)
        }

        fn path(&self) -> &Path {
            &self.0
        }

        fn write(&self, relative: &str, text: &str) -> PathBuf {
            let path = self.0.join(relative);
            if let Some(parent) = path.parent() {
                fs::create_dir_all(parent).expect("create parent");
            }
            fs::write(&path, text).expect("write fixture");
            path
        }
    }

    impl Drop for TestRoot {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    fn initialize_response() -> Value {
        json!({
            "id": 1,
            "result": {
                "userAgent": "codex-cli/9.9.9-test",
                "platformFamily": "unix",
                "platformOs": "linux"
            }
        })
    }

    fn positive_response() -> Value {
        json!({
            "id": 2,
            "result": {
                "exitCode": 0,
                "stdout": format!("{}\n", CONFINEMENT_CONTROL_MARKER),
                "stderr": ""
            }
        })
    }

    fn denied_response() -> Value {
        json!({
            "id": 3,
            "result": {
                "exitCode": 1,
                "stdout": "",
                "stderr": "/bin/cat: Permission denied\n"
            }
        })
    }

    fn thread_response(profile: &str) -> Value {
        json!({
            "id": 4,
            "result": {
                "thread": { "id": "thr_confinement_0001" },
                "activePermissionProfile": { "id": profile, "extends": null }
            }
        })
    }

    fn fixture_plan() -> (TestRoot, TestRoot, ConfinementProbePlan) {
        let provider = TestRoot::new("provider");
        let governed = TestRoot::new("governed");
        let marker = "MONAD_FORBIDDEN_SENTINEL_6B1D9C";
        let forbidden = governed.write("sentinel.txt", marker);
        let plan = ConfinementProbePlan::linux_file_read(
            "monad-geh-confinement",
            provider.path(),
            forbidden,
            marker,
        );
        (provider, governed, plan)
    }

    #[test]
    fn geh_cf_038_confinement_positive_control_denies_sentinel_and_binds_same_profile() {
        let (_provider, _governed, plan) = fixture_plan();
        let transport = ScriptedTransport::with_incoming(vec![
            initialize_response(),
            positive_response(),
            denied_response(),
            thread_response(&plan.profile_id),
        ]);
        let mut verifier = CodexConfinementVerifier::new(transport);
        verifier.initialize().unwrap();
        let certificate = verifier.certify(&plan).unwrap();

        assert!(certificate.verified);
        assert_eq!(certificate.profile_id, "monad-geh-confinement");
        assert_eq!(certificate.active_permission_profile_id, plan.profile_id);
        assert_eq!(certificate.dynamic_tool_registered, MONAD_WORKSPACE_READ_TOOL);
        assert!(matches!(
            certificate.denied_probe,
            DeniedProbeEvidence::NonzeroExit(_)
        ));

        let sent = &verifier.transport().sent;
        assert_eq!(sent[1]["method"], "initialized");
        assert_eq!(sent[2]["method"], "command/exec");
        assert_eq!(
            sent[2]["params"]["permissionProfile"],
            "monad-geh-confinement"
        );
        assert_eq!(sent[3]["method"], "command/exec");
        assert_eq!(sent[4]["method"], "thread/start");
        assert_eq!(sent[4]["params"]["permissions"], "monad-geh-confinement");
    }

    #[test]
    fn geh_cf_038_confinement_rejects_forbidden_content_leak() {
        let (_provider, _governed, plan) = fixture_plan();
        let transport = ScriptedTransport::with_incoming(vec![
            initialize_response(),
            positive_response(),
            json!({
                "id": 3,
                "result": {
                    "exitCode": 0,
                    "stdout": format!("{}\n", plan.forbidden_marker),
                    "stderr": ""
                }
            }),
        ]);
        let mut verifier = CodexConfinementVerifier::new(transport);
        verifier.initialize().unwrap();

        assert!(matches!(
            verifier.certify(&plan),
            Err(CodexConfinementError::ForbiddenContentLeaked)
        ));
    }

    #[test]
    fn geh_cf_038_confinement_positive_control_prevents_false_pass_from_invalid_profile() {
        let (_provider, _governed, plan) = fixture_plan();
        let transport = ScriptedTransport::with_incoming(vec![
            initialize_response(),
            json!({
                "id": 2,
                "error": { "code": -32602, "message": "invalid permission profile" }
            }),
        ]);
        let mut verifier = CodexConfinementVerifier::new(transport);
        verifier.initialize().unwrap();

        assert!(matches!(
            verifier.certify(&plan),
            Err(CodexConfinementError::PositiveControlRejected(_))
        ));
    }

    #[test]
    fn geh_cf_038_confinement_rejects_thread_profile_mismatch() {
        let (_provider, _governed, plan) = fixture_plan();
        let transport = ScriptedTransport::with_incoming(vec![
            initialize_response(),
            positive_response(),
            denied_response(),
            thread_response(":read-only"),
        ]);
        let mut verifier = CodexConfinementVerifier::new(transport);
        verifier.initialize().unwrap();

        assert!(matches!(
            verifier.certify(&plan),
            Err(CodexConfinementError::ActiveProfileMismatch { .. })
        ));
    }

    #[test]
    fn confinement_requires_host_to_prove_the_sentinel_before_provider_probe() {
        let provider = TestRoot::new("provider");
        let governed = TestRoot::new("governed");
        let forbidden = governed.write("sentinel.txt", "different-marker");
        let plan = ConfinementProbePlan::linux_file_read(
            "monad-geh-confinement",
            provider.path(),
            forbidden,
            "expected-marker",
        );
        let transport = ScriptedTransport::with_incoming(vec![initialize_response()]);
        let mut verifier = CodexConfinementVerifier::new(transport);
        verifier.initialize().unwrap();

        assert!(matches!(
            verifier.certify(&plan),
            Err(CodexConfinementError::HostSentinelMismatch)
        ));
    }
}
