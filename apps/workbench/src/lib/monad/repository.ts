import { execFile } from "node:child_process";
import { access, readdir, readFile } from "node:fs/promises";
import path from "node:path";

import type {
  GitStatusEntry,
  RepositorySnapshot,
  RepositorySource,
} from "./model";

async function exists(target: string): Promise<boolean> {
  try {
    await access(target);
    return true;
  } catch {
    return false;
  }
}

async function findMonadRoot(start: string): Promise<string> {
  let current = path.resolve(start);

  while (true) {
    const manifest = path.join(current, "monad.toml");

    if (await exists(manifest)) {
      return current;
    }

    const parent = path.dirname(current);

    if (parent === current) {
      throw new Error(`Unable to locate Monad repository root from ${start}`);
    }

    current = parent;
  }
}

async function countFiles(directory: string): Promise<number> {
  if (!(await exists(directory))) {
    return 0;
  }

  const entries = await readdir(directory, {
    withFileTypes: true,
  });

  let count = 0;

  for (const entry of entries) {
    const target = path.join(directory, entry.name);

    if (entry.isDirectory()) {
      count += await countFiles(target);
      continue;
    }

    if (entry.isFile()) {
      count += 1;
    }
  }

  return count;
}

function runGit(root: string, args: string[]): Promise<string> {
  return new Promise((resolve) => {
    execFile(
      "git",
      ["-C", root, ...args],
      {
        encoding: "utf8",
      },
      (error, stdout) => {
        if (error) {
          resolve("");
          return;
        }

        resolve(stdout.trim());
      },
    );
  });
}

async function readVersion(root: string): Promise<string | null> {
  const versionPath = path.join(root, "VERSION");

  if (!(await exists(versionPath))) {
    return null;
  }

  return (await readFile(versionPath, "utf8")).trim() || null;
}

function parseGitStatus(raw: string): GitStatusEntry[] {
  if (!raw) {
    return [];
  }

  return raw.split("\n").map((line) => ({
    status: line.slice(0, 2).trim() || "??",
    path: line.slice(3),
  }));
}

async function buildSources(root: string): Promise<RepositorySource[]> {
  const sourceDefinitions = [
    ["Engineering", "engineering"],
    ["Specifications", "specifications"],
    ["Schemas", "schemas"],
    ["Documentation", "docs"],
    ["Architecture", "architecture"],
    ["Product", "product"],
    ["Governance", "governance"],
    ["Monad metadata", ".monad"],
  ] as const;

  return Promise.all(
    sourceDefinitions.map(async ([label, relativePath]) => ({
      label,
      path: relativePath,
      fileCount: await countFiles(
        path.join(/* turbopackIgnore: true */ root, relativePath),
      ),
    })),
  );
}

export async function getRepositorySnapshot(): Promise<RepositorySnapshot> {
  const root = await findMonadRoot(process.cwd());

  const [branch, rawStatus, version, sources] = await Promise.all([
    runGit(root, ["branch", "--show-current"]),
    runGit(root, ["status", "--short"]),
    readVersion(root),
    buildSources(root),
  ]);

  return {
    rootPath: root,
    branch: branch || "unknown",
    version,
    workbenchSpecificationPresent: await exists(
      path.join(root, "docs/implementation/workbench-v0.md"),
    ),
    sources,
    gitStatus: parseGitStatus(rawStatus),
  };
}
