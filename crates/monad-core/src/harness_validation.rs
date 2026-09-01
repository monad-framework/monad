//! Validation and JSON ingestion for governed execution envelopes.
//!
//! The authoritative [`ExecutionEnvelope`] remains immutable and can only be
//! created by the compiler. External serialized input is first decoded into an
//! inspectable document, validated against the supported contract, and only
//! then recompiled into an authoritative envelope value.

use std::{
    collections::{BTreeMap, BTreeSet},
    error::Error,
    fmt,
};

use serde::{Deserialize, Serialize};

use crate::harness::{
    ActorIdentity, CapabilityGrant, ExecutionEnvelope, ExecutionEnvelopeDraft, GovernedReference,
    RunId, compile_execution_envelope,
};

pub const EXECUTION_ENVELOPE_SCHEMA_VERSION: &str = "0.1.0";

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GovernedReferenceDocument {
    pub kind: String,
    pub identifier: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub content_digest: Option<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ActorIdentityDocument {
    pub actor_id: String,
    pub role: String,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CapabilityGrantDocument {
    pub capability: String,
    pub scope: String,
}

/// Untrusted serialized representation of an Execution Envelope.
///
/// Decoding this type does not establish validity or authority. Call
/// [`validate_execution_envelope_document`] before using its contents for
/// governed execution.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExecutionEnvelopeDocument {
    pub envelope_id: String,
    pub envelope_digest: String,
    pub schema_version: String,
    pub run_id: String,
    pub logical_time: String,
    pub work_subject: String,
    pub intent: String,
    pub requested_outcome: String,
    pub governing_state_digest: String,
    pub governed_references: Vec<GovernedReferenceDocument>,
    pub initiating_actor: ActorIdentityDocument,
    pub executor: ActorIdentityDocument,
    pub granted_capabilities: Vec<CapabilityGrantDocument>,
    pub prohibited_capabilities: Vec<CapabilityGrantDocument>,
    pub allowed_tools: Vec<String>,
    pub environment_constraints: Vec<String>,
    pub acceptance_criteria: Vec<String>,
    pub verification_obligations: Vec<String>,
    pub approval_gates: Vec<String>,
    pub escalation_conditions: Vec<String>,
    pub completion_criteria: Vec<String>,
    pub resource_limits: BTreeMap<String, String>,
}

impl From<&ExecutionEnvelope> for ExecutionEnvelopeDocument {
    fn from(envelope: &ExecutionEnvelope) -> Self {
        Self {
            envelope_id: envelope.envelope_id().0.clone(),
            envelope_digest: envelope.envelope_digest().0.clone(),
            schema_version: envelope.schema_version().to_owned(),
            run_id: envelope.run_id().0.clone(),
            logical_time: envelope.logical_time().to_owned(),
            work_subject: envelope.work_subject().to_owned(),
            intent: envelope.intent().to_owned(),
            requested_outcome: envelope.requested_outcome().to_owned(),
            governing_state_digest: envelope.governing_state_digest().to_owned(),
            governed_references: envelope
                .governed_references()
                .iter()
                .map(|reference| GovernedReferenceDocument {
                    kind: reference.kind.clone(),
                    identifier: reference.identifier.clone(),
                    content_digest: reference.content_digest.clone(),
                })
                .collect(),
            initiating_actor: ActorIdentityDocument {
                actor_id: envelope.initiating_actor().actor_id.clone(),
                role: envelope.initiating_actor().role.clone(),
            },
            executor: ActorIdentityDocument {
                actor_id: envelope.executor().actor_id.clone(),
                role: envelope.executor().role.clone(),
            },
            granted_capabilities: envelope
                .granted_capabilities()
                .iter()
                .map(|grant| CapabilityGrantDocument {
                    capability: grant.capability.clone(),
                    scope: grant.scope.clone(),
                })
                .collect(),
            prohibited_capabilities: envelope
                .prohibited_capabilities()
                .iter()
                .map(|grant| CapabilityGrantDocument {
                    capability: grant.capability.clone(),
                    scope: grant.scope.clone(),
                })
                .collect(),
            allowed_tools: envelope.allowed_tools().to_vec(),
            environment_constraints: envelope.environment_constraints().to_vec(),
            acceptance_criteria: envelope.acceptance_criteria().to_vec(),
            verification_obligations: envelope.verification_obligations().to_vec(),
            approval_gates: envelope.approval_gates().to_vec(),
            escalation_conditions: envelope.escalation_conditions().to_vec(),
            completion_criteria: envelope.completion_criteria().to_vec(),
            resource_limits: envelope.resource_limits().clone(),
        }
    }
}

impl ExecutionEnvelopeDocument {
    fn to_draft(&self) -> ExecutionEnvelopeDraft {
        ExecutionEnvelopeDraft {
            schema_version: self.schema_version.clone(),
            run_id: RunId(self.run_id.clone()),
            logical_time: self.logical_time.clone(),
            work_subject: self.work_subject.clone(),
            intent: self.intent.clone(),
            requested_outcome: self.requested_outcome.clone(),
            governing_state_digest: self.governing_state_digest.clone(),
            governed_references: self
                .governed_references
                .iter()
                .map(|reference| GovernedReference {
                    kind: reference.kind.clone(),
                    identifier: reference.identifier.clone(),
                    content_digest: reference.content_digest.clone(),
                })
                .collect(),
            initiating_actor: ActorIdentity {
                actor_id: self.initiating_actor.actor_id.clone(),
                role: self.initiating_actor.role.clone(),
            },
            executor: ActorIdentity {
                actor_id: self.executor.actor_id.clone(),
                role: self.executor.role.clone(),
            },
            granted_capabilities: self
                .granted_capabilities
                .iter()
                .map(|grant| CapabilityGrant::new(grant.capability.clone(), grant.scope.clone()))
                .collect(),
            prohibited_capabilities: self
                .prohibited_capabilities
                .iter()
                .map(|grant| CapabilityGrant::new(grant.capability.clone(), grant.scope.clone()))
                .collect(),
            allowed_tools: self.allowed_tools.clone(),
            environment_constraints: self.environment_constraints.clone(),
            acceptance_criteria: self.acceptance_criteria.clone(),
            verification_obligations: self.verification_obligations.clone(),
            approval_gates: self.approval_gates.clone(),
            escalation_conditions: self.escalation_conditions.clone(),
            completion_criteria: self.completion_criteria.clone(),
            resource_limits: self.resource_limits.clone(),
        }
    }
}

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct EnvelopeValidationContext {
    /// Current authoritative governing-state digest when freshness is known and
    /// must be enforced at this boundary.
    pub current_governing_state_digest: Option<String>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum EnvelopeValidationError {
    UnsupportedSchemaVersion { found: String, supported: String },
    EmptyRequiredValue { field: String },
    EnvelopeDigestMismatch { expected: String, actual: String },
    EnvelopeIdMismatch { expected: String, actual: String },
    GoverningStateStale { bound: String, current: String },
    CapabilityConflict { capability: String, scope: String },
}

impl fmt::Display for EnvelopeValidationError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::UnsupportedSchemaVersion { found, supported } => {
                write!(
                    formatter,
                    "unsupported execution-envelope schema version {found:?}; supported version is {supported:?}"
                )
            }
            Self::EmptyRequiredValue { field } => {
                write!(
                    formatter,
                    "required execution-envelope value {field:?} is empty"
                )
            }
            Self::EnvelopeDigestMismatch { expected, actual } => {
                write!(
                    formatter,
                    "execution-envelope digest mismatch: expected {expected}, received {actual}"
                )
            }
            Self::EnvelopeIdMismatch { expected, actual } => {
                write!(
                    formatter,
                    "execution-envelope identifier mismatch: expected {expected}, received {actual}"
                )
            }
            Self::GoverningStateStale { bound, current } => {
                write!(
                    formatter,
                    "execution envelope is bound to governing state {bound}, but current state is {current}"
                )
            }
            Self::CapabilityConflict { capability, scope } => {
                write!(
                    formatter,
                    "capability {capability:?} is both granted and prohibited for scope {scope:?}"
                )
            }
        }
    }
}

