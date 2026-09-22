/**
 * The JSON contract, typed and validated.
 *
 * Python owns the data, this app owns the presentation, and they meet ONLY here. Zod validates at
 * load so a malformed build fails loudly with a readable message rather than rendering something
 * subtly wrong — which, for a CRM, is the worse outcome.
 */
import { z } from "zod";

const nullableStr = z.string().nullable().optional();

/* ------------------------------------------------------------------ schemas */

export const CompanyIndexRow = z.object({
  slug: z.string(),
  name: z.string(),
  country: nullableStr,
  city: nullableStr,
  segment: nullableStr,
  status: z.string(),
  stage: nullableStr,
  regulator: nullableStr,
  website: nullableStr,
  score: z.number().nullable().optional(),
  has_contact_route: z.boolean().default(false),
  has_email: z.boolean().default(false),
  has_phone: z.boolean().default(false),
  has_linkedin: z.boolean().default(false),
  /** The "why now", short form. Null means coverage, not a lead. */
  trigger: nullableStr,
  created: nullableStr,
  updated: nullableStr,
  tags: z.array(z.string()).default([]),
});
export type CompanyIndexRow = z.infer<typeof CompanyIndexRow>;

export const Contact = z.object({
  name: z.string(),
  title: nullableStr,
  role: nullableStr,
  email: nullableStr,
  phone: nullableStr,
  linkedin: nullableStr,
  language: nullableStr,
  notes: nullableStr,
  source: nullableStr,
});

export const Activity = z.object({
  date: z.string(),
  type: z.string(),
  summary: z.string(),
  link: nullableStr,
});

export const Company = CompanyIndexRow.extend({
  legal_name: nullableStr,
  description: nullableStr,
  owner: nullableStr,
  size: z
    .object({
      aum: z.unknown().nullable(),
      employees: z.unknown().nullable(),
      portfolios: z.unknown().nullable(),
    })
    .partial()
    .nullable()
    .optional(),
  source: z
    .object({ channel: nullableStr, detail: nullableStr, date: nullableStr })
    .partial()
    .nullable()
    .optional(),
  fit: z
    .object({
      score: z.number().nullable(),
      reasoning: nullableStr,
      disqualified_reason: nullableStr,
    })
    .partial()
    .nullable()
    .optional(),
  contacts: z.array(Contact).default([]),
  activities: z.array(Activity).default([]),
  next_action: z
    .object({ who: nullableStr, what: nullableStr, due: nullableStr })
    .partial()
    .nullable()
    .optional(),
});
export type Company = z.infer<typeof Company>;

export const Rfp = z.object({
  slug: z.string(),
  title: z.string(),
  issuer: nullableStr,
  country: nullableStr,
  segment: nullableStr,
  source_url: nullableStr,
  published_date: nullableStr,
  deadline: nullableStr,
  status: z.string(),
  fit_assessment: nullableStr,
});
export type Rfp = z.infer<typeof Rfp>;

export const SourceRow = z.object({
  register: z.string(),
  regulator: nullableStr,
  /** True when the source only exposes a slice of its register — it catches new names but
      cannot see a firm leave. Saudi CMA is one. */
  partial: z.boolean().default(false),
  note: nullableStr,
  status: z.enum(["ok", "stale", "failing"]),
  last_success_date: nullableStr,
  consecutive_failures: z.number().default(0),
  latest_count: z.number().nullable().optional(),
  runs_seen: z.number().default(0),
  history: z.array(z.object({ date: z.string(), count: z.number() })).default([]),
});
export type SourceRow = z.infer<typeof SourceRow>;

export const RunRow = z.object({
  id: z.string(),
  started_at: z.string(),
  finished_at: nullableStr,
  duration_s: z.number().nullable().optional(),
  commit: nullableStr,
  connectors: z
    .array(
      z.object({
        register: z.string(),
        ok: z.boolean(),
        error: nullableStr,
        total: z.number().nullable().optional(),
        created: z.number().default(0),
        skipped: z.number().default(0),
        changes: z.number().default(0),
      }),
    )
    .default([]),
});
export type RunRow = z.infer<typeof RunRow>;

export const EventRow = z.object({
  date: z.string(),
  register: nullableStr,
  company_slug: nullableStr,
  company_name: z.string(),
  field: nullableStr,
  label: nullableStr,
  before: z.unknown().nullable().optional(),
  after: z.unknown().nullable().optional(),
  is_trigger: z.boolean().default(false),
  woke: z.boolean().default(false),
});
export type EventRow = z.infer<typeof EventRow>;

export const QuestionRow = z.object({
  id: z.string(),
  question: z.string(),
  priority: z.enum(["blocking", "soon", "nice"]).default("soon"),
  section: nullableStr,
  unblocks: nullableStr,
});
export type QuestionRow = z.infer<typeof QuestionRow>;

/** Shapes mirror exactly what `tools/site_data.py` emits — Python owns this contract. */
export const Stats = z.object({
  companies_total: z.number(),
  active_total: z.number().default(0),
  rfps_total: z.number().default(0),
  by_status: z.record(z.string(), z.number()).default({}),
  by_segment: z.record(z.string(), z.number()).default({}),
  by_country: z.record(z.string(), z.number()).default({}),
  /** country -> segment -> count */
  coverage: z.record(z.string(), z.record(z.string(), z.number())).default({}),
  score_distribution: z.array(z.object({ band: z.string(), count: z.number() })).default([]),
  contact_route_by_market: z
    .array(z.object({ country: z.string(), total: z.number(), with_route: z.number() }))
    .default([]),
  rfps_by_status: z.record(z.string(), z.number()).default({}),
  rfp_deadlines_approaching: z.array(z.unknown()).default([]),
});
export type Stats = z.infer<typeof Stats>;

export const Build = z.object({
  schema_version: z.number(),
  commit: nullableStr,
  company_count: z.number().optional(),
});
export type Build = z.infer<typeof Build>;

/* ------------------------------------------------------------------ loading */

const BASE = `${import.meta.env.BASE_URL}data`;

async function loadJson<T>(path: string, schema: z.ZodType<T>): Promise<T> {
  const res = await fetch(`${BASE}/${path}`);
  if (!res.ok) {
    throw new Error(
      `Could not load ${path} (HTTP ${res.status}). The data layer has not been generated — run \`python tools/site_data.py\`.`,
    );
  }
  const raw = await res.json();
  const parsed = schema.safeParse(raw);
  if (!parsed.success) {
    throw new Error(
      `${path} does not match the expected contract: ${parsed.error.issues[0]?.message ?? "unknown"}`,
    );
  }
  return parsed.data;
}

/** Cached once per page load — the data is static for the life of the build. */
function once<T>(fn: () => Promise<T>): () => Promise<T> {
  let p: Promise<T> | undefined;
  return () => {
    p ??= fn();
    return p;
  };
}

export const getIndex = once(() => loadJson("index.json", z.array(CompanyIndexRow)));
export const getStats = once(() => loadJson("stats.json", Stats));
export const getSources = once(() => loadJson("sources.json", z.array(SourceRow)));
export const getRuns = once(() => loadJson("runs.json", z.array(RunRow)));
export const getEvents = once(() => loadJson("events.json", z.array(EventRow)));
export const getRfps = once(() => loadJson("rfps.json", z.array(Rfp)));
export const getQuestions = once(() => loadJson("questions.json", z.array(QuestionRow)));
export const getBuild = once(() => loadJson("build.json", Build));

export function getCompany(slug: string): Promise<Company> {
  return loadJson(`companies/${slug}.json`, Company);
}
