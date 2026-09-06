import type { RepositorySnapshot } from "@/lib/monad/model";

import { Inspector } from "./inspector";
import { Navigator } from "./navigator";
import { Workspace } from "./workspace";

type AppShellProps = {
  snapshot: RepositorySnapshot;
};

export function AppShell({ snapshot }: AppShellProps) {
  return (
    <div className="workbench">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">M</span>

          <div>
            <strong>Monad</strong>
            <span>Workbench</span>
          </div>
        </div>

        <div className="topbar-context">
          <span>Repository</span>
          <span className="context-separator">/</span>
          <strong>{snapshot.branch}</strong>
        </div>

        <button className="command-button" type="button">
          Search
          <kbd>⌘K</kbd>
        </button>
      </header>

      <div className="workbench-body">
        <Navigator />
        <Workspace snapshot={snapshot} />
        <Inspector snapshot={snapshot} />
      </div>

      <footer className="statusbar">
        <span>Monad Workbench v0</span>
        <span>{snapshot.branch}</span>
        <span>{snapshot.gitStatus.length} working-tree changes</span>
      </footer>
    </div>
  );
}
