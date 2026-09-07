import { readFile } from "node:fs/promises";
import path from "node:path";

import { parseTsv } from "./tsv";

export type ChangeRequestItem = {
  id: string;
  path: string;
  target: string;
  summary: string;
  status: string;
  created: string;
  updated: string;
};

export type DecisionItem = {
  timestamp: string;
  target: string;
  action: string;
  outcome: string;
  actor: string;
  reason: string;
};

export type ControlArtifactItem = {
  id: string;
  path: string;
  title: string;
  type: string;
  authority: string;
  status?: string;
};

export type ReleaseItem = {
  id: string;
  path: string;
  version: string;
  status: string;
  created: string;
  updated: string;
};

export type VerificationSummary = {
  total: number;
  current: number;
  passed: number;
  failed: number;
  skipped: number;
};

export type ConsistencyFinding = {
  id: string;
  severity: "info" | "warning";
  title: string;
  detail: string;
  canonicalSource: string;
  comparedSource: string;
};

export type ControlProjection = {
  changes: ChangeRequestItem[];
  decisions: DecisionItem[];
  risks: ControlArtifactItem[];
  reviews: ControlArtifactItem[];
  releases: ReleaseItem[];
  verification: VerificationSummary;
  findings: ConsistencyFinding[];
  sources: string[];
};

type ArtifactRow = {
  artifact_id: string;
  path: string;
  type: string;
  authority: string;
};

type ChangeRequestRow = ChangeRequestItem;
type DecisionRow = DecisionItem;
type ReleaseRow = ReleaseItem;

type EvidenceRow = {
  id: string;
  status: string;
  result: string;
};

type CurrentEntity = {
  id: string;
  lifecycle_state?: string;
};

type CurrentState = {
  entities?: {
    WP?: Record<string, CurrentEntity>;
  };
};

const RISK_REGISTER_SOURCE = "engineering/risks/risk-register.md";
const SOURCES = [
  ".eos/change-requests.tsv",
  ".eos/decisions.tsv",
  ".eos/artifacts.tsv",
  ".eos/releases.tsv",
  ".eos/evidence.tsv",
  ".eos/state/current.json",
  "engineering/project-status.md",
  RISK_REGISTER_SOURCE,
] as const;

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
): Promise<string> {
  try {
    return await readSource(root, relativePath);
  } catch {
    return "";
  }
}

function humanizePath(relativePath: string): string {
  return path
    .basename(relativePath)
    .replace(/\.(?:md|mdx|json|ya?ml|toml)$/i, "")
    .replace(/[-_]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/^./, (character) => character.toUpperCase());
}

function artifactItem(row: ArtifactRow): ControlArtifactItem {
  return {
    id: row.artifact_id,
    path: row.path,
    title: humanizePath(row.path) || row.artifact_id,
    type: row.type,
    authority: row.authority,
  };
}

function parseRiskRegister(markdown: string): ControlArtifactItem[] {
  const risks: ControlArtifactItem[] = [];

  for (const line of markdown.split(/\r?\n/)) {
    const match = line.match(
      /^\|\s*(R-\d+)\s*\|\s*([^|]+?)\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*\d+\s*\|[^|]*\|[^|]*\|\s*([^|]+?)\s*\|$/,
    );

    if (!match) {
      continue;
    }

    risks.push({
      id: match[1],
      path: RISK_REGISTER_SOURCE,
      title: match[2].trim(),
      type: "risk",
      authority: "risk-register-authoritative",
      status: match[3].trim(),
    });
  }

  return risks;
}

function verificationSummary(rows: EvidenceRow[]): VerificationSummary {
  return rows.reduce<VerificationSummary>(
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
      current: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
    },
  );
}

function selectCurrentWorkPacket(
  state: CurrentState,
): CurrentEntity | undefined {
  const packets = Object.values(state.entities?.WP ?? {});

  for (const lifecycleState of ["IN_PROGRESS", "AUTHORIZED", "READY"]) {
    const match = packets.find(
      (packet) => packet.lifecycle_state === lifecycleState,
    );

    if (match) {
      return match;
    }
  }

  return undefined;
}

