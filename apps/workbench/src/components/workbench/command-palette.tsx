"use client";

import {
  BookOpen,
  Gauge,
  GitBranch,
  PlayCircle,
  Search,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";

import type { MonadObjectType } from "@/lib/monad/model";

type SearchResult = {
  id: string;
  type: MonadObjectType;
  title: string;
  description?: string;
  status?: string;
  authority?: string;
  source: string;
};

type CommandPaletteProps = {
  open: boolean;
  onClose: () => void;
};

type PaletteItem = {
  key: string;
  label: string;
  description: string;
  href: string;
  type: string;
};

const NAVIGATION_ITEMS: PaletteItem[] = [
  {
    key: "nav-now",
    label: "Now",
    description:
      "Current product, execution, knowledge, and repository context",
    href: "/",
    type: "workspace",
  },
  {
    key: "nav-attention",
    label: "Attention",
    description:
      "Actionable engineering conditions, autonomous work, and recent activity",
    href: "/attention",
    type: "workspace",
  },
  {
    key: "nav-plan",
    label: "Plan",
    description: "Product Goal → Initiative → Epic → Feature → Story / Enabler",
    href: "/plan",
    type: "workspace",
  },
  {
    key: "nav-execution",
    label: "Execution",
    description: "Program Increment → Work Cycle → Work Packet → Execution",
    href: "/execution",
    type: "workspace",
  },
  {
    key: "nav-knowledge",
    label: "Knowledge",
    description: "Requirements, specifications, ADRs, policies, and evidence",
    href: "/knowledge",
    type: "workspace",
  },
  {
    key: "nav-control",
    label: "Control",
    description: "Changes, reviews, verification, risk, releases, and drift",
    href: "/control",
    type: "workspace",
  },
];

function navigationIcon(key: string) {
  if (key === "nav-now") return <Gauge size={15} />;
  if (key === "nav-attention") return <ShieldAlert size={15} />;
  if (key === "nav-plan") return <GitBranch size={15} />;
  if (key === "nav-execution") return <PlayCircle size={15} />;
  if (key === "nav-knowledge") return <BookOpen size={15} />;
  return <ShieldCheck size={15} />;
}

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);

  const items = useMemo<PaletteItem[]>(() => {
    if (!query.trim()) {
      return NAVIGATION_ITEMS;
    }

    return results.map((result) => ({
      key: result.id,
      label: `${result.id} — ${result.title}`,
      description: [result.type, result.status, result.authority, result.source]
        .filter(Boolean)
        .join(" · "),
      href: `/focus/${encodeURIComponent(result.id)}`,
      type: result.type,
    }));
  }, [query, results]);

  useEffect(() => {
    if (!open) {
      setQuery("");
      setResults([]);
      setActiveIndex(0);
      return;
    }

    window.setTimeout(() => inputRef.current?.focus(), 0);
  }, [open]);

  useEffect(() => {
    const normalized = query.trim();

    if (!open || !normalized) {
      setResults([]);
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setLoading(true);

      try {
        const response = await fetch(
          `/api/search?q=${encodeURIComponent(normalized)}`,
          {
            signal: controller.signal,
          },
        );

        if (!response.ok) {
          setResults([]);
          return;
        }

        const payload = (await response.json()) as { results?: SearchResult[] };
        setResults(payload.results ?? []);
        setActiveIndex(0);
      } catch (error) {
        if (!(error instanceof DOMException && error.name === "AbortError")) {
          setResults([]);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }, 120);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [open, query]);

  if (!open) {
    return null;
  }

  function openItem(item: PaletteItem) {
    router.push(item.href);
    onClose();
  }

  return (
    <div
      aria-label="Command palette"
      className="command-palette-backdrop"
      onMouseDown={(event) => {
        if (event.currentTarget === event.target) {
          onClose();
        }
      }}
      role="dialog"
    >
      <div className="command-palette">
        <div className="command-palette-input-row">
          <Search size={16} />
          <input
            aria-label="Search Monad objects"
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Escape") {
                event.preventDefault();
                onClose();
                return;
              }

              if (event.key === "ArrowDown") {
                event.preventDefault();
                setActiveIndex((current) =>
                  items.length === 0 ? 0 : (current + 1) % items.length,
                );
                return;
              }

              if (event.key === "ArrowUp") {
                event.preventDefault();
                setActiveIndex((current) =>
                  items.length === 0
                    ? 0
                    : (current - 1 + items.length) % items.length,
                );
                return;
              }

              if (event.key === "Enter") {
                const item = items[activeIndex];
                if (item) {
                  event.preventDefault();
                  openItem(item);
                }
              }
            }}
            placeholder="Search by ID, title, or object type…"
            ref={inputRef}
            value={query}
          />
          <kbd>Esc</kbd>
        </div>

        <div className="command-palette-results">
          {loading ? (
            <div className="command-palette-empty">
              Searching canonical projections…
            </div>
          ) : items.length === 0 ? (
            <div className="command-palette-empty">
              No matching Monad objects.
            </div>
          ) : (
            items.map((item, index) => (
              <button
                className={
                  index === activeIndex
                    ? "command-palette-item active"
                    : "command-palette-item"
                }
                key={item.key}
                onClick={() => openItem(item)}
                onMouseEnter={() => setActiveIndex(index)}
                type="button"
              >
                <span className="command-palette-item-icon">
                  {item.type === "workspace" ? (
                    navigationIcon(item.key)
                  ) : (
                    <Search size={14} />
                  )}
                </span>
                <span className="command-palette-item-copy">
                  <strong>{item.label}</strong>
                  <span>{item.description}</span>
                </span>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
