import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

import type {
  AcceptanceCriterion,
  CurrentKnowledgeContext,
  EvidenceRecord,
  ExecutionRecord,
  KnowledgeReference,
  KnowledgeReferenceKind,
  MonadObject,
} from "./model";
import { parseTsv } from "./tsv";

type TraceEdgeRow = {
  source_id: string;
  target_id: string;
  edge_type: string;
  source_path: string;
  evidence: string;
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
};

type ExecutionRow = {
  id: string;
  path: string;
  target: string;
  status: string;
  branch: string;
  actor: string;
};

function classifyReference(id: string): KnowledgeReferenceKind {
  if (id.startsWith("ADR-")) {
    return "adr";
  }

  if (id.startsWith("FR-")) {
    return "requirement";
  }

  if (id.startsWith("QR-")) {
    return "quality-requirement";
  }

  if (id.startsWith("IFC-")) {
    return "interface";
  }

  if (id.startsWith("DATA-")) {
    return "data";
  }

  if (id.startsWith("TECH-")) {
    return "technical";
  }

  if (id.startsWith("WP-")) {
    return "work-packet";
  }

  if (id.startsWith("CR-")) {
    return "change-request";
  }

  return "other";
}

async function readText(root: string, relativePath: string): Promise<string> {
  return readFile(path.join(root, relativePath), "utf8");
}

function readSection(markdown: string, heading: string): string | undefined {
  const lines = markdown.split(/\r?\n/);
  const headingLine = `## ${heading}`;

  const start = lines.findIndex((line) => line.trim() === headingLine);

  if (start === -1) {
    return undefined;
  }

  const body: string[] = [];

  for (let index = start + 1; index < lines.length; index += 1) {
    const line = lines[index];

    if (line.startsWith("## ")) {
      break;
    }

    body.push(line);
  }

  return body.join("\n").trim();
}

function extractIdentifiers(text: string): string[] {
  const identifiers =
    text.match(/\b(?:ADR|FR|QR|IFC|DATA|TECH|WP|CR)-[A-Z0-9-]+\b/g) ?? [];

  return [...new Set(identifiers)];
}

function parseAcceptanceCriteria(markdown: string): AcceptanceCriterion[] {
  const section = readSection(markdown, "Acceptance criteria");

  if (!section) {
    return [];
  }

  return section
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(
      (line) =>
        line.startsWith("- [ ]") ||
        line.startsWith("- [x]") ||
        line.startsWith("- [X]"),
    )
    .map((line) => ({
      complete: line.startsWith("- [x]") || line.startsWith("- [X]"),
      text: line.replace(/^- \[[ xX]\]\s*/, ""),
    }));
}

async function findAdrPath(
  root: string,
  id: string,
): Promise<string | undefined> {
  const directory = path.join(root, "architecture", "decisions");

  try {
    const files = await readdir(directory);

    const match = files.find((file) => file.startsWith(`${id}-`));

    return match ? path.join("architecture", "decisions", match) : undefined;
  } catch {
    return undefined;
  }
}

async function resolveReferencePath(
  root: string,
  id: string,
): Promise<string | undefined> {
  if (id.startsWith("ADR-")) {
    return findAdrPath(root, id);
  }

  if (id.startsWith("WP-")) {
    const candidate = path.join("engineering", "work-packets", `${id}.md`);

    try {
      await readFile(path.join(root, candidate), "utf8");
      return candidate;
    } catch {
      return undefined;
    }
  }

  if (id.startsWith("CR-")) {
    const candidate = path.join("engineering", "changes", `${id}.md`);

    try {
      await readFile(path.join(root, candidate), "utf8");
      return candidate;
    } catch {
      return undefined;
    }
  }

  return undefined;
}

async function makeReference(
  root: string,
  id: string,
  relationship: string,
  source: string,
): Promise<KnowledgeReference> {
  return {
    id,
    kind: classifyReference(id),
    relationship,
    path: await resolveReferencePath(root, id),
    source,
  };
}

