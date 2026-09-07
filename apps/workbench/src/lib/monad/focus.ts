import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

import type {
  CurrentExecutionContext,
  CurrentKnowledgeContext,
  CurrentProductContext,
  FocusContext,
  KnowledgeReference,
  MonadObject,
  MonadObjectType,
} from "./model";
import { parseTsv } from "./tsv";

type FocusInputs = {
  product: CurrentProductContext;
  execution: CurrentExecutionContext;
  knowledge: CurrentKnowledgeContext;
};

type TraceEdgeRow = {
  source_id: string;
  target_id: string;
  edge_type: string;
  source_path: string;
  evidence: string;
};

type ArtifactRow = {
  artifact_id: string;
  path: string;
  type: string;
  authority: string;
};

const SAFE_FOCUS_ID = /^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$/;

function currentObjects(inputs: FocusInputs): MonadObject[] {
  return [
    inputs.product.productGoal,
    inputs.product.initiative,
    inputs.product.epic,
    inputs.product.feature,
    ...inputs.product.stories,
    ...inputs.product.enablers,
    inputs.execution.programIncrement,
    inputs.execution.workCycle,
    inputs.execution.workPacket,
  ].filter((object): object is MonadObject => object !== undefined);
}

function objectTypeForId(id: string): MonadObjectType {
  if (id.startsWith("PG-")) {
    return "product-goal";
  }

  if (id.startsWith("INIT-")) {
    return "initiative";
  }

  if (id.startsWith("EPIC-")) {
    return "epic";
  }

  if (id.startsWith("F-")) {
    return "feature";
  }

  if (id.startsWith("US-")) {
    return "story";
  }

  if (id.startsWith("EN-")) {
    return "enabler";
  }

  if (id.startsWith("PI-")) {
    return "program-increment";
  }

  if (id.startsWith("WC-")) {
    return "work-cycle";
  }

  if (id.startsWith("WP-")) {
    return "work-packet";
  }

  if (id.startsWith("ADR-")) {
    return "adr";
  }

  if (id.startsWith("CR-")) {
    return "change-request";
  }

  if (id.startsWith("EVID-")) {
    return "evidence";
  }

  if (id.startsWith("FR-") || id.startsWith("QR-")) {
    return "requirement";
  }

  if (
    id.startsWith("IFC-") ||
    id.startsWith("DATA-") ||
    id.startsWith("TECH-")
  ) {
    return "specification";
  }

  return "specification";
}

async function readOptional(target: string): Promise<string | undefined> {
  try {
    return await readFile(
      /* turbopackIgnore: true */
      target,
      "utf8",
    );
  } catch {
    return undefined;
  }
}

function resolveRepositoryPath(
  root: string,
  relativePath: string,
): string | undefined {
  const repositoryRoot = path.resolve(root);

  const candidate = path.resolve(
    path.join(
      /* turbopackIgnore: true */
      root,
      relativePath,
    ),
  );

  if (
    candidate !== repositoryRoot &&
    !candidate.startsWith(`${repositoryRoot}${path.sep}`)
  ) {
    return undefined;
  }

  return candidate;
}

