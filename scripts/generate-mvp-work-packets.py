#!/usr/bin/env python3
"""Generate the forecast MVP Work Packet records from the approved backlog map."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

MARKER = "<!-- mvp-work-packet-forecast:v1 -->"

@dataclass(frozen=True)
class Packet:
    number: int
    title: str
    cycle: str
    epic: str
    stories: tuple[str, ...]

PACKETS = [
    Packet(1,"Repository identity and configuration","WC-0001","EPIC-002",("US-002 detect repository root","US-003 resolve configuration precedence","US-004 explain effective configuration")),
    Packet(2,"Workspace discovery","WC-0001","EPIC-002",("US-005 discover supported workspace structure","US-006 guarantee stable discovery ordering","US-007 diagnose unsupported workspace structure")),
    Packet(3,"Stable source and document identity","WC-0001","EPIC-003",("US-008 assign stable source identifiers","US-009 preserve source hashes and provenance","US-010 diagnose identity collisions")),
    Packet(4,"Markdown engineering artifact parser","WC-0002","EPIC-003",("US-011 parse sections and metadata","US-012 extract stable identifiers","US-013 extract links and references","US-014 diagnose malformed Markdown")),
    Packet(5,"Structured configuration parser","WC-0002","EPIC-003",("US-015 parse Monad configuration","US-016 report schema errors","US-017 normalize configuration deterministically")),
    Packet(6,"Reference resolution","WC-0002","EPIC-003",("US-018 resolve local artifact references","US-019 retain unresolved references explicitly","US-020 emit typed relation candidates")),
    Packet(7,"Semantic graph ontology","WC-0003","EPIC-004",("US-021 define MVP node types","US-022 define MVP edge types","US-023 define graph invariants")),
    Packet(8,"Semantic graph construction","WC-0003","EPIC-004",("US-024 build graph from normalized knowledge","US-025 guarantee deterministic ordering","US-026 handle duplicates and conflicts")),
    Packet(9,"Graph provenance and integrity","WC-0003","EPIC-004",("US-027 attach source provenance","US-028 attach relationship-rule provenance","US-029 validate graph integrity")),
    Packet(10,"KIR schema and canonicalization","WC-0004","EPIC-005",("US-030 define MVP KIR schema","US-031 canonicalize serialization","US-032 expose KIR version","US-033 validate KIR")),
    Packet(11,"Diagnostic contract","WC-0004","EPIC-006",("US-034 define stable diagnostic identifiers","US-035 carry severity location and entity","US-036 support human and structured forms")),
    Packet(12,"Semantic validation engine","WC-0004","EPIC-006",("US-037 evaluate validation rules","US-038 validate authority and references","US-039 emit deterministic findings")),
    Packet(13,"Graph query engine","WC-0005","EPIC-007",("US-040 query references and dependents","US-041 query governing artifacts","US-042 query traceability gaps")),
    Packet(14,"Explain relationship paths","WC-0005","EPIC-007",("US-043 explain why an entity exists","US-044 explain governing paths","US-045 distinguish missing knowledge from negative answers")),
    Packet(15,"Work Packet semantic contract","WC-0006","EPIC-008",("US-046 parse canonical Work Packets","US-047 validate authority and scope","US-048 identify acceptance and validation commands")),
    Packet(16,"Minimal agent-context selection","WC-0006","EPIC-008",("US-049 select graph neighborhood","US-050 enforce exclusion rules","US-051 explain selection membership")),
    Packet(17,"Agent context package","WC-0006","EPIC-008",("US-052 serialize deterministic context package","US-053 provide Codex profile","US-054 minimize secrets and irrelevant data","US-055 retain context provenance")),
    Packet(18,"MVP CLI command surface","WC-0007","EPIC-009",("US-056 implement inspect","US-057 implement validate","US-058 implement graph and query","US-059 implement explain","US-060 implement context")),
    Packet(19,"CLI output and error contract","WC-0007","EPIC-009",("US-061 define exit codes","US-062 define structured output","US-063 support no-color and CI-safe output")),
    Packet(20,"Doctor completion and onboarding","WC-0007","EPIC-009",("US-064 implement doctor","US-065 provide shell completion","US-066 provide actionable first-run help")),
    Packet(21,"Determinism conformance suite","WC-0008","EPIC-010",("US-067 establish golden fixtures","US-068 prove cross-run equivalence","US-069 add ordering and property tests")),
    Packet(22,"Untrusted repository hardening","WC-0008","EPIC-010",("US-070 defend paths and symlinks","US-071 prevent implicit execution","US-072 enforce secret and context exclusions")),
    Packet(23,"Performance baseline","WC-0008","EPIC-010",("US-073 establish reference repositories","US-074 measure latency and memory","US-075 define regression budgets")),
    Packet(24,"Native validation adapter","WC-0009","EPIC-011",("US-076 define validation capability contract","US-077 preserve invocation evidence","US-078 preserve native tool results")),
    Packet(25,"Semantic diff and impact baseline","WC-0009","EPIC-011",("US-079 diff semantic graph state","US-080 identify affected entities","US-081 recommend validation scope")),
    Packet(26,"Monad self-inspection","WC-0010","EPIC-012",("US-082 compile the Monad repository","US-083 resolve dogfood diagnostics","US-084 publish dogfood evidence")),
    Packet(27,"GitHub engineering projection","WC-0010","EPIC-012",("US-085 trace Issues to Work Packets","US-086 emit PR semantic-summary baseline","US-087 define project-status projection rules")),
    Packet(28,"Installation and packaging","WC-0011","EPIC-013",("US-088 provide supported installation","US-089 expose version identity","US-090 publish checksummed artifacts")),
    Packet(29,"User and reference documentation","WC-0011","EPIC-013",("US-091 publish quickstart","US-092 publish CLI reference","US-093 publish concepts and troubleshooting")),
    Packet(30,"Release provenance","WC-0011","EPIC-013",("US-094 produce source-artifact manifest","US-095 produce SBOM baseline","US-096 produce reproducible release evidence")),
    Packet(31,"End-to-end MVP acceptance","WC-0012","EPIC-014",("US-097 pass clean-clone journey","US-098 pass agent-context journey","US-099 pass negative and recovery journey")),
    Packet(32,"Security and release readiness","WC-0012","EPIC-014",("US-100 assemble threat and control evidence","US-101 dispose open release risks","US-102 complete release-readiness checklist")),
    Packet(33,"Release candidate and MVP release","WC-0012","EPIC-014",("US-103 validate release candidate","US-104 record Product Goal acceptance","US-105 cut release tag and notes")),
]


def render(packet: Packet) -> str:
    pid = f"WP-MVP-{packet.number:04d}"
    acceptance = "\n".join(f"- [ ] {story}." for story in packet.stories)
    return f"""{MARKER}
