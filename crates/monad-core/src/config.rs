//! Semantic adaptation of canonical `monad.toml` after bootstrap validation.
//!
//! This module deliberately reuses the workspace bootstrap validator. It does not
//! implement configuration precedence, consult legacy manifests, interpolate the
//! environment, execute repository code, perform network access, or process includes.

use std::str;

use serde::Serialize;

use crate::{
    discovery::{DiscoveredSource, DiscoveryProvenance, SourceKindCandidate},
    identity::{DocumentIdentity, ParserContract, SourceRecord},
    workspace::{
        BootstrapError, CliOverrides, Diagnostic, DiagnosticCode, EffectiveConfiguration,
        parse_effective_configuration,
    },
};

pub const CONFIG_PARSER_CONTRACT: &str = "monad.structured-configuration";
pub const CONFIG_PARSER_VERSION: &str = "1";
pub const CONFIG_DOCUMENT_KIND: &str = "monad_configuration";

/// A semantic configuration document keeps canonical source/default values separate
/// from run-effective values. This is required because CLI overrides affect the run
/// without editing or replacing canonical `monad.toml` facts.
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ParsedConfigurationDocument {
    pub identity: DocumentIdentity,
    pub canonical_configuration: EffectiveConfiguration,
    pub effective_configuration: EffectiveConfiguration,
}

pub fn config_parser_contract() -> ParserContract {
    ParserContract::new(CONFIG_PARSER_CONTRACT, CONFIG_PARSER_VERSION)
}

