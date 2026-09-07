import { connection } from "next/server";

import { AppShell } from "@/components/workbench/app-shell";
import { ExecutionWorkspace } from "@/components/workbench/execution-workspace";
import { readExecutionProjection } from "@/lib/monad/execution";
import { getRepositorySnapshot } from "@/lib/monad/repository";

export default async function ExecutionPage() {
  await connection();

  const snapshot = await getRepositorySnapshot();
  const execution = await readExecutionProjection(snapshot.rootPath);

  return (
    <AppShell snapshot={snapshot}>
      <ExecutionWorkspace execution={execution} snapshot={snapshot} />
    </AppShell>
  );
}
