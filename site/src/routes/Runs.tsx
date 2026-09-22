/**
 * `/runs` — what has the engine actually been doing?
 *
 * The engine's memory of itself (plan §3.1). Every execution is a row here, reverse-chronological,
 * with its full report — including the failures, which is the point: `run_all.py` used to print a
 * report to stdout and forget it, so "was the radar looking last Tuesday?" was unanswerable. A
 * connector that failed inside a run renders exactly as loud as one that fails on `/sources`.
 */
import { History } from "lucide-react";
import { BarSeries, Chart } from "../design/Chart";
import { DataTable, Td, Tr } from "../design/DataGrid";
import { Mono } from "../design/domain";
import {
  cn,
  EmptyState,
  ErrorState,
  Page,
  PageHeader,
  Section,
  Stat,
  StatRow,
} from "../design/primitives";
import type { RunRow } from "../lib/data";
import { getRuns } from "../lib/data";
import { useAsync } from "../lib/useAsync";

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("en-GB", { dateStyle: "medium", timeStyle: "short" });
}

function formatDuration(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined) return "unknown";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return `${m}m ${s}s`;
}

function createdInRun(run: RunRow): number {
  return run.connectors.reduce((sum, c) => sum + c.created, 0);
}

export function Runs() {
  const state = useAsync(() => getRuns(), []);

  if (state.status === "loading") return <Page>{null}</Page>;
  if (state.status === "error") {
    return (
      <Page>
        <PageHeader title="Runs" />
        <ErrorState title="The data layer could not be loaded">{state.error.message}</ErrorState>
      </Page>
    );
  }

  const runs = [...state.data].sort((a, b) => b.started_at.localeCompare(a.started_at));
  const withFailure = runs.filter((r) => r.connectors.some((c) => !c.ok));
  const latest = runs[0];

  const trend = runs
    .slice()
    .reverse()
    .map((r) => ({
      run: formatDateTime(r.started_at).replace(",", ""),
      created: createdInRun(r),
    }));

  return (
    <Page>
      <PageHeader
        title="Runs"
        lede="Run history, reverse-chronological. Each run is the engine's own report of what it did — including what it failed to do — so this is where 'did it actually look?' gets answered with evidence, not a guess."
      />

      {runs.length === 0 ? (
        <Section>
          <EmptyState icon={History} title="No runs recorded yet">
            Run `python tools/connectors/run_all.py` to produce the first record.
          </EmptyState>
        </Section>
      ) : (
        <>
          <Section>
            <StatRow>
              <Stat label="runs recorded" value={runs.length} />
              <Stat
                label="runs with a failure"
                value={withFailure.length}
                tone={withFailure.length > 0 ? "critical" : "positive"}
              />
              {latest ? (
                <Stat
                  label="latest run"
                  value={formatDateTime(latest.started_at)}
                  hint={
                    latest.connectors.some((c) => !c.ok)
                      ? "had a failing connector"
                      : "all connectors reported ok"
                  }
                  tone={latest.connectors.some((c) => !c.ok) ? "critical" : "positive"}
                />
              ) : null}
            </StatRow>
          </Section>

          {trend.length >= 3 ? (
            <Section title="Created records per run">
              <Chart caption="Records created, summed across connectors, per run. A drop can mean the market went quiet — or a connector went quiet. Check /sources before reading a low bar as good news.">
                <BarSeries data={trend} x="run" y="created" />
              </Chart>
            </Section>
          ) : null}

          <Section title="History">
            <DataTable head={["Started", "Duration", "Commit", "Outcome"]}>
              {runs.map((r) => (
                <Tr key={r.id}>
                  <Td className="whitespace-nowrap tnum">{formatDateTime(r.started_at)}</Td>
                  <Td className="tnum whitespace-nowrap">{formatDuration(r.duration_s)}</Td>
                  <Td>
                    {r.commit ? (
                      <Mono>{r.commit.slice(0, 7)}</Mono>
                    ) : (
                      <span className="text-subtle italic text-micro">unknown</span>
                    )}
                  </Td>
                  <Td>
                    {r.connectors.length === 0 ? (
                      <span className="text-subtle italic text-micro">no connectors recorded</span>
                    ) : (
                      <div className="flex flex-col gap-1.5 py-1">
                        {r.connectors.map((c) => (
                          <div
                            key={c.register}
                            className={cn(
                              "flex flex-wrap items-center gap-x-2 gap-y-0.5 rounded-[var(--radius-sm)] px-2 py-1",
                              !c.ok && "bg-critical-weak",
                            )}
                          >
                            <span className={cn("font-medium", !c.ok && "text-critical")}>
                              {c.register}
                            </span>
                            {c.ok ? (
                              <span className="text-small text-muted tnum">
                                {c.created} created · {c.skipped} skipped
                                {c.changes > 0 ? ` · ${c.changes} changed` : ""}
                                {c.total != null ? ` · ${c.total} total` : ""}
                              </span>
                            ) : (
                              <span className="text-small font-medium text-critical">failed</span>
                            )}
                            {!c.ok && c.error ? (
                              <span className="w-full text-small text-critical">{c.error}</span>
                            ) : null}
                          </div>
                        ))}
                      </div>
                    )}
                  </Td>
                </Tr>
              ))}
            </DataTable>
          </Section>
        </>
      )}
    </Page>
  );
}
