import { afterEach, expect, test } from "bun:test";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { readKnowledgeCatalogProjection } from "./knowledge-catalog";

const roots: string[] = [];

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { recursive: true, force: true })),
  );
});

test("ingests repository ADRs even when the EOS artifact registry has no ADR rows", async () => {
  const root = await mkdtemp(
    path.join(os.tmpdir(), "monad-workbench-knowledge-"),
  );
  roots.push(root);

  await mkdir(path.join(root, "product"), { recursive: true });
  await mkdir(path.join(root, ".eos"), { recursive: true });
  await mkdir(path.join(root, "architecture", "decisions"), {
    recursive: true,
  });

  await writeFile(
    path.join(root, "product", "product-requirements.md"),
    "# Requirements\n",
    "utf8",
  );
  await writeFile(
    path.join(root, ".eos", "artifacts.tsv"),
    "artifact_id\tpath\ttype\tauthority\n",
    "utf8",
  );
  await writeFile(
    path.join(root, ".eos", "evidence.tsv"),
    "id\tpath\ttarget\texecution\tvalidator\tprofile\tkind\tstatus\tresult\tcreated\tupdated\n",
    "utf8",
  );
  await writeFile(
    path.join(root, "architecture", "decisions", "ADR-0004-safe-ingestion.md"),
    "# ADR-0004 — Safe deterministic ingestion boundary\n",
    "utf8",
  );

  const projection = await readKnowledgeCatalogProjection(root);

  expect(projection.counts.adrs).toBe(1);
  expect(projection.adrs[0]?.id).toBe("ADR-0004");
  expect(projection.adrs[0]?.title).toBe(
    "Safe deterministic ingestion boundary",
  );
  expect(projection.adrs[0]?.path).toBe(
    "architecture/decisions/ADR-0004-safe-ingestion.md",
  );
});
