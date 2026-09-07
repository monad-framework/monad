import Link from "next/link";
import type {
  CurrentKnowledgeContext,
  KnowledgeReference,
} from "@/lib/monad/model";

type KnowledgeContextProps = {
  knowledge: CurrentKnowledgeContext;
};

function ReferenceRow({ reference }: { reference: KnowledgeReference }) {
  return (
    <Link
      className="knowledge-reference knowledge-reference-link"
      href={`/?focus=${encodeURIComponent(reference.id)}`}
    >
      <div>
        <code>{reference.id}</code>
        <span>{reference.kind}</span>
      </div>

      <span className="relationship-label">{reference.relationship}</span>

      {reference.path ? (
        <code className="knowledge-path">{reference.path}</code>
      ) : null}
    </Link>
  );
}

export function KnowledgeContext({ knowledge }: KnowledgeContextProps) {
  const completedCriteria = knowledge.acceptanceCriteria.filter(
    (criterion) => criterion.complete,
  ).length;

  return (
    <section className="knowledge-grid">
      <article className="panel">
        <div className="panel-heading">
          <div>
            <p className="section-label">How</p>
            <h2>Governing knowledge</h2>
          </div>

          <span className="count-badge">{knowledge.governing.length}</span>
        </div>

        {knowledge.governing.length === 0 ? (
          <div className="empty-state">
            <p>No governing references resolved.</p>
          </div>
        ) : (
          <div className="knowledge-reference-list">
            {knowledge.governing.map((reference) => (
              <ReferenceRow
                key={`${reference.relationship}:${reference.id}`}
                reference={reference}
              />
            ))}
          </div>
        )}
      </article>

      <article className="panel">
        <div className="panel-heading">
          <div>
            <p className="section-label">Prerequisites</p>
            <h2>Dependencies</h2>
          </div>

          <span className="count-badge">{knowledge.dependencies.length}</span>
        </div>

        {knowledge.dependencies.length === 0 ? (
          <div className="empty-state">
            <p>No dependencies resolved.</p>
          </div>
        ) : (
          <div className="knowledge-reference-list">
            {knowledge.dependencies.map((reference) => (
              <ReferenceRow
                key={`${reference.relationship}:${reference.id}`}
                reference={reference}
              />
            ))}
          </div>
        )}
      </article>

      <article className="panel">
        <div className="panel-heading">
          <div>
            <p className="section-label">Did it work</p>
            <h2>Acceptance</h2>
          </div>

          <span className="count-badge">
            {completedCriteria}/{knowledge.acceptanceCriteria.length}
          </span>
        </div>

        {knowledge.acceptanceCriteria.length === 0 ? (
          <div className="empty-state">
            <p>No acceptance criteria resolved.</p>
          </div>
        ) : (
          <div className="acceptance-list">
            {knowledge.acceptanceCriteria.map((criterion, index) => (
              <div
                className="acceptance-row"
                key={`${index}:${criterion.text}`}
              >
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
        )}
      </article>

      <article className="panel">
        <div className="panel-heading">
          <div>
            <p className="section-label">Evidence</p>
            <h2>Execution & verification</h2>
          </div>
        </div>

        <div className="execution-summary">
          <div>
            <span>Executions</span>
            <strong>{knowledge.executions.length}</strong>
          </div>

          <div>
            <span>Evidence records</span>
            <strong>{knowledge.evidence.length}</strong>
          </div>
        </div>

        {knowledge.executions.length === 0 &&
        knowledge.evidence.length === 0 ? (
          <div className="empty-state knowledge-empty">
            <p>None recorded yet.</p>
            <span>
              The packet is active, but no execution or verification evidence is
              currently registered for it.
            </span>
          </div>
        ) : null}

        {knowledge.executions.map((execution) => (
          <div className="execution-record" key={execution.id}>
            <code>{execution.id}</code>
            <span>{execution.status}</span>
            <span>{execution.actor}</span>
          </div>
        ))}

        {knowledge.evidence.map((evidence) => (
          <div className="execution-record" key={evidence.id}>
            <code>{evidence.id}</code>
            <span>{evidence.result}</span>
            <span>{evidence.validator}</span>
          </div>
        ))}
      </article>
    </section>
  );
}
