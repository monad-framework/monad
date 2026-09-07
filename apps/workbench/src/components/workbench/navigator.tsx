"use client";

import {
  Activity,
  BadgeCheck,
  Blocks,
  BookOpen,
  CircleDot,
  ClipboardCheck,
  FileCheck2,
  FileKey,
  Flag,
  Gauge,
  GitBranch,
  Layers3,
  ListChecks,
  type LucideIcon,
  Milestone,
  PackageCheck,
  PanelLeftClose,
  PanelLeftOpen,
  PlayCircle,
  Repeat2,
  Rocket,
  ScanSearch,
  ShieldAlert,
  ShieldCheck,
  Target,
  TriangleAlert,
  Workflow,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

type NavigatorProps = {
  collapsed: boolean;
  focusId?: string;
  onToggle: () => void;
};

type NavigationItem = {
  label: string;
  icon: LucideIcon;
  href: string;
};

type NavigationGroup = {
  label: string;
  items: NavigationItem[];
};

function workspaceItems(focusId?: string): NavigationItem[] {
  return [
    { label: "Now", icon: Gauge, href: "/" },
    { label: "Attention", icon: ShieldAlert, href: "/attention" },
    { label: "Plan", icon: GitBranch, href: "/plan" },
    { label: "Execution", icon: PlayCircle, href: "/execution" },
    { label: "Knowledge", icon: BookOpen, href: "/knowledge" },
    { label: "Control", icon: ShieldCheck, href: "/control" },
    {
      label: "Focus",
      icon: ScanSearch,
      href: focusId ? `/focus/${encodeURIComponent(focusId)}` : "/",
    },
  ];
}

const groups: NavigationGroup[] = [
  {
    label: "Product",
    items: [
      { label: "Product Goals", icon: Target, href: "/plan#product-goals" },
      { label: "Initiatives", icon: Flag, href: "/plan#product-goals" },
      { label: "Epics", icon: Layers3, href: "/plan#product-goals" },
      { label: "Features", icon: Blocks, href: "/plan#product-goals" },
      {
        label: "Stories & Enablers",
        icon: ListChecks,
        href: "/plan#product-goals",
      },
    ],
  },
  {
    label: "Execution",
    items: [
      {
        label: "Program Increments",
        icon: Milestone,
        href: "/execution#execution-hierarchy",
      },
      {
        label: "Work Cycles",
        icon: Repeat2,
        href: "/execution#execution-hierarchy",
      },
      {
        label: "Work Packets",
        icon: PackageCheck,
        href: "/execution#execution-hierarchy",
      },
      {
        label: "Executions",
        icon: PlayCircle,
        href: "/execution#execution-hierarchy",
      },
    ],
  },
  {
    label: "Knowledge",
    items: [
      {
        label: "Requirements",
        icon: FileCheck2,
        href: "/knowledge?kind=requirement",
      },
      {
        label: "Specifications",
        icon: FileKey,
        href: "/knowledge?kind=specification",
      },
      { label: "ADRs", icon: CircleDot, href: "/knowledge?kind=adr" },
      {
        label: "Policies",
        icon: ShieldCheck,
        href: "/knowledge?kind=policy",
      },
      {
        label: "Evidence",
        icon: BadgeCheck,
        href: "/knowledge?kind=evidence",
      },
    ],
  },
  {
    label: "Control",
    items: [
      { label: "Risks", icon: TriangleAlert, href: "/control#risks" },
      { label: "Changes", icon: Workflow, href: "/control#changes" },
      { label: "Reviews", icon: ClipboardCheck, href: "/control#reviews" },
      {
        label: "Verification",
        icon: Activity,
        href: "/control#verification",
      },
      { label: "Releases", icon: Rocket, href: "/control#releases" },
    ],
  },
];

function routePath(href: string): string {
  return href.split(/[?#]/, 1)[0] ?? href;
}

function isActiveRoute(pathname: string, href: string): boolean {
  const target = routePath(href);

  if (target === "/") {
    return pathname === "/";
  }

  return pathname === target || pathname.startsWith(`${target}/`);
}

export function Navigator({ collapsed, focusId, onToggle }: NavigatorProps) {
  const pathname = usePathname();
  const workspace = workspaceItems(focusId);

  return (
    <aside className="navigator">
      <div className="side-panel-toolbar">
        {!collapsed ? <span>Navigator</span> : null}

        <button
          aria-label={collapsed ? "Expand navigator" : "Collapse navigator"}
          className="side-panel-toggle"
          onClick={onToggle}
          title={collapsed ? "Expand navigator" : "Collapse navigator"}
          type="button"
        >
          {collapsed ? (
            <PanelLeftOpen size={15} />
          ) : (
            <PanelLeftClose size={15} />
          )}
        </button>
      </div>

      <div className="navigator-section">
        {!collapsed ? <p className="section-label">Workspace</p> : null}

        <nav aria-label="Workbench" className="primary-navigation">
          {workspace.map((item) => {
            const Icon = item.icon;
            const active = isActiveRoute(pathname, item.href);

            return (
              <Link
                className={active ? "nav-item active" : "nav-item"}
                href={item.href}
                key={item.label}
                title={collapsed ? item.label : undefined}
              >
                <Icon className="navigation-icon" size={15} />
                {!collapsed ? <span>{item.label}</span> : null}
              </Link>
            );
          })}
        </nav>
      </div>

      {groups.map((group) => (
        <div className="navigator-section" key={group.label}>
          {!collapsed ? (
            <p className="section-label">{group.label}</p>
          ) : (
            <div className="collapsed-group-divider" />
          )}

          <div className="context-navigation">
            {group.items.map((item) => {
              const Icon = item.icon;
              const active = isActiveRoute(pathname, item.href);

              return (
                <Link
                  className={active ? "context-item active" : "context-item"}
                  href={item.href}
                  key={item.label}
                  title={item.label}
                >
                  <Icon className="navigation-icon" size={14} />
                  {!collapsed ? <span>{item.label}</span> : null}
                </Link>
              );
            })}
          </div>
        </div>
      ))}
    </aside>
  );
}
