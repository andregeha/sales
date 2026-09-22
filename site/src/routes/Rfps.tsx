/**
 * `/rfps` — what closes soon.
 *
 * The lede carries a caveat that matters more than the table: the public portals we can search
 * carry PUBLIC procurement only, and our buyers are private firms with no obligation to publish.
 * A short list here is not evidence of a quiet market.
 */
import { FileSearch } from "lucide-react";
import { DataTable, Td, Tr } from "../design/DataGrid";
import { MarketTag, SegmentTag } from "../design/domain";
import {
  Callout,
  EmptyState,
  ErrorState,
  Page,
  PageHeader,
  Section,
  SourceLink,
} from "../design/primitives";
import { getRfps } from "../lib/data";
import { useAsync } from "../lib/useAsync";

export function Rfps() {
  const state = useAsync(getRfps, []);
  if (state.status === "loading") return <Page>{null}</Page>;
  if (state.status === "error") {
    return (
      <Page>
        <PageHeader title="RFPs" />
        <ErrorState title="Could not load RFPs">{state.error.message}</ErrorState>
      </Page>
    );
  }
  const today = new Date().toISOString().slice(0, 10);
  const rows = [...state.data].sort((a, b) =>
    (a.deadline ?? "9999").localeCompare(b.deadline ?? "9999"),
  );
  const open = rows.filter((r) => r.deadline && r.deadline >= today);
  const closed = rows.filter((r) => !r.deadline || r.deadline < today);

  return (
    <Page>
      <PageHeader
        title="RFPs"
        lede="Soonest deadline first. A missed deadline is the worst thing this workspace can produce."
      />
      <Section>
        <Callout tone="info" title="Read a short list carefully">
          BOAMP, PLACE and TED carry <strong>public procurement only</strong>. Our buyers — family
          offices, private banks, asset and fund managers — are private firms with no obligation to
          publish, and most of this category is invitation-only. A quiet board is not a quiet
          market.
        </Callout>
      </Section>

      <Section title={`Open (${open.length})`}>
        {open.length === 0 ? (
          <EmptyState icon={FileSearch} title="No open tenders on record" />
        ) : (
          <DataTable
            head={["Deadline", "Issuer", "Title", "Market", "Segment", "Status", "Source"]}
          >
            {open.map((r) => (
              <Tr key={r.slug}>
                <Td className="tnum whitespace-nowrap">{r.deadline}</Td>
                <Td>{r.issuer}</Td>
                <Td>{r.title}</Td>
                <Td>
                  <MarketTag country={r.country} />
                </Td>
                <Td>
                  <SegmentTag segment={r.segment} />
                </Td>
                <Td className="text-small text-muted">{r.status}</Td>
                <Td>{r.source_url ? <SourceLink href={r.source_url}>notice</SourceLink> : null}</Td>
              </Tr>
            ))}
          </DataTable>
        )}
      </Section>

      {closed.length > 0 ? (
        <Section
          title={`Closed or undated (${closed.length})`}
          description="Kept so we do not re-find them."
        >
          <DataTable head={["Deadline", "Issuer", "Title", "Market"]}>
            {closed.map((r) => (
              <Tr key={r.slug}>
                <Td className="tnum whitespace-nowrap text-subtle">{r.deadline ?? "—"}</Td>
                <Td className="text-muted">{r.issuer}</Td>
                <Td className="text-muted">{r.title}</Td>
                <Td>
                  <MarketTag country={r.country} />
                </Td>
              </Tr>
            ))}
          </DataTable>
        </Section>
      ) : null}
    </Page>
  );
}
