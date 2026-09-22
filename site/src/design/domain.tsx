/**
 * Domain components — the vocabulary of this product.
 *
 * A status, score, segment, market, contact route or trigger is ALWAYS one of these. Never an
 * ad-hoc span. That is what makes a score look identical on `/`, `/companies` and a detail page:
 * it is the same component, not three implementations that happen to agree today.
 */
import { AtSign, Link2, Phone, ShieldAlert, ShieldCheck, ShieldQuestion } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "./primitives";

/* ------------------------------------------------------------------ badges */

function Badge({
  children,
  tone,
  title,
}: {
  children: ReactNode;
  tone: "neutral" | "accent" | "positive" | "caution" | "critical" | "info";
  title?: string;
}) {
  const tones = {
    neutral: "bg-surface-raised text-muted",
    accent: "bg-accent-weak text-accent",
    positive: "bg-positive-weak text-positive",
    caution: "bg-caution-weak text-caution",
    critical: "bg-critical-weak text-critical",
    info: "bg-info-weak text-info",
  }[tone];
  return (
    <span
      title={title}
      className={cn(
        "inline-flex items-center gap-1 whitespace-nowrap rounded-[var(--radius-sm)] px-1.5 py-0.5 text-micro font-medium",
        tones,
      )}
    >
      {children}
    </span>
  );
}

/**
 * Status. The colouring says how *live* a record is, not how good it is — `qualified` is accent
 * because something is happening, `nurture` is deliberately quiet because nothing is.
 */
export function StatusBadge({ status }: { status: string }) {
  const map: Record<
    string,
    { tone: Parameters<typeof Badge>[0]["tone"]; label: string; title: string }
  > = {
    new: { tone: "info", label: "new", title: "Recorded, not yet assessed" },
    researching: { tone: "info", label: "researching", title: "Being worked up" },
    qualified: {
      tone: "accent",
      label: "qualified",
      title: "Has a real trigger — a reason to write now",
    },
    contacted: { tone: "accent", label: "contacted", title: "We have reached out" },
    engaged: { tone: "positive", label: "engaged", title: "They replied" },
    opportunity: { tone: "positive", label: "opportunity", title: "A live deal" },
    won: { tone: "positive", label: "won", title: "Closed won" },
    lost: { tone: "neutral", label: "lost", title: "Closed lost" },
    nurture: { tone: "neutral", label: "nurture", title: "Market coverage — no current trigger" },
    disqualified: { tone: "neutral", label: "disqualified", title: "Ruled out, with a reason" },
  };
  const m = map[status] ?? { tone: "neutral" as const, label: status, title: status };
  return (
    <Badge tone={m.tone} title={m.title}>
      {m.label}
    </Badge>
  );
}

/** Fit score, banded exactly as `knowledge/market/icp.md` defines the bands. */
export function ScoreBadge({ score }: { score: number | null | undefined }) {
  if (score === null || score === undefined) {
    return <span className="text-subtle italic text-micro">unscored</span>;
  }
  const band =
    score >= 80
      ? { tone: "positive" as const, title: "80–100 — work it now" }
      : score >= 60
        ? { tone: "accent" as const, title: "60–79 — active queue" }
        : score >= 40
          ? { tone: "caution" as const, title: "40–59 — worth a look" }
          : { tone: "neutral" as const, title: "under 40 — nurture or skip" };
  return (
    <Badge tone={band.tone} title={band.title}>
      <span className="tnum">{score}</span>
    </Badge>
  );
}

const SEGMENT_LABELS: Record<string, string> = {
  family_office: "family office",
  mfo: "MFO",
  bank: "bank",
  asset_manager: "asset manager",
  fund_manager: "fund manager",
  broker: "broker",
  insurer: "insurer",
  custodian: "custodian",
};

/** Our three priority segments read normally; adjacent ones are visually quieter. */
export function SegmentTag({ segment }: { segment: string | null | undefined }) {
  if (!segment) return <span className="text-subtle italic text-micro">no segment</span>;
  const priority = ["family_office", "mfo", "bank", "asset_manager", "fund_manager"].includes(
    segment,
  );
  return (
    <span className={cn("whitespace-nowrap text-small", priority ? "text-text" : "text-subtle")}>
      {SEGMENT_LABELS[segment] ?? segment}
    </span>
  );
}

export function MarketTag({ country }: { country: string | null | undefined }) {
  if (!country) return <span className="text-subtle italic text-micro">—</span>;
  return <span className="whitespace-nowrap text-small">{country}</span>;
}

/* ---------------------------------------------------- the binding constraint */

/**
 * Whether we can actually reach this firm — the binding constraint on the whole engine, so it gets
 * a first-class component and renders as a *problem* when it is missing (plan §5.4).
 */
export function ContactRoute({
  hasEmail,
  hasPhone,
  hasLinkedin,
}: {
  hasEmail?: boolean;
  hasPhone?: boolean;
  hasLinkedin?: boolean;
}) {
  if (!hasEmail && !hasPhone && !hasLinkedin) {
    return (
      <span
        className="inline-flex items-center gap-1 text-micro text-critical"
        title="No way to reach this firm — the binding constraint on the whole engine"
      >
        no route
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 text-muted">
      {hasEmail ? <AtSign className="size-3.5 text-positive" aria-label="email" /> : null}
      {hasPhone ? <Phone className="size-3.5" aria-label="phone" /> : null}
      {hasLinkedin ? <Link2 className="size-3.5" aria-label="LinkedIn" /> : null}
    </span>
  );
}

/** The "why now". Without one, a firm is coverage, not a lead — and that is stated, not implied. */
export function TriggerLine({ trigger }: { trigger: string | null | undefined }) {
  if (!trigger) {
    return <span className="text-small text-subtle">no current trigger</span>;
  }
  return <span className="text-small">{trigger}</span>;
}

/* ------------------------------------------------------------ source health */

/** A dead connector must be impossible to miss. This is the honesty surface in component form. */
export function SourceHealth({
  status,
  detail,
}: {
  status: "ok" | "stale" | "failing";
  detail?: string;
}) {
  const map = {
    ok: { Icon: ShieldCheck, tone: "text-positive", label: "ok" },
    stale: { Icon: ShieldQuestion, tone: "text-caution", label: "stale" },
    failing: { Icon: ShieldAlert, tone: "text-critical", label: "failing" },
  }[status];
  const { Icon } = map;
  return (
    <span className={cn("inline-flex items-center gap-1.5 font-medium", map.tone)} title={detail}>
      <Icon className="size-4" aria-hidden />
      {map.label}
    </span>
  );
}

/* -------------------------------------------------------------------- misc */

export function Mono({ children }: { children: ReactNode }) {
  return <span className="font-mono text-micro text-subtle">{children}</span>;
}
