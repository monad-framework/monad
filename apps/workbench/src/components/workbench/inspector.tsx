"use client";

import { PanelRightClose, PanelRightOpen } from "lucide-react";
import Link from "next/link";

import type { KnowledgeReference, RepositorySnapshot } from "@/lib/monad/model";

type InspectorProps = {
  snapshot: RepositorySnapshot;
  collapsed: boolean;
  onToggle: () => void;
};

function Relation({
  relation,
  direction,
}: {
  relation: KnowledgeReference;
  direction: "incoming" | "outgoing";
}) {
  return (
    <Link
      className="focus-relation"
      href={`/focus/${encodeURIComponent(relation.id)}`}
    >
      <div>
        <span>{direction === "incoming" ? "←" : "→"}</span>

        <code>{relation.id}</code>
      </div>

      <span>{relation.relationship}</span>
    </Link>
  );
}

export function Inspector({ snapshot, collapsed, onToggle }: InspectorProps) {
  const focus = snapshot.focus.object;

  return (
    <aside className="inspector">
      <div className="side-panel-toolbar inspector-toolbar">
        {!collapsed ? <span>Inspector</span> : null}

        <button
          aria-label={collapsed ? "Expand inspector" : "Collapse inspector"}
          className="side-panel-toggle"
          onClick={onToggle}
          title={collapsed ? "Expand inspector" : "Collapse inspector"}
          type="button"
        >
          {collapsed ? (
            <PanelRightOpen size={15} />
          ) : (
            <PanelRightClose size={15} />
          )}
        </button>
      </div>

      {!collapsed ? (
        <>
          <div className="inspector-heading">
            <p className="section-label">Focus</p>

            <h2>{focus?.id ?? "No focus"}</h2>

            <p>{focus?.title ?? "Nothing selected"}</p>
          </div>

          {focus ? (
            <>
              <dl className="metadata-list">
                <div>
                  <dt>Type</dt>
                  <dd>{focus.type}</dd>
                </div>

                <div>
                  <dt>Lifecycle</dt>
                  <dd>{focus.status ?? "—"}</dd>
                </div>

                <div>
                  <dt>Authority</dt>
                  <dd>{focus.authority ?? "—"}</dd>
                </div>

                <div>
                  <dt>Outgoing</dt>
                  <dd>{snapshot.focus.outgoing.length}</dd>
                </div>

                <div>
                  <dt>Incoming</dt>
                  <dd>{snapshot.focus.incoming.length}</dd>
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
                  <dt>Working tree</dt>
                  <dd>
                    {snapshot.gitStatus.length === 0
                      ? "Clean"
                      : `${snapshot.gitStatus.length} changed items`}
                  </dd>
                </div>
              </dl>

              <div className="inspector-section">
                <Link
                  className="open-focus"
                  href={`/focus/${encodeURIComponent(focus.id)}`}
                >
                  Open in Focus
                  <span>→</span>
                </Link>
              </div>

              <div className="inspector-section">
                <p className="section-label">Source</p>

                <code className="source-path">
                  {focus.artifactPath ?? focus.source}
                </code>
              </div>

              <div className="inspector-section">
                <p className="section-label">Outgoing</p>

                <div className="focus-relations">
                  {snapshot.focus.outgoing.length === 0 ? (
                    <p className="relation-empty">No outgoing trace edges.</p>
                  ) : (
                    snapshot.focus.outgoing.map((relation) => (
                      <Relation
                        direction="outgoing"
                        key={`${relation.relationship}:${relation.id}`}
                        relation={relation}
                      />
                    ))
                  )}
                </div>
              </div>

              <div className="inspector-section">
                <p className="section-label">Incoming</p>

                <div className="focus-relations">
                  {snapshot.focus.incoming.length === 0 ? (
                    <p className="relation-empty">No incoming trace edges.</p>
                  ) : (
                    snapshot.focus.incoming.map((relation) => (
                      <Relation
                        direction="incoming"
                        key={`${relation.relationship}:${relation.id}`}
                        relation={relation}
                      />
                    ))
                  )}
                </div>
              </div>

              {focus.id !== snapshot.execution.workPacket?.id ? (
                <div className="inspector-section">
                  <Link className="return-to-current" href="/">
                    Return to current Work Packet
                  </Link>
                </div>
              ) : null}
            </>
          ) : null}
        </>
      ) : null}
    </aside>
  );
}
