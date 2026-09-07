import Link from "next/link";

import type {
  ChangeRequestItem,
  ConsistencyFinding,
  ControlArtifactItem,
  ControlProjection,
  DecisionItem,
  ReleaseItem,
} from "@/lib/monad/control";
import type { RepositorySnapshot } from "@/lib/monad/model";

type ControlWorkspaceProps = {
  control: ControlProjection;
  snapshot: RepositorySnapshot;
};

function FindingRow({ finding }: { finding: ConsistencyFinding }) {
  return (
    <div className="knowledge-reference">
      <div>
        <code>{finding.id}</code>
        <span>{finding.severity}</span>
      </div>
      <span className="relationship-label">drift</span>
      <strong>{finding.title}</strong>
      <span className="knowledge-path">{finding.detail}</span>
      <code className="knowledge-path">
        {finding.canonicalSource} ↔ {finding.comparedSource}
      </code>
    </div>
  );
}

function ChangeRow({ change }: { change: ChangeRequestItem }) {
  return (
    <Link
      className="knowledge-reference knowledge-reference-link"
      href={`/focus/${encodeURIComponent(change.id)}`}
    >
      <div>
        <code>{change.id}</code>
        <span>change request</span>
      </div>
      <span className="relationship-label">{change.status}</span>
      <strong>{change.summary}</strong>
      <span className="knowledge-path">target {change.target}</span>
      <code className="knowledge-path">{change.path}</code>
    </Link>
  );
}

function ArtifactRow({ artifact }: { artifact: ControlArtifactItem }) {
  return (
    <Link
      className="knowledge-reference knowledge-reference-link"
      href={`/focus/${encodeURIComponent(artifact.id)}`}
    >
      <div>
        <code>{artifact.id}</code>
        <span>{artifact.type}</span>
      </div>
      <span className="relationship-label">{artifact.authority}</span>
      <strong>{artifact.title}</strong>
      <code className="knowledge-path">{artifact.path}</code>
    </Link>
  );
}

function DecisionRow({ decision }: { decision: DecisionItem }) {
  return (
    <div className="knowledge-reference">
      <div>
        <code>{decision.target}</code>
        <span>{decision.action}</span>
      </div>
      <span className="relationship-label">{decision.outcome}</span>
      <strong>{decision.actor || "unknown actor"}</strong>
      <span className="knowledge-path">{decision.reason}</span>
      <code className="knowledge-path">{decision.timestamp}</code>
    </div>
  );
}

function ReleaseRow({ release }: { release: ReleaseItem }) {
  return (
    <Link
      className="knowledge-reference knowledge-reference-link"
      href={`/focus/${encodeURIComponent(release.id)}`}
    >
      <div>
        <code>{release.id}</code>
        <span>release</span>
      </div>
      <span className="relationship-label">
        {release.status || "registered"}
      </span>
      <strong>{release.version || release.id}</strong>
      <code className="knowledge-path">{release.path}</code>
    </Link>
  );
}

