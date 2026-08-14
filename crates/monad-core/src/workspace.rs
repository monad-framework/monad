use std::{
    collections::BTreeMap,
    fmt, fs,
    path::{Component, Path, PathBuf},
};

use serde::{Serialize, Serializer};

const CONFIG_FILE: &str = "monad.toml";
const SUPPORTED_SCHEMA_VERSION: i64 = 1;

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum DiagnosticCode {
    RepositoryNotFound,
    MalformedToml,
    UnsupportedSchemaVersion,
    UnknownKey,
    InvalidConfiguration,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct Diagnostic {
    pub code: DiagnosticCode,
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub location: Option<String>,
}

impl Diagnostic {
    fn new(code: DiagnosticCode, message: impl Into<String>, location: Option<String>) -> Self {
        Self {
            code,
            message: message.into(),
            location,
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct BootstrapError {
    diagnostics: Vec<Diagnostic>,
}

impl BootstrapError {
    pub fn diagnostics(&self) -> &[Diagnostic] {
        &self.diagnostics
    }

    pub fn from_diagnostic(diagnostic: Diagnostic) -> Self {
        Self::one(diagnostic)
    }

    fn one(diagnostic: Diagnostic) -> Self {
        Self {
            diagnostics: vec![diagnostic],
        }
    }
}

impl fmt::Display for BootstrapError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(formatter, "{}", self.diagnostics[0].message)
    }
}

impl std::error::Error for BootstrapError {}

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct CliOverrides {
    pub project_id: Option<String>,
    pub project_name: Option<String>,
    pub project_type: Option<String>,
    pub artifact_roots: BTreeMap<String, Vec<String>>,
    pub exclude_paths: Option<Vec<String>>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Provenance {
    Default,
    File { location: String },
    Cli,
}

impl Serialize for Provenance {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        match self {
            Self::Default => serializer.serialize_str("default"),
            Self::File { location } => serializer.serialize_str(location),
            Self::Cli => serializer.serialize_str("cli"),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct EffectiveValue<T> {
    pub value: T,
    pub source: Provenance,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ProjectConfiguration {
    pub id: String,
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub project_type: Option<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct IngestionConfiguration {
    pub encoding: String,
    pub execute_repository_code: bool,
    pub follow_symlinks: bool,
    pub network: bool,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct EffectiveConfiguration {
    pub schema_version: EffectiveValue<i64>,
    pub project: ProjectEffectiveConfiguration,
    pub artifacts: BTreeMap<String, EffectiveValue<Vec<String>>>,
    pub exclude_paths: EffectiveValue<Vec<String>>,
    pub ingestion: IngestionEffectiveConfiguration,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ProjectEffectiveConfiguration {
    pub id: EffectiveValue<String>,
    pub name: EffectiveValue<String>,
    pub project_type: EffectiveValue<Option<String>>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct IngestionEffectiveConfiguration {
    pub encoding: EffectiveValue<String>,
    pub execute_repository_code: EffectiveValue<bool>,
    pub follow_symlinks: EffectiveValue<bool>,
    pub network: EffectiveValue<bool>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct BootstrapResult {
    pub root: String,
    pub configuration: EffectiveConfiguration,
}

pub fn bootstrap(
    start: Option<&Path>,
    overrides: &CliOverrides,
) -> Result<BootstrapResult, BootstrapError> {
    let start = absolute_lexical(start)?;
    let root = discover_root(&start)?;
    let config_path = root.join(CONFIG_FILE);
    let text = fs::read_to_string(&config_path).map_err(|error| {
        BootstrapError::one(Diagnostic::new(
            DiagnosticCode::InvalidConfiguration,
            format!("cannot read {}: {error}", config_path.display()),
            Some(CONFIG_FILE.to_owned()),
        ))
    })?;
    let configuration = parse_effective_configuration(&text, overrides)?;
    Ok(BootstrapResult {
        root: root.to_string_lossy().into_owned(),
        configuration,
    })
}

fn absolute_lexical(start: Option<&Path>) -> Result<PathBuf, BootstrapError> {
    let path = match start {
        Some(path) if path.is_absolute() => path.to_path_buf(),
        Some(path) => std::env::current_dir().map_err(io_diagnostic)?.join(path),
        None => std::env::current_dir().map_err(io_diagnostic)?,
    };
    let normalized = lexical_normalize(&path);
    if normalized.is_file() {
        Ok(normalized.parent().unwrap_or(&normalized).to_path_buf())
    } else {
        Ok(normalized)
    }
}

fn io_diagnostic(error: std::io::Error) -> BootstrapError {
    BootstrapError::one(Diagnostic::new(
        DiagnosticCode::InvalidConfiguration,
        format!("cannot determine invocation path: {error}"),
        None,
    ))
}

fn lexical_normalize(path: &Path) -> PathBuf {
    let mut normalized = PathBuf::new();
    for component in path.components() {
        match component {
            Component::CurDir => {}
            Component::ParentDir => {
                normalized.pop();
            }
            other => normalized.push(other.as_os_str()),
        }
    }
    normalized
}

fn discover_root(start: &Path) -> Result<PathBuf, BootstrapError> {
    for ancestor in start.ancestors() {
        if ancestor.join(CONFIG_FILE).is_file() {
            return Ok(ancestor.to_path_buf());
        }
    }
    Err(BootstrapError::one(Diagnostic::new(
        DiagnosticCode::RepositoryNotFound,
        format!("no Monad repository found from {}", start.display()),
        None,
    )))
}

fn parse_effective_configuration(
    text: &str,
    overrides: &CliOverrides,
) -> Result<EffectiveConfiguration, BootstrapError> {
    let value: toml::Value = toml::from_str(text).map_err(|error| {
        BootstrapError::one(Diagnostic::new(
            DiagnosticCode::MalformedToml,
            format!("malformed monad.toml: {error}"),
            Some(CONFIG_FILE.to_owned()),
        ))
    })?;
    let table = value
        .as_table()
        .ok_or_else(|| invalid("monad.toml must contain a table", CONFIG_FILE))?;
    validate_keys(
        table,
        "",
        &[
            "schema_version",
            "project",
            "artifacts",
            "ingestion",
            "exclude",
        ],
    )?;

    let schema_version = integer(table, "schema_version")?;
    if schema_version != SUPPORTED_SCHEMA_VERSION {
        return Err(BootstrapError::one(Diagnostic::new(
            DiagnosticCode::UnsupportedSchemaVersion,
            format!("unsupported schema_version {schema_version}; supported version is 1"),
            Some("schema_version".to_owned()),
        )));
    }
    let project = required_table(table, "project")?;
    validate_keys(project, "project", &["id", "name", "type"])?;
    let id = required_string(project, "id", "project")?;
    if !valid_identifier(&id) {
        return Err(invalid(
            "project.id must match ^[a-z0-9][a-z0-9._-]*$",
            "project.id",
        ));
    }
    let name = required_string(project, "name", "project")?;
    let project_type = optional_string(project, "type", "project")?;

    let artifacts = optional_table(table, "artifacts")?;
    let mut artifact_values = BTreeMap::new();
    for (name, value) in artifacts.unwrap_or(&toml::map::Map::new()) {
        let patterns = string_array(value, &format!("artifacts.{name}"))?;
        validate_paths(&patterns, &format!("artifacts.{name}"))?;
        artifact_values.insert(
            name.clone(),
            EffectiveValue {
                value: patterns,
                source: file_source(&format!("artifacts.{name}")),
            },
        );
    }

    let exclude = optional_table(table, "exclude")?;
    if let Some(exclude) = exclude {
        validate_keys(exclude, "exclude", &["paths"])?;
    }
    let exclude_paths = exclude
        .and_then(|table| table.get("paths"))
        .map(|value| string_array(value, "exclude.paths"))
        .transpose()?
        .unwrap_or_default();
    validate_paths(&exclude_paths, "exclude.paths")?;

    let ingestion = optional_table(table, "ingestion")?;
    if let Some(ingestion) = ingestion {
        validate_keys(
            ingestion,
            "ingestion",
            &[
                "encoding",
                "execute_repository_code",
                "follow_symlinks",
                "network",
            ],
        )?;
    }
    let encoding = optional_string_from(ingestion, "encoding", "ingestion")?
        .unwrap_or_else(|| "utf-8".to_owned());
    if encoding != "utf-8" {
        return Err(invalid(
            "ingestion.encoding must be utf-8",
            "ingestion.encoding",
        ));
    }
    let execute_repository_code =
        optional_bool(ingestion, "execute_repository_code", "ingestion")?.unwrap_or(false);
    let follow_symlinks =
        optional_bool(ingestion, "follow_symlinks", "ingestion")?.unwrap_or(false);
    let network = optional_bool(ingestion, "network", "ingestion")?.unwrap_or(false);
    if execute_repository_code {
        return Err(invalid(
            "ingestion.execute_repository_code must be false during MVP bootstrap",
            "ingestion.execute_repository_code",
        ));
    }
    if network {
        return Err(invalid(
            "ingestion.network must be false during MVP bootstrap",
            "ingestion.network",
        ));
    }

    let mut effective = EffectiveConfiguration {
        schema_version: EffectiveValue {
            value: schema_version,
            source: file_source("schema_version"),
        },
        project: ProjectEffectiveConfiguration {
            id: EffectiveValue {
                value: id,
                source: file_source("project.id"),
            },
            name: EffectiveValue {
                value: name,
                source: file_source("project.name"),
            },
            project_type: EffectiveValue {
                value: project_type,
                source: file_source("project.type"),
            },
        },
        artifacts: artifact_values,
        exclude_paths: EffectiveValue {
            value: exclude_paths,
            source: if table
                .get("exclude")
                .is_some_and(|v| v.get("paths").is_some())
            {
                file_source("exclude.paths")
            } else {
                Provenance::Default
            },
        },
        ingestion: IngestionEffectiveConfiguration {
            encoding: EffectiveValue {
                value: encoding,
                source: source_for(ingestion, "encoding", "ingestion.encoding"),
            },
            execute_repository_code: EffectiveValue {
                value: execute_repository_code,
                source: source_for(
                    ingestion,
                    "execute_repository_code",
                    "ingestion.execute_repository_code",
                ),
            },
            follow_symlinks: EffectiveValue {
                value: follow_symlinks,
                source: source_for(ingestion, "follow_symlinks", "ingestion.follow_symlinks"),
            },
            network: EffectiveValue {
                value: network,
                source: source_for(ingestion, "network", "ingestion.network"),
            },
        },
    };
    apply_overrides(&mut effective, overrides)?;
    Ok(effective)
}

fn apply_overrides(
    config: &mut EffectiveConfiguration,
    overrides: &CliOverrides,
) -> Result<(), BootstrapError> {
    if let Some(id) = &overrides.project_id {
        if !valid_identifier(id) {
            return Err(invalid(
                "project.id must match ^[a-z0-9][a-z0-9._-]*$",
                "cli.project_id",
            ));
        }
        config.project.id = EffectiveValue {
            value: id.clone(),
            source: Provenance::Cli,
        };
    }
    if let Some(name) = &overrides.project_name {
        if name.is_empty() {
            return Err(invalid(
                "project.name must be non-empty",
                "cli.project_name",
            ));
        }
        config.project.name = EffectiveValue {
            value: name.clone(),
            source: Provenance::Cli,
        };
    }
    if let Some(project_type) = &overrides.project_type {
        config.project.project_type = EffectiveValue {
            value: Some(project_type.clone()),
            source: Provenance::Cli,
        };
    }
    for (name, paths) in &overrides.artifact_roots {
        validate_paths(paths, &format!("cli.artifacts.{name}"))?;
        config.artifacts.insert(
            name.clone(),
            EffectiveValue {
                value: paths.clone(),
                source: Provenance::Cli,
            },
        );
    }
    if let Some(paths) = &overrides.exclude_paths {
        validate_paths(paths, "cli.exclude_paths")?;
        config.exclude_paths = EffectiveValue {
            value: paths.clone(),
            source: Provenance::Cli,
        };
    }
    Ok(())
}

fn file_source(location: &str) -> Provenance {
    Provenance::File {
        location: format!("monad.toml:{location}"),
    }
}
fn source_for(
    table: Option<&toml::map::Map<String, toml::Value>>,
    key: &str,
    location: &str,
) -> Provenance {
    if table.is_some_and(|table| table.contains_key(key)) {
        file_source(location)
    } else {
        Provenance::Default
    }
}
fn invalid(message: impl Into<String>, location: &str) -> BootstrapError {
    BootstrapError::one(Diagnostic::new(
        DiagnosticCode::InvalidConfiguration,
        message,
        Some(location.to_owned()),
    ))
}

fn validate_keys(
    table: &toml::map::Map<String, toml::Value>,
    prefix: &str,
    permitted: &[&str],
) -> Result<(), BootstrapError> {
    if let Some(key) = table.keys().find(|key| !permitted.contains(&key.as_str())) {
        let location = if prefix.is_empty() {
            key.clone()
        } else {
            format!("{prefix}.{key}")
        };
        return Err(BootstrapError::one(Diagnostic::new(
            DiagnosticCode::UnknownKey,
            format!("unknown semantic configuration key: {location}"),
            Some(location),
        )));
    }
    Ok(())
}
fn required_table<'a>(
    table: &'a toml::map::Map<String, toml::Value>,
    key: &str,
) -> Result<&'a toml::map::Map<String, toml::Value>, BootstrapError> {
    table
        .get(key)
        .and_then(toml::Value::as_table)
        .ok_or_else(|| invalid(format!("{key} must be a table"), key))
}
fn optional_table<'a>(
    table: &'a toml::map::Map<String, toml::Value>,
    key: &str,
) -> Result<Option<&'a toml::map::Map<String, toml::Value>>, BootstrapError> {
    match table.get(key) {
        None => Ok(None),
        Some(value) => value
            .as_table()
            .map(Some)
            .ok_or_else(|| invalid(format!("{key} must be a table"), key)),
    }
}
fn integer(table: &toml::map::Map<String, toml::Value>, key: &str) -> Result<i64, BootstrapError> {
    table
        .get(key)
        .and_then(toml::Value::as_integer)
        .ok_or_else(|| invalid(format!("{key} must be an integer"), key))
}
fn required_string(
    table: &toml::map::Map<String, toml::Value>,
    key: &str,
    prefix: &str,
) -> Result<String, BootstrapError> {
    optional_string(table, key, prefix)?
        .filter(|value| !value.is_empty())
        .ok_or_else(|| {
            invalid(
                format!("{prefix}.{key} must be a non-empty string"),
                &format!("{prefix}.{key}"),
            )
        })
}
fn optional_string(
    table: &toml::map::Map<String, toml::Value>,
    key: &str,
    prefix: &str,
) -> Result<Option<String>, BootstrapError> {
    optional_string_from(Some(table), key, prefix)
}
fn optional_string_from(
    table: Option<&toml::map::Map<String, toml::Value>>,
    key: &str,
    prefix: &str,
) -> Result<Option<String>, BootstrapError> {
    match table.and_then(|table| table.get(key)) {
        None => Ok(None),
        Some(value) => value
            .as_str()
            .map(|value| Some(value.to_owned()))
            .ok_or_else(|| {
                invalid(
                    format!("{prefix}.{key} must be a string"),
                    &format!("{prefix}.{key}"),
                )
            }),
    }
}
fn optional_bool(
    table: Option<&toml::map::Map<String, toml::Value>>,
    key: &str,
    prefix: &str,
) -> Result<Option<bool>, BootstrapError> {
    match table.and_then(|table| table.get(key)) {
        None => Ok(None),
        Some(value) => value.as_bool().map(Some).ok_or_else(|| {
            invalid(
                format!("{prefix}.{key} must be a boolean"),
                &format!("{prefix}.{key}"),
            )
        }),
    }
}
fn string_array(value: &toml::Value, location: &str) -> Result<Vec<String>, BootstrapError> {
    value
        .as_array()
        .ok_or_else(|| invalid(format!("{location} must be an array of strings"), location))?
        .iter()
        .map(|value| {
            value
                .as_str()
                .map(ToOwned::to_owned)
                .ok_or_else(|| invalid(format!("{location} must be an array of strings"), location))
        })
        .collect()
}
fn valid_identifier(value: &str) -> bool {
    !value.is_empty()
        && value.as_bytes()[0].is_ascii_lowercase()
        && value.bytes().all(|byte| {
            byte.is_ascii_lowercase() || byte.is_ascii_digit() || matches!(byte, b'.' | b'_' | b'-')
        })
}
fn validate_paths(values: &[String], location: &str) -> Result<(), BootstrapError> {
    for value in values {
        let path = Path::new(value);
        if value.is_empty()
            || path.is_absolute()
            || path.components().any(|component| {
                matches!(
                    component,
                    Component::ParentDir | Component::RootDir | Component::Prefix(_)
                )
            })
        {
            return Err(invalid(
                format!("{location} contains a path that escapes the repository root: {value}"),
                location,
            ));
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::{
        fs,
        time::{SystemTime, UNIX_EPOCH},
    };

    fn temp_dir(name: &str) -> PathBuf {
        let path = std::env::temp_dir().join(format!(
            "monad-core-{name}-{}",
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("clock")
                .as_nanos()
        ));
        fs::create_dir_all(&path).expect("create temp directory");
        path
    }
    fn config(id: &str) -> String {
        format!("schema_version = 1\n[project]\nid = \"{id}\"\nname = \"Example\"\n")
    }
    fn write_config(path: &Path, contents: &str) {
        fs::create_dir_all(path).expect("directories");
        fs::write(path.join(CONFIG_FILE), contents).expect("config");
    }

    #[test]
    fn finds_root_from_root_and_descendant() {
        let root = temp_dir("root");
        write_config(&root, &config("outer"));
        let descendant = root.join("a/b");
        fs::create_dir_all(&descendant).expect("descendant");
        assert_eq!(
            bootstrap(Some(&root), &CliOverrides::default())
                .expect("root")
                .root,
            root.to_string_lossy()
        );
        assert_eq!(
            bootstrap(Some(&descendant), &CliOverrides::default())
                .expect("descendant")
                .root,
            root.to_string_lossy()
        );
    }
    #[test]
    fn nearest_nested_root_wins() {
        let root = temp_dir("nested");
        write_config(&root, &config("outer"));
        let inner = root.join("subproject");
        write_config(&inner, &config("inner"));
        let result =
            bootstrap(Some(&inner.join("deep")), &CliOverrides::default()).expect("nested root");
        assert_eq!(result.root, inner.to_string_lossy());
        assert_eq!(result.configuration.project.id.value, "inner");
    }
    #[test]
    fn missing_root_is_stable() {
        let root = temp_dir("missing");
        let error = bootstrap(Some(&root), &CliOverrides::default()).expect_err("missing root");
        assert_eq!(
            error.diagnostics()[0].code,
            DiagnosticCode::RepositoryNotFound
        );
    }
    #[test]
    fn validates_malformed_unsupported_and_unknown() {
        let overrides = CliOverrides::default();
        for (text, code) in [
            ("schema_version =", DiagnosticCode::MalformedToml),
            (
                "schema_version = 2\n[project]\nid = \"x\"\nname = \"X\"",
                DiagnosticCode::UnsupportedSchemaVersion,
            ),
            (
                "schema_version = 1\nother = true\n[project]\nid = \"x\"\nname = \"X\"",
                DiagnosticCode::UnknownKey,
            ),
        ] {
            let error =
                parse_effective_configuration(text, &overrides).expect_err("invalid config");
            assert_eq!(error.diagnostics()[0].code, code);
        }
    }
    #[test]
    fn defaults_file_cli_and_provenance_are_explicit() {
        let text = "schema_version = 1\n[project]\nid = \"file\"\nname = \"File\"\n[artifacts]\nproduct = [\"product/**/*.md\"]\n";
        let mut overrides = CliOverrides {
            project_name: Some("CLI".to_owned()),
            ..CliOverrides::default()
        };
        overrides
            .artifact_roots
            .insert("product".to_owned(), vec!["override/**/*.md".to_owned()]);
        let effective = parse_effective_configuration(text, &overrides).expect("config");
        assert_eq!(effective.project.id.source, file_source("project.id"));
        assert_eq!(effective.project.name.source, Provenance::Cli);
        assert_eq!(effective.ingestion.network.source, Provenance::Default);
        assert_eq!(effective.artifacts["product"].source, Provenance::Cli);
    }
    #[test]
    fn paths_cannot_escape_and_environment_is_ignored() {
        let error = parse_effective_configuration("schema_version = 1\n[project]\nid = \"x\"\nname = \"X\"\n[exclude]\npaths = [\"../outside\"]", &CliOverrides::default()).expect_err("escape");
        assert_eq!(
            error.diagnostics()[0].code,
            DiagnosticCode::InvalidConfiguration
        );
        let text = &config("environment");
        assert_eq!(
            parse_effective_configuration(text, &CliOverrides::default()).expect("first"),
            parse_effective_configuration(text, &CliOverrides::default()).expect("second")
        );
    }
    #[test]
    fn parsing_never_executes_configuration_text() {
        let root = temp_dir("safe");
        write_config(
            &root,
            &format!(
                "{}\n[artifacts]\nsource = [\"$(touch should-not-run)\"]",
                config("safe")
            ),
        );
        let result = bootstrap(Some(&root), &CliOverrides::default()).expect("safe parsing");
        assert_eq!(
            result.configuration.artifacts["source"].value,
            ["$(touch should-not-run)"]
        );
        assert!(!root.join("should-not-run").exists());
    }
    #[test]
    fn canonical_json_output_is_byte_equivalent_with_ordered_maps_and_provenance() {
        let root = temp_dir("canonical-json");
        write_config(
            &root,
            "schema_version = 1\n[project]\nid = \"example\"\nname = \"Example\"\n[artifacts]\nzeta = [\"z/**/*.md\"]\nalpha = [\"a/**/*.md\"]\n",
        );
        let overrides = CliOverrides {
            project_name: Some("CLI Example".to_owned()),
            ..CliOverrides::default()
        };

        let first = serde_json::to_string(
            &bootstrap(Some(&root), &overrides).expect("bootstrap configuration"),
        )
        .expect("canonical JSON");
        for _ in 0..4 {
            let repeated = serde_json::to_string(
                &bootstrap(Some(&root), &overrides).expect("bootstrap configuration"),
            )
            .expect("canonical JSON");
            assert_eq!(repeated, first);
        }

        assert!(
            first.find("\"alpha\"").expect("alpha artifact")
                < first.find("\"zeta\"").expect("zeta artifact")
        );
        assert!(first.contains("\"source\":\"monad.toml:artifacts.alpha\""));
        assert!(first.contains("\"source\":\"cli\""));
        assert!(first.contains("\"source\":\"default\""));
    }
    #[test]
    fn network_enabled_configuration_is_rejected_at_network() {
        let root = temp_dir("network-enabled");
        write_config(
            &root,
            &format!(
                "{}\n[ingestion]\nnetwork = true\n",
                config("network-enabled")
            ),
        );

        let error = bootstrap(Some(&root), &CliOverrides::default()).expect_err("network rejected");
        assert_eq!(
            error.diagnostics()[0].code,
            DiagnosticCode::InvalidConfiguration
        );
        assert_eq!(
            error.diagnostics()[0].location.as_deref(),
            Some("ingestion.network")
        );
        assert_eq!(
            error.diagnostics()[0].message,
            "ingestion.network must be false during MVP bootstrap"
        );
    }
    #[test]
    fn invalid_project_id_is_rejected_at_project_id() {
        let root = temp_dir("invalid-project-id");
        write_config(&root, &config("Invalid Project"));

        let error =
            bootstrap(Some(&root), &CliOverrides::default()).expect_err("invalid project ID");
        assert_eq!(
            error.diagnostics()[0].code,
            DiagnosticCode::InvalidConfiguration
        );
        assert_eq!(
            error.diagnostics()[0].location.as_deref(),
            Some("project.id")
        );
        assert_eq!(
            error.diagnostics()[0].message,
            "project.id must match ^[a-z0-9][a-z0-9._-]*$"
        );
    }
}