function normalizeLifecycleNarrative(value: string): string {
  return value.toUpperCase().replace(/[ -]+/g, "_");
}

function consistencyFindings(
  projectStatus: string,
  currentState: CurrentState,
): ConsistencyFinding[] {
  const findings: ConsistencyFinding[] = [];
  const narrativePacket = projectStatus.match(
    /^\*\*Current packet:\*\*\s+([A-Z0-9-]+)\s+—\s+(.+)$/m,
  );
  const canonicalPacket = selectCurrentWorkPacket(currentState);

  if (!narrativePacket || !canonicalPacket) {
    return findings;
  }

  const [, narrativeId, narrative] = narrativePacket;

  if (narrativeId !== canonicalPacket.id) {
    findings.push({
      id: "CTRL-DRIFT-001",
      severity: "warning",
      title:
        "Narrative current packet differs from canonical EOS current state",
      detail: `${narrativeId} is named as current in engineering/project-status.md, while .eos/state/current.json selects ${canonicalPacket.id} as the current governed Work Packet. Canonical EOS current state wins.`,
      canonicalSource: ".eos/state/current.json",
      comparedSource: "engineering/project-status.md",
    });

    return findings;
  }

  const canonicalLifecycle = canonicalPacket.lifecycle_state;

  if (
    canonicalLifecycle &&
    !normalizeLifecycleNarrative(narrative).includes(
      normalizeLifecycleNarrative(canonicalLifecycle),
    )
  ) {
    findings.push({
      id: "CTRL-DRIFT-001",
      severity: "warning",
      title: "Narrative project status lags canonical EOS lifecycle state",
      detail: `${canonicalPacket.id} is ${canonicalLifecycle} in .eos/state/current.json, while engineering/project-status.md currently says “${narrative.trim()}”. Canonical EOS current state wins.`,
      canonicalSource: ".eos/state/current.json",
      comparedSource: "engineering/project-status.md",
    });
  }

  return findings;
}

export async function readControlProjection(
  root: string,
): Promise<ControlProjection> {
  const [
    changesRaw,
    decisionsRaw,
    artifactsRaw,
    releasesRaw,
    evidenceRaw,
    currentStateRaw,
    projectStatus,
    riskRegister,
  ] = await Promise.all([
    ...SOURCES.slice(0, -1).map((source) => readSource(root, source)),
    readOptionalSource(root, RISK_REGISTER_SOURCE),
  ]);

  const changes = parseTsv<ChangeRequestRow>(changesRaw);
  const decisions = parseTsv<DecisionRow>(decisionsRaw).sort((left, right) =>
    right.timestamp.localeCompare(left.timestamp),
  );
  const artifacts = parseTsv<ArtifactRow>(artifactsRaw);
  const releases = parseTsv<ReleaseRow>(releasesRaw);
  const evidence = parseTsv<EvidenceRow>(evidenceRaw);
  const currentState = JSON.parse(currentStateRaw) as CurrentState;

  const reviews = artifacts
    .filter((row) => row.type === "review" || /review/i.test(row.artifact_id))
    .map(artifactItem);

  const riskById = new Map(
    parseRiskRegister(riskRegister).map((risk) => [risk.id, risk]),
  );

  for (const row of artifacts.filter(
    (artifact) =>
      /risk/i.test(artifact.type) ||
      /risk/i.test(artifact.artifact_id) ||
      /(?:^|\/)risks?(?:\/|$)/i.test(artifact.path),
  )) {
    const item = artifactItem(row);
    const canonical = riskById.get(item.id);
    riskById.set(item.id, canonical ? { ...item, ...canonical } : item);
  }

  return {
    changes,
    decisions,
    risks: [...riskById.values()].sort((left, right) =>
      left.id.localeCompare(right.id, undefined, { numeric: true }),
    ),
    reviews,
    releases,
    verification: verificationSummary(evidence),
    findings: consistencyFindings(projectStatus, currentState),
    sources: [...SOURCES],
  };
}