async function readTraceReferences(
  root: string,
  workPacketId: string,
): Promise<{
  outgoing: KnowledgeReference[];
  incoming: KnowledgeReference[];
}> {
  const source = ".eos/trace-edges.tsv";
  const raw = await readText(root, source);

  const rows = parseTsv<TraceEdgeRow>(raw);

  const outgoingRows = rows.filter((row) => row.source_id === workPacketId);

  const incomingRows = rows.filter((row) => row.target_id === workPacketId);

  const outgoing = await Promise.all(
    outgoingRows.map((row) =>
      makeReference(root, row.target_id, row.edge_type, source),
    ),
  );

  const incoming = await Promise.all(
    incomingRows.map((row) =>
      makeReference(root, row.source_id, row.edge_type, source),
    ),
  );

  return {
    outgoing,
    incoming,
  };
}

async function readEvidence(
  root: string,
  workPacketId: string,
): Promise<EvidenceRecord[]> {
  const raw = await readText(root, ".eos/evidence.tsv");

  return parseTsv<EvidenceRow>(raw)
    .filter((row) => row.target === workPacketId)
    .map((row) => ({
      id: row.id,
      path: row.path,
      status: row.status,
      result: row.result,
      validator: row.validator,
      kind: row.kind,
    }));
}

async function readExecutions(
  root: string,
  workPacketId: string,
): Promise<ExecutionRecord[]> {
  const raw = await readText(root, ".eos/executions.tsv");

  return parseTsv<ExecutionRow>(raw)
    .filter((row) => row.target === workPacketId)
    .map((row) => ({
      id: row.id,
      path: row.path,
      status: row.status,
      actor: row.actor,
      branch: row.branch,
    }));
}

function deduplicate(references: KnowledgeReference[]): KnowledgeReference[] {
  const seen = new Set<string>();

  return references.filter((reference) => {
    const key = `${reference.relationship}:${reference.id}`;

    if (seen.has(key)) {
      return false;
    }

    seen.add(key);
    return true;
  });
}

export async function readCurrentKnowledgeContext(
  root: string,
  workPacket: MonadObject | undefined,
): Promise<CurrentKnowledgeContext> {
  if (!workPacket?.artifactPath) {
    return {
      governing: [],
      dependencies: [],
      incoming: [],
      acceptanceCriteria: [],
      evidence: [],
      executions: [],
    };
  }

  const markdown = await readText(root, workPacket.artifactPath);

  const governingSection = readSection(markdown, "Governing authority") ?? "";

  const dependencySection = readSection(markdown, "Dependencies") ?? "";

  const governingIds = extractIdentifiers(governingSection);
  const dependencyIds = extractIdentifiers(dependencySection);

  const trace = await readTraceReferences(root, workPacket.id);

  const explicitGoverning = await Promise.all(
    governingIds.map((id) =>
      makeReference(root, id, "GOVERNS", workPacket.artifactPath ?? ""),
    ),
  );

  const explicitDependencies = await Promise.all(
    dependencyIds.map((id) =>
      makeReference(root, id, "DEPENDS_ON", workPacket.artifactPath ?? ""),
    ),
  );

  const traceGovernance = trace.outgoing.filter(
    (reference) =>
      reference.relationship === "conforms-to" || reference.kind === "adr",
  );

  const traceDependencies = trace.outgoing.filter(
    (reference) => reference.kind === "work-packet",
  );

  const [evidence, executions] = await Promise.all([
    readEvidence(root, workPacket.id),
    readExecutions(root, workPacket.id),
  ]);

  return {
    governing: deduplicate([...explicitGoverning, ...traceGovernance]),
    dependencies: deduplicate([...explicitDependencies, ...traceDependencies]),
    incoming: deduplicate(trace.incoming),
    acceptanceCriteria: parseAcceptanceCriteria(markdown),
    evidence,
    executions,
  };
}