/// Adapt exact canonical `monad.toml` bytes into semantic state after bootstrap has
/// produced the supplied effective configuration.
///
/// The exact bytes are parsed again with *no* CLI overrides through the same bootstrap
/// validator. That recovers canonical file/default values and provenance while the
/// separately supplied effective configuration retains any run-local CLI provenance.
pub fn parse_monad_configuration(
    bytes: &[u8],
    effective_configuration: &EffectiveConfiguration,
) -> Result<ParsedConfigurationDocument, BootstrapError> {
    let text = str::from_utf8(bytes).map_err(|_| {
        BootstrapError::from_diagnostic(Diagnostic {
            code: DiagnosticCode::InvalidConfiguration,
            message: "monad.toml must be valid UTF-8".to_owned(),
            location: Some("monad.toml".to_owned()),
        })
    })?;

    // Reuse the canonical bootstrap validator rather than creating a second schema or
    // precedence implementation. Invalid/unknown/unsupported input therefore cannot
    // become a semantic configuration document.
    let canonical_configuration = parse_effective_configuration(text, &CliOverrides::default())?;

    let discovered = DiscoveredSource {
        canonical_path: "monad.toml".to_owned(),
        source_kind: SourceKindCandidate::Toml,
        provenance: vec![DiscoveryProvenance {
            artifact_class: "workspace_configuration".to_owned(),
            pattern: "monad.toml".to_owned(),
        }],
    };
    let source = SourceRecord::from_discovered(&discovered, bytes, config_parser_contract());
    let identity = DocumentIdentity::new(source, CONFIG_DOCUMENT_KIND, None);

    Ok(ParsedConfigurationDocument {
        identity,
        canonical_configuration,
        effective_configuration: effective_configuration.clone(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        identity::content_sha256,
        workspace::{CliOverrides, DiagnosticCode, Provenance, bootstrap},
    };
    use std::{
        fs,
        path::{Path, PathBuf},
        time::{SystemTime, UNIX_EPOCH},
    };

    const VALID: &str = r#"schema_version = 1
[project]
id = "example"
name = "File Name"
type = "service"

[artifacts]
zeta = ["z/**/*.md"]
alpha = ["a/**/*.md"]

[exclude]
paths = ["vendor/**"]
"#;

    fn effective(text: &str, overrides: &CliOverrides) -> EffectiveConfiguration {
        parse_effective_configuration(text, overrides).expect("effective configuration")
    }

    fn temp_dir(name: &str) -> PathBuf {
        let path = std::env::temp_dir().join(format!(
            "monad-config-{name}-{}",
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("clock")
                .as_nanos()
        ));
        fs::create_dir_all(&path).expect("create temp directory");
        path
    }

    fn write_config(root: &Path, text: &str) {
        fs::write(root.join("monad.toml"), text).expect("write monad.toml");
    }

    #[test]
    fn exact_bytes_become_stable_toml_source_and_document_identity() {
        let effective = effective(VALID, &CliOverrides::default());
        let first = parse_monad_configuration(VALID.as_bytes(), &effective).expect("parse");
        let second = parse_monad_configuration(VALID.as_bytes(), &effective).expect("parse");

        assert_eq!(first, second);
        assert_eq!(first.identity.source.canonical_path, "monad.toml");
        assert_eq!(first.identity.source.source_kind, SourceKindCandidate::Toml);
        assert_eq!(
            first.identity.source.content_sha256,
            content_sha256(VALID.as_bytes())
        );
        assert_eq!(first.identity.source.byte_length, VALID.len() as u64);
        assert_eq!(
            first.identity.source.parser_contract,
            config_parser_contract()
        );
        assert_eq!(first.identity.document_kind, CONFIG_DOCUMENT_KIND);

        let changed = format!("{VALID}\n");
        let changed_doc =
            parse_monad_configuration(changed.as_bytes(), &effective).expect("changed");
        assert_eq!(
            first.identity.source.source_id,
            changed_doc.identity.source.source_id
        );
        assert_ne!(
            first.identity.source.content_sha256,
            changed_doc.identity.source.content_sha256
        );
    }

    #[test]
    fn canonical_file_values_remain_distinct_from_cli_effective_values() {
        let overrides = CliOverrides {
            project_name: Some("CLI Name".to_owned()),
            project_type: Some("cli-type".to_owned()),
            ..CliOverrides::default()
        };
        let effective = effective(VALID, &overrides);
        let document = parse_monad_configuration(VALID.as_bytes(), &effective).expect("parse");

        assert_eq!(
            document.canonical_configuration.project.name.value,
            "File Name"
        );
        assert!(matches!(
            document.canonical_configuration.project.name.source,
            Provenance::File { .. }
        ));
        assert_eq!(
            document.effective_configuration.project.name.value,
            "CLI Name"
        );
        assert_eq!(
            document.effective_configuration.project.name.source,
            Provenance::Cli
        );
        assert_eq!(
            document
                .canonical_configuration
                .project
                .project_type
                .value
                .as_deref(),
            Some("service")
        );
        assert_eq!(
            document
                .effective_configuration
                .project
                .project_type
                .value
                .as_deref(),
            Some("cli-type")
        );
        assert_eq!(
            document.effective_configuration.project.project_type.source,
            Provenance::Cli
        );
    }

    #[test]
    fn invalid_semantic_inputs_are_blocking_diagnostics_not_documents() {
        let valid_effective = effective(VALID, &CliOverrides::default());
        let cases = [
            ("schema_version =", DiagnosticCode::MalformedToml),
            (
                "schema_version = 2\n[project]\nid = \"x\"\nname = \"X\"\n",
                DiagnosticCode::UnsupportedSchemaVersion,
            ),
            (
                "schema_version = 1\nother = true\n[project]\nid = \"x\"\nname = \"X\"\n",
                DiagnosticCode::UnknownKey,
            ),
            (
                "schema_version = 1\nschema_version = 1\n[project]\nid = \"x\"\nname = \"X\"\n",
                DiagnosticCode::MalformedToml,
            ),
        ];

        for (text, expected) in cases {
            let error = parse_monad_configuration(text.as_bytes(), &valid_effective)
                .expect_err("invalid input must not produce a document");
            assert_eq!(error.diagnostics()[0].code, expected);
        }

        let error = parse_monad_configuration(&[0xff, 0xfe], &valid_effective)
            .expect_err("invalid UTF-8 must fail");
        assert_eq!(
            error.diagnostics()[0].code,
            DiagnosticCode::InvalidConfiguration
        );
        assert_eq!(
            error.diagnostics()[0].location.as_deref(),
            Some("monad.toml")
        );
    }

    #[test]
    fn interpolation_command_network_and_include_surfaces_remain_inert() {
        let text = r#"schema_version = 1
[project]
id = "inert"
name = "${HOME} $(touch should-not-run) include://example.invalid"
[artifacts]
source = ["$(touch should-not-run)/**/*.md"]
"#;
        let effective = effective(text, &CliOverrides::default());
        let document = parse_monad_configuration(text.as_bytes(), &effective).expect("parse inert");

        assert_eq!(
            document.canonical_configuration.project.name.value,
            "${HOME} $(touch should-not-run) include://example.invalid"
        );
        assert_eq!(
            document.canonical_configuration.artifacts["source"].value,
            ["$(touch should-not-run)/**/*.md"]
        );
    }

    #[test]
    fn legacy_manifest_cannot_override_or_become_a_parser_input() {
        let root = temp_dir("manifest-non-authority");
        write_config(&root, VALID);
        fs::create_dir_all(root.join(".monad")).expect(".monad");
        fs::write(
            root.join(".monad/manifest.yaml"),
            "project:\n  id: manifest-wins\n  name: Manifest Wins\n",
        )
        .expect("legacy manifest");

        let bootstrap = bootstrap(Some(&root), &CliOverrides::default()).expect("bootstrap");
        let bytes = fs::read(root.join("monad.toml")).expect("canonical bytes");
        let document =
            parse_monad_configuration(&bytes, &bootstrap.configuration).expect("semantic config");

        assert_eq!(document.canonical_configuration.project.id.value, "example");
        assert_eq!(document.effective_configuration.project.id.value, "example");
        let serialized = serde_json::to_string(&document).expect("serialize");
        assert!(!serialized.contains("manifest-wins"));
        assert!(!serialized.contains("manifest.yaml"));
    }

    #[test]
    fn normalized_serialization_is_byte_deterministic_and_key_ordered() {
        let effective = effective(VALID, &CliOverrides::default());
        let document = parse_monad_configuration(VALID.as_bytes(), &effective).expect("parse");
        let first = serde_json::to_vec(&document).expect("serialize");
        for _ in 0..4 {
            assert_eq!(serde_json::to_vec(&document).expect("serialize"), first);
        }
        let text = String::from_utf8(first).expect("utf8");
        assert!(text.find("\"alpha\"").expect("alpha") < text.find("\"zeta\"").expect("zeta"));
        assert!(text.contains("\"source_kind\":\"toml\""));
        assert!(text.contains("\"source\":\"monad.toml:project.name\""));
    }
}
