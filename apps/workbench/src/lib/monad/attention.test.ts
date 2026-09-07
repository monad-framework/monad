import { describe, expect, test } from "bun:test";
import { type AttentionEvidenceRow, projectAttention } from "./attention";
import type { ControlProjection } from "./control";
import type { ExecutionProjection } from "./execution";

function executionProjection(): ExecutionProjection {
  return {
    programIncrements: [
      {
        id: "PI-TEST-001",
        path: "engineering/increments/PI-TEST-001.md",
        title: "Test increment",
        status: "ACTIVE",
        created: "2026-09-01T00:00:00Z",
        updated: "2026-09-07T10:00:00Z",
        workCycles: [
          {
            id: "WC-TEST-001",
            path: "engineering/work-cycles/WC-TEST-001.md",
            title: "Test cycle",
            status: "ACTIVE",
            pi: "PI-TEST-001",
            created: "2026-09-01T00:00:00Z",
            updated: "2026-09-07T10:00:00Z",
            workPackets: [
              {
                id: "WP-TEST-001",
                path: "engineering/work-packets/WP-TEST-001.md",
                title: "Attention fixture",
                status: "IN_PROGRESS",
                registryStatus: "READY",
                pi: "PI-TEST-001",
                wc: "WC-TEST-001",
                domain: "CORE",
                created: "2026-09-01T00:00:00Z",
                updated: "2026-09-07T10:00:00Z",
                executions: [
                  {
                    id: "EXEC-TEST-001",
                    path: ".eos/executions/EXEC-TEST-001.json",
                    target: "WP-TEST-001",
                    status: "CLOSED",
                    branch: "wp/test-001",
                    actor: "chatgpt",
                    created: "2026-09-07T09:00:00Z",
                    updated: "2026-09-07T09:30:00Z",
                  },
                ],
                evidence: {
                  total: 0,
                  passed: 0,
                  failed: 0,
                  skipped: 0,
                  current: 0,
                },
              },
            ],
          },
        ],
      },
    ],
    counts: {
      programIncrements: 1,
      workCycles: 1,
      workPackets: 1,
      executions: 1,
      evidence: 0,
      lifecycleDrift: 1,
    },
    sources: [
      ".eos/program-increments.tsv",
      ".eos/work-cycles.tsv",
      ".eos/work-packets.tsv",
      ".eos/executions.tsv",
      ".eos/evidence.tsv",
      ".eos/state/current.json",
    ],
  };
}

function controlProjection(): ControlProjection {
  return {
    changes: [],
    decisions: [],
    risks: [],
    reviews: [],
    releases: [],
    verification: {
      total: 0,
      current: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
    },
    findings: [],
    sources: [".eos/state/current.json"],
  };
}

function evidence(
  overrides: Partial<AttentionEvidenceRow>,
): AttentionEvidenceRow {
  return {
    id: "EVID-TEST-001",
    path: "engineering/evidence/EVID-TEST-001.md",
    target: "WP-TEST-001",
    execution: "EXEC-TEST-001",
    validator: "repository",
    kind: "repository",
    status: "CURRENT",
    result: "PASSED",
    created: "2026-09-07T09:31:00Z",
    updated: "2026-09-07T09:31:00Z",
    ...overrides,
  };
}

describe("Attention projection", () => {
  test("surfaces canonical lifecycle drift and derives reconciliation work", async () => {
    const projection = await projectAttention({
      root: "/fixture",
      execution: executionProjection(),
      control: controlProjection(),
      evidence: [],
    });

    const drift = projection.conditions.find(
      (condition) => condition.state === "DRIFTED",
    );

    expect(drift?.affectedObject.id).toBe("WP-TEST-001");
    expect(drift?.classification).toBe("attention");
    expect(drift?.reason).toContain("canonical EOS current state");
    expect(projection.workstreams).toHaveLength(1);
    expect(projection.workstreams[0]?.state).toBe("RECONCILING");
    expect(projection.workstreams[0]?.authorization).toBe("GRANTED");
  });

  test("deduplicates repeated failed evidence observations by target and validator", async () => {
    const projection = await projectAttention({
      root: "/fixture",
      execution: executionProjection(),
      control: controlProjection(),
      evidence: [
        evidence({
          id: "EVID-TEST-002",
          result: "FAILED",
          updated: "2026-09-07T09:32:00Z",
        }),
        evidence({
          id: "EVID-TEST-003",
          result: "FAILED",
          updated: "2026-09-07T09:33:00Z",
        }),
      ],
    });

    const failures = projection.conditions.filter(
      (condition) =>
        condition.state === "FAILED" &&
        condition.provenance.provider === "eos-evidence",
    );

    expect(failures).toHaveLength(1);
    expect(failures[0]?.classification).toBe("operator-action");
    expect(failures[0]?.reason).toContain("EVID-TEST-003");
  });

  test("does not keep an older failure active after newer current evidence passes", async () => {
    const projection = await projectAttention({
      root: "/fixture",
      execution: executionProjection(),
      control: controlProjection(),
      evidence: [
        evidence({
          id: "EVID-TEST-004",
          result: "FAILED",
          updated: "2026-09-07T09:32:00Z",
        }),
        evidence({
          id: "EVID-TEST-005",
          result: "PASSED",
          updated: "2026-09-07T09:34:00Z",
        }),
      ],
    });

    expect(
      projection.conditions.some(
        (condition) =>
          condition.state === "FAILED" &&
          condition.provenance.provider === "eos-evidence",
      ),
    ).toBe(false);
  });

  test("classifies blocked executions as operator action required", async () => {
    const execution = executionProjection();
    const packet =
      execution.programIncrements[0]?.workCycles[0]?.workPackets[0];
    if (!packet) throw new Error("fixture packet missing");

    packet.executions = [
      {
        id: "EXEC-TEST-BLOCKED",
        path: ".eos/executions/EXEC-TEST-BLOCKED.json",
        target: packet.id,
        status: "BLOCKED",
        branch: "wp/test-blocked",
        actor: "chatgpt",
        created: "2026-09-07T10:00:00Z",
        updated: "2026-09-07T10:05:00Z",
      },
    ];

    const projection = await projectAttention({
      root: "/fixture",
      execution,
      control: controlProjection(),
      evidence: [],
    });

    const blocked = projection.conditions.find(
      (condition) => condition.affectedObject.id === "EXEC-TEST-BLOCKED",
    );

    expect(blocked?.state).toBe("BLOCKED");
    expect(blocked?.classification).toBe("operator-action");
    expect(blocked?.severity).toBe("critical");
    expect(projection.summary.operatorAction).toBeGreaterThan(0);
  });

  test("turns control consistency findings into current drift attention", async () => {
    const control = controlProjection();
    control.findings = [
      {
        id: "CTRL-DRIFT-TEST",
        severity: "warning",
        title: "Projection mismatch",
        detail: "Canonical state and narrative differ.",
        canonicalSource: ".eos/state/current.json",
        comparedSource: "engineering/project-status.md",
      },
    ];

    const projection = await projectAttention({
      root: "/fixture",
      execution: executionProjection(),
      control,
      evidence: [],
    });

    expect(
      projection.conditions.some(
        (condition) =>
          condition.dedupeKey === "control-finding:CTRL-DRIFT-TEST" &&
          condition.state === "DRIFTED",
      ),
    ).toBe(true);
  });
});
