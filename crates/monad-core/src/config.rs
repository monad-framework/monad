//! Semantic adaptation of canonical `monad.toml` after bootstrap validation.
//!
//! This module deliberately reuses the workspace bootstrap validator. It does not
//! implement configuration precedence, consult legacy manifests, interpolate the
//! environment, execute repository code, perform network access, or process includes.

use std::{collections::BTreeMap, str};

use serde::{Deserialize, Serialize};

use crate::{
    discovery::{DiscoveredSource, DiscoveryProvenance, SourceKindCandidate},
    identity::{DocumentIdentity, ParserContract, SourceRecord},
    workspace::{
        BootstrapError, CliOverrides, Diagnostic, DiagnosticCode, EffectiveConfiguration,
        Provenance, parse_effective_configuration,
    },
};

pub const CONFIG_PARSER_CONTRACT: &str = "monad.structured-configuration";
pub const CONFIG_PARSER_VERSION: &str = "1";
pub const CONFIG_DOCUMENT_KIND: &str = "monad_configuration";

/// A byte range into the exact canonical `monad.toml` input. `end_byte` is exclusive.
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct SourceRange {
    pub start_byte: usize,
    pub end_byte: usize,
}

/// A semantic configuration document keeps canonical source/default values separate
/// from run-effective values. This is required because CLI overrides affect the run
/// without editing or replacing canonical `monad.toml` facts.
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ParsedConfigurationDocument {
    pub identity: DocumentIdentity,
    pub canonical_configuration: EffectiveConfiguration,
    pub effective_configuration: EffectiveConfiguration,
    pub source_ranges: BTreeMap<String, SourceRange>,
}

#[derive(Debug, Deserialize)]
struct SpannedConfiguration {
    schema_version: toml::Spanned<i64>,
    project: SpannedProject,
    #[serde(default)]
    artifacts: BTreeMap<String, toml::Spanned<Vec<toml::Spanned<String>>>>,
    #[serde(default)]
    exclude: Option<SpannedExclude>,
    #[serde(default)]
    ingestion: Option<SpannedIngestion>,
}

#[derive(Debug, Deserialize)]
struct SpannedProject {
    id: toml::Spanned<String>,
    name: toml::Spanned<String>,
    #[serde(rename = "type")]
    project_type: Option<toml::Spanned<String>>,
}

#[derive(Debug, Deserialize)]
struct SpannedExclude {
    paths: Option<toml::Spanned<Vec<toml::Spanned<String>>>>,
}

#[derive(Debug, Deserialize)]
struct SpannedIngestion {
    encoding: Option<toml::Spanned<String>>,
    execute_repository_code: Option<toml::Spanned<bool>>,
    follow_symlinks: Option<toml::Spanned<bool>>,
    network: Option<toml::Spanned<bool>>,
}

pub fn config_parser_contract() -> ParserContract {
    ParserContract::new(CONFIG_PARSER_CONTRACT, CONFIG_PARSER_VERSION)
}

/// Adapt exact canonical `monad.toml` bytes into semantic state after bootstrap has
/// produced the supplied effective configuration.
///
/// The exact bytes are parsed again with no CLI overrides through the same bootstrap
/// validator to recover canonical file/default values. CLI-provenance values are then
/// reconstructed from the supplied effective configuration and reapplied to these exact
/// bytes. The rebound result must equal the supplied effective configuration, preventing
/// stale or unrelated bootstrap state from being attributed to the identified bytes.
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
    let effective_configuration = rebound_effective_configuration(text, effective_configuration)?;
    let source_ranges = source_ranges(text)?;

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
        effective_configuration,
        source_ranges,
    })
}

fn rebound_effective_configuration(
    text: &str,
    supplied: &EffectiveConfiguration,
) -> Result<EffectiveConfiguration, BootstrapError> {
    let overrides = cli_overrides_from_effective(supplied);
    let rebound = parse_effective_configuration(text, &overrides)?;
    if &rebound != supplied {
        return Err(BootstrapError::from_diagnostic(Diagnostic {
            code: DiagnosticCode::InvalidConfiguration,
            message: "effective configuration does not correspond to the supplied monad.toml bytes and CLI provenance"
                .to_owned(),
            location: Some("monad.toml".to_owned()),
        }));
    }
    Ok(rebound)
}

