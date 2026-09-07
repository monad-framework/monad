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

# Product requirement families have established fixed numeric identities.
#
# Examples:
#   FR-043
#   QR-010
#
# Generic REQ identities retain compatibility with both:
#   REQ-0042
#   REQ-FOO-0001
#   REQ-AI-ENG-0001
#
# The final segment is therefore always the stable numeric identity rather
# than arbitrary trailing identifier text.
REQUIREMENT_ID_PATTERN = (
    r"(?:"
    r"(?:FR|QR)-\d{3}"
    r"|"
    r"REQ-(?:[A-Z0-9]+-)*\d{4}"
    r")"
)

# Specification identities follow:
#
#   <CLASS>-<AREA...>-NNNN
#
# Examples:
#   FUN-AIENG-0001
#   IFC-AIENG-0001
#   SEC-AIENG-0001
#   TECH-HARNESS-0001
#   DATA-SOURCE-0001
#   MKE-CORE-0001
#   SPEC-CORE-0001
#
# Requiring the terminal NNNN segment is important: identifiers such as
# FUN-AIENG-V01 are verification-scenario identifiers, not specifications.
SPECIFICATION_ID_PATTERN = (
    r"(?:SPEC|FUN|IFC|SEC|TECH|DATA|MKE)-"
    r"(?:[A-Z0-9]+-)*"
    r"\d{4}"
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
