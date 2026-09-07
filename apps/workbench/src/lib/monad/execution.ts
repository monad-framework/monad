import { readFile } from "node:fs/promises";
import path from "node:path";

import { parseTsv } from "./tsv";

export type ExecutionProjectionRecord = {
  id: string;
  path: string;
  target: string;
  status: string;
  registryStatus?: string;
  branch: string;
  actor: string;
  created: string;
  updated: string;
};

export type ExecutionEvidenceSummary = {
  total: number;
  passed: number;
  failed: number;
  skipped: number;
  current: number;
};

type LifecycleProjection = {
  status: string;
  registryStatus?: string;
};

export type ExecutionWorkPacket = LifecycleProjection & {
  id: string;
  path: string;
  title: string;
  pi: string;
  wc: string;
  domain: string;
  created: string;
  updated: string;
  executions: ExecutionProjectionRecord[];
  evidence: ExecutionEvidenceSummary;
};

export type ExecutionWorkCycle = LifecycleProjection & {
  id: string;
  path: string;
  title: string;
  pi: string;
  created: string;
  updated: string;
  workPackets: ExecutionWorkPacket[];
};

export type ExecutionProgramIncrement = LifecycleProjection & {
  id: string;
  path: string;
  title: string;
  created: string;
  updated: string;
  workCycles: ExecutionWorkCycle[];
};

export type ExecutionProjectionCounts = {
  programIncrements: number;
  workCycles: number;
  workPackets: number;
  executions: number;
  evidence: number;
  lifecycleDrift: number;
};

export type ExecutionProjection = {
  programIncrements: ExecutionProgramIncrement[];
  counts: ExecutionProjectionCounts;
  sources: string[];
};

type ProgramIncrementRow = {
  id: string;
  path: string;
  title: string;
  status: string;
  created: string;
  updated: string;
};

type WorkCycleRow = {
  id: string;
  path: string;
  title: string;
  status: string;
  pi: string;
  created: string;
  updated: string;
};

type WorkPacketRow = {
  id: string;
  path: string;
  title: string;
  status: string;
  pi: string;
  wc: string;
  domain: string;
  created: string;
  updated: string;
};

type ExecutionRow = {
  id: string;
  path: string;
  target: string;
  status: string;
  branch: string;
  actor: string;
  created: string;
  updated: string;
};

type EvidenceRow = {
  id: string;
  target: string;
  status: string;
  result: string;
};

type CanonicalEntity = {
  id: string;
  lifecycle_state?: string;
};

type CurrentState = {
  entities?: Record<string, Record<string, CanonicalEntity>>;
};

const REGISTRY_SOURCES = [
  ".eos/program-increments.tsv",
  ".eos/work-cycles.tsv",
  ".eos/work-packets.tsv",
  ".eos/executions.tsv",
  ".eos/evidence.tsv",
] as const;
const CURRENT_STATE_SOURCE = ".eos/state/current.json";
const SOURCES = [...REGISTRY_SOURCES, CURRENT_STATE_SOURCE] as const;

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

async function readOptionalSource(
  root: string,
  relativePath: string,
  fallback: string,
): Promise<string> {
  try {
    return await readSource(root, relativePath);
  } catch {
    return fallback;
  }
}

function summarizeEvidence(rows: EvidenceRow[]): ExecutionEvidenceSummary {
  return rows.reduce<ExecutionEvidenceSummary>(
    (summary, row) => {
      summary.total += 1;

      if (row.status !== "SUPERSEDED") {
        summary.current += 1;
      }

      if (row.result === "PASSED") {
        summary.passed += 1;
      } else if (row.result === "FAILED") {
        summary.failed += 1;
      } else if (row.result === "SKIPPED") {
        summary.skipped += 1;
      }

      return summary;
    },
    {
      total: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
      current: 0,
    },
  );
}

function canonicalEntities(state: CurrentState): Map<string, CanonicalEntity> {
  const entities = new Map<string, CanonicalEntity>();

  for (const bucket of Object.values(state.entities ?? {})) {
    for (const entity of Object.values(bucket)) {
      entities.set(entity.id, entity);
    }
  }

  return entities;
}

