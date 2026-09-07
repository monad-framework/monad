import { connection } from "next/server";

import { AppShell } from "@/components/workbench/app-shell";
import { Workspace } from "@/components/workbench/workspace";
import { getRepositorySnapshot } from "@/lib/monad/repository";

type PageProps = {
  searchParams: Promise<{
    focus?: string | string[];
  }>;
};

export default async function Home({ searchParams }: PageProps) {
  await connection();

  const params = await searchParams;

  const focusId = Array.isArray(params.focus) ? params.focus[0] : params.focus;

  const snapshot = await getRepositorySnapshot(focusId);

  return (
    <AppShell snapshot={snapshot}>
      <Workspace snapshot={snapshot} />
    </AppShell>
  );
}
