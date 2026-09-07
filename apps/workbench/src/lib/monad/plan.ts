import { readFile } from "node:fs/promises";
import path from "node:path";

export type PlanStoryKind = "story" | "enabler";

export type PlanStory = {
  id: string;
  title: string;
  kind: PlanStoryKind;
};

export type PlanFeature = {
  id: string;
  title: string;
  workPacket?: string;
  workCycle?: string;
  stories: PlanStory[];
  source: string;
};

export type PlanEpic = {
  id: string;
  title: string;
  features: PlanFeature[];
};

export type PlanInitiative = {
  id: string;
  title: string;
  outcome?: string;
  exitCondition?: string;
  epics: PlanEpic[];
};

export type PlanProductGoal = {
  id: string;
  title: string;
  initiatives: PlanInitiative[];
};

export type PlanCounts = {
  productGoals: number;
  initiatives: number;
  epics: number;
  features: number;
  stories: number;
  enablers: number;
};

export type PlanProjection = {
  goals: PlanProductGoal[];
  counts: PlanCounts;
  sources: string[];
};

type ParsedFeature = PlanFeature & {
  epicId: string;
};

const PLAN_SOURCES = [
  "product/initiatives.md",
  "product/backlog/MVP-BACKLOG.md",
  "product/backlog/EXPANDED-BACKLOG.md",
] as const;

function resolveRepositoryPath(root: string, relativePath: string): string {
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
    throw new Error(`Plan source escapes repository root: ${relativePath}`);
  }

  return candidate;
}

async function readSource(root: string, relativePath: string): Promise<string> {
  return readFile(resolveRepositoryPath(root, relativePath), "utf8");
}

function readBoldField(section: string, label: string): string | undefined {
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  return section
    .match(new RegExp(String.raw`^\*\*${escaped}:\*\*\s*(.+?)\s*$`, "m"))?.[1]
    ?.trim();
}

function readSectionBody(section: string, heading: string): string | undefined {
  const lines = section.split(/\r?\n/);

  const start = lines.findIndex((line) => line.trim() === `### ${heading}`);

  if (start === -1) {
    return undefined;
  }

  const body: string[] = [];

  for (let index = start + 1; index < lines.length; index += 1) {
    const line = lines[index];

    if (
      line.startsWith("### ") ||
      line.startsWith("## ") ||
      line.startsWith("# ")
    ) {
      break;
    }

    body.push(line);
  }

  const value = body.join("\n").trim();

  return value || undefined;
}

function parseEpicList(initiativeSection: string): PlanEpic[] {
  const epicsSection = readSectionBody(initiativeSection, "Epics");

  if (!epicsSection) {
    return [];
  }

  const epics: PlanEpic[] = [];

  for (const line of epicsSection.split(/\r?\n/)) {
    const match = line.trim().match(/^-\s+`(EPIC-\d+)`\s+[—–-]\s+(.+)$/);

    if (!match) {
      continue;
    }

    epics.push({
      id: match[1],
      title: match[2].trim(),
      features: [],
    });
  }

  return epics;
}

