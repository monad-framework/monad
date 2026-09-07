import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";

import {
  readControlProjection,
  type ControlArtifactItem,
  type ControlProjection,
  type ReleaseItem,
} from "./control";
import {
  readExecutionProjection,
  type ExecutionProgramIncrement,
  type ExecutionProjection,
  type ExecutionProjectionRecord,
  type ExecutionWorkCycle,
  type ExecutionWorkPacket,
} from "./execution";
import type {
  AttentionClassification,
  AttentionCondition,
  AttentionProjection,
  AttentionSeverity,
  AttentionState,
  AttentionSummary,
  AutonomousWorkstream,
} from "./attention-model";
import { parseTsv } from "./tsv";

export type AttentionEvidenceRow = {
  id: string;
  path: string;
  target: string;
  execution: string;
  validator: string;
  kind: string;
  status: string;
  result: string;
  created: string;
  updated: string;
};

export type AttentionProviderContext = {
  root: string;
  execution: ExecutionProjection;
  control: ControlProjection;
  evidence: AttentionEvidenceRow[];
};

type AttentionObservation = Omit<AttentionCondition, "id">;

export type AttentionProviderResult = {
  conditions: AttentionObservation[];
  workstreams?: AutonomousWorkstream[];
  sources?: string[];
};

export type AttentionProvider = {
  id: string;
  project: (
    context: AttentionProviderContext,
  ) => AttentionProviderResult | Promise<AttentionProviderResult>;
};

type StateProfile = {
  state: AttentionState;
  classification: AttentionClassification;
  severity: AttentionSeverity;
  current: boolean;
};

const EVIDENCE_SOURCE = ".eos/evidence.tsv";

function sourcePath(root: string, relativePath: string): string {
  return path.join(
    /* turbopackIgnore: true */
    root,
    relativePath,
  );
}

async function readEvidence(root: string): Promise<AttentionEvidenceRow[]> {
  try {
    return parseTsv<AttentionEvidenceRow>(
      await readFile(sourcePath(root, EVIDENCE_SOURCE), "utf8"),
    );
  } catch {
    return [];
  }
}

function normalizeStatus(value: string): string {
  return value.trim().toUpperCase().replace(/[ -]+/g, "_");
}

function stateProfile(rawStatus: string): StateProfile | undefined {
  const status = normalizeStatus(rawStatus);

  if (
    status === "HUMAN_ACTION_REQUIRED" ||
    status === "WAITING_FOR_HUMAN" ||
    status === "AWAITING_APPROVAL" ||
    status === "PENDING_APPROVAL"
  ) {
    return {
      state: "HUMAN_ACTION_REQUIRED",
      classification: "operator-action",
      severity: "critical",
      current: true,
    };
  }

  if (status === "BLOCKED") {
    return {
      state: "BLOCKED",
      classification: "operator-action",
      severity: "critical",
      current: true,
    };
  }

  if (status === "FAILED" || status === "FAILURE") {
    return {
      state: "FAILED",
      classification: "operator-action",
      severity: "critical",
      current: true,
    };
  }

  if (status === "READY_FOR_INTEGRATION") {
    return {
      state: "READY_FOR_INTEGRATION",
      classification: "operator-action",
      severity: "warning",
      current: true,
    };
  }

  if (status === "STALE") {
    return {
      state: "STALE",
      classification: "attention",
      severity: "warning",
      current: true,
    };
  }

  if (status === "DRIFTED" || status === "DRIFT") {
    return {
      state: "DRIFTED",
      classification: "attention",
      severity: "warning",
      current: true,
    };
  }

  if (status === "RUNNING") {
    return {
      state: "RUNNING",
      classification: "activity",
      severity: "info",
      current: true,
    };
  }

  if (status === "COMPLETED" || status === "CLOSED") {
    return {
      state: "COMPLETED",
      classification: "activity",
      severity: "info",
      current: false,
    };
  }

  return undefined;
}

function titleForState(id: string, state: AttentionState): string {
  const label = state.toLowerCase().replaceAll("_", " ");
  return `${id} · ${label}`;
}