impl Error for EnvelopeValidationError {}

#[derive(Debug)]
pub enum ExecutionEnvelopeJsonError {
    Decode(serde_json::Error),
    Invalid(Vec<EnvelopeValidationError>),
}

impl fmt::Display for ExecutionEnvelopeJsonError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Decode(error) => write!(formatter, "invalid execution-envelope JSON: {error}"),
            Self::Invalid(errors) => {
                write!(formatter, "execution envelope failed validation")?;
                for error in errors {
                    write!(formatter, "; {error}")?;
                }
                Ok(())
            }
        }
    }
}

impl Error for ExecutionEnvelopeJsonError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::Decode(error) => Some(error),
            Self::Invalid(_) => None,
        }
    }
}

/// Validate an untrusted serialized envelope document and return a freshly
/// compiled authoritative envelope when all C0 integrity checks pass.
pub fn validate_execution_envelope_document(
    document: &ExecutionEnvelopeDocument,
    context: &EnvelopeValidationContext,
) -> Result<ExecutionEnvelope, Vec<EnvelopeValidationError>> {
    let mut errors = Vec::new();

    if document.schema_version != EXECUTION_ENVELOPE_SCHEMA_VERSION {
        errors.push(EnvelopeValidationError::UnsupportedSchemaVersion {
            found: document.schema_version.clone(),
            supported: EXECUTION_ENVELOPE_SCHEMA_VERSION.to_owned(),
        });
    }

    validate_required_values(document, &mut errors);

    if let Some(current) = &context.current_governing_state_digest
        && current != &document.governing_state_digest
    {
        errors.push(EnvelopeValidationError::GoverningStateStale {
            bound: document.governing_state_digest.clone(),
            current: current.clone(),
        });
    }

    let compiled = compile_execution_envelope(document.to_draft());

    if document.schema_version == EXECUTION_ENVELOPE_SCHEMA_VERSION {
        if document.envelope_digest != compiled.envelope_digest().0 {
            errors.push(EnvelopeValidationError::EnvelopeDigestMismatch {
                expected: compiled.envelope_digest().0.clone(),
                actual: document.envelope_digest.clone(),
            });
        }

        if document.envelope_id != compiled.envelope_id().0 {
            errors.push(EnvelopeValidationError::EnvelopeIdMismatch {
                expected: compiled.envelope_id().0.clone(),
                actual: document.envelope_id.clone(),
            });
        }
    }

    let granted: BTreeSet<_> = compiled.granted_capabilities().iter().cloned().collect();
    for prohibition in compiled.prohibited_capabilities() {
        if granted.contains(prohibition) {
            errors.push(EnvelopeValidationError::CapabilityConflict {
                capability: prohibition.capability.clone(),
                scope: prohibition.scope.clone(),
            });
        }
    }

    if errors.is_empty() {
        Ok(compiled)
    } else {
        Err(errors)
    }
}

