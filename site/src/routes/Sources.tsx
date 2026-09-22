/**
 * `/sources` — is the machine actually looking?
 *
 * The honesty surface for connectors (plan §3.2, §5.4). This page exists because a run once
 * reported a confident "0 created, 412 skipped" while never having looked. A failed register does
 * not mean "nothing happened" — it means we did not look, and every count downstream of it is
 * meaningless until it is fixed. That is the one thing this page must make impossible to miss.
 */
import { RadioTower } from "lucide-react";
import { Sparkline } from "../design/Chart";
import { SourceHealth } from "../design/domain";
import {
  Callout,
  cn,
  EmptyState,
  ErrorState,
  Page,
  PageHeader,
  Panel,
  Section,
  Stat,
  StatRow,
} from "../design/primitives";
import type { SourceRow } from "../lib/data";
import { getSources } from "../lib/data";
import { useAsync } from "../lib/useAsync";

export function Sources() {
  const state = useAsync(() => getSources(), []);

  if (state.status === "loading") return <Page>{null}</Page>;
  if (state.status === "error") {
    return (
      <Page>
        <PageHeader title="Sources" />
        <ErrorState title="The data layer could not be loaded">{state.error.message}</ErrorState>
      </Page>
    );
  }

  const sources = state.data;
  const failing = sources.filter((s) => s.status === "failing");
  const stale = sources.filter((s) => s.status === "stale");

  return (
    <Page>
      <PageHeader
        title="Sources"
        lede="Whether each register is actually being read. A failed source means we did not look — not that nothing changed there — so treat any zero below with that in mind until the source is green again."
      />

      {failing.length > 0 ? (
        <Section>
          <Callout
            tone="critical"
            title={`${failing.length} of ${sources.length} source${sources.length === 1 ? "" : "s"} failing`}
          >
            {failing
              .map(
                (s) =>
                  `${s.register}${s.consecutive_failures > 0 ? ` — ${s.consecutive_failures} run${s.consecutive_failures === 1 ? "" : "s"} in a row` : ""}`,
              )
              .join(", ")}
            . Any zero reported for these registers is an absence of evidence, not evidence of
            nothing new.
          </Callout>
        </Section>
      ) : stale.length > 0 ? (
        <Section>
          <Callout
            tone="caution"
            title={`${stale.length} source${stale.length === 1 ? "" : "s"} has not refreshed recently`}
          >
            {stale.map((s) => s.register).join(", ")}. Not failing outright, but due a look.
          </Callout>
        </Section>
      ) : null}

      <Section title="Registers" description="One card per connector, most recent history first.">
        {sources.length === 0 ? (
          <EmptyState icon={RadioTower} title="No source health recorded yet">
            Run the connectors at least once to populate this page.
          </EmptyState>
        ) : (
          <div className="flex flex-col gap-3">
            {sources.map((s) => (
              <SourceCard key={s.register} source={s} />
            ))}
          </div>
        )}
      </Section>
    </Page>
  );
}

function SourceCard({ source }: { source: SourceRow }) {
  return (
    <Panel className={cn("p-4", source.status === "failing" && "border-[var(--critical)]")}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium">{source.register}</span>
            {source.regulator ? (
              <span className="text-small text-subtle">{source.regulator}</span>
            ) : null}
            <SourceHealth status={source.status} detail={source.note ?? undefined} />
            {source.partial ? (
              <span
                className="inline-flex items-center rounded-[var(--radius-sm)] bg-caution-weak px-1.5 py-0.5 text-micro font-medium text-caution"
                title="Catches new names but cannot detect disappearances"
              >
                partial
              </span>
            ) : null}
          </div>
          {/* The emitter already supplies the explanation for a partial source in `note`, so
              this renders that rather than restating it — one source of truth for the wording. */}
          {source.note ? (
            <p className="mt-1.5 max-w-[62ch] text-small text-muted">{source.note}</p>
          ) : null}
        </div>
        <Sparkline
          data={source.history}
          y="count"
          tone={source.status === "failing" ? "var(--critical)" : "var(--chart-1)"}
        />
      </div>

      <StatRow>
        <Stat
          label="last success"
          value={source.last_success_date ?? "never recorded"}
          tone={source.status === "failing" ? "critical" : "neutral"}
        />
        <Stat
          label="consecutive failures"
          value={source.consecutive_failures}
          tone={source.consecutive_failures > 0 ? "critical" : "positive"}
        />
        <Stat
          label="latest entry count"
          value={source.latest_count ?? "unknown"}
          hint={
            source.history.length > 0
              ? `${source.history.length} runs of history`
              : "no history yet"
          }
        />
      </StatRow>
    </Panel>
  );
}
