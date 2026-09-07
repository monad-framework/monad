import Link from "next/link";

import {
  buildFocusProjectionBlocks,
  type FocusProjectionBlock,
} from "@/lib/monad/focus-blocks";
import type { KnowledgeReference, RepositorySnapshot } from "@/lib/monad/model";

type FocusWorkspaceProps = {
  snapshot: RepositorySnapshot;
};

function RelationshipBlock({
  title,
  relationships,
}: {
  title: string;
  relationships: KnowledgeReference[];
}) {
  return (
    <section className="panel focus-relations-panel">
      <div className="panel-heading">
        <div>
          <p className="section-label">Relationships</p>

          <h2>{title}</h2>
        </div>

        <span className="count-badge">{relationships.length}</span>
      </div>

      {relationships.length === 0 ? (
        <div className="empty-state">
          <p>No relationships recorded.</p>
        </div>
      ) : (
        <div className="focus-workspace-relations">
          {relationships.map((relationship) => (
            <Link
              className="focus-workspace-relation"
              href={`/focus/${encodeURIComponent(relationship.id)}`}
              key={`${relationship.relationship}:${relationship.id}`}
            >
              <div>
                <code>{relationship.id}</code>

                <span>{relationship.relationship}</span>
              </div>

              <span>→</span>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}

function ReferenceProjection({
  references,
}: {
  references: KnowledgeReference[];
}) {
  return (
    <div className="focus-workspace-relations">
      {references.map((reference) => (
        <Link
          className="focus-workspace-relation"
          href={`/focus/${encodeURIComponent(reference.id)}`}
          key={`${reference.relationship}:${reference.id}`}
        >
          <div>
            <code>{reference.id}</code>

            <span>{reference.relationship}</span>
          </div>

          <span>→</span>
        </Link>
      ))}
    </div>
  );
}

function AcceptanceProjection({ block }: { block: FocusProjectionBlock }) {
  const criteria = block.criteria ?? [];

  const complete = criteria.filter((criterion) => criterion.complete).length;

  return (
    <>
      <div className="execution-summary">
        <div>
          <span>Complete</span>
          <strong>{complete}</strong>
        </div>

        <div>
          <span>Total</span>
          <strong>{criteria.length}</strong>
        </div>
      </div>

      <div className="acceptance-list">
        {criteria.map((criterion, index) => (
          <div className="acceptance-row" key={`${index}:${criterion.text}`}>
            <span
              className={
                criterion.complete
                  ? "criterion-state complete"
                  : "criterion-state"
              }
            >
              {criterion.complete ? "✓" : "○"}
            </span>

            <span>{criterion.text}</span>
          </div>
        ))}
      </div>
    </>
  );
}

function FieldsProjection({ block }: { block: FocusProjectionBlock }) {
  const fields = block.fields ?? [];

  if (fields.length === 0) {
    return null;
  }

  return (
    <dl className="focus-metadata">
      {fields.map((field) => (
        <div key={`${field.label}:${field.value}`}>
          <dt>{field.label}</dt>

          <dd>{field.value}</dd>
        </div>
      ))}
    </dl>
  );
}

function ProjectionBlock({ block }: { block: FocusProjectionBlock }) {
  const references = block.references ?? [];

  const hasReferences = references.length > 0;

  const hasCriteria = (block.criteria?.length ?? 0) > 0;

  const hasFields = (block.fields?.length ?? 0) > 0;

  return (
    <section className="panel focus-document-block" id={block.id}>
      <div className="panel-heading">
        <div>
          <p className="section-label">{block.eyebrow}</p>

          <h2>{block.title}</h2>
        </div>

        {hasReferences ? (
          <span className="count-badge">{references.length}</span>
        ) : null}

        {hasCriteria ? (
          <span className="count-badge">
            {block.criteria?.filter((criterion) => criterion.complete).length}/
            {block.criteria?.length ?? 0}
          </span>
        ) : null}
      </div>

      {hasFields ? <FieldsProjection block={block} /> : null}

      {block.body ? <div className="focus-copy">{block.body}</div> : null}

      {hasReferences ? <ReferenceProjection references={references} /> : null}

      {hasCriteria ? <AcceptanceProjection block={block} /> : null}

      {!block.body && !hasReferences && !hasCriteria && !hasFields ? (
        <div className="empty-state">
          <p>No projected content.</p>
        </div>
      ) : null}
    </section>
  );
}

export function FocusWorkspace({ snapshot }: FocusWorkspaceProps) {
  const { object, document, incoming, outgoing } = snapshot.focus;

  const blocks = buildFocusProjectionBlocks(snapshot);

  if (!object) {
    return (
      <main className="workspace focus-workspace">
        <section className="panel">
          <div className="empty-state">
            <p>No focus object could be resolved.</p>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="workspace focus-workspace">
      <header className="focus-header">
        <div>
          <p className="eyebrow">Monad / Focus / {object.type}</p>

          <div className="focus-title-row">
            <code>{object.id}</code>

            {object.status ? (
              <span className="lifecycle-badge">{object.status}</span>
            ) : null}
          </div>

          <h1>{object.title}</h1>
        </div>

        <Link className="back-to-now" href="/">
          ← Now
        </Link>
      </header>

      <section className="focus-overview-grid">
        <article className="panel focus-summary-panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">Object</p>

              <h2>Identity</h2>
            </div>
          </div>

          <dl className="focus-metadata">
            <div>
              <dt>Identifier</dt>

              <dd>
                <code>{object.id}</code>
              </dd>
            </div>

            <div>
              <dt>Type</dt>

              <dd>{object.type}</dd>
            </div>

            <div>
              <dt>Lifecycle</dt>

              <dd>{object.status ?? "—"}</dd>
            </div>

            <div>
              <dt>Authority</dt>

              <dd>{object.authority ?? "—"}</dd>
            </div>
          </dl>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="section-label">Artifact</p>

              <h2>Metadata</h2>
            </div>
          </div>

          {document?.metadata.length ? (
            <dl className="focus-metadata">
              {document.metadata.map((field) => (
                <div key={`${field.label}:${field.value}`}>
                  <dt>{field.label}</dt>

                  <dd>{field.value}</dd>
                </div>
              ))}
            </dl>
          ) : (
            <div className="empty-state">
              <p>No artifact metadata resolved.</p>
            </div>
          )}
        </article>
      </section>

      <section className="focus-relationship-grid">
        <RelationshipBlock relationships={outgoing} title="Outgoing" />

        <RelationshipBlock relationships={incoming} title="Incoming" />
      </section>

      {blocks.length === 0 ? (
        <section className="panel focus-document-block">
          <div className="empty-state">
            <p>
              No semantic projection blocks could be derived for this object.
            </p>
          </div>
        </section>
      ) : (
        blocks.map((block) => <ProjectionBlock block={block} key={block.id} />)
      )}

      <section className="panel focus-source-panel">
        <div className="panel-heading">
          <div>
            <p className="section-label">Provenance</p>

            <h2>Source</h2>
          </div>
        </div>

        <div className="focus-source">
          <code>
            {document?.sourcePath ?? object.artifactPath ?? object.source}
          </code>
        </div>
      </section>
    </main>
  );
}
