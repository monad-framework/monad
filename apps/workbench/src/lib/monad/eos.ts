import { readFile } from "node:fs/promises";
import path from "node:path";

import type {
  CurrentExecutionContext,
  ExecutionObjectType,
  MonadObject,
} from "./model";

type EosRelationship = {
  target_id: string;
  target_type?: string;
  type: string;
};

type EosEntity = {
  authority_level?: string;
  entity_type?: string;
  id: string;
  kind?: string;
  lifecycle_state?: string;
  operational_metadata?: {
    domain?: string;
    github_url?: string;
    path?: string;
    pi?: string;
    title?: string;
    wc?: string;
  };
  relationships?: EosRelationship[];
};

type EosCurrentState = {
  entities: {
    PI?: Record<string, EosEntity>;
    WC?: Record<string, EosEntity>;
    WP?: Record<string, EosEntity>;
    [kind: string]: Record<string, EosEntity> | undefined;
  };
};

function selectByState(
  entities: Record<string, EosEntity> | undefined,
  preferredStates: string[],
): EosEntity | undefined {
  if (!entities) {
    return undefined;
  }

  const values = Object.values(entities);

  for (const state of preferredStates) {
    const match = values.find((entity) => entity.lifecycle_state === state);

    if (match) {
      return match;
    }
  }

  return undefined;
}

function toMonadObject(
  entity: EosEntity | undefined,
  type: ExecutionObjectType,
): MonadObject | undefined {
  if (!entity) {
    return undefined;
  }

  return {
    id: entity.id,
    type,
    title: entity.operational_metadata?.title ?? entity.id,
    status: entity.lifecycle_state,
    authority: entity.authority_level,
    source: ".eos/state/current.json",
    artifactPath: entity.operational_metadata?.path,
    relationships:
      entity.relationships?.map((relationship) => ({
        type: relationship.type,
        target: relationship.target_id,
      })) ?? [],
  };
}

export async function readCurrentExecutionContext(
  root: string,
): Promise<CurrentExecutionContext> {
  const currentStatePath = path.join(root, ".eos", "state", "current.json");

  const raw = await readFile(currentStatePath, "utf8");
  const state = JSON.parse(raw) as EosCurrentState;

  const programIncrement = selectByState(state.entities.PI, ["ACTIVE"]);

  const workCycle = selectByState(state.entities.WC, ["ACTIVE"]);

  const workPacket = selectByState(state.entities.WP, [
    "IN_PROGRESS",
    "AUTHORIZED",
    "READY",
  ]);

  return {
    programIncrement: toMonadObject(programIncrement, "program-increment"),
    workCycle: toMonadObject(workCycle, "work-cycle"),
    workPacket: toMonadObject(workPacket, "work-packet"),
  };
}
