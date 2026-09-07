import { connection } from "next/server";

import { AppShell } from "@/components/workbench/app-shell";
import { KnowledgeWorkspace } from "@/components/workbench/knowledge-workspace";
import {
  type KnowledgeCatalogKind,
  readKnowledgeCatalogProjection,
} from "@/lib/monad/knowledge-catalog";
import { getRepositorySnapshot } from "@/lib/monad/repository";

const VALID_KINDS = new Set<KnowledgeCatalogKind>([
  "requirement",
  "specification",
  "adr",
  "policy",
  "evidence",
]);

type KnowledgePageProps = {
  searchParams: Promise<{
    kind?: string | string[];
  }>;
};

export default async function KnowledgePage({
  searchParams,
}: KnowledgePageProps) {
  await connection();

  const params = await searchParams;
  const rawKind = Array.isArray(params.kind) ? params.kind[0] : params.kind;
  const selectedKind =
    rawKind && VALID_KINDS.has(rawKind as KnowledgeCatalogKind)
      ? (rawKind as KnowledgeCatalogKind)
      : undefined;

  const snapshot = await getRepositorySnapshot();
  const catalog = await readKnowledgeCatalogProjection(snapshot.rootPath);

  return (
    <AppShell snapshot={snapshot}>
      <KnowledgeWorkspace
        catalog={catalog}
        selectedKind={selectedKind}
        snapshot={snapshot}
      />
    </AppShell>
  );
}
