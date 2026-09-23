/**
 * Zod schemas for the JSON contract — DEVELOPMENT ONLY.
 *
 * This module is reached solely through a dynamic `import()` inside an `import.meta.env.DEV`
 * branch, so Zod never enters the production graph. That matters: an earlier version kept the
 * schemas at module scope in `data.ts` and claimed they were tree-shaken; they were not, and Zod
 * sat in the main chunk with 313 references.
 *
 * `data.ts` imports the TYPES from here with `import type`, which erases at compile time and
 * therefore pulls nothing into the bundle.
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
  /**
   * ⚠ `count` is nullable on purpose. A run that could not READ the source has no entry count —
   * that is unknown, not zero. Writing 0 would draw the line to the floor and read as "the register
   * emptied overnight", which is a far worse lie than a gap. The sparkline breaks instead.
   */
  history: z.array(z.object({ date: z.string(), count: z.number().nullable() })).default([]),
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
export const CandidateRow = z.object({
  source: z.string(),
  source_id: nullableStr,
  name: z.string(),
  country: z.string(),
  city: nullableStr,
  segment_guess: nullableStr,
  created: nullableStr,
  why: z.string(),
  evidence_url: nullableStr,
  matched_slug: nullableStr,
  /** How likely this proposal is to be one of ours. NOT the ICP score — see `candidates.py`. */
  score: z.number().default(0),
  score_reasoning: z.string().default(""),
  extra: z.record(z.string(), z.unknown()).default({}),
});
export type CandidateRow = z.infer<typeof CandidateRow>;

export const CoverageCell = z.object({
  market: z.string(),
  segment: z.string(),
  records: z.number(),
  candidates: z.number(),
  sources: z
    .array(
      z.object({
        kind: nullableStr,
        name: z.string(),
        connector: nullableStr,
        note: nullableStr,
      }),
    )
    .default([]),
  /** True when NOTHING feeds this cell — then a zero says nothing about the market. */
  unfed: z.boolean().default(false),
  gap: nullableStr,
});
export type CoverageCell = z.infer<typeof CoverageCell>;

export const Coverage = z.object({
  measured: nullableStr,
  cells: z.array(CoverageCell).default([]),
});
export type Coverage = z.infer<typeof Coverage>;

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

/* ---------------------------------------------------------------- validation */

const BY_PATH: Record<string, z.ZodType> = {
  "index.json": z.array(CompanyIndexRow),
  "stats.json": Stats,
  "sources.json": z.array(SourceRow),
  "runs.json": z.array(RunRow),
  "events.json": z.array(EventRow),
  "rfps.json": z.array(Rfp),
  "questions.json": z.array(QuestionRow),
  "build.json": Build,
  "candidates.json": z.array(CandidateRow),
  "coverage.json": Coverage,
};

/** Throws with a readable message when the emitter and this app disagree about a shape. */
export function validate(path: string, raw: unknown): void {
  const schema = path.startsWith("companies/") ? Company : BY_PATH[path];
  if (!schema) return;
  const parsed = schema.safeParse(raw);
  if (!parsed.success) {
    throw new Error(
      `${path} does not match the expected contract: ${parsed.error.issues[0]?.message ?? "unknown"}`,
    );
  }
}
