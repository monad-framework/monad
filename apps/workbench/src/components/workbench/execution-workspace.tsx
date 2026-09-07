import Link from "next/link";

import type {
  ExecutionProgramIncrement,
  ExecutionProjection,
  ExecutionProjectionRecord,
  ExecutionWorkCycle,
  ExecutionWorkPacket,
} from "@/lib/monad/execution";
import type { RepositorySnapshot } from "@/lib/monad/model";

type ExecutionWorkspaceProps = {
  execution: ExecutionProjection;
  snapshot: RepositorySnapshot;
};

type LifecycleValue = {
  status: string;
  registryStatus?: string;
};

function StateBadge({ status }: { status: string }) {
  return <span className="lifecycle-badge">{status || "UNKNOWN"}</span>;
}

function LifecycleState({ value }: { value: LifecycleValue }) {
  return (
    <div>
      <StateBadge status={value.status} />
      {value.registryStatus ? (
        <span
          className="count-badge"
          title="Canonical EOS current state overrides registry projection drift"
        >
          registry {value.registryStatus} → canonical {value.status}
        </span>
      ) : null}
    </div>
  );
}

function ExecutionState({
  execution,
}: {
  execution: ExecutionProjectionRecord;
}) {
  return <LifecycleState value={execution} />;
}

