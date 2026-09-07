"use client";

import {
  ChevronRight,
  Copy,
  FileText,
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightClose,
  PanelRightOpen,
  RefreshCw,
  RotateCcw,
} from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import type { MouseEvent as ReactMouseEvent, ReactNode } from "react";
import { useCallback, useEffect, useRef, useState } from "react";

import type { RepositorySnapshot } from "@/lib/monad/model";

import { Inspector } from "./inspector";
import { Navigator } from "./navigator";

type AppShellProps = {
  snapshot: RepositorySnapshot;
  children: ReactNode;
};

type ContextMenuState = {
  open: boolean;
  x: number;
  y: number;
};

type MenuName = "file" | "edit" | "view" | "navigate" | "help";

const LEFT_PANEL_KEY = "monad-workbench:left-collapsed";

const RIGHT_PANEL_KEY = "monad-workbench:right-collapsed";

export function AppShell({ snapshot, children }: AppShellProps) {
  const router = useRouter();
  const pathname = usePathname();

  const [leftCollapsed, setLeftCollapsed] = useState(false);

  const [rightCollapsed, setRightCollapsed] = useState(false);

  const [activeMenu, setActiveMenu] = useState<MenuName | null>(null);

  const [contextMenu, setContextMenu] = useState<ContextMenuState>({
    open: false,
    x: 0,
    y: 0,
  });

  const menuRef = useRef<HTMLDivElement>(null);

  const focus = snapshot.focus.object;

  useEffect(() => {
    setLeftCollapsed(window.localStorage.getItem(LEFT_PANEL_KEY) === "true");

    setRightCollapsed(window.localStorage.getItem(RIGHT_PANEL_KEY) === "true");
  }, []);

  const toggleLeft = useCallback(() => {
    setLeftCollapsed((current) => {
      const next = !current;

      window.localStorage.setItem(LEFT_PANEL_KEY, String(next));

      return next;
    });
  }, []);

  const toggleRight = useCallback(() => {
    setRightCollapsed((current) => {
      const next = !current;

      window.localStorage.setItem(RIGHT_PANEL_KEY, String(next));

      return next;
    });
  }, []);

  const closeMenus = useCallback(() => {
    setActiveMenu(null);

    setContextMenu((current) => ({
      ...current,
      open: false,
    }));
  }, []);

  const copyText = useCallback(async (value?: string) => {
    if (!value) {
      return;
    }

    await navigator.clipboard.writeText(value);
  }, []);

  const openCurrentFocus = useCallback(() => {
    if (!focus) {
      return;
    }

    router.push(`/focus/${encodeURIComponent(focus.id)}`);
  }, [focus, router]);

  const handleContextMenu = useCallback(
    (event: ReactMouseEvent<HTMLDivElement>) => {
      event.preventDefault();

      const width = 238;
      const height = 290;

      const x = Math.max(
        8,
        Math.min(event.clientX, window.innerWidth - width - 8),
      );

      const y = Math.max(
        8,
        Math.min(event.clientY, window.innerHeight - height - 8),
      );

      setActiveMenu(null);

      setContextMenu({
        open: true,
        x,
        y,
      });
    },
    [],
  );

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        closeMenus();
        return;
      }

      const command = event.metaKey || event.ctrlKey;

      if (command && !event.shiftKey && event.key.toLowerCase() === "b") {
        event.preventDefault();
        toggleLeft();
      }

      if (command && event.shiftKey && event.key.toLowerCase() === "b") {
        event.preventDefault();
        toggleRight();
      }
    }

    function handlePointerDown(event: MouseEvent) {
      const target = event.target instanceof Element ? event.target : null;

      if (target?.closest(".context-menu")) {
        return;
      }

      if (menuRef.current?.contains(event.target as Node)) {
        return;
      }

      closeMenus();
    }

    window.addEventListener("keydown", handleKeyDown);

    window.addEventListener("mousedown", handlePointerDown);

    window.addEventListener("resize", closeMenus);

    window.addEventListener("scroll", closeMenus, true);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);

      window.removeEventListener("mousedown", handlePointerDown);

      window.removeEventListener("resize", closeMenus);

      window.removeEventListener("scroll", closeMenus, true);
    };
  }, [closeMenus, toggleLeft, toggleRight]);

  const shellClassName = [
    "workbench",
    leftCollapsed ? "navigator-collapsed" : "",
    rightCollapsed ? "inspector-collapsed" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const activeTab =
    pathname === "/plan"
      ? "Plan"
      : pathname.startsWith("/focus/") && focus
        ? focus.id
        : "Now";

  return (
    <div
      className={shellClassName}
      onContextMenu={handleContextMenu}
      role="application"
    >
      <div className="application-menu-bar">
        <div className="application-menus" ref={menuRef}>
          <MenuButton
            active={activeMenu === "file"}
            label="File"
            onClick={() =>
              setActiveMenu((current) => (current === "file" ? null : "file"))
            }
          />

          <MenuButton
            active={activeMenu === "edit"}
            label="Edit"
            onClick={() =>
              setActiveMenu((current) => (current === "edit" ? null : "edit"))
            }
          />

          <MenuButton
            active={activeMenu === "view"}
            label="View"
            onClick={() =>
              setActiveMenu((current) => (current === "view" ? null : "view"))
            }
          />

          <MenuButton
            active={activeMenu === "navigate"}
            label="Navigate"
            onClick={() =>
              setActiveMenu((current) =>
                current === "navigate" ? null : "navigate",
              )
            }
          />

          <MenuButton
            active={activeMenu === "help"}
            label="Help"
            onClick={() =>
              setActiveMenu((current) => (current === "help" ? null : "help"))
            }
          />

          {activeMenu ? (
            <ApplicationMenu
              focusId={focus?.id}
              leftCollapsed={leftCollapsed}
              menu={activeMenu}
              onClose={closeMenus}
              onCopyFocus={() => copyText(focus?.id)}
              onCopySource={() =>
                copyText(focus?.artifactPath ?? focus?.source)
              }
              onFocus={openCurrentFocus}
              onNow={() => router.push("/")}
              onPlan={() => router.push("/plan")}
              onRefresh={() => router.refresh()}
              onToggleLeft={toggleLeft}
              onToggleRight={toggleRight}
              rightCollapsed={rightCollapsed}
            />
          ) : null}
        </div>

        <span className="application-title">Monad Workbench</span>
      </div>

      <div className="tab-bar">
        <div className="tabs">
          <button className="workbench-tab active" type="button">
            <FileText size={13} />
            <span>{activeTab}</span>
          </button>
        </div>

        <button
          aria-label="New tab"
          className="new-tab-button"
          title="Tab support will be added later"
          type="button"
        >
          +
        </button>
      </div>

      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">M</span>

          <div className="brand-text">
            <strong>Monad</strong>
            <span>Workbench</span>
          </div>
        </div>

        <div className="topbar-context">
          <span>Monad</span>

          <span className="context-separator">/</span>

          <strong>{activeTab}</strong>

          <span className="context-separator">/</span>

          <span>{snapshot.branch}</span>
        </div>

        <button className="command-button" type="button">
          Search
          <kbd>⌘K</kbd>
        </button>
      </header>

      <div className="workbench-body">
        <Navigator collapsed={leftCollapsed} onToggle={toggleLeft} />

        {children}

        <Inspector
          collapsed={rightCollapsed}
          onToggle={toggleRight}
          snapshot={snapshot}
        />
      </div>

      <footer className="statusbar">
        <span>Monad Workbench v0</span>

        <span>{snapshot.branch}</span>

        <span>{snapshot.gitStatus.length} working-tree changes</span>
      </footer>

      {contextMenu.open ? (
        <ContextMenu
          focusId={focus?.id}
          leftCollapsed={leftCollapsed}
          onClose={closeMenus}
          onCopyFocus={() => copyText(focus?.id)}
          onCopySource={() => copyText(focus?.artifactPath ?? focus?.source)}
          onFocus={openCurrentFocus}
          onNow={() => router.push("/")}
          onRefresh={() => router.refresh()}
          onToggleLeft={toggleLeft}
          onToggleRight={toggleRight}
          rightCollapsed={rightCollapsed}
          x={contextMenu.x}
          y={contextMenu.y}
        />
      ) : null}
    </div>
  );
}

