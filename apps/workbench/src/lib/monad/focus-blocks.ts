import type {
  AcceptanceCriterion,
  FocusDocument,
  FocusDocumentSection,
  KnowledgeReference,
  RepositorySnapshot,
} from "./model";

export type FocusProjectionBlockKind =
  | "summary"
  | "context"
  | "decision"
  | "consequences"
  | "authority"
  | "dependencies"
  | "acceptance"
  | "lifecycle"
  | "execution"
  | "validation"
  | "implementation"
  | "document";

export type FocusProjectionField = {
  label: string;
  value: string;
};

export type FocusProjectionBlock = {
  id: string;
  kind: FocusProjectionBlockKind;
  eyebrow: string;
  title: string;
  body?: string;
  references?: KnowledgeReference[];
  criteria?: AcceptanceCriterion[];
  fields?: FocusProjectionField[];
};

function normalizeHeading(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim();
}

function sectionMap(
  document: FocusDocument | undefined,
): Map<string, FocusDocumentSection> {
  return new Map(
    (document?.sections ?? []).map((section) => [
      normalizeHeading(section.title),
      section,
    ]),
  );
}

function findMetadata(
  document: FocusDocument | undefined,
  label: string,
): string | undefined {
  const normalized = normalizeHeading(label);

  return document?.metadata.find(
    (field) => normalizeHeading(field.label) === normalized,
  )?.value;
}

