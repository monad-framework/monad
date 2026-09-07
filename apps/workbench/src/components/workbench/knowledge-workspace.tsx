import Link from "next/link";

import type {
  KnowledgeCatalogItem,
  KnowledgeCatalogKind,
  KnowledgeCatalogProjection,
} from "@/lib/monad/knowledge-catalog";
import type { RepositorySnapshot } from "@/lib/monad/model";

type KnowledgeWorkspaceProps = {
  catalog: KnowledgeCatalogProjection;
  selectedKind?: KnowledgeCatalogKind;
  snapshot: RepositorySnapshot;
};

const CATEGORY_LABELS: Record<KnowledgeCatalogKind, string> = {
  requirement: "Requirements",
  specification: "Specifications",
  adr: "ADRs",
  policy: "Policies",
  evidence: "Evidence",
};

function CatalogRow({ item }: { item: KnowledgeCatalogItem }) {
  return (
    <Link
      className="knowledge-reference knowledge-reference-link"
      href={`/focus/${encodeURIComponent(item.id)}`}
    >
      <div>
        <code>{item.id}</code>
        <span>{item.kind}</span>
      </div>

      <span className="relationship-label">
        {item.status ?? item.result ?? item.authority ?? "registered"}
      </span>

      <strong>{item.title}</strong>

      {item.summary ? (
        <span className="knowledge-path">{item.summary}</span>
      ) : null}

      {item.target ? (
        <span className="knowledge-path">
          target {item.target}
          {item.validator ? ` · ${item.validator}` : ""}
        </span>
      ) : (
        <code className="knowledge-path">{item.path}</code>
      )}
    </Link>
  );
}

function CatalogSection({
  kind,
  items,
}: {
  kind: KnowledgeCatalogKind;
  items: KnowledgeCatalogItem[];
}) {
  return (
    <section className="panel focus-document-block" id={kind}>
      <div className="panel-heading">
        <div>
          <p className="section-label">Knowledge</p>
          <h2>{CATEGORY_LABELS[kind]}</h2>
        </div>
        <span className="count-badge">{items.length}</span>
      </div>

      {items.length === 0 ? (
        <div className="empty-state">
          <p>No registered objects were resolved for this category.</p>
        </div>
      ) : (
        <div className="knowledge-reference-list">
          {items.map((item) => (
            <CatalogRow item={item} key={item.id} />
          ))}
        </div>
      )}
    </section>
  );
}

export function KnowledgeWorkspace({
  catalog,
  selectedKind,
  snapshot,
}: KnowledgeWorkspaceProps) {
  const categories: Array<[KnowledgeCatalogKind, KnowledgeCatalogItem[]]> = [
    ["requirement", catalog.requirements],
    ["specification", catalog.specifications],
    ["adr", catalog.adrs],
    ["policy", catalog.policies],
    ["evidence", catalog.evidence],
  ];

  const visibleCategories = selectedKind
    ? categories.filter(([kind]) => kind === selectedKind)
    : categories;

  return (
    <main className="workspace">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Monad / Knowledge</p>
          <h1>Governed engineering knowledge</h1>
          <p className="workspace-description">
            Requirements, specifications, architecture decisions, policies, and
            evidence projected from authoritative repository and EOS sources.
          </p>
        </div>

        <div className="branch-chip">
          <span className="status-dot" />
          {snapshot.branch}
        </div>
      </header>

      <section className="summary-grid">
        <Link className="summary-card" href="/knowledge?kind=requirement">
          <p className="card-label">Requirements</p>
          <strong>{catalog.counts.requirements}</strong>
          <p>Functional and quality requirements.</p>
        </Link>
        <Link className="summary-card" href="/knowledge?kind=specification">
          <p className="card-label">Specifications</p>
          <strong>{catalog.counts.specifications}</strong>
          <p>Registered specification authority.</p>
        </Link>
        <Link className="summary-card" href="/knowledge?kind=adr">
          <p className="card-label">ADRs / Policies</p>
          <strong>
            {catalog.counts.adrs} / {catalog.counts.policies}
          </strong>
          <p>Architecture and governance authority.</p>
        </Link>
        <Link className="summary-card" href="/knowledge?kind=evidence">
          <p className="card-label">Evidence</p>
          <strong>
            {catalog.counts.currentEvidence} / {catalog.counts.evidence}
          </strong>
          <p>Current versus total evidence records.</p>
        </Link>
      </section>

      {selectedKind ? (
        <div className="focus-document-block">
          <Link className="back-to-now" href="/knowledge">
            ← All knowledge
          </Link>
        </div>
      ) : null}

      {visibleCategories.map(([kind, items]) => (
        <CatalogSection items={items} key={kind} kind={kind} />
      ))}

      <section className="panel focus-source-panel">
        <div className="panel-heading">
          <div>
            <p className="section-label">Provenance</p>
            <h2>Knowledge sources</h2>
          </div>
        </div>

        <dl className="focus-metadata">
          {catalog.sources.map((source) => (
            <div key={source}>
              <dt>Canonical source</dt>
              <dd>
                <code>{source}</code>
              </dd>
            </div>
          ))}
        </dl>
      </section>
    </main>
  );
}
