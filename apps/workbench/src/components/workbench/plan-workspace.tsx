import type { RepositorySnapshot } from "@/lib/monad/model";
import type {
  PlanEpic,
  PlanFeature,
  PlanInitiative,
  PlanProductGoal,
  PlanProjection,
  PlanStory,
} from "@/lib/monad/plan";

type PlanWorkspaceProps = {
  plan: PlanProjection;
  snapshot: RepositorySnapshot;
};

type CurrentIds = {
  productGoal?: string;
  initiative?: string;
  epic?: string;
  feature?: string;
  stories: Set<string>;
};

function CurrentBadge({ current }: { current: boolean }) {
  if (!current) {
    return null;
  }

  return <span className="lifecycle-badge">Current</span>;
}

function StoryRow({ story, current }: { story: PlanStory; current: boolean }) {
  return (
    <div className="story-row" id={story.id}>
      <code>{story.id}</code>

      <span>
        {story.title}
        {story.kind === "enabler" ? " · Enabler" : ""}
        {current ? " · Current" : ""}
      </span>
    </div>
  );
}

function FeatureProjection({
  feature,
  currentIds,
}: {
  feature: PlanFeature;
  currentIds: CurrentIds;
}) {
  const current = feature.id === currentIds.feature;

  return (
    <details id={feature.id} open={current}>
      <summary className="context-object context-object-link">
        <div>
          <code>{feature.id}</code>

          <strong>{feature.title}</strong>
        </div>

        <CurrentBadge current={current} />
      </summary>

      <div className="story-section">
        <dl className="focus-metadata">
          <div>
            <dt>Work Packet</dt>
            <dd>{feature.workPacket ?? "Not forecast"}</dd>
          </div>

          <div>
            <dt>Work Cycle</dt>
            <dd>{feature.workCycle ?? "Not forecast"}</dd>
          </div>

          <div>
            <dt>Stories / Enablers</dt>
            <dd>{feature.stories.length}</dd>
          </div>

          <div>
            <dt>Source</dt>
            <dd>
              <code>{feature.source}</code>
            </dd>
          </div>
        </dl>

        {feature.stories.length > 0 ? (
          <div className="story-list">
            {feature.stories.map((story) => (
              <StoryRow
                current={currentIds.stories.has(story.id)}
                key={story.id}
                story={story}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>No Story or Enabler records were resolved.</p>
          </div>
        )}

        <div className="empty-state">
          <p>
            Detailed implementation Tasks remain rolling-wave and are refined
            before the corresponding Work Packet becomes Ready.
          </p>
        </div>
      </div>
    </details>
  );
}

function EpicProjection({
  epic,
  currentIds,
}: {
  epic: PlanEpic;
  currentIds: CurrentIds;
}) {
  const current = epic.id === currentIds.epic;

  return (
    <details id={epic.id} open={current}>
      <summary className="context-object context-object-link">
        <div>
          <code>{epic.id}</code>

          <strong>{epic.title}</strong>
        </div>

        <span className="count-badge">{epic.features.length}</span>
      </summary>

      <div className="story-section">
        <CurrentBadge current={current} />

        {epic.features.length > 0 ? (
          <div className="context-stack">
            {epic.features.map((feature) => (
              <FeatureProjection
                currentIds={currentIds}
                feature={feature}
                key={feature.id}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>No Features were resolved for this Epic.</p>
          </div>
        )}
      </div>
    </details>
  );
}

function InitiativeProjection({
  initiative,
  currentIds,
}: {
  initiative: PlanInitiative;
  currentIds: CurrentIds;
}) {
  const current = initiative.id === currentIds.initiative;

  return (
    <details id={initiative.id} open={current}>
      <summary className="context-object context-object-link">
        <div>
          <code>{initiative.id}</code>

          <strong>{initiative.title}</strong>
        </div>

        <span className="count-badge">{initiative.epics.length}</span>
      </summary>

      <div className="story-section">
        <CurrentBadge current={current} />

        {initiative.outcome ? (
          <div className="focus-copy">{initiative.outcome}</div>
        ) : null}

        {initiative.epics.length > 0 ? (
          <div className="context-stack">
            {initiative.epics.map((epic) => (
              <EpicProjection
                currentIds={currentIds}
                epic={epic}
                key={epic.id}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>No Epics were resolved for this Initiative.</p>
          </div>
        )}

        {initiative.exitCondition ? (
          <section className="panel focus-document-block">
            <div className="panel-heading">
              <div>
                <p className="section-label">Completion</p>

                <h2>Exit condition</h2>
              </div>
            </div>

            <div className="focus-copy">{initiative.exitCondition}</div>
          </section>
        ) : null}
      </div>
    </details>
  );
}

function GoalProjection({
  goal,
  currentIds,
}: {
  goal: PlanProductGoal;
  currentIds: CurrentIds;
}) {
  const current = goal.id === currentIds.productGoal;

  return (
    <details id={goal.id} open={current}>
      <summary className="context-object context-object-link">
        <div>
          <code>{goal.id}</code>

          <strong>{goal.title}</strong>
        </div>

        <span className="count-badge">{goal.initiatives.length}</span>
      </summary>

      <div className="story-section">
        <CurrentBadge current={current} />

        <div className="context-stack">
          {goal.initiatives.map((initiative) => (
            <InitiativeProjection
              currentIds={currentIds}
              initiative={initiative}
              key={initiative.id}
            />
          ))}
        </div>
      </div>
    </details>
  );
}

export function PlanWorkspace({ plan, snapshot }: PlanWorkspaceProps) {
  const currentIds: CurrentIds = {
    productGoal: snapshot.product.productGoal?.id,
    initiative: snapshot.product.initiative?.id,
    epic: snapshot.product.epic?.id,
    feature: snapshot.product.feature?.id,
    stories: new Set([
      ...snapshot.product.stories.map((story) => story.id),
      ...snapshot.product.enablers.map((enabler) => enabler.id),
    ]),
  };

  return (
    <main className="workspace">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">Monad / Plan</p>

          <h1>Product planning hierarchy</h1>

          <p className="workspace-description">
            Canonical Product Goal → Initiative → Epic → Feature → Story /
            Enabler projection. Governed execution remains a separate orthogonal
            dimension.
          </p>
        </div>

        <div className="branch-chip">
          <span className="status-dot" />
          {snapshot.branch}
        </div>
      </header>

      <section className="summary-grid">
        <article className="summary-card">
          <p className="card-label">Product Goals</p>

          <strong>{plan.counts.productGoals}</strong>

          <p>Canonical product outcomes.</p>
        </article>

        <article className="summary-card">
          <p className="card-label">Initiatives</p>

          <strong>{plan.counts.initiatives}</strong>

          <p>Finite outcome-oriented program initiatives.</p>
        </article>

        <article className="summary-card">
          <p className="card-label">Epics / Features</p>

          <strong>
            {plan.counts.epics} / {plan.counts.features}
          </strong>

          <p>Roadmap decomposition from capability to engineering outcome.</p>
        </article>

        <article className="summary-card">
          <p className="card-label">Stories / Enablers</p>

          <strong>
            {plan.counts.stories} / {plan.counts.enablers}
          </strong>

          <p>Stable backlog identifiers; Tasks remain rolling-wave.</p>
        </article>
      </section>

      <section className="panel focus-document-block" id="product-goals">
        <div className="panel-heading">
          <div>
            <p className="section-label">Product</p>

            <h2>Canonical hierarchy</h2>
          </div>

          <span className="count-badge">{plan.goals.length}</span>
        </div>

        <div className="context-stack">
          {plan.goals.map((goal) => (
            <GoalProjection currentIds={currentIds} goal={goal} key={goal.id} />
          ))}
        </div>
      </section>

      <section className="panel focus-source-panel">
        <div className="panel-heading">
          <div>
            <p className="section-label">Provenance</p>

            <h2>Planning sources</h2>
          </div>
        </div>

        <dl className="focus-metadata">
          {plan.sources.map((source) => (
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
