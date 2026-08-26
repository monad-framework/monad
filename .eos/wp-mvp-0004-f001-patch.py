from pathlib import Path

path = Path("crates/monad-core/src/markdown.rs")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    'pub const MARKDOWN_PARSER_VERSION: &str = "1";',
    'pub const MARKDOWN_PARSER_VERSION: &str = "2";',
    "parser contract version",
)

replace_once(
    '''    let mut explicit_identifier = None;
    let mut explicit_identifier_conflicted = false;
    let mut in_fence: Option<(char, usize, SourceSpan)> = None;
    let mut in_html_comment = false;
    let mut in_inline_code = None;
    let mut byte_offset = 0usize;
''',
    '''    let mut explicit_identifier = None;
    let mut explicit_identifier_conflicted = false;
    let mut explicit_identifier_declared = false;
    let mut heading_identifier = None;
    let mut heading_identifier_conflicted = false;
    let mut in_fence: Option<(char, usize, SourceSpan)> = None;
    let mut in_html_comment = false;
    let mut in_inline_code = None;
    let front_matter_end = parse_front_matter(
        text,
        &mut metadata,
        &mut explicit_identifier,
        &mut explicit_identifier_conflicted,
        &mut explicit_identifier_declared,
        &mut diagnostics,
    );
    let mut byte_offset = 0usize;
''',
    "parser state",
)

replace_once(
    '''        let span = line_span(line_start, line.len(), line_number);

        if let Some((marker, width, _)) = &in_fence {
''',
    '''        let span = line_span(line_start, line.len(), line_number);

        if line_start < front_matter_end {
            continue;
        }

        if let Some((marker, width, _)) = &in_fence {
''',
    "front matter skip",
)

replace_once(
    '''                record_explicit_identifier(
                    &mut explicit_identifier,
                    &mut explicit_identifier_conflicted,
                    governed_identifier(heading_text).map(|(identifier, _)| identifier),
                    heading_span.clone(),
                    &mut diagnostics,
                );
''',
    '''                record_explicit_identifier(
                    &mut heading_identifier,
                    &mut heading_identifier_conflicted,
                    governed_identifier(heading_text).map(|(identifier, _)| identifier),
                    heading_span.clone(),
                    &mut diagnostics,
                );
''',
    "H1 fallback identity",
)

old_metadata = '''        if let Some(metadata_result) = metadata_field(&plain) {
            match metadata_result {
                Ok(field) => {
                    let field_span = line_span(
                        line_start + field.key_offset,
                        line.len() - field.key_offset,
                        line_number,
                    );
                    let mut accept_field = true;
                    if field.key.eq_ignore_ascii_case("id") {
                        match exact_governed_identifier(field.value) {
                            Some(identifier) => record_explicit_identifier(
                                &mut explicit_identifier,
                                &mut explicit_identifier_conflicted,
                                Some(identifier),
                                field_span.clone(),
                                &mut diagnostics,
                            ),
                            None => {
                                diagnostics.push(diagnostic(
                                    MarkdownDiagnosticCode::MalformedMetadata,
                                    "invalid explicit document identifier",
                                    field_span.clone(),
                                ));
                                accept_field = false;
                            }
                        }
                    }
                    if accept_field {
                        if metadata.iter().any(|metadata: &MetadataField| {
                            metadata.key.eq_ignore_ascii_case(field.key)
                        }) {
                            diagnostics.push(diagnostic(
                                MarkdownDiagnosticCode::DuplicateMetadata,
                                format!("duplicate metadata field: {}", field.key),
                                field_span,
                            ));
                        } else {
                            metadata.push(MetadataField {
                                key: field.key.to_owned(),
                                value: field.value.to_owned(),
                                source_range: field_span,
                            });
                        }
                    }
                }
                Err(offset) => diagnostics.push(diagnostic(
                    MarkdownDiagnosticCode::MalformedMetadata,
                    "malformed bold metadata field",
                    line_span(line_start + offset, line.len() - offset, line_number),
                )),
            }
        }
'''
new_metadata = '''        if let Some(metadata_result) = metadata_field(&plain) {
            match metadata_result {
                Ok(field) => record_metadata_field(
                    field,
                    line_start,
                    line.len(),
                    line_number,
                    &mut metadata,
                    &mut explicit_identifier,
                    &mut explicit_identifier_conflicted,
                    &mut explicit_identifier_declared,
                    &mut diagnostics,
                ),
                Err(offset) => diagnostics.push(diagnostic(
                    MarkdownDiagnosticCode::MalformedMetadata,
                    "malformed bold metadata field",
                    line_span(line_start + offset, line.len() - offset, line_number),
                )),
            }
        }
'''
replace_once(old_metadata, new_metadata, "metadata handling")

