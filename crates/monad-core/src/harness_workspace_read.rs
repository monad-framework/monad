//! Bounded, local-first read-only workspace operation backend for governed execution.
//!
//! The backend implements one concrete operation family: `workspace.read_text`.
//! Governance remains in [`crate::harness_gateway`]; this module only executes a
//! request after the gateway has admitted it. Raw file contents are retained as
//! a transient observation and are deliberately kept out of the serialized
//! governed decision/evidence record.

use std::{
    collections::BTreeMap,
    fs::{self, File},
    io::{self, Read},
    path::{Path, PathBuf},
};

use sha2::{Digest, Sha256};

use crate::{
    harness::{ExecutionEnvelope, OperationDisposition, OperationId, OperationRequest},
    harness_gateway::{
        BackendExecution, MediatedOperationResult, OperationBackend, OperationGovernanceContext,
        mediate_operation,
    },
};

pub const WORKSPACE_TOOL: &str = "workspace";
pub const WORKSPACE_READ_CAPABILITY: &str = "workspace.read";
pub const WORKSPACE_READ_TEXT_OPERATION: &str = "read_text";

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct WorkspaceTextObservation {
    pub relative_path: String,
    pub text: String,
    pub byte_length: u64,
    pub content_digest: String,
}

/// Result returned to the local Tool Gateway caller.
///
/// `mediated` is safe to serialize as governed decision/effect metadata. The
/// raw `observation` is intentionally a separate transient value so reading a
/// file does not automatically make its contents durable audit evidence.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct WorkspaceReadOutcome {
    pub mediated: MediatedOperationResult,
    pub observation: Option<WorkspaceTextObservation>,
}

#[derive(Debug)]
pub struct WorkspaceReadBackend {
    canonical_root: PathBuf,
    max_bytes: u64,
    observations: BTreeMap<OperationId, WorkspaceTextObservation>,
}

impl WorkspaceReadBackend {
    pub fn new(root: impl AsRef<Path>, max_bytes: u64) -> io::Result<Self> {
        if max_bytes == 0 {
            return Err(io::Error::new(
                io::ErrorKind::InvalidInput,
                "workspace read max_bytes must be greater than zero",
            ));
        }

        let canonical_root = fs::canonicalize(root.as_ref())?;
        if !fs::metadata(&canonical_root)?.is_dir() {
            return Err(io::Error::new(
                io::ErrorKind::InvalidInput,
                "workspace read root must be a directory",
            ));
        }

        Ok(Self {
            canonical_root,
            max_bytes,
            observations: BTreeMap::new(),
        })
    }

    pub fn canonical_root(&self) -> &Path {
        &self.canonical_root
    }

    pub fn max_bytes(&self) -> u64 {
        self.max_bytes
    }

    pub fn take_observation(
        &mut self,
        operation_id: &OperationId,
    ) -> Option<WorkspaceTextObservation> {
        self.observations.remove(operation_id)
    }

    fn execute_read(&self, request: &OperationRequest) -> Result<WorkspaceTextObservation, String> {
        if request.tool != WORKSPACE_TOOL {
            return Err(format!(
                "workspace read backend does not implement tool {:?}",
                request.tool
            ));
        }
        if request.capability != WORKSPACE_READ_CAPABILITY {
            return Err(format!(
                "workspace read backend requires capability {:?}",
                WORKSPACE_READ_CAPABILITY
            ));
        }
        if request.operation_type != WORKSPACE_READ_TEXT_OPERATION {
            return Err(format!(
                "workspace read backend does not implement operation {:?}",
                request.operation_type
            ));
        }

        let (relative, portable_path) = validate_portable_relative_path(&request.target_scope)?;
        reject_symlink_components(&self.canonical_root, &relative)?;

        let candidate = self.canonical_root.join(&relative);
        let canonical_target = fs::canonicalize(&candidate).map_err(|error| {
            format!("cannot resolve workspace target {portable_path:?}: {error}")
        })?;

        if !canonical_target.starts_with(&self.canonical_root) {
            return Err(format!(
                "workspace target {portable_path:?} resolves outside the workspace root"
            ));
        }

        // Inspect the target before opening it so pre-existing special files
        // such as FIFOs cannot block the governed read at File::open.
        let pre_open_metadata = fs::metadata(&canonical_target).map_err(|error| {
            format!("cannot inspect workspace target {portable_path:?}: {error}")
        })?;
        validate_regular_file_metadata(&portable_path, &pre_open_metadata, self.max_bytes)?;

        let file = File::open(&canonical_target)
            .map_err(|error| format!("cannot open workspace target {portable_path:?}: {error}"))?;
        let post_open_metadata = file.metadata().map_err(|error| {
            format!("cannot inspect opened workspace target {portable_path:?}: {error}")
        })?;
        validate_regular_file_metadata(&portable_path, &post_open_metadata, self.max_bytes)?;

        let mut bytes = Vec::new();
        let mut limited = file.take(self.max_bytes.saturating_add(1));
        limited
            .read_to_end(&mut bytes)
            .map_err(|error| format!("cannot read workspace target {portable_path:?}: {error}"))?;
        if bytes.len() as u64 > self.max_bytes {
            return Err(format!(
                "workspace target {portable_path:?} exceeded the {} byte read limit while reading",
                self.max_bytes
            ));
        }

        let byte_length = bytes.len() as u64;
        let content_digest = sha256_hex(&bytes);
        let text = String::from_utf8(bytes)
            .map_err(|_| format!("workspace target {portable_path:?} is not valid UTF-8 text"))?;

        Ok(WorkspaceTextObservation {
            relative_path: portable_path,
            text,
            byte_length,
            content_digest,
        })
    }
}

