/**
 * The ONLY entry point to Recharts. No view imports `recharts` directly.
 *
 * Why that rule exists: every chart then reads the same `--chart-*` tokens as the rest of the
 * design system, so a chart and a table are literally the same palette and a theme change reaches
 * both. A chart that looks like a different product is the failure mode when the brief is
 * "simple, elegant, clear, pure".
 *
 * Axes, grids and tooltips are styled once, here, so no chart can drift.
 */
import type { ReactNode } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { cn } from "./primitives";

export const CHART_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-6)",
] as const;

const axis = {
  stroke: "var(--border-strong)",
  tick: { fill: "var(--text-subtle)", fontSize: 11 },
  tickLine: false,
  axisLine: false,
} as const;

function ChartTooltip() {
  return (
    <Tooltip
      cursor={{ fill: "var(--surface-raised)" }}
      contentStyle={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-sm)",
        fontSize: 12,
        color: "var(--text)",
        boxShadow: "var(--shadow)",
      }}
      labelStyle={{ color: "var(--text-muted)", marginBottom: 2 }}
    />
  );
}

/**
 * Chart frame. `caption` is where the honest reading of the chart goes — what it means, and what
 * it does not. A chart without one tends to get over-read.
 */
export function Chart({
  title,
  caption,
  height = 220,
  children,
  className,
}: {
  title?: string;
  caption?: string;
  height?: number;
  children: ReactNode;
  className?: string;
}) {
  return (
    <figure className={cn("rounded-[var(--radius)] border bg-surface p-4", className)}>
      {title ? <figcaption className="mb-3 font-medium">{title}</figcaption> : null}
      <div style={{ height }}>{children}</div>
      {caption ? <p className="mt-2 text-micro text-subtle">{caption}</p> : null}
    </figure>
  );
}

type Datum = Record<string, string | number | null>;

export function BarSeries({
  data,
  x,
  y,
  colorByIndex = false,
  horizontal = false,
}: {
  data: Datum[];
  x: string;
  y: string;
  /** Colour each bar differently — for categories, not for a single measure over time. */
  colorByIndex?: boolean;
  horizontal?: boolean;
}) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={data}
        layout={horizontal ? "vertical" : "horizontal"}
        margin={{ top: 4, right: 8, bottom: 0, left: 0 }}
      >
        <CartesianGrid
          stroke="var(--border)"
          vertical={!horizontal}
          horizontal={horizontal}
          strokeDasharray="2 4"
        />
        {horizontal ? (
          <>
            <XAxis type="number" {...axis} />
            <YAxis type="category" dataKey={x} width={130} {...axis} />
          </>
        ) : (
          <>
            <XAxis dataKey={x} {...axis} />
            <YAxis {...axis} width={40} />
          </>
        )}
        <ChartTooltip />
        <Bar dataKey={y} radius={3} fill={CHART_COLORS[0]}>
          {colorByIndex
            ? data.map((d, i) => (
                <Cell key={String(d[x])} fill={CHART_COLORS[i % CHART_COLORS.length]} />
              ))
            : null}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function AreaSeries({ data, x, y }: { data: Datum[]; x: string; y: string }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.28} />
            <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="var(--border)" vertical={false} strokeDasharray="2 4" />
        <XAxis dataKey={x} {...axis} />
        <YAxis {...axis} width={40} />
        <ChartTooltip />
        <Area
          type="monotone"
          dataKey={y}
          stroke="var(--chart-1)"
          strokeWidth={2}
          fill="url(#areaFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

/**
 * A sparkline with no axes — for "is this source alive?". A line that flattens and stops is a dead
 * connector, and that should be readable at a glance without reading a number.
 */
export function Sparkline({
  data,
  y,
  tone = "var(--chart-1)",
  height = 28,
}: {
  data: Datum[];
  y: string;
  tone?: string;
  height?: number;
}) {
  if (data.length === 0) {
    return <span className="text-micro text-subtle">no history</span>;
  }
  return (
    <div style={{ height, width: 120 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
          <Line
            type="monotone"
            dataKey={y}
            stroke={tone}
            strokeWidth={1.75}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * Market × segment coverage. Deliberately a styled grid, not a charting component — a heatmap of
 * two categorical axes is a table, and routing it through Recharts would make it less clear.
 * Gaps are the point, so a zero renders loudly rather than as a pale cell.
 */
export function CoverageMatrix({
  rows,
  cols,
  value,
  rowLabel,
  colLabel,
}: {
  rows: string[];
  cols: string[];
  value: (row: string, col: string) => number;
  rowLabel?: (row: string) => string;
  colLabel?: (col: string) => string;
}) {
  const max = Math.max(1, ...rows.flatMap((r) => cols.map((c) => value(r, c))));
  return (
    <div className="overflow-x-auto">
      <table className="border-collapse text-small">
        <thead>
          <tr>
            <th className="px-2 py-1" />
            {cols.map((c) => (
              <th
                key={c}
                className="px-2 py-1 text-left text-micro font-semibold text-muted uppercase"
              >
                {colLabel?.(c) ?? c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r}>
              <th className="py-1 pr-3 text-left text-small font-medium whitespace-nowrap">
                {rowLabel?.(r) ?? r}
              </th>
              {cols.map((c) => {
                const n = value(r, c);
                const intensity = n === 0 ? 0 : 0.14 + 0.66 * (n / max);
                return (
                  <td key={c} className="p-0.5">
                    <div
                      title={`${rowLabel?.(r) ?? r} · ${colLabel?.(c) ?? c}: ${n}`}
                      className={cn(
                        "flex h-9 min-w-[3.5rem] items-center justify-center rounded-[var(--radius-sm)] tnum",
                        n === 0 && "border border-dashed border-[var(--critical)] text-critical",
                      )}
                      style={
                        n === 0
                          ? undefined
                          : {
                              background: `color-mix(in oklch, var(--accent) ${intensity * 100}%, transparent)`,
                            }
                      }
                    >
                      {n === 0 ? "none" : n}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
