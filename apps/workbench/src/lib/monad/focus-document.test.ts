import { afterEach, describe, expect, test } from "bun:test";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { readFocusDocument } from "./focus-document";
import type { MonadObject } from "./model";

const roots: string[] = [];

async function fixtureRoot(): Promise<string> {
  const root = await mkdtemp(path.join(os.tmpdir(), "monad-workbench-focus-"));
  roots.push(root);
  await mkdir(path.join(root, "engineering", "work-packets"), {
    recursive: true,
  });
  return root;
}

function workPacket(artifactPath: string): MonadObject {
  return {
    id: "WP-MVP-0005",
    type: "work-packet",
    title: "Structured Monad configuration parser",
    status: "IN_PROGRESS",
    source: artifactPath,
    artifactPath,
    relationships: [],
  };
}

afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { recursive: true, force: true })),
  );
});

describe("readFocusDocument", () => {
  test("parses frontmatter, metadata, introduction, and semantic sections", async () => {
    const root = await fixtureRoot();
    const artifactPath = "engineering/work-packets/WP-MVP-0005.md";

    await writeFile(
      path.join(root, artifactPath),
      `---\ntitle: "Packet"\n---\n\n# WP-MVP-0005 — Structured Monad configuration parser\n\n**Status:** IN_PROGRESS\n**Epic:** EPIC-003\n\nThis packet compiles canonical configuration.\n\n## Objective\n\nProduce deterministic semantic configuration.\n\n## Acceptance criteria\n\n- [ ] Parse valid configuration.\n`,
      "utf8",
    );

    const document = await readFocusDocument(root, workPacket(artifactPath));

    expect(document?.heading).toBe(
      "WP-MVP-0005 — Structured Monad configuration parser",
    );
    expect(document?.metadata).toEqual([
      { label: "Status", value: "IN_PROGRESS" },
      { label: "Epic", value: "EPIC-003" },
    ]);
    expect(document?.introduction).toBe(
      "This packet compiles canonical configuration.",
    );
    expect(document?.sections.map((section) => section.title)).toEqual([
      "Objective",
      "Acceptance criteria",
    ]);
  });

  test("refuses artifact paths outside the repository root", async () => {
    const root = await fixtureRoot();
    const outside = path.join(path.dirname(root), "outside-workbench.md");
    await writeFile(outside, "# Outside\n", "utf8");

    try {
      const document = await readFocusDocument(
        root,
        workPacket("../outside-workbench.md"),
      );
      expect(document).toBeUndefined();
    } finally {
      await rm(outside, { force: true });
    }
  });
});