impl OperationBackend for WorkspaceReadBackend {
    fn execute(&mut self, request: &OperationRequest) -> BackendExecution {
        // Never allow a repeated operation ID to expose stale observation data.
        self.observations.remove(&request.operation_id);

        match self.execute_read(request) {
            Ok(observation) => {
                let digest = observation.content_digest.clone();
                let evidence_reference = format!(
                    "workspace-read:{}:sha256:{digest}",
                    observation.relative_path
                );
                self.observations
                    .insert(request.operation_id.clone(), observation);
                BackendExecution::Success {
                    result_digest: Some(digest),
                    evidence_reference: Some(evidence_reference),
                }
            }
            Err(diagnostic) => BackendExecution::ToolFailure { diagnostic },
        }
    }
}

/// Mediate one workspace read and return its transient observation only when the
/// governed operation actually executed successfully.
pub fn mediate_workspace_read(
    envelope: &ExecutionEnvelope,
    request: &OperationRequest,
    context: &OperationGovernanceContext,
    backend: &mut WorkspaceReadBackend,
) -> WorkspaceReadOutcome {
    let mediated = mediate_operation(envelope, request, context, backend);
    let observation = if mediated.result.disposition == OperationDisposition::ExecutedSuccess {
        backend.take_observation(&request.operation_id)
    } else {
        // Defensive cleanup in case a future backend implementation stages data
        // before returning a non-success disposition.
        backend.take_observation(&request.operation_id);
        None
    };

    WorkspaceReadOutcome {
        mediated,
        observation,
    }
}

fn validate_portable_relative_path(raw: &str) -> Result<(PathBuf, String), String> {
    if raw.is_empty() {
        return Err("workspace target path must be non-empty".into());
    }
    if raw.starts_with('/') || raw.contains('\\') || raw.contains('\0') {
        return Err(format!(
            "workspace target {raw:?} is not a portable repository-relative path"
        ));
    }

    let mut path = PathBuf::new();
    let mut normalized = Vec::new();
    for segment in raw.split('/') {
        if segment.is_empty() || segment == "." || segment == ".." || segment.contains(':') {
            return Err(format!(
                "workspace target {raw:?} contains a forbidden path segment"
            ));
        }
        path.push(segment);
        normalized.push(segment);
    }

    Ok((path, normalized.join("/")))
}

fn reject_symlink_components(root: &Path, relative: &Path) -> Result<(), String> {
    let mut current = root.to_path_buf();
    for component in relative.components() {
        current.push(component.as_os_str());
        let metadata = fs::symlink_metadata(&current).map_err(|error| {
            format!(
                "cannot inspect workspace path {}: {error}",
                current.display()
            )
        })?;
        if metadata.file_type().is_symlink() {
            return Err(format!(
                "workspace read refuses symlink component {}",
                current.display()
            ));
        }
    }
    Ok(())
}

fn validate_regular_file_metadata(
    portable_path: &str,
    metadata: &fs::Metadata,
    max_bytes: u64,
) -> Result<(), String> {
    if !metadata.is_file() {
        return Err(format!(
            "workspace target {portable_path:?} is not a regular file"
        ));
    }
    if metadata.len() > max_bytes {
        return Err(format!(
            "workspace target {portable_path:?} exceeds the {max_bytes} byte read limit"
        ));
    }
    Ok(())
}

fn sha256_hex(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let digest = Sha256::digest(bytes);
    let mut output = String::with_capacity(digest.len() * 2);
    for byte in digest {
        output.push(HEX[(byte >> 4) as usize] as char);
        output.push(HEX[(byte & 0x0f) as usize] as char);
    }
    output
}

#[cfg(test)]
mod tests {
    use std::{
        collections::BTreeMap,
        fs,
        path::PathBuf,
        time::{SystemTime, UNIX_EPOCH},
    };