export function ControlWorkspace({ control, snapshot }: ControlWorkspaceProps) {
  return (
    <main className="workspace">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Monad / Control</p>
          <h1>Governance and control state</h1>
          <p className="workspace-description">
            Change control, decisions, review authority, verification state,
            releases, risks, and consistency findings across canonical and
            narrative projections.
          </p>
        </div>
        <div className="branch-chip">
          <span className="status-dot" />
          {snapshot.branch}
        </div>
      </header>

      <section className="summary-grid">
        <article className="summary-card">
          <p className="card-label">Changes</p>
          <strong>{control.changes.length}</strong>
          <p>Registered governed change requests.</p>
        </article>
        <article className="summary-card">
          <p className="card-label">Reviews / Risks</p>
          <strong>
            {control.reviews.length} / {control.risks.length}
          </strong>
          <p>Review authority and registered risk artifacts.</p>
        </article>
        <article className="summary-card">
          <p className="card-label">Verification</p>
          <strong>
            {control.verification.current} / {control.verification.total}
          </strong>
          <p>Current versus total evidence records.</p>
        </article>
        <article className="summary-card">
          <p className="card-label">Consistency findings</p>
          <strong>{control.findings.length}</strong>
          <p>Detected projection drift requiring operator attention.</p>
        </article>
      </section>

      <section className="panel focus-document-block" id="findings">
        <div className="panel-heading">
          <div>
            <p className="section-label">Control</p>
            <h2>Consistency findings</h2>
          </div>
          <span className="count-badge">{control.findings.length}</span>
        </div>
        {control.findings.length === 0 ? (
          <div className="empty-state">
            <p>
              No canonical-versus-narrative consistency findings were detected.
            </p>
          </div>
        ) : (
          <div className="knowledge-reference-list">
            {control.findings.map((finding) => (
              <FindingRow finding={finding} key={finding.id} />
            ))}
          </div>
        )}
      </section>

      <section className="panel focus-document-block" id="changes">
        <div className="panel-heading">
          <div>
            <p className="section-label">Change control</p>
            <h2>Change requests</h2>
          </div>
          <span className="count-badge">{control.changes.length}</span>
        </div>
        {control.changes.length === 0 ? (
          <div className="empty-state">
            <p>No change requests are registered.</p>
          </div>
        ) : (
          <div className="knowledge-reference-list">
            {control.changes.map((change) => (
              <ChangeRow change={change} key={change.id} />
            ))}
          </div>
        )}
      </section>

      <section className="panel focus-document-block" id="decisions">
        <div className="panel-heading">
          <div>
            <p className="section-label">Authority</p>
            <h2>Decision history</h2>
          </div>
          <span className="count-badge">{control.decisions.length}</span>
        </div>
        {control.decisions.length === 0 ? (
          <div className="empty-state">
            <p>No decision records are registered.</p>
          </div>
        ) : (
          <div className="knowledge-reference-list">
            {control.decisions.map((decision) => (
              <DecisionRow
                decision={decision}
                key={`${decision.timestamp}:${decision.target}:${decision.action}`}
              />
            ))}
          </div>
        )}
      </section>

      <section className="focus-relationship-grid">
        <section className="panel" id="reviews">
          <div className="panel-heading">
            <div>
              <p className="section-label">Control</p>
              <h2>Reviews</h2>
            </div>
            <span className="count-badge">{control.reviews.length}</span>
          </div>
          {control.reviews.length === 0 ? (
            <div className="empty-state">
              <p>No review artifacts registered.</p>
            </div>
          ) : (
            <div className="knowledge-reference-list">
              {control.reviews.map((review) => (
                <ArtifactRow artifact={review} key={review.id} />
              ))}
            </div>
          )}
        </section>

        <section className="panel" id="risks">
          <div className="panel-heading">
            <div>
              <p className="section-label">Control</p>
              <h2>Risks</h2>
            </div>
            <span className="count-badge">{control.risks.length}</span>
          </div>
          {control.risks.length === 0 ? (
            <div className="empty-state">
              <p>No dedicated risk artifacts are currently registered.</p>
            </div>
          ) : (
            <div className="knowledge-reference-list">
              {control.risks.map((risk) => (
                <ArtifactRow artifact={risk} key={risk.id} />
              ))}
            </div>
          )}
        </section>
      </section>

      <section className="focus-relationship-grid">
        <section className="panel" id="verification">
          <div className="panel-heading">
            <div>
              <p className="section-label">Verification</p>
              <h2>Evidence state</h2>
            </div>
          </div>
          <dl className="focus-metadata">
            <div>
              <dt>Total</dt>
              <dd>{control.verification.total}</dd>
            </div>
            <div>
              <dt>Current</dt>
              <dd>{control.verification.current}</dd>
            </div>
            <div>
              <dt>Passed</dt>
              <dd>{control.verification.passed}</dd>
            </div>
            <div>
              <dt>Failed</dt>
              <dd>{control.verification.failed}</dd>
            </div>
            <div>
              <dt>Skipped</dt>
              <dd>{control.verification.skipped}</dd>
            </div>
          </dl>
        </section>

        <section className="panel" id="releases">
          <div className="panel-heading">
            <div>
              <p className="section-label">Delivery</p>
              <h2>Releases</h2>
            </div>
            <span className="count-badge">{control.releases.length}</span>
          </div>
          {control.releases.length === 0 ? (
            <div className="empty-state">
              <p>No release records exist yet in .eos/releases.tsv.</p>
            </div>
          ) : (
            <div className="knowledge-reference-list">
              {control.releases.map((release) => (
                <ReleaseRow key={release.id} release={release} />
              ))}
            </div>
          )}
        </section>
      </section>

      <section className="panel focus-source-panel">
        <div className="panel-heading">
          <div>
            <p className="section-label">Provenance</p>
            <h2>Control sources</h2>
          </div>
        </div>
        <dl className="focus-metadata">
          {control.sources.map((source) => (
            <div key={source}>
              <dt>Canonical / compared source</dt>
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