fn cli_overrides_from_effective(configuration: &EffectiveConfiguration) -> CliOverrides {
    let mut overrides = CliOverrides::default();

    if matches!(&configuration.project.id.source, Provenance::Cli) {
        overrides.project_id = Some(configuration.project.id.value.clone());
    }
    if matches!(&configuration.project.name.source, Provenance::Cli) {
        overrides.project_name = Some(configuration.project.name.value.clone());
    }
    if matches!(&configuration.project.project_type.source, Provenance::Cli) {
        overrides.project_type = configuration.project.project_type.value.clone();
    }
    for (name, value) in &configuration.artifacts {
        if matches!(&value.source, Provenance::Cli) {
            overrides
                .artifact_roots
                .insert(name.clone(), value.value.clone());
        }
    }
    if matches!(&configuration.exclude_paths.source, Provenance::Cli) {
        overrides.exclude_paths = Some(configuration.exclude_paths.value.clone());
    }

    overrides
}

fn source_ranges(text: &str) -> Result<BTreeMap<String, SourceRange>, BootstrapError> {
    let spanned: SpannedConfiguration = toml::from_str(text).map_err(|error| {
        BootstrapError::from_diagnostic(Diagnostic {
            code: DiagnosticCode::MalformedToml,
            message: format!("malformed monad.toml while retaining source ranges: {error}"),
            location: Some("monad.toml".to_owned()),
        })
    })?;

    let mut ranges = BTreeMap::new();
    insert_range(&mut ranges, "schema_version", &spanned.schema_version);
    insert_range(&mut ranges, "project.id", &spanned.project.id);
    insert_range(&mut ranges, "project.name", &spanned.project.name);
    if let Some(project_type) = &spanned.project.project_type {
        insert_range(&mut ranges, "project.type", project_type);
    }

    for (name, values) in &spanned.artifacts {
        let path = format!("artifacts.{name}");
        insert_range(&mut ranges, &path, values);
        for (index, value) in values.get_ref().iter().enumerate() {
            insert_range(&mut ranges, &format!("{path}[{index}]"), value);
        }
    }

    if let Some(paths) = spanned
        .exclude
        .as_ref()
        .and_then(|exclude| exclude.paths.as_ref())
    {
        insert_range(&mut ranges, "exclude.paths", paths);
        for (index, value) in paths.get_ref().iter().enumerate() {
            insert_range(&mut ranges, &format!("exclude.paths[{index}]"), value);
        }
    }

    if let Some(ingestion) = &spanned.ingestion {
        if let Some(value) = &ingestion.encoding {
            insert_range(&mut ranges, "ingestion.encoding", value);
        }
        if let Some(value) = &ingestion.execute_repository_code {
            insert_range(&mut ranges, "ingestion.execute_repository_code", value);
        }
        if let Some(value) = &ingestion.follow_symlinks {
            insert_range(&mut ranges, "ingestion.follow_symlinks", value);
        }
        if let Some(value) = &ingestion.network {
            insert_range(&mut ranges, "ingestion.network", value);
        }
    }

    Ok(ranges)
}

fn insert_range<T>(
    ranges: &mut BTreeMap<String, SourceRange>,
    path: &str,
    value: &toml::Spanned<T>,
) {
    let span = value.span();
    ranges.insert(
        path.to_owned(),
        SourceRange {
            start_byte: span.start,
            end_byte: span.end,
        },
    );
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
        assert_eq!(first.identity.source.parser_contract, config_parser_contract());
        assert_eq!(first.identity.document_kind, CONFIG_DOCUMENT_KIND);

        let changed = format!("{VALID}\n");
        let changed_effective = effective(&changed, &CliOverrides::default());
        let changed_doc = parse_monad_configuration(changed.as_bytes(), &changed_effective)
            .expect("changed");
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
    fn effective_configuration_is_bound_to_the_identified_bytes() {
        let supplied = effective(VALID, &CliOverrides::default());
        let different = VALID.replace("id = \"example\"", "id = \"different\"");
        let error = parse_monad_configuration(different.as_bytes(), &supplied)
            .expect_err("stale effective configuration must fail");
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
    fn reliable_toml_value_ranges_are_retained() {
        let effective = effective(VALID, &CliOverrides::default());
        let document = parse_monad_configuration(VALID.as_bytes(), &effective).expect("parse");

        let name = &document.source_ranges["project.name"];
        assert_eq!(&VALID[name.start_byte..name.end_byte], "\"File Name\"");
        let artifact = &document.source_ranges["artifacts.alpha[0]"];
        assert_eq!(
            &VALID[artifact.start_byte..artifact.end_byte],
            "\"a/**/*.md\""
        );
        let schema = &document.source_ranges["schema_version"];
        assert_eq!(&VALID[schema.start_byte..schema.end_byte], "1");
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
        assert!(
            text.find("\"alpha\"").expect("alpha") < text.find("\"zeta\"").expect("zeta")
        );
        assert!(text.contains("\"source_kind\":\"toml\""));
        assert!(text.contains("\"source\":\"monad.toml:project.name\""));
        assert!(text.contains("\"source_ranges\""));
    }
}