function observation(input: {
  dedupeKey: string;
  profile: StateProfile;
  provider: string;
  source: string;
  sourceKind: string;
  objectId: string;
  objectType: string;
  objectTitle?: string;
  reason: string;
  observedAt?: string;
  href?: string;
  title?: string;
}): AttentionObservation {
  return {
    dedupeKey: input.dedupeKey,
    classification: input.profile.classification,
    state: input.profile.state,
    severity: input.profile.severity,
    title: input.title ?? titleForState(input.objectId, input.profile.state),
    reason: input.reason,
    affectedObject: {
      id: input.objectId,
      type: input.objectType,
      title: input.objectTitle,
      href: input.href,
    },
    provenance: {
      provider: input.provider,
      source: input.source,
      sourceKind: input.sourceKind,
      observedAt: input.observedAt,
    },
    current: input.profile.current,
    freshness: input.profile.current ? "current" : "historical",
    action: input.href
      ? {
          kind: "navigate",
          label: "Open object",
          href: input.href,
        }
      : undefined,
  };
}

function statusObservation(input: {
  rawStatus: string;
  provider: string;
  source: string;
  sourceKind: string;
  objectId: string;
  objectType: string;
  objectTitle?: string;
  reason: string;
  observedAt?: string;
  href?: string;
  dedupeKey?: string;
}): AttentionObservation | undefined {
  const profile = stateProfile(input.rawStatus);

  if (!profile) {
    return undefined;
  }

  return observation({
    ...input,
    profile,
    dedupeKey:
      input.dedupeKey ??
      `${input.sourceKind}:${input.objectId}:${profile.state}`,
  });
}

function lifecycleDriftObservation(input: {
  id: string;
  type: string;
  title: string;
  status: string;
  registryStatus: string;
  updated?: string;
  registrySource: string;
}): AttentionObservation {
  return observation({
    dedupeKey: `lifecycle-drift:${input.id}`,
    profile: {
      state: "DRIFTED",
      classification: "attention",
      severity: "warning",
      current: true,
    },
    provider: "eos-lifecycle",
    source: `.eos/state/current.json ↔ ${input.registrySource}`,
    sourceKind: "canonical-lifecycle-drift",
    objectId: input.id,
    objectType: input.type,
    objectTitle: input.title,
    href: `/focus/${encodeURIComponent(input.id)}`,
    observedAt: input.updated,
    title: `${input.id} lifecycle projection drift`,
    reason: `${input.id} is ${input.status} in canonical EOS current state while ${input.registrySource} reports ${input.registryStatus}. Canonical EOS current state wins.`,
  });
}

function executionConditions(
  execution: ExecutionProjection,
): AttentionObservation[] {
  const conditions: AttentionObservation[] = [];

  const addLifecycle = (
    item:
      | ExecutionProgramIncrement
      | ExecutionWorkCycle
      | ExecutionWorkPacket
      | ExecutionProjectionRecord,
    type: string,
    title: string,
    registrySource: string,
  ) => {
    if (item.registryStatus) {
      conditions.push(
        lifecycleDriftObservation({
          id: item.id,
          type,
          title,
          status: item.status,
          registryStatus: item.registryStatus,
          updated: item.updated,
          registrySource,
        }),
      );
    }

    const projected = statusObservation({
      rawStatus: item.status,
      provider: "eos-lifecycle",
      source: ".eos/state/current.json",
      sourceKind: "canonical-lifecycle",
      objectId: item.id,
      objectType: type,
      objectTitle: title,
      reason: `${item.id} is ${item.status} according to the canonical EOS lifecycle projection.`,
      observedAt: item.updated,
      href: `/focus/${encodeURIComponent(item.id)}`,
    });

    if (projected) {
      conditions.push(projected);
    }
  };

  for (const program of execution.programIncrements) {
    addLifecycle(
      program,
      "program-increment",
      program.title,
      ".eos/program-increments.tsv",
    );

    for (const cycle of program.workCycles) {
      addLifecycle(cycle, "work-cycle", cycle.title, ".eos/work-cycles.tsv");

      for (const packet of cycle.workPackets) {
        addLifecycle(
          packet,
          "work-packet",
          packet.title,
          ".eos/work-packets.tsv",
        );

        for (const executionRecord of packet.executions) {
          addLifecycle(
            executionRecord,
            "execution",
            executionRecord.id,
            ".eos/executions.tsv",
          );
        }
      }
    }
  }

  return conditions;
}