replace_once(
    '''    let identity =
        DocumentIdentity::new(fallback_identity.source, document_kind, explicit_identifier);
''',
    '''    let resolved_identifier = if explicit_identifier_declared {
        explicit_identifier
    } else {
        heading_identifier
    };
    let identity = DocumentIdentity::new(
        fallback_identity.source,
        document_kind,
        resolved_identifier,
    );
''',
    "identity resolution",
)

helper_marker = '''fn diagnostic(
    code: MarkdownDiagnosticCode,
'''
helpers = r'''fn parse_front_matter(
    text: &str,
    metadata: &mut Vec<MetadataField>,
    explicit_identifier: &mut Option<GovernedIdentifier>,
    explicit_identifier_conflicted: &mut bool,
    explicit_identifier_declared: &mut bool,
    diagnostics: &mut Vec<MarkdownDiagnostic>,
) -> usize {
    let mut lines = text.split_inclusive('\n').enumerate();
    let Some((_, first_with_ending)) = lines.next() else {
        return 0;
    };
    let first = first_with_ending.trim_end_matches(['\r', '\n']);
    if first != "---" {
        return 0;
    }

    let mut local_metadata = Vec::new();
    let mut local_identifier = None;
    let mut local_identifier_conflicted = false;
    let mut local_identifier_declared = false;
    let mut local_diagnostics = Vec::new();
    let mut saw_governed_front_matter = false;
    let mut saw_identity_syntax = false;
    let mut byte_offset = first_with_ending.len();

    for (index, line_with_ending) in lines {
        let line_number = (index + 1) as u64;
        let line = line_with_ending.trim_end_matches(['\r', '\n']);
        let line_start = byte_offset;
        byte_offset += line_with_ending.len();

        if line == "---" {
            metadata.extend(local_metadata);
            *explicit_identifier = local_identifier;
            *explicit_identifier_conflicted = local_identifier_conflicted;
            *explicit_identifier_declared = local_identifier_declared;
            diagnostics.extend(local_diagnostics);
            return byte_offset;
        }
        if line.trim().is_empty() {
            continue;
        }

        let governed_key = front_matter_governed_key(line);
        if let Some(key) = governed_key {
            saw_governed_front_matter = true;
            if key == "artifact_id" {
                saw_identity_syntax = true;
            }
        }

        match front_matter_field(line) {
            Some(Ok(field)) => record_metadata_field(
                field,
                line_start,
                line.len(),
                line_number,
                &mut local_metadata,
                &mut local_identifier,
                &mut local_identifier_conflicted,
                &mut local_identifier_declared,
                &mut local_diagnostics,
            ),
            Some(Err(offset)) => {
                if governed_key == Some("artifact_id") {
                    local_identifier_declared = true;
                    local_identifier = None;
                    local_identifier_conflicted = true;
                }
                local_diagnostics.push(diagnostic(
                    MarkdownDiagnosticCode::MalformedMetadata,
                    "malformed YAML front-matter scalar",
                    line_span(line_start + offset, line.len() - offset, line_number),
                ));
            }
            None if governed_key.is_some() => {
                if governed_key == Some("artifact_id") {
                    local_identifier_declared = true;
                    local_identifier = None;
                    local_identifier_conflicted = true;
                }
                local_diagnostics.push(diagnostic(
                    MarkdownDiagnosticCode::MalformedMetadata,
                    "malformed governed YAML front-matter field",
                    line_span(line_start, line.len(), line_number),
                ));
            }
            None => {}
        }
    }

    if saw_governed_front_matter {
        diagnostics.extend(local_diagnostics);
        if saw_identity_syntax || local_identifier_declared {
            *explicit_identifier = None;
            *explicit_identifier_conflicted = true;
            *explicit_identifier_declared = true;
        }
        diagnostics.push(diagnostic(
            MarkdownDiagnosticCode::MalformedMetadata,
            "unclosed YAML front matter",
            line_span(0, first.len(), 1),
        ));
        return text.len();
    }

    0
}

fn front_matter_field(line: &str) -> Option<Result<ParsedMetadataField<'_>, usize>> {
    if line.starts_with(' ') || line.starts_with('\t') {
        return None;
    }
    let colon = line.find(':')?;
    let key_segment = &line[..colon];
    let key = key_segment.trim();
    if key.is_empty()
        || !key
            .chars()
            .all(|character| character.is_ascii_alphanumeric() || matches!(character, '_' | '-'))
    {
        return None;
    }
    let key_offset = key_segment.find(key).unwrap_or(0);
    let raw_value = line[colon + 1..].trim();
    match front_matter_scalar(raw_value) {
        Some(value) => Some(Ok(ParsedMetadataField {
            key_offset,
            key,
            value,
        })),
        None => Some(Err(key_offset)),
    }
}

fn front_matter_scalar(raw: &str) -> Option<&str> {
    let value = raw.trim();
    let Some(first) = value.chars().next() else {
        return Some(value);
    };
    if !matches!(first, '"' | '\'') {
        return Some(value);
    }
    let last = value.chars().next_back()?;
    if value.len() < 2 || last != first {
        return None;
    }
    Some(&value[first.len_utf8()..value.len() - last.len_utf8()])
}

fn front_matter_governed_key(line: &str) -> Option<&'static str> {
    let trimmed = line.trim_start();
    for key in ["artifact_id", "status"] {
        let Some(prefix) = trimmed.get(..key.len()) else {
            continue;
        };
        if !prefix.eq_ignore_ascii_case(key) {
            continue;
        }
        let suffix = &trimmed[key.len()..];
        if suffix.chars().next().is_none_or(|character| {
            !character.is_alphanumeric() && !matches!(character, '_' | '-')
        }) {
            return Some(key);
        }
    }
    None
}

fn record_metadata_field(
    field: ParsedMetadataField<'_>,
    line_start: usize,
    line_length: usize,
    line_number: u64,
    metadata: &mut Vec<MetadataField>,
    explicit_identifier: &mut Option<GovernedIdentifier>,
    explicit_identifier_conflicted: &mut bool,
    explicit_identifier_declared: &mut bool,
    diagnostics: &mut Vec<MarkdownDiagnostic>,
) {
    let field_span = line_span(
        line_start + field.key_offset,
        line_length.saturating_sub(field.key_offset),
        line_number,
    );
    let existing = metadata
        .iter()
        .find(|existing| existing.key.eq_ignore_ascii_case(field.key));
    let duplicate = existing.is_some();
    let equivalent_duplicate = existing.is_some_and(|existing| existing.value == field.value);
    let identity_field = field.key.eq_ignore_ascii_case("id")
        || field.key.eq_ignore_ascii_case("artifact_id");
    let mut accept_field = true;

    if identity_field {
        *explicit_identifier_declared = true;
        if duplicate {
            if existing.is_some_and(|existing| existing.value != field.value) {
                diagnostics.push(diagnostic(
                    MarkdownDiagnosticCode::MalformedMetadata,
                    "conflicting explicit document identifier",
                    field_span.clone(),
                ));
            }
            *explicit_identifier = None;
            *explicit_identifier_conflicted = true;
        } else {
            match exact_governed_identifier(field.value) {
                Some(identifier) => record_explicit_identifier(
                    explicit_identifier,
                    explicit_identifier_conflicted,
                    Some(identifier),
                    field_span.clone(),
                    diagnostics,
                ),
                None => {
                    diagnostics.push(diagnostic(
                        MarkdownDiagnosticCode::MalformedMetadata,
                        "invalid explicit document identifier",
                        field_span.clone(),
                    ));
                    *explicit_identifier = None;
                    *explicit_identifier_conflicted = true;
                    accept_field = false;
                }
            }
        }
    } else if field.key.eq_ignore_ascii_case("status") && field.value.is_empty() {
        diagnostics.push(diagnostic(
            MarkdownDiagnosticCode::MalformedMetadata,
            "invalid empty status metadata",
            field_span.clone(),
        ));
        accept_field = false;
    }

    if !accept_field {
        return;
    }
    if duplicate {
        if identity_field || !equivalent_duplicate {
            diagnostics.push(diagnostic(
                MarkdownDiagnosticCode::DuplicateMetadata,
                format!("duplicate metadata field: {}", field.key),
                field_span,
            ));
        }
        return;
    }
    metadata.push(MetadataField {
        key: field.key.to_owned(),
        value: field.value.to_owned(),
        source_range: field_span,
    });
}

'''
replace_once(helper_marker, helpers + helper_marker, "front matter helpers")