function lifecycleProjection(
  id: string,
  registryStatus: string,
  entities: Map<string, CanonicalEntity>,
): LifecycleProjection {
  const canonical = entities.get(id)?.lifecycle_state;

  if (!canonical || canonical === registryStatus) {
    return { status: canonical ?? registryStatus };
  }

  return {
    status: canonical,
    registryStatus,
  };
}

export async function readExecutionProjection(
  root: string,
): Promise<ExecutionProjection> {
  const [piRaw, wcRaw, wpRaw, executionRaw, evidenceRaw, currentStateRaw] =
    await Promise.all([
      ...REGISTRY_SOURCES.map((source) => readSource(root, source)),
      readOptionalSource(root, CURRENT_STATE_SOURCE, "{}"),
    ]);

  const programRows = parseTsv<ProgramIncrementRow>(piRaw);
  const cycleRows = parseTsv<WorkCycleRow>(wcRaw);
  const packetRows = parseTsv<WorkPacketRow>(wpRaw);
  const executionRows = parseTsv<ExecutionRow>(executionRaw);
  const evidenceRows = parseTsv<EvidenceRow>(evidenceRaw);
  const currentState = JSON.parse(currentStateRaw) as CurrentState;
  const currentEntities = canonicalEntities(currentState);
  let lifecycleDrift = 0;

  const projectLifecycle = (id: string, registryStatus: string) => {
    const projection = lifecycleProjection(id, registryStatus, currentEntities);
    if (projection.registryStatus) {
      lifecycleDrift += 1;
    }
    return projection;
  };

  const executionsByTarget = new Map<string, ExecutionProjectionRecord[]>();
  const evidenceByTarget = new Map<string, EvidenceRow[]>();

  for (const row of executionRows) {
    const target = executionsByTarget.get(row.target) ?? [];
    const lifecycle = projectLifecycle(row.id, row.status);

    target.push({
      id: row.id,
      path: row.path,
      target: row.target,
      ...lifecycle,
      branch: row.branch,
      actor: row.actor,
      created: row.created,
      updated: row.updated,
    });

    executionsByTarget.set(row.target, target);
  }

  for (const row of evidenceRows) {
    const target = evidenceByTarget.get(row.target) ?? [];
    target.push(row);
    evidenceByTarget.set(row.target, target);
  }

  const packetsByCycle = new Map<string, ExecutionWorkPacket[]>();

  for (const row of packetRows) {
    const packet: ExecutionWorkPacket = {
      id: row.id,
      path: row.path,
      title: row.title,
      ...projectLifecycle(row.id, row.status),
      pi: row.pi,
      wc: row.wc,
      domain: row.domain,
      created: row.created,
      updated: row.updated,
      executions: executionsByTarget.get(row.id) ?? [],
      evidence: summarizeEvidence(evidenceByTarget.get(row.id) ?? []),
    };

    const packets = packetsByCycle.get(row.wc) ?? [];
    packets.push(packet);
    packetsByCycle.set(row.wc, packets);
  }

  const cyclesByProgram = new Map<string, ExecutionWorkCycle[]>();

  for (const row of cycleRows) {
    const cycle: ExecutionWorkCycle = {
      id: row.id,
      path: row.path,
      title: row.title,
      ...projectLifecycle(row.id, row.status),
      pi: row.pi,
      created: row.created,
      updated: row.updated,
      workPackets: packetsByCycle.get(row.id) ?? [],
    };

    const cycles = cyclesByProgram.get(row.pi) ?? [];
    cycles.push(cycle);
    cyclesByProgram.set(row.pi, cycles);
  }

  const programIncrements = programRows.map<ExecutionProgramIncrement>(
    (row) => ({
      id: row.id,
      path: row.path,
      title: row.title,
      ...projectLifecycle(row.id, row.status),
      created: row.created,
      updated: row.updated,
      workCycles: cyclesByProgram.get(row.id) ?? [],
    }),
  );

  return {
    programIncrements,
    counts: {
      programIncrements: programRows.length,
      workCycles: cycleRows.length,
      workPackets: packetRows.length,
      executions: executionRows.length,
      evidence: evidenceRows.length,
      lifecycleDrift,
    },
    sources: [...SOURCES],
  };
}