function parseInitiativeCatalog(markdown: string): PlanProductGoal[] {
  const goalMatches = [...markdown.matchAll(/^# (PG-\d+) — (.+)$/gm)];

  const goals: PlanProductGoal[] = [];

  for (let goalIndex = 0; goalIndex < goalMatches.length; goalIndex += 1) {
    const goalMatch = goalMatches[goalIndex];

    const goalStart = goalMatch.index ?? 0;

    const goalEnd = goalMatches[goalIndex + 1]?.index ?? markdown.length;

    const goalSection = markdown.slice(goalStart, goalEnd);

    const initiativeMatches = [
      ...goalSection.matchAll(/^## (INIT-\d+) — (.+)$/gm),
    ];

    const initiatives: PlanInitiative[] = [];

    for (
      let initiativeIndex = 0;
      initiativeIndex < initiativeMatches.length;
      initiativeIndex += 1
    ) {
      const initiativeMatch = initiativeMatches[initiativeIndex];

      const start = initiativeMatch.index ?? 0;

      const end =
        initiativeMatches[initiativeIndex + 1]?.index ?? goalSection.length;

      const initiativeSection = goalSection.slice(start, end);

      initiatives.push({
        id: initiativeMatch[1],
        title: initiativeMatch[2].trim(),
        outcome: readBoldField(initiativeSection, "Outcome"),
        exitCondition: readSectionBody(initiativeSection, "Exit condition"),
        epics: parseEpicList(initiativeSection),
      });
    }

    goals.push({
      id: goalMatch[1],
      title: goalMatch[2].trim(),
      initiatives,
    });
  }

  return goals;
}

function parseStoryCell(value: string): PlanStory[] {
  const stories: PlanStory[] = [];

  for (const rawItem of value.split(";")) {
    const item = rawItem.trim();

    const match = item.match(/^((?:US|EN)-\d+)\s+(.+)$/);

    if (!match) {
      continue;
    }

    stories.push({
      id: match[1],
      title: match[2].trim(),
      kind: match[1].startsWith("EN-") ? "enabler" : "story",
    });
  }

  return stories;
}

function parseFeatureCell(value: string):
  | {
      id: string;
      title: string;
      epicId: string;
    }
  | undefined {
  const match = value.match(/^(F-(\d{3})-\d{2})\s+(.+)$/);

  if (!match) {
    return undefined;
  }

  return {
    id: match[1],
    epicId: `EPIC-${match[2]}`,
    title: match[3].trim(),
  };
}

function parseFeatureBacklog(
  markdown: string,
  source: string,
): ParsedFeature[] {
  const features: ParsedFeature[] = [];

  for (const line of markdown.split(/\r?\n/)) {
    if (!line.startsWith("|")) {
      continue;
    }

    const cells = line
      .split("|")
      .slice(1, -1)
      .map((cell) => cell.trim());

    if (cells.length < 4) {
      continue;
    }

    const [featureCell, workPacketCell, workCycleCell, storyCell] = cells;

    const feature = parseFeatureCell(featureCell);

    if (!feature) {
      continue;
    }

    features.push({
      id: feature.id,
      title: feature.title,
      epicId: feature.epicId,
      workPacket: /^WP-/.test(workPacketCell) ? workPacketCell : undefined,
      workCycle: /^WC-/.test(workCycleCell) ? workCycleCell : undefined,
      stories: parseStoryCell(storyCell),
      source,
    });
  }

  return features;
}

function attachFeatures(
  goals: PlanProductGoal[],
  features: ParsedFeature[],
): void {
  const epicIndex = new Map<string, PlanEpic>();

  for (const goal of goals) {
    for (const initiative of goal.initiatives) {
      for (const epic of initiative.epics) {
        epicIndex.set(epic.id, epic);
      }
    }
  }

  for (const feature of features) {
    const epic = epicIndex.get(feature.epicId);

    if (!epic) {
      continue;
    }

    epic.features.push({
      id: feature.id,
      title: feature.title,
      workPacket: feature.workPacket,
      workCycle: feature.workCycle,
      stories: feature.stories,
      source: feature.source,
    });
  }
}

function countProjection(goals: PlanProductGoal[]): PlanCounts {
  let initiatives = 0;
  let epics = 0;
  let features = 0;
  let stories = 0;
  let enablers = 0;

  for (const goal of goals) {
    initiatives += goal.initiatives.length;

    for (const initiative of goal.initiatives) {
      epics += initiative.epics.length;

      for (const epic of initiative.epics) {
        features += epic.features.length;

        for (const feature of epic.features) {
          for (const story of feature.stories) {
            if (story.kind === "enabler") {
              enablers += 1;
            } else {
              stories += 1;
            }
          }
        }
      }
    }
  }

  return {
    productGoals: goals.length,
    initiatives,
    epics,
    features,
    stories,
    enablers,
  };
}

export async function readPlanProjection(
  root: string,
): Promise<PlanProjection> {
  const [initiativesMarkdown, mvpBacklog, expandedBacklog] = await Promise.all([
    readSource(root, PLAN_SOURCES[0]),
    readSource(root, PLAN_SOURCES[1]),
    readSource(root, PLAN_SOURCES[2]),
  ]);

  const goals = parseInitiativeCatalog(initiativesMarkdown);

  const features = [
    ...parseFeatureBacklog(mvpBacklog, PLAN_SOURCES[1]),
    ...parseFeatureBacklog(expandedBacklog, PLAN_SOURCES[2]),
  ];

  attachFeatures(goals, features);

  return {
    goals,
    counts: countProjection(goals),
    sources: [...PLAN_SOURCES],
  };
}
