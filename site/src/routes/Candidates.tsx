/**
 * `/candidates` — the review queue.
 *
 * These are **not records**. They are firms a noisy source proposed: French NAF `64.20Z` is every
 * holding company in France, of which a handful are family offices. Creating records from that
 * would destroy the thing that makes a record in this CRM mean something.
 *
 * So the page's only job is to make one question cheap to answer: **is this one of ours?** Every
 * row therefore carries its reason and a link to the evidence, and nothing here is counted as
 * pipeline anywhere else in the product.
 */
import { ExternalLink, Inbox } from "lucide-react";
import { useMemo, useState } from "react";
import { type ColumnLayout, DataGrid, type GridColumn } from "../design/DataGrid";
import { CandidateScore, DecisionTag, MarketTag, SegmentTag } from "../design/domain";
import {
  Button,
  Callout,
  cn,
  EmptyState,
  ErrorState,
  Page,
  PageHeader,
  Stat,
  StatRow,
  Toolbar,
} from "../design/primitives";
import { type CandidateRow, getCandidates } from "../lib/data";
import { navigate } from "../lib/router";
import { useAsync } from "../lib/useAsync";
import { useIsNarrow } from "../lib/useMediaQuery";

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

export function Candidates() {
  const state = useAsync(getCandidates, []);
  const narrow = useIsNarrow();
  const [unknownOnly, setUnknownOnly] = useState(true);
  const [source, setSource] = useState<string | null>(null);
  const [minScore, setMinScore] = useState(0);
  /** "waiting" is the work; "dismissed" is the accountability. */
  const [view, setView] = useState<"waiting" | "dismissed" | "accepted" | "all">("waiting");

  const rows = state.status === "ok" ? state.data : [];

  const sources = useMemo(() => [...new Set(rows.map((r) => r.source))].sort(), [rows]);
  const unknown = useMemo(() => rows.filter((r) => !r.matched_slug), [rows]);
  const dismissed = useMemo(
    () => rows.filter((r) => r.decision === "reject" || r.decision === "defer"),
    [rows],
  );

  const filtered = useMemo(
    () =>
      rows.filter((r) => {
        if (view === "waiting" && r.decision) return false;
        if (view === "dismissed" && r.decision !== "reject" && r.decision !== "defer") return false;
        if (view === "accepted" && r.decision !== "accept") return false;
        if (unknownOnly && r.matched_slug) return false;
        if (source && r.source !== source) return false;
        if (r.score < minScore) return false;
        return true;
      }),
    [rows, unknownOnly, source, minScore, view],
  );

  const columns = useMemo<GridColumn<CandidateRow>[]>(
    () =>
      narrow
        ? [
            {
              accessorKey: "name",
              header: "Candidate",
              cell: (ctx) => (
                <div className="min-w-0 py-1">
                  <div className="flex items-center gap-2">
                    <span className="truncate font-medium">{ctx.row.original.name}</span>
                    <CandidateScore score={ctx.row.original.score} />
                  </div>
                  <div className="truncate text-micro text-subtle">{ctx.row.original.why}</div>
                </div>
              ),
            },
            {
              id: "evidence",
              header: "Check",
              size: 64,
              enableSorting: false,
              cell: (ctx) =>
                ctx.row.original.evidence_url ? (
                  <a
                    href={ctx.row.original.evidence_url}
                    target="_blank"
                    rel="noreferrer noopener"
                    onClick={(e) => e.stopPropagation()}
                    className="text-accent hover:underline"
                  >
                    <ExternalLink className="size-4" />
                  </a>
                ) : null,
            },
          ]
        : [
            {
              accessorKey: "score",
              header: "Likelihood",
              cell: (ctx) => (
                <span title={ctx.row.original.score_reasoning}>
                  <CandidateScore score={ctx.row.original.score} />
                </span>
              ),
            },
            {
              accessorKey: "name",
              header: "Candidate",
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
              cell: (ctx) => <MarketTag country={ctx.row.original.country} />,
            },
            {
              accessorKey: "segment_guess",
              header: "Guess",
              cell: (ctx) => <SegmentTag segment={ctx.row.original.segment_guess} />,
            },
            {
              accessorKey: "why",
              header: view === "waiting" ? "Why it was proposed" : "Why, and what we decided",
              enableSorting: false,
              cell: (ctx) => (
                <div className="min-w-0">
                  <span className="text-small">{ctx.row.original.why}</span>
                  {ctx.row.original.decision ? (
                    <div className="mt-1 text-micro">
                      <DecisionTag decision={ctx.row.original.decision} />{" "}
                      <span className="text-subtle">{ctx.row.original.decision_reason}</span>
                    </div>
                  ) : null}
                </div>
              ),
            },
            {
              accessorKey: "source",
              header: "Source",
              cell: (ctx) => (
                <span className="text-micro text-subtle">{ctx.row.original.source}</span>
              ),
            },
            {
              id: "evidence",
              header: "Check",
              size: 72,
              enableSorting: false,
              cell: (ctx) =>
                ctx.row.original.evidence_url ? (
                  <a
                    href={ctx.row.original.evidence_url}
                    target="_blank"
                    rel="noreferrer noopener"
                    onClick={(e) => e.stopPropagation()}
                    className="inline-flex items-center gap-1 text-small text-accent hover:underline"
                  >
                    open <ExternalLink className="size-3" />
                  </a>
                ) : (
                  <span className="text-micro text-subtle">none</span>
                ),
            },
          ],
    [narrow, view],
  );

  const layout: ColumnLayout[] = narrow
    ? [{ flex: 1 }, { width: 64, align: "center" }]
    : [
        { width: 132 },
        { flex: 0.3 },
        { width: 104 },
        { width: 124 },
        { flex: 0.7 },
        { width: 128 },
        { width: 72, align: "center" },
      ];

  if (state.status === "error") {
    return (
      <Page>
        <PageHeader title="Candidates" />
        <ErrorState title="Could not load the review queue">{state.error.message}</ErrorState>
      </Page>
    );
  }

  return (
    <Page>
      <PageHeader
        title="Candidates"
        lede="Firms a source proposed but was not allowed to record. One question each: is this one of ours?"
      />

      <Callout tone="info" title="These are not records">
        A licence register is clean enough to create from. These sources are not — French NAF{" "}
        <code className="font-mono text-micro">64.20Z</code> is every holding company in France, of
        which a handful are family offices. Nothing here counts as pipeline until a human promotes
        it, and a candidate nobody promotes has cost us nothing.{" "}
        <strong>Likelihood is not the ICP score</strong> — it ranks how worth looking at a proposal
        is, and carries none of a researched record's authority. Hover it to see what produced it.
      </Callout>

      <div className="mt-6">
        <StatRow>
          <Stat label="proposed in total" value={rows.length} />
          <Stat
            label="not in the CRM"
            value={unknown.length}
            tone="accent"
            hint="the reconciliation gap"
          />
          <Stat
            label="still waiting"
            value={rows.filter((r) => !r.decision && !r.matched_slug).length}
            tone="accent"
            hint="nobody has decided about these yet"
          />
          <Stat
            label="dismissed, with a reason"
            value={dismissed.length}
            hint="examined and turned down — not the same as never looked at"
          />
          <Stat
            label="already known to us"
            value={rows.length - unknown.length}
            hint="may still carry new detail"
          />
        </StatRow>
      </div>

      <div className="mt-6">
        <Toolbar>
          <Chip active={view === "waiting"} onClick={() => setView("waiting")}>
            waiting ({rows.filter((r) => !r.decision && !r.matched_slug).length})
          </Chip>
          <Chip active={view === "dismissed"} onClick={() => setView("dismissed")}>
            dismissed ({dismissed.length})
          </Chip>
          <Chip active={view === "accepted"} onClick={() => setView("accepted")}>
            promoted ({rows.filter((r) => r.decision === "accept").length})
          </Chip>
          <Chip active={view === "all"} onClick={() => setView("all")}>
            all
          </Chip>
          <Chip active={unknownOnly} onClick={() => setUnknownOnly(!unknownOnly)}>
            not in the CRM
          </Chip>
          <Chip active={minScore === 60} onClick={() => setMinScore(minScore === 60 ? 0 : 60)}>
            likely ours
          </Chip>
          <Chip active={minScore === 40} onClick={() => setMinScore(minScore === 40 ? 0 : 40)}>
            40+
          </Chip>
          {sources.map((s) => (
            <Chip key={s} active={source === s} onClick={() => setSource(source === s ? null : s)}>
              {s}
            </Chip>
          ))}
          {source || !unknownOnly || minScore || view !== "waiting" ? (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                setSource(null);
                setUnknownOnly(true);
                setMinScore(0);
                setView("waiting");
              }}
            >
              reset
            </Button>
          ) : null}
        </Toolbar>
      </div>

      <DataGrid
        data={filtered}
        columns={columns}
        layout={layout}
        onRowClick={(r) => (r.matched_slug ? navigate(`/companies/${r.matched_slug}`) : undefined)}
        empty={
          <EmptyState
            icon={Inbox}
            title={
              view === "dismissed"
                ? "Nothing has been dismissed yet"
                : view === "accepted"
                  ? "Nothing has been promoted yet"
                  : "Nothing waiting for review"
            }
          >
            {view === "dismissed"
              ? "When a candidate is turned down, it stays here with the reason — so a rejection can be challenged rather than vanishing."
              : "Sources have proposed nothing new, or everything proposed has been decided."}
          </EmptyState>
        }
      />
    </Page>
  );
}
