//! Stable source and document identity plus exact-byte provenance.

use std::collections::BTreeMap;

use serde::Serialize;
use sha2::{Digest, Sha256};

use crate::discovery::{DiscoveredSource, DiscoveryProvenance, SourceKindCandidate};

const SOURCE_ID_DOMAIN: &str = "monad.source-id.v1";
const PATH_DOCUMENT_ID_DOMAIN: &str = "monad.document-id.path.v1";
const EXPLICIT_DOCUMENT_ID_DOMAIN: &str = "monad.document-id.explicit.v1";

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(transparent)]
pub struct SourceId(pub String);
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(transparent)]
pub struct DocumentId(pub String);
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(transparent)]
pub struct ContentSha256(pub String);
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct ParserContract {
    pub name: String,
    pub version: String,
}
impl ParserContract {
    pub fn new(name: impl Into<String>, version: impl Into<String>) -> Self {
        Self {
            name: name.into(),
            version: version.into(),
        }
    }
}
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct GovernedIdentifier {
    pub namespace: String,
    pub value: String,
}
impl GovernedIdentifier {
    pub fn new(namespace: impl Into<String>, value: impl Into<String>) -> Self {
        Self {
            namespace: namespace.into(),
            value: value.into(),
        }
    }
}
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct SourceRecord {
    pub source_id: SourceId,
    pub canonical_path: String,
    pub source_kind: SourceKindCandidate,
    pub content_sha256: ContentSha256,
    pub byte_length: u64,
    pub parser_contract: ParserContract,
    pub discovery_provenance: Vec<DiscoveryProvenance>,
}
impl SourceRecord {
    pub fn from_discovered(
        source: &DiscoveredSource,
        bytes: &[u8],
        parser_contract: ParserContract,
    ) -> Self {
        Self {
            source_id: derive_source_id(&source.canonical_path, &source.source_kind),
            canonical_path: source.canonical_path.clone(),
            source_kind: source.source_kind.clone(),
            content_sha256: content_sha256(bytes),
            byte_length: bytes.len() as u64,
            parser_contract,
            discovery_provenance: source.provenance.clone(),
        }
    }
}
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct DocumentIdentity {
    pub document_id: DocumentId,
    pub document_kind: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub explicit_governed_identifier: Option<GovernedIdentifier>,
    pub source: SourceRecord,
}
impl DocumentIdentity {
    pub fn new(
        source: SourceRecord,
        document_kind: impl Into<String>,
        explicit_governed_identifier: Option<GovernedIdentifier>,
    ) -> Self {
        let document_kind = document_kind.into();
        let document_id = match &explicit_governed_identifier {
            Some(identifier) => derive_explicit_document_id(&document_kind, identifier),
            None => derive_path_document_id(&source.source_id, &document_kind),
        };
        Self {
            document_id,
            document_kind,
            explicit_governed_identifier,
            source,
        }
    }
}
#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum IdentityDiagnosticCode {
    DuplicateGovernedIdentifier,
}
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct IdentityDiagnostic {
    pub code: IdentityDiagnosticCode,
    pub identifier: GovernedIdentifier,
    pub source_locations: Vec<String>,
    pub message: String,
}
pub fn derive_source_id(canonical_path: &str, source_kind: &SourceKindCandidate) -> SourceId {
    SourceId(format!(
        "src-v1-{}",
        digest_framed(&[
            SOURCE_ID_DOMAIN.as_bytes(),
            canonical_path.as_bytes(),
            source_kind_name(source_kind).as_bytes()
        ])
    ))
}
pub fn derive_path_document_id(source_id: &SourceId, document_kind: &str) -> DocumentId {
    DocumentId(format!(
        "doc-v1-{}",
        digest_framed(&[
            PATH_DOCUMENT_ID_DOMAIN.as_bytes(),
            source_id.0.as_bytes(),
            document_kind.as_bytes()
        ])
    ))
}
pub fn derive_explicit_document_id(
    document_kind: &str,
    identifier: &GovernedIdentifier,
) -> DocumentId {
    DocumentId(format!(
        "doc-v1-{}",
        digest_framed(&[
            EXPLICIT_DOCUMENT_ID_DOMAIN.as_bytes(),
            document_kind.as_bytes(),
            identifier.namespace.as_bytes(),
            identifier.value.as_bytes()
        ])
    ))
}
pub fn content_sha256(bytes: &[u8]) -> ContentSha256 {
    ContentSha256(hex_digest(Sha256::digest(bytes).as_slice()))
}
pub fn detect_duplicate_governed_identifiers(
    documents: &[DocumentIdentity],
) -> Vec<IdentityDiagnostic> {
    let mut locations = BTreeMap::<GovernedIdentifier, Vec<String>>::new();
    for document in documents {
        if let Some(identifier) = &document.explicit_governed_identifier {
            locations
                .entry(identifier.clone())
                .or_default()
                .push(document.source.canonical_path.clone());
        }
    }
    locations
        .into_iter()
        .filter_map(|(identifier, mut source_locations)| {
            let duplicate_count = source_locations.len();
            source_locations.sort();
            source_locations.dedup();
            (duplicate_count > 1).then(|| IdentityDiagnostic {
                code: IdentityDiagnosticCode::DuplicateGovernedIdentifier,
                message: format!(
                    "duplicate governed identifier {}/{} in sources: {}",
                    identifier.namespace,
                    identifier.value,
                    source_locations.join(", ")
                ),
                identifier,
                source_locations,
            })
        })
        .collect()
}
fn source_kind_name(kind: &SourceKindCandidate) -> &'static str {
    match kind {
        SourceKindCandidate::Markdown => "markdown",
        SourceKindCandidate::Yaml => "yaml",
    }
}
fn digest_framed(parts: &[&[u8]]) -> String {
    let mut hasher = Sha256::new();
    for part in parts {
        hasher.update((part.len() as u64).to_be_bytes());
        hasher.update(part);
    }
    hex_digest(hasher.finalize().as_slice())
}
fn hex_digest(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut output = String::with_capacity(bytes.len() * 2);
    for byte in bytes {
        output.push(HEX[(byte >> 4) as usize] as char);
        output.push(HEX[(byte & 0x0f) as usize] as char);
    }
    output
}
#[cfg(test)]
mod tests {
    use super::*;
    use crate::discovery::{DiscoveryProvenance, discover_workspace};
    use crate::workspace::{CliOverrides, EffectiveConfiguration, bootstrap};
    use std::{
        fs,
        path::{Path, PathBuf},
        time::{SystemTime, UNIX_EPOCH},
    };
    fn source(path: &str, kind: SourceKindCandidate, bytes: &[u8]) -> SourceRecord {
        SourceRecord::from_discovered(
            &DiscoveredSource {
                canonical_path: path.to_owned(),
                source_kind: kind,
                provenance: vec![DiscoveryProvenance {
                    artifact_class: "docs".to_owned(),
                    pattern: "docs/**/*.md".to_owned(),
                }],
            },
            bytes,
            ParserContract::new("markdown", "1"),
        )
    }
    #[test]
    fn source_identity_is_clone_independent_and_content_provenance_is_exact() {
        let first = source("docs/plan.md", SourceKindCandidate::Markdown, b"first\n");
        let second = source("docs/plan.md", SourceKindCandidate::Markdown, b"second\n");
        assert_eq!(first.source_id, second.source_id);
        assert_ne!(first.content_sha256, second.content_sha256);
        assert_eq!(first.byte_length, 6);
        assert_eq!(second.byte_length, 7);
        assert_eq!(
            first.content_sha256.0,
            "b640e840b19d378660b32fb51ae18d67dccb4a8596a29e7bd72c1b2ae5928f41"
        );
        assert_eq!(
            content_sha256(b"").0,
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        );
        assert_eq!(
            content_sha256(&[0, 255, 10]).0,
            "712450d3c4a79eea9509e75dc1dacdeff58034df538536cfae2da882bd8a0c50"
        );
    }
    #[test]
    fn framing_preserves_path_case_special_characters_and_source_kind() {
        let upper = derive_source_id("docs/A.md", &SourceKindCandidate::Markdown);
        let lower = derive_source_id("docs/a.md", &SourceKindCandidate::Markdown);
        assert_eq!(
            upper.0,
            "src-v1-a0d42fb24a4ef08cdaca306bb3fbcef30e6929991ee84b48a64965f866b13d56"
        );
        assert_ne!(upper, lower);
        assert_ne!(
            upper,
            derive_source_id("docs/A.md", &SourceKindCandidate::Yaml)
        );
        assert_ne!(
            derive_source_id("døcs/a b|c.md", &SourceKindCandidate::Markdown),
            derive_source_id("døcs/a|b c.md", &SourceKindCandidate::Markdown)
        );
    }
    #[test]
    fn document_ids_follow_explicit_and_path_only_rules() {
        let old = source("docs/old.md", SourceKindCandidate::Markdown, b"one");
        let moved = source("docs/new.md", SourceKindCandidate::Markdown, b"two");
        assert_ne!(old.source_id, moved.source_id);
        assert_ne!(
            DocumentIdentity::new(old.clone(), "markdown_document", None).document_id,
            DocumentIdentity::new(moved.clone(), "markdown_document", None).document_id
        );
        let identifier = GovernedIdentifier::new("architecture-decision", "ADR-0001");
        assert_eq!(
            DocumentIdentity::new(old, "markdown_document", Some(identifier.clone())).document_id,
            DocumentIdentity::new(moved, "markdown_document", Some(identifier)).document_id
        );
    }
    #[test]
    fn duplicate_identifiers_are_sorted_fatal_diagnostics_and_namespaced() {
        let identifier = GovernedIdentifier::new("adr", "SAME");
        let first = DocumentIdentity::new(
            source("z.md", SourceKindCandidate::Markdown, b""),
            "markdown",
            Some(identifier.clone()),
        );
        let second = DocumentIdentity::new(
            source("a.md", SourceKindCandidate::Markdown, b""),
            "markdown",
            Some(identifier),
        );
        let distinct = DocumentIdentity::new(
            source("other.md", SourceKindCandidate::Markdown, b""),
            "markdown",
            Some(GovernedIdentifier::new("spec", "SAME")),
        );
        let forward = detect_duplicate_governed_identifiers(&[
            first.clone(),
            second.clone(),
            distinct.clone(),
        ]);
        let reverse = detect_duplicate_governed_identifiers(&[distinct, second, first]);
        assert_eq!(forward, reverse);
        assert_eq!(forward[0].source_locations, ["a.md", "z.md"]);
        assert_eq!(forward.len(), 1);
    }
    #[test]
    fn records_serialize_deterministically_without_host_state() {
        let first = source("docs/a.md", SourceKindCandidate::Markdown, b"x");
        let second = source("docs/a.md", SourceKindCandidate::Markdown, b"x");
        let one = serde_json::to_vec(&first).expect("serialize");
        assert_eq!(one, serde_json::to_vec(&second).expect("serialize"));
        let text = String::from_utf8(one).expect("utf8");
        for forbidden in ["/tmp", "branch", "inode", "timestamp"] {
            assert!(!text.contains(forbidden));
        }
    }
    #[cfg(unix)]
    #[test]
    fn symlink_alias_is_one_source_and_one_identity() {
        use std::os::unix::fs::symlink;
        let root = temp_dir("identity-symlink");
        fs::create_dir_all(root.join("docs")).expect("docs");
        fs::write(root.join("docs/real.md"), "content").expect("source");
        symlink("real.md", root.join("docs/alias.md")).expect("alias");
        let discovered = discover_workspace(&root, &config(&root)).expect("discovery");
        assert_eq!(discovered.sources.len(), 1);
        assert_eq!(
            SourceRecord::from_discovered(
                &discovered.sources[0],
                b"content",
                ParserContract::new("markdown", "1")
            )
            .source_id,
            derive_source_id("docs/real.md", &SourceKindCandidate::Markdown)
        );
    }
    fn temp_dir(name: &str) -> PathBuf {
        let path = std::env::temp_dir().join(format!(
            "monad-identity-{name}-{}",
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("clock")
                .as_nanos()
        ));
        fs::create_dir_all(&path).expect("create");
        path
    }
    fn config(root: &Path) -> EffectiveConfiguration {
        fs::write(root.join("monad.toml"), "schema_version = 1\n[project]\nid = \"example\"\nname = \"Example\"\n[artifacts]\ndocs = [\"docs/**\"]\n[ingestion]\nfollow_symlinks = true\n").expect("config");
        bootstrap(Some(root), &CliOverrides::default())
            .expect("bootstrap")
            .configuration
    }
}