function isTerminal(value: string): boolean {
  const status = normalizeStatus(value);
  return ["CLOSED", "COMPLETED", "SUPERSEDED", "CANCELLED"].includes(status);
}

function latestExecution(
  executions: ExecutionProjectionRecord[],
): ExecutionProjectionRecord | undefined {
  return [...executions].sort((left, right) =>
    right.updated.localeCompare(left.updated),
  )[0];
}

function deriveWorkstreamState(
  packet: ExecutionWorkPacket,
  execution?: ExecutionProjectionRecord,
): { state: string; reason: string } {
  if (execution && !isTerminal(execution.status)) {
    return {
      state: normalizeStatus(execution.status),
      reason: `${execution.id} is ${execution.status}; the execution currently determines the observable autonomous-work state.`,
    };
  }

  if (
    execution &&
    isTerminal(execution.status) &&
    normalizeStatus(packet.status) === "IN_PROGRESS"
  ) {
    return {
      state: "RECONCILING",
      reason: `${execution.id} is ${execution.status} while ${packet.id} remains ${packet.status}; post-execution reconciliation is still observable.`,
    };
  }

  if (normalizeStatus(packet.status) === "IN_PROGRESS") {
    return {
      state: "RUNNING",
      reason: `${packet.id} is IN_PROGRESS in canonical EOS lifecycle state.`,
    };
  }

  if (normalizeStatus(packet.status) === "READY") {
    return {
      state: "PREPARING",
      reason: `${packet.id} is READY but no active execution currently owns the workstream.`,
    };
  }

  return {
    state: normalizeStatus(packet.status),
    reason: `${packet.id} is ${packet.status} in canonical EOS lifecycle state.`,
  };
}

function workstreams(execution: ExecutionProjection): AutonomousWorkstream[] {
  const streams: AutonomousWorkstream[] = [];

  for (const program of execution.programIncrements) {
    for (const cycle of program.workCycles) {
      for (const packet of cycle.workPackets) {
        const latest = latestExecution(packet.executions);
        const current =
          !isTerminal(packet.status) || (latest ? !isTerminal(latest.status) : false);

        if (!current) {
          continue;
        }

        const derived = deriveWorkstreamState(packet, latest);
        const packetStatus = normalizeStatus(packet.status);
        const authorization =
          packetStatus === "READY"
            ? "NOT_GRANTED"
            : ["AUTHORIZED", "IN_PROGRESS"].includes(packetStatus)
              ? "GRANTED"
              : undefined;

        streams.push({
          id: `eos-work-packet:${packet.id}`,
          group: packet.domain || cycle.title || program.title,
          label: packet.title,
          objectId: packet.id,
          objectHref: `/focus/${encodeURIComponent(packet.id)}`,
          state: derived.state,
          reason: derived.reason,
          source: ".eos/state/current.json",
          updatedAt: latest?.updated || packet.updated,
          latestExecutionId: latest?.id,
          authorization,
          current: true,
        });
      }
    }
  }

  return streams.sort((left, right) =>
    (right.updatedAt ?? "").localeCompare(left.updatedAt ?? ""),
  );
}

function latestCurrentEvidence(rows: AttentionEvidenceRow[]): AttentionEvidenceRow[] {
  const latest = new Map<string, AttentionEvidenceRow>();

  for (const row of rows) {
    if (normalizeStatus(row.status) === "SUPERSEDED") {
      continue;
    }

    const key = `${row.target}:${row.validator || row.kind}`;
    const current = latest.get(key);

    if (!current || row.updated.localeCompare(current.updated) > 0) {
      latest.set(key, row);
    }
  }

  return [...latest.values()];
}

