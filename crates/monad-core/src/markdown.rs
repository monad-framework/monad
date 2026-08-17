//! Deterministic, non-executing extraction for canonical Markdown artifacts.

use serde::Serialize;

use crate::identity::{DocumentIdentity, GovernedIdentifier, ParserContract, SourceRecord};

pub const MARKDOWN_PARSER_CONTRACT: &str = "monad.markdown-engineering-artifact";
pub const MARKDOWN_PARSER_VERSION: &str = "1";

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
pub struct SourceSpan {
    pub byte_start: u64,
    pub byte_end: u64,
    pub line_start: u64,
    pub line_end: u64,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct Heading {
    pub level: u8,
    pub text: String,
    pub source_range: SourceSpan,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct MetadataField {
    pub key: String,
    pub value: String,
    pub source_range: SourceSpan,
}

struct ParsedMetadataField<'a> {
    key_offset: usize,
    key: &'a str,
    value: &'a str,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct LinkCandidate {
    pub label: String,
    pub destination: String,
    pub source_range: SourceSpan,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct IdentifierReferenceCandidate {
    pub identifier: GovernedIdentifier,
    pub source_range: SourceSpan,
}

#[derive(Clone, Debug, Eq, Ord, PartialEq, PartialOrd, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum MarkdownDiagnosticCode {
    InvalidUtf8,
    MalformedMetadata,
    DuplicateMetadata,
    MalformedLink,
    UnclosedCodeFence,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct MarkdownDiagnostic {
    pub code: MarkdownDiagnosticCode,
    pub message: String,
    pub source_range: SourceSpan,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct ParsedMarkdownDocument {
    pub identity: DocumentIdentity,
    pub headings: Vec<Heading>,
    pub metadata: Vec<MetadataField>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub status: Option<String>,
    pub links: Vec<LinkCandidate>,
    pub identifier_references: Vec<IdentifierReferenceCandidate>,
    pub diagnostics: Vec<MarkdownDiagnostic>,
}

pub fn markdown_parser_contract() -> ParserContract {
    ParserContract::new(MARKDOWN_PARSER_CONTRACT, MARKDOWN_PARSER_VERSION)
}

pub fn parse_markdown(source: SourceRecord, bytes: &[u8]) -> ParsedMarkdownDocument {
    let document_kind = "markdown_engineering_artifact";
    let fallback_identity = DocumentIdentity::new(source, document_kind, None);
    let text = match std::str::from_utf8(bytes) {
        Ok(text) => text,
        Err(error) => return invalid_utf8(fallback_identity, bytes.len(), error.valid_up_to()),
    };

    let mut headings = Vec::new();
    let mut metadata = Vec::new();
    let mut links = Vec::new();
    let mut identifier_references = Vec::new();
    let mut diagnostics = Vec::new();
    let mut explicit_identifier = None;
    let mut in_fence: Option<(char, usize, SourceSpan)> = None;
    let mut in_html_comment = false;
    let mut in_inline_code = false;
    let mut byte_offset = 0usize;

    for (index, line_with_ending) in text
        .split_inclusive('\n')
        .chain(if text.ends_with('\n') { None } else { Some("") })
        .enumerate()
    {
        if line_with_ending.is_empty() && text.ends_with('\n') {
            continue;
        }
        let line_number = (index + 1) as u64;
        let line = line_with_ending.trim_end_matches(['\r', '\n']);
        let line_start = byte_offset;
        byte_offset += line_with_ending.len();
        let span = line_span(line_start, line.len(), line_number);

        if let Some((marker, width, _)) = &in_fence {
            if is_fence_close(line, *marker, *width) {
                in_fence = None;
            }
            continue;
        }
        if !in_html_comment && let Some((marker, width)) = fence_open(line) {
            in_fence = Some((marker, width, span));
            continue;
        }
        let visible = mask_html_comments(line, &mut in_html_comment);
        if let Some((marker, width)) = fence_open(&visible) {
            in_fence = Some((marker, width, span));
            continue;
        }
        if let Some((level, text_start, heading_text)) = heading(&visible) {
            let heading_span = line_span(line_start + text_start, heading_text.len(), line_number);
            if explicit_identifier.is_none() {
                explicit_identifier =
                    governed_identifier(heading_text).map(|(identifier, _)| identifier);
            }
            headings.push(Heading {
                level,
                text: heading_text.to_owned(),
                source_range: heading_span,
            });
        }
        if let Some(metadata_result) = metadata_field(&visible) {
            match metadata_result {
                Ok(field) => {
                    let field_span = line_span(
                        line_start + field.key_offset,
                        line.len() - field.key_offset,
                        line_number,
                    );
                    if metadata.iter().any(|metadata: &MetadataField| {
                        metadata.key.eq_ignore_ascii_case(field.key)
                    }) {
                        diagnostics.push(diagnostic(
                            MarkdownDiagnosticCode::DuplicateMetadata,
                            format!("duplicate metadata field: {}", field.key),
                            field_span,
                        ));
                    } else {
                        if explicit_identifier.is_none() && field.key.eq_ignore_ascii_case("id") {
                            explicit_identifier =
                                governed_identifier(field.value).map(|(identifier, _)| identifier);
                        }
                        metadata.push(MetadataField {
                            key: field.key.to_owned(),
                            value: field.value.to_owned(),
                            source_range: field_span,
                        });
                    }
                }
                Err(offset) => diagnostics.push(diagnostic(
                    MarkdownDiagnosticCode::MalformedMetadata,
                    "malformed bold metadata field",
                    line_span(line_start + offset, line.len() - offset, line_number),
                )),
            }
        }
        let plain = remove_inline_code(&visible, &mut in_inline_code);
        extract_links(
            &plain,
            line_start,
            line_number,
            &mut links,
            &mut diagnostics,
        );
        extract_identifiers(&plain, line_start, line_number, &mut identifier_references);
    }
    if let Some((_, _, opening_span)) = in_fence {
        diagnostics.push(diagnostic(
            MarkdownDiagnosticCode::UnclosedCodeFence,
            "unclosed code fence",
            opening_span,
        ));
    }
    let identity =
        DocumentIdentity::new(fallback_identity.source, document_kind, explicit_identifier);
    let status = metadata
        .iter()
        .find(|field| field.key.eq_ignore_ascii_case("status"))
        .map(|field| field.value.clone());
    ParsedMarkdownDocument {
        identity,
        headings,
        metadata,
        status,
        links,
        identifier_references,
        diagnostics,
    }
}

fn invalid_utf8(
    identity: DocumentIdentity,
    byte_length: usize,
    valid_up_to: usize,
) -> ParsedMarkdownDocument {
    ParsedMarkdownDocument {
        identity,
        headings: Vec::new(),
        metadata: Vec::new(),
        status: None,
        links: Vec::new(),
        identifier_references: Vec::new(),
        diagnostics: vec![diagnostic(
            MarkdownDiagnosticCode::InvalidUtf8,
            "Markdown source is not valid UTF-8",
            SourceSpan {
                byte_start: valid_up_to as u64,
                byte_end: byte_length as u64,
                line_start: 1,
                line_end: 1,
            },
        )],
    }
}

fn line_span(start: usize, length: usize, line: u64) -> SourceSpan {
    SourceSpan {
        byte_start: start as u64,
        byte_end: (start + length) as u64,
        line_start: line,
        line_end: line,
    }
}
fn diagnostic(
    code: MarkdownDiagnosticCode,
    message: impl Into<String>,
    source_range: SourceSpan,
) -> MarkdownDiagnostic {
    MarkdownDiagnostic {
        code,
        message: message.into(),
        source_range,
    }
}
fn fence_open(line: &str) -> Option<(char, usize)> {
    let trimmed = line.trim_start();
    let marker = trimmed.chars().next()?;
    if !matches!(marker, '`' | '~') {
        return None;
    }
    let width = trimmed
        .chars()
        .take_while(|character| *character == marker)
        .count();
    (width >= 3).then_some((marker, width))
}
fn is_fence_close(line: &str, marker: char, width: usize) -> bool {
    let trimmed = line.trim_start();
    trimmed
        .chars()
        .take_while(|character| *character == marker)
        .count()
        >= width
}
fn heading(line: &str) -> Option<(u8, usize, &str)> {
    let count = line
        .chars()
        .take_while(|character| *character == '#')
        .count();
    if !(1..=6).contains(&count) || line.as_bytes().get(count) != Some(&b' ') {
        return None;
    }
    let start = count + 1;
    Some((
        count as u8,
        start,
        line[start..].trim_end_matches('#').trim_end(),
    ))
}
fn metadata_field(line: &str) -> Option<Result<ParsedMetadataField<'_>, usize>> {
    let start = line.find("**")?;
    let remaining = &line[start + 2..];
    let end = remaining.find(":**");
    match end {
        Some(end) if !remaining[..end].trim().is_empty() => {
            let key = remaining[..end].trim();
            let value_start = start + 2 + end + 3;
            Some(Ok(ParsedMetadataField {
                key_offset: start + 2,
                key,
                value: line[value_start..].trim(),
            }))
        }
        _ => Some(Err(start)),
    }
}
fn mask_html_comments(line: &str, in_comment: &mut bool) -> String {
    let mut output = line.as_bytes().to_vec();
    let mut index = 0;
    while index < output.len() {
        if *in_comment {
            if output[index..].starts_with(b"-->") {
                output[index..index + 3].fill(b' ');
                index += 3;
                *in_comment = false;
            } else {
                output[index] = b' ';
                index += 1;
            }
        } else if output[index..].starts_with(b"<!--") {
            output[index..index + 4].fill(b' ');
            index += 4;
            *in_comment = true;
        } else {
            index += 1;
        }
    }
    String::from_utf8(output).expect("only valid UTF-8 bytes were replaced")
}
fn remove_inline_code(line: &str, in_code: &mut bool) -> String {
    let mut output = line.as_bytes().to_vec();
    for byte in &mut output {
        if *byte == b'`' {
            *in_code = !*in_code;
            *byte = b' ';
        } else if *in_code {
            *byte = b' ';
        }
    }
    String::from_utf8(output).expect("only valid UTF-8 bytes were replaced")
}
fn extract_links(
    line: &str,
    base: usize,
    line_number: u64,
    links: &mut Vec<LinkCandidate>,
    diagnostics: &mut Vec<MarkdownDiagnostic>,
) {
    let bytes = line.as_bytes();
    let mut index = 0;
    while index < bytes.len() {
        if bytes[index] != b'[' {
            index += 1;
            continue;
        }
        let Some(label_end_relative) = line[index + 1..].find(']') else {
            diagnostics.push(diagnostic(
                MarkdownDiagnosticCode::MalformedLink,
                "unclosed link label",
                line_span(base + index, bytes.len() - index, line_number),
            ));
            break;
        };
        let label_end = index + 1 + label_end_relative;
        if bytes.get(label_end + 1) != Some(&b'(') {
            index = label_end + 1;
            continue;
        }
        let destination_start = label_end + 2;
        let Some(destination_end_relative) = line[destination_start..].find(')') else {
            diagnostics.push(diagnostic(
                MarkdownDiagnosticCode::MalformedLink,
                "unclosed link destination",
                line_span(base + index, bytes.len() - index, line_number),
            ));
            break;
        };
        let destination_end = destination_start + destination_end_relative;
        if destination_end == destination_start {
            diagnostics.push(diagnostic(
                MarkdownDiagnosticCode::MalformedLink,
                "empty link destination",
                line_span(base + index, destination_end + 1 - index, line_number),
            ));
        } else {
            links.push(LinkCandidate {
                label: line[index + 1..label_end].to_owned(),
                destination: line[destination_start..destination_end].to_owned(),
                source_range: line_span(base + index, destination_end + 1 - index, line_number),
            });
        }
        index = destination_end + 1;
    }
}
fn governed_identifier(text: &str) -> Option<(GovernedIdentifier, usize)> {
    let bytes = text.as_bytes();
    for start in 0..bytes.len() {
        if !bytes[start].is_ascii_uppercase() || (start > 0 && is_identifier_byte(bytes[start - 1]))
        {
            continue;
        }
        let mut end = start;
        while end < bytes.len() && is_identifier_byte(bytes[end]) {
            end += 1;
        }
        let candidate = &text[start..end];
        if candidate.contains('-')
            && candidate.split('-').all(valid_identifier_part)
            && candidate.split('-').count() >= 2
            && candidate.as_bytes()[0].is_ascii_uppercase()
        {
            let namespace = candidate.split('-').next()?.to_ascii_lowercase();
            return Some((GovernedIdentifier::new(namespace, candidate), start));
        }
    }
    None
}
fn extract_identifiers(
    text: &str,
    base: usize,
    line_number: u64,
    output: &mut Vec<IdentifierReferenceCandidate>,
) {
    let mut remaining = text;
    let mut offset = 0;
    while let Some((identifier, start)) = governed_identifier(remaining) {
        let length = identifier.value.len();
        output.push(IdentifierReferenceCandidate {
            identifier,
            source_range: line_span(base + offset + start, length, line_number),
        });
        let next = start + length;
        offset += next;
        remaining = &remaining[next..];
    }
}
fn is_identifier_byte(byte: u8) -> bool {
    byte.is_ascii_uppercase() || byte.is_ascii_digit() || byte == b'-'
}
fn valid_identifier_part(part: &str) -> bool {
    !part.is_empty()
        && part
            .as_bytes()
            .iter()
            .all(|byte| byte.is_ascii_uppercase() || byte.is_ascii_digit())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::discovery::{DiscoveryProvenance, SourceKindCandidate};
    use crate::identity::SourceRecord;

    fn source() -> SourceRecord {
        SourceRecord {
            source_id: crate::identity::derive_source_id(
                "engineering/example.md",
                &SourceKindCandidate::Markdown,
            ),
            canonical_path: "engineering/example.md".to_owned(),
            source_kind: SourceKindCandidate::Markdown,
            content_sha256: crate::identity::content_sha256(b"fixture"),
            byte_length: 7,
            parser_contract: markdown_parser_contract(),
            discovery_provenance: vec![DiscoveryProvenance {
                artifact_class: "engineering".to_owned(),
                pattern: "engineering/**/*.md".to_owned(),
            }],
        }
    }
    fn parse(text: &str) -> ParsedMarkdownDocument {
        parse_markdown(source(), text.as_bytes())
    }

    #[test]
    fn extracts_structures_metadata_candidates_and_spans_in_source_order() {
        let parsed = parse(
            "# ADR-0007: Parser\n**Status:** Accepted\n## Ω section\nSee [contract](../TECH-INGEST-0001.md) and WP-MVP-0004.\n",
        );
        assert_eq!(
            parsed
                .identity
                .explicit_governed_identifier
                .as_ref()
                .unwrap()
                .value,
            "ADR-0007"
        );
        assert_eq!(parsed.status.as_deref(), Some("Accepted"));
        assert_eq!(
            parsed
                .headings
                .iter()
                .map(|heading| heading.text.as_str())
                .collect::<Vec<_>>(),
            ["ADR-0007: Parser", "Ω section"]
        );
        assert_eq!(parsed.links[0].destination, "../TECH-INGEST-0001.md");
        assert_eq!(
            parsed
                .identifier_references
                .iter()
                .map(|candidate| candidate.identifier.value.as_str())
                .collect::<Vec<_>>(),
            ["ADR-0007", "TECH-INGEST-0001", "WP-MVP-0004"]
        );
        assert_eq!(parsed.headings[1].source_range.line_start, 3);
    }
    #[test]
    fn fences_comments_and_inline_code_are_inert_for_candidates() {
        let parsed = parse(
            "<!-- [hidden](x) ADR-9999 -->\n`[inline](x) ADR-8888`\n```md\n[bad](https://example.test) WP-MVP-9999\n```\n[real](docs/a.md) WP-MVP-0004\n",
        );
        assert_eq!(parsed.links.len(), 1);
        assert_eq!(parsed.identifier_references.len(), 1);
        assert_eq!(
            parsed.identifier_references[0].identifier.value,
            "WP-MVP-0004"
        );
    }
    #[test]
    fn diagnoses_malformed_governed_constructs_and_invalid_utf8_without_promoting_them() {
        let parsed = parse("**Status Broken\n[unclosed](target\n```\n");
        assert_eq!(parsed.metadata.len(), 0);
        assert!(
            parsed
                .diagnostics
                .iter()
                .any(|diagnostic| diagnostic.code == MarkdownDiagnosticCode::MalformedMetadata)
        );
        assert!(
            parsed
                .diagnostics
                .iter()
                .any(|diagnostic| diagnostic.code == MarkdownDiagnosticCode::MalformedLink)
        );
        assert!(
            parsed
                .diagnostics
                .iter()
                .any(|diagnostic| diagnostic.code == MarkdownDiagnosticCode::UnclosedCodeFence)
        );
        let invalid = parse_markdown(source(), &[0xff]);
        assert_eq!(
            invalid.diagnostics[0].code,
            MarkdownDiagnosticCode::InvalidUtf8
        );
    }
    #[test]
    fn normalized_output_is_repeatable_and_byte_stable() {
        let input =
            "# TECH-INGEST-0001\r\n**Status:** approved\r\n[link](https://example.test)\r\n";
        let first = serde_json::to_vec(&parse(input)).unwrap();
        let second = serde_json::to_vec(&parse(input)).unwrap();
        assert_eq!(first, second);
    }

    #[test]
    fn candidate_spans_remain_exact_bytes_after_unicode_and_comments() {
        let input = "Ω <!-- ignored --> [real](docs/a.md)";
        let parsed = parse(input);
        assert_eq!(parsed.links[0].source_range.byte_start, 20);
        assert_eq!(parsed.links[0].source_range.byte_end, input.len() as u64);
    }

    #[test]
    fn empty_documents_and_duplicate_metadata_remain_explicit() {
        let empty = parse("");
        assert!(empty.headings.is_empty());
        assert!(empty.metadata.is_empty());
        assert!(empty.diagnostics.is_empty());

        let duplicate = parse("**Status:** draft\n**status:** approved\n");
        assert_eq!(duplicate.status.as_deref(), Some("draft"));
        assert_eq!(duplicate.metadata.len(), 1);
        assert!(
            duplicate
                .diagnostics
                .iter()
                .any(|diagnostic| diagnostic.code == MarkdownDiagnosticCode::DuplicateMetadata)
        );
    }

    #[test]
    fn executable_looking_text_is_only_recorded_as_data() {
        let parsed = parse(
            "<script>window.location = 'https://example.test'</script>\n\
             {{ include \"https://example.test/remote.md\" }}\n\
             [remote](https://example.test/remote.md)\n",
        );
        assert_eq!(parsed.links.len(), 1);
        assert_eq!(
            parsed.links[0].destination,
            "https://example.test/remote.md"
        );
    }

    #[test]
    fn html_comments_are_suppressed_across_lines_without_changing_visible_spans() {
        let input = "[before](before.md) WP-MVP-0001 <!-- fake [one](fake.md) WP-MVP-9999\n\
                     Ω [two](fake-two.md) WP-MVP-9998\n\
                     ```md\n\
                     [three](fake-three.md) WP-MVP-9997\n\
                     ``` --> [after](after.md) WP-MVP-0002\n\
                     <!-- [four](fake-four.md) --><!-- WP-MVP-9996 -->\n\
                     ```md\n\
                     <!-- [fenced](fake.md) WP-MVP-9995 -->\n\
                     ```\n\
                     [last](last.md) WP-MVP-0003\n";
        let parsed = parse(input);
        assert_eq!(
            parsed
                .links
                .iter()
                .map(|link| link.destination.as_str())
                .collect::<Vec<_>>(),
            ["before.md", "after.md", "last.md"]
        );
        assert_eq!(
            parsed
                .identifier_references
                .iter()
                .map(|candidate| candidate.identifier.value.as_str())
                .collect::<Vec<_>>(),
            ["WP-MVP-0001", "WP-MVP-0002", "WP-MVP-0003"]
        );
        let after_start = input.find("[after]").unwrap() as u64;
        assert_eq!(parsed.links[1].source_range.byte_start, after_start);
        assert_eq!(parsed.links[1].source_range.line_start, 5);
    }

    #[test]
    fn unterminated_html_comments_safely_suppress_remaining_input() {
        let parsed = parse("visible WP-MVP-0001\n<!--\n[hidden](fake.md) WP-MVP-9999\n");
        assert_eq!(parsed.identifier_references.len(), 1);
        assert_eq!(
            parsed.identifier_references[0].identifier.value,
            "WP-MVP-0001"
        );
        assert!(parsed.links.is_empty());
    }

    #[test]
    fn comment_masking_is_repeatable_with_crlf_and_unicode() {
        let input = "<!-- Ω [fake](fake.md) WP-MVP-9999\r\n-->[real](real.md) WP-MVP-0004\r\n";
        let first = serde_json::to_vec(&parse(input)).unwrap();
        let second = serde_json::to_vec(&parse(input)).unwrap();
        assert_eq!(first, second);
        let parsed = parse(input);
        assert_eq!(
            parsed.links[0].source_range.byte_start,
            input.find("[real]").unwrap() as u64
        );
    }

    #[test]
    fn inline_code_suppression_persists_across_lines() {
        let parsed =
            parse("before WP-MVP-0001\n`[hidden](fake.md) WP-MVP-9999\n` after WP-MVP-0002\n");
        assert!(parsed.links.is_empty());
        assert_eq!(
            parsed
                .identifier_references
                .iter()
                .map(|candidate| candidate.identifier.value.as_str())
                .collect::<Vec<_>>(),
            ["WP-MVP-0001", "WP-MVP-0002"]
        );
    }
}
