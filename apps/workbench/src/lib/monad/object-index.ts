import { readControlProjection } from "./control";
import { readExecutionProjection } from "./execution";
import { readKnowledgeCatalogProjection } from "./knowledge-catalog";
import type { MonadObjectType } from "./model";
import { readPlanProjection } from "./plan";

export type WorkbenchIndexItem = {
  id: string;
  type: MonadObjectType;
  title: string;
  description?: string;
  status?: string;
  authority?: string;
  source: string;
  artifactPath?: string;
};

export type WorkbenchObjectIndex = {
  items: WorkbenchIndexItem[];
};

function pushUnique(
  target: Map<string, WorkbenchIndexItem>,
  item: WorkbenchIndexItem,
): void {
  const existing = target.get(item.id);

  if (!existing) {
    target.set(item.id, item);
    return;
  }

  target.set(item.id, {
    ...existing,
    ...item,
    description: item.description ?? existing.description,
    status: item.status ?? existing.status,
    authority: item.authority ?? existing.authority,
    artifactPath: item.artifactPath ?? existing.artifactPath,
  });
}

export async function readWorkbenchObjectIndex(
  root: string,
): Promise<WorkbenchObjectIndex> {
  const [plan, execution, knowledge, control] = await Promise.all([
    readPlanProjection(root),
    readExecutionProjection(root),
    readKnowledgeCatalogProjection(root),
    readControlProjection(root),
  ]);

  const items = new Map<string, WorkbenchIndexItem>();

  for (const goal of plan.goals) {
    pushUnique(items, {
      id: goal.id,
      type: "product-goal",
      title: goal.title,
      source: "product/initiatives.md",
    });

    for (const initiative of goal.initiatives) {
      pushUnique(items, {
        id: initiative.id,
        type: "initiative",
        title: initiative.title,
        description: initiative.outcome,
        source: "product/initiatives.md",
      });

      for (const epic of initiative.epics) {
        pushUnique(items, {
          id: epic.id,
          type: "epic",
          title: epic.title,
          source: "product/initiatives.md",
        });

        for (const feature of epic.features) {
          pushUnique(items, {
            id: feature.id,
            type: "feature",
            title: feature.title,
            source: feature.source,
          });

          for (const story of feature.stories) {
            pushUnique(items, {
              id: story.id,
              type: story.kind,
              title: story.title,
              source: feature.source,
            });
          }
        }
      }
    }
  }

  for (const program of execution.programIncrements) {
    pushUnique(items, {
      id: program.id,
      type: "program-increment",
      title: program.title,
      status: program.status,
      source: ".eos/state/current.json",
      artifactPath: program.path,
    });

    for (const cycle of program.workCycles) {
      pushUnique(items, {
        id: cycle.id,
        type: "work-cycle",
        title: cycle.title,
        status: cycle.status,
        source: ".eos/state/current.json",
        artifactPath: cycle.path,
      });

      for (const packet of cycle.workPackets) {
        pushUnique(items, {
          id: packet.id,
          type: "work-packet",
          title: packet.title,
          description: `${packet.domain || "Unclassified"} · ${packet.executions.length} executions · ${packet.evidence.total} evidence records`,
          status: packet.status,
          source: ".eos/state/current.json",
          artifactPath: packet.path,
        });

        for (const run of packet.executions) {
          pushUnique(items, {
            id: run.id,
            type: "execution",
            title: `${run.actor || "unknown actor"} · ${run.branch || packet.title}`,
            description: `Execution targeting ${packet.id}`,
            status: run.status,
            source: ".eos/state/current.json",
            artifactPath: run.path,
          });
        }
      }
    }
  }

  for (const requirement of knowledge.requirements) {
    pushUnique(items, {
      id: requirement.id,
      type: "requirement",
      title: requirement.title,
      description: requirement.summary,
      authority: requirement.authority,
      source: requirement.path,
    });
  }

  for (const specification of knowledge.specifications) {
    pushUnique(items, {
      id: specification.id,
      type: "specification",
      title: specification.title,
      authority: specification.authority,
      source: specification.path,
      artifactPath: specification.path,
    });
  }

  for (const adr of knowledge.adrs) {
    pushUnique(items, {
      id: adr.id,
      type: "adr",
      title: adr.title,
      authority: adr.authority,
      source: adr.path,
      artifactPath: adr.path,
    });
  }

  for (const policy of knowledge.policies) {
    pushUnique(items, {
      id: policy.id,
      type: "policy",
      title: policy.title,
      authority: policy.authority,
      source: policy.path,
      artifactPath: policy.path,
    });
  }

  for (const evidence of knowledge.evidence) {
    pushUnique(items, {
      id: evidence.id,
      type: "evidence",
      title: evidence.title,
      description: evidence.target
        ? `Evidence for ${evidence.target}`
        : undefined,
      status: evidence.status,
      authority: evidence.authority,
      source: evidence.path,
      artifactPath: evidence.path,
    });
  }

  for (const change of control.changes) {
    pushUnique(items, {
      id: change.id,
      type: "change-request",
      title: change.summary,
      description: `Change request targeting ${change.target}`,
      status: change.status,
      source: change.path,
      artifactPath: change.path,
    });
  }

  for (const review of control.reviews) {
    pushUnique(items, {
      id: review.id,
      type: "review",
      title: review.title,
      authority: review.authority,
      source: review.path,
      artifactPath: review.path,
    });
  }

  for (const risk of control.risks) {
    pushUnique(items, {
      id: risk.id,
      type: "risk",
      title: risk.title,
      status: risk.status,
      authority: risk.authority,
      source: risk.path,
      artifactPath: risk.path,
    });
  }

  for (const release of control.releases) {
    pushUnique(items, {
      id: release.id,
      type: "release",
      title: release.version || release.id,
      description: `Release ${release.version || release.id}`,
      status: release.status,
      source: ".eos/releases.tsv",
      artifactPath: release.path,
    });
  }

  return {
    items: [...items.values()].sort((left, right) =>
      left.id.localeCompare(right.id, undefined, { numeric: true }),
    ),
  };
}
