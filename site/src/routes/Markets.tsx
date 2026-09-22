/**
 * `/markets` — Where are we thin?
 *
 * Answers exactly that: a market × segment coverage matrix over our four territories and five
 * priority segments (plan §4, "the ten views"). Gaps are the point — a zero already renders as a
 * loud dashed "none" cell in `CoverageMatrix` — so this page adds nothing to soften that, only a
 * one-line summary naming which combinations are empty, plus two supporting charts on the
 * constraint (contact routes) and the mass (score distribution).
 */
import { AlertTriangle } from "lucide-react";
import { BarSeries, Chart, CoverageMatrix } from "../design/Chart";
import {
  Callout,
  EmptyState,
  ErrorState,
  Page,
  PageHeader,
  Panel,
  Section,
} from "../design/primitives";
import { getStats } from "../lib/data";
import { useAsync } from "../lib/useAsync";

const MARKETS = ["UAE", "Saudi Arabia", "Lebanon", "France"] as const;

const SEGMENTS = ["family_office", "mfo", "bank", "asset_manager", "fund_manager"] as const;

const SEGMENT_LABEL: Record<(typeof SEGMENTS)[number], string> = {
  family_office: "Family office",
  mfo: "MFO",
  bank: "Bank",
  asset_manager: "Asset manager",
  fund_manager: "Fund manager",
};

export function Markets() {
  const state = useAsync(getStats, []);

  if (state.status === "loading") return <Page>{null}</Page>;
  if (state.status === "error") {
    return (
      <Page>
        <PageHeader title="Markets" />
        <ErrorState title="Could not load coverage stats">{state.error.message}</ErrorState>
      </Page>
    );
  }

  const stats = state.data;

  const coverageValue = (row: string, col: string) => stats.coverage[row]?.[col] ?? 0;

  const gaps: string[] = [];
  for (const m of MARKETS) {
    for (const s of SEGMENTS) {
      if (coverageValue(m, s) === 0) gaps.push(`${m} × ${SEGMENT_LABEL[s]}`);
    }
  }

  const routeData = stats.contact_route_by_market.map((m) => ({
    country: m.country,
    reachable: m.total === 0 ? 0 : Math.round((m.with_route / m.total) * 100),
  }));

  const scoreData = stats.score_distribution.map((b) => ({ band: b.band, count: b.count }));

  return (
    <Page>
      <PageHeader
        title="Markets"
        lede="Where the universe is thin, across the four markets and five segments we actually sell into. A gap here is a sourcing job, not a coincidence."
      />

      <Section
        title="Coverage"
        description="Records per market × segment. A dashed &ldquo;none&rdquo; cell is a real zero, not a missing figure."
      >
        <Panel className="p-4">
          <CoverageMatrix
            rows={[...MARKETS]}
            cols={[...SEGMENTS]}
            value={coverageValue}
            colLabel={(c) => SEGMENT_LABEL[c as (typeof SEGMENTS)[number]] ?? c}
          />
        </Panel>

        <div className="mt-3">
          <Callout
            tone={gaps.length > 0 ? "caution" : "positive"}
            title={
              gaps.length > 0
                ? `${gaps.length} market × segment combination${gaps.length === 1 ? "" : "s"} with no coverage`
                : "Every market × segment combination has at least one record"
            }
          >
            {gaps.length > 0
              ? `Nothing sourced yet for: ${gaps.join(", ")}. That is a sourcing gap, not evidence the segment is empty in that market.`
              : "That says the universe is broad, not that it is deep — check the score distribution below before reading this as done."}
          </Callout>
        </div>
      </Section>

      <Section
        title="Can we reach who we have?"
        description="Contact-route coverage, by market — the binding constraint, broken down by geography."
      >
        {routeData.length === 0 ? (
          <EmptyState icon={AlertTriangle} title="No coverage data yet" />
        ) : (
          <Chart
            title="Share of records with a contact route, by market"
            caption="A route means an email, phone or LinkedIn profile we actually hold — never a guessed address. Thin coverage above compounds with a low bar here: fewer firms, and fewer of those reachable."
            height={220}
          >
            <BarSeries data={routeData} x="country" y="reachable" colorByIndex />
          </Chart>
        )}
      </Section>

      <Section
        title="Where is the mass?"
        description="Fit-score distribution across active records."
      >
        {scoreData.length === 0 ? (
          <EmptyState icon={AlertTriangle} title="No score data yet" />
        ) : (
          <Chart
            title="Active records by fit-score band"
            caption="A pile in the low bands can mean the ICP is filtering hard, or that sourcing has not yet reached the firms that would score higher — this chart cannot tell you which."
            height={220}
          >
            <BarSeries data={scoreData} x="band" y="count" colorByIndex />
          </Chart>
        )}
      </Section>
    </Page>
  );
}
