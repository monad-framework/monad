import { afterEach, describe, expect, test } from "bun:test";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { readControlProjection } from "./control";

const roots: string[] = [];

async function fixtureRoot(): Promise<string> {
  const root = await mkdtemp(
    path.join(os.tmpdir(), "monad-workbench-control-"),
  );
  roots.push(root);

  await mkdir(path.join(root, ".eos", "state"), { recursive: true });
  await mkdir(path.join(root, "engineering", "risks"), { recursive: true });

  await writeFile(
    path.join(root, ".eos", "change-requests.tsv"),
    "id\tpath\ttarget\tsummary\tstatus\tcreated\tupdated\nCR-0001\tengineering/changes/CR-0001.md\tWP-MVP-0005\tUpdate packet\tAPPROVED\t2026-01-01T00:00:00Z\t2026-01-01T01:00:00Z\n",
    "utf8",
  );
  await writeFile(
    path.join(root, ".eos", "decisions.tsv"),
    "timestamp\ttarget\taction\toutcome\tactor\treason\n2026-01-01T00:00:00Z\tWP-MVP-0005\tAUTHORIZE\tAPPROVED\thuman\tready\n",
    "utf8",
  );
  await writeFile(
    path.join(root, ".eos", "artifacts.tsv"),
    "artifact_id\tpath\ttype\tauthority\nRISK-001\tengineering/risks/RISK-001.md\trisk\tL2\nREV-001\tengineering/reviews/REV-001.md\treview\tL2\n",
    "utf8",
  );
  await writeFile(
    path.join(root, ".eos", "releases.tsv"),
    "id\tpath\tversion\tstatus\tcreated\tupdated\nREL-001\treleases/REL-001.md\t0.1.0\tPLANNED\t2026-01-01T00:00:00Z\t2026-01-01T00:00:00Z\n",
    "utf8",
  );
  await writeFile(
    path.join(root, ".eos", "evidence.tsv"),
    "id\tstatus\tresult\nEVID-001\tCURRENT\tPASSED\nEVID-002\tSUPERSEDED\tFAILED\n",
    "utf8",
  );
  await writeFile(
    path.join(root, ".eos", "state", "current.json"),
    JSON.stringify({
      entities: {
        WP: {
          "WP-MVP-0005": {
            id: "WP-MVP-0005",
            lifecycle_state: "IN_PROGRESS",
          },
        },
      },
    }),
    "utf8",
  );
  await writeFile(
    path.join(root, "engineering", "project-status.md"),
    "# Project Status\n\n**Current packet:** WP-MVP-0005 — AUTHORIZED; start not yet executed\n",
    "utf8",
  );
  await writeFile(
    path.join(root, "engineering", "risks", "risk-register.md"),
    "# Risk Register\n\n## Active risks\n\n| ID | Risk | L | I | Exposure | Response and leading indicator | Owner | State |\n| --- | --- | ---: | ---: | ---: | --- | --- | --- |\n| R-001 | Canonical risk from register | 4 | 5 | 20 | Treat it | Owner | Treating |\n",
    "utf8",
  );

  return root;
}

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { recursive: true, force: true })),
  );
});

describe("readControlProjection", () => {
  test("uses .eos/state/current.json as lifecycle authority when narrative status is stale", async () => {
    const root = await fixtureRoot();
    const projection = await readControlProjection(root);

    expect(projection.findings).toHaveLength(1);
    expect(projection.findings[0]?.canonicalSource).toBe(
      ".eos/state/current.json",
    );
    expect(projection.findings[0]?.detail).toContain("IN_PROGRESS");
    expect(projection.findings[0]?.detail).toContain("AUTHORIZED");
  });

  test("summarizes evidence without treating superseded records as current", async () => {
    const root = await fixtureRoot();
    const projection = await readControlProjection(root);

    expect(projection.verification).toEqual({
      total: 2,
      current: 1,
      passed: 1,
      failed: 1,
      skipped: 0,
    });
  });

  test("loads active risks from the canonical risk register", async () => {
    const root = await fixtureRoot();
    const projection = await readControlProjection(root);
    const risk = projection.risks.find((item) => item.id === "R-001");

    expect(risk?.title).toBe("Canonical risk from register");
    expect(risk?.status).toBe("Treating");
    expect(risk?.path).toBe("engineering/risks/risk-register.md");
  });
});