replace_once(
    '    use crate::identity::SourceRecord;',
    '    use crate::identity::{SourceRecord, detect_duplicate_governed_identifiers};',
    "test imports",
)

old_conflict = '''        let conflicting = parse("# ADR-0001\\n**ID:** ADR-0002\\n");
        assert!(conflicting.identity.explicit_governed_identifier.is_none());
        assert!(conflicting.diagnostics.iter().any(|diagnostic| {
            diagnostic.code == MarkdownDiagnosticCode::MalformedMetadata
                && diagnostic.message == "conflicting explicit document identifier"
                && diagnostic.source_range.line_start == 2
        }));
'''
new_conflict = '''        let explicit_overrides_heading = parse("# ADR-0001\\n**ID:** ADR-0002\\n");
        assert_eq!(
            explicit_overrides_heading
                .identity
                .explicit_governed_identifier
                .as_ref()
                .map(|identifier| identifier.value.as_str()),
            Some("ADR-0002")
        );
        assert!(explicit_overrides_heading.diagnostics.is_empty());
'''
replace_once(old_conflict, new_conflict, "H1 fallback test")

insert_at = text.rfind("\n}")
if insert_at < 0:
    raise SystemExit("test module close not found")
new_tests = r'''

    #[test]
    fn canonical_front_matter_controls_identity_status_and_h1_fallback() {
        let parsed = parse(
            "---\nartifact_id: \"REV-WP-MVP-0003\"\nstatus: \"In Review\"\n---\n# WP-MVP-0003 — Engineering Review\n",
        );
        assert_eq!(
            parsed
                .identity
                .explicit_governed_identifier
                .as_ref()
                .map(|identifier| identifier.value.as_str()),
            Some("REV-WP-MVP-0003")
        );
        assert_eq!(parsed.status.as_deref(), Some("In Review"));
        assert!(parsed.metadata.iter().any(|field| {
            field.key == "artifact_id"
                && field.value == "REV-WP-MVP-0003"
                && field.source_range.line_start == 2
        }));
        assert!(parsed.metadata.iter().any(|field| {
            field.key == "status"
                && field.value == "In Review"
                && field.source_range.line_start == 3
        }));
        assert_eq!(
            parsed
                .identifier_references
                .iter()
                .map(|candidate| candidate.identifier.value.as_str())
                .collect::<Vec<_>>(),
            ["WP-MVP-0003"]
        );
        assert!(parsed.diagnostics.is_empty());

        let fallback = parse("# WP-MVP-0003 — Stable source and document identity\n");
        assert_eq!(
            fallback
                .identity
                .explicit_governed_identifier
                .as_ref()
                .map(|identifier| identifier.value.as_str()),
            Some("WP-MVP-0003")
        );
    }

    #[test]
    fn review_front_matter_prevents_false_duplicate_governed_identifier() {
        let review = parse(
            "---\nartifact_id: \"REV-WP-MVP-0003\"\nstatus: \"In Review\"\n---\n# WP-MVP-0003 — Engineering Review\n",
        );
        let work_packet = parse("# WP-MVP-0003 — Stable source and document identity\n");
        assert!(
            detect_duplicate_governed_identifiers(&[review.identity, work_packet.identity]).is_empty()
        );
    }

    #[test]
    fn malformed_duplicate_or_conflicting_explicit_identity_suppresses_h1_fallback() {
        let malformed = parse(
            "---\nartifact_id: \"not-a-governed-id\"\n---\n# WP-MVP-0003 — Engineering Review\n",
        );
        assert!(malformed.identity.explicit_governed_identifier.is_none());
        assert!(malformed.diagnostics.iter().any(|diagnostic| {
            diagnostic.code == MarkdownDiagnosticCode::MalformedMetadata
                && diagnostic.message == "invalid explicit document identifier"
                && diagnostic.source_range.line_start == 2
        }));

        let duplicate = parse(
            "---\nartifact_id: \"REV-WP-MVP-0003\"\nartifact_id: \"REV-WP-MVP-0003\"\n---\n# WP-MVP-0003 — Engineering Review\n",
        );
        assert!(duplicate.identity.explicit_governed_identifier.is_none());
        assert!(duplicate.diagnostics.iter().any(|diagnostic| {
            diagnostic.code == MarkdownDiagnosticCode::DuplicateMetadata
                && diagnostic.source_range.line_start == 3
        }));

        let conflicting = parse(
            "---\nartifact_id: \"REV-WP-MVP-0003\"\n---\n# WP-MVP-0003 — Engineering Review\n**ID:** WP-MVP-0003\n",
        );
        assert!(conflicting.identity.explicit_governed_identifier.is_none());
        assert!(conflicting.diagnostics.iter().any(|diagnostic| {
            diagnostic.code == MarkdownDiagnosticCode::MalformedMetadata
                && diagnostic.message == "conflicting explicit document identifier"
                && diagnostic.source_range.line_start == 5
        }));
    }

    #[test]
    fn equivalent_projected_status_does_not_create_a_false_duplicate() {
        let parsed = parse(
            "---\nstatus: \"APPROVED\"\n---\n# CR-0002 — Change\n**Status:** APPROVED\n",
        );
        assert_eq!(parsed.status.as_deref(), Some("APPROVED"));
        assert!(parsed.diagnostics.iter().all(|diagnostic| {
            diagnostic.code != MarkdownDiagnosticCode::DuplicateMetadata
        }));
    }

    #[test]
    fn governed_unclosed_front_matter_is_diagnostic_and_does_not_fall_back_to_h1() {
        let parsed = parse(
            "---\nartifact_id: \"REV-WP-MVP-0003\"\n# WP-MVP-0003 — Engineering Review\n",
        );
        assert!(parsed.identity.explicit_governed_identifier.is_none());
        assert!(parsed.headings.is_empty());
        assert!(parsed.diagnostics.iter().any(|diagnostic| {
            diagnostic.code == MarkdownDiagnosticCode::MalformedMetadata
                && diagnostic.message == "unclosed YAML front matter"
                && diagnostic.source_range.line_start == 1
        }));
    }
'''
text = text[:insert_at] + new_tests + text[insert_at:]

path.write_text(text, encoding="utf-8")