function evidenceConditions(rows: AttentionEvidenceRow[]): AttentionObservation[] {
  const conditions: AttentionObservation[] = [];

  for (const row of latestCurrentEvidence(rows)) {
    const status = normalizeStatus(row.status);
    const result = normalizeStatus(row.result);
    const href = row.target
      ? `/focus/${encodeURIComponent(row.target)}`
      : undefined;

    if (result === "FAILED") {
      const projected = statusObservation({
        rawStatus: "FAILED",
        provider: "eos-evidence",
        source: EVIDENCE_SOURCE,
        sourceKind: "verification-evidence",
        objectId: row.target || row.id,
        objectType: row.target ? "verification-target" : "evidence",
        objectTitle: row.validator || row.kind,
        reason: `${row.id} is the latest current ${row.validator || row.kind} evidence for ${row.target || "its target"} and reports FAILED.`,
        observedAt: row.updated,
        href,
        dedupeKey: `evidence:${row.target}:${row.validator || row.kind}:FAILED`,
      });

      if (projected) {
        conditions.push(projected);
      }
      continue;
    }

    if (status === "STALE" || status === "DRIFTED") {
      const projected = statusObservation({
        rawStatus: status,
        provider: "eos-evidence",
        source: EVIDENCE_SOURCE,
        sourceKind: "verification-evidence-freshness",
        objectId: row.target || row.id,
        objectType: row.target ? "verification-target" : "evidence",
        objectTitle: row.validator || row.kind,
        reason: `${row.id} is the latest current ${row.validator || row.kind} evidence and its freshness state is ${status}.`,
        observedAt: row.updated,
        href,
        dedupeKey: `evidence:${row.target}:${row.validator || row.kind}:${status}`,
      });

      if (projected) {
        conditions.push(projected);
      }
    }
  }

  return conditions;
}

function controlStatusCondition(
  item: ControlArtifactItem | ReleaseItem,
  objectType: string,
  source: string,
): AttentionObservation | undefined {
  const status = item.status;

  if (!status) {
    return undefined;
  }

  return statusObservation({
    rawStatus: status,
    provider: "workbench-control",
    source,
    sourceKind: objectType,
    objectId: item.id,
    objectType,
    objectTitle: "title" in item ? item.title : item.version,
    reason: `${item.id} is ${status} in ${source}.`,
    observedAt: "updated" in item ? item.updated : undefined,
    href: `/focus/${encodeURIComponent(item.id)}`,
  });
}

function controlConditions(control: ControlProjection): AttentionObservation[] {
  const conditions: AttentionObservation[] = control.findings.map((finding) =>
    observation({
      dedupeKey: `control-finding:${finding.id}`,
      profile: {
        state: "DRIFTED",
        classification: "attention",
        severity: finding.severity === "warning" ? "warning" : "info",
        current: true,
      },
      provider: "workbench-control",
      source: `${finding.canonicalSource} ↔ ${finding.comparedSource}`,
      sourceKind: "consistency-finding",
      objectId: finding.id,
      objectType: "control-finding",
      objectTitle: finding.title,
      href: "/control",
      title: finding.title,
      reason: finding.detail,
    }),
  );

  for (const change of control.changes) {
    const projected = statusObservation({
      rawStatus: change.status,
      provider: "workbench-control",
      source: ".eos/change-requests.tsv",
      sourceKind: "change-request",
      objectId: change.id,
      objectType: "change-request",
      objectTitle: change.summary,
      reason: `${change.id} is ${change.status} according to the change-request registry.`,
      observedAt: change.updated,
      href: `/focus/${encodeURIComponent(change.id)}`,
    });

    if (projected) {
      conditions.push(projected);
    }
  }

  for (const risk of control.risks) {
    const projected = controlStatusCondition(
      risk,
      "risk",
      "engineering/risks/risk-register.md",
    );
    if (projected) conditions.push(projected);
  }

  for (const release of control.releases) {
    const projected = controlStatusCondition(
      release,
      "release",
      ".eos/releases.tsv",
    );
    if (projected) conditions.push(projected);
  }

  return conditions;
}

export const eosLifecycleAttentionProvider: AttentionProvider = {
  id: "eos-lifecycle",
  project(context) {
    return {
      conditions: executionConditions(context.execution),
      workstreams: workstreams(context.execution),
      sources: context.execution.sources,
    };
  },
};

export const eosEvidenceAttentionProvider: AttentionProvider = {
  id: "eos-evidence",
  project(context) {
    return {
      conditions: evidenceConditions(context.evidence),
      sources: [EVIDENCE_SOURCE],
    };
  },
};