function parseChecklist(body: string | undefined): AcceptanceCriterion[] {
  if (!body) {
    return [];
  }

  return body
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

function classifyDocumentSection(
  section: FocusDocumentSection,
): FocusProjectionBlockKind {
  const heading = normalizeHeading(section.title);

  if (
    heading === "context" ||
    heading === "background" ||
    heading === "problem"
  ) {
    return "context";
  }

  if (heading === "decision" || heading === "decision outcome") {
    return "decision";
  }

  if (heading === "consequences" || heading === "consequence") {
    return "consequences";
  }

  if (heading.includes("implementation")) {
    return "implementation";
  }

  if (heading === "validation" || heading.includes("verification")) {
    return "validation";
  }

  if (
    heading === "status" ||
    heading.includes("lifecycle") ||
    heading.includes("authorization")
  ) {
    return "lifecycle";
  }

  return "document";
}

function eyebrowForKind(kind: FocusProjectionBlockKind): string {
  switch (kind) {
    case "summary":
      return "Purpose";

    case "context":
      return "Context";

    case "decision":
      return "Decision";

    case "consequences":
      return "Impact";

    case "authority":
      return "Governance";

    case "dependencies":
      return "Prerequisites";

    case "acceptance":
      return "Acceptance";

    case "lifecycle":
      return "State";

    case "execution":
      return "Evidence";

    case "validation":
      return "Verification";

    case "implementation":
      return "Implementation";

    default:
      return "Artifact block";
  }
}

function isCurrentWorkPacket(snapshot: RepositorySnapshot): boolean {
  const focus = snapshot.focus.object;

  const current = snapshot.execution.workPacket;

  return Boolean(focus && current && focus.id === current.id);
}

function buildCurrentWorkPacketBlocks(
  snapshot: RepositorySnapshot,
): FocusProjectionBlock[] {
  const blocks: FocusProjectionBlock[] = [];

  const document = snapshot.focus.document;

  const sections = sectionMap(document);

  const objective = sections.get("objective");

  if (objective?.body || document?.introduction) {
    blocks.push({
      id: "summary",
      kind: "summary",
      eyebrow: "Purpose",
      title: "Objective",
      body: objective?.body ?? document?.introduction,
    });
  }

  if (snapshot.knowledge.governing.length > 0) {
    blocks.push({
      id: "governing-authority",
      kind: "authority",
      eyebrow: "Governance",
      title: "Governing authority",
      references: snapshot.knowledge.governing,
    });
  }

  if (snapshot.knowledge.dependencies.length > 0) {
    blocks.push({
      id: "dependencies",
      kind: "dependencies",
      eyebrow: "Prerequisites",
      title: "Dependencies",
      references: snapshot.knowledge.dependencies,
    });
  }

  const acceptanceFromModel = snapshot.knowledge.acceptanceCriteria;

  const acceptanceFromDocument = parseChecklist(
    sections.get("acceptance criteria")?.body,
  );

  const acceptance =
    acceptanceFromModel.length > 0
      ? acceptanceFromModel
      : acceptanceFromDocument;

  if (acceptance.length > 0) {
    blocks.push({
      id: "acceptance",
      kind: "acceptance",
      eyebrow: "Acceptance",
      title: "Acceptance criteria",
      criteria: acceptance,
    });
  }

  const canonicalStatus = snapshot.focus.object?.status;

  const documentStatus = findMetadata(document, "Status");

  const authorizationDisposition = sections.get(
    "authorization disposition",
  )?.body;

  const lifecycleFields: FocusProjectionField[] = [];

  if (canonicalStatus) {
    lifecycleFields.push({
      label: "Canonical lifecycle",
      value: canonicalStatus,
    });
  }

  if (documentStatus) {
    lifecycleFields.push({
      label: "Artifact status",
      value: documentStatus,
    });
  }

  lifecycleFields.push({
    label: "Lifecycle authority",
    value: ".eos/state/current.json",
  });

  let lifecycleBody: string | undefined;

  if (canonicalStatus && documentStatus && canonicalStatus !== documentStatus) {
    lifecycleBody = [
      "Canonical EOS state and artifact metadata do not currently match.",
      "Workbench treats canonical EOS current state as authoritative for lifecycle projection.",
      authorizationDisposition,
    ]
      .filter(Boolean)
      .join("\n\n");
  } else if (authorizationDisposition) {
    lifecycleBody = authorizationDisposition;
  } else if (canonicalStatus) {
    lifecycleBody =
      "Canonical EOS lifecycle state and the current focus projection are aligned.";
  }

  if (lifecycleFields.length > 0 || lifecycleBody) {
    blocks.push({
      id: "lifecycle",
      kind: "lifecycle",
      eyebrow: "State",
      title: "Lifecycle reconciliation",
      body: lifecycleBody,
      fields: lifecycleFields,
    });
  }

  const executionCount = snapshot.knowledge.executions.length;

  const evidenceCount = snapshot.knowledge.evidence.length;

  blocks.push({
    id: "execution-evidence",
    kind: "execution",
    eyebrow: "Evidence",
    title: "Execution and verification",
    body:
      executionCount === 0 && evidenceCount === 0
        ? "No execution or verification evidence is currently registered for this Work Packet."
        : undefined,
    fields: [
      {
        label: "Executions",
        value: String(executionCount),
      },
      {
        label: "Evidence records",
        value: String(evidenceCount),
      },
    ],
  });

  const consumedSections = new Set([
    "objective",
    "governing authority",
    "dependencies",
    "acceptance criteria",
    "authorization disposition",
  ]);

  for (const section of document?.sections ?? []) {
    const normalized = normalizeHeading(section.title);

    if (consumedSections.has(normalized)) {
      continue;
    }

    const kind = classifyDocumentSection(section);

    blocks.push({
      id: section.id,
      kind,
      eyebrow: eyebrowForKind(kind),
      title: section.title,
      body: section.body || undefined,
    });
  }

  return blocks;
}

function buildGenericFocusBlocks(
  snapshot: RepositorySnapshot,
): FocusProjectionBlock[] {
  const document = snapshot.focus.document;

  const blocks: FocusProjectionBlock[] = [];

  if (document?.introduction) {
    blocks.push({
      id: "summary",
      kind: "summary",
      eyebrow: "Purpose",
      title: "Summary",
      body: document.introduction,
    });
  }

  for (const section of document?.sections ?? []) {
    const kind = classifyDocumentSection(section);

    const criteria =
      normalizeHeading(section.title) === "acceptance criteria"
        ? parseChecklist(section.body)
        : [];

    if (criteria.length > 0) {
      blocks.push({
        id: section.id,
        kind: "acceptance",
        eyebrow: "Acceptance",
        title: section.title,
        criteria,
      });

      continue;
    }

    blocks.push({
      id: section.id,
      kind,
      eyebrow: eyebrowForKind(kind),
      title: section.title,
      body: section.body || undefined,
    });
  }

  return blocks;
}

export function buildFocusProjectionBlocks(
  snapshot: RepositorySnapshot,
): FocusProjectionBlock[] {
  if (isCurrentWorkPacket(snapshot)) {
    return buildCurrentWorkPacketBlocks(snapshot);
  }

  return buildGenericFocusBlocks(snapshot);
}
