import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

import { parseTsv } from "./tsv";

export type KnowledgeCatalogKind =
  | "requirement"
  | "specification"
  | "adr"
  | "policy"
  | "evidence";

export type KnowledgeCatalogItem = {
  id: string;
  kind: KnowledgeCatalogKind;
  title: string;
  path: string;
  authority?: string;
  status?: string;
  summary?: string;
  target?: string;
  validator?: string;
  result?: string;
  updated?: string;
};

export type KnowledgeCatalogCounts = {
  requirements: number;
  specifications: number;
  adrs: number;
  policies: number;
  evidence: number;
  currentEvidence: number;
};

export type KnowledgeCatalogProjection = {
  requirements: KnowledgeCatalogItem[];
  specifications: KnowledgeCatalogItem[];
  adrs: KnowledgeCatalogItem[];
  policies: KnowledgeCatalogItem[];
  evidence: KnowledgeCatalogItem[];
  counts: KnowledgeCatalogCounts;
  sources: string[];
};

type ArtifactRow = {
  artifact_id: string;
  path: string;
  type: string;
  authority: string;
};

type EvidenceRow = {
  id: string;
  path: string;
  target: string;
  execution: string;
  validator: string;
  profile: string;
  kind: string;
  status: string;
  result: string;
  created: string;
  updated: string;
};

const REQUIREMENTS_SOURCE = "product/product-requirements.md";
const ARTIFACTS_SOURCE = ".eos/artifacts.tsv";
const EVIDENCE_SOURCE = ".eos/evidence.tsv";
const ADR_SOURCE = "architecture/decisions";

function sourcePath(root: string, relativePath: string): string {
  return path.join(
    /* turbopackIgnore: true */
    root,
    relativePath,
  );
}

async function readSource(root: string, relativePath: string): Promise<string> {
  return readFile(sourcePath(root, relativePath), "utf8");
}

function humanize(value: string): string {
  return value
    .replace(/\.(?:md|mdx|json|ya?ml|toml)$/i, "")
    .replace(/^(?:ADR|SPEC|IFC|DATA|TECH)-[A-Z0-9-]+[-_]?/i, "")
    .replace(/[-_]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^./, (character) => character.toUpperCase());
}

function artifactTitle(row: ArtifactRow): string {
  const basename = path.basename(row.path);
  const title = humanize(basename);
  return title || row.artifact_id;
}