function titleFromMarkdown(markdown: string, id: string): string | undefined {
  const heading = markdown.match(/^#\s+(.+)$/m)?.[1]?.trim();

  if (!heading) {
    return undefined;
  }

  const escapedId = id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  const withoutId = heading
    .replace(new RegExp(`^${escapedId}\\s*`), "")
    .replace(/^[—–:-]\s*/, "")
    .trim();

  return withoutId || heading;
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

async function readArtifactIndex(
  root: string,
): Promise<Map<string, ArtifactRow>> {
  const raw = await readOptional(path.join(root, ".eos", "artifacts.tsv"));

  if (!raw) {
    return new Map();
  }

  return new Map(
    parseTsv<ArtifactRow>(raw).map((row) => [row.artifact_id, row]),
  );
}

async function resolvePath(
  root: string,
  id: string,
  artifacts: Map<string, ArtifactRow>,
): Promise<string | undefined> {
  const indexed = artifacts.get(id);

  if (indexed?.path) {
    return indexed.path;
  }

  if (id.startsWith("ADR-")) {
    return findAdrPath(root, id);
  }

  if (id.startsWith("WP-")) {
    return path.join("engineering", "work-packets", `${id}.md`);
  }

  if (id.startsWith("CR-")) {
    return path.join("engineering", "changes", `${id}.md`);
  }

  if (id.startsWith("EVID-")) {
    return path.join("engineering", "evidence", `${id}.md`);
  }

  return undefined;
}

async function resolveObject(
  root: string,
  id: string,
  inputs: FocusInputs,
  artifacts: Map<string, ArtifactRow>,
): Promise<MonadObject> {
  const current = currentObjects(inputs).find((object) => object.id === id);

  if (current) {
    return current;
  }

  const knowledgeReference = [
    ...inputs.knowledge.governing,
    ...inputs.knowledge.dependencies,
    ...inputs.knowledge.incoming,
  ].find((reference) => reference.id === id);

  const artifactPath =
    knowledgeReference?.path ?? (await resolvePath(root, id, artifacts));

  const resolvedArtifactPath = artifactPath
    ? resolveRepositoryPath(root, artifactPath)
    : undefined;

  const markdown = resolvedArtifactPath
    ? await readOptional(resolvedArtifactPath)
    : undefined;

  const artifact = artifacts.get(id);

  return {
    id,
    type: objectTypeForId(id),
    title: (markdown ? titleFromMarkdown(markdown, id) : undefined) ?? id,
    authority: artifact?.authority,
    source:
      artifactPath ?? knowledgeReference?.source ?? "unresolved-reference",
    artifactPath,
    relationships: [],
  };
}

function classifyReference(id: string): KnowledgeReference["kind"] {
  if (id.startsWith("ADR-")) {
    return "adr";
  }

  if (id.startsWith("WP-")) {
    return "work-packet";
  }

  if (id.startsWith("CR-")) {
    return "change-request";
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

  return "other";
}

function traceReference(
  id: string,
  relationship: string,
  row: TraceEdgeRow,
  sourcePathApplies: boolean,
): KnowledgeReference {
  return {
    id,
    kind: classifyReference(id),
    relationship,
    path: sourcePathApplies && row.source_path ? row.source_path : undefined,
    source: ".eos/trace-edges.tsv",
  };
}

async function readTraceContext(
  root: string,
  id: string,
): Promise<{
  incoming: KnowledgeReference[];
  outgoing: KnowledgeReference[];
}> {
  const raw = await readOptional(path.join(root, ".eos", "trace-edges.tsv"));

  if (!raw) {
    return {
      incoming: [],
      outgoing: [],
    };
  }

  const rows = parseTsv<TraceEdgeRow>(raw);

  return {
    outgoing: rows
      .filter((row) => row.source_id === id)
      .map((row) => traceReference(row.target_id, row.edge_type, row, false)),

    incoming: rows
      .filter((row) => row.target_id === id)
      .map((row) => traceReference(row.source_id, row.edge_type, row, true)),
  };
}

export async function readFocusContext(
  root: string,
  requestedId: string | undefined,
  inputs: FocusInputs,
): Promise<FocusContext> {
  const defaultId =
    inputs.execution.workPacket?.id ??
    inputs.product.feature?.id ??
    inputs.product.productGoal?.id;

  const requested = requestedId?.trim();

  const id = requested && SAFE_FOCUS_ID.test(requested) ? requested : defaultId;

  if (!id) {
    return {
      incoming: [],
      outgoing: [],
    };
  }

  const artifacts = await readArtifactIndex(root);

  const [object, trace] = await Promise.all([
    resolveObject(root, id, inputs, artifacts),
    readTraceContext(root, id),
  ]);

  return {
    requestedId: id,
    object: {
      ...object,
      relationships: trace.outgoing.map((reference) => ({
        type: reference.relationship,
        target: reference.id,
      })),
    },
    incoming: trace.incoming,
    outgoing: trace.outgoing,
  };
}
