import { BarSeries, Chart } from "../design/Chart";

/**
 * Today's only chart, split into its own module so Recharts is NOT part of the first load.
 *
 * Today is the landing page and this chart is its last section, below the fold — so the reader sees
 * the numbers that matter before a charting library is even fetched. Without this the main chunk
 * carried all of Recharts for every visitor (finding F6).
 */
export default function ReachChart({
  data,
}: {
  data: Array<{ country: string; reachable: number }>;
}) {
  return (
    <Chart
      title="Share of records with a contact route, by market"
      caption="A route means an email, phone or LinkedIn profile we actually hold — never a guessed address. A switchboard number counts as a route but converts far worse than a named person."
      height={200}
    >
      <BarSeries data={data} x="country" y="reachable" colorByIndex />
    </Chart>
  );
}
