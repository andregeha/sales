/**
 * `/triggers` — What moved?
 *
 * The change feed: every register delta detected across every firm, reverse-chronological (plan
 * §4). Most rows are routine; a few **wake** a record — turn a quiet firm back into one worth
 * looking at — and those are the whole point of this page, so they are made visually prominent
 * rather than left to blend into the feed.
 *
 * The lede matters as much as the data: a register amendment is evidence, not a verdict. A woken
 * record still needs research before it earns a "why now" and an outreach draft.
 */
import { ArrowRight, History, Zap } from "lucide-react";
import { useMemo, useState } from "react";
import { DataGrid, type GridColumn } from "../design/DataGrid";
import {
  cn,
  EmptyState,
  ErrorState,
  Page,
  PageHeader,
  Section,
  Stat,
  StatRow,
  Toolbar,
} from "../design/primitives";
import type { EventRow } from "../lib/data";
import { getEvents } from "../lib/data";
import { Link } from "../lib/router";
import { useAsync } from "../lib/useAsync";

function fmt(v: unknown): string {
  if (v === null || v === undefined || v === "") return "—";
  if (typeof v === "string" || typeof v === "number" || typeof v === "boolean") return String(v);
  try {
    return JSON.stringify(v);
  } catch {
    return String(v);
  }
}

function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full border px-2.5 py-1 text-small transition-colors",
        active ? "border-[var(--accent)] bg-accent-weak text-accent" : "text-muted hover:text-text",
      )}
    >
      {children}
    </button>
  );
}

function WokeBadge() {
  return (
    <span className="inline-flex items-center gap-1 whitespace-nowrap rounded-[var(--radius-sm)] bg-accent-weak px-1.5 py-0.5 text-micro font-semibold text-accent">
      <Zap className="size-3" aria-hidden />
      woke
    </span>
  );
}

export function Events() {
  const state = useAsync(getEvents, []);
  const [triggersOnly, setTriggersOnly] = useState(false);

  const rows = state.status === "ok" ? state.data : [];

  const sorted = useMemo(() => [...rows].sort((a, b) => b.date.localeCompare(a.date)), [rows]);

  const filtered = useMemo(
    () => (triggersOnly ? sorted.filter((e) => e.is_trigger) : sorted),
    [sorted, triggersOnly],
  );

  const wokeCount = rows.filter((e) => e.woke).length;
  const triggerCount = rows.filter((e) => e.is_trigger).length;

  const columns = useMemo<GridColumn<EventRow>[]>(
    () => [
      {
        accessorKey: "date",
        header: "Date",
        size: 100,
        cell: (ctx) => (
          <span
            className={cn(
              "tnum whitespace-nowrap",
              ctx.row.original.woke && "font-semibold text-accent",
            )}
          >
            {ctx.row.original.date}
          </span>
        ),
      },
      {
        accessorKey: "company_name",
        header: "Company",
        size: 240,
        cell: (ctx) => {
          const e = ctx.row.original;
          return (
            <div className="min-w-0">
              {e.company_slug ? (
                <Link
                  to={`/companies/${e.company_slug}`}
                  className={cn("truncate font-medium hover:text-accent", e.woke && "text-accent")}
                >
                  {e.company_name}
                </Link>
              ) : (
                <span className="truncate font-medium">{e.company_name}</span>
              )}
              {e.register ? (
                <div className="truncate text-micro text-subtle">{e.register}</div>
              ) : null}
            </div>
          );
        },
      },
      {
        id: "label",
        header: "What changed",
        size: 260,
        enableSorting: false,
        cell: (ctx) => {
          const e = ctx.row.original;
          return (
            <div className="min-w-0">
              <div className="truncate">{e.label ?? e.field ?? "—"}</div>
              {e.field && e.label && e.field !== e.label ? (
                <div className="truncate text-micro text-subtle">{e.field}</div>
              ) : null}
            </div>
          );
        },
      },
      {
        id: "delta",
        header: "Before → after",
        size: 280,
        enableSorting: false,
        cell: (ctx) => {
          const e = ctx.row.original;
          return (
            <span className="inline-flex min-w-0 items-center gap-1.5 text-small">
              <span className="max-w-[14ch] truncate text-subtle">{fmt(e.before)}</span>
              <ArrowRight className="size-3 shrink-0 text-subtle" aria-hidden />
              <span className="max-w-[14ch] truncate font-medium">{fmt(e.after)}</span>
            </span>
          );
        },
      },
      {
        id: "woke",
        header: "Woke",
        size: 90,
        enableSorting: false,
        cell: (ctx) =>
          ctx.row.original.woke ? <WokeBadge /> : <span className="text-subtle">—</span>,
      },
    ],
    [],
  );

  if (state.status === "loading") return <Page>{null}</Page>;
  if (state.status === "error") {
    return (
      <Page>
        <PageHeader title="Triggers" />
        <ErrorState title="Could not load the change feed">{state.error.message}</ErrorState>
      </Page>
    );
  }

  return (
    <Page>
      <PageHeader
        title="Triggers"
        lede="What moved, across every firm, since the last run. A register amendment is evidence, not a verdict — a woken record still needs research before it is ready for outreach."
      />

      <Section>
        <StatRow>
          <Stat label="changes recorded" value={rows.length} />
          <Stat label="that are triggers" value={triggerCount} tone="accent" />
          <Stat
            label="that woke a record"
            value={wokeCount}
            tone={wokeCount > 0 ? "accent" : "neutral"}
            hint="the reason this page exists"
          />
        </StatRow>
      </Section>

      <Toolbar>
        <Chip active={!triggersOnly} onClick={() => setTriggersOnly(false)}>
          all changes
        </Chip>
        <Chip active={triggersOnly} onClick={() => setTriggersOnly(true)}>
          triggers only
        </Chip>
      </Toolbar>

      <DataGrid
        data={filtered}
        columns={columns}
        layout={[
          { width: 104 },
          { flex: 0.34 },
          { flex: 0.26 },
          { flex: 0.4 },
          { width: 88, align: "center" },
        ]}
        initialSorting={[{ id: "date", desc: true }]}
        empty={
          <EmptyState icon={History} title="No changes recorded yet">
            {rows.length > 0
              ? "Nothing matches this filter — try &ldquo;all changes&rdquo;."
              : "The register-change feed fills in as runs detect deltas against the last snapshot."}
          </EmptyState>
        }
      />
    </Page>
  );
}
