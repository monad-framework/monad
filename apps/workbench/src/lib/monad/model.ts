import type { AttentionSummary } from "./attention-model";

export type ProductObjectType =
  | "product-goal"
  | "initiative"
  | "epic"
  | "feature"
  | "story"
  | "enabler"
  | "task";

export type ExecutionObjectType =
  | "program-increment"
  | "work-cycle"
  | "work-packet"
  | "execution";

export type KnowledgeObjectType =
  | "requirement"
  | "specification"
  | "adr"
  | "policy"
  | "review"
  | "risk"
  | "change-request"
  | "evidence"
  | "release";

export type MonadObjectType =
  | ProductObjectType
  | ExecutionObjectType
  | KnowledgeObjectType;

export type MonadRelationship = {
  type: string;
  target: string;
};

export type MonadObject = {
  id: string;
  type: MonadObjectType;
  title: string;
  status?: string;
  description?: string;
  authority?: string;
  source: string;
  artifactPath?: string;
  relationships: MonadRelationship[];
};

export type CurrentProductContext = {
  productGoal?: MonadObject;
  initiative?: MonadObject;
  epic?: MonadObject;
  feature?: MonadObject;
  stories: MonadObject[];
  enablers: MonadObject[];
};

export type CurrentExecutionContext = {
  programIncrement?: MonadObject;
  workCycle?: MonadObject;
  workPacket?: MonadObject;
};

export type RepositorySource = {
  label: string;
  path: string;
  fileCount: number;
};

export type GitStatusEntry = {
  status: string;
  path: string;
};

export type KnowledgeReferenceKind =
  | "requirement"
  | "quality-requirement"
  | "adr"
  | "interface"
  | "data"
  | "technical"
  | "work-packet"
  | "change-request"
  | "other";

export type KnowledgeReference = {
  id: string;
  kind: KnowledgeReferenceKind;
  relationship: string;
  path?: string;
  source: string;
};

export type AcceptanceCriterion = {
  text: string;
  complete: boolean;
};

export type EvidenceRecord = {
  id: string;
  path: string;
  status: string;
  result: string;
  validator: string;
  kind: string;
};

export type ExecutionRecord = {
  id: string;
  path: string;
  status: string;
  actor: string;
  branch: string;
};

export type CurrentKnowledgeContext = {
  governing: KnowledgeReference[];
  dependencies: KnowledgeReference[];
  incoming: KnowledgeReference[];
  acceptanceCriteria: AcceptanceCriterion[];
  evidence: EvidenceRecord[];
  executions: ExecutionRecord[];
};

export type FocusContext = {
  requestedId?: string;
  object?: MonadObject;
  document?: FocusDocument;
  knowledge?: CurrentKnowledgeContext;
  incoming: KnowledgeReference[];
  outgoing: KnowledgeReference[];
};

export type RepositorySnapshot = {
  rootPath: string;
  branch: string;
  version: string | null;

  product: CurrentProductContext;
  execution: CurrentExecutionContext;
  knowledge: CurrentKnowledgeContext;
  focus: FocusContext;
  attention: AttentionSummary;

  sources: RepositorySource[];
  gitStatus: GitStatusEntry[];
};

export type FocusDocumentMetadata = {
  label: string;
  value: string;
};

export type FocusDocumentSection = {
  id: string;
  title: string;
  body: string;
};

export type FocusDocument = {
  heading?: string;
  introduction?: string;
  metadata: FocusDocumentMetadata[];
  sections: FocusDocumentSection[];
  sourcePath: string;
};
