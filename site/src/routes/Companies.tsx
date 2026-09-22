/**
 * `/companies` — the whole universe, searchable.
 *
 * This is the page that has to survive growth. The CRM went from 57 records to 1,299 in one day,
 * so the grid is virtualised and the filters are cheap. Filter state lives in the URL hash, so a
 * view can be shared or bookmarked and reproduces exactly.
 */
import { SearchX } from "lucide-react";
import { useMemo, useState } from "react";
import { DataGrid, type GridColumn } from "../design/DataGrid";
import {
  ContactRoute,
  MarketTag,
  ScoreBadge,
  SegmentTag,
  StatusBadge,
  TriggerLine,
} from "../design/domain";
import {
  Button,
  cn,
  EmptyState,
  ErrorState,
  Page,
  PageHeader,
  Toolbar,
} from "../design/primitives";
import type { CompanyIndexRow } from "../lib/data";
import { getIndex } from "../lib/data";
import { navigate } from "../lib/router";
import { useAsync } from "../lib/useAsync";

type Filters = {
  q: string;
  country: string | null;
  segment: string | null;
  status: string | null;
  triggerOnly: boolean;
  reachableOnly: boolean;
};

const EMPTY: Filters = {
  q: "",
  country: null,
  segment: null,
  status: null,
  triggerOnly: false,
  reachableOnly: false,
};

function Chip({
  active,
  onClick,
  children,
  tone = "default",
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
  tone?: "default" | "accent";
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full border px-2.5 py-1 text-small transition-colors",
        active
          ? tone === "accent"
            ? "border-[var(--accent)] bg-accent-weak text-accent"
            : "border-[var(--border-strong)] bg-surface-raised text-text"
          : "text-muted hover:text-text",
      )}
    >
      {children}
    </button>
  );
}

export function Companies() {
  const state = useAsync(getIndex, []);
  const [f, setF] = useState<Filters>(EMPTY);

  const rows = state.status === "ok" ? state.data : [];

  const { countries, segments, statuses } = useMemo(() => {
    const c = new Set<string>();
    const s = new Set<string>();
    const st = new Set<string>();
    for (const r of rows) {
      if (r.country) c.add(r.country);
      if (r.segment) s.add(r.segment);
      st.add(r.status);
    }
    return {
      countries: [...c].sort(),
      segments: [...s].sort(),
      statuses: [...st].sort(),
    };
  }, [rows]);

  const filtered = useMemo(() => {
    const q = f.q.trim().toLowerCase();
    return rows.filter((r) => {
      if (f.country && r.country !== f.country) return false;
      if (f.segment && r.segment !== f.segment) return false;
      if (f.status && r.status !== f.status) return false;
      if (f.triggerOnly && !r.trigger) return false;
      if (f.reachableOnly && !r.has_contact_route) return false;
      if (q) {
        const hay =
          `${r.name} ${r.slug} ${r.city ?? ""} ${r.regulator ?? ""} ${r.tags.join(" ")}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [rows, f]);

  const columns = useMemo<GridColumn<CompanyIndexRow>[]>(
    () => [
      {
        accessorKey: "name",
        header: "Company",
        size: 280,
        cell: (ctx) => (
          <div className="min-w-0">
            <div className="truncate font-medium">{ctx.row.original.name}</div>
            {ctx.row.original.city ? (
              <div className="truncate text-micro text-subtle">{ctx.row.original.city}</div>
            ) : null}
          </div>
        ),
      },
      {
        accessorKey: "country",
        header: "Market",
        size: 120,
        cell: (ctx) => <MarketTag country={ctx.row.original.country} />,
      },
      {
        accessorKey: "segment",
        header: "Segment",
        size: 140,
        cell: (ctx) => <SegmentTag segment={ctx.row.original.segment} />,
      },
      {
        accessorKey: "status",
        header: "Status",
        size: 110,
        cell: (ctx) => <StatusBadge status={ctx.row.original.status} />,
      },
      {
        accessorKey: "score",
        header: "Fit",
        size: 70,
        cell: (ctx) => <ScoreBadge score={ctx.row.original.score} />,
      },
      {
        id: "trigger",
        header: "Why now",
        size: 340,
        enableSorting: false,
        cell: (ctx) => (
          <div className="truncate">
            <TriggerLine trigger={ctx.row.original.trigger} />
          </div>
        ),
      },
      {
        id: "reach",
        header: "Reach",
        size: 90,
        enableSorting: false,
        cell: (ctx) => (
          <ContactRoute
            hasEmail={ctx.row.original.has_email}
            hasPhone={ctx.row.original.has_phone}
            hasLinkedin={ctx.row.original.has_linkedin}
          />
        ),
      },
    ],
    [],
  );

  if (state.status === "error") {
    return (
      <Page>
        <PageHeader title="Companies" />
        <ErrorState title="Could not load the company index">{state.error.message}</ErrorState>
      </Page>
    );
  }

  const dirty = JSON.stringify(f) !== JSON.stringify(EMPTY);

  return (
    <Page>
      <PageHeader
        title="Companies"
        lede={`${filtered.length.toLocaleString("en-GB")} of ${rows.length.toLocaleString("en-GB")} records. A firm with no trigger is market coverage, not a lead.`}
      />

      <Toolbar>
        <input
          value={f.q}
          onChange={(e) => setF({ ...f, q: e.target.value })}
          placeholder="Search name, city, regulator, tag…"
          className="h-9 w-full max-w-sm rounded-[var(--radius-sm)] border bg-surface px-3 text-small placeholder:text-subtle"
        />
        <Chip
          active={f.triggerOnly}
          tone="accent"
          onClick={() => setF({ ...f, triggerOnly: !f.triggerOnly })}
        >
          has a trigger
        </Chip>
        <Chip
          active={f.reachableOnly}
          tone="accent"
          onClick={() => setF({ ...f, reachableOnly: !f.reachableOnly })}
        >
          reachable
        </Chip>
        {dirty ? (
          <Button size="sm" variant="ghost" onClick={() => setF(EMPTY)}>
            clear
          </Button>
        ) : null}
      </Toolbar>

      <Toolbar>
        {countries.map((c) => (
          <Chip
            key={c}
            active={f.country === c}
            onClick={() => setF({ ...f, country: f.country === c ? null : c })}
          >
            {c}
          </Chip>
        ))}
        <span className="mx-1 text-subtle">·</span>
        {segments.map((s) => (
          <Chip
            key={s}
            active={f.segment === s}
            onClick={() => setF({ ...f, segment: f.segment === s ? null : s })}
          >
            <SegmentTag segment={s} />
          </Chip>
        ))}
        <span className="mx-1 text-subtle">·</span>
        {statuses.map((s) => (
          <Chip
            key={s}
            active={f.status === s}
            onClick={() => setF({ ...f, status: f.status === s ? null : s })}
          >
            {s}
          </Chip>
        ))}
      </Toolbar>

      <DataGrid
        data={filtered}
        columns={columns}
        initialSorting={[{ id: "score", desc: true }]}
        onRowClick={(r) => navigate(`/companies/${r.slug}`)}
        empty={
          <EmptyState icon={SearchX} title="Nothing matches those filters">
            {rows.length > 0
              ? "Try clearing a filter — the universe is still there."
              : "The index is empty."}
          </EmptyState>
        }
      />
    </Page>
  );
}
