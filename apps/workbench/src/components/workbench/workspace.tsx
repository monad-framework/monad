import type { RepositorySnapshot } from "@/lib/monad/model";

type WorkspaceProps = {
  snapshot: RepositorySnapshot;
};

function describeStatus(status: string): string {
  switch (status) {
    case "M":
      return "Modified";
    case "A":
      return "Added";
    case "D":
      return "Deleted";
    case "R":
      return "Renamed";
    case "??":
      return "Untracked";
    default:
      return status;
  }
}

export function Workspace({ snapshot }: WorkspaceProps) {
  const totalFiles = snapshot.sources.reduce(
    (sum, source) => sum + source.fileCount,
    0,
  );

  return (
    <main className="workspace">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Monad / Now</p>
          <h1>Development context</h1>
          <p className="workspace-description">
            A current projection of the repository state that Workbench can
            establish without inventing engineering state.
          </p>
        </div>

        <div className="branch-chip">
          <span className="status-dot" />
          {snapshot.branch}
        </div>
      </header>

      <section className="summary-grid" aria-label="Repository summary">
        <article className="summary-card">
          <p className="card-label">Current focus</p>
          <strong>Workbench v0</strong>
          <p>Internal cognitive interface for planning and developing Monad.</p>
        </article>

        <article className="summary-card">
          <p className="card-label">Repository version</p>
          <strong>{snapshot.version ?? "Unknown"}</strong>
          <p>Read from the repository VERSION artifact.</p>
        </article>

        <article className="summary-card">
          <p className="card-label">Indexed sources</p>
          <strong>{snapshot.sources.length}</strong>
          <p>{totalFiles.toLocaleString()} files currently visible.</p>
        </article>

        <article className="summary-card">
          <p className="card-label">Working tree</p>
          <strong>{snapshot.gitStatus.length}</strong>
          <p>
            {snapshot.gitStatus.length === 0
              ? "No local changes detected."
              : "Local changes require awareness."}
          </p>
        </article>
      </section>

      <div className="workspace-columns">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">Knowledge surface</p>
              <h2>Repository sources</h2>
            </div>
          </div>

          <div className="source-list">
            {snapshot.sources.map((source) => (
              <div className="source-row" key={source.path}>
                <div>
                  <strong>{source.label}</strong>
                  <code>{source.path}/</code>
                </div>

                <span>{source.fileCount}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">Attention</p>
              <h2>Working tree</h2>
            </div>

            <span className="count-badge">{snapshot.gitStatus.length}</span>
          </div>

          {snapshot.gitStatus.length === 0 ? (
            <div className="empty-state">
              <p>No working-tree changes detected.</p>
            </div>
          ) : (
            <div className="change-list">
              {snapshot.gitStatus.slice(0, 12).map((entry) => (
                <div
                  className="change-row"
                  key={`${entry.status}:${entry.path}`}
                >
                  <span className="change-status">
                    {describeStatus(entry.status)}
                  </span>
                  <code>{entry.path}</code>
                </div>
              ))}

              {snapshot.gitStatus.length > 12 ? (
                <p className="remaining-changes">
                  +{snapshot.gitStatus.length - 12} more
                </p>
              ) : null}
            </div>
          )}
        </section>
      </div>

      <section className="panel next-panel">
        <div>
          <p className="section-label">Next projection</p>
          <h2>Planning hierarchy</h2>
        </div>

        <p>
          The next Workbench capability will derive Goal → Initiative → Epic →
          Story → Work Packet → Task relationships from real Monad engineering
          artifacts.
        </p>
      </section>
    </main>
  );
}