function parseRequirements(markdown: string): KnowledgeCatalogItem[] {
  const matches = [...markdown.matchAll(/^### ((?:FR|QR)-\d+) — (.+)$/gm)];

  return matches.map((match, index) => {
    const start = (match.index ?? 0) + match[0].length;
    const end = matches[index + 1]?.index ?? markdown.length;
    const body = markdown.slice(start, end).trim();
    const firstParagraph = body
      .split(/\n\s*\n/)
      .find((paragraph) => paragraph.trim().length > 0)
      ?.replace(/\s+/g, " ")
      .trim();

    return {
      id: match[1],
      kind: "requirement" as const,
      title: match[2].trim(),
      path: REQUIREMENTS_SOURCE,
      authority: "requirements-authoritative",
      summary: firstParagraph,
    };
  });
}

function classifyArtifact(row: ArtifactRow): KnowledgeCatalogKind | undefined {
  if (
    /^ADR-/i.test(row.artifact_id) ||
    /architecture\/decisions\//i.test(row.path)
  ) {
    return "adr";
  }

  if (
    /specification/i.test(row.type) ||
    /^(?:SPEC|IFC|DATA|TECH)-/i.test(row.artifact_id) ||
    /^specifications\//i.test(row.path)
  ) {
    return "specification";
  }

  if (
    /policy/i.test(row.type) ||
    /policy/i.test(row.artifact_id) ||
    /policy/i.test(row.path)
  ) {
    return "policy";
  }

  return undefined;
}

function mapArtifact(
  row: ArtifactRow,
  kind: KnowledgeCatalogKind,
): KnowledgeCatalogItem {
  return {
    id: row.artifact_id,
    kind,
    title: artifactTitle(row),
    path: row.path,
    authority: row.authority,
  };
}

function mapEvidence(row: EvidenceRow): KnowledgeCatalogItem {
  return {
    id: row.id,
    kind: "evidence",
    title: `${row.validator || row.kind || "Evidence"} · ${row.result || row.status}`,
    path: row.path,
    authority: "evidence-authoritative",
    status: row.status,
    target: row.target,
    validator: row.validator,
    result: row.result,
    updated: row.updated,
  };
}

async function readAdrDirectory(root: string): Promise<KnowledgeCatalogItem[]> {
  try {
    const directory = sourcePath(root, ADR_SOURCE);
    const entries = await readdir(directory, { withFileTypes: true });
    const items: KnowledgeCatalogItem[] = [];

    for (const entry of entries) {
      if (!entry.isFile() || !/^ADR-\d+.*\.md$/i.test(entry.name)) {
        continue;
      }

      const id = entry.name.match(/^(ADR-\d+)/i)?.[1]?.toUpperCase();
      if (!id) {
        continue;
      }

      const relativePath = `${ADR_SOURCE}/${entry.name}`;
      const markdown = await readSource(root, relativePath);
      const heading = markdown.match(/^#\s+(.+)$/m)?.[1]?.trim();
      const title = heading
        ?.replace(new RegExp(`^${id}\\s*(?:—|-|:)\\s*`, "i"), "")
        .trim();

      items.push({
        id,
        kind: "adr",
        title: title || humanize(entry.name) || id,
        path: relativePath,
        authority: "architecture-decision-authoritative",
      });
    }

    return items;
  } catch {
    return [];
  }
}

function sortById<T extends { id: string }>(items: T[]): T[] {
  return [...items].sort((left, right) =>
    left.id.localeCompare(right.id, undefined, { numeric: true }),
  );
}

export async function readKnowledgeCatalogProjection(
  root: string,
): Promise<KnowledgeCatalogProjection> {
  const [requirementsRaw, artifactsRaw, evidenceRaw, repositoryAdrs] =
    await Promise.all([
      readSource(root, REQUIREMENTS_SOURCE),
      readSource(root, ARTIFACTS_SOURCE),
      readSource(root, EVIDENCE_SOURCE),
      readAdrDirectory(root),
    ]);

  const requirements = parseRequirements(requirementsRaw);
  const artifacts = parseTsv<ArtifactRow>(artifactsRaw);
  const evidenceRows = parseTsv<EvidenceRow>(evidenceRaw);

  const specifications: KnowledgeCatalogItem[] = [];
  const adrById = new Map(repositoryAdrs.map((item) => [item.id, item]));
  const policies: KnowledgeCatalogItem[] = [];

  for (const artifact of artifacts) {
    const kind = classifyArtifact(artifact);

    if (!kind) {
      continue;
    }

    const item = mapArtifact(artifact, kind);

    if (kind === "adr") {
      const repositoryAdr = adrById.get(item.id);
      adrById.set(item.id, {
        ...repositoryAdr,
        ...item,
        title: repositoryAdr?.title || item.title,
        path: repositoryAdr?.path || item.path,
        authority: item.authority || repositoryAdr?.authority,
      });
    } else if (kind === "policy") {
      policies.push(item);
    } else if (kind === "specification") {
      specifications.push(item);
    }
  }

  const adrs = [...adrById.values()];
  const evidence = [...evidenceRows]
    .sort((left, right) => right.updated.localeCompare(left.updated))
    .map(mapEvidence);

  return {
    requirements: sortById(requirements),
    specifications: sortById(specifications),
    adrs: sortById(adrs),
    policies: sortById(policies),
    evidence,
    counts: {
      requirements: requirements.length,
      specifications: specifications.length,
      adrs: adrs.length,
      policies: policies.length,
      evidence: evidence.length,
      currentEvidence: evidence.filter((item) => item.status !== "SUPERSEDED")
        .length,
    },
    sources: [
      REQUIREMENTS_SOURCE,
      ARTIFACTS_SOURCE,
      EVIDENCE_SOURCE,
      ADR_SOURCE,
    ],
  };
}