/// Revalidate an already-compiled envelope, including optional governing-state
/// freshness checks. This is useful before binding or resuming a run.
pub fn validate_execution_envelope(
    envelope: &ExecutionEnvelope,
    context: &EnvelopeValidationContext,
) -> Result<(), Vec<EnvelopeValidationError>> {
    validate_execution_envelope_document(&ExecutionEnvelopeDocument::from(envelope), context)
        .map(|_| ())
}

/// Decode JSON as untrusted data, validate C0 invariants, and return a compiled
/// immutable envelope. Callers never receive an authoritative envelope merely
/// because JSON deserialization succeeded.
pub fn parse_execution_envelope_json(
    json: &str,
    context: &EnvelopeValidationContext,
) -> Result<ExecutionEnvelope, ExecutionEnvelopeJsonError> {
    let document: ExecutionEnvelopeDocument =
        serde_json::from_str(json).map_err(ExecutionEnvelopeJsonError::Decode)?;

    validate_execution_envelope_document(&document, context)
        .map_err(ExecutionEnvelopeJsonError::Invalid)
}

pub fn serialize_execution_envelope_json(
    envelope: &ExecutionEnvelope,
) -> Result<String, serde_json::Error> {
    serde_json::to_string(&ExecutionEnvelopeDocument::from(envelope))
}

