#!/usr/bin/env python3
"""Validate Monad publication policy, schemas, and contract fixtures."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXIT_OK = 0
EXIT_DEPENDENCY = 2
EXIT_SCHEMA = 3
EXIT_VALID_INSTANCE = 4
EXIT_INVALID_INSTANCE = 5
EXIT_IO = 6


@dataclass(frozen=True)
class Paths:
    root: Path
    policy: Path
    schema_dir: Path
    valid_dir: Path
    invalid_dir: Path


SCHEMAS = {
    "projection": "projection.schema.json",
    "manifest": "manifest.schema.json",
    "provenance": "provenance.schema.json",
    "site-state": "site-state.schema.json",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the Monad website publication policy, publication JSON Schemas, "
            "and positive/negative contract fixtures."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root; defaults to the parent of scripts/",
    )
    parser.add_argument(
        "--policy-only",
        action="store_true",
        help="validate schemas and publication/website/projection.yaml only",
    )
    parser.add_argument(
        "--fixtures-only",
        action="store_true",
        help="validate schemas and fixtures only; skip projection.yaml",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="print only errors and the final result",
    )
    return parser.parse_args()


def load_dependencies():
    try:
        import yaml  # type: ignore
        from jsonschema import Draft202012Validator, FormatChecker
        from jsonschema.exceptions import SchemaError, best_match
    except ImportError as exc:
        print(
            "ERROR: publication validation dependencies are missing.\n"
            "Create/activate .venv and run:\n"
            "  python3 -m pip install -r scripts/requirements/publication-validation.txt\n"
            f"Underlying import error: {exc}",
            file=sys.stderr,
        )
        raise SystemExit(EXIT_DEPENDENCY) from exc
    return yaml, Draft202012Validator, FormatChecker, SchemaError, best_match


def repository_paths(args: argparse.Namespace) -> Paths:
    if args.root is None:
        root = Path(__file__).resolve().parent.parent
    else:
        root = args.root.resolve()
    return Paths(
        root=root,
        policy=root / "publication/website/projection.yaml",
        schema_dir=root / "schemas/publication",
        valid_dir=root / "tests/publication/fixtures/valid",
        invalid_dir=root / "tests/publication/fixtures/invalid",
    )


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read JSON {path}: {exc}") from exc


def read_yaml(path: Path, yaml_module) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml_module.safe_load(handle)
    except (OSError, yaml_module.YAMLError) as exc:
        raise RuntimeError(f"cannot read YAML {path}: {exc}") from exc


def schema_key_for_fixture(path: Path) -> str:
    name = path.name
    if name.startswith("projection-") and path.suffix in {".yaml", ".yml"}:
        return "projection"
    if name.startswith("manifest-") and path.suffix == ".json":
        return "manifest"
    if name.startswith("provenance-") and path.suffix == ".json":
        return "provenance"
    if name.startswith("site-state-") and path.suffix == ".json":
        return "site-state"
    raise RuntimeError(f"fixture name does not identify a schema: {path}")


def instance_for_fixture(path: Path, yaml_module) -> Any:
    if path.suffix == ".json":
        return read_json(path)
    if path.suffix in {".yaml", ".yml"}:
        return read_yaml(path, yaml_module)
    raise RuntimeError(f"unsupported fixture type: {path}")


def format_error(error, best_match) -> str:
    chosen = best_match([error]) or error
    path = "$"
    if chosen.absolute_path:
        path += "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}"
            for part in chosen.absolute_path
        )
    return f"{path}: {chosen.message}"


def first_error(validator, instance, best_match):
    errors = list(validator.iter_errors(instance))
    if not errors:
        return None
    return best_match(errors) or errors[0]


def load_and_check_schemas(paths: Paths, Draft202012Validator, SchemaError, quiet: bool):
    schemas: dict[str, Any] = {}
    validators: dict[str, Any] = {}

    for key, filename in SCHEMAS.items():
        path = paths.schema_dir / filename
        if not path.is_file():
            print(f"ERROR: required schema is missing: {path}", file=sys.stderr)
            raise SystemExit(EXIT_IO)
        schema = read_json(path)
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            print(f"ERROR: invalid JSON Schema {path}: {exc.message}", file=sys.stderr)
            raise SystemExit(EXIT_SCHEMA) from exc
        schemas[key] = schema
        validators[key] = Draft202012Validator(schema)
        if not quiet:
            print(f"PASS schema     {path.relative_to(paths.root)}")

    return schemas, validators


def validate_policy(paths: Paths, validators, yaml_module, FormatChecker, best_match, quiet: bool):
    if not paths.policy.is_file():
        print(f"ERROR: publication policy is missing: {paths.policy}", file=sys.stderr)
        raise SystemExit(EXIT_IO)

    instance = read_yaml(paths.policy, yaml_module)
    validator = validators["projection"].evolve(format_checker=FormatChecker())
    error = first_error(validator, instance, best_match)
    if error is not None:
        print(
            f"ERROR: policy does not conform to projection.schema.json: "
            f"{format_error(error, best_match)}",
            file=sys.stderr,
        )
        raise SystemExit(EXIT_VALID_INSTANCE)

    if not quiet:
        print(f"PASS policy     {paths.policy.relative_to(paths.root)}")

    # Boundary mutations prove that critical schema constraints reject drift.
    mutations = [
        (
            "non-main source branch",
            lambda p: p["projection"]["source"].__setitem__("branch", "feature/test"),
        ),
        (
            "non-deny default disposition",
            lambda p: p["defaults"].__setitem__("disposition", "MIRROR"),
        ),
    ]
    for label, mutate in mutations:
        candidate = copy.deepcopy(instance)
        mutate(candidate)
        error = first_error(validator, candidate, best_match)
        if error is None:
            print(
                f"ERROR: projection schema unexpectedly accepted boundary mutation: {label}",
                file=sys.stderr,
            )
            raise SystemExit(EXIT_INVALID_INSTANCE)
        if not quiet:
            print(f"PASS reject     projection boundary: {label}")


def iter_fixtures(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise RuntimeError(f"fixture directory is missing: {directory}")
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix in {".json", ".yaml", ".yml"}
    )


def validate_fixtures(paths: Paths, validators, yaml_module, FormatChecker, best_match, quiet: bool):
    valid = iter_fixtures(paths.valid_dir)
    invalid = iter_fixtures(paths.invalid_dir)

    if not valid:
        raise RuntimeError(f"no positive fixtures found in {paths.valid_dir}")
    if not invalid:
        raise RuntimeError(f"no negative fixtures found in {paths.invalid_dir}")

    format_checker = FormatChecker()

    for path in valid:
        key = schema_key_for_fixture(path)
        validator = validators[key].evolve(format_checker=format_checker)
        instance = instance_for_fixture(path, yaml_module)
        error = first_error(validator, instance, best_match)
        if error is not None:
            print(
                f"ERROR: positive fixture failed [{key}] {path.relative_to(paths.root)}: "
                f"{format_error(error, best_match)}",
                file=sys.stderr,
            )
            raise SystemExit(EXIT_VALID_INSTANCE)
        if not quiet:
            print(f"PASS fixture    {path.relative_to(paths.root)}")

    for path in invalid:
        key = schema_key_for_fixture(path)
        validator = validators[key].evolve(format_checker=format_checker)
        instance = instance_for_fixture(path, yaml_module)
        error = first_error(validator, instance, best_match)
        if error is None:
            print(
                f"ERROR: negative fixture unexpectedly validated [{key}] "
                f"{path.relative_to(paths.root)}",
                file=sys.stderr,
            )
            raise SystemExit(EXIT_INVALID_INSTANCE)
        if not quiet:
            print(f"PASS reject     {path.relative_to(paths.root)}")


def main() -> int:
    args = parse_args()
    if args.policy_only and args.fixtures_only:
        print("ERROR: --policy-only and --fixtures-only are mutually exclusive", file=sys.stderr)
        return EXIT_DEPENDENCY

    yaml_module, Draft202012Validator, FormatChecker, SchemaError, best_match = load_dependencies()
    paths = repository_paths(args)

    try:
        _, validators = load_and_check_schemas(
            paths, Draft202012Validator, SchemaError, args.quiet
        )
        if not args.fixtures_only:
            validate_policy(
                paths,
                validators,
                yaml_module,
                FormatChecker,
                best_match,
                args.quiet,
            )
        if not args.policy_only:
            validate_fixtures(
                paths,
                validators,
                yaml_module,
                FormatChecker,
                best_match,
                args.quiet,
            )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_IO

    print("Publication validation: PASS")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
