import { connection } from "next/server";

import { AppShell } from "@/components/workbench/app-shell";
import { AttentionWorkspace } from "@/components/workbench/attention-workspace";
import { readAttentionProjection } from "@/lib/monad/attention";
import { getRepositorySnapshot } from "@/lib/monad/repository";

export default async function AttentionPage() {
  await connection();

  const snapshot = await getRepositorySnapshot();
  const attention = await readAttentionProjection(snapshot.rootPath);

  return (
    <AppShell snapshot={snapshot}>
      <AttentionWorkspace attention={attention} snapshot={snapshot} />
    </AppShell>
  );
}