    use super::*;
    use crate::{
        harness::{
            ActorIdentity, CapabilityGrant, ExecutionEnvelopeDraft, GovernedReference, RunId,
            compile_execution_envelope,
        },
        harness_gateway::{OperationGovernanceContext, PolicyDecision},
    };

    struct TestWorkspace(PathBuf);

    impl TestWorkspace {
        fn new(label: &str) -> Self {
            let nonce = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("clock after epoch")
                .as_nanos();
            let path = std::env::temp_dir().join(format!(
                "monad-harness-workspace-read-{label}-{}-{nonce}",
                std::process::id()
            ));
            fs::create_dir_all(&path).expect("create test workspace");
            Self(path)
        }

        fn root(&self) -> &Path {
            &self.0
        }

        fn write(&self, relative: &str, bytes: &[u8]) {
            let path = self.0.join(relative);
            if let Some(parent) = path.parent() {
                fs::create_dir_all(parent).expect("create parent");
            }
            fs::write(path, bytes).expect("write fixture");
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
            run_id: RunId("run-workspace-read-0001".into()),
            logical_time: "2026-09-01T18:00:00Z".into(),
            work_subject: "WP-HARNESS-WORKSPACE-READ".into(),
            intent: "read one bounded workspace text file".into(),
            requested_outcome: "transient governed text observation".into(),
            governing_state_digest: "state-workspace-read".into(),
            governed_references: vec![GovernedReference::new("spec", "TECH-HARNESS-0002")],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new("adapter:test", "executor"),
            granted_capabilities: vec![CapabilityGrant::new(WORKSPACE_READ_CAPABILITY, scope)],
            prohibited_capabilities: vec![],
            allowed_tools: vec![WORKSPACE_TOOL.into()],
            environment_constraints: vec!["local-first".into(), "read-only".into()],
            acceptance_criteria: vec!["only the exact governed target may be read".into()],
            verification_obligations: vec![
                "cargo test -p monad-core harness_workspace_read".into(),
            ],
            approval_gates: vec![],
            escalation_conditions: vec!["workspace path cannot be safely resolved".into()],
            completion_criteria: vec!["read observation is attributable and digest-bound".into()],
            resource_limits: BTreeMap::from([("workspace_read_max_bytes".into(), "4096".into())]),
        })
    }

    fn request(envelope: &ExecutionEnvelope, scope: &str) -> OperationRequest {
        OperationRequest {
            operation_id: OperationId("op-workspace-read-0001".into()),
            run_id: envelope.run_id().clone(),
            envelope_id: envelope.envelope_id().clone(),
            executor_actor_id: envelope.executor().actor_id.clone(),
            capability: WORKSPACE_READ_CAPABILITY.into(),
            tool: WORKSPACE_TOOL.into(),
            operation_type: WORKSPACE_READ_TEXT_OPERATION.into(),
            target_scope: scope.into(),
            parameters_digest: "sha256-empty-parameters".into(),
            causal_parent: None,
            idempotency_key: None,
        }
    }

    fn context() -> OperationGovernanceContext {
        OperationGovernanceContext {
            current_governing_state_digest: "state-workspace-read".into(),
            run_state: crate::harness::RunState::Running,
            policy: PolicyDecision::Allow,
            approved_gates: vec![],
        }
    }

    #[test]
    fn harness_workspace_read_authorized_text_returns_transient_observation() {
        let workspace = TestWorkspace::new("success");
        workspace.write("docs/input.txt", b"governed observation\n");
        let envelope = envelope("docs/input.txt");
        let request = request(&envelope, "docs/input.txt");
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let outcome = mediate_workspace_read(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.mediated.result.disposition,
            OperationDisposition::ExecutedSuccess
        );
        let observation = outcome.observation.expect("observation");
        assert_eq!(observation.relative_path, "docs/input.txt");
        assert_eq!(observation.text, "governed observation\n");
        assert_eq!(observation.byte_length, 21);
        assert_eq!(
            outcome.mediated.result.result_digest.as_deref(),
            Some(observation.content_digest.as_str())
        );
    }

    #[test]
    fn harness_workspace_read_raw_content_is_not_serialized_as_governed_evidence() {
        let workspace = TestWorkspace::new("transient");
        workspace.write("secret.txt", b"transient-sensitive-content");
        let envelope = envelope("secret.txt");
        let request = request(&envelope, "secret.txt");
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let outcome = mediate_workspace_read(&envelope, &request, &context(), &mut backend);
        let serialized = serde_json::to_string(&outcome.mediated).unwrap();

        assert!(!serialized.contains("transient-sensitive-content"));
        assert_eq!(
            outcome
                .observation
                .as_ref()
                .map(|value| value.text.as_str()),
            Some("transient-sensitive-content")
        );
    }

    #[test]
    fn harness_workspace_read_parent_traversal_fails_even_if_erroneously_granted() {
        let workspace = TestWorkspace::new("traversal");
        let envelope = envelope("../outside.txt");
        let request = request(&envelope, "../outside.txt");
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let outcome = mediate_workspace_read(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.mediated.result.disposition,
            OperationDisposition::ToolFailure
        );
        assert!(outcome.observation.is_none());
    }

    #[test]
    fn harness_workspace_read_absolute_path_fails_even_if_erroneously_granted() {
        let workspace = TestWorkspace::new("absolute");
        let envelope = envelope("/etc/passwd");
        let request = request(&envelope, "/etc/passwd");
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let outcome = mediate_workspace_read(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.mediated.result.disposition,
            OperationDisposition::ToolFailure
        );
        assert!(outcome.observation.is_none());
    }

    #[test]
    fn harness_workspace_read_directory_is_not_a_text_file() {
        let workspace = TestWorkspace::new("directory");
        fs::create_dir_all(workspace.root().join("docs")).unwrap();
        let envelope = envelope("docs");
        let request = request(&envelope, "docs");
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let outcome = mediate_workspace_read(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.mediated.result.disposition,
            OperationDisposition::ToolFailure
        );
        assert!(outcome.observation.is_none());
    }

    #[test]
    fn harness_workspace_read_enforces_backend_byte_limit() {
        let workspace = TestWorkspace::new("limit");
        workspace.write("large.txt", b"123456789");
        let envelope = envelope("large.txt");
        let request = request(&envelope, "large.txt");
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 8).unwrap();

        let outcome = mediate_workspace_read(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.mediated.result.disposition,
            OperationDisposition::ToolFailure
        );
        assert!(outcome.observation.is_none());
    }

    #[test]
    fn harness_workspace_read_rejects_non_utf8_content() {
        let workspace = TestWorkspace::new("non-utf8");
        workspace.write("binary.bin", &[0xff, 0xfe, 0xfd]);
        let envelope = envelope("binary.bin");
        let request = request(&envelope, "binary.bin");
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let outcome = mediate_workspace_read(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.mediated.result.disposition,
            OperationDisposition::ToolFailure
        );
        assert!(outcome.observation.is_none());
    }

    #[test]
    fn harness_workspace_read_rejects_unsupported_operation() {
        let workspace = TestWorkspace::new("operation");
        workspace.write("input.txt", b"hello");
        let envelope = envelope("input.txt");
        let mut request = request(&envelope, "input.txt");
        request.operation_type = "write_text".into();
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let outcome = mediate_workspace_read(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.mediated.result.disposition,
            OperationDisposition::ToolFailure
        );
        assert!(outcome.observation.is_none());
        assert_eq!(
            fs::read_to_string(workspace.root().join("input.txt")).unwrap(),
            "hello"
        );
    }

    #[test]
    fn harness_workspace_read_gateway_denial_produces_no_observation() {
        let workspace = TestWorkspace::new("denied");
        workspace.write("allowed.txt", b"allowed");
        workspace.write("other.txt", b"other");
        let envelope = envelope("allowed.txt");
        let request = request(&envelope, "other.txt");
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let outcome = mediate_workspace_read(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.mediated.result.disposition,
            OperationDisposition::DeniedScope
        );
        assert!(outcome.observation.is_none());
    }

    #[cfg(unix)]
    #[test]
    fn harness_workspace_read_rejects_symlink_components() {
        use std::os::unix::fs::symlink;

        let workspace = TestWorkspace::new("symlink");
        let outside = TestWorkspace::new("outside");
        outside.write("outside.txt", b"outside");
        symlink(
            outside.root().join("outside.txt"),
            workspace.root().join("link.txt"),
        )
        .unwrap();

        let envelope = envelope("link.txt");
        let request = request(&envelope, "link.txt");
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let outcome = mediate_workspace_read(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.mediated.result.disposition,
            OperationDisposition::ToolFailure
        );
        assert!(outcome.observation.is_none());
    }

    #[cfg(unix)]
    #[test]
    fn harness_workspace_read_rejects_fifo_before_open() {
        use std::process::Command;

        let workspace = TestWorkspace::new("fifo");
        let fifo = workspace.root().join("pipe");
        let status = Command::new("mkfifo")
            .arg(&fifo)
            .status()
            .expect("run mkfifo");
        assert!(status.success(), "mkfifo fixture creation failed");

        let envelope = envelope("pipe");
        let request = request(&envelope, "pipe");
        let mut backend = WorkspaceReadBackend::new(workspace.root(), 4096).unwrap();

        let outcome = mediate_workspace_read(&envelope, &request, &context(), &mut backend);

        assert_eq!(
            outcome.mediated.result.disposition,
            OperationDisposition::ToolFailure
        );
        assert!(outcome.observation.is_none());
        assert!(
            outcome
                .mediated
                .result
                .diagnostic
                .as_deref()
                .is_some_and(|value| value.contains("not a regular file"))
        );
    }
}
