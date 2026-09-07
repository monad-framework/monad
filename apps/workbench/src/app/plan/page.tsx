import { connection } from "next/server";

import { AppShell } from "@/components/workbench/app-shell";
import { PlanWorkspace } from "@/components/workbench/plan-workspace";
import { readPlanProjection } from "@/lib/monad/plan";
import { getRepositorySnapshot } from "@/lib/monad/repository";

export default async function PlanPage() {
  await connection();

  const snapshot = await getRepositorySnapshot();

  const plan = await readPlanProjection(snapshot.rootPath);

  return (
    <AppShell snapshot={snapshot}>
      <PlanWorkspace plan={plan} snapshot={snapshot} />
    </AppShell>
  );
}
