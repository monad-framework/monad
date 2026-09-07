"use client";

import {
  Activity,
  Clock3,
  Eye,
  EyeOff,
  RotateCcw,
  ShieldAlert,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import type {
  AttentionCondition,
  AttentionProjection,
  AutonomousWorkstream,
} from "@/lib/monad/attention-model";
import type { RepositorySnapshot } from "@/lib/monad/model";

type AttentionWorkspaceProps = {
  attention: AttentionProjection;
  snapshot: RepositorySnapshot;
};

type AttentionView = "active" | "activity" | "all";

type ConditionUiState = {
  readAt?: string;
  dismissedAt?: string;
  snoozedUntil?: string;
};

type AttentionUiStore = {
  view: AttentionView;
  showHidden: boolean;
  conditions: Record<string, ConditionUiState>;
};

const STORE_KEY = "monad-workbench:attention-ui:v1";
const DEFAULT_STORE: AttentionUiStore = {
  view: "active",
  showHidden: false,
  conditions: {},
};

function loadStore(): AttentionUiStore {
  if (typeof window === "undefined") return DEFAULT_STORE;

  try {
    const raw = window.localStorage.getItem(STORE_KEY);
    if (!raw) return DEFAULT_STORE;
    const parsed = JSON.parse(raw) as Partial<AttentionUiStore>;

    return {
      view:
        parsed.view === "active" ||
        parsed.view === "activity" ||
        parsed.view === "all"
          ? parsed.view
          : "active",
      showHidden: parsed.showHidden === true,
      conditions: parsed.conditions ?? {},
    };
  } catch {
    return DEFAULT_STORE;
  }
}

function persistStore(store: AttentionUiStore) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORE_KEY, JSON.stringify(store));
}

function isConditionHidden(
  state: ConditionUiState | undefined,
  now: number,
): boolean {
  if (!state) return false;
  if (state.dismissedAt) return true;
  if (!state.snoozedUntil) return false;

  const snoozedUntil = Date.parse(state.snoozedUntil);
  return Number.isFinite(snoozedUntil) && snoozedUntil > now;
}

function conditionStateClass(condition: AttentionCondition): string {
  return `attention-state ${condition.severity}`;
}

function conditionTarget(condition: AttentionCondition) {
  const href = condition.affectedObject.href;
  const label = condition.affectedObject.title
    ? `${condition.affectedObject.id} · ${condition.affectedObject.title}`
    : condition.affectedObject.id;

  if (!href) {
    return <strong>{label}</strong>;
  }

  return (
    <Link className="attention-object-link" href={href}>
      {label}
    </Link>
  );
}

