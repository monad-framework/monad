//! Effectful OpenAI Codex App Server transport for Monad GEH C2.
//!
//! `monad-core` owns deterministic authority and mediation semantics. This crate
//! owns the replaceable process/JSONL boundary: launching App Server, performing
//! the initialization handshake, registering Monad's dynamic tool, routing
//! `item/tool/call` requests through the core adapter, and mapping
//! `turn/completed` back to verification-controlled completion.
//!
//! Version 0.1.0 intentionally distinguishes protocol conformance from a claim
//! that a live Codex process is safe for governed dogfood execution. Codex also
//! has provider-native tools. Until their access to the governed workspace can
//! be independently confined and verified, live dogfood eligibility fails
//! closed even though this transport can be exercised against a real or
//! scripted App Server.

use std::{
    collections::VecDeque,
    error::Error,
    ffi::OsStr,
    fmt,
    io::{BufRead, BufReader, BufWriter, Write},
    path::Path,
    process::{Child, ChildStdin, ChildStdout, Command, Stdio},
};

use monad_core::{
    harness::ExecutionEnvelope,
    harness_adapter::{AdapterInitializationOutcome, AdapterSessionId},
    harness_codex_adapter::{
        CODEX_ADAPTER_ID, CODEX_ADAPTER_VERSION, CODEX_WORKSPACE_READ_TOOL, CodexAdapterSession,
        CodexDynamicToolCallDocument, CodexDynamicToolContentItem, CodexDynamicToolResponse,
        bind_codex_thread, handle_codex_turn_completed, initialize_codex_adapter,
        mediate_codex_dynamic_tool_call,
    },
    harness_gateway::OperationGovernanceContext,
    harness_verification::{AdapterCompletionResponse, VerificationEvidenceBundle},
    harness_workspace_read::WorkspaceReadBackend,
};
use serde::Serialize;
use serde_json::{Value, json};

const APP_SERVER_INITIALIZE: &str = "initialize";
const APP_SERVER_INITIALIZED: &str = "initialized";
const APP_SERVER_THREAD_START: &str = "thread/start";
const APP_SERVER_TURN_START: &str = "turn/start";
const APP_SERVER_TURN_COMPLETED: &str = "turn/completed";
const APP_SERVER_DYNAMIC_TOOL_CALL: &str = "item/tool/call";
const APP_SERVER_TURN_INTERRUPT: &str = "turn/interrupt";

#[derive(Debug)]
pub enum CodexRuntimeError {
    Io(String),
    Json(String),
    Protocol(String),
    Adapter(String),
    ExecutorBindingMismatch { expected: String, actual: String },
    EffectConfinementUnproven { diagnostic: String },
}

impl fmt::Display for CodexRuntimeError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io(diagnostic) => write!(formatter, "Codex App Server I/O failed: {diagnostic}"),
            Self::Json(diagnostic) => {
                write!(formatter, "Codex App Server JSON was invalid: {diagnostic}")
            }
            Self::Protocol(diagnostic) => {
                write!(formatter, "Codex App Server protocol failed closed: {diagnostic}")
            }
            Self::Adapter(diagnostic) => {
                write!(formatter, "Monad Codex adapter rejected the request: {diagnostic}")
            }
            Self::ExecutorBindingMismatch { expected, actual } => write!(
                formatter,
                "execution envelope binds executor {actual:?}; Codex runtime requires {expected:?}"
            ),
            Self::EffectConfinementUnproven { diagnostic } => write!(
                formatter,
                "live governed Codex dogfood is not eligible: {diagnostic}"
            ),
        }
    }
}

impl Error for CodexRuntimeError {}

impl From<std::io::Error> for CodexRuntimeError {
    fn from(error: std::io::Error) -> Self {
        Self::Io(error.to_string())
    }
}

impl From<serde_json::Error> for CodexRuntimeError {
    fn from(error: serde_json::Error) -> Self {
        Self::Json(error.to_string())
    }
}

