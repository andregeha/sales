/**
 * `/` — Today.
 *
 * Answers exactly one question: **what needs me now?** Nothing else belongs here, and the
 * temptation to add a stats wall is the thing this page exists to resist (plan §5.1).
 *
 * Order is deliberate and is the order of consequence:
 *   1. A source that failed — because that means we did not look, not that nothing happened.
 *   2. Deadlines — because a missed one is unrecoverable.
 *   3. What changed — the reasons to write that appeared since the last run.
 *   4. Reachability — the binding constraint, shown as a problem.
 */
import { AlertTriangle, CalendarClock, Inbox } from "lucide-react";
import { lazy, Suspense } from "react";

/** Lazy so Recharts stays out of the first load — see ReachChart. */
const ReachChart = lazy(() => import("../features/ReachChart"));

import { DataTable, Td, Tr } from "../design/DataGrid";
import { ContactRoute, MarketTag, ScoreBadge, SegmentTag, TriggerLine } from "../design/domain";
import {
  Callout,
  EmptyState,
  ErrorState,
  Page,
  PageHeader,
  Section,
  Stat,
  StatRow,
} from "../design/primitives";
import { getEvents, getIndex, getRfps, getSources, getStats } from "../lib/data";
import { Link, navigate } from "../lib/router";
import { useAsync } from "../lib/useAsync";
import { useIsNarrow } from "../lib/useMediaQuery";

