import { readFile } from "node:fs/promises";
import path from "node:path";

import type {
  CurrentExecutionContext,
  CurrentProductContext,
  MonadObject,
} from "./model";

type WorkPacketPlanningRefs = {
  productGoal?: string;
  epic?: string;
  feature?: string;
};

type ParsedFeature = {
  id: string;
  title: string;
  stories: MonadObject[];
  enablers: MonadObject[];
};

function readBoldField(markdown: string, label: string): string | undefined {
  const expression = new RegExp(
    String.raw`^\*\*${label}:\*\*\s*(.+?)\s*$`,
    "m",
  );

  const match = markdown.match(expression);

  return match?.[1]?.trim();
}

async function readText(root: string, relativePath: string): Promise<string> {
  return readFile(path.join(root, relativePath), "utf8");
}

async function readWorkPacketPlanningRefs(
  root: string,
  workPacketPath: string,
): Promise<WorkPacketPlanningRefs> {
  const markdown = await readText(root, workPacketPath);

  return {
    productGoal: readBoldField(markdown, "Product Goal"),
    epic: readBoldField(markdown, "Epic"),
    feature: readBoldField(markdown, "Feature"),
  };
}

function parseIdentifierAndTitle(
  value: string,
): { id: string; title: string } | undefined {
  const match = value
    .trim()
    .match(/^([A-Z]+(?:-[A-Z]+)*-\d+(?:-\d+)*)\s+(.+)$/);

  if (!match) {
    return undefined;
  }

  return {
    id: match[1],
    title: match[2].trim(),
  };
}

function parseStoryCell(
  value: string,
  source: string,
): {
  stories: MonadObject[];
  enablers: MonadObject[];
} {
  const stories: MonadObject[] = [];
  const enablers: MonadObject[] = [];

  for (const item of value.split(";")) {
    const parsed = parseIdentifierAndTitle(item);

    if (!parsed) {
      continue;
    }

    const object: MonadObject = {
      id: parsed.id,
      type: parsed.id.startsWith("EN-") ? "enabler" : "story",
      title: parsed.title,
      source,
      relationships: [],
    };

    if (object.type === "enabler") {
      enablers.push(object);
    } else {
      stories.push(object);
    }
  }

  return {
    stories,
    enablers,
  };
}

async function findFeature(
  root: string,
  workPacketId: string,
  featureId?: string,
): Promise<ParsedFeature | undefined> {
  const backlogPath = "product/backlog/MVP-BACKLOG.md";
  const markdown = await readText(root, backlogPath);

  for (const line of markdown.split("\n")) {
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

    const [featureCell, packetCell, , storyCell] = cells;

    if (
      packetCell !== workPacketId &&
      !(featureId && featureCell.startsWith(`${featureId} `))
    ) {
      continue;
    }

    const parsedFeature = parseIdentifierAndTitle(featureCell);

    if (!parsedFeature) {
      continue;
    }

    const { stories, enablers } = parseStoryCell(storyCell, backlogPath);

    return {
      id: parsedFeature.id,
      title: parsedFeature.title,
      stories,
      enablers,
    };
  }

  return undefined;
}

async function findEpicTitle(
  root: string,
  epicId: string,
): Promise<string | undefined> {
  const markdown = await readText(root, "product/backlog/MVP-BACKLOG.md");

  for (const line of markdown.split("\n")) {
    if (!line.startsWith(`| ${epicId} `)) {
      continue;
    }

    const firstCell = line.split("|").slice(1, -1)[0]?.trim();

    const parsed = firstCell ? parseIdentifierAndTitle(firstCell) : undefined;

    return parsed?.title;
  }

  return undefined;
}

async function findInitiativeForEpic(
  root: string,
  epicId: string,
): Promise<MonadObject | undefined> {
  const source = "product/initiatives.md";
  const markdown = await readText(root, source);

  const headings = [...markdown.matchAll(/^## (INIT-\d+) — (.+)$/gm)];

  for (let index = 0; index < headings.length; index += 1) {
    const heading = headings[index];
    const start = heading.index ?? 0;
    const end = headings[index + 1]?.index ?? markdown.length;

    const section = markdown.slice(start, end);

    if (!section.includes(`\`${epicId}\``)) {
      continue;
    }

    return {
      id: heading[1],
      type: "initiative",
      title: heading[2].trim(),
      source,
      relationships: [
        {
          type: "CONTAINS",
          target: epicId,
        },
      ],
    };
  }

  return undefined;
}

async function readProductGoal(
  root: string,
  productGoalId: string,
): Promise<MonadObject> {
  if (productGoalId === "PG-001") {
    const source = "product/PRODUCT-GOAL.md";
    const markdown = await readText(root, source);

    const heading = markdown.match(/^# Product Goal — (.+)$/m);

    return {
      id: productGoalId,
      type: "product-goal",
      title: heading?.[1]?.trim() ?? productGoalId,
      source,
      relationships: [],
    };
  }

  return {
    id: productGoalId,
    type: "product-goal",
    title: productGoalId,
    source: "product/POST-MVP-PRODUCT-GOALS.md",
    relationships: [],
  };
}

export async function readCurrentProductContext(
  root: string,
  execution: CurrentExecutionContext,
): Promise<CurrentProductContext> {
  const workPacket = execution.workPacket;

  if (!workPacket?.artifactPath) {
    return {
      stories: [],
      enablers: [],
    };
  }

  const refs = await readWorkPacketPlanningRefs(root, workPacket.artifactPath);

  const feature = await findFeature(root, workPacket.id, refs.feature);

  const initiative = refs.epic
    ? await findInitiativeForEpic(root, refs.epic)
    : undefined;

  const epicTitle = refs.epic
    ? await findEpicTitle(root, refs.epic)
    : undefined;

  const productGoal = refs.productGoal
    ? await readProductGoal(root, refs.productGoal)
    : undefined;

  const epic =
    refs.epic !== undefined
      ? {
          id: refs.epic,
          type: "epic" as const,
          title: epicTitle ?? refs.epic,
          source: "product/backlog/MVP-BACKLOG.md",
          relationships: feature
            ? [
                {
                  type: "CONTAINS",
                  target: feature.id,
                },
              ]
            : [],
        }
      : undefined;

  const featureObject =
    feature !== undefined
      ? {
          id: feature.id,
          type: "feature" as const,
          title: feature.title,
          source: "product/backlog/MVP-BACKLOG.md",
          relationships: [
            {
              type: "REALIZED_THROUGH",
              target: workPacket.id,
            },
            ...feature.stories.map((story) => ({
              type: "CONTAINS",
              target: story.id,
            })),
            ...feature.enablers.map((enabler) => ({
              type: "CONTAINS",
              target: enabler.id,
            })),
          ],
        }
      : undefined;

  return {
    productGoal,
    initiative,
    epic,
    feature: featureObject,
    stories: feature?.stories ?? [],
    enablers: feature?.enablers ?? [],
  };
}
