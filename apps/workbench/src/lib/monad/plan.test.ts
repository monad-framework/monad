import { afterEach, describe, expect, test } from "bun:test";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { readPlanProjection } from "./plan";

const roots: string[] = [];

async function fixtureRoot(): Promise<string> {
  const root = await mkdtemp(path.join(os.tmpdir(), "monad-workbench-plan-"));
  roots.push(root);

  await mkdir(path.join(root, "product", "backlog"), { recursive: true });

  await writeFile(
    path.join(root, "product", "initiatives.md"),
    `# Monad Initiative Catalog

# PG-001 — MVP Release 1

## INIT-001 — Establish Foundation

**Outcome:** Establish a coherent engineering foundation.

### Epics

- \`EPIC-001\` — Foundation Stabilization

### Exit condition

Foundation work is accepted.

## INIT-002 — Compile Knowledge

**Outcome:** Compile canonical engineering knowledge.

### Epics

- \`EPIC-002\` — Workspace & Configuration
- \`EPIC-003\` — Canonical Knowledge Ingestion

### Exit condition

Canonical knowledge can be compiled deterministically.

# PG-002 — Living Workspace Intelligence

## INIT-003 — Build Workspace Intelligence

**Outcome:** Measure and explain workspace health.

### Epics

- \`EPIC-015\` — Workspace Intelligence & Memory
`,
    "utf8",
  );

  await writeFile(
    path.join(root, "product", "backlog", "MVP-BACKLOG.md"),
    `# MVP Backlog

| Feature | Work Packet | Sprint | Stories |
| --- | --- | --- | --- |
| F-003-01 Markdown ingestion | WP-MVP-0003 | WC-MVP-0001 | US-001 parse Markdown; EN-002 preserve provenance |
| F-003-03 Structured configuration parser | WP-MVP-0005 | WC-MVP-0002 | US-015 parse Monad config; US-016 schema errors; US-017 deterministic normalization |
`,
    "utf8",
  );

  await writeFile(
    path.join(root, "product", "backlog", "EXPANDED-BACKLOG.md"),
    `# Expanded Backlog

| Feature | Work Packet | Sprint | Stories |
| --- | --- | --- | --- |
| F-015-01 Intelligence score | WP-EXP-0001 | WC-EXP-0001 | US-106 score model; US-107 maturity tiers |
`,
    "utf8",
  );

  return root;
}

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { recursive: true, force: true })),
  );
});

describe("readPlanProjection", () => {
  test("builds the product hierarchy while keeping execution metadata orthogonal", async () => {
    const root = await fixtureRoot();
    const projection = await readPlanProjection(root);

    expect(projection.counts).toEqual({
      productGoals: 2,
      initiatives: 3,
      epics: 4,
      features: 3,
      stories: 6,
      enablers: 1,
    });

    const goal = projection.goals.find((item) => item.id === "PG-001");
    const initiative = goal?.initiatives.find((item) => item.id === "INIT-002");
    const epic = initiative?.epics.find((item) => item.id === "EPIC-003");
    const feature = epic?.features.find((item) => item.id === "F-003-03");

    expect(feature?.title).toBe("Structured configuration parser");
    expect(feature?.workPacket).toBe("WP-MVP-0005");
    expect(feature?.workCycle).toBe("WC-MVP-0002");
    expect(feature?.stories.map((story) => story.id)).toEqual([
      "US-015",
      "US-016",
      "US-017",
    ]);
  });

  test("classifies EN identifiers as enablers without changing their place in the product hierarchy", async () => {
    const root = await fixtureRoot();
    const projection = await readPlanProjection(root);

    const enabler = projection.goals
      .flatMap((goal) => goal.initiatives)
      .flatMap((initiative) => initiative.epics)
      .flatMap((epic) => epic.features)
      .flatMap((feature) => feature.stories)
      .find((story) => story.id === "EN-002");

    expect(enabler?.kind).toBe("enabler");
  });
});