# {pid} — {packet.title}

**Status:** Planned  
**Epic:** {packet.epic}  
**Work Cycle / Sprint:** {packet.cycle}  
**Product Goal:** PG-001  
**Target:** MVP Release 1

## Objective

Deliver **{packet.title.lower()}** as one independently reviewable vertical engineering outcome that advances PG-001 without expanding beyond the MVP boundary.

## Context

This packet is forecast in `product/backlog/MVP-BACKLOG.md`. It becomes **Ready** only after its required governing ADRs/specifications are accepted or explicitly identified as not required, upstream packet dependencies have passing evidence, and task-level implementation scope can be bounded without guessing.

## Scope

### In scope

- behavior necessary to satisfy the linked stories/enablers;
- deterministic positive, negative, boundary, and failure behavior;
- diagnostics, provenance, documentation, and tests required by the Definition of Done;
- compatibility/security implications introduced by this packet.

### Out of scope

- unrelated refactoring;
- post-MVP generalization not required by PG-001;
- silent changes to accepted architecture/specification authority;
- introducing hosted, remote, or agent autonomy dependencies unless explicitly authorized.

## Governing artifacts

Before activation, replace unresolved entries with concrete links:

- Product Goal: `product/PRODUCT-GOAL.md`
- MVP contract: `product/MVP-RELEASE-1.md`
- Product requirements: `product/product-requirements.md`
- Architecture: `architecture/overview.md`
- Required ADR(s): **TBD during refinement**
- Required specification(s): **TBD during refinement**

## Dependencies

Dependencies are the accepted outputs of earlier packets on the critical path plus any explicit native-tool/schema contracts discovered during refinement. A packet MUST NOT become Ready while a dependency capable of changing its public semantic contract remains unresolved.

## Acceptance criteria

{acceptance}
- [ ] Required negative and boundary behavior is verified.
- [ ] Deterministic output/order/identity requirements relevant to this packet pass.
- [ ] Diagnostics and provenance are sufficient to explain failure and derived state.
- [ ] No new unaccepted critical/high security or correctness risk remains.
- [ ] Canonical documentation and machine projection are synchronized.

## Implementation constraints

1. Core semantic truth must not depend on LLM output.
2. Canonical repository inspection must not execute untrusted project code implicitly.
3. Stable public identifiers/schemas require explicit compatibility treatment.
4. Native tool results remain authoritative for native semantics.
5. Agent execution scope cannot exceed this Work Packet or its governing authority.
6. Generated state must be rebuildable or explicitly treated as external evidence.

## Validation

Refinement MUST identify exact commands/tests before authorization. Expected evidence includes focused unit tests, conformance/golden/property tests where semantics are canonical, integration tests across the affected boundary, machine-document synchronization, and end-to-end evidence when the packet changes a user-visible journey.

## Risks

Primary risks are semantic ambiguity, accidental coupling to future architecture, nondeterminism, insufficient provenance, and over-broad MVP scope. Any discovered risk that changes the governing contract triggers refinement or escalation rather than being hidden in implementation.

## Completion evidence

Populate with branch/commit, PR, test commands/results, semantic/architecture review, generated artifacts, and closure disposition. Merge alone is not completion.

## Refinement state

This forecast packet is intentionally not Ready merely because it has been generated. Remove `{MARKER}` when the packet has been manually refined and authorized; the generator will then stop owning its contents.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    target = root / "engineering" / "work-packets"
    target.mkdir(parents=True, exist_ok=True)
    drift = []
    for packet in PACKETS:
        path = target / f"WP-MVP-{packet.number:04d}.md"
        expected = render(packet)
        if path.exists():
            current = path.read_text(encoding="utf-8")
            if MARKER not in current:
                continue
            if current == expected:
                continue
        if args.check:
            drift.append(path.relative_to(root).as_posix())
        else:
            path.write_text(expected, encoding="utf-8")
    if drift:
        print("MVP Work Packet forecast requires regeneration:")
        for item in drift:
            print(f"  {item}")
        return 1
    print(f"MVP Work Packet forecast verified: {len(PACKETS)} packets.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
