import { connection } from "next/server";

import { AppShell } from "@/components/workbench/app-shell";
import { ControlWorkspace } from "@/components/workbench/control-workspace";
import { readControlProjection } from "@/lib/monad/control";
import { getRepositorySnapshot } from "@/lib/monad/repository";

export default async function ControlPage() {
  await connection();

  const snapshot = await getRepositorySnapshot();
  const control = await readControlProjection(snapshot.rootPath);

  return (
    <AppShell snapshot={snapshot}>
      <ControlWorkspace control={control} snapshot={snapshot} />
    </AppShell>
  );
}
