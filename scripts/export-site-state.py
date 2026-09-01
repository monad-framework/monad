#!/usr/bin/env python3
"""Export Monad's deterministic website publication projection from an exact Git revision.

The exporter is intentionally local-only. It reads governed source content from Git,
never from the mutable working tree, and never performs network I/O. Output timestamps
are derived from the source commit so repeated exports of the same revision are byte
reproducible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

EXIT_OK = 0
EXIT_DEPENDENCY = 2
EXIT_SCHEMA = 3
EXIT_POLICY = 4
EXIT_SOURCE = 5
EXIT_OUTPUT = 6
EXIT_NOT_MAIN = 7
EXIT_DETERMINISM = 8

POLICY_PATH = "publication/website/projection.yaml"
PROJECTION_SCHEMA_PATH = "schemas/publication/projection.schema.json"
MANIFEST_SCHEMA_PATH = "schemas/publication/manifest.schema.json"
PROVENANCE_SCHEMA_PATH = "schemas/publication/provenance.schema.json"
SITE_STATE_SCHEMA_PATH = "schemas/publication/site-state.schema.json"

STATE_FILENAMES = {
    "project": "project.json",
    "roadmap": "roadmap.json",
    "work-packets": "work-packets.json",
    "milestones": "milestones.json",
    "risks": "risks.json",
    "releases": "releases.json",
    "verification": "verification.json",
    "artifacts": "artifacts.json",
    "research": "research.json",
    "evolution": "evolution.json",
}

GLOB_CHARS = set("*?[")
RESERVED_FRONTMATTER_KEYS = {
    "projection",
    "source_repository",
    "source_path",
    "source_commit",
    "source_blob",
    "projection_version",
    "generated",
}


@dataclass(frozen=True)
class TreeEntry:
    path: str
    blob: str


@dataclass
class OutputRecord:
    destination: str
    content: bytes
    mode: str
    policy_rule_id: str
    source_path: str
    source_blob: str
    inputs: list[TreeEntry]
    source_status: str | None = None
    notes: str | None = None


class ExportError(RuntimeError):
    pass


class GitSnapshot:
    def __init__(self, root: Path, ref: str):
        self.root = root
        self.ref = ref
        self.commit = self._text("rev-parse", f"{ref}^{{commit}}")
        self._tree: dict[str, TreeEntry] | None = None

    def _run(self, *args: str, binary: bool = False) -> bytes | str:
        try:
            result = subprocess.run(
                ["git", "-C", str(self.root), *args],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            detail = ""
            if isinstance(exc, subprocess.CalledProcessError):
                detail = exc.stderr.decode("utf-8", errors="replace").strip()
            raise ExportError(f"git {' '.join(args)} failed{': ' + detail if detail else ''}") from exc
        if binary:
            return result.stdout
        return result.stdout.decode("utf-8").strip()

    def _text(self, *args: str) -> str:
        value = self._run(*args)
        assert isinstance(value, str)
        return value

    @property
    def tree(self) -> dict[str, TreeEntry]:
        if self._tree is None:
            raw = self._run("ls-tree", "-r", "-z", self.commit, binary=True)
            assert isinstance(raw, bytes)
            entries: dict[str, TreeEntry] = {}
            for record in raw.split(b"\0"):
                if not record:
                    continue
                header, path_bytes = record.split(b"\t", 1)
                _mode, obj_type, sha = header.decode("ascii").split(" ", 2)
                if obj_type != "blob":
                    continue
                path = path_bytes.decode("utf-8")
                entries[path] = TreeEntry(path=path, blob=sha)
            self._tree = entries
        return self._tree

    def has(self, path: str) -> bool:
        return path in self.tree

    def entry(self, path: str) -> TreeEntry:
        try:
            return self.tree[path]
        except KeyError as exc:
            raise ExportError(f"source path is not present at {self.commit}: {path}") from exc

    def bytes(self, path: str) -> bytes:
        entry = self.entry(path)
        value = self._run("cat-file", "blob", entry.blob, binary=True)
        assert isinstance(value, bytes)
        return value

    def text(self, path: str) -> str:
        try:
            return self.bytes(path).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ExportError(f"expected UTF-8 source but found binary content: {path}") from exc

    def generated_at(self) -> str:
        raw = self._text("show", "-s", "--format=%cI", self.commit)
        value = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
        return value.isoformat(timespec="seconds").replace("+00:00", "Z")

    def is_on_main(self) -> bool:
        candidates = ["refs/heads/main", "refs/remotes/origin/main"]
        for candidate in candidates:
            try:
                main_commit = self._text("rev-parse", f"{candidate}^{{commit}}")
            except ExportError:
                continue
            result = subprocess.run(
                ["git", "-C", str(self.root), "merge-base", "--is-ancestor", self.commit, main_commit],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                return True
        return False

    def log(self, paths: list[str]) -> list[dict[str, str]]:
        cmd = [
            "git",
            "-C",
            str(self.root),
            "log",
            "--format=%H%x09%cI%x09%s",
            self.commit,
            "--",
            *paths,
        ]
        try:
            result = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise ExportError(f"git log failed: {exc}") from exc
        events: list[dict[str, str]] = []
        for line in result.stdout.splitlines():
            parts = line.split("\t", 2)
            if len(parts) != 3:
                continue
            sha, when, subject = parts
            try:
                dt = datetime.fromisoformat(when.replace("Z", "+00:00")).astimezone(timezone.utc)
                when = dt.isoformat(timespec="seconds").replace("+00:00", "Z")
            except ValueError:
                pass
            events.append({"sha": sha, "when": when, "subject": subject})
        return events


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export Monad's deterministic publication projection from a Git revision. "
            "The exporter performs no network I/O and reads source artifacts from Git, "
            "not from the mutable working tree."
        )
    )
    parser.add_argument("--root", type=Path, default=None, help="repository root; defaults to parent of scripts/")
    parser.add_argument("--ref", default="main", help="Git revision to export; must be reachable from main")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".tmp/publication-export"),
        help="staging root containing destination-repository-relative output",
    )
    parser.add_argument("--clean", action="store_true", help="replace an existing output directory after safety checks")
    parser.add_argument(
        "--verify-determinism",
        action="store_true",
        help="export twice to temporary directories and require byte-identical output before writing --output",
    )
    parser.add_argument("--quiet", action="store_true", help="print only errors and final result")
    return parser.parse_args()


def load_dependencies():
    try:
        import yaml  # type: ignore
        from jsonschema import Draft202012Validator, FormatChecker
        from jsonschema.exceptions import SchemaError
    except ImportError as exc:
        print(
            "ERROR: publication exporter dependencies are missing.\n"
            "Create/activate .venv and run:\n"
            "  python3 -m pip install -r scripts/requirements/publication-validation.txt\n"
            f"Underlying import error: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(EXIT_DEPENDENCY) from exc
    return yaml, Draft202012Validator, FormatChecker, SchemaError


def repository_root(args: argparse.Namespace) -> Path:
    if args.root is not None:
        return args.root.resolve()
    return Path(__file__).resolve().parent.parent


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def has_glob(pattern: str) -> bool:
    return any(char in pattern for char in GLOB_CHARS)


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    i = 0
    out = "^"
    while i < len(pattern):
        char = pattern[i]
        if char == "*":
            if i + 1 < len(pattern) and pattern[i + 1] == "*":
                i += 2
                if i < len(pattern) and pattern[i] == "/":
                    i += 1
                    out += "(?:.*/)?"
                else:
                    out += ".*"
                continue
            out += "[^/]*"
        elif char == "?":
            out += "[^/]"
        elif char == "[":
            end = pattern.find("]", i + 1)
            if end == -1:
                out += re.escape(char)
            else:
                out += pattern[i : end + 1]
                i = end
        else:
            out += re.escape(char)
        i += 1
    return re.compile(out + "$")


def pattern_matches(path: str, pattern: str) -> bool:
    return bool(glob_to_regex(pattern).match(path))


def static_prefix(pattern: str) -> str:
    positions = [pattern.find(char) for char in "*?[" if pattern.find(char) >= 0]
    if not positions:
        return str(PurePosixPath(pattern).parent)
    prefix = pattern[: min(positions)]
    if "/" not in prefix:
        return ""
    return prefix.rsplit("/", 1)[0]


def normalize_relative(path: str) -> str:
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts:
        raise ExportError(f"unsafe destination path: {path}")
    return str(pure)


def markdown_metadata(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines()[:120]:
        match = re.match(r"^\*\*([^:*]+):\*\*\s*(.*?)\s*$", line)
        if match:
            values[match.group(1).strip().lower()] = match.group(2).strip().rstrip("  ")
    return values


def h1(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def id_and_title(value: str | None, fallback_id: str, fallback_title: str) -> tuple[str, str]:
    if not value:
        return fallback_id, fallback_title
    for sep in (" — ", " – ", " - "):
        if sep in value:
            left, right = value.split(sep, 1)
            if re.match(r"^[A-Z][A-Z0-9-]*\d", left.strip()):
                return left.strip(), right.strip()
    first = value.split()[0].strip("[]():") if value.split() else fallback_id
    if re.match(r"^[A-Z][A-Z0-9-]*\d", first):
        rest = value[len(value.split()[0]) :].strip(" —–-:")
        return first, rest or fallback_title
    return fallback_id, value


def section_text(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    target = f"## {heading}".lower()
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == target:
            start = idx + 1
            break
    if start is None:
        return None
    body: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    paragraphs = "\n".join(body).strip().split("\n\n")
    for paragraph in paragraphs:
        cleaned = " ".join(piece.strip() for piece in paragraph.splitlines()).strip()
        if cleaned:
            return cleaned
    return None


def first_paragraph(text: str) -> str | None:
    body: list[str] = []
    seen_h1 = False
    for line in text.splitlines():
        if line.startswith("# ") and not seen_h1:
            seen_h1 = True
            continue
        if not seen_h1:
            continue
        if line.startswith("[") and "](" in line:
            continue
        if line.startswith("!"):
            continue
        if line.startswith("## "):
            break
        body.append(line)
    for paragraph in "\n".join(body).split("\n\n"):
        cleaned = " ".join(piece.strip() for piece in paragraph.splitlines()).strip()
        if cleaned:
            return cleaned
    return None


def strip_md(value: str) -> str:
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", value)
    value = value.replace("**", "").replace("__", "")
    return value.strip()


def extract_identifier(value: str | None, prefix: str) -> str | None:
    if not value:
        return None
    match = re.search(rf"\b{re.escape(prefix)}[A-Z0-9-]*\d+[A-Z0-9-]*\b", value)
    return match.group(0) if match else None


def extract_all_identifiers(value: str, prefix: str) -> list[str]:
    return sorted(set(re.findall(rf"\b{re.escape(prefix)}[A-Z0-9-]*\d+[A-Z0-9-]*\b", value)))


def parse_markdown_table(text: str, required_header: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        headers = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if required_header not in headers:
            continue
        if idx + 1 >= len(lines) or not re.match(r"^\s*\|?\s*:?-+", lines[idx + 1]):
            continue
        rows: list[dict[str, str]] = []
        for row_line in lines[idx + 2 :]:
            if not row_line.strip().startswith("|"):
                break
            cells = [cell.strip() for cell in row_line.strip().strip("|").split("|")]
            if len(cells) != len(headers):
                continue
            rows.append(dict(zip(headers, cells)))
        return rows
    return []


def parse_target_date(value: str | None) -> tuple[str | None, bool]:
    if not value:
        return None, False
    match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", value)
    return (match.group(0) if match else None, "forecast" in value.lower())


def source_status(text: str) -> str | None:
    return markdown_metadata(text).get("status")


def frontmatter_block(source_path: str, source_commit: str, source_blob: str, mode: str = "mirror") -> list[str]:
    return [
        f"projection: {mode}",
        'source_repository: "monad-framework/monad"',
        f"source_path: {json.dumps(source_path)}",
        f"source_commit: {json.dumps(source_commit)}",
        f"source_blob: {json.dumps(source_blob)}",
        "projection_version: 1",
        "generated: true",
    ]


def inject_frontmatter(text: str, source_path: str, source_commit: str, source_blob: str) -> str:
    fields = frontmatter_block(source_path, source_commit, source_blob)
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        closing = None
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                closing = idx
                break
        if closing is None:
            raise ExportError(f"unterminated YAML frontmatter in {source_path}")
        existing_keys: set[str] = set()
        for line in lines[1:closing]:
            match = re.match(r"^([A-Za-z0-9_-]+):", line)
            if match:
                existing_keys.add(match.group(1))
        conflict = RESERVED_FRONTMATTER_KEYS.intersection(existing_keys)
        if conflict:
            raise ExportError(
                f"source frontmatter uses projection-reserved keys in {source_path}: {', '.join(sorted(conflict))}"
            )
        merged = lines[:closing] + fields + lines[closing:]
        return "\n".join(merged) + ("\n" if text.endswith("\n") else "")
    block = ["---", *fields, "---", ""]
    return "\n".join(block) + text


def relative_link(from_destination: str, to_destination: str) -> str:
    source_dir = PurePosixPath(from_destination).parent
    source_parts = source_dir.parts
    target_parts = PurePosixPath(to_destination).parts
    common = 0
    for left, right in zip(source_parts, target_parts):
        if left != right:
            break
        common += 1
    pieces = [".."] * (len(source_parts) - common) + list(target_parts[common:])
    return "/".join(pieces) or PurePosixPath(to_destination).name


def rewrite_markdown_links(text: str, source_path: str, destination: str, mirror_map: dict[str, str]) -> str:
    source_parent = PurePosixPath(source_path).parent
    pattern = re.compile(r"(?P<prefix>!?)\[(?P<label>[^\]]*)\]\((?P<target>[^)]+)\)")

    def replace(match: re.Match[str]) -> str:
        target = match.group("target").strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)
        if " " in target and not target.startswith("<"):
            # Avoid rewriting Markdown targets with titles; a full Markdown parser
            # belongs in a later rendering-specific layer.
            return match.group(0)
        raw_target = target.strip("<>")
        path_part, sep, fragment = raw_target.partition("#")
        if not path_part:
            return match.group(0)
        if path_part.startswith("/"):
            resolved = str(PurePosixPath(path_part.lstrip("/")))
        else:
            resolved = str(source_parent.joinpath(path_part))
        # Resolve . and .. without touching the filesystem.
        stack: list[str] = []
        for part in PurePosixPath(resolved).parts:
            if part in ("", "."):
                continue
            if part == "..":
                if stack:
                    stack.pop()
                continue
            stack.append(part)
        resolved = "/".join(stack)
        mapped = mirror_map.get(resolved)
        if not mapped:
            return match.group(0)
        new_target = relative_link(destination, mapped)
        if sep:
            new_target += "#" + fragment
        return f"{match.group('prefix')}[{match.group('label')}]({new_target})"

    return pattern.sub(replace, text)


def render_plain_text_mdx(text: str, source_path: str, commit: str, blob: str) -> str:
    fields = frontmatter_block(source_path, commit, blob)
    fence = "````"
    return "\n".join(["---", *fields, "---", "", f"# {PurePosixPath(source_path).name}", "", f"{fence}text", text.rstrip("\n"), fence, ""])


def derived_frontmatter(title: str, description: str, commit: str) -> str:
    return "\n".join(
        [
            "---",
            f"title: {json.dumps(title)}",
            f"description: {json.dumps(description)}",
            "projection: derive",
            f"source_commit: {json.dumps(commit)}",
            "projection_version: 1",
            "generated: true",
            "---",
            "",
        ]
    )


def validate_json(instance: Any, schema: Any, validator_cls, format_checker, label: str) -> None:
    validator = validator_cls(schema, format_checker=format_checker)
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    if not errors:
        return
    error = errors[0]
    path = "$" + "".join(
        f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path
    )
    raise ExportError(f"{label} failed schema validation at {path}: {error.message}")


class Exporter:
    def __init__(self, root: Path, snapshot: GitSnapshot, yaml_module, validator_cls, format_checker_cls, schema_error_cls, quiet: bool):
        self.root = root
        self.snapshot = snapshot
        self.yaml = yaml_module
        self.validator_cls = validator_cls
        self.format_checker = format_checker_cls()
        self.schema_error_cls = schema_error_cls
        self.quiet = quiet
        self.generated_at = snapshot.generated_at()
        self.policy = self._load_yaml_from_snapshot(POLICY_PATH)
        self.schemas = {
            "projection": self._load_json_from_snapshot(PROJECTION_SCHEMA_PATH),
            "manifest": self._load_json_from_snapshot(MANIFEST_SCHEMA_PATH),
            "provenance": self._load_json_from_snapshot(PROVENANCE_SCHEMA_PATH),
            "site-state": self._load_json_from_snapshot(SITE_STATE_SCHEMA_PATH),
        }
        self._validate_contracts()
        self.policy_entry = self.snapshot.entry(POLICY_PATH)
        self.outputs: dict[str, OutputRecord] = {}
        self.mirror_source_to_destination: dict[str, str] = {}
        self.derive_inputs_by_output: dict[str, list[TreeEntry]] = {}
        self.state: dict[str, Any] = {}

    def _load_yaml_from_snapshot(self, path: str) -> Any:
        try:
            return self.yaml.safe_load(self.snapshot.text(path))
        except self.yaml.YAMLError as exc:
            raise ExportError(f"invalid YAML at {path}: {exc}") from exc

    def _load_json_from_snapshot(self, path: str) -> Any:
        try:
            return json.loads(self.snapshot.text(path))
        except json.JSONDecodeError as exc:
            raise ExportError(f"invalid JSON at {path}: {exc}") from exc

    def _validate_contracts(self) -> None:
        for name, schema in self.schemas.items():
            try:
                self.validator_cls.check_schema(schema)
            except self.schema_error_cls as exc:
                raise ExportError(f"invalid {name} JSON Schema: {exc.message}") from exc
        validate_json(
            self.policy,
            self.schemas["projection"],
            self.validator_cls,
            self.format_checker,
            POLICY_PATH,
        )

    def expand_patterns(self, value: str | list[str], excludes: list[str] | None = None) -> list[TreeEntry]:
        patterns = [value] if isinstance(value, str) else list(value)
        excludes = excludes or []
        found: dict[str, TreeEntry] = {}
        for pattern in patterns:
            if has_glob(pattern):
                for path, entry in self.snapshot.tree.items():
                    if pattern_matches(path, pattern):
                        found[path] = entry
            elif self.snapshot.has(pattern):
                found[pattern] = self.snapshot.entry(pattern)
            else:
                raise ExportError(f"required exact source does not exist at {self.snapshot.commit}: {pattern}")
        for path in list(found):
            if any(pattern_matches(path, pattern) for pattern in excludes):
                del found[path]
        return [found[path] for path in sorted(found)]

    def mirror_destination(self, rule: dict[str, Any], source_path: str) -> str:
        destination = normalize_relative(rule["destination"])
        strategy = rule.get("destination_strategy")
        if strategy is None:
            return destination
        if strategy == "preserve_basename":
            result = str(PurePosixPath(destination) / PurePosixPath(source_path).name)
        elif strategy == "preserve_relative_path":
            relative_to = rule.get("relative_to")
            if not relative_to:
                source_value = rule["source"]
                first_pattern = source_value[0] if isinstance(source_value, list) else source_value
                relative_to = static_prefix(first_pattern)
            root = PurePosixPath(relative_to)
            source = PurePosixPath(source_path)
            try:
                relative = source.relative_to(root)
            except ValueError as exc:
                raise ExportError(
                    f"{rule['id']} cannot preserve path {source_path} relative to {relative_to}"
                ) from exc
            result = str(PurePosixPath(destination) / relative)
        else:
            raise ExportError(f"unsupported destination strategy in {rule['id']}: {strategy}")
        extension = rule.get("extension")
        if extension:
            result = str(PurePosixPath(result).with_suffix(extension))
        return normalize_relative(result)

    def plan_mirrors(self) -> list[tuple[dict[str, Any], TreeEntry, str]]:
        plans: list[tuple[dict[str, Any], TreeEntry, str]] = []
        for rule in self.policy["mirror"]:
            optional = bool(rule.get("optional_source_family"))
            try:
                matches = self.expand_patterns(rule["source"], rule.get("exclude"))
            except ExportError:
                if optional:
                    matches = []
                else:
                    raise
            if not matches and not optional and isinstance(rule["source"], str) and not has_glob(rule["source"]):
                raise ExportError(f"{rule['id']} matched no required source")
            for entry in matches:
                destination = self.mirror_destination(rule, entry.path)
                plans.append((rule, entry, destination))
                current = self.mirror_source_to_destination.get(entry.path)
                if current is None:
                    self.mirror_source_to_destination[entry.path] = destination
        return plans

    def add_output(self, record: OutputRecord) -> None:
        destination = normalize_relative(record.destination)
        if destination in {
            self.policy["generated_state"]["manifest"],
            self.policy["generated_state"]["provenance"],
        }:
            raise ExportError(f"projection rule may not write metadata envelope path directly: {destination}")
        existing = self.outputs.get(destination)
        if existing is not None:
            raise ExportError(
                f"projection destination collision: {destination} from {existing.policy_rule_id} and {record.policy_rule_id}"
            )
        record.destination = destination
        self.outputs[destination] = record

    def execute_mirrors(self, plans: list[tuple[dict[str, Any], TreeEntry, str]]) -> None:
        for rule, entry, destination in plans:
            transformation = rule["transformation"]
            raw = self.snapshot.bytes(entry.path)
            status = None
            if entry.path.endswith((".md", ".mdx")):
                try:
                    status = source_status(raw.decode("utf-8"))
                except UnicodeDecodeError:
                    status = None
            if transformation in {"markdown_archive", "structured_copy"}:
                content = raw
            elif transformation == "markdown_mirror":
                text = raw.decode("utf-8")
                text = rewrite_markdown_links(text, entry.path, destination, self.mirror_source_to_destination)
                content = inject_frontmatter(text, entry.path, self.snapshot.commit, entry.blob).encode("utf-8")
            elif transformation == "plain_text_to_mdx":
                content = render_plain_text_mdx(
                    raw.decode("utf-8"), entry.path, self.snapshot.commit, entry.blob
                ).encode("utf-8")
            else:
                raise ExportError(f"unsupported mirror transformation {transformation} in {rule['id']}")
            self.add_output(
                OutputRecord(
                    destination=destination,
                    content=content,
                    mode="MIRROR",
                    policy_rule_id=rule["id"],
                    source_path=entry.path,
                    source_blob=entry.blob,
                    inputs=[entry],
                    source_status=status,
                )
            )

    def rule_by_id(self, rule_id: str) -> dict[str, Any]:
        for rule in self.policy["derive"]:
            if rule["id"] == rule_id:
                return rule
        raise ExportError(f"derive rule not found: {rule_id}")

    def rule_inputs(self, rule: dict[str, Any]) -> list[TreeEntry]:
        inputs: dict[str, TreeEntry] = {}
        for pattern in rule.get("inputs", []):
            try:
                matches = self.expand_patterns(pattern)
            except ExportError:
                # Exact optional-ish execution inputs such as .eos may legitimately
                # be absent in a historical commit; DERIVE rules remain conservative.
                matches = []
            for entry in matches:
                inputs[entry.path] = entry
        for state_path in rule.get("state_inputs", []):
            for entry in self.derive_inputs_by_output.get(state_path, []):
                inputs[entry.path] = entry
        return [inputs[path] for path in sorted(inputs)]

    def text_if_present(self, path: str) -> str | None:
        return self.snapshot.text(path) if self.snapshot.has(path) else None

    def entry_if_present(self, path: str) -> TreeEntry | None:
        return self.snapshot.entry(path) if self.snapshot.has(path) else None

    def build_project_state(self, rule: dict[str, Any]) -> tuple[dict[str, Any], list[TreeEntry], str]:
        status_text = self.snapshot.text("engineering/project-status.md")
        status_meta = markdown_metadata(status_text)
        backlog_text = self.text_if_present("product/backlog/MVP-BACKLOG.md") or ""
        backlog_meta = markdown_metadata(backlog_text)
        readme = self.snapshot.text("README.md")
        version = (self.text_if_present("VERSION") or "").strip() or None
        identity_name = "Monad"
        description = first_paragraph(readme)
        project_toml = self.text_if_present("monad.toml")
        if project_toml:
            try:
                parsed = tomllib.loads(project_toml)
                identity_name = parsed.get("project", {}).get("name", identity_name)
            except tomllib.TOMLDecodeError as exc:
                raise ExportError(f"monad.toml is invalid at {self.snapshot.commit}: {exc}") from exc

        overall = status_meta.get("overall state", "unknown")
        current_milestone = status_meta.get("current milestone")
        current_increment = status_meta.get("current increment")
        current_cycle = status_meta.get("current work cycle")
        current_packet = status_meta.get("current packet")
        active_packets = extract_all_identifiers(current_packet or "", "WP-")
        product_goal = backlog_meta.get("product goal") or extract_identifier(status_text, "PG-")

        cargo_info: dict[str, Any] = {}
        cargo_text = self.text_if_present("Cargo.toml")
        if cargo_text:
            try:
                cargo = tomllib.loads(cargo_text)
                workspace = cargo.get("workspace", {})
                package = cargo.get("package", {})
                if package.get("name") is not None:
                    cargo_info["packageName"] = str(package["name"])
                if package.get("version") is not None:
                    cargo_info["packageVersion"] = str(package["version"])
                if workspace.get("members"):
                    cargo_info["workspaceMembers"] = sorted(str(x) for x in workspace["members"])
            except tomllib.TOMLDecodeError as exc:
                raise ExportError(f"Cargo.toml is invalid at {self.snapshot.commit}: {exc}") from exc

        sources = [
            {"path": path}
            for path in [
                "README.md",
                "VERSION",
                "monad.toml",
                "Cargo.toml",
                "product/backlog/MVP-BACKLOG.md",
                "engineering/project-status.md",
            ]
            if self.snapshot.has(path)
        ]
        value: dict[str, Any] = {
            "schemaVersion": 1,
            "kind": "project",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "identity": {
                "name": identity_name,
                "repository": "monad-framework/monad",
                "description": description,
            },
            "version": version,
            "status": strip_md(overall),
            "phase": strip_md(current_milestone) if current_milestone else None,
            "productGoal": strip_md(product_goal) if product_goal else None,
            "activeIncrement": extract_identifier(current_increment, "PI-") if current_increment else None,
            "activeWorkCycle": extract_identifier(current_cycle, "WC-") if current_cycle else None,
            "activeWorkPackets": active_packets,
            "nextGate": None,
            "blockers": [],
            "sources": sources,
        }
        if cargo_info:
            value["implementation"] = {"cargo": cargo_info}
        inputs = self.rule_inputs(rule)
        for extra in ["VERSION", "monad.toml", "Cargo.toml"]:
            entry = self.entry_if_present(extra)
            if entry:
                inputs.append(entry)
        inputs = unique_entries(inputs)
        notes = "Includes deterministic fields authorized by DERIVE-VERSION, DERIVE-MONAD-TOML-IDENTITY, and DERIVE-CARGO-METADATA."
        return value, inputs, notes

    def build_work_packets_state(self, rule: dict[str, Any]) -> tuple[dict[str, Any], list[TreeEntry]]:
        items: list[dict[str, Any]] = []
        active: list[str] = []
        for path in sorted(self.snapshot.tree):
            if not pattern_matches(path, "engineering/work-packets/*.md"):
                continue
            name = PurePosixPath(path).name
            if name == "README.md" or name.endswith("-FORECAST.md"):
                continue
            text = self.snapshot.text(path)
            heading = h1(text)
            fallback = PurePosixPath(path).stem
            wp_id, title = id_and_title(heading, fallback, fallback)
            if not wp_id.startswith("WP-"):
                continue
            meta = markdown_metadata(text)
            status = strip_md(meta.get("status", "UNKNOWN"))
            item: dict[str, Any] = {
                "id": wp_id,
                "title": title,
                "status": status,
                "authorizationState": "AUTHORIZED" if "AUTHORIZED" in status.upper() else None,
                "workCycle": extract_identifier(meta.get("work cycle"), "WC-") if meta.get("work cycle") else None,
                "increment": extract_identifier(meta.get("program increment"), "PI-") if meta.get("program increment") else None,
                "objective": section_text(text, "Objective"),
                "nextGate": None,
                "blockedBy": [],
                "sourcePath": path,
            }
            items.append(item)
            closed_tokens = ("CLOSED", "COMPLETE", "CANCELLED", "CANCELED", "RETIRED", "PLANNED", "DRAFT")
            if not any(token in status.upper() for token in closed_tokens):
                active.append(wp_id)
        items.sort(key=lambda item: item["id"])
        active = sorted(set(active))
        return {
            "schemaVersion": 1,
            "kind": "work-packets",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "active": active,
            "items": items,
        }, self.rule_inputs(rule)

    def build_milestones_state(self, rule: dict[str, Any]) -> tuple[dict[str, Any], list[TreeEntry]]:
        items: list[dict[str, Any]] = []
        for path in sorted(self.snapshot.tree):
            if not pattern_matches(path, "engineering/milestones/**/*.md"):
                continue
            if PurePosixPath(path).name == "README.md":
                continue
            text = self.snapshot.text(path)
            fallback = PurePosixPath(path).stem.split("-", 2)[0]
            milestone_id, title = id_and_title(h1(text), fallback, PurePosixPath(path).stem)
            if not milestone_id.startswith("M-"):
                continue
            meta = markdown_metadata(text)
            target, forecast = parse_target_date(meta.get("target gate") or meta.get("target date"))
            item: dict[str, Any] = {
                "id": milestone_id,
                "title": title,
                "status": strip_md(meta.get("status", "UNKNOWN")),
                "targetDate": target,
                "forecast": forecast,
                "sourcePath": path,
            }
            items.append(item)
        items.sort(key=lambda item: item["id"])
        return {
            "schemaVersion": 1,
            "kind": "milestones",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "items": items,
        }, self.rule_inputs(rule)

    def build_risks_state(self, rule: dict[str, Any]) -> tuple[dict[str, Any], list[TreeEntry]]:
        items: list[dict[str, Any]] = []
        for entry in self.rule_inputs(rule):
            if not entry.path.endswith(".md"):
                continue
            text = self.snapshot.text(entry.path)
            rows = parse_markdown_table(text, "ID")
            for row in rows:
                risk_id = strip_md(row.get("ID", ""))
                if not risk_id.startswith("R-"):
                    continue
                items.append(
                    {
                        "id": risk_id,
                        "title": strip_md(row.get("Risk", risk_id)),
                        "status": strip_md(row.get("State", "UNKNOWN")),
                        "severity": strip_md(row.get("I", "")) or None,
                        "likelihood": strip_md(row.get("L", "")) or None,
                        "owner": strip_md(row.get("Owner", "")) or None,
                        "mitigation": strip_md(row.get("Response and leading indicator", "")) or None,
                        "sourcePath": entry.path,
                    }
                )
        items.sort(key=lambda item: item["id"])
        return {
            "schemaVersion": 1,
            "kind": "risks",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "items": items,
        }, self.rule_inputs(rule)

    def build_releases_state(self, rule: dict[str, Any]) -> tuple[dict[str, Any], list[TreeEntry], str]:
        version = (self.text_if_present("VERSION") or "").strip() or None
        changelog = self.text_if_present("CHANGELOG.md") or ""
        releases: list[dict[str, Any]] = []
        for match in re.finditer(r"^## \[([^\]]+)\](?:\s+-\s+(\d{4}-\d{2}-\d{2}))?\s*$", changelog, re.MULTILINE):
            label, date = match.groups()
            if label.lower() == "unreleased":
                continue
            released_at = f"{date}T00:00:00Z" if date else None
            releases.append(
                {
                    "version": label,
                    "status": "released",
                    "releasedAt": released_at,
                    "sourcePath": "CHANGELOG.md",
                    "sourceTag": None,
                }
            )
        latest = releases[0]["version"] if releases else None
        value = {
            "schemaVersion": 1,
            "kind": "releases",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "currentVersion": version,
            "latestRelease": latest,
            "releases": releases,
        }
        notes = "Deterministic offline export uses VERSION and CHANGELOG. GitHub Releases is reserved for the later LIVE/enrichment layer."
        return value, self.rule_inputs(rule), notes

    def build_verification_state(self, rule: dict[str, Any]) -> tuple[dict[str, Any], list[TreeEntry]]:
        path = "testing/quality-gates.md"
        gates: list[dict[str, Any]] = []
        if self.snapshot.has(path):
            text = self.snapshot.text(path)
            gate_index = 0
            for line in text.splitlines():
                if not line.startswith("## "):
                    continue
                name = line[3:].strip()
                if "gate" not in name.lower():
                    continue
                gate_index += 1
                gate_id = "GATE-" + re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-")
                gates.append(
                    {
                        "id": gate_id,
                        "name": name,
                        "status": "unknown",
                        "evidence": [],
                        "sourcePath": path,
                    }
                )
        return {
            "schemaVersion": 1,
            "kind": "verification",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "overallStatus": "unknown",
            "gates": gates,
        }, self.rule_inputs(rule)

    def mirror_destination_for_source(self, path: str) -> str | None:
        return self.mirror_source_to_destination.get(path)

    def build_artifacts_state(self, rule: dict[str, Any]) -> tuple[dict[str, Any], list[TreeEntry]]:
        entries = self.rule_inputs(rule)
        items: list[dict[str, Any]] = []
        for entry in entries:
            path = entry.path
            if not path.endswith((".md", ".mdx", ".json", ".yaml", ".yml")):
                continue
            title = None
            status = None
            artifact_id = None
            if path.endswith((".md", ".mdx")):
                text = self.snapshot.text(path)
                heading = h1(text)
                if heading:
                    candidate, parsed_title = id_and_title(heading, "", heading)
                    if candidate:
                        artifact_id = candidate
                    title = parsed_title
                status = markdown_metadata(text).get("status")
            root = path.split("/", 1)[0]
            artifact_type = {
                "architecture": "architecture",
                "specifications": "specification",
                "artifact-system": "artifact-contract",
                "engineering": "engineering-record",
                "testing": "verification",
                "research": "research",
            }.get(root, root)
            items.append(
                {
                    "id": artifact_id,
                    "title": title,
                    "type": artifact_type,
                    "status": strip_md(status) if status else None,
                    "sourcePath": path,
                    "destinationPath": self.mirror_destination_for_source(path),
                }
            )
        items.sort(key=lambda item: item["sourcePath"])
        return {
            "schemaVersion": 1,
            "kind": "artifacts",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "items": items,
        }, entries

    def build_research_state(self, rule: dict[str, Any]) -> tuple[dict[str, Any], list[TreeEntry]]:
        questions: list[dict[str, Any]] = []
        qpath = "research/questions.md"
        if self.snapshot.has(qpath):
            text = self.snapshot.text(qpath)
            for line in text.splitlines():
                if not line.startswith("### "):
                    continue
                value = line[4:].strip()
                qid, question = id_and_title(value, "", value)
                if qid.startswith("RQ-"):
                    questions.append(
                        {"id": qid, "question": question, "status": "open", "sourcePath": qpath}
                    )
        questions.sort(key=lambda item: item["id"])

        def records_under(prefix: str) -> list[dict[str, Any]]:
            records: list[dict[str, Any]] = []
            for path in sorted(self.snapshot.tree):
                if not path.startswith(prefix + "/") or not path.endswith(".md"):
                    continue
                text = self.snapshot.text(path)
                fallback = PurePosixPath(path).stem
                rid, title = id_and_title(h1(text), fallback, fallback)
                records.append(
                    {
                        "id": rid,
                        "title": title,
                        "status": strip_md(markdown_metadata(text).get("status", "unknown")),
                        "sourcePath": path,
                    }
                )
            return records

        return {
            "schemaVersion": 1,
            "kind": "research",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "openQuestions": questions,
            "experiments": records_under("research/experiments"),
            "findings": records_under("research/findings"),
        }, self.rule_inputs(rule)

    def build_roadmap_state(self, rule: dict[str, Any]) -> tuple[dict[str, Any], list[TreeEntry]]:
        items: list[dict[str, Any]] = []
        backlog_path = "product/backlog/MVP-BACKLOG.md"
        if self.snapshot.has(backlog_path):
            text = self.snapshot.text(backlog_path)
            rows = parse_markdown_table(text, "Epic")
            sequence = 0
            for row in rows:
                epic_cell = strip_md(row.get("Epic", ""))
                match = re.match(r"^(EPIC-\d+)\s+(.*)$", epic_cell)
                if not match:
                    continue
                sequence += 1
                items.append(
                    {
                        "id": match.group(1),
                        "title": match.group(2).strip(),
                        "type": "epic",
                        "status": "forecast",
                        "sequence": sequence,
                        "targetDate": None,
                        "forecast": True,
                        "parentId": None,
                        "sourcePath": backlog_path,
                    }
                )
        milestone_state, _ = self.build_milestones_state(self.rule_by_id("DERIVE-MILESTONES"))
        sequence = len(items)
        for milestone in milestone_state["items"]:
            sequence += 1
            items.append(
                {
                    "id": milestone["id"],
                    "title": milestone["title"],
                    "type": "milestone",
                    "status": milestone["status"],
                    "sequence": sequence,
                    "targetDate": milestone.get("targetDate"),
                    "forecast": bool(milestone.get("forecast", False)),
                    "parentId": None,
                    "sourcePath": milestone["sourcePath"],
                }
            )
        return {
            "schemaVersion": 1,
            "kind": "roadmap",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "items": items,
        }, self.rule_inputs(rule)

    def build_evolution_state(self, rule: dict[str, Any]) -> tuple[dict[str, Any], list[TreeEntry], str]:
        log_paths = [
            "architecture/decisions",
            "specifications",
            "product",
            "engineering/changes",
            "engineering/work-packets",
            "engineering/milestones",
            "engineering/increments",
            "engineering/evidence",
            "testing",
            "VERSION",
            "CHANGELOG.md",
        ]
        events = [
            {
                "id": f"commit:{entry['sha']}",
                "type": "repository-change",
                "summary": entry["subject"],
                "occurredAt": entry["when"],
                "sourcePath": None,
                "commit": entry["sha"],
                "externalReference": None,
            }
            for entry in self.snapshot.log(log_paths)
        ]
        notes = "Evolution is derived from local Git history for governed input paths; merged-PR enrichment is deferred to the external/live layer."
        return {
            "schemaVersion": 1,
            "kind": "evolution",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "events": events,
        }, self.rule_inputs(rule), notes

    def add_derived_json(self, rule: dict[str, Any], value: dict[str, Any], inputs: list[TreeEntry], notes: str | None = None) -> None:
        output = rule["output"]
        validate_json(value, self.schemas["site-state"], self.validator_cls, self.format_checker, output)
        content = json_bytes(value)
        self.state[value["kind"]] = value
        inputs = unique_entries(inputs)
        self.derive_inputs_by_output[output] = inputs
        self.add_output(
            OutputRecord(
                destination=output,
                content=content,
                mode="DERIVE",
                policy_rule_id=rule["id"],
                source_path=POLICY_PATH,
                source_blob=self.policy_entry.blob,
                inputs=inputs,
                notes=notes,
            )
        )

    def render_project_index(self) -> str:
        project = self.state["project"]
        return derived_frontmatter("Project", "Current governed Monad project state", self.snapshot.commit) + "\n".join(
            [
                "# Project",
                "",
                f"**Status:** {project['status']}",
                f"**Version:** {project.get('version') or 'not released'}",
                f"**Active increment:** {project.get('activeIncrement') or 'none'}",
                f"**Active work cycle:** {project.get('activeWorkCycle') or 'none'}",
                f"**Active Work Packets:** {', '.join(project.get('activeWorkPackets', [])) or 'none'}",
                "",
                "This page is generated from Monad's governed project state. It is not independently maintained website status.",
                "",
            ]
        )

    def render_project_now(self) -> str:
        project = self.state["project"]
        packets = self.state["work-packets"]
        by_id = {item["id"]: item for item in packets["items"]}
        lines = [
            derived_frontmatter("Now", "What Monad is working on now", self.snapshot.commit),
            "# Now",
            "",
            f"**Project status:** {project['status']}",
            f"**Increment:** {project.get('activeIncrement') or 'none'}",
            f"**Work cycle:** {project.get('activeWorkCycle') or 'none'}",
            "",
            "## Active Work Packets",
            "",
        ]
        active = project.get("activeWorkPackets", []) or packets.get("active", [])
        if not active:
            lines.append("No active Work Packet is declared by the current governed state.")
        for wp_id in active:
            item = by_id.get(wp_id)
            if item:
                lines.append(f"- **{wp_id} — {item['title']}** — {item['status']}")
            else:
                lines.append(f"- **{wp_id}**")
        lines.extend(["", "Generated deterministically from the exact Monad source revision shown in this page's provenance metadata.", ""])
        return "\n".join(lines)

    def render_project_status(self) -> str:
        project = self.state["project"]
        risks = self.state["risks"]
        verification = self.state["verification"]
        return derived_frontmatter("Project Status", "Governed Monad project status", self.snapshot.commit) + "\n".join(
            [
                "# Project Status",
                "",
                f"**Overall state:** {project['status']}",
                f"**Current phase/milestone:** {project.get('phase') or 'not declared'}",
                f"**Current increment:** {project.get('activeIncrement') or 'none'}",
                f"**Current work cycle:** {project.get('activeWorkCycle') or 'none'}",
                f"**Verification:** {verification['overallStatus']}",
                f"**Open risk records:** {len(risks['items'])}",
                "",
                "Website status is a deterministic projection of canonical Monad records. Live GitHub operational state is intentionally separate.",
                "",
            ]
        )

    def render_roadmap_page(self) -> str:
        roadmap = self.state["roadmap"]
        lines = [derived_frontmatter("Roadmap", "Governed Monad roadmap projection", self.snapshot.commit), "# Roadmap", "", "| ID | Type | Outcome | Status | Target |", "| --- | --- | --- | --- | --- |"]
        for item in roadmap["items"]:
            lines.append(
                f"| {item['id']} | {item['type']} | {item['title'].replace('|', '\\|')} | {item['status']} | {item.get('targetDate') or ''} |"
            )
        lines.append("")
        return "\n".join(lines)

    def render_work_packet_index(self) -> str:
        packets = self.state["work-packets"]
        lines = [derived_frontmatter("Work Packets", "Governed Monad Work Packet inventory", self.snapshot.commit), "# Work Packets", "", "| Work Packet | Title | Status | Work Cycle | Increment |", "| --- | --- | --- | --- | --- |"]
        for item in packets["items"]:
            lines.append(
                f"| {item['id']} | {item['title'].replace('|', '\\|')} | {item['status']} | {item.get('workCycle') or ''} | {item.get('increment') or ''} |"
            )
        lines.append("")
        return "\n".join(lines)

    def render_risk_index(self) -> str:
        risks = self.state["risks"]
        lines = [derived_frontmatter("Risks", "Current governed Monad risk register projection", self.snapshot.commit), "# Risks", "", "| ID | Risk | Status | Likelihood | Severity | Owner |", "| --- | --- | --- | --- | --- | --- |"]
        for item in risks["items"]:
            lines.append(
                f"| {item['id']} | {item['title'].replace('|', '\\|')} | {item['status']} | {item.get('likelihood') or ''} | {item.get('severity') or ''} | {item.get('owner') or ''} |"
            )
        lines.append("")
        return "\n".join(lines)

    def render_releases_page(self) -> str:
        releases = self.state["releases"]
        lines = [derived_frontmatter("Releases", "Monad release-state projection", self.snapshot.commit), "# Releases", "", f"**Current version marker:** {releases.get('currentVersion') or 'none'}", ""]
        if releases["releases"]:
            lines.extend(["| Version | Status | Released |", "| --- | --- | --- |"]) 
            for item in releases["releases"]:
                lines.append(f"| {item['version']} | {item['status']} | {item.get('releasedAt') or ''} |")
        else:
            lines.append("No dated release section exists in the canonical changelog at this revision.")
        lines.append("")
        return "\n".join(lines)

    def render_system_overview(self) -> str:
        readme = self.snapshot.text("README.md")
        title = h1(readme) or "Monad"
        description = first_paragraph(readme) or "Monad system overview"
        return derived_frontmatter("System", "Authoritative Monad system overview projection", self.snapshot.commit) + "\n".join(
            [f"# {title}", "", description, "", "This page is generated from the canonical repository README at the exact source revision recorded above.", ""]
        )

    def add_derived_page(self, rule: dict[str, Any], content: str, inputs: list[TreeEntry]) -> None:
        output = rule["output"]
        inputs = unique_entries(inputs)
        self.derive_inputs_by_output[output] = inputs
        self.add_output(
            OutputRecord(
                destination=output,
                content=content.encode("utf-8"),
                mode="DERIVE",
                policy_rule_id=rule["id"],
                source_path=POLICY_PATH,
                source_blob=self.policy_entry.blob,
                inputs=inputs,
            )
        )

    def execute_derivations(self) -> None:
        # State documents first, in dependency order.
        rule = self.rule_by_id("DERIVE-PROJECT")
        project, inputs, notes = self.build_project_state(rule)
        self.add_derived_json(rule, project, inputs, notes)

        rule = self.rule_by_id("DERIVE-WORK-PACKETS")
        value, inputs = self.build_work_packets_state(rule)
        self.add_derived_json(rule, value, inputs)

        rule = self.rule_by_id("DERIVE-MILESTONES")
        value, inputs = self.build_milestones_state(rule)
        self.add_derived_json(rule, value, inputs)

        rule = self.rule_by_id("DERIVE-RISKS")
        value, inputs = self.build_risks_state(rule)
        self.add_derived_json(rule, value, inputs)

        rule = self.rule_by_id("DERIVE-VERIFICATION")
        value, inputs = self.build_verification_state(rule)
        self.add_derived_json(rule, value, inputs)

        rule = self.rule_by_id("DERIVE-ROADMAP-STATE")
        value, inputs = self.build_roadmap_state(rule)
        self.add_derived_json(rule, value, inputs)

        rule = self.rule_by_id("DERIVE-RELEASES")
        value, inputs, notes = self.build_releases_state(rule)
        self.add_derived_json(rule, value, inputs, notes)

        rule = self.rule_by_id("DERIVE-ARTIFACT-INDEX")
        value, inputs = self.build_artifacts_state(rule)
        self.add_derived_json(rule, value, inputs)

        rule = self.rule_by_id("DERIVE-RESEARCH")
        value, inputs = self.build_research_state(rule)
        self.add_derived_json(rule, value, inputs)

        rule = self.rule_by_id("DERIVE-EVOLUTION")
        value, inputs, notes = self.build_evolution_state(rule)
        self.add_derived_json(rule, value, inputs, notes)

        # Human-readable derived pages consume the state above.
        page_renderers = {
            "DERIVE-SYSTEM-OVERVIEW": self.render_system_overview,
            "DERIVE-PROJECT-INDEX": self.render_project_index,
            "DERIVE-PROJECT-NOW": self.render_project_now,
            "DERIVE-PROJECT-STATUS": self.render_project_status,
            "DERIVE-ROADMAP-PAGE": self.render_roadmap_page,
            "DERIVE-WORK-PACKETS-INDEX": self.render_work_packet_index,
            "DERIVE-RISKS-INDEX": self.render_risk_index,
            "DERIVE-RELEASES-PAGE": self.render_releases_page,
        }
        for rule_id, renderer in page_renderers.items():
            rule = self.rule_by_id(rule_id)
            self.add_derived_page(rule, renderer(), self.rule_inputs(rule))

    def manifest_and_provenance(self) -> tuple[dict[str, Any], dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []
        records: list[dict[str, Any]] = []
        for destination in sorted(self.outputs):
            record = self.outputs[destination]
            artifact: dict[str, Any] = {
                "sourcePath": record.source_path,
                "sourceBlob": record.source_blob,
                "sourceCommit": self.snapshot.commit,
                "destinationPath": destination,
                "mode": record.mode,
                "contentHash": sha256(record.content),
                "policyRuleId": record.policy_rule_id,
            }
            if record.mode == "DERIVE":
                artifact["inputs"] = [
                    {"path": entry.path, "blob": entry.blob} for entry in unique_entries(record.inputs)
                ]
            artifacts.append(artifact)
            provenance: dict[str, Any] = {
                "destinationPath": destination,
                "mode": record.mode,
                "policyRuleId": record.policy_rule_id,
                "inputs": [
                    {"path": entry.path, "blob": entry.blob} for entry in unique_entries(record.inputs)
                ],
                "sourceStatus": record.source_status,
                "notes": record.notes,
            }
            records.append(provenance)
        manifest = {
            "projectionVersion": 1,
            "sourceRepository": "monad-framework/monad",
            "sourceBranch": "main",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "artifacts": artifacts,
        }
        provenance = {
            "projectionVersion": 1,
            "sourceRepository": "monad-framework/monad",
            "sourceBranch": "main",
            "sourceCommit": self.snapshot.commit,
            "generatedAt": self.generated_at,
            "records": records,
        }
        validate_json(manifest, self.schemas["manifest"], self.validator_cls, self.format_checker, "manifest.json")
        validate_json(provenance, self.schemas["provenance"], self.validator_cls, self.format_checker, "provenance.json")
        return manifest, provenance

    def build(self) -> dict[str, bytes]:
        plans = self.plan_mirrors()
        self.execute_mirrors(plans)
        self.execute_derivations()
        manifest, provenance = self.manifest_and_provenance()
        result = {destination: record.content for destination, record in self.outputs.items()}
        # The manifest and provenance files are projection metadata envelopes and
        # intentionally do not self-inventory; doing so would create a content-hash cycle.
        result[self.policy["generated_state"]["manifest"]] = json_bytes(manifest)
        result[self.policy["generated_state"]["provenance"]] = json_bytes(provenance)
        return dict(sorted(result.items()))


def unique_entries(entries: Iterable[TreeEntry]) -> list[TreeEntry]:
    values: dict[str, TreeEntry] = {}
    for entry in entries:
        values[entry.path] = entry
    return [values[path] for path in sorted(values)]


def safe_prepare_output(root: Path, output: Path, clean: bool) -> Path:
    resolved = output if output.is_absolute() else root / output
    resolved = resolved.resolve()
    root = root.resolve()
    if resolved == root or resolved == root.parent or resolved == Path(resolved.anchor):
        raise ExportError(f"refusing unsafe output directory: {resolved}")
    if resolved.exists():
        if not clean:
            raise ExportError(f"output already exists; pass --clean to replace it: {resolved}")
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True, exist_ok=False)
    return resolved


def write_tree(output: Path, files: dict[str, bytes]) -> None:
    for relative, content in files.items():
        destination = output / normalize_relative(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)


def tree_digest(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        result[path.relative_to(root).as_posix()] = sha256(path.read_bytes())
    return result


def verify_determinism(exporter_factory, root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="monad-publication-a-") as a_dir, tempfile.TemporaryDirectory(prefix="monad-publication-b-") as b_dir:
        a = Path(a_dir)
        b = Path(b_dir)
        write_tree(a, exporter_factory().build())
        write_tree(b, exporter_factory().build())
        a_digest = tree_digest(a)
        b_digest = tree_digest(b)
        if a_digest != b_digest:
            all_paths = sorted(set(a_digest) | set(b_digest))
            mismatches = [path for path in all_paths if a_digest.get(path) != b_digest.get(path)]
            raise ExportError("determinism verification failed for: " + ", ".join(mismatches[:20]))


def main() -> int:
    args = parse_args()
    yaml_module, validator_cls, format_checker_cls, schema_error_cls = load_dependencies()
    root = repository_root(args)
    try:
        snapshot = GitSnapshot(root, args.ref)
        if not snapshot.is_on_main():
            print(
                f"ERROR: source revision {snapshot.commit} is not reachable from local main/origin/main; "
                "current publication exports must come from main.",
                file=sys.stderr,
            )
            return EXIT_NOT_MAIN

        def factory() -> Exporter:
            return Exporter(
                root,
                snapshot,
                yaml_module,
                validator_cls,
                format_checker_cls,
                schema_error_cls,
                args.quiet,
            )

        if args.verify_determinism:
            verify_determinism(factory, root)
            if not args.quiet:
                print(f"PASS determinism {snapshot.commit}")

        exporter = factory()
        files = exporter.build()
        output = safe_prepare_output(root, args.output, args.clean)
        write_tree(output, files)
        if not args.quiet:
            print(f"PASS source      {snapshot.commit}")
            print(f"PASS generated   {len(files)} files")
            print(f"PASS output      {output}")
        print("Publication export: PASS")
        return EXIT_OK
    except ExportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_OUTPUT


if __name__ == "__main__":
    raise SystemExit(main())