function AttentionConditionCard({
  condition,
  localState,
  hidden,
  onRead,
  onDismiss,
  onSnooze,
  onRestore,
}: {
  condition: AttentionCondition;
  localState?: ConditionUiState;
  hidden: boolean;
  onRead: () => void;
  onDismiss: () => void;
  onSnooze: () => void;
  onRestore: () => void;
}) {
  const unread = !localState?.readAt;

  return (
    <article
      className={[
        "attention-condition",
        unread ? "unread" : "",
        hidden ? "locally-hidden" : "",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <div className="attention-condition-heading">
        <div>
          <span className={conditionStateClass(condition)}>
            {condition.state.replaceAll("_", " ")}
          </span>
          <span className="attention-classification">
            {condition.classification.replace("-", " ")}
          </span>
        </div>
        {unread ? <span className="attention-unread-dot">Unread</span> : null}
      </div>

      <h3>{condition.title}</h3>
      <div className="attention-target">{conditionTarget(condition)}</div>
      <p>{condition.reason}</p>

      <dl className="attention-provenance">
        <div>
          <dt>Source</dt>
          <dd>{condition.provenance.source}</dd>
        </div>
        <div>
          <dt>Provider</dt>
          <dd>{condition.provenance.provider}</dd>
        </div>
        <div>
          <dt>Freshness</dt>
          <dd>{condition.freshness}</dd>
        </div>
        <div>
          <dt>Observed</dt>
          <dd>
            {condition.provenance.observedAt ? (
              <time dateTime={condition.provenance.observedAt}>
                {condition.provenance.observedAt}
              </time>
            ) : (
              "current snapshot"
            )}
          </dd>
        </div>
      </dl>

      <div className="attention-condition-actions">
        {condition.action ? (
          <Link
            className="attention-primary-action"
            href={condition.action.href}
          >
            {condition.action.label}
          </Link>
        ) : null}

        {!hidden ? (
          <>
            <button disabled={!unread} onClick={onRead} type="button">
              <Eye size={13} />
              Mark read
            </button>
            <button onClick={onSnooze} type="button">
              <Clock3 size={13} />
              Snooze 1h
            </button>
            <button onClick={onDismiss} type="button">
              <EyeOff size={13} />
              Dismiss
            </button>
          </>
        ) : (
          <button onClick={onRestore} type="button">
            <RotateCcw size={13} />
            Restore
          </button>
        )}
      </div>
    </article>
  );
}

function WorkstreamCard({ stream }: { stream: AutonomousWorkstream }) {
  return (
    <article className="autonomous-workstream">
      <div className="autonomous-workstream-heading">
        <span className="section-label">{stream.group}</span>
        <span className="attention-state info">{stream.state}</span>
      </div>
      <h3>
        <Link href={stream.objectHref}>{stream.objectId}</Link>
        <span>{stream.label}</span>
      </h3>
      <p>{stream.reason}</p>
      <dl>
        {stream.latestExecutionId ? (
          <div>
            <dt>Execution</dt>
            <dd>{stream.latestExecutionId}</dd>
          </div>
        ) : null}
        {stream.authorization ? (
          <div>
            <dt>Authorization</dt>
            <dd>{stream.authorization.replace("_", " ")}</dd>
          </div>
        ) : null}
        <div>
          <dt>Source</dt>
          <dd>{stream.source}</dd>
        </div>
        <div>
          <dt>Updated</dt>
          <dd>{stream.updatedAt ?? "unknown"}</dd>
        </div>
      </dl>
    </article>
  );
}

export function AttentionWorkspace({
  attention,
  snapshot,
}: AttentionWorkspaceProps) {
  const [store, setStore] = useState<AttentionUiStore>(DEFAULT_STORE);
  const now = Date.now();

  useEffect(() => {
    setStore(loadStore());
  }, []);

  const needsAttention = useMemo(
    () =>
      attention.conditions.filter(
        (condition) =>
          condition.current && condition.classification !== "activity",
      ),
    [attention.conditions],
  );
  const historicalActivity = useMemo(
    () =>
      attention.conditions.filter(
        (condition) =>
          !condition.current || condition.classification === "activity",
      ),
    [attention.conditions],
  );
  const hiddenCount = needsAttention.filter((condition) =>
    isConditionHidden(store.conditions[condition.id], now),
  ).length;
  const visibleAttention = needsAttention.filter(
    (condition) =>
      store.showHidden ||
      !isConditionHidden(store.conditions[condition.id], now),
  );
  const unreadCount = visibleAttention.filter(
    (condition) => !store.conditions[condition.id]?.readAt,
  ).length;

  function setView(view: AttentionView) {
    setStore((current) => {
      const next = { ...current, view };
      persistStore(next);
      return next;
    });
  }

  function setShowHidden(showHidden: boolean) {
    setStore((current) => {
      const next = { ...current, showHidden };
      persistStore(next);
      return next;
    });
  }

  function updateCondition(
    id: string,
    update: (state: ConditionUiState) => ConditionUiState,
  ) {
    setStore((current) => {
      const next = {
        ...current,
        conditions: {
          ...current.conditions,
          [id]: update(current.conditions[id] ?? {}),
        },
      };
      persistStore(next);
      return next;
    });
  }

  return (
    <main className="workspace attention-workspace">
      <div className="workspace-header">
        <div>
          <p className="eyebrow">Operator attention projection</p>
          <h1>Attention Center</h1>
          <p className="workspace-description">
            Answers whether trusted Monad sources currently project anything
            that requires awareness or operator action. Attention records are
            projections; local read, dismiss, and snooze state never changes EOS
            lifecycle or engineering authority.
          </p>
        </div>
        <div className="branch-chip">
          <span className="status-dot" />
          {snapshot.branch}
        </div>
      </div>

      <div className="summary-grid attention-summary-grid" aria-live="polite">
        <div className="summary-card">
          <p className="card-label">Operator action</p>
          <strong>{attention.summary.operatorAction}</strong>
          <p>
            Explicit blocked, failed, integration-ready, or human-gated
            conditions.
          </p>
        </div>
        <div className="summary-card">
          <p className="card-label">Attention</p>
          <strong>{attention.summary.attention}</strong>
          <p>Current stale or drifted conditions that deserve inspection.</p>
        </div>
        <div className="summary-card">
          <p className="card-label">Unread visible</p>
          <strong>{unreadCount}</strong>
          <p>
            Local presentation state only; it is not engineering lifecycle
            state.
          </p>
        </div>
        <div className="summary-card">
          <p className="card-label">Autonomous running</p>
          <strong>{attention.summary.running}</strong>
          <p>
            Current workstreams whose trusted projection indicates active
            execution.
          </p>
        </div>
      </div>

      <fieldset
        aria-label="Attention Center view filters"
        className="attention-toolbar"
      >
        <div>
          {(["active", "activity", "all"] as const).map((view) => (
            <button
              aria-pressed={store.view === view}
              className={store.view === view ? "active" : ""}
              key={view}
              onClick={() => setView(view)}
              type="button"
            >
              {view === "active"
                ? "Needs attention"
                : view === "activity"
                  ? "Activity"
                  : "All"}
            </button>
          ))}
        </div>
        <button
          aria-pressed={store.showHidden}
          className={store.showHidden ? "active" : ""}
          disabled={hiddenCount === 0}
          onClick={() => setShowHidden(!store.showHidden)}
          type="button"
        >
          {store.showHidden
            ? "Hide local dismissals"
            : `Show hidden (${hiddenCount})`}
        </button>
      </fieldset>

      {store.view !== "activity" ? (
        <section
          aria-labelledby="needs-attention-heading"
          className="panel attention-section"
        >
          <div className="panel-heading">
            <div>
              <p className="section-label">Current conditions</p>
              <h2 id="needs-attention-heading">Needs attention</h2>
            </div>
            <span className="count-badge">{visibleAttention.length}</span>
          </div>

          {visibleAttention.length > 0 ? (
            <div className="attention-condition-list">
              {visibleAttention.map((condition) => {
                const localState = store.conditions[condition.id];
                const hidden = isConditionHidden(localState, now);

                return (
                  <AttentionConditionCard
                    condition={condition}
                    hidden={hidden}
                    key={condition.id}
                    localState={localState}
                    onDismiss={() =>
                      updateCondition(condition.id, (state) => ({
                        ...state,
                        dismissedAt: new Date().toISOString(),
                      }))
                    }
                    onRead={() =>
                      updateCondition(condition.id, (state) => ({
                        ...state,
                        readAt: new Date().toISOString(),
                      }))
                    }
                    onRestore={() =>
                      updateCondition(condition.id, (state) => ({
                        ...state,
                        dismissedAt: undefined,
                        snoozedUntil: undefined,
                      }))
                    }
                    onSnooze={() =>
                      updateCondition(condition.id, (state) => ({
                        ...state,
                        snoozedUntil: new Date(
                          Date.now() + 60 * 60 * 1000,
                        ).toISOString(),
                      }))
                    }
                  />
                );
              })}
            </div>
          ) : (
            <div className="empty-state attention-empty-state">
              <ShieldAlert size={18} />
              <div>
                <strong>
                  No visible active condition requires operator attention.
                </strong>
                <p>
                  Workbench is not claiming there is no work. It is reporting
                  that its trusted providers currently project no non-hidden
                  attention-worthy condition.
                </p>
              </div>
            </div>
          )}
        </section>
      ) : null}

      {store.view !== "activity" ? (
        <section
          aria-labelledby="autonomous-work-heading"
          className="panel attention-section"
        >
          <div className="panel-heading">
            <div>
              <p className="section-label">Autonomous work</p>
              <h2 id="autonomous-work-heading">Current workstreams</h2>
            </div>
            <span className="count-badge">{attention.workstreams.length}</span>
          </div>

          {attention.workstreams.length > 0 ? (
            <div className="autonomous-workstream-grid">
              {attention.workstreams.map((stream) => (
                <WorkstreamCard key={stream.id} stream={stream} />
              ))}
            </div>
          ) : (
            <div className="empty-state attention-empty-state">
              <Activity size={18} />
              <div>
                <strong>
                  No autonomous workstream is currently observable.
                </strong>
                <p>
                  Workstreams appear when trusted execution/lifecycle providers
                  expose non-terminal governed work.
                </p>
              </div>
            </div>
          )}
        </section>
      ) : null}

      {store.view !== "active" ? (
        <section
          aria-labelledby="attention-activity-heading"
          className="panel attention-section"
        >
          <div className="panel-heading">
            <div>
              <p className="section-label">Historical and informational</p>
              <h2 id="attention-activity-heading">Activity</h2>
            </div>
            <span className="count-badge">{historicalActivity.length}</span>
          </div>

          {historicalActivity.length > 0 ? (
            <div className="attention-activity-list">
              {historicalActivity.map((condition) => (
                <article className="attention-activity-row" key={condition.id}>
                  <span className={conditionStateClass(condition)}>
                    {condition.state.replaceAll("_", " ")}
                  </span>
                  <div>
                    {conditionTarget(condition)}
                    <p>{condition.reason}</p>
                  </div>
                  <span>{condition.provenance.observedAt ?? "snapshot"}</span>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              No historical activity is projected.
            </div>
          )}
        </section>
      ) : null}

      <section
        aria-labelledby="attention-providers-heading"
        className="panel attention-section attention-providers"
      >
        <div className="panel-heading">
          <div>
            <p className="section-label">Projection provenance</p>
            <h2 id="attention-providers-heading">Trusted sources</h2>
          </div>
          <span className="count-badge">{attention.sources.length}</span>
        </div>
        <div className="attention-source-list">
          {attention.sources.map((source) => (
            <code key={source}>{source}</code>
          ))}
        </div>
      </section>
    </main>
  );
}