type MenuButtonProps = {
  label: string;
  active: boolean;
  onClick: () => void;
};

function MenuButton({ label, active, onClick }: MenuButtonProps) {
  return (
    <button
      className={
        active ? "application-menu-button active" : "application-menu-button"
      }
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  );
}

type ApplicationMenuProps = {
  menu: MenuName;
  focusId?: string;
  leftCollapsed: boolean;
  rightCollapsed: boolean;
  onClose: () => void;
  onNow: () => void;
  onPlan: () => void;
  onFocus: () => void;
  onRefresh: () => void;
  onCopyFocus: () => void;
  onCopySource: () => void;
  onToggleLeft: () => void;
  onToggleRight: () => void;
};

function ApplicationMenu(props: ApplicationMenuProps) {
  const items =
    props.menu === "file"
      ? [
          {
            label: "Go to Now",
            action: props.onNow,
          },
          {
            label: "Refresh Workspace",
            action: props.onRefresh,
          },
        ]
      : props.menu === "edit"
        ? [
            {
              label: "Copy Focus ID",
              action: props.onCopyFocus,
              disabled: !props.focusId,
            },
            {
              label: "Copy Source Path",
              action: props.onCopySource,
              disabled: !props.focusId,
            },
          ]
        : props.menu === "view"
          ? [
              {
                label: props.leftCollapsed
                  ? "Show Navigator"
                  : "Hide Navigator",
                action: props.onToggleLeft,
              },
              {
                label: props.rightCollapsed
                  ? "Show Inspector"
                  : "Hide Inspector",
                action: props.onToggleRight,
              },
            ]
          : props.menu === "navigate"
            ? [
                {
                  label: "Now",
                  action: props.onNow,
                },
                {
                  label: "Plan",
                  action: props.onPlan,
                },
                {
                  label: "Open Focus",
                  action: props.onFocus,
                  disabled: !props.focusId,
                },
              ]
            : [
                {
                  label: "Monad Workbench v0",
                  disabled: true,
                  action: () => {},
                },
              ];

  return (
    <div className="application-menu-dropdown" role="menu">
      {items.map((item) => (
        <button
          disabled={item.disabled}
          key={item.label}
          onClick={() => {
            item.action();
            props.onClose();
          }}
          role="menuitem"
          type="button"
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}

type ContextMenuProps = {
  x: number;
  y: number;
  focusId?: string;
  leftCollapsed: boolean;
  rightCollapsed: boolean;
  onClose: () => void;
  onNow: () => void;
  onFocus: () => void;
  onRefresh: () => void;
  onCopyFocus: () => void;
  onCopySource: () => void;
  onToggleLeft: () => void;
  onToggleRight: () => void;
};

function ContextMenu({
  x,
  y,
  focusId,
  leftCollapsed,
  rightCollapsed,
  onClose,
  onNow,
  onFocus,
  onRefresh,
  onCopyFocus,
  onCopySource,
  onToggleLeft,
  onToggleRight,
}: ContextMenuProps) {
  function run(action: () => void) {
    action();
    onClose();
  }

  return (
    <div
      className="context-menu"
      onContextMenu={(event) => event.preventDefault()}
      role="menu"
      style={{
        left: x,
        top: y,
      }}
    >
      <button
        disabled={!focusId}
        onClick={() => run(onFocus)}
        role="menuitem"
        type="button"
      >
        <ChevronRight size={14} />
        Open in Focus
      </button>

      <button onClick={() => run(onNow)} role="menuitem" type="button">
        <RotateCcw size={14} />
        Back to Now
      </button>

      <hr className="context-menu-separator" style={{ border: 0 }} />

      <button
        disabled={!focusId}
        onClick={() => run(onCopyFocus)}
        role="menuitem"
        type="button"
      >
        <Copy size={14} />
        Copy Focus ID
      </button>

      <button
        disabled={!focusId}
        onClick={() => run(onCopySource)}
        role="menuitem"
        type="button"
      >
        <FileText size={14} />
        Copy Source Path
      </button>

      <hr className="context-menu-separator" style={{ border: 0 }} />

      <button onClick={() => run(onToggleLeft)} role="menuitem" type="button">
        {leftCollapsed ? (
          <PanelLeftOpen size={14} />
        ) : (
          <PanelLeftClose size={14} />
        )}

        {leftCollapsed ? "Show Navigator" : "Hide Navigator"}
      </button>

      <button onClick={() => run(onToggleRight)} role="menuitem" type="button">
        {rightCollapsed ? (
          <PanelRightOpen size={14} />
        ) : (
          <PanelRightClose size={14} />
        )}

        {rightCollapsed ? "Show Inspector" : "Hide Inspector"}
      </button>

      <hr className="context-menu-separator" style={{ border: 0 }} />

      <button onClick={() => run(onRefresh)} role="menuitem" type="button">
        <RefreshCw size={14} />
        Refresh Workspace
      </button>
    </div>
  );
}
