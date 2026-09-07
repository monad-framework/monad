import { afterEach, describe, expect, test } from "bun:test";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { findMonadRoot } from "./repository";

const roots: string[] = [];

async function fixtureRoot(): Promise<string> {
  const root = await mkdtemp(path.join(os.tmpdir(), "monad-workbench-root-"));
  roots.push(root);
  await writeFile(
    path.join(root, "monad.toml"),
    '[workspace]\nname = "fixture"\n',
    "utf8",
  );
  return root;
}

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { recursive: true, force: true })),
  );
});

describe("findMonadRoot", () => {
  test("walks upward from apps/workbench to the repository manifest", async () => {
    const root = await fixtureRoot();
    const nested = path.join(root, "apps", "workbench", "src", "app");
    await mkdir(nested, { recursive: true });

    await expect(findMonadRoot(nested)).resolves.toBe(root);
  });

  test("fails explicitly when no Monad manifest is reachable", async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), "not-monad-"));
    roots.push(root);

    await expect(findMonadRoot(root)).rejects.toThrow(
      "Unable to locate Monad repository root",
    );
  });
});
