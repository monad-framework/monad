use std::{
    collections::{BTreeMap, BTreeSet, HashMap},
    ffi::OsString,
    fmt, fs, io,
    path::{Path, PathBuf},
};

use serde::Serialize;

use crate::workspace::EffectiveConfiguration;

const DEFAULT_EXCLUDES: [&str; 4] = [".git/**", ".eos/**", "machine/**", "target/**"];

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SourceKindCandidate {
    Markdown,
    Yaml,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct DiscoveryProvenance {
    pub artifact_class: String,
    pub pattern: String,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct DiscoveredSource {
    pub canonical_path: String,
    pub source_kind: SourceKindCandidate,
    pub provenance: Vec<DiscoveryProvenance>,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum DiscoveryDiagnosticCode {
    RootUnavailable,
    InvalidUtf8Path,
    UnreadableSource,
    InvalidSymlink,
    RootEscape,
    UnsupportedSourceKind,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct DiscoveryDiagnostic {
    pub code: DiscoveryDiagnosticCode,
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub location: Option<String>,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct DiscoveryResult {
    pub sources: Vec<DiscoveredSource>,
    pub diagnostics: Vec<DiscoveryDiagnostic>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct DiscoveryError {
    diagnostic: DiscoveryDiagnostic,
}

impl DiscoveryError {
    pub fn diagnostic(&self) -> &DiscoveryDiagnostic {
        &self.diagnostic
    }
}

impl fmt::Display for DiscoveryError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.diagnostic.message)
    }
}

impl std::error::Error for DiscoveryError {}

pub fn discover_workspace(
    root: &Path,
    configuration: &EffectiveConfiguration,
) -> Result<DiscoveryResult, DiscoveryError> {
    let canonical_root = fs::canonicalize(root).map_err(|error| DiscoveryError {
        diagnostic: DiscoveryDiagnostic {
            code: DiscoveryDiagnosticCode::RootUnavailable,
            message: format!("cannot access repository root: {error}"),
            location: None,
        },
    })?;
    if !canonical_root.is_dir() {
        return Err(DiscoveryError {
            diagnostic: DiscoveryDiagnostic {
                code: DiscoveryDiagnosticCode::RootUnavailable,
                message: "repository root is not a directory".to_owned(),
                location: None,
            },
        });
    }

    let mut includes = Vec::new();
    for (artifact_class, patterns) in &configuration.artifacts {
        for pattern in &patterns.value {
            includes.push((artifact_class.clone(), pattern.clone()));
        }
    }
    includes.sort();

    let mut excludes = DEFAULT_EXCLUDES
        .into_iter()
        .map(str::to_owned)
        .chain(configuration.exclude_paths.value.iter().cloned())
        .collect::<Vec<_>>();
    excludes.sort();
    excludes.dedup();

    let mut walker = Walker {
        root,
        canonical_root: &canonical_root,
        includes: &includes,
        excludes: &excludes,
        follow_symlinks: configuration.ingestion.follow_symlinks.value,
        candidates: BTreeMap::new(),
        diagnostics: Vec::new(),
    };
    let mut ancestors = BTreeSet::new();
    ancestors.insert(canonical_root.clone());
    walker.walk_directory(root, &mut ancestors);

    walker.diagnostics.sort();
    walker.diagnostics.dedup();
    let sources = walker
        .candidates
        .into_iter()
        .map(
            |((canonical_path, source_kind), provenance)| DiscoveredSource {
                canonical_path,
                source_kind,
                provenance: provenance.into_iter().collect(),
            },
        )
        .collect();
    Ok(DiscoveryResult {
        sources,
        diagnostics: walker.diagnostics,
    })
}

fn collect_directory_entries<I>(entries: I) -> (Vec<(OsString, PathBuf)>, Vec<io::Error>)
where
    I: IntoIterator<Item = io::Result<(OsString, PathBuf)>>,
{
    let mut valid = Vec::new();
    let mut errors = Vec::new();
    for entry in entries {
        match entry {
            Ok(entry) => valid.push(entry),
            Err(error) => errors.push(error),
        }
    }
    valid.sort_by(|left, right| left.0.cmp(&right.0));
    (valid, errors)
}

struct Walker<'a> {
    root: &'a Path,
    canonical_root: &'a Path,
    includes: &'a [(String, String)],
    excludes: &'a [String],
    follow_symlinks: bool,
    candidates: BTreeMap<(String, SourceKindCandidate), BTreeSet<DiscoveryProvenance>>,
    diagnostics: Vec<DiscoveryDiagnostic>,
}

impl Walker<'_> {
    fn walk_directory(&mut self, directory: &Path, ancestors: &mut BTreeSet<PathBuf>) {
        let entries = match fs::read_dir(directory) {
            Ok(entries) => entries,
            Err(error) => {
                let location = relative_utf8(self.root, directory);
                self.diagnostic(
                    DiscoveryDiagnosticCode::UnreadableSource,
                    format!("cannot read directory: {error}"),
                    location,
                );
                return;
            }
        };
        let (entries, errors) = collect_directory_entries(
            entries.map(|entry| entry.map(|entry| (entry.file_name(), entry.path()))),
        );
        let location = relative_utf8(self.root, directory);
        for error in errors {
            self.diagnostic(
                DiscoveryDiagnosticCode::UnreadableSource,
                format!("cannot enumerate directory entry: {error}"),
                location.clone(),
            );
        }
        for (_, path) in entries {
            self.walk_entry(&path, ancestors);
        }
    }

    fn walk_entry(&mut self, path: &Path, ancestors: &mut BTreeSet<PathBuf>) {
        let Some(lexical_path) = relative_utf8(self.root, path) else {
            self.diagnostic(
                DiscoveryDiagnosticCode::InvalidUtf8Path,
                "encountered a non-UTF-8 repository path",
                None,
            );
            return;
        };
        if excluded(&lexical_path, self.excludes) {
            return;
        }

        let metadata = match fs::symlink_metadata(path) {
            Ok(metadata) => metadata,
            Err(error) => {
                self.diagnostic(
                    DiscoveryDiagnosticCode::UnreadableSource,
                    format!("cannot inspect source: {error}"),
                    Some(lexical_path),
                );
                return;
            }
        };

        if metadata.file_type().is_symlink() {
            self.walk_symlink(path, &lexical_path, ancestors);
        } else if metadata.is_dir() {
            self.walk_regular_directory(path, &lexical_path, ancestors);
        } else if metadata.is_file() {
            self.process_file(path, &lexical_path, false);
        }
    }

    fn walk_regular_directory(
        &mut self,
        path: &Path,
        lexical_path: &str,
        ancestors: &mut BTreeSet<PathBuf>,
    ) {
        let Some(canonical) = self.resolve(path, lexical_path, false) else {
            return;
        };
        if !ancestors.insert(canonical.clone()) {
            self.diagnostic(
                DiscoveryDiagnosticCode::InvalidSymlink,
                "directory traversal cycle detected",
                Some(lexical_path.to_owned()),
            );
            return;
        }
        self.walk_directory(path, ancestors);
        ancestors.remove(&canonical);
    }

    fn walk_symlink(&mut self, path: &Path, lexical_path: &str, ancestors: &mut BTreeSet<PathBuf>) {
        let Some(canonical) = self.resolve(path, lexical_path, true) else {
            return;
        };
        let metadata = match fs::metadata(&canonical) {
            Ok(metadata) => metadata,
            Err(error) => {
                self.diagnostic(
                    DiscoveryDiagnosticCode::InvalidSymlink,
                    format!("cannot inspect symlink target: {error}"),
                    Some(lexical_path.to_owned()),
                );
                return;
            }
        };
        if metadata.is_dir() {
            if !self.follow_symlinks {
                return;
            }
            if !ancestors.insert(canonical.clone()) {
                self.diagnostic(
                    DiscoveryDiagnosticCode::InvalidSymlink,
                    "symlink cycle detected",
                    Some(lexical_path.to_owned()),
                );
                return;
            }
            self.walk_directory(path, ancestors);
            ancestors.remove(&canonical);
        } else if metadata.is_file() && self.follow_symlinks {
            self.process_file(path, lexical_path, true);
        }
    }

    fn process_file(&mut self, path: &Path, lexical_path: &str, symlink: bool) {
        let provenance = self
            .includes
            .iter()
            .filter(|(_, pattern)| glob_matches(pattern, lexical_path))
            .map(|(artifact_class, pattern)| DiscoveryProvenance {
                artifact_class: artifact_class.clone(),
                pattern: pattern.clone(),
            })
            .collect::<BTreeSet<_>>();
        if provenance.is_empty() {
            return;
        }

        let Some(canonical) = self.resolve(path, lexical_path, symlink) else {
            return;
        };
        let Some(canonical_path) = relative_utf8(self.canonical_root, &canonical) else {
            self.diagnostic(
                DiscoveryDiagnosticCode::InvalidUtf8Path,
                "resolved source path is not valid UTF-8",
                Some(lexical_path.to_owned()),
            );
            return;
        };
        if excluded(&canonical_path, self.excludes) {
            return;
        }

        let Some(source_kind) = source_kind(&canonical_path) else {
            self.diagnostic(
                DiscoveryDiagnosticCode::UnsupportedSourceKind,
                format!("unsupported source kind: {canonical_path}"),
                Some(canonical_path),
            );
            return;
        };
        if let Err(error) = fs::File::open(path) {
            self.diagnostic(
                DiscoveryDiagnosticCode::UnreadableSource,
                format!("cannot read source: {error}"),
                Some(canonical_path),
            );
            return;
        }

        self.candidates
            .entry((canonical_path, source_kind))
            .or_default()
            .extend(provenance);
    }

    fn resolve(&mut self, path: &Path, lexical_path: &str, symlink: bool) -> Option<PathBuf> {
        let canonical = match fs::canonicalize(path) {
            Ok(canonical) => canonical,
            Err(error) => {
                self.diagnostic(
                    if symlink {
                        DiscoveryDiagnosticCode::InvalidSymlink
                    } else {
                        DiscoveryDiagnosticCode::UnreadableSource
                    },
                    if symlink {
                        format!("cannot resolve symlink: {error}")
                    } else {
                        format!("cannot resolve source path: {error}")
                    },
                    Some(lexical_path.to_owned()),
                );
                return None;
            }
        };
        if !canonical.starts_with(self.canonical_root) {
            self.diagnostic(
                DiscoveryDiagnosticCode::RootEscape,
                "resolved source escapes the repository root",
                Some(lexical_path.to_owned()),
            );
            return None;
        }
        Some(canonical)
    }

    fn diagnostic(
        &mut self,
        code: DiscoveryDiagnosticCode,
        message: impl Into<String>,
        location: Option<String>,
    ) {
        self.diagnostics.push(DiscoveryDiagnostic {
            code,
            message: message.into(),
            location,
        });
    }
}

fn relative_utf8(base: &Path, path: &Path) -> Option<String> {
    let relative = path.strip_prefix(base).ok()?;
    relative
        .to_str()
        .map(|value| value.replace('\\', "/").trim_start_matches("./").to_owned())
}

fn source_kind(path: &str) -> Option<SourceKindCandidate> {
    match Path::new(path)
        .extension()
        .and_then(|extension| extension.to_str())
        .map(str::to_ascii_lowercase)
        .as_deref()
    {
        Some("md") => Some(SourceKindCandidate::Markdown),
        Some("yaml" | "yml") => Some(SourceKindCandidate::Yaml),
        _ => None,
    }
}

fn excluded(path: &str, patterns: &[String]) -> bool {
    patterns.iter().any(|pattern| glob_matches(pattern, path))
}

fn glob_matches(pattern: &str, path: &str) -> bool {
    let pattern = pattern.trim_start_matches("./");
    let path = path.trim_start_matches("./");
    let pattern_segments = pattern.split('/').collect::<Vec<_>>();
    let path_segments = path.split('/').collect::<Vec<_>>();
    let mut memo = HashMap::new();
    glob_segments(&pattern_segments, &path_segments, 0, 0, &mut memo)
}

fn glob_segments(
    pattern: &[&str],
    path: &[&str],
    pattern_index: usize,
    path_index: usize,
    memo: &mut HashMap<(usize, usize), bool>,
) -> bool {
    if let Some(result) = memo.get(&(pattern_index, path_index)) {
        return *result;
    }
    let result = if pattern_index == pattern.len() {
        path_index == path.len()
    } else if pattern[pattern_index] == "**" {
        glob_segments(pattern, path, pattern_index + 1, path_index, memo)
            || (path_index < path.len()
                && glob_segments(pattern, path, pattern_index, path_index + 1, memo))
    } else {
        path_index < path.len()
            && segment_matches(pattern[pattern_index], path[path_index])
            && glob_segments(pattern, path, pattern_index + 1, path_index + 1, memo)
    };
    memo.insert((pattern_index, path_index), result);
    result
}

fn segment_matches(pattern: &str, text: &str) -> bool {
    let pattern = pattern.chars().collect::<Vec<_>>();
    let text = text.chars().collect::<Vec<_>>();
    let mut states = vec![vec![false; text.len() + 1]; pattern.len() + 1];
    states[0][0] = true;
    for pattern_index in 0..pattern.len() {
        for text_index in 0..=text.len() {
            if !states[pattern_index][text_index] {
                continue;
            }
            match pattern[pattern_index] {
                '*' => {
                    states[pattern_index + 1][text_index] = true;
                    if text_index < text.len() {
                        states[pattern_index][text_index + 1] = true;
                    }
                }
                '?' if text_index < text.len() => {
                    states[pattern_index + 1][text_index + 1] = true;
                }
                literal if text_index < text.len() && literal == text[text_index] => {
                    states[pattern_index + 1][text_index + 1] = true;
                }
                _ => {}
            }
        }
    }
    states[pattern.len()][text.len()]
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::workspace::{CliOverrides, bootstrap};
    use std::time::{SystemTime, UNIX_EPOCH};

    fn temp_dir(name: &str) -> PathBuf {
        let path = std::env::temp_dir().join(format!(
            "monad-discovery-{name}-{}",
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("clock")
                .as_nanos()
        ));
        fs::create_dir_all(&path).expect("create temp directory");
        path
    }

    fn write_config(root: &Path, artifacts: &str, extra: &str) -> EffectiveConfiguration {
        let text = format!(
            "schema_version = 1\n[project]\nid = \"example\"\nname = \"Example\"\n[artifacts]\n{artifacts}\n{extra}\n"
        );
        fs::write(root.join("monad.toml"), text).expect("write config");
        bootstrap(Some(root), &CliOverrides::default())
            .expect("bootstrap")
            .configuration
    }

    fn write(root: &Path, relative: &str) {
        let path = root.join(relative);
        fs::create_dir_all(path.parent().expect("parent")).expect("create parents");
        fs::write(path, "content\n").expect("write source");
    }

    #[test]
    fn directory_entry_errors_are_preserved_while_valid_entries_sort() {
        let input = vec![
            Ok((OsString::from("z.md"), PathBuf::from("z.md"))),
            Err(io::Error::new(
                io::ErrorKind::PermissionDenied,
                "simulated directory entry failure",
            )),
            Ok((OsString::from("a.md"), PathBuf::from("a.md"))),
        ];
        let (entries, errors) = collect_directory_entries(input);
        let names = entries
            .iter()
            .map(|(name, _)| name.to_string_lossy().into_owned())
            .collect::<Vec<_>>();
        assert_eq!(names, ["a.md", "z.md"]);
        assert_eq!(errors.len(), 1);
        assert_eq!(errors[0].kind(), io::ErrorKind::PermissionDenied);
        assert_eq!(errors[0].to_string(), "simulated directory entry failure");
    }

    #[test]
    fn discovery_is_sorted_and_merges_overlapping_pattern_provenance() {
        let root = temp_dir("ordering");
        write(&root, "docs/z.md");
        write(&root, "docs/a.md");
        write(&root, "root.md");
        let configuration =
            write_config(&root, "docs = [\"docs/**/*.md\"]\nall = [\"**/*.md\"]", "");
        let result = discover_workspace(&root, &configuration).expect("discovery");
        let paths = result
            .sources
            .iter()
            .map(|source| source.canonical_path.as_str())
            .collect::<Vec<_>>();
        assert_eq!(paths, ["docs/a.md", "docs/z.md", "root.md"]);
        assert_eq!(result.sources[0].provenance.len(), 2);
        assert_eq!(result.sources[0].provenance[0].artifact_class, "all");
        assert_eq!(result.sources[0].provenance[1].artifact_class, "docs");
    }

    #[test]
    fn default_and_configured_exclusions_are_pruned() {
        let root = temp_dir("exclusions");
        for path in [
            ".git/hidden.md",
            ".eos/hidden.md",
            "machine/hidden.md",
            "target/hidden.md",
            "generated/hidden.md",
            "docs/visible.md",
        ] {
            write(&root, path);
        }
        let configuration = write_config(
            &root,
            "all = [\"**/*.md\"]",
            "[exclude]\npaths = [\"generated/**\"]",
        );
        let result = discover_workspace(&root, &configuration).expect("discovery");
        assert_eq!(result.sources.len(), 1);
        assert_eq!(result.sources[0].canonical_path, "docs/visible.md");
    }

    #[test]
    fn broad_patterns_report_unsupported_sources_but_keep_supported_yaml() {
        let root = temp_dir("kinds");
        write(&root, "docs/model.yaml");
        write(&root, "docs/notes.txt");
        let configuration = write_config(&root, "all = [\"docs/**\"]", "");
        let result = discover_workspace(&root, &configuration).expect("discovery");
        assert_eq!(result.sources.len(), 1);
        assert_eq!(result.sources[0].canonical_path, "docs/model.yaml");
        assert_eq!(result.sources[0].source_kind, SourceKindCandidate::Yaml);
        assert_eq!(result.diagnostics.len(), 1);
        assert_eq!(
            result.diagnostics[0].code,
            DiscoveryDiagnosticCode::UnsupportedSourceKind
        );
        assert_eq!(
            result.diagnostics[0].location.as_deref(),
            Some("docs/notes.txt")
        );
    }

    #[test]
    fn equivalent_clones_are_byte_equivalent_despite_creation_order() {
        let first = temp_dir("clone-a");
        let second = temp_dir("clone-b");
        for path in ["docs/b.md", "docs/a.md", "config/settings.yml"] {
            write(&first, path);
        }
        for path in ["config/settings.yml", "docs/a.md", "docs/b.md"] {
            write(&second, path);
        }
        let first_config = write_config(&first, "all = [\"**/*\"]", "");
        let second_config = write_config(&second, "all = [\"**/*\"]", "");
        let first_result = discover_workspace(&first, &first_config).expect("first");
        let second_result = discover_workspace(&second, &second_config).expect("second");
        assert_eq!(first_result, second_result);
        assert_eq!(
            serde_json::to_vec(&first_result).expect("serialize first"),
            serde_json::to_vec(&second_result).expect("serialize second")
        );
    }

    #[test]
    fn discovery_never_executes_repository_content() {
        let root = temp_dir("no-execution");
        write(&root, "docs/source.md");
        fs::write(root.join("docs/source.md"), "$(touch should-not-exist)\n")
            .expect("write payload");
        let configuration = write_config(&root, "docs = [\"docs/**/*.md\"]", "");
        let result = discover_workspace(&root, &configuration).expect("discovery");
        assert_eq!(result.sources.len(), 1);
        assert!(!root.join("should-not-exist").exists());
    }

    #[test]
    fn globstar_matches_zero_or_more_segments() {
        assert!(glob_matches("**/*.md", "root.md"));
        assert!(glob_matches("docs/**/*.md", "docs/a.md"));
        assert!(glob_matches("docs/**/*.md", "docs/nested/a.md"));
        assert!(!glob_matches("docs/*.md", "docs/nested/a.md"));
    }

    #[cfg(unix)]
    #[test]
    fn symlink_aliases_deduplicate_and_unsafe_links_are_diagnostic() {
        use std::os::unix::fs::symlink;

        let root = temp_dir("symlinks");
        let outside = temp_dir("outside");
        write(&root, "docs/real.md");
        write(&outside, "outside.md");
        symlink("real.md", root.join("docs/alias.md")).expect("internal link");
        symlink(outside.join("outside.md"), root.join("docs/external.md")).expect("external link");
        symlink(".", root.join("docs/cycle")).expect("cycle link");
        let configuration = write_config(
            &root,
            "docs = [\"docs/**\"]",
            "[ingestion]\nfollow_symlinks = true",
        );
        let result = discover_workspace(&root, &configuration).expect("discovery");
        assert_eq!(result.sources.len(), 1);
        assert_eq!(result.sources[0].canonical_path, "docs/real.md");
        assert!(result.diagnostics.iter().any(|diagnostic| {
            diagnostic.code == DiscoveryDiagnosticCode::RootEscape
                && diagnostic.location.as_deref() == Some("docs/external.md")
        }));
        assert!(result.diagnostics.iter().any(|diagnostic| {
            diagnostic.code == DiscoveryDiagnosticCode::InvalidSymlink
                && diagnostic.location.as_deref() == Some("docs/cycle")
        }));
    }

    #[cfg(unix)]
    #[test]
    fn non_utf8_paths_produce_deterministic_diagnostics() {
        use std::{ffi::OsString, os::unix::ffi::OsStringExt};

        let root = temp_dir("non-utf8");
        let invalid = OsString::from_vec(vec![b'd', b'o', b'c', b's', b'/', 0xff]);
        fs::create_dir_all(root.join("docs")).expect("docs");
        fs::write(root.join(invalid), "content").expect("invalid path source");
        let configuration = write_config(&root, "all = [\"**/*\"]", "");
        let result = discover_workspace(&root, &configuration).expect("discovery");
        assert!(
            result
                .diagnostics
                .iter()
                .any(|diagnostic| { diagnostic.code == DiscoveryDiagnosticCode::InvalidUtf8Path })
        );
    }
}
