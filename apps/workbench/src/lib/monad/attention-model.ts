export type AttentionClassification =
  | "activity"
  | "attention"
  | "operator-action";

export type AttentionState =
  | "HUMAN_ACTION_REQUIRED"
  | "BLOCKED"
  | "FAILED"
  | "READY_FOR_INTEGRATION"
  | "RUNNING"
  | "COMPLETED"
  | "STALE"
  | "DRIFTED"
  | "INFORMATIONAL";

export type AttentionSeverity = "info" | "warning" | "critical";

export type AttentionFreshness = "current" | "historical" | "unknown";

export type AttentionAffectedObject = {
  id: string;
  type: string;
  title?: string;
  href?: string;
};

export type AttentionProvenance = {
  provider: string;
  source: string;
  sourceKind: string;
  observedAt?: string;
};

export type AttentionAction = {
  kind: "navigate";
  label: string;
  href: string;
};

export type AttentionCondition = {
  id: string;
  dedupeKey: string;
  classification: AttentionClassification;
  state: AttentionState;
  severity: AttentionSeverity;
  title: string;
  reason: string;
  affectedObject: AttentionAffectedObject;
  provenance: AttentionProvenance;
  current: boolean;
  freshness: AttentionFreshness;
  action?: AttentionAction;
};

export type AutonomousWorkstream = {
  id: string;
  group: string;
  label: string;
  objectId: string;
  objectHref: string;
  state: string;
  reason: string;
  source: string;
  updatedAt?: string;
  latestExecutionId?: string;
  authorization?: "GRANTED" | "NOT_GRANTED";
  current: boolean;
};

export type AttentionSummary = {
  active: number;
  operatorAction: number;
  attention: number;
  running: number;
  historical: number;
};

export type AttentionProjection = {
  conditions: AttentionCondition[];
  workstreams: AutonomousWorkstream[];
  summary: AttentionSummary;
  sources: string[];
};
