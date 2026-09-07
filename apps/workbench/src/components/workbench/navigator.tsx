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
  ShieldCheck,
  Target,
  TriangleAlert,
  Workflow,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

type NavigatorProps = {
  collapsed: boolean;
  onToggle: () => void;
};

type NavigationItem = {
  label: string;
  icon: LucideIcon;
  href?: string;
};

type NavigationGroup = {
  label: string;
  items: NavigationItem[];
};

const workspace: NavigationItem[] = [
  {
    label: "Now",
    icon: Gauge,
    href: "/",
  },
  {
    label: "Plan",
    icon: GitBranch,
    href: "/plan",
  },
  {
    label: "Knowledge",
    icon: BookOpen,
  },
  {
    label: "Focus",
    icon: ScanSearch,
  },
];

const groups: NavigationGroup[] = [
  {
    label: "Product",
    items: [
      {
        label: "Product Goals",
        icon: Target,
        href: "/plan",
      },
      {
        label: "Initiatives",
        icon: Flag,
        href: "/plan",
      },
      {
        label: "Epics",
        icon: Layers3,
        href: "/plan",
      },
      {
        label: "Features",
        icon: Blocks,
        href: "/plan",
      },
      {
        label: "Stories & Enablers",
        icon: ListChecks,
        href: "/plan",
      },
    ],
  },
  {
    label: "Execution",
    items: [
      {
        label: "Program Increments",
        icon: Milestone,
      },
      {
        label: "Work Cycles",
        icon: Repeat2,
      },
      {
        label: "Work Packets",
        icon: PackageCheck,
      },
      {
        label: "Executions",
        icon: PlayCircle,
      },
    ],
  },
  {
    label: "Knowledge",
    items: [
      {
        label: "Requirements",
        icon: FileCheck2,
      },
      {
        label: "Specifications",
        icon: FileKey,
      },
      {
        label: "ADRs",
        icon: CircleDot,
      },
      {
        label: "Policies",
        icon: ShieldCheck,
      },
      {
        label: "Evidence",
        icon: BadgeCheck,
      },
    ],
  },
  {
    label: "Control",
    items: [
      {
        label: "Risks",
        icon: TriangleAlert,
      },
      {
        label: "Changes",
        icon: Workflow,
      },
      {
        label: "Reviews",
        icon: ClipboardCheck,
      },
      {
        label: "Verification",
        icon: Activity,
      },
      {
        label: "Releases",
        icon: Rocket,
      },
    ],
  },
];

function isActiveRoute(pathname: string, href: string): boolean {
  if (href === "/") {
    return pathname === "/";
  }

  return pathname === href || pathname.startsWith(`${href}/`);
}

export function Navigator({ collapsed, onToggle }: NavigatorProps) {
  const pathname = usePathname();

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
            const active = item.href
              ? isActiveRoute(pathname, item.href)
              : false;

            if (item.href) {
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
            }

            return (
              <button
                className="nav-item"
                disabled
                key={item.label}
                title={`${item.label} projection is not implemented yet`}
                type="button"
              >
                <Icon className="navigation-icon" size={15} />

                {!collapsed ? <span>{item.label}</span> : null}
              </button>
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

              if (item.href) {
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
              }

              return (
                <button
                  className="context-item"
                  disabled
                  key={item.label}
                  title={`${item.label} projection is not implemented yet`}
                  type="button"
                >
                  <Icon className="navigation-icon" size={14} />

                  {!collapsed ? <span>{item.label}</span> : null}
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </aside>
  );
}
