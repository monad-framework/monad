#!/usr/bin/env python3
from __future__ import annotations

import re

REQUIREMENT_FAMILIES = ("REQ", "FR", "QR")

SPECIFICATION_FAMILIES = (
    "SPEC",
    "FUN",
    "IFC",
    "SEC",
    "TECH",
    "DATA",
    "MKE",
)

REQUIREMENT_ID_PATTERN = (
    r"(?:REQ|FR|QR)-[A-Z0-9][A-Z0-9-]*"
)

SPECIFICATION_ID_PATTERN = (
    r"(?:SPEC|FUN|IFC|SEC|TECH|DATA|MKE)-"
    r"[A-Z0-9][A-Z0-9-]*"
)

REQUIREMENT_ID_RE = re.compile(
    rf"^{REQUIREMENT_ID_PATTERN}$"
)

SPECIFICATION_ID_RE = re.compile(
    rf"^{SPECIFICATION_ID_PATTERN}$"
)


def is_requirement_id(value: str) -> bool:
    return REQUIREMENT_ID_RE.fullmatch(value) is not None


def is_specification_id(value: str) -> bool:
    return SPECIFICATION_ID_RE.fullmatch(value) is not None


def is_requirement_or_specification_id(value: str) -> bool:
    return is_requirement_id(value) or is_specification_id(value)
