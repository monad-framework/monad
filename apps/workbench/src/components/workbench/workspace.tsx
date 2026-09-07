import Link from "next/link";
import type { MonadObject, RepositorySnapshot } from "@/lib/monad/model";
import { KnowledgeContext } from "./knowledge-context";

type WorkspaceProps = {
  snapshot: RepositorySnapshot;
};

function ContextObject({ object }: { object: MonadObject | undefined }) {
  if (!object) {
    return (
      <div className="context-object muted-object">
        <strong>Unknown</strong>
      </div>
    );
  }

  return (
    <Link
      className="context-object context-object-link"
      href={`/?focus=${encodeURIComponent(object.id)}`}
    >
      <div>
        <code>{object.id}</code>
        <strong>{object.title}</strong>
      </div>

      {object.status ? (
        <span className="lifecycle-badge">{object.status}</span>
      ) : null}
    </Link>
  );
}

export function Workspace({ snapshot }: WorkspaceProps) {
  const { product, execution } = snapshot;

  return (
    <main className="workspace">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Monad / Now</p>
          <h1>Current development context</h1>
          <p className="workspace-description">
            Product intent and governed execution projected from canonical Monad
            and EOS sources.
          </p>
        </div>

        <div className="branch-chip">
          <span className="status-dot" />
          {snapshot.branch}
        </div>
      </header>

      <section className="summary-grid">
        <article className="summary-card">
          <p className="card-label">Product Goal</p>
          <strong>{product.productGoal?.id ?? "Unknown"}</strong>
          <p>{product.productGoal?.title ?? "Not resolved"}</p>
        </article>

        <article className="summary-card">
          <p className="card-label">Initiative</p>
          <strong>{product.initiative?.id ?? "Unknown"}</strong>
          <p>{product.initiative?.title ?? "Not resolved"}</p>
        </article>

        <article className="summary-card">
          <p className="card-label">Work Cycle</p>
          <strong>{execution.workCycle?.id ?? "Unknown"}</strong>
          <p>{execution.workCycle?.title ?? "Not resolved"}</p>
        </article>

        <article className="summary-card">
          <p className="card-label">Active Work Packet</p>
          <strong>{execution.workPacket?.id ?? "None"}</strong>
          <p>{execution.workPacket?.status ?? "No active packet"}</p>
        </article>
      </section>

      <div className="workspace-columns">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">Why / What</p>
              <h2>Product context</h2>
            </div>
          </div>

          <div className="context-stack">
            <ContextObject object={product.productGoal} />
            <ContextObject object={product.initiative} />
            <ContextObject object={product.epic} />
            <ContextObject object={product.feature} />
          </div>

          <div className="story-section">
            <p className="section-label">Stories / Enablers</p>

            <div className="story-list">
              {[...product.stories, ...product.enablers].map((object) => (
                <Link
                  className="story-row story-row-link"
                  href={`/?focus=${encodeURIComponent(object.id)}`}
                  key={object.id}
                ></Link>
              ))}
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">When / Through What</p>
              <h2>Governed execution</h2>
            </div>
          </div>

          <div className="context-stack">
            <ContextObject object={execution.programIncrement} />
            <ContextObject object={execution.workCycle} />
            <ContextObject object={execution.workPacket} />
          </div>

          <div className="authority-note">
            <p className="section-label">Lifecycle authority</p>
            <code>.eos/state/current.json</code>
          </div>
        </section>
      </div>

      <div className="workspace-columns secondary-columns">
        <KnowledgeContext knowledge={snapshot.knowledge} />

        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">Workspace state</p>
              <h2>Repository</h2>
            </div>
          </div>

          <div className="compact-metrics">
            <div>
              <span>Branch</span>
              <code>{snapshot.branch}</code>
            </div>

            <div>
              <span>Version</span>
              <strong>{snapshot.version ?? "Unknown"}</strong>
            </div>

            <div>
              <span>Local changes</span>
              <strong>{snapshot.gitStatus.length}</strong>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">Next lens</p>
              <h2>Governing knowledge</h2>
            </div>
          </div>

          <div className="empty-state">
            <p>
              Next we will project requirements, ADRs, specifications,
              dependencies, evidence, and verification for the active Work
              Packet.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