/// Minimal bidirectional JSONL transport required by Codex App Server.
///
/// App Server uses JSON-RPC 2.0 semantics with the `jsonrpc` member omitted on
/// the wire. Each stdio message occupies exactly one UTF-8 JSON line.
pub trait AppServerTransport {
    fn send(&mut self, message: &Value) -> Result<(), CodexRuntimeError>;
    fn receive(&mut self) -> Result<Value, CodexRuntimeError>;
}

/// Effectful stdio transport for a real `codex app-server` child process.
pub struct ProcessJsonlTransport {
    child: Child,
    stdin: BufWriter<ChildStdin>,
    stdout: BufReader<ChildStdout>,
}

impl ProcessJsonlTransport {
    pub fn spawn(
        executable: impl AsRef<OsStr>,
        args: &[String],
        process_cwd: Option<&Path>,
    ) -> Result<Self, CodexRuntimeError> {
        let mut command = Command::new(executable);
        command
            .args(args)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit());
        if let Some(cwd) = process_cwd {
            command.current_dir(cwd);
        }

        let mut child = command.spawn()?;
        let stdin = child
            .stdin
            .take()
            .ok_or_else(|| CodexRuntimeError::Io("child stdin was not piped".into()))?;
        let stdout = child
            .stdout
            .take()
            .ok_or_else(|| CodexRuntimeError::Io("child stdout was not piped".into()))?;

        Ok(Self {
            child,
            stdin: BufWriter::new(stdin),
            stdout: BufReader::new(stdout),
        })
    }

    pub fn spawn_codex(process_cwd: Option<&Path>) -> Result<Self, CodexRuntimeError> {
        Self::spawn("codex", &["app-server".into()], process_cwd)
    }

    pub fn child_id(&self) -> u32 {
        self.child.id()
    }
}

impl AppServerTransport for ProcessJsonlTransport {
    fn send(&mut self, message: &Value) -> Result<(), CodexRuntimeError> {
        serde_json::to_writer(&mut self.stdin, message)?;
        self.stdin.write_all(b"\n")?;
        self.stdin.flush()?;
        Ok(())
    }

    fn receive(&mut self) -> Result<Value, CodexRuntimeError> {
        let mut line = String::new();
        let bytes = self.stdout.read_line(&mut line)?;
        if bytes == 0 {
            return Err(CodexRuntimeError::Io(
                "Codex App Server closed stdout before the protocol completed".into(),
            ));
        }
        Ok(serde_json::from_str(&line)?)
    }
}

