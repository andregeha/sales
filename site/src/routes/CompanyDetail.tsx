/**
 * `/companies/:slug` — everything about one firm.
 *
 * The governing principle here is §5.10: **every claim traceable.** A score shows its full
 * reasoning, a contact shows where it came from, and an unknown renders as an unknown rather than
 * as a blank that could be mistaken for a value. That is the UI expression of the rule that has
 * held across every record in this CRM — nothing is ever invented.
 */
import { ArrowLeft, ExternalLink, Mail, Phone } from "lucide-react";
import { DataTable, Td, Tr } from "../design/DataGrid";
import {
  ContactRoute,
  MarketTag,
  Mono,
  ScoreBadge,
  SegmentTag,
  StatusBadge,
  TriggerLine,
} from "../design/domain";
import {
  Callout,
  EmptyState,
  ErrorState,
  Field,
  Page,
  PageHeader,
  Panel,
  Prose,
  Section,
  SourceLink,
  Unknown,
} from "../design/primitives";
import { getCompany } from "../lib/data";
import { Link } from "../lib/router";
import { useAsync } from "../lib/useAsync";

export function CompanyDetail({ slug }: { slug: string }) {
  const state = useAsync(() => getCompany(slug), [slug]);

  if (state.status === "loading") return <Page>{null}</Page>;
  if (state.status === "error") {
    return (
      <Page>
        <PageHeader title="Company" />
        <ErrorState title={`Could not load “${slug}”`}>{state.error.message}</ErrorState>
      </Page>
    );
  }

  const c = state.data;
  const fit = c.fit ?? {};
  const contacts = c.contacts ?? [];
  const activities = [...(c.activities ?? [])].sort((a, b) => b.date.localeCompare(a.date));

  return (
    <Page>
      <div className="pt-6">
        <Link to="/companies" className="inline-flex items-center gap-1.5 text-small text-muted hover:text-accent">
          <ArrowLeft className="size-3.5" /> all companies
        </Link>
      </div>

      <PageHeader
        title={c.name}
        lede={c.description ?? undefined}
        actions={
          <div className="flex items-center gap-2">
            <StatusBadge status={c.status} />
            <ScoreBadge score={c.score ?? fit.score ?? null} />
          </div>
        }
      />

      {c.status === "disqualified" && fit.disqualified_reason ? (
        <Section>
          <Callout tone="caution" title="Disqualified — and the reason is the point">
            {fit.disqualified_reason}
          </Callout>
        </Section>
      ) : null}

      {!c.has_contact_route ? (
        <Section>
          <Callout tone="critical" title="No contact route">
            We hold no email, phone or LinkedIn profile for anyone here. Until that changes this firm
            cannot be worked, whatever its score. <strong>Never guess an address to fill the gap.</strong>
          </Callout>
        </Section>
      ) : null}

      <div className="grid gap-8 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
        <div className="min-w-0">
          <Section title="Why now">
            <Panel className="px-4 py-3">
              <TriggerLine trigger={c.trigger} />
            </Panel>
          </Section>

          <Section title="How this score was reached" description="Scored against knowledge/market/icp.md.">
            {fit.reasoning ? (
              <Panel className="px-4 py-3">
                <Prose>{fit.reasoning}</Prose>
              </Panel>
            ) : (
              <EmptyState title="No reasoning recorded">
                A score without its reasoning is not trustworthy — the reasoning is the part that matters.
              </EmptyState>
            )}
          </Section>

          <Section title="Timeline" description={`${activities.length} recorded ${activities.length === 1 ? "entry" : "entries"}.`}>
            {activities.length === 0 ? (
              <EmptyState title="Nothing recorded yet" />
            ) : (
              <ol className="space-y-3">
                {activities.map((a, i) => (
                  <li
                    // biome-ignore lint/suspicious/noArrayIndexKey: activities have no stable id
                    key={`${a.date}-${i}`}
                    className="rounded-[var(--radius)] border bg-surface px-4 py-3"
                  >
                    <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                      <span className="tnum text-small text-muted">{a.date}</span>
                      <span className="text-micro tracking-wide text-subtle uppercase">{a.type.replace(/_/g, " ")}</span>
                      {a.link ? (
                        <SourceLink href={a.link}>
                          source <ExternalLink className="inline size-3" />
                        </SourceLink>
                      ) : null}
                    </div>
                    <Prose>{a.summary}</Prose>
                  </li>
                ))}
              </ol>
            )}
          </Section>
        </div>

        <aside className="min-w-0">
          <Section title="Facts">
            <Panel className="px-4 py-1">
              <dl className="divide-y">
                <Field label="Market">
                  <MarketTag country={c.country} />
                  {c.city ? <span className="text-muted"> · {c.city}</span> : null}
                </Field>
                <Field label="Segment">
                  <SegmentTag segment={c.segment} />
                </Field>
                <Field label="Regulator">{c.regulator ?? <Unknown />}</Field>
                <Field label="Website">
                  {c.website ? (
                    <SourceLink href={c.website}>
                      {c.website.replace(/^https?:\/\//, "")} <ExternalLink className="inline size-3" />
                    </SourceLink>
                  ) : (
                    <Unknown />
                  )}
                </Field>
                <Field label="Stage">{c.stage ?? <Unknown />}</Field>
                <Field label="Owner">{c.owner ?? <Unknown />}</Field>
                <Field label="Reach">
                  <ContactRoute hasEmail={c.has_email} hasPhone={c.has_phone} hasLinkedin={c.has_linkedin} />
                </Field>
                <Field label="Record">
                  <Mono>{c.slug}</Mono>
                  <span className="text-micro text-subtle"> · created {c.created} · updated {c.updated}</span>
                </Field>
              </dl>
            </Panel>
          </Section>

          <Section title="Where this came from">
            <Panel className="px-4 py-1">
              <dl className="divide-y">
                <Field label="Channel">{c.source?.channel ?? <Unknown />}</Field>
                <Field label="Detail">
                  <span className="text-small text-muted">{c.source?.detail ?? <Unknown />}</span>
                </Field>
              </dl>
            </Panel>
          </Section>

          <Section title={`Contacts (${contacts.length})`}>
            {contacts.length === 0 ? (
              <EmptyState title="No named contact">Nothing has been invented to fill this.</EmptyState>
            ) : (
              <div className="space-y-3">
                {contacts.map((k) => (
                  <Panel key={`${k.name}-${k.email ?? k.phone ?? ""}`} className="px-4 py-3">
                    <div className="font-medium">{k.name}</div>
                    {k.title ? <div className="text-small text-muted">{k.title}</div> : null}
                    <div className="mt-2 flex flex-wrap items-center gap-3 text-small">
                      {k.email ? (
                        <a href={`mailto:${k.email}`} className="inline-flex items-center gap-1 text-accent hover:underline">
                          <Mail className="size-3.5" /> {k.email}
                        </a>
                      ) : null}
                      {k.phone ? (
                        <span className="inline-flex items-center gap-1 text-muted">
                          <Phone className="size-3.5" /> {k.phone}
                        </span>
                      ) : null}
                      {k.linkedin ? (
                        <SourceLink href={k.linkedin}>LinkedIn</SourceLink>
                      ) : null}
                    </div>
                    {k.notes ? <p className="mt-2 text-micro text-subtle">{k.notes}</p> : null}
                    {k.source ? (
                      <p className="mt-1 text-micro text-subtle">
                        <span className="tracking-wide uppercase">source</span> · {k.source}
                      </p>
                    ) : null}
                  </Panel>
                ))}
              </div>
            )}
          </Section>

          {c.next_action?.what ? (
            <Section title="Next action">
              <DataTable head={["Who", "What", "Due"]}>
                <Tr>
                  <Td>{c.next_action.who}</Td>
                  <Td>{c.next_action.what}</Td>
                  <Td className="tnum whitespace-nowrap">{c.next_action.due}</Td>
                </Tr>
              </DataTable>
            </Section>
          ) : null}
        </aside>
      </div>
    </Page>
  );
}