export function Today() {
  const narrow = useIsNarrow();
  const all = useAsync(
    () => Promise.all([getIndex(), getStats(), getSources(), getRfps(), getEvents()]),
    [],
  );

  if (all.status === "loading") return <Page>{null}</Page>;
  if (all.status === "error") {
    return (
      <Page>
        <PageHeader title="Today" />
        <ErrorState title="The data layer could not be loaded">{all.error.message}</ErrorState>
      </Page>
    );
  }

  const [index, stats, sources, rfps, events] = all.data;

  const failing = sources.filter((s) => s.status === "failing");
  const stale = sources.filter((s) => s.status === "stale");

  const today = new Date().toISOString().slice(0, 10);
  const soon = rfps
    .filter((r) => r.deadline && r.deadline >= today)
    .sort((a, b) => (a.deadline ?? "").localeCompare(b.deadline ?? ""))
    .slice(0, 8);

  const woken = events.filter((e) => e.woke).slice(0, 10);

  const actionable = index
    .filter((c) => c.trigger && c.status === "qualified")
    .sort((a, b) => (b.score ?? 0) - (a.score ?? 0));
  const reachable = actionable.filter((c) => c.has_contact_route);
  const blocked = actionable.length - reachable.length;

  const routeData = stats.contact_route_by_market
    .map((m) => ({
      country: m.country,
      reachable: m.total === 0 ? 0 : Math.round((m.with_route / m.total) * 100),
    }))
    .sort((a, b) => b.reachable - a.reachable);

  return (
    <Page>
      <PageHeader
        title="Today"
        lede="What needs you now — and nothing else. Everything here is actionable or it is a problem."
      />

      {/* 1. Did the machine actually look? */}
      {failing.length > 0 ? (
        <Section>
          <Callout tone="critical" title={`${failing.length} source could not be read`}>
            {failing.map((s) => s.register).join(", ")} — this means{" "}
            <strong>we did not look</strong>, not that nothing happened. Do not read any zero below
            as a quiet day.{" "}
            <Link to="/sources" className="underline">
              See sources
            </Link>
          </Callout>
        </Section>
      ) : stale.length > 0 ? (
        <Section>
          <Callout tone="caution" title={`${stale.length} source has not refreshed recently`}>
            {stale.map((s) => s.register).join(", ")}.{" "}
            <Link to="/sources" className="underline">
              See sources
            </Link>
          </Callout>
        </Section>
      ) : null}

      <Section>
        <StatRow>
          <Stat
            label="with a reason to write"
            value={actionable.length}
            tone="accent"
            hint={`of ${stats.active_total.toLocaleString("en-GB")} active records`}
          />
          <Stat
            label="of those we can reach"
            value={reachable.length}
            tone={reachable.length > 0 ? "positive" : "critical"}
          />
          <Stat
            label="blocked on a contact route"
            value={blocked}
            tone={blocked > 0 ? "critical" : "neutral"}
            hint={blocked > 0 ? "the binding constraint" : undefined}
          />
          <Stat label="woken by a register change" value={woken.length} hint="since the last run" />
        </StatRow>
      </Section>

      {/* 2. Deadlines. */}
      <Section
        title="Closing soon"
        description="A missed deadline is the worst thing this workspace can produce."
      >
        {soon.length === 0 ? (
          <EmptyState icon={CalendarClock} title="No open deadlines on record">
            That is a real result for the public portals — but note they only carry <em>public</em>{" "}
            procurement, and our buyers are private firms who never publish.
          </EmptyState>
        ) : (
          <DataTable
            head={narrow ? ["Deadline", "Title"] : ["Deadline", "Issuer", "Title", "Market"]}
            layout={
              narrow
                ? [{ width: 96 }, { flex: 1 }]
                : [{ width: 108 }, { flex: 0.34 }, { flex: 0.66 }, { width: 104 }]
            }
          >
            {soon.map((r) =>
              narrow ? (
                <Tr key={r.slug}>
                  <Td className="tnum whitespace-nowrap">{r.deadline}</Td>
                  <Td truncate title={r.title}>
                    <div className="py-1">
                      <div className="truncate">{r.title}</div>
                      <div className="truncate text-micro text-subtle">
                        {r.issuer}
                        {r.country ? ` · ${r.country}` : ""}
                      </div>
                    </div>
                  </Td>
                </Tr>
              ) : (
                <Tr key={r.slug}>
                  <Td className="tnum whitespace-nowrap">{r.deadline}</Td>
                  <Td truncate title={r.issuer ?? undefined}>
                    {r.issuer}
                  </Td>
                  <Td truncate title={r.title}>
                    {r.title}
                  </Td>
                  <Td>
                    <MarketTag country={r.country} />
                  </Td>
                </Tr>
              ),
            )}
          </DataTable>
        )}
      </Section>

      {/* 3. What changed. */}
      <Section
        title="Worth writing to now"
        description="Highest fit first. A firm with no trigger is coverage, not a lead — it is not here."
        actions={
          <Link to="/companies" className="text-small text-muted underline hover:text-accent">
            all companies
          </Link>
        }
      >
        {actionable.length === 0 ? (
          <EmptyState icon={Inbox} title="Nothing with a reason to write">
            That is a normal day. New licences arrive at roughly two a month per market.
          </EmptyState>
        ) : (
          <DataTable
            head={
              narrow
                ? ["Company", "Fit", "Reach"]
                : ["Company", "Market", "Segment", "Fit", "Why now", "Reach"]
            }
            layout={
              // ⚠ On a 375px phone the six fixed columns alone came to 446px, so the two flex
              // columns resolved to ZERO and the company name vanished. Today is the page Andre
              // reads on a phone, so narrow gets three columns with the detail stacked instead.
              narrow
                ? [{ flex: 1 }, { width: 62, align: "center" }, { width: 66, align: "center" }]
                : [
                    { flex: 0.4 },
                    { width: 104 },
                    { width: 128 },
                    { width: 136, align: "center" },
                    { flex: 0.6 },
                    { width: 78, align: "center" },
                  ]
            }
          >
            {actionable.slice(0, 12).map((c) =>
              narrow ? (
                <Tr key={c.slug} onClick={() => navigate(`/companies/${c.slug}`)}>
                  <Td truncate title={c.name}>
                    <div className="py-1">
                      <div className="truncate font-medium">{c.name}</div>
                      <div className="truncate text-micro text-subtle">
                        {c.country}
                        {c.segment ? ` · ${c.segment.replace(/_/g, " ")}` : ""}
                      </div>
                      <div className="truncate text-micro text-muted">{c.trigger}</div>
                    </div>
                  </Td>
                  <Td>
                    <ScoreBadge score={c.score} compact />
                  </Td>
                  <Td>
                    <ContactRoute
                      hasEmail={c.has_email}
                      hasPhone={c.has_phone}
                      hasLinkedin={c.has_linkedin}
                    />
                  </Td>
                </Tr>
              ) : (
                <Tr key={c.slug} onClick={() => navigate(`/companies/${c.slug}`)}>
                  <Td truncate className="font-medium" title={c.name}>
                    {c.name}
                  </Td>
                  <Td>
                    <MarketTag country={c.country} />
                  </Td>
                  <Td>
                    <SegmentTag segment={c.segment} />
                  </Td>
                  <Td>
                    <ScoreBadge score={c.score} />
                  </Td>
                  <Td truncate title={c.trigger ?? undefined}>
                    <TriggerLine trigger={c.trigger} />
                  </Td>
                  <Td>
                    <ContactRoute
                      hasEmail={c.has_email}
                      hasPhone={c.has_phone}
                      hasLinkedin={c.has_linkedin}
                    />
                  </Td>
                </Tr>
              ),
            )}
          </DataTable>
        )}
      </Section>

      {/* 4. The constraint. */}
      <Section
        title="Can we actually reach them?"
        description="Contact routes, not lead volume, are what limit this engine."
      >
        {routeData.length === 0 ? (
          <EmptyState icon={AlertTriangle} title="No coverage data yet" />
        ) : (
          <Suspense fallback={<div className="h-[200px]" />}>
            <ReachChart data={routeData} />
          </Suspense>
        )}
      </Section>
    </Page>
  );
}