fn validate_required_values(
    document: &ExecutionEnvelopeDocument,
    errors: &mut Vec<EnvelopeValidationError>,
) {
    required("envelope_id", &document.envelope_id, errors);
    required("envelope_digest", &document.envelope_digest, errors);
    required("schema_version", &document.schema_version, errors);
    required("run_id", &document.run_id, errors);
    required("logical_time", &document.logical_time, errors);
    required("work_subject", &document.work_subject, errors);
    required("intent", &document.intent, errors);
    required("requested_outcome", &document.requested_outcome, errors);
    required(
        "governing_state_digest",
        &document.governing_state_digest,
        errors,
    );
    required(
        "initiating_actor.actor_id",
        &document.initiating_actor.actor_id,
        errors,
    );
    required(
        "initiating_actor.role",
        &document.initiating_actor.role,
        errors,
    );
    required("executor.actor_id", &document.executor.actor_id, errors);
    required("executor.role", &document.executor.role, errors);

    for (index, reference) in document.governed_references.iter().enumerate() {
        required(
            &format!("governed_references[{index}].kind"),
            &reference.kind,
            errors,
        );
        required(
            &format!("governed_references[{index}].identifier"),
            &reference.identifier,
            errors,
        );
        if let Some(digest) = &reference.content_digest {
            required(
                &format!("governed_references[{index}].content_digest"),
                digest,
                errors,
            );
        }
    }

    validate_capabilities(
        "granted_capabilities",
        &document.granted_capabilities,
        errors,
    );
    validate_capabilities(
        "prohibited_capabilities",
        &document.prohibited_capabilities,
        errors,
    );

    validate_strings("allowed_tools", &document.allowed_tools, errors);
    validate_strings(
        "environment_constraints",
        &document.environment_constraints,
        errors,
    );
    validate_strings("acceptance_criteria", &document.acceptance_criteria, errors);
    validate_strings(
        "verification_obligations",
        &document.verification_obligations,
        errors,
    );
    validate_strings("approval_gates", &document.approval_gates, errors);
    validate_strings(
        "escalation_conditions",
        &document.escalation_conditions,
        errors,
    );
    validate_strings("completion_criteria", &document.completion_criteria, errors);

    for (key, value) in &document.resource_limits {
        required("resource_limits key", key, errors);
        required(&format!("resource_limits[{key}]"), value, errors);
    }
}

fn validate_capabilities(
    field: &str,
    capabilities: &[CapabilityGrantDocument],
    errors: &mut Vec<EnvelopeValidationError>,
) {
    for (index, grant) in capabilities.iter().enumerate() {
        required(
            &format!("{field}[{index}].capability"),
            &grant.capability,
            errors,
        );
        required(&format!("{field}[{index}].scope"), &grant.scope, errors);
    }
}

fn validate_strings(field: &str, values: &[String], errors: &mut Vec<EnvelopeValidationError>) {
    for (index, value) in values.iter().enumerate() {
        required(&format!("{field}[{index}]"), value, errors);
    }
}

