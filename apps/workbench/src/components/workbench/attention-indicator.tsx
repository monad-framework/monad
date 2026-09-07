"use client";

import { Activity, ShieldAlert, ShieldCheck } from "lucide-react";
import Link from "next/link";

import type { AttentionSummary } from "@/lib/monad/attention-model";

type AttentionIndicatorProps = {
  summary: AttentionSummary;
};

export function AttentionIndicator({ summary }: AttentionIndicatorProps) {
  const critical = summary.operatorAction > 0;
  const warning = !critical && summary.attention > 0;
  const running = !critical && !warning && summary.running > 0;
  const label = critical
    ? `${summary.operatorAction} action required`
    : warning
      ? `${summary.attention} attention`
      : running
        ? `${summary.running} autonomous`
        : "No attention";
  const className = [
    "attention-indicator",
    critical ? "critical" : "",
    warning ? "warning" : "",
    running ? "running" : "",
    !critical && !warning && !running ? "clear" : "",
  ]
    .filter(Boolean)
    .join(" ");
  const Icon =
    critical || warning ? ShieldAlert : running ? Activity : ShieldCheck;

  return (
    <Link
      aria-label={`Attention Center: ${label}`}
      className={className}
      href="/attention"
      title="Open Attention Center"
    >
      <Icon aria-hidden="true" size={14} />
      <span>{label}</span>
      {summary.active > 0 ? <strong>{summary.active}</strong> : null}
    </Link>
  );
}
