/**
 * `/pipeline` — What is actually live?
 *
 * The handful of real deals, by stage (plan §4). Deliberately small: this is not a forecast and it
 * is not padded to look busier than it is. A firm sitting at `qualified` with a trigger belongs on
 * `/companies` and `/`, not here — this page only shows records that have actually moved past a
 * first touch (`contacted` through `won`/`lost`).
 */
import { Radio } from "lucide-react";
import { useMemo } from "react";
import { DataTable, Td, Tr } from "../design/DataGrid";
import {
  ContactRoute,
  MarketTag,
  ScoreBadge,
  SegmentTag,
  StatusBadge,
  TriggerLine,
} from "../design/domain";
import { EmptyState, ErrorState, Page, PageHeader, Section } from "../design/primitives";
import type { CompanyIndexRow } from "../lib/data";
import { getIndex } from "../lib/data";
import { navigate } from "../lib/router";
import { useAsync } from "../lib/useAsync";

const LIVE_STATUSES = new Set(["contacted", "engaged", "opportunity", "won", "lost"]);

function stageLabel(stage: string | null | undefined): string {
  if (!stage) return "No stage recorded";
  return stage.charAt(0).toUpperCase() + stage.slice(1).replace(/_/g, " ");
}

export function Pipeline() {
  const state = useAsync(getIndex, []);

  const rows = state.status === "ok" ? state.data : [];

  const live = useMemo(() => rows.filter((r) => LIVE_STATUSES.has(r.status)), [rows]);

  const groups = useMemo(() => {
    const map = new Map<string, CompanyIndexRow[]>();
    for (const r of live) {
      const key = r.stage ?? "";
      const bucket = map.get(key);
      if (bucket) bucket.push(r);
      else map.set(key, [r]);
    }
    return [...map.entries()].sort(([a], [b]) => {
      if (a === "") return 1;
      if (b === "") return -1;
      return a.localeCompare(b);
    });
  }, [live]);

  if (state.status === "loading") return <Page>{null}</Page>;
  if (state.status === "error") {
    return (
      <Page>
        <PageHeader title="Pipeline" />
        <ErrorState title="Could not load the company index">{state.error.message}</ErrorState>
      </Page>
    );
  }

  return (
    <Page>
      <PageHeader
        title="Pipeline"
        lede="The deals that are actually live — contacted through won or lost. A firm with a trigger but no first touch yet is coverage, not pipeline: find it on Companies or Today."
      />

      {live.length === 0 ? (
        <Section>
          <EmptyState icon={Radio} title="No live deals yet">
            The engine is still building the top of the funnel — sourcing and qualifying firms, not
            yet running deals. This page will fill in once outreach starts converting.
          </EmptyState>
        </Section>
      ) : (
        groups.map(([stage, companies]) => (
          <Section
            key={stage || "none"}
            title={stageLabel(stage)}
            description={`${companies.length} record${companies.length === 1 ? "" : "s"}`}
          >
            <DataTable head={["Company", "Market", "Segment", "Status", "Fit", "Why now", "Reach"]}>
              {companies.map((c) => (
                <Tr key={c.slug} onClick={() => navigate(`/companies/${c.slug}`)}>
                  <Td className="font-medium">{c.name}</Td>
                  <Td>
                    <MarketTag country={c.country} />
                  </Td>
                  <Td>
                    <SegmentTag segment={c.segment} />
                  </Td>
                  <Td>
                    <StatusBadge status={c.status} />
                  </Td>
                  <Td>
                    <ScoreBadge score={c.score} />
                  </Td>
                  <Td className="max-w-[34ch] truncate">
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
              ))}
            </DataTable>
          </Section>
        ))
      )}
    </Page>
  );
}
