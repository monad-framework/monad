#!/usr/bin/env python3
"""Generate and verify deterministic machine-readable document companions.

Human-readable UTF-8 files outside machine/ are canonical. This tool projects
them into structured JSON, a manifest, a knowledge graph, and a JSONL section
corpus using only the Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import posixpath
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import quote, unquote, urlsplit


SCHEMA_VERSION = "1.0.0"
TOOL_NAME = "sync-machine-docs"
TOOL_VERSION = "1.0.0"

EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".cache",
    ".gradle",
    ".mypy_cache",
    ".next",
    ".nox",
    ".npm",
    ".pnpm-store",
    ".pytest_cache",
    ".ruff_cache",
    ".terraform",
    ".tox",
    ".turbo",
    ".venv",
    ".yarn",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "htmlcov",
    "node_modules",
    "out",
    "target",
    "tmp",
    "venv",
    "vendor",
}

SENSITIVE_FILE_NAMES = {
    ".netrc",
    ".npmrc",
    ".pypirc",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
}

SENSITIVE_SUFFIXES = {
    ".der",
    ".jks",
    ".key",
    ".p12",
    ".pem",
    ".pfx",
}

NORMATIVE_ROOTS = {
    "architecture",
    "engineering",
    "governance",
    "operations",
    "product",
    "security",
    "specifications",
    "testing",
    "vision",
}

NORMATIVE_ROOT_FILES = {
    ".editorconfig",
    ".gitattributes",
    ".githubignore",
    ".gitignore",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "SECURITY.md",
}

DOCUMENT_TYPE_BY_ROOT = {
    "architecture": "architecture",
    "docs": "published-documentation",
    "engineering": "engineering-control",
    "governance": "governance",
    "journal": "journal",
    "operations": "operations",
    "product": "product",
    "research": "research",
    "scripts": "automation",
    "security": "security",
    "specifications": "specification",
    "testing": "quality-assurance",
    "tools": "tooling",
    "vision": "vision",
}

LANGUAGE_BY_NAME = {
    ".editorconfig": "editorconfig",
    ".gitattributes": "gitattributes",
    ".githubignore": "gitignore-patterns",
    ".gitignore": "gitignore",
    "CODEOWNERS": "codeowners",
    "LICENSE": "plain-text",
    "Makefile": "make",
}

LANGUAGE_BY_SUFFIX = {
    ".adoc": "asciidoc",
    ".bash": "bash",
    ".cfg": "ini",
    ".conf": "configuration",
    ".css": "css",
    ".go": "go",
    ".graphql": "graphql",
    ".html": "html",
    ".ini": "ini",
    ".java": "java",
    ".js": "javascript",
    ".json": "json",
    ".jsonl": "json-lines",
    ".jsx": "javascript-jsx",
    ".md": "markdown",
    ".py": "python",
    ".rs": "rust",
    ".rst": "restructuredtext",
    ".sh": "bash",
    ".sql": "sql",
    ".toml": "toml",
    ".ts": "typescript",
    ".tsx": "typescript-jsx",
    ".txt": "plain-text",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".zsh": "zsh",
}

MEDIA_TYPE_BY_SUFFIX = {
    ".md": "text/markdown",
    ".rst": "text/x-rst",
    ".adoc": "text/asciidoc",
    ".jsonl": "application/x-ndjson",
    ".toml": "application/toml",
    ".yaml": "application/yaml",
    ".yml": "application/yaml",
}

HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
IDENTIFIER_RE = re.compile(
    r"\b(?:ADR|EXP|FND|FUN|TEC|INT|DATA|SEC|OPS|FR|QR|UC|AC|WP|INC|MS|WC|"
    r"RQ|NG|AP|QA|C|G|P|A|R|T)-[0-9]{2,5}\b"
)


@dataclass(frozen=True)
class SourceFile:
    path: Path
    relative_path: str
    data: bytes
    text: str


@dataclass(frozen=True)
class GeneratedOutput:
    relative_path: str
    data: bytes


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: Any) -> bytes:
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        separators=(",", ": "),
    )
    return (rendered + "\n").encode("utf-8")


def compact_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def is_sensitive(relative: PurePosixPath) -> bool:
    name = relative.name
    lowered = name.lower()
    if name in SENSITIVE_FILE_NAMES:
        return True
    if lowered == ".env" or (lowered.startswith(".env.") and lowered != ".env.example"):
        return True
    return relative.suffix.lower() in SENSITIVE_SUFFIXES


def is_excluded(relative: PurePosixPath) -> bool:
    if not relative.parts:
        return True
    if relative.parts[0] == "machine":
        return True
    if any(part in EXCLUDED_DIRECTORY_NAMES for part in relative.parts[:-1]):
        return True
    return is_sensitive(relative)


def discover_sources(root: Path) -> list[SourceFile]:
    sources: list[SourceFile] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink() or not path.is_file():
            continue
        relative = PurePosixPath(path.relative_to(root).as_posix())
        if is_excluded(relative):
            continue
        data = path.read_bytes()
        if b"\x00" in data:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        sources.append(
            SourceFile(
                path=path,
                relative_path=relative.as_posix(),
                data=data,
                text=text,
            )
        )
    return sources


def document_id(source_path: str) -> str:
    return "doc:" + quote(source_path, safe="-._~")


def identifier_node_id(identifier: str) -> str:
    return "identifier:" + quote(identifier, safe="-._~")


def language_for(source_path: str) -> str:
    pure_path = PurePosixPath(source_path)
    if pure_path.name in LANGUAGE_BY_NAME:
        return LANGUAGE_BY_NAME[pure_path.name]
    return LANGUAGE_BY_SUFFIX.get(pure_path.suffix.lower(), "plain-text")


def media_type_for(source_path: str) -> str:
    pure_path = PurePosixPath(source_path)
    if pure_path.name == "LICENSE":
        return "text/plain"
    if pure_path.name.startswith(".") and not pure_path.suffix:
        return "text/plain"
    if pure_path.suffix.lower() in MEDIA_TYPE_BY_SUFFIX:
        return MEDIA_TYPE_BY_SUFFIX[pure_path.suffix.lower()]
    guessed, _ = mimetypes.guess_type(pure_path.name)
    if guessed and (guessed.startswith("text/") or guessed in {"application/json", "application/xml"}):
        return guessed
    return "text/plain"


def document_type_for(source_path: str) -> str:
    pure_path = PurePosixPath(source_path)
    if pure_path.parts[0] == ".github":
        if len(pure_path.parts) > 1 and pure_path.parts[1] == "workflows":
            return "continuous-integration"
        return "repository-governance"
    if len(pure_path.parts) > 1:
        return DOCUMENT_TYPE_BY_ROOT.get(pure_path.parts[0], "project-source")
    if pure_path.name == "LICENSE":
        return "license"
    if pure_path.name == "CHANGELOG.md":
        return "changelog"
    if pure_path.name == "README.md":
        return "repository-index"
    if pure_path.name.startswith("."):
        return "repository-configuration"
    return "project-record"


def is_normative(source_path: str) -> bool:
    pure_path = PurePosixPath(source_path)
    return pure_path.parts[0] in NORMATIVE_ROOTS or pure_path.name in NORMATIVE_ROOT_FILES


def clean_heading(value: str) -> str:
    value = re.sub(r"[ \t]+#+[ \t]*$", "", value).strip()
    return re.sub(r"\s+", " ", value)


def title_for(source_path: str, text: str) -> str:
    if language_for(source_path) == "markdown":
        in_fence = False
        fence_character = ""
        for line in text.splitlines():
            fence_match = FENCE_RE.match(line)
            if fence_match:
                character = fence_match.group(1)[0]
                if not in_fence:
                    in_fence = True
                    fence_character = character
                elif character == fence_character:
                    in_fence = False
                    fence_character = ""
                continue
            if not in_fence:
                heading = HEADING_RE.match(line)
                if heading and len(heading.group(1)) == 1:
                    return clean_heading(heading.group(2))
    pure_path = PurePosixPath(source_path)
    if pure_path.name == "LICENSE":
        return "License"
    display = pure_path.name.lstrip(".") or pure_path.name
    stem = display.rsplit(".", 1)[0] if "." in display else display
    return re.sub(r"[-_]+", " ", stem).strip().title() or source_path


def strip_markdown(value: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[`*_~]", "", value)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def summary_for(source_path: str, text: str, title: str) -> str:
    if language_for(source_path) != "markdown":
        return f"Canonical {language_for(source_path)} source for {source_path}."

    paragraphs: list[list[str]] = []
    current: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            if current:
                paragraphs.append(current)
                current = []
            continue
        stripped = line.strip()
        if in_fence or not stripped:
            if current:
                paragraphs.append(current)
                current = []
            continue
        if HEADING_RE.match(line) or stripped.startswith(("|", "- ", "* ", ">", "```")):
            if current:
                paragraphs.append(current)
                current = []
            continue
        current.append(stripped)
    if current:
        paragraphs.append(current)

    for paragraph in paragraphs:
        candidate = strip_markdown(" ".join(paragraph))
        if candidate and candidate != title:
            return candidate[:600]
    return f"Canonical project document: {title}."


def unique_identifiers(text: str) -> list[str]:
    return sorted(set(IDENTIFIER_RE.findall(text)))


def section_slug(title: str) -> str:
    slug = title.casefold()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug or "section"


def markdown_sections(text: str, fallback_title: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    headings: list[tuple[int, int, str]] = []
    in_fence = False
    fence_character = ""

    for index, line in enumerate(lines):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            character = fence_match.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_character = character
            elif character == fence_character:
                in_fence = False
                fence_character = ""
            continue
        if in_fence:
            continue
        heading = HEADING_RE.match(line)
        if heading:
            headings.append((index, len(heading.group(1)), clean_heading(heading.group(2))))

    raw_sections: list[tuple[str, int, int, int, str]] = []
    if not headings:
        full_text = text.rstrip("\n")
        return [
            {
                "section_id": "content",
                "title": fallback_title,
                "level": 1,
                "line_start": 1,
                "line_end": max(1, len(lines)),
                "text": full_text,
                "identifiers": unique_identifiers(full_text),
            }
        ]

    first_heading_index = headings[0][0]
    if first_heading_index > 0:
        preamble = "\n".join(lines[:first_heading_index]).strip("\n")
        if preamble.strip():
            raw_sections.append(("Preamble", 0, 1, first_heading_index, preamble))

    for position, (line_index, level, heading_title) in enumerate(headings):
        end_index = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
        section_text = "\n".join(lines[line_index:end_index]).rstrip("\n")
        raw_sections.append(
            (heading_title, level, line_index + 1, max(line_index + 1, end_index), section_text)
        )

    seen_slugs: dict[str, int] = {}
    sections: list[dict[str, Any]] = []
    for heading_title, level, line_start, line_end, section_text in raw_sections:
        base_slug = "preamble" if level == 0 else section_slug(heading_title)
        seen_slugs[base_slug] = seen_slugs.get(base_slug, 0) + 1
        section_id = base_slug
        if seen_slugs[base_slug] > 1:
            section_id = f"{base_slug}-{seen_slugs[base_slug]}"
        sections.append(
            {
                "section_id": section_id,
                "title": heading_title,
                "level": level,
                "line_start": line_start,
                "line_end": line_end,
                "text": section_text,
                "identifiers": unique_identifiers(section_text),
            }
        )
    return sections


def sections_for(source_path: str, text: str, title: str) -> list[dict[str, Any]]:
    if language_for(source_path) == "markdown":
        return markdown_sections(text, title)
    lines = text.splitlines()
    body = text.rstrip("\n")
    return [
        {
            "section_id": "content",
            "title": title,
            "level": 1,
            "line_start": 1,
            "line_end": max(1, len(lines)),
            "text": body,
            "identifiers": unique_identifiers(body),
        }
    ]


def clean_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")].strip()
    title_match = re.match(r"^([^\s]+)(?:\s+[\"'].*)?$", target)
    if title_match:
        return title_match.group(1).strip()
    return target


def resolve_local_target(
    source_path: str,
    target: str,
    known_sources: set[str],
) -> str | None:
    split = urlsplit(target)
    if split.scheme or split.netloc:
        return None
    raw_path = unquote(split.path)
    if not raw_path:
        return source_path if split.fragment else None

    if raw_path.startswith("/"):
        candidate = posixpath.normpath(raw_path.lstrip("/"))
    else:
        base = PurePosixPath(source_path).parent.as_posix()
        candidate = posixpath.normpath(posixpath.join(base, raw_path))
    if candidate == ".." or candidate.startswith("../"):
        return None
    if candidate in known_sources:
        return candidate
    index_candidate = posixpath.join(candidate, "README.md")
    if index_candidate in known_sources:
        return index_candidate
    return None


def links_for(
    source_path: str,
    text: str,
    known_sources: set[str],
) -> list[dict[str, str]]:
    if language_for(source_path) != "markdown":
        return []

    links: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for match in MARKDOWN_LINK_RE.finditer(text):
        target = clean_link_target(match.group(1))
        split = urlsplit(target)
        if target.startswith("#"):
            kind = "anchor"
        elif split.scheme or split.netloc or target.startswith("//"):
            kind = "external"
        elif split.path:
            kind = "local"
        else:
            kind = "other"

        resolved = resolve_local_target(source_path, target, known_sources) if kind == "local" else None
        key = (target, kind, resolved or "")
        if key in seen:
            continue
        seen.add(key)
        item = {"target": target, "kind": kind}
        if resolved:
            item["resolved_source"] = resolved
        links.append(item)
    return links


def relations_for(links: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    targets = sorted({link["resolved_source"] for link in links if "resolved_source" in link})
    return [
        {
            "type": "references",
            "target_document_id": document_id(target),
            "target_source": target,
        }
        for target in targets
    ]


def build_document(source: SourceFile, known_sources: set[str]) -> dict[str, Any]:
    title = title_for(source.relative_path, source.text)
    links = links_for(source.relative_path, source.text, known_sources)
    sections = sections_for(source.relative_path, source.text, title)
    return {
        "schema": "machine/schemas/document.schema.json",
        "schema_version": SCHEMA_VERSION,
        "document_id": document_id(source.relative_path),
        "source": {
            "path": source.relative_path,
            "sha256": sha256_bytes(source.data),
            "media_type": media_type_for(source.relative_path),
            "language": language_for(source.relative_path),
            "bytes": len(source.data),
            "lines": max(1, len(source.text.splitlines())),
            "canonical": True,
        },
        "metadata": {
            "title": title,
            "summary": summary_for(source.relative_path, source.text, title),
            "document_type": document_type_for(source.relative_path),
            "normative": is_normative(source.relative_path),
        },
        "content": source.text,
        "sections": sections,
        "links": links,
        "identifiers": unique_identifiers(source.text),
        "relations": relations_for(links),
        "generation": {
            "tool": TOOL_NAME,
            "version": TOOL_VERSION,
            "deterministic": True,
        },
    }


def source_tree_hash(sources: Iterable[SourceFile]) -> str:
    digest = hashlib.sha256()
    for source in sources:
        digest.update(source.relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_bytes(source.data).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def build_outputs(sources: list[SourceFile]) -> tuple[list[GeneratedOutput], dict[str, Any]]:
    known_sources = {source.relative_path for source in sources}
    tree_hash = source_tree_hash(sources)
    documents: list[tuple[SourceFile, dict[str, Any], str, bytes]] = []
    outputs: list[GeneratedOutput] = []

    for source in sources:
        document = build_document(source, known_sources)
        companion_path = f"machine/documents/{source.relative_path}.json"
        companion_data = json_bytes(document)
        documents.append((source, document, companion_path, companion_data))
        outputs.append(GeneratedOutput(companion_path, companion_data))

    manifest_documents: list[dict[str, Any]] = []
    for source, document, companion_path, companion_data in documents:
        manifest_documents.append(
            {
                "document_id": document["document_id"],
                "source_path": source.relative_path,
                "source_sha256": document["source"]["sha256"],
                "companion_path": companion_path,
                "companion_sha256": sha256_bytes(companion_data),
                "title": document["metadata"]["title"],
                "document_type": document["metadata"]["document_type"],
                "normative": document["metadata"]["normative"],
                "section_count": len(document["sections"]),
                "identifier_count": len(document["identifiers"]),
                "relation_count": len(document["relations"]),
            }
        )

    manifest = {
        "schema": "machine/schemas/manifest.schema.json",
        "schema_version": SCHEMA_VERSION,
        "canonical_representation": "human-readable source files outside machine/",
        "generator": {
            "name": TOOL_NAME,
            "version": TOOL_VERSION,
            "deterministic": True,
        },
        "source_root": ".",
        "source_count": len(sources),
        "source_tree_sha256": tree_hash,
        "documents": manifest_documents,
    }
    outputs.append(GeneratedOutput("machine/manifest.json", json_bytes(manifest)))

    document_nodes = [
        {
            "id": document["document_id"],
            "type": "document",
            "source_path": source.relative_path,
            "title": document["metadata"]["title"],
            "document_type": document["metadata"]["document_type"],
            "normative": document["metadata"]["normative"],
        }
        for source, document, _, _ in documents
    ]

    identifier_values = sorted(
        {identifier for _, document, _, _ in documents for identifier in document["identifiers"]}
    )
    identifier_nodes = [
        {"id": identifier_node_id(identifier), "type": "identifier", "value": identifier}
        for identifier in identifier_values
    ]

    graph_edges: list[dict[str, str]] = []
    for _, document, _, _ in documents:
        for relation in document["relations"]:
            graph_edges.append(
                {
                    "source": document["document_id"],
                    "type": "references",
                    "target": relation["target_document_id"],
                }
            )
        for identifier in document["identifiers"]:
            graph_edges.append(
                {
                    "source": document["document_id"],
                    "type": "declares",
                    "target": identifier_node_id(identifier),
                }
            )
    graph_edges.sort(key=lambda edge: (edge["source"], edge["type"], edge["target"]))

    graph = {
        "schema_version": SCHEMA_VERSION,
        "source_tree_sha256": tree_hash,
        "nodes": sorted(document_nodes + identifier_nodes, key=lambda node: node["id"]),
        "edges": graph_edges,
    }
    outputs.append(GeneratedOutput("machine/graph.json", json_bytes(graph)))

    corpus_records: list[dict[str, Any]] = []
    for source, document, _, _ in documents:
        relation_ids = [relation["target_document_id"] for relation in document["relations"]]
        for section in document["sections"]:
            corpus_records.append(
                {
                    "record_id": f"{document['document_id']}#{section['section_id']}",
                    "document_id": document["document_id"],
                    "source_path": source.relative_path,
                    "source_sha256": document["source"]["sha256"],
                    "document_title": document["metadata"]["title"],
                    "document_type": document["metadata"]["document_type"],
                    "normative": document["metadata"]["normative"],
                    "section_id": section["section_id"],
                    "section_title": section["title"],
                    "section_level": section["level"],
                    "line_start": section["line_start"],
                    "line_end": section["line_end"],
                    "text": section["text"],
                    "identifiers": section["identifiers"],
                    "related_documents": relation_ids,
                }
            )
    corpus_records.sort(key=lambda record: record["record_id"])
    corpus_data = "".join(compact_json(record) + "\n" for record in corpus_records).encode("utf-8")
    outputs.append(GeneratedOutput("machine/corpus.jsonl", corpus_data))

    outputs.sort(key=lambda output: output.relative_path)
    return outputs, manifest


def ensure_safe_generated_root(root: Path) -> None:
    machine_root = root / "machine"
    document_root = machine_root / "documents"
    if machine_root.is_symlink() or document_root.is_symlink():
        raise RuntimeError("machine/ and machine/documents/ must not be symbolic links")


def ensure_safe_output_path(root: Path, path: Path) -> None:
    machine_root = root / "machine"
    try:
        relative = path.relative_to(machine_root)
    except ValueError as error:
        raise RuntimeError(f"generated output escapes machine/: {path}") from error
    current = machine_root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise RuntimeError(f"generated output parent is a symbolic link: {current}")
        if current.exists() and not current.is_dir():
            raise RuntimeError(f"generated output parent is not a directory: {current}")


def atomic_write(root: Path, path: Path, data: bytes) -> bool:
    ensure_safe_output_path(root, path)
    if path.is_file() and path.read_bytes() == data:
        return False
    if path.exists() and not path.is_file():
        raise RuntimeError(f"generated output path is not a regular file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_bytes(data)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return True


def existing_generated_documents(root: Path) -> set[str]:
    document_root = root / "machine" / "documents"
    if not document_root.is_dir():
        return set()
    existing: set[str] = set()
    for path in document_root.rglob("*.json"):
        if path.is_file() and not path.is_symlink():
            existing.add(path.relative_to(root).as_posix())
    return existing


def remove_empty_generated_directories(root: Path) -> None:
    document_root = root / "machine" / "documents"
    if not document_root.is_dir():
        return
    directories = [path for path in document_root.rglob("*") if path.is_dir() and not path.is_symlink()]
    for directory in sorted(directories, key=lambda path: len(path.parts), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass


def write_outputs(root: Path, outputs: list[GeneratedOutput]) -> tuple[int, int]:
    ensure_safe_generated_root(root)
    expected_documents = {
        output.relative_path
        for output in outputs
        if output.relative_path.startswith("machine/documents/")
    }
    orphaned = sorted(existing_generated_documents(root) - expected_documents)
    for relative_path in orphaned:
        path = root / relative_path
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"refusing to remove unsafe generated path: {path}")
        path.unlink()

    changed = 0
    for output in outputs:
        if atomic_write(root, root / output.relative_path, output.data):
            changed += 1
    remove_empty_generated_directories(root)
    return changed, len(orphaned)


def check_outputs(root: Path, outputs: list[GeneratedOutput]) -> list[str]:
    expected_documents = {
        output.relative_path
        for output in outputs
        if output.relative_path.startswith("machine/documents/")
    }
    drift: list[str] = []
    for output in outputs:
        path = root / output.relative_path
        if not path.is_file() or path.is_symlink():
            drift.append(f"missing: {output.relative_path}")
        elif path.read_bytes() != output.data:
            drift.append(f"stale: {output.relative_path}")
    for relative_path in sorted(existing_generated_documents(root) - expected_documents):
        drift.append(f"orphaned: {relative_path}")
    return drift


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate or verify deterministic machine-readable project documents."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root; defaults to the parent of this script's directory.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", dest="mode", action="store_const", const="write", help="Write generated outputs.")
    mode.add_argument("--check", dest="mode", action="store_const", const="check", help="Fail if generated outputs differ.")
    parser.set_defaults(mode="write")
    parser.add_argument("--quiet", action="store_true", help="Suppress success output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"error: project root is not a directory: {root}", file=sys.stderr)
        return 2

    try:
        ensure_safe_generated_root(root)
        sources = discover_sources(root)
        if not sources:
            raise RuntimeError("no canonical UTF-8 source files were discovered")
        outputs, manifest = build_outputs(sources)

        if args.mode == "check":
            drift = check_outputs(root, outputs)
            if drift:
                print("machine-readable documentation is out of sync:", file=sys.stderr)
                for item in drift[:50]:
                    print(f"  {item}", file=sys.stderr)
                if len(drift) > 50:
                    print(f"  ... and {len(drift) - 50} more", file=sys.stderr)
                print(
                    "run: python3 scripts/sync-machine-docs.py --write",
                    file=sys.stderr,
                )
                return 1
            if not args.quiet:
                print(
                    f"Machine documentation is synchronized: {manifest['source_count']} sources."
                )
            return 0

        changed, orphaned = write_outputs(root, outputs)
        if not args.quiet:
            print(
                "Machine documentation synchronized: "
                f"{manifest['source_count']} sources, {changed} outputs changed, "
                f"{orphaned} orphaned companions removed."
            )
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
