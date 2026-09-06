import type { RepositorySnapshot } from "@/lib/monad/model";

type InspectorProps = {
  snapshot: RepositorySnapshot;
};

export function Inspector({ snapshot }: InspectorProps) {
  return (
    <aside className="inspector">
      <div className="inspector-heading">
        <p className="section-label">Inspector</p>
        <h2>Monad</h2>
        <p>Repository</p>
      </div>

      <dl className="metadata-list">
        <div>
          <dt>Type</dt>
          <dd>Repository</dd>
        </div>

        <div>
          <dt>Branch</dt>
          <dd>
            <code>{snapshot.branch}</code>
          </dd>
        </div>

        <div>
          <dt>Version</dt>
          <dd>{snapshot.version ?? "Unknown"}</dd>
        </div>

        <div>
          <dt>Workbench spec</dt>
          <dd>
            {snapshot.workbenchSpecificationPresent ? "Present" : "Missing"}
          </dd>
        </div>

        <div>
          <dt>Working tree</dt>
          <dd>
            {snapshot.gitStatus.length === 0
              ? "Clean"
              : `${snapshot.gitStatus.length} changed items`}
          </dd>
        </div>
      </dl>

      <div className="inspector-section">
        <p className="section-label">Source</p>
        <code className="source-path">{snapshot.rootPath}</code>
      </div>
    </aside>
  );
}