export const controlAttentionProvider: AttentionProvider = {
  id: "workbench-control",
  project(context) {
    return {
      conditions: controlConditions(context.control),
      sources: context.control.sources,
    };
  },
};

export const DEFAULT_ATTENTION_PROVIDERS: AttentionProvider[] = [
  eosLifecycleAttentionProvider,
  eosEvidenceAttentionProvider,
  controlAttentionProvider,
];

function stableConditionId(dedupeKey: string): string {
  return `ATTN-${createHash("sha256").update(dedupeKey).digest("hex").slice(0, 12).toUpperCase()}`;
}

function dedupeConditions(
  observations: AttentionObservation[],
): AttentionCondition[] {
  const byKey = new Map<string, AttentionObservation>();

  for (const candidate of observations) {
    const existing = byKey.get(candidate.dedupeKey);

    if (!existing) {
      byKey.set(candidate.dedupeKey, candidate);
      continue;
    }

    const existingTime = existing.provenance.observedAt ?? "";
    const candidateTime = candidate.provenance.observedAt ?? "";

    if (
      candidate.current !== existing.current
        ? candidate.current
        : candidateTime.localeCompare(existingTime) >= 0
    ) {
      byKey.set(candidate.dedupeKey, candidate);
    }
  }

  const severityRank: Record<AttentionSeverity, number> = {
    critical: 0,
    warning: 1,
    info: 2,
  };

  return [...byKey.values()]
    .map<AttentionCondition>((condition) => ({
      ...condition,
      id: stableConditionId(condition.dedupeKey),
    }))
    .sort((left, right) => {
      if (left.current !== right.current) return left.current ? -1 : 1;
      if (severityRank[left.severity] !== severityRank[right.severity]) {
        return severityRank[left.severity] - severityRank[right.severity];
      }
      return (right.provenance.observedAt ?? "").localeCompare(
        left.provenance.observedAt ?? "",
      );
    });
}

function summarize(
  conditions: AttentionCondition[],
  streams: AutonomousWorkstream[],
): AttentionSummary {
  const activeConditions = conditions.filter(
    (condition) => condition.current && condition.classification !== "activity",
  );

  return {
    active: activeConditions.length,
    operatorAction: activeConditions.filter(
      (condition) => condition.classification === "operator-action",
    ).length,
    attention: activeConditions.filter(
      (condition) => condition.classification === "attention",
    ).length,
    running: streams.filter(
      (stream) => normalizeStatus(stream.state) === "RUNNING",
    ).length,
    historical: conditions.filter(
      (condition) => !condition.current || condition.classification === "activity",
    ).length,
  };
}

export async function projectAttention(
  context: AttentionProviderContext,
  providers: AttentionProvider[] = DEFAULT_ATTENTION_PROVIDERS,
): Promise<AttentionProjection> {
  const results = await Promise.all(
    providers.map((provider) => provider.project(context)),
  );
  const conditions = dedupeConditions(
    results.flatMap((result) => result.conditions),
  );
  const workstreamMap = new Map<string, AutonomousWorkstream>();

  for (const stream of results.flatMap((result) => result.workstreams ?? [])) {
    workstreamMap.set(stream.id, stream);
  }

  const projectedWorkstreams = [...workstreamMap.values()].sort((left, right) =>
    (right.updatedAt ?? "").localeCompare(left.updatedAt ?? ""),
  );
  const sources = [
    ...new Set(results.flatMap((result) => result.sources ?? [])),
  ].sort();

  return {
    conditions,
    workstreams: projectedWorkstreams,
    summary: summarize(conditions, projectedWorkstreams),
    sources,
  };
}

export async function readAttentionProjection(
  root: string,
  providers: AttentionProvider[] = DEFAULT_ATTENTION_PROVIDERS,
): Promise<AttentionProjection> {
  const [execution, control, evidence] = await Promise.all([
    readExecutionProjection(root),
    readControlProjection(root),
    readEvidence(root),
  ]);

  return projectAttention(
    {
      root,
      execution,
      control,
      evidence,
    },
    providers,
  );
}