fn required(field: &str, value: &str, errors: &mut Vec<EnvelopeValidationError>) {
    if value.trim().is_empty() {
        errors.push(EnvelopeValidationError::EmptyRequiredValue {
            field: field.to_owned(),
        });
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn draft() -> ExecutionEnvelopeDraft {
        ExecutionEnvelopeDraft {
            schema_version: EXECUTION_ENVELOPE_SCHEMA_VERSION.into(),
            run_id: RunId("run-c0-0001".into()),
            logical_time: "2026-09-01T12:00:00Z".into(),
            work_subject: "WP-HARNESS-C0".into(),
            intent: "validate execution-envelope C0 conformance".into(),
            requested_outcome: "validated immutable envelope".into(),
            governing_state_digest: "state-c0".into(),
            governed_references: vec![
                GovernedReference::new("adr", "ADR-0007"),
                GovernedReference::new("spec", "DATA-HARNESS-0001"),
            ],
            initiating_actor: ActorIdentity::new("human:owner", "engineering_owner"),
            executor: ActorIdentity::new("adapter:test", "executor"),
            granted_capabilities: vec![CapabilityGrant::new("fs.read", "workspace/**")],
            prohibited_capabilities: vec![CapabilityGrant::new("release.publish", "*")],
            allowed_tools: vec!["filesystem".into()],
            environment_constraints: vec!["local-first".into()],
            acceptance_criteria: vec!["C0 fixtures pass".into()],
            verification_obligations: vec!["cargo test -p monad-core".into()],
            approval_gates: vec![],
            escalation_conditions: vec!["governing state becomes stale".into()],
            completion_criteria: vec!["required C0 evidence passes".into()],
            resource_limits: BTreeMap::from([
                ("max_operations".into(), "100".into()),
                ("max_seconds".into(), "60".into()),
            ]),
        }
    }

    fn has_error(
        errors: &[EnvelopeValidationError],
        predicate: impl Fn(&EnvelopeValidationError) -> bool,
    ) -> bool {
        errors.iter().any(predicate)
    }

    #[test]
    fn geh_cf_001_equivalent_inputs_have_same_identity() {
        let left = compile_execution_envelope(draft());
        let mut reordered = draft();
        reordered.governed_references.reverse();
        reordered.allowed_tools.push("filesystem".into());
        reordered
            .acceptance_criteria
            .push("C0 fixtures pass".into());
        let right = compile_execution_envelope(reordered);

        assert_eq!(left.envelope_id(), right.envelope_id());
        assert_eq!(left.envelope_digest(), right.envelope_digest());
    }

    #[test]
    fn geh_cf_002_material_governing_state_change_changes_identity() {
        let before = compile_execution_envelope(draft());
        let mut changed = draft();
        changed.governing_state_digest = "state-c0-changed".into();
        let after = compile_execution_envelope(changed);

        assert_ne!(before.envelope_id(), after.envelope_id());
        assert_ne!(before.envelope_digest(), after.envelope_digest());
    }

    #[test]
    fn geh_cf_003_digest_and_identifier_mismatch_are_rejected() {
        let envelope = compile_execution_envelope(draft());
        let mut document = ExecutionEnvelopeDocument::from(&envelope);
        document.envelope_digest = "0".repeat(64);
        document.envelope_id = format!("env-v1-{}", "1".repeat(64));

        let errors =
            validate_execution_envelope_document(&document, &EnvelopeValidationContext::default())
                .expect_err("mismatched identity must fail closed");

        assert!(has_error(&errors, |error| matches!(
            error,
            EnvelopeValidationError::EnvelopeDigestMismatch { .. }
        )));
        assert!(has_error(&errors, |error| matches!(
            error,
            EnvelopeValidationError::EnvelopeIdMismatch { .. }
        )));
    }

    #[test]
    fn geh_cf_004_unsupported_schema_version_is_rejected() {
        let envelope = compile_execution_envelope(draft());
        let mut document = ExecutionEnvelopeDocument::from(&envelope);
        document.schema_version = "9.0.0".into();

        let errors =
            validate_execution_envelope_document(&document, &EnvelopeValidationContext::default())
                .expect_err("unsupported schema must fail closed");

        assert!(has_error(&errors, |error| matches!(
            error,
            EnvelopeValidationError::UnsupportedSchemaVersion { .. }
        )));
    }

    #[test]
    fn geh_cf_005_exact_capability_conflict_fails_closed() {
        let mut conflicting = draft();
        conflicting.granted_capabilities = vec![CapabilityGrant::new("fs.write", "src/**")];
        conflicting.prohibited_capabilities = vec![CapabilityGrant::new("fs.write", "src/**")];
        let envelope = compile_execution_envelope(conflicting);
        let document = ExecutionEnvelopeDocument::from(&envelope);

        let errors =
            validate_execution_envelope_document(&document, &EnvelopeValidationContext::default())
                .expect_err("contradictory capability must fail closed");

        assert!(has_error(&errors, |error| matches!(
            error,
            EnvelopeValidationError::CapabilityConflict { capability, scope }
                if capability == "fs.write" && scope == "src/**"
        )));
    }

    #[test]
    fn geh_cf_006_secret_reference_serializes_without_raw_secret() {
        let mut secret_aware = draft();
        secret_aware.granted_capabilities.push(CapabilityGrant::new(
            "secret.read",
            "ref:secret/github-token",
        ));
        let envelope = compile_execution_envelope(secret_aware);
        let json = serialize_execution_envelope_json(&envelope).expect("serialize envelope");

        assert!(json.contains("ref:secret/github-token"));
        assert!(!json.contains("super-secret-token-value"));
    }

    #[test]
    fn json_round_trip_revalidates_identity() {
        let envelope = compile_execution_envelope(draft());
        let json = serialize_execution_envelope_json(&envelope).expect("serialize envelope");
        let parsed = parse_execution_envelope_json(&json, &EnvelopeValidationContext::default())
            .expect("round-trip envelope validates");

        assert_eq!(parsed, envelope);
    }

    #[test]
    fn governing_state_freshness_is_enforced_when_supplied() {
        let envelope = compile_execution_envelope(draft());
        let context = EnvelopeValidationContext {
            current_governing_state_digest: Some("different-current-state".into()),
        };

        let errors = validate_execution_envelope(&envelope, &context)
            .expect_err("stale governing state must fail closed");

        assert!(has_error(&errors, |error| matches!(
            error,
            EnvelopeValidationError::GoverningStateStale { .. }
        )));
    }

    #[test]
    fn malformed_required_value_is_rejected() {
        let envelope = compile_execution_envelope(draft());
        let mut document = ExecutionEnvelopeDocument::from(&envelope);
        document.executor.actor_id.clear();

        let errors =
            validate_execution_envelope_document(&document, &EnvelopeValidationContext::default())
                .expect_err("empty required actor identity must be rejected");

        assert!(has_error(&errors, |error| matches!(
            error,
            EnvelopeValidationError::EmptyRequiredValue { field }
                if field == "executor.actor_id"
        )));
    }

    #[test]
    fn resource_limit_serialization_is_deterministically_key_ordered() {
        let envelope = compile_execution_envelope(draft());
        let json = serialize_execution_envelope_json(&envelope).expect("serialize envelope");

        let operations = json.find("max_operations").expect("operations key");
        let seconds = json.find("max_seconds").expect("seconds key");
        assert!(operations < seconds);
    }

    #[test]
    fn unknown_json_field_is_rejected_before_validation() {
        let envelope = compile_execution_envelope(draft());
        let json = serialize_execution_envelope_json(&envelope).expect("serialize envelope");
        let mut value: serde_json::Value = serde_json::from_str(&json).expect("decode value");
        value
            .as_object_mut()
            .expect("envelope object")
            .insert("unapproved_extension".into(), serde_json::json!(true));

        let malformed = serde_json::to_string(&value).expect("serialize mutated value");
        let error =
            parse_execution_envelope_json(&malformed, &EnvelopeValidationContext::default())
                .expect_err("unknown field must not silently extend mandatory semantics");

        assert!(matches!(error, ExecutionEnvelopeJsonError::Decode(_)));
    }
}