function WorkPacketProjection({
  packet,
  currentId,
}: {
  packet: ExecutionWorkPacket;
  currentId?: string;
}) {
  const current = packet.id === currentId;

  return (
    <details id={packet.id} open={current}>
      <summary className="context-object context-object-link">
        <div>
          <code>{packet.id}</code>
          <strong>{packet.title}</strong>
        </div>

        <LifecycleState value={packet} />
      </summary>

      <div className="story-section">
        <dl className="focus-metadata">
          <div>
            <dt>Domain</dt>
            <dd>{packet.domain || "—"}</dd>
          </div>
          <div>
            <dt>Lifecycle authority</dt>
            <dd>.eos/state/current.json</dd>
          </div>
          {packet.registryStatus ? (
            <div>
              <dt>Registry projection</dt>
              <dd>{packet.registryStatus} (drift detected)</dd>
            </div>
          ) : null}
          <div>
            <dt>Executions</dt>
            <dd>{packet.executions.length}</dd>
          </div>
          <div>
            <dt>Evidence</dt>
            <dd>{packet.evidence.total}</dd>
          </div>
          <div>
            <dt>Current evidence</dt>
            <dd>{packet.evidence.current}</dd>
          </div>
          <div>
            <dt>Source</dt>
            <dd>
              <code>{packet.path}</code>
            </dd>
          </div>
        </dl>

        <div className="inspector-section">
          <Link
            className="open-focus"
            href={`/focus/${encodeURIComponent(packet.id)}`}
          >
            Open Work Packet in Focus
            <span>→</span>
          </Link>
        </div>

        <section className="panel focus-document-block">
          <div className="panel-heading">
            <div>
              <p className="section-label">Execution history</p>
              <h2>Executions</h2>
            </div>
            <span className="count-badge">{packet.executions.length}</span>
          </div>

          {packet.executions.length === 0 ? (
            <div className="empty-state">
              <p>No executions are registered for this Work Packet.</p>
            </div>
          ) : (
            <div className="context-stack">
              {packet.executions.map((execution) => (
                <Link
                  className="context-object context-object-link"
                  href={`/focus/${encodeURIComponent(execution.id)}`}
                  key={execution.id}
                >
                  <div>
                    <code>{execution.id}</code>
                    <strong>
                      {execution.actor || "unknown actor"} ·{" "}
                      {execution.branch || "no branch"}
                    </strong>
                  </div>
                  <ExecutionState execution={execution} />
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="panel focus-document-block">
          <div className="panel-heading">
            <div>
              <p className="section-label">Verification</p>
              <h2>Evidence summary</h2>
            </div>
          </div>

          <dl className="focus-metadata">
            <div>
              <dt>Total</dt>
              <dd>{packet.evidence.total}</dd>
            </div>
            <div>
              <dt>Current</dt>
              <dd>{packet.evidence.current}</dd>
            </div>
            <div>
              <dt>Passed</dt>
              <dd>{packet.evidence.passed}</dd>
            </div>
            <div>
              <dt>Failed</dt>
              <dd>{packet.evidence.failed}</dd>
            </div>
            <div>
              <dt>Skipped</dt>
              <dd>{packet.evidence.skipped}</dd>
            </div>
          </dl>
        </section>
      </div>
    </details>
  );
}

function WorkCycleProjection({
  cycle,
  currentCycleId,
  currentPacketId,
}: {
  cycle: ExecutionWorkCycle;
  currentCycleId?: string;
  currentPacketId?: string;
}) {
  const current = cycle.id === currentCycleId;

  return (
    <details id={cycle.id} open={current}>
      <summary className="context-object context-object-link">
        <div>
          <code>{cycle.id}</code>
          <strong>{cycle.title}</strong>
        </div>
        <LifecycleState value={cycle} />
      </summary>

      <div className="story-section">
        <div className="inspector-section">
          <Link
            className="open-focus"
            href={`/focus/${encodeURIComponent(cycle.id)}`}
          >
            Open Work Cycle in Focus
            <span>→</span>
          </Link>
        </div>

        {cycle.workPackets.length === 0 ? (
          <div className="empty-state">
            <p>No Work Packets are registered for this Work Cycle.</p>
          </div>
        ) : (
          <div className="context-stack">
            {cycle.workPackets.map((packet) => (
              <WorkPacketProjection
                currentId={currentPacketId}
                key={packet.id}
                packet={packet}
              />
            ))}
          </div>
        )}
      </div>
    </details>
  );
}

function ProgramIncrementProjection({
  program,
  snapshot,
}: {
  program: ExecutionProgramIncrement;
  snapshot: RepositorySnapshot;
}) {
  const current = program.id === snapshot.execution.programIncrement?.id;

  return (
    <details id={program.id} open={current}>
      <summary className="context-object context-object-link">
        <div>
          <code>{program.id}</code>
          <strong>{program.title}</strong>
        </div>
        <LifecycleState value={program} />
      </summary>

      <div className="story-section">
        <div className="inspector-section">
          <Link
            className="open-focus"
            href={`/focus/${encodeURIComponent(program.id)}`}
          >
            Open Program Increment in Focus
            <span>→</span>
          </Link>
        </div>

        {program.workCycles.length === 0 ? (
          <div className="empty-state">
            <p>No Work Cycles are registered for this Program Increment.</p>
          </div>
        ) : (
          <div className="context-stack">
            {program.workCycles.map((cycle) => (
              <WorkCycleProjection
                currentCycleId={snapshot.execution.workCycle?.id}
                currentPacketId={snapshot.execution.workPacket?.id}
                cycle={cycle}
                key={cycle.id}
              />
            ))}
          </div>
        )}
      </div>
    </details>
  );
}

export function ExecutionWorkspace({
  execution,
  snapshot,
}: ExecutionWorkspaceProps) {
  return (
    <main className="workspace">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Monad / Execution</p>
          <h1>Governed execution hierarchy</h1>
          <p className="workspace-description">
            Canonical Program Increment → Work Cycle → Work Packet → Execution
            projection. Product planning remains a separate orthogonal
            dimension. Lifecycle values are overlaid from canonical EOS current
            state; registry drift is surfaced explicitly.
          </p>
        </div>

        <div className="branch-chip">
          <span className="status-dot" />
          {snapshot.branch}
        </div>
      </header>

      <section className="summary-grid">
        <article className="summary-card">
          <p className="card-label">Program Increments</p>
          <strong>{execution.counts.programIncrements}</strong>
          <p>Canonical increment registry.</p>
        </article>
        <article className="summary-card">
          <p className="card-label">Work Cycles</p>
          <strong>{execution.counts.workCycles}</strong>
          <p>Governed execution cycles.</p>
        </article>
        <article className="summary-card">
          <p className="card-label">Work Packets</p>
          <strong>{execution.counts.workPackets}</strong>
          <p>Bounded governed units of execution.</p>
        </article>
        <article className="summary-card">
          <p className="card-label">Lifecycle drift</p>
          <strong>{execution.counts.lifecycleDrift}</strong>
          <p>Registry states overridden by canonical EOS current state.</p>
        </article>
      </section>

      <section className="panel focus-document-block" id="execution-hierarchy">
        <div className="panel-heading">
          <div>
            <p className="section-label">Execution</p>
            <h2>Canonical hierarchy</h2>
          </div>
          <span className="count-badge">
            {execution.programIncrements.length}
          </span>
        </div>

        <div className="context-stack">
          {execution.programIncrements.map((program) => (
            <ProgramIncrementProjection
              key={program.id}
              program={program}
              snapshot={snapshot}
            />
          ))}
        </div>
      </section>

      <section className="panel focus-source-panel">
        <div className="panel-heading">
          <div>
            <p className="section-label">Provenance</p>
            <h2>Execution sources</h2>
          </div>
        </div>
        <dl className="focus-metadata">
          {execution.sources.map((source) => (
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
