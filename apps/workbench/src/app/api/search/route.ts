import { NextResponse } from "next/server";

import { readWorkbenchObjectIndex } from "@/lib/monad/object-index";
import { findMonadRoot } from "@/lib/monad/repository";

function score(query: string, id: string, title: string, type: string): number {
  const normalizedId = id.toLowerCase();
  const normalizedTitle = title.toLowerCase();
  const normalizedType = type.toLowerCase();

  if (normalizedId === query) return 100;
  if (normalizedId.startsWith(query)) return 90;
  if (normalizedTitle.startsWith(query)) return 80;
  if (normalizedId.includes(query)) return 70;
  if (normalizedTitle.includes(query)) return 60;
  if (normalizedType.includes(query)) return 40;
  return 0;
}

export async function GET(request: Request) {
  const url = new URL(request.url);
  const query = (url.searchParams.get("q") ?? "")
    .trim()
    .slice(0, 80)
    .toLowerCase();

  if (!query) {
    return NextResponse.json({ results: [] });
  }

  const root = await findMonadRoot(process.cwd());
  const index = await readWorkbenchObjectIndex(root);

  const results = index.items
    .map((item) => ({
      ...item,
      score: score(query, item.id, item.title, item.type),
    }))
    .filter((item) => item.score > 0)
    .sort(
      (left, right) =>
        right.score - left.score || left.id.localeCompare(right.id),
    )
    .slice(0, 40)
    .map(({ score: _score, ...item }) => item);

  return NextResponse.json({ results });
}
