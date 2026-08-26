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
    '''                Ok(field) => record_metadata_field(
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
''',
    '''                Ok(field) => {
                    let field_span = line_span(
                        line_start + field.key_offset,
                        line.len().saturating_sub(field.key_offset),
                        line_number,
                    );
                    record_metadata_field(
                        field,
                        field_span,
                        &mut metadata,
                        &mut explicit_identifier,
                        &mut explicit_identifier_conflicted,
                        &mut explicit_identifier_declared,
                        &mut diagnostics,
                    );
                }
''',
    "body metadata call",
)

replace_once(
    '''            Some(Ok(field)) => record_metadata_field(
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
''',
    '''            Some(Ok(field)) => {
                let field_span = line_span(
                    line_start + field.key_offset,
                    line.len().saturating_sub(field.key_offset),
                    line_number,
                );
                record_metadata_field(
                    field,
                    field_span,
                    &mut local_metadata,
                    &mut local_identifier,
                    &mut local_identifier_conflicted,
                    &mut local_identifier_declared,
                    &mut local_diagnostics,
                );
            }
''',
    "front matter metadata call",
)

replace_once(
    '''fn record_metadata_field(
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
''',
    '''fn record_metadata_field(
    field: ParsedMetadataField<'_>,
    field_span: SourceSpan,
    metadata: &mut Vec<MetadataField>,
    explicit_identifier: &mut Option<GovernedIdentifier>,
    explicit_identifier_conflicted: &mut bool,
    explicit_identifier_declared: &mut bool,
    diagnostics: &mut Vec<MarkdownDiagnostic>,
) {
''',
    "metadata helper signature",
)

path.write_text(text, encoding="utf-8")
