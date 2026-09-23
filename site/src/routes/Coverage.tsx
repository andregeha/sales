/**
 * `/coverage` — can we even see this market?
 *
 * The Markets view counts records and answers "where are we thin?". This one answers the question
 * underneath it, which counting cannot: **is a zero a fact about the market, or a hole in our
 * machinery?**
 *
 * Those look identical on a chart and demand opposite responses. France × family office read as a
 * thin market for weeks; it was a *wrong-instrument* failure — a family office is usually not
 * licensed, so no licence register can ever find one. No amount of running the AMF connector harder
 * would have produced a single record.
 *
 * So each cell here names the instrument that feeds it, or states in writing why none can exist.
 * `tools/site_data.py` refuses to build if a cell does neither.
 */
import { ShieldQuestion } from "lucide-react";
import { useMemo } from "react";
import { MarketTag, NoInstrumentBadge, SegmentTag, SourceKindTag } from "../design/domain";
import {
  Callout,
  ErrorState,
  Page,
  PageHeader,
  Panel,
  Section,
  Stat,
  StatRow,
} from "../design/primitives";
import { type CoverageCell, getCoverage } from "../lib/data";
import { useAsync } from "../lib/useAsync";

function CellCard({ cell }: { cell: CoverageCell }) {
  // A cell holding records that NO source maintains is the quietest kind of rot: the records look
  // fine, and nothing will ever tell us they went stale. It is called out separately from a cell
  // that is merely empty.
  const unmaintained = cell.unfed && cell.records > 0;
  return (
    <Panel
      className={
        cell.unfed ? "border-[var(--critical)] bg-critical-weak/30" : undefined
      }
    >
      <div className="flex flex-wrap items-center gap-2">
        <MarketTag country={cell.market} />
        <SegmentTag segment={cell.segment} />
        {cell.unfed ? <NoInstrumentBadge /> : null}
      </div>

      <div className="mt-3 text-small text-muted">
        {/* Never a number without its meaning. */}
        {cell.records === 0
          ? "No records held."
          : `${cell.records} record${cell.records === 1 ? "" : "s"} held`}
        {cell.candidates > 0 ? ` · ${cell.candidates} unreviewed candidate(s)` : null}
      </div>

      {unmaintained ? (
        <div className="mt-3 flex gap-2 rounded-md border border-[var(--critical)] bg-critical-weak/40 p-2.5 text-small">
          <ShieldQuestion className="mt-0.5 size-4 shrink-0 text-critical" />
          <span>
            <strong>{cell.records} records that nothing maintains.</strong> No source feeds this
            cell, so these cannot be refreshed, and a firm that closed or changed hands would go on
            looking current indefinitely.
          </span>
        </div>
      ) : null}

      {cell.sources.length > 0 ? (
        <ul className="mt-3 space-y-2">
          {cell.sources.map((s) => (
            <li key={`${s.name}`} className="text-small">
              <div className="flex flex-wrap items-center gap-2">
                <SourceKindTag kind={s.kind} />
                <span className="font-medium">{s.name}</span>
              </div>
              {s.note ? <div className="mt-1 text-micro text-subtle">{s.note}</div> : null}
            </li>
          ))}
        </ul>
      ) : null}

      {cell.gap ? (
        <p className="mt-3 whitespace-pre-line border-t border-[var(--border)] pt-3 text-small text-muted">
          {cell.gap}
        </p>
      ) : null}
    </Panel>
  );
}

export function Coverage() {
  const state = useAsync(getCoverage, []);

  const cells = state.status === "ok" ? state.data.cells : [];
  const unfed = useMemo(() => cells.filter((c) => c.unfed), [cells]);
  const unmaintained = useMemo(
    () => unfed.filter((c) => c.records > 0).reduce((n, c) => n + c.records, 0),
    [unfed],
  );

  if (state.status === "error") {
    return (
      <Page>
        <PageHeader title="Coverage" />
        <ErrorState title="Could not load source coverage">{state.error.message}</ErrorState>
      </Page>
    );
  }

  return (
    <Page>
      <PageHeader
        title="Coverage"
        lede="Not how many firms we hold — whether we can see this market at all."
      />

      <Callout tone="info" title="A zero means two different things">
        Counting records cannot tell a market we looked at and found empty from a market we never had
        a way to look at. One is a fact about the world; the other is a hole in our machinery, and
        running the same connector harder will never close it. Every cell below names its instrument
        or states why none can exist — the build fails if a cell does neither.
      </Callout>

      <div className="mt-6">
        <StatRow>
          <Stat label="market × segment cells" value={cells.length} />
          <Stat
            label="with no instrument at all"
            value={unfed.length}
            tone={unfed.length > 0 ? "critical" : "positive"}
            hint="nothing feeds these — a zero here says nothing about the market"
          />
          <Stat
            label="records nothing maintains"
            value={unmaintained}
            tone={unmaintained > 0 ? "critical" : "positive"}
            hint="held in unfed cells; they cannot go stale visibly"
          />
        </StatRow>
      </div>

      {unfed.length > 0 ? (
        <Section title={`No instrument (${unfed.length})`}>
          <div className="grid gap-3 md:grid-cols-2">
            {unfed.map((c) => (
              <CellCard key={`${c.market}-${c.segment}`} cell={c} />
            ))}
          </div>
        </Section>
      ) : null}

      <Section title={`Fed by a source (${cells.length - unfed.length})`}>
        <div className="grid gap-3 md:grid-cols-2">
          {cells
            .filter((c) => !c.unfed)
            .map((c) => (
              <CellCard key={`${c.market}-${c.segment}`} cell={c} />
            ))}
        </div>
      </Section>

      {state.status === "ok" && state.data.measured ? (
        <p className="mt-8 text-micro text-subtle">
          Instruments and counts measured {state.data.measured}. Declared in{" "}
          <code className="font-mono">knowledge/market/source-coverage.yaml</code>, which is the
          source of truth — this page renders it and never adds to it.
        </p>
      ) : null}
    </Page>
  );
}
