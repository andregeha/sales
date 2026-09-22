/**
 * Design-system primitives. Layout, content and controls.
 *
 * Rules these enforce structurally rather than by convention:
 *  - `Stat` cannot be rendered without a label (plan §5.3 — never a number without its meaning).
 *  - `EmptyState` and `ErrorState` exist so every data view can declare them; `DataGrid` requires
 *    the empty one as a prop, so "screen says nothing when it has nothing" is not reachable.
 *  - Nothing here uses a raw colour. Tokens only.
 */
import { clsx } from "clsx";
import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export function cn(...parts: Array<string | undefined | null | false>) {
  return twMerge(clsx(parts));
}

/* ------------------------------------------------------------------ layout */

export function Page({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn("mx-auto w-full max-w-[1400px] px-5 pb-24 sm:px-8", className)}>{children}</div>;
}

export function PageHeader({
  title,
  lede,
  actions,
}: {
  title: string;
  /** One sentence saying what this page answers. Not decoration — it is the page's contract. */
  lede?: string;
  actions?: ReactNode;
}) {
  return (
    <header className="flex flex-wrap items-start justify-between gap-4 pt-8 pb-6">
      <div className="min-w-0">
        <h1 className="text-[length:var(--text-h1)] font-semibold tracking-[-0.015em]">{title}</h1>
        {lede ? <p className="mt-1 max-w-[62ch] text-muted">{lede}</p> : null}
      </div>
      {actions ? <div className="flex shrink-0 items-center gap-2">{actions}</div> : null}
    </header>
  );
}

export function Section({
  title,
  description,
  actions,
  children,
  className,
}: {
  title?: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={cn("mb-10", className)}>
      {title ? (
        <div className="mb-3 flex flex-wrap items-baseline justify-between gap-3">
          <div>
            <h2 className="text-[length:var(--text-h2)] font-semibold tracking-[-0.01em]">{title}</h2>
            {description ? <p className="mt-0.5 text-small text-muted">{description}</p> : null}
          </div>
          {actions}
        </div>
      ) : null}
      {children}
    </section>
  );
}

export function Panel({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("rounded-[var(--radius)] border bg-surface", className)}>{children}</div>
  );
}

export function Toolbar({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("flex flex-wrap items-center gap-2 pb-3", className)}>{children}</div>
  );
}

/* -------------------------------------------------------------------- data */

/**
 * A number with its meaning. The label is required — there is no way to render a bare figure.
 * `hint` is where the honest caveat goes ("of 1,299", "3 failing").
 */
export function Stat({
  label,
  value,
  hint,
  tone = "neutral",
}: {
  label: string;
  value: string | number;
  hint?: string;
  tone?: "neutral" | "positive" | "caution" | "critical" | "accent";
}) {
  const toneClass = {
    neutral: "text-text",
    positive: "text-positive",
    caution: "text-caution",
    critical: "text-critical",
    accent: "text-accent",
  }[tone];
  return (
    <div className="min-w-[8rem]">
      <div className={cn("tnum text-[length:var(--text-h1)] font-semibold leading-none", toneClass)}>
        {typeof value === "number" ? value.toLocaleString("en-GB") : value}
      </div>
      <div className="mt-1.5 text-small text-muted">{label}</div>
      {hint ? <div className="mt-0.5 text-micro text-subtle">{hint}</div> : null}
    </div>
  );
}

export function StatRow({ children }: { children: ReactNode }) {
  return <div className="flex flex-wrap gap-x-10 gap-y-6">{children}</div>;
}

/* ----------------------------------------------------------------- content */

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="py-2.5">
      <dt className="text-micro tracking-wide text-subtle uppercase">{label}</dt>
      <dd className="mt-1 break-words">{children ?? <Unknown />}</dd>
    </div>
  );
}

/** An unknown is shown as an unknown. It must never look like a value. */
export function Unknown({ note }: { note?: string }) {
  return (
    <span className="text-subtle italic" title={note ?? "Not known — never guessed"}>
      unknown
    </span>
  );
}

export function Callout({
  tone = "info",
  title,
  children,
}: {
  tone?: "info" | "positive" | "caution" | "critical";
  title?: string;
  children: ReactNode;
}) {
  const map = {
    info: "bg-info-weak text-info",
    positive: "bg-positive-weak text-positive",
    caution: "bg-caution-weak text-caution",
    critical: "bg-critical-weak text-critical",
  }[tone];
  return (
    <div className={cn("rounded-[var(--radius)] px-4 py-3", map)}>
      {title ? <div className="font-semibold">{title}</div> : null}
      <div className={cn("text-small", title && "mt-0.5")}>{children}</div>
    </div>
  );
}

export function EmptyState({
  icon: Icon,
  title,
  children,
}: {
  icon?: LucideIcon;
  title: string;
  children?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-[var(--radius)] border border-dashed px-6 py-14 text-center">
      {Icon ? <Icon className="mb-3 size-6 text-subtle" strokeWidth={1.5} aria-hidden /> : null}
      <div className="font-medium">{title}</div>
      {children ? <div className="mt-1 max-w-[52ch] text-small text-muted">{children}</div> : null}
    </div>
  );
}

export function ErrorState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="rounded-[var(--radius)] border border-[var(--critical)] bg-critical-weak px-4 py-3">
      <div className="font-semibold text-critical">{title}</div>
      {children ? <div className="mt-1 text-small text-critical">{children}</div> : null}
    </div>
  );
}

/** A link to the evidence behind a claim. Every sourced fact should carry one. */
export function SourceLink({ href, children }: { href?: string | null; children: ReactNode }) {
  if (!href) return <span className="text-small text-subtle">{children}</span>;
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer noopener"
      className="text-small text-muted underline decoration-[var(--border-strong)] underline-offset-2 hover:text-accent hover:decoration-[var(--accent)]"
    >
      {children}
    </a>
  );
}

export function Prose({ children }: { children: ReactNode }) {
  return <div className="max-w-[78ch] text-small leading-relaxed text-muted">{children}</div>;
}

/* ---------------------------------------------------------------- controls */

export function Button({
  children,
  onClick,
  variant = "quiet",
  size = "md",
  type = "button",
  title,
  disabled,
}: {
  children: ReactNode;
  onClick?: () => void;
  variant?: "primary" | "quiet" | "ghost";
  size?: "sm" | "md";
  type?: "button" | "submit";
  title?: string;
  disabled?: boolean;
}) {
  const variants = {
    primary: "bg-accent text-accent-fg hover:opacity-90",
    quiet: "border bg-surface hover:bg-surface-raised",
    ghost: "hover:bg-surface-raised",
  }[variant];
  return (
    <button
      type={type}
      title={title}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-[var(--radius-sm)] font-medium transition-colors disabled:opacity-40",
        size === "sm" ? "h-7 px-2 text-small" : "h-9 px-3",
        variants,
      )}
    >
      {children}
    </button>
  );
}

export function Kbd({ children }: { children: ReactNode }) {
  return (
    <kbd className="rounded-[4px] border bg-surface-raised px-1.5 py-0.5 font-mono text-micro text-muted">
      {children}
    </kbd>
  );
}