impl Drop for ProcessJsonlTransport {
    fn drop(&mut self) {
        if let Ok(None) = self.child.try_wait() {
            let _ = self.child.kill();
            let _ = self.child.wait();
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct CodexServerIdentity {
    pub user_agent: Option<String>,
    pub codex_home: Option<String>,
    pub platform_family: Option<String>,
    pub platform_os: Option<String>,
}

#[derive(Debug)]
pub struct CodexRuntimeSession {
    binding: CodexAdapterSession,
}

impl CodexRuntimeSession {
    pub fn binding(&self) -> &CodexAdapterSession {
        &self.binding
    }

    pub fn thread_id(&self) -> &str {
        self.binding.thread_id()
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct CodexTurnOutcome {
    pub thread_id: String,
    pub turn_id: String,
    pub dynamic_tool_calls: u64,
    pub completion: AdapterCompletionResponse,
}

/// Synchronous App Server driver. The synchronous design is deliberate for the
/// initial C2 bridge: protocol ordering remains inspectable and deterministic,
/// while provider/model cognition stays outside Monad.
pub struct CodexAppServerRuntime<T: AppServerTransport> {
    transport: T,
    next_request_id: u64,
    initialized: bool,
    deferred: VecDeque<Value>,
}

impl<T: AppServerTransport> CodexAppServerRuntime<T> {
    pub fn new(transport: T) -> Self {
        Self {
            transport,
            next_request_id: 1,
            initialized: false,
            deferred: VecDeque::new(),
        }
    }

    pub fn transport(&self) -> &T {
        &self.transport
    }

    pub fn transport_mut(&mut self) -> &mut T {
        &mut self.transport
    }

    pub fn initialize_connection(&mut self) -> Result<CodexServerIdentity, CodexRuntimeError> {
        if self.initialized {
            return Err(CodexRuntimeError::Protocol(
                "initialize may occur only once per App Server connection".into(),
            ));
        }

        let result = self.request(
            APP_SERVER_INITIALIZE,
            json!({
                "clientInfo": {
                    "name": "monad",
                    "title": "Monad Governed Execution Harness",
                    "version": CODEX_ADAPTER_VERSION
                },
                "capabilities": {
                    "experimentalApi": true
                }
            }),
        )?;
        self.transport
            .send(&json!({ "method": APP_SERVER_INITIALIZED, "params": {} }))?;
        self.initialized = true;

        Ok(CodexServerIdentity {
            user_agent: optional_string(&result, "userAgent"),
            codex_home: optional_string(&result, "codexHome"),
            platform_family: optional_string(&result, "platformFamily"),
            platform_os: optional_string(&result, "platformOs"),
        })
    }

    /// Start an ephemeral, read-only provider thread and bind it beneath the
    /// already-governed Monad run/envelope.
    ///
    /// The provider cwd is deliberately independent of the workspace root used
    /// by `WorkspaceReadBackend`. Callers should use an empty runtime directory
    /// rather than point Codex at governed repository content.
    pub fn start_read_only_session(
        &mut self,
        envelope: &ExecutionEnvelope,
        session_id: AdapterSessionId,
        provider_runtime_cwd: &Path,
    ) -> Result<CodexRuntimeSession, CodexRuntimeError> {
        self.require_initialized()?;
        if envelope.executor().actor_id != CODEX_ADAPTER_ID {
            return Err(CodexRuntimeError::ExecutorBindingMismatch {
                expected: CODEX_ADAPTER_ID.into(),
                actual: envelope.executor().actor_id.clone(),
            });
        }

        let initialized = initialize_codex_adapter(envelope, session_id);
        let adapter_session = match initialized {
            AdapterInitializationOutcome::Accepted(session) => session,
            AdapterInitializationOutcome::Rejected(reason) => {
                return Err(CodexRuntimeError::Adapter(format!(
                    "C2 initialization rejected: {reason:?}"
                )));
            }
        };

        let cwd = provider_runtime_cwd.to_str().ok_or_else(|| {
            CodexRuntimeError::Protocol("provider runtime cwd is not valid UTF-8".into())
        })?;
        let result = self.request(
            APP_SERVER_THREAD_START,
            json!({
                "cwd": cwd,
                "ephemeral": true,
                "sandbox": "readOnly",
                "approvalPolicy": "untrusted",
                "environments": [],
                "selectedCapabilityRoots": [],
                "dynamicTools": [workspace_read_dynamic_tool_spec()],
                "developerInstructions": "Use the Monad-provided dynamic tool for any governed workspace observation. Provider-native effects are not Monad authority."
            }),
        )?;
        let thread_id = result
            .pointer("/thread/id")
            .and_then(Value::as_str)
            .filter(|value| !value.trim().is_empty())
            .ok_or_else(|| {
                CodexRuntimeError::Protocol(
                    "thread/start response omitted a non-empty thread.id".into(),
                )
            })?;
        let binding = bind_codex_thread(adapter_session, thread_id.to_owned())
            .map_err(|error| CodexRuntimeError::Adapter(format!("{error:?}")))?;

        Ok(CodexRuntimeSession { binding })
    }

    /// Run one provider turn and service only the concrete Monad dynamic-tool
    /// request family. Any other App Server request fails closed.
    pub fn run_turn(
        &mut self,
        session: &CodexRuntimeSession,
        envelope: &ExecutionEnvelope,
        prompt: &str,
        governance: &OperationGovernanceContext,
        backend: &mut WorkspaceReadBackend,
        evidence: &VerificationEvidenceBundle,
    ) -> Result<CodexTurnOutcome, CodexRuntimeError> {
        self.require_initialized()?;
        if prompt.trim().is_empty() {
            return Err(CodexRuntimeError::Protocol(
                "turn prompt must be non-empty".into(),
            ));
        }

        let result = self.request(
            APP_SERVER_TURN_START,
            json!({
                "threadId": session.thread_id(),
                "input": [{ "type": "text", "text": prompt }],
                "sandboxPolicy": {
                    "type": "readOnly",
                    "networkAccess": false
                }
            }),
        )?;
        let turn_id = result
            .pointer("/turn/id")
            .and_then(Value::as_str)
            .filter(|value| !value.trim().is_empty())
            .ok_or_else(|| {
                CodexRuntimeError::Protocol("turn/start response omitted a non-empty turn.id".into())
            })?
            .to_owned();

        let mut dynamic_tool_calls = 0_u64;
        loop {
            let message = self.receive_message()?;
            let method = message.get("method").and_then(Value::as_str);
            match method {
                Some(APP_SERVER_DYNAMIC_TOOL_CALL) => {
                    let request_id = message.get("id").cloned().ok_or_else(|| {
                        CodexRuntimeError::Protocol(
                            "item/tool/call request omitted JSON-RPC id".into(),
                        )
                    })?;
                    let params = message.get("params").cloned().unwrap_or(Value::Null);
                    let call: CodexDynamicToolCallDocument = match serde_json::from_value(params) {
                        Ok(call) => call,
                        Err(error) => {
                            self.send_dynamic_tool_rejection(
                                request_id,
                                format!("malformed item/tool/call params: {error}"),
                            )?;
                            continue;
                        }
                    };
                    if call.turn_id != turn_id {
                        self.send_dynamic_tool_rejection(
                            request_id,
                            "dynamic tool call is not bound to the active turn".into(),
                        )?;
                        continue;
                    }

                    match mediate_codex_dynamic_tool_call(
                        session.binding(),
                        envelope,
                        &call,
                        governance,
                        backend,
                    ) {
                        Ok(mediated) => {
                            self.transport.send(&json!({
                                "id": request_id,
                                "result": mediated.codex_response
                            }))?;
                            dynamic_tool_calls += 1;
                        }
                        Err(error) => {
                            self.send_dynamic_tool_rejection(
                                request_id,
                                format!("Monad rejected dynamic tool request: {error:?}"),
                            )?;
                        }
                    }
                }
                Some(APP_SERVER_TURN_COMPLETED) => {
                    let params = message.get("params").ok_or_else(|| {
                        CodexRuntimeError::Protocol(
                            "turn/completed notification omitted params".into(),
                        )
                    })?;
                    let completed_thread = params
                        .get("threadId")
                        .and_then(Value::as_str)
                        .ok_or_else(|| {
                            CodexRuntimeError::Protocol(
                                "turn/completed omitted threadId".into(),
                            )
                        })?;
                    let completed_turn = params
                        .pointer("/turn/id")
                        .and_then(Value::as_str)
                        .ok_or_else(|| {
                            CodexRuntimeError::Protocol("turn/completed omitted turn.id".into())
                        })?;
                    if completed_thread != session.thread_id() || completed_turn != turn_id {
                        return Err(CodexRuntimeError::Protocol(
                            "turn/completed binding does not match active Monad adapter session"
                                .into(),
                        ));
                    }
                    let completion = handle_codex_turn_completed(
                        session.binding(),
                        envelope,
                        completed_thread,
                        completed_turn,
                        evidence,
                    )
                    .map_err(|error| CodexRuntimeError::Adapter(format!("{error:?}")))?;

                    return Ok(CodexTurnOutcome {
                        thread_id: completed_thread.to_owned(),
                        turn_id,
                        dynamic_tool_calls,
                        completion,
                    });
                }
                Some(_) if message.get("id").is_some() => {
                    self.reject_unexpected_server_request(&message)?;
                    return Err(CodexRuntimeError::Protocol(format!(
                        "unexpected App Server request method {:?}; only item/tool/call is accepted during governed turns",
                        method.unwrap_or_default()
                    )));
                }
                _ => {
                    // Notifications are observable provider progress only. They
                    // do not create Monad authority or lifecycle state.
                }
            }
        }
    }

    pub fn interrupt_turn(
        &mut self,
        thread_id: &str,
        turn_id: &str,
    ) -> Result<(), CodexRuntimeError> {
        self.require_initialized()?;
        self.request(
            APP_SERVER_TURN_INTERRUPT,
            json!({ "threadId": thread_id, "turnId": turn_id }),
        )?;
        Ok(())
    }

    /// Version 0.1.0 has not yet established a machine-verifiable guarantee
    /// that provider-native Codex command/filesystem tools cannot observe the
    /// governed repository outside Monad's Tool Gateway. Therefore a live run
    /// MUST NOT be labeled governed dogfood merely because the App Server
    /// transport and dynamic-tool adapter function correctly.
    pub fn require_live_governed_dogfood_eligibility(&self) -> Result<(), CodexRuntimeError> {
        Err(CodexRuntimeError::EffectConfinementUnproven {
            diagnostic: "read-only sandbox prevents writes but does not by itself prove that provider-native read/command tools cannot bypass GEH workspace.read mediation; add and verify a provider-effect confinement profile before activation".into(),
        })
    }

    fn request(&mut self, method: &str, params: Value) -> Result<Value, CodexRuntimeError> {
        let request_id = self.next_request_id;
        self.next_request_id = self
            .next_request_id
            .checked_add(1)
            .ok_or_else(|| CodexRuntimeError::Protocol("request id exhausted".into()))?;
        self.transport.send(&json!({
            "method": method,
            "id": request_id,
            "params": params
        }))?;

        loop {
            let message = self.receive_message()?;
            if message.get("id") == Some(&json!(request_id)) {
                if let Some(error) = message.get("error") {
                    return Err(CodexRuntimeError::Protocol(format!(
                        "{method} returned JSON-RPC error {error}"
                    )));
                }
                return message.get("result").cloned().ok_or_else(|| {
                    CodexRuntimeError::Protocol(format!(
                        "{method} response omitted both result and error"
                    ))
                });
            }

            if message.get("id").is_some() && message.get("method").is_some() {
                self.reject_unexpected_server_request(&message)?;
                return Err(CodexRuntimeError::Protocol(format!(
                    "App Server sent a server request while waiting for {method} response"
                )));
            }

            self.deferred.push_back(message);
        }
    }

    fn receive_message(&mut self) -> Result<Value, CodexRuntimeError> {
        if let Some(message) = self.deferred.pop_front() {
            return Ok(message);
        }
        self.transport.receive()
    }

    fn send_dynamic_tool_rejection(
        &mut self,
        request_id: Value,
        diagnostic: String,
    ) -> Result<(), CodexRuntimeError> {
        let response = CodexDynamicToolResponse {
            content_items: vec![CodexDynamicToolContentItem::InputText {
                text: format!("MONAD_ADAPTER_REJECTED {diagnostic}"),
            }],
            success: false,
        };
        self.transport
            .send(&json!({ "id": request_id, "result": response }))
    }

    fn reject_unexpected_server_request(
        &mut self,
        message: &Value,
    ) -> Result<(), CodexRuntimeError> {
        let Some(request_id) = message.get("id").cloned() else {
            return Ok(());
        };
        self.transport.send(&json!({
            "id": request_id,
            "error": {
                "code": -32601,
                "message": "Monad governed runtime does not authorize this App Server request"
            }
        }))
    }

    fn require_initialized(&self) -> Result<(), CodexRuntimeError> {
        if self.initialized {
            Ok(())
        } else {
            Err(CodexRuntimeError::Protocol(
                "App Server connection must be initialized first".into(),
            ))
        }
    }
}

fn workspace_read_dynamic_tool_spec() -> Value {
    json!({
        "type": "function",
        "name": CODEX_WORKSPACE_READ_TOOL,
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

fn optional_string(value: &Value, key: &str) -> Option<String> {
    value.get(key).and_then(Value::as_str).map(str::to_owned)
}

#[cfg(test)]
mod tests {
    use std::{
        collections::{BTreeMap, VecDeque},
        fs,
        path::{Path, PathBuf},
        time::{SystemTime, UNIX_EPOCH},
    };

    use monad_core::{
        harness::{
            ActorIdentity, CapabilityGrant, ExecutionEnvelopeDraft, RunId, RunState,
            compile_execution_envelope,
        },
        harness_gateway::{OperationGovernanceContext, PolicyDecision},
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
                CodexRuntimeError::Io("scripted App Server exhausted incoming messages".into())
            })
        }
    }

    struct TestWorkspace(PathBuf);

    impl TestWorkspace {
        fn new(label: &str) -> Self {
            let nonce = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("clock after epoch")
                .as_nanos();
            let path = std::env::temp_dir().join(format!(
                "monad-codex-runtime-{label}-{}-{nonce}",
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
                fs::create_dir_all(parent).expect("create fixture parent");
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
            run_id: RunId("run-codex-runtime-0001".into()),
            logical_time: "2026-09-01T21:00:00Z".into(),
            work_subject: "WP-HARNESS-CODEX-RUNTIME".into(),
            intent: "exercise Codex App Server through GEH".into(),
            requested_outcome: "one mediated workspace observation".into(),
            governing_state_digest: "state-codex-runtime".into(),
            governed_references: vec![],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new(CODEX_ADAPTER_ID, "executor"),
            granted_capabilities: vec![CapabilityGrant::new("workspace.read", scope)],
            prohibited_capabilities: vec![],
            allowed_tools: vec!["workspace".into()],
            environment_constraints: vec!["read-only".into()],
            acceptance_criteria: vec!["read remains exactly scoped".into()],
            verification_obligations: vec!["runtime conformance passes".into()],
            approval_gates: vec![],
            escalation_conditions: vec![],
            completion_criteria: vec!["result is attributable".into()],
            resource_limits: BTreeMap::new(),
        })
    }

    fn governance() -> OperationGovernanceContext {
        OperationGovernanceContext {
            current_governing_state_digest: "state-codex-runtime".into(),
            run_state: RunState::Running,
            policy: PolicyDecision::Allow,
            approved_gates: vec![],
        }
    }

    fn initialize_response() -> Value {
        json!({
            "id": 1,
            "result": {
                "userAgent": "codex-test/1",
                "codexHome": "/tmp/codex-home",
                "platformFamily": "unix",
                "platformOs": "linux"
            }
        })
    }

    fn thread_start_response() -> Value {
        json!({ "id": 2, "result": { "thread": { "id": "thr_runtime_0001" } } })
    }

    fn turn_start_response() -> Value {
        json!({ "id": 3, "result": { "turn": { "id": "turn_runtime_0001" } } })
    }

    #[test]
    fn c2_runtime_initialization_enables_experimental_api_and_registers_dynamic_tool() {
        let transport = ScriptedTransport::with_incoming(vec![
            initialize_response(),
            thread_start_response(),
        ]);
        let mut runtime = CodexAppServerRuntime::new(transport);
        let identity = runtime.initialize_connection().unwrap();
        let envelope = envelope("README.md");
        let runtime_cwd = TestWorkspace::new("provider-cwd");
        let session = runtime
            .start_read_only_session(
                &envelope,
                AdapterSessionId("session-runtime-0001".into()),
                runtime_cwd.root(),
            )
            .unwrap();

        assert_eq!(identity.user_agent.as_deref(), Some("codex-test/1"));
        assert_eq!(session.thread_id(), "thr_runtime_0001");
        let sent = &runtime.transport().sent;
        assert_eq!(sent[0]["method"], APP_SERVER_INITIALIZE);
        assert_eq!(
            sent[0]["params"]["capabilities"]["experimentalApi"],
            true
        );
        assert_eq!(sent[1]["method"], APP_SERVER_INITIALIZED);
        assert_eq!(sent[2]["method"], APP_SERVER_THREAD_START);
        assert_eq!(
            sent[2]["params"]["dynamicTools"][0]["name"],
            CODEX_WORKSPACE_READ_TOOL
        );
        assert_eq!(sent[2]["params"]["sandbox"], "readOnly");
        assert_eq!(sent[2]["params"]["environments"], json!([]));
    }

    #[test]
    fn c2_runtime_routes_real_wire_shape_through_workspace_read_and_verification() {
        let workspace = TestWorkspace::new("governed-workspace");
        workspace.write("docs/input.txt", "runtime governed observation\n");
        let provider_cwd = TestWorkspace::new("provider-cwd");
        let envelope = envelope("docs/input.txt");
        let transport = ScriptedTransport::with_incoming(vec![
            initialize_response(),
            thread_start_response(),
            turn_start_response(),
            json!({
                "method": APP_SERVER_DYNAMIC_TOOL_CALL,
                "id": 900,
                "params": {
                    "threadId": "thr_runtime_0001",
                    "turnId": "turn_runtime_0001",
                    "callId": "call_runtime_0001",
                    "tool": CODEX_WORKSPACE_READ_TOOL,
                    "arguments": { "path": "docs/input.txt" }
                }
            }),
            json!({
                "method": APP_SERVER_TURN_COMPLETED,
                "params": {
                    "threadId": "thr_runtime_0001",
                    "turn": { "id": "turn_runtime_0001", "status": "completed" }
                }
            }),
        ]);
        let mut runtime = CodexAppServerRuntime::new(transport);
        runtime.initialize_connection().unwrap();
        let session = runtime
            .start_read_only_session(
                &envelope,
                AdapterSessionId("session-runtime-0001".into()),
                provider_cwd.root(),
            )
            .unwrap();
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let outcome = runtime
            .run_turn(
                &session,
                &envelope,
                "Read docs/input.txt using the governed Monad tool.",
                &governance(),
                &mut backend,
                &VerificationEvidenceBundle::default(),
            )
            .unwrap();

        assert_eq!(outcome.dynamic_tool_calls, 1);
        assert_eq!(outcome.turn_id, "turn_runtime_0001");
        assert_eq!(
            outcome.completion.assessment.disposition,
            CompletionDisposition::Incomplete
        );
        let tool_response = runtime
            .transport()
            .sent
            .iter()
            .find(|message| message.get("id") == Some(&json!(900)))
            .expect("dynamic tool response");
        assert_eq!(tool_response["result"]["success"], true);
        assert_eq!(
            tool_response["result"]["contentItems"][1]["text"],
            "runtime governed observation\n"
        );
    }

    #[test]
    fn c2_runtime_rejects_unexpected_provider_approval_request() {
        let workspace = TestWorkspace::new("workspace");
        workspace.write("README.md", "hello");
        let provider_cwd = TestWorkspace::new("provider-cwd");
        let envelope = envelope("README.md");
        let transport = ScriptedTransport::with_incoming(vec![
            initialize_response(),
            thread_start_response(),
            turn_start_response(),
            json!({
                "method": "item/commandExecution/requestApproval",
                "id": 901,
                "params": { "threadId": "thr_runtime_0001" }
            }),
        ]);
        let mut runtime = CodexAppServerRuntime::new(transport);
        runtime.initialize_connection().unwrap();
        let session = runtime
            .start_read_only_session(
                &envelope,
                AdapterSessionId("session-runtime-0001".into()),
                provider_cwd.root(),
            )
            .unwrap();
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let error = runtime
            .run_turn(
                &session,
                &envelope,
                "Attempt a read.",
                &governance(),
                &mut backend,
                &VerificationEvidenceBundle::default(),
            )
            .unwrap_err();

        assert!(matches!(error, CodexRuntimeError::Protocol(_)));
        let rejection = runtime
            .transport()
            .sent
            .iter()
            .find(|message| message.get("id") == Some(&json!(901)))
            .expect("unexpected request rejection");
        assert_eq!(rejection["error"]["code"], -32601);
    }

    #[test]
    fn live_governed_dogfood_fails_closed_until_provider_effect_confinement_is_verified() {
        let runtime = CodexAppServerRuntime::new(ScriptedTransport::default());
        assert!(matches!(
            runtime.require_live_governed_dogfood_eligibility(),
            Err(CodexRuntimeError::EffectConfinementUnproven { .. })
        ));
    }
}
