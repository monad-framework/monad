import { connection } from "next/server";

import { AppShell } from "@/components/workbench/app-shell";
import { FocusWorkspace } from "@/components/workbench/focus-workspace";
import { getRepositorySnapshot } from "@/lib/monad/repository";

type FocusPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function FocusPage({ params }: FocusPageProps) {
  await connection();

  const { id } = await params;

  const snapshot = await getRepositorySnapshot(id);

  return (
    <AppShell snapshot={snapshot}>
      <FocusWorkspace snapshot={snapshot} />
    </AppShell>
  );
}
