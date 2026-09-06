import { connection } from "next/server";

import { AppShell } from "@/components/workbench/app-shell";
import { getRepositorySnapshot } from "@/lib/monad/repository";

export default async function Home() {
  await connection();

  const snapshot = await getRepositorySnapshot();

  return <AppShell snapshot={snapshot} />;
}
