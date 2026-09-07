import { afterEach, describe, expect, test } from "bun:test";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { readExecutionProjection } from "./execution";

const roots: string[] = [];

async function fixtureRoot(): Promise<string> {
  const root = await mkdtemp(
    path.join(os.tmpdir(), "monad-workbench-execution-"),
  );
  roots.push(root);

  const eos = path.join(root, ".eos");
  await mkdir(path.join(eos, "state"), { recursive: true });

  await writeFile(
    path.join(eos, "program-increments.tsv"),
    "id\tpath\ttitle\tstatus\tcreated\tupdated\nPI-MVP-001\tengineering/increments/PI-MVP-001.md\tSemantic Foundation\tACTIVE\t2026-01-01T00:00:00Z\t2026-01-02T00:00:00Z\n",
    "utf8",
  );

  await writeFile(
    path.join(eos, "work-cycles.tsv"),
    "id\tpath\ttitle\tstatus\tpi\tcreated\tupdated\nWC-MVP-0002\tengineering/work-cycles/WC-MVP-0002.md\tParsing and Reference Resolution\tACTIVE\tPI-MVP-001\t2026-01-01T00:00:00Z\t2026-01-02T00:00:00Z\n",
    "utf8",
  );

  await writeFile(
    path.join(eos, "work-packets.tsv"),
    "id\tpath\ttitle\tstatus\tpi\twc\tdomain\tcreated\tupdated\nWP-MVP-0005\tengineering/work-packets/WP-MVP-0005.md\tStructured Monad configuration parser\tIN_PROGRESS\tPI-MVP-001\tWC-MVP-0002\tCORE\t2026-01-01T00:00:00Z\t2026-01-02T00:00:00Z\n",
    "utf8",
  );

  await writeFile(
    path.join(eos, "executions.tsv"),
    "id\tpath\ttarget\tstatus\tbranch\tactor\tcreated\tupdated\nEXEC-0010\t.eos/executions/EXEC-0010.json\tWP-MVP-0005\tCLOSED\twp/mvp-0005\tchatgpt\t2026-01-01T00:00:00Z\t2026-01-01T01:00:00Z\n",
    "utf8",
  );

  await writeFile(
    path.join(eos, "evidence.tsv"),
    "id\ttarget\tstatus\tresult\nEVID-001\tWP-MVP-0005\tCURRENT\tPASSED\nEVID-002\tWP-MVP-0005\tSUPERSEDED\tFAILED\nEVID-003\tWP-MVP-0005\tCURRENT\tSKIPPED\n",
    "utf8",
  );

  await writeFile(path.join(eos, "state", "current.json"), "{}\n", "utf8");

  return root;
}

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { recursive: true, force: true })),
  );
});

describe("readExecutionProjection", () => {
  test("builds the governed execution hierarchy from EOS registries", async () => {
    const root = await fixtureRoot();
    const projection = await readExecutionProjection(root);

    expect(projection.counts).toEqual({
      programIncrements: 1,
      workCycles: 1,
      workPackets: 1,
      executions: 1,
      evidence: 3,
      lifecycleDrift: 0,
    });

    const program = projection.programIncrements[0];
    const cycle = program?.workCycles[0];
    const packet = cycle?.workPackets[0];

    expect(program?.id).toBe("PI-MVP-001");
    expect(cycle?.id).toBe("WC-MVP-0002");
    expect(packet?.id).toBe("WP-MVP-0005");
    expect(packet?.status).toBe("IN_PROGRESS");
    expect(packet?.executions[0]?.id).toBe("EXEC-0010");
    expect(packet?.executions[0]?.actor).toBe("chatgpt");
  });

  test("distinguishes current evidence from superseded evidence", async () => {
    const root = await fixtureRoot();
    const projection = await readExecutionProjection(root);
    const packet =
      projection.programIncrements[0]?.workCycles[0]?.workPackets[0];

    expect(packet?.evidence).toEqual({
      total: 3,
      passed: 1,
      failed: 1,
      skipped: 1,
      current: 2,
    });
  });

  test("overlays canonical lifecycle state and exposes registry drift", async () => {
    const root = await fixtureRoot();

    await writeFile(
      path.join(root, ".eos", "state", "current.json"),
      JSON.stringify({
        entities: {
          WP: {
            "WP-MVP-0005": {
              id: "WP-MVP-0005",
              lifecycle_state: "CLOSED",
            },
          },
        },
      }),
      "utf8",
    );

    const projection = await readExecutionProjection(root);
    const packet =
      projection.programIncrements[0]?.workCycles[0]?.workPackets[0];

    expect(packet?.status).toBe("CLOSED");
    expect(packet?.registryStatus).toBe("IN_PROGRESS");
    expect(projection.counts.lifecycleDrift).toBe(1);
  });
});
