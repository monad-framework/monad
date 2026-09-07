import { readFile } from "node:fs/promises";
import path from "node:path";

import type {
  FocusDocument,
  FocusDocumentMetadata,
  FocusDocumentSection,
  MonadObject,
} from "./model";

function stripFrontmatter(lines: string[]): string[] {
  if (lines[0]?.trim() !== "---") {
    return lines;
  }

  const closingIndex = lines
    .slice(1)
    .findIndex((line) => line.trim() === "---");

  if (closingIndex === -1) {
    return lines;
  }

  return lines.slice(closingIndex + 2);
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function parseMarkdown(markdown: string, sourcePath: string): FocusDocument {
  const lines = stripFrontmatter(markdown.split(/\r?\n/));

  let heading: string | undefined;
  const introduction: string[] = [];
  const metadata: FocusDocumentMetadata[] = [];
  const sections: FocusDocumentSection[] = [];

  let currentTitle: string | undefined;
  let currentBody: string[] = [];

  function flushSection() {
    if (!currentTitle) {
      return;
    }

    sections.push({
      id: slugify(currentTitle),
      title: currentTitle,
      body: currentBody.join("\n").trim(),
    });

    currentTitle = undefined;
    currentBody = [];
  }

  for (const line of lines) {
    if (!heading && line.startsWith("# ")) {
      heading = line.slice(2).trim();
      continue;
    }

    if (line.startsWith("## ")) {
      flushSection();

      currentTitle = line.slice(3).trim();
      continue;
    }

    if (currentTitle) {
      currentBody.push(line);
      continue;
    }

    const metadataMatch = line.match(/^\*\*([^*]+?):\*\*\s*(.*?)\s*$/);

    if (metadataMatch) {
      metadata.push({
        label: metadataMatch[1].trim(),
        value: metadataMatch[2].trim(),
      });

      continue;
    }

    introduction.push(line);
  }

  flushSection();

  return {
    heading,
    introduction: introduction.join("\n").trim() || undefined,
    metadata,
    sections,
    sourcePath,
  };
}

export async function readFocusDocument(
  root: string,
  object: MonadObject | undefined,
): Promise<FocusDocument | undefined> {
  if (!object?.artifactPath) {
    return undefined;
  }

  const repositoryRoot = path.resolve(root);

  const target = path.resolve(repositoryRoot, object.artifactPath);

  if (
    target !== repositoryRoot &&
    !target.startsWith(`${repositoryRoot}${path.sep}`)
  ) {
    return undefined;
  }

  try {
    const markdown = await readFile(target, "utf8");

    return parseMarkdown(markdown, object.artifactPath);
  } catch {
    return undefined;
  }
}
