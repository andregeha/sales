# Changelog

## 2026-09-22 (laptop) — The network block is gone; the register engine is built and running

The first session on Andre's Windows laptop. Its whole purpose was to test the premise that moving
off the cloud unblocks the job. **It does.**

**Verified first, rather than assumed.** `geco.amf-france.org`, `data.gouv.fr`, `cma.org.sa`,
`tenders.etimad.sa`, `boamp.fr`, `ted.europa.eu`, `dfsa.ae` and `adgm.com` all reachable. Python
3.13.0 and PyYAML were already installed; `crm.py validate` exits 0.

**Register connectors — built, tested and live.** `base.py` + `amf_france.py` + `cma_saudi.py` +
`run_all.py` + `enrich_from_registers.py`, with 17 tests that need no network.
- **AMF France is live**: the AMF's own daily CSV on data.gouv.fr, 666 licensed firms. The first run
  created **10 new French asset/fund managers**, all licensed within six months, scoring 70-83, and
  correctly recognised two that were already in the CRM.
- **Saudi CMA is written but blocked**: every `/api/` call times out at the TCP layer from Europe.
  It fails loudly and says so. Retry from the Riyadh office.
- **Enrichment**: 6 existing French records gained a regulator-published switchboard number.

**RFP radar — the first trustworthy run.** TED and BOAMP were searched through their real APIs
(15 and 11 query variants, EN + FR, 2025+). **France is a measured zero**, which is a real result
rather than the previous "found nothing indexable". **Saudi Arabia is still zero COVERAGE** — Etimad
serves its own bot challenge, which we do not attempt to defeat. The best finding was not a tender:
**free saved-search email alerts on BOAMP, PLACE and TED**, which beat any scraper we could write.

**A correction that mattered.** The handover named Barjeel Geojit as "the one lead with a fund open
for subscription right now". It is not — the BGIOF NFO closed **2026-02-13**, seven months ago, and
the "open for subscription" banner still on their homepage is leftover launch copy. Outreach was
re-grounded on the umbrella/sub-fund administration workload instead. Also captured their real
published office email and phone.

**Sourcing.** Lead sourcing run against the unsourced market x segment combinations, working from
registers and company sites directly rather than search snippets.

**Outreach drafted** for the four best leads. Only one has a real published email route, and it is a
switchboard inbox — the draft says so rather than pretending otherwise. **Contact routes, not lead
volume, remain the binding constraint.**

**Housekeeping:** `python3` fixed to `python` across every file an agent actually executes (it would
have failed on Windows); `slugify` now folds accents; two display-path helpers no longer raise.


## 2026-09-22 — Workspace initialized
- Created `CLAUDE.md` (operating constitution, golden rules, deck conventions, approval gates).
- Built `knowledge/`: company profile, Gaia current product (full five-step workflow + compliance
  engine), Web Portal feature map, New Gaia roadmap, value propositions by segment, objection
  handling, competitors placeholder.
- Built `memory/`: facts, decisions, open questions, this changelog.
- Deep-dived `andregeha/ofs-marketing` in full — company, product, all module documentation,
  portal, New Gaia, and every prospect folder — and distilled it into `knowledge/`.
- Seeded `accounts/` from the marketing repo's prospect folders, `pipeline/pipeline.md`,
  `playbooks/`, and the agent + skill definitions.

## 2026-09-22 (later) — Mission set, workspace re-scoped to new business
Andre's answers landed and changed the shape of the work: this is a **continuous new-business
engine**, not a general sales assistant.

- **CLAUDE.md rewritten** — the mission, the territory (UAE · KSA · Lebanon · France; family
  offices & MFOs, private/investment banks, asset & fund managers), and a new non-negotiable
  **outreach rules** section (agents never send; make Andre's approve-and-send loop frictionless;
  never invent a contact detail; personalise on something real).
- **`knowledge/market/icp.md`** — the ICP and a 0–100 scoring model (fit 60 / trigger 25 / access 15)
  with explicit disqualification criteria.
- **Playbooks added** — `daily-run.md` (the heartbeat), `lead-sourcing.md`, `outreach.md`,
  `rfp-radar.md`.
- **`accounts/` re-scoped** — existing clients are now explicitly **proof and context, not pipeline**.
  `pipeline/pipeline.md` reframed: the CRM is the system of record, and the new-business pipeline is
  honestly recorded as empty until the first run.
- **Team extended** — added `ofs-lead-sourcer`; added the `/daily-run` skill.
- Agents dispatched in parallel to build the CRM tooling, the RFP source registry and the market
  landscape.

## 2026-09-22 (later still) — CRM tooling completed: `crm.py` + `crm_report.py`
This repo is now a working CRM, not just a schema.

- **`crm/SCHEMA.md`** — the full record shape for `crm/companies/<slug>.yaml` and
  `crm/rfps/<slug>.yaml`, enumerations, and a fully worked example of each.
- **`tools/crm.py`** — the CLI: `add`, `show`, `list` (filters on country/segment/status/stage/
  tag/owner/min-score, comma-separated multi-value, `table`/`json`/`csv` output), `update`
  (including the "one person, one verb, one date" `next_action` rule), `log` (append-only
  activities), `contact` (add/update, embedded per company), `next` (the daily work queue — due/
  overdue next actions + stalled contacted/engaged deals), `rfp add|list|show|update`, `stats`,
  and `validate` (the QA gate — schema, enums, dates, slug/filename match, disqualified-reason
  consistency; non-zero exit on error). `compute_next()`/`compute_stats()` are pure functions so
  `crm_report.py` reuses the exact same logic as the CLI.
- **`tools/crm_report.py`** — generates a self-contained, offline, printable HTML daily brief:
  outreach awaiting Andre's approval (pre-filled `mailto:` + copy-to-clipboard for emails,
  profile/search link + copy-to-clipboard for LinkedIn — never an automated send), RFP deadlines
  soonest-first, the work queue, new leads since the last run, and a pipeline breakdown by status/
  segment/country. Light/dark via `prefers-color-scheme`, responsive, print-friendly.
- **One seed record**, clearly marked `EXAMPLE-` and `status: disqualified` with reason "schema
  example, not a real lead" (`crm/companies/EXAMPLE-oasis-family-office.yaml`,
  `crm/rfps/EXAMPLE-mfo-portfolio-system-rfp.yaml`) — fictional, obviously fake, used only to
  demonstrate and validate the tooling.
- `.gitignore` — added `crm/reports/` and `crm/.report_state.json` (generated daily brief + local
  run marker; the YAML under `crm/companies/` and `crm/rfps/` remains the only source of truth).
- Verified: `crm.py validate` exits 0 on the real repo; every subcommand's `--help` works;
  `crm.py add/update/log/contact/rfp *` exercised end-to-end against synthetic records in a
  scratch directory (never committed) to confirm filtering, the overdue/stalled work queue, and
  schema-violation detection all behave correctly; `crm_report.py` generates valid HTML (parsed
  with `html.parser`, embedded JS syntax-checked with `node --check`) whose pending-outreach
  cards, mailto links, RFP urgency flags, work queue and pipeline breakdown were all confirmed
  against known inputs. **Not verified: actual pixel-level rendering in a real browser** — no
  headless browser was available in this environment; only structural/content checks were run.

### CRM verification and fixes (same day)
Independently re-tested the CRM tooling rather than accepting it as delivered. Two real bugs found
and fixed — both would have broken the first scheduled run:
1. **Unquoted YAML dates broke everything.** PyYAML resolves `date: 2026-09-22` into a
   `datetime.date`, which made `validate` fail on every date field and crashed `crm_report.py`.
   The seed records happened to use quoted dates, so it passed in testing. Since records are meant
   to be **hand-editable**, unquoted is the natural thing to write. Fixed by normalizing dates to
   ISO strings on load (`normalize_dates()` in `tools/crm.py`), accepting both forms.
2. **An inline draft's `Subject:` line was left in the email body.** A subject was only lifted out
   of a linked draft *file*, so a draft written into the activity summary produced a generic subject
   and a body starting with a duplicated "Subject:" line. Fixed in `tools/crm_report.py`.

Verified end to end: `crm.py validate` exits 0; the work queue reports due and overdue correctly;
the generated brief's `mailto:` link decodes to the right recipient, the real subject, and a clean
body. ⚠ Still **not** visually checked in a browser — no headless browser in this environment.

### First live RFP radar run — 2026-09-22 — nil return
Searched all four markets in English, French and Arabic (~19 queries). **Zero qualifying open
tenders found and none recorded** — reported plainly rather than padding the CRM with a speculative
match. Two candidates investigated and correctly rejected: an Abu Dhabi education-authority
"corporate portfolio management" RFQ (already closed, and project-portfolio not investment-portfolio),
and a World Bank Lebanon tax-administration system (out of scope). French public pension-fund
*appels d'offres* were correctly identified as selecting asset managers, not software.

The binding constraint is the blocked egress, not agent effort: estimated coverage is well under 10%
of live tender flow. Learned filters written into `playbooks/rfp-radar.md`; measured performance
recorded in `memory/facts.md` so a future nil return is read correctly.

### Lebanon + France passes; laptop route opened — 2026-09-22
- **Lebanon: 17 records.** Twelve commercial banks, two investment banks/wealth managers, two asset
  managers, one disqualified retail forex app. **Every bank is `nurture`, not `qualified`** — no
  public source resolves which Law 23/2025 track any individual bank is on (Parliament only passed
  the amended restructuring law in August 2026 and no "viable banks" list exists). Scores were held
  down from their mechanical total to reflect that, and each carries a next action for Andre to
  confirm the track before any outreach.
- **First competitor sighting recorded** — Amwal Capital (DIFC) went live on Broadridge IMS in May
  2024. Not a prospect; real intelligence. `knowledge/positioning/competitors.md` is no longer empty.
- **CLI bug found and fixed:** `crm.py add --website null` stored the literal string `"null"` rather
  than a null. That quietly corrupts the one rule that matters most — unknown must *look* unknown —
  so the CLI now treats "null"/"none"/"n/a"/"" as a real null. Audited every existing record: clean.
- **Andre approved running from his laptop.** Wrote `RUN-ON-LAPTOP.md` (five steps plus a paste-ready
  prompt) and `tools/connectors/README.md` (the register-connector spec, in build order, with the
  hard requirement that a connector must **fail loudly** in the cloud rather than return an empty
  diff that reads as a quiet day).

### France pass complete — all four markets now sourced — 2026-09-22
14 French records. Best: **Hope Asset Management** (88, new AMF licence + a genuinely multi-asset
fund launch spanning PE, infrastructure, real estate, listed and commodities — named founders) and
**Fundcraft France** (78, new AIFM licence, and structurally interesting because a ManCo-as-a-service
is itself a multi-fund, multi-client administration buyer).

Discipline worth keeping: the **Cyrus group entities** (Amplegest, Eternam, Cyrus Herez) are
cross-referenced in each other's reasoning so we do not pursue one group three times.
**RockFi disqualified** — a CIF/ORIAS network, not AMF-authorised, and has already built its own
back/middle office — recorded so it is not re-found later as a lookalike. Several triggers used are
from 2024 and were **scored down as dated rather than inflated**.

**Totals across all four markets: 57 companies · 24 qualified or researching · 20 of those with at
least one named person · 0 invented contact details.**

## 2026-09-22 (site) — `/markets`, `/triggers`, `/pipeline` routes built
Built the three P2/P3 route components for the sales website (`plan/website.md` §4, §5, §6c),
matching the idiom set by `site/src/routes/Today.tsx` and `Companies.tsx`:
- **`site/src/routes/Markets.tsx`** (`Markets`) — market × segment coverage via `CoverageMatrix`
  (rows: UAE/Saudi Arabia/Lebanon/France, cols: our five priority segments), a one-line summary
  naming every empty combination (gaps are the point, so this is additive to the matrix's own loud
  "none" cells, not a replacement), plus contact-route coverage and score-distribution `BarSeries`
  charts, each with an honest `caption`.
- **`site/src/routes/Events.tsx`** (`Events`, mounted at `/triggers`) — the reverse-chronological
  change feed from `getEvents()`, in a `DataGrid`: date, company (linked only when `company_slug`
  is set), what changed, before → after, and a "woke" indicator made visually prominent (accent
  badge + accent text) since a woken record is the whole reason this page exists. A "triggers
  only" vs "all changes" filter chip. Lede states plainly that a register amendment is evidence,
  not a verdict.
- **`site/src/routes/Pipeline.tsx`** (`Pipeline`) — filters `getIndex()` to
  contacted/engaged/opportunity/won/lost, grouped by `stage`, rendered as one `DataTable` per
  stage. Honest `EmptyState` ("no live deals yet; the engine is still building the top of the
  funnel") when there are none — not padded.

All three handle loading/error/empty per `useAsync`, use only design-system components and token
classes (no raw colour, no raw `<table>`), and pass Biome format/lint clean.

**Found, not fixed (out of scope for this task, flagged for whoever owns the dependency
versions):** the installed `@tanstack/react-table@9.2.4` does not match the v8-style API
`site/src/design/DataGrid.tsx` is written against (`useReactTable`, `getCoreRowModel`,
`ColumnDef<T, unknown>` no longer exist in that shape), so `tsc --noEmit` fails inside
`DataGrid.tsx` itself and cascades into every route that uses `DataGrid` — this reproduces
identically on the already-existing `Companies.tsx`, so it predates and is independent of this
change. `Markets.tsx` and `Pipeline.tsx` (which don't use `DataGrid`) type-check clean in
isolation; `Events.tsx` inherits the same pre-existing cascade as `Companies.tsx`, nothing new.
Also noted: `src/lib/data.ts`'s `import.meta.env` needs a `vite/client` types reference that isn't
present yet.

## 2026-09-22 (site, P0) — the JSON data contract: `tools/site_data.py` + three new entities
Built P0 of the website plan (`plan/website.md` §3, §6b, §7): the pure-Python layer that turns
`crm/` into the JSON the site reads. No frontend code — the boundary the plan draws at "nothing is
authored in `site/`" stays a Python/Node split, enforced at the JSON contract.

**Three append-only entities that did not exist before:**
- **`Run`** — `crm/runs/<YYYY-MM-DD-HHMMSS>.json`, written by `tools/connectors/run_all.py` on
  every invocation, success or failure (`write_run_record`/`build_run_record`), never overwritten
  (a filename collision gets a `-2` suffix). Records started/finished/duration, the commit sha
  (`git rev-parse HEAD`, `None` if it cannot be read), and per connector: ok/failed, the error
  message, total/new-on-register/created/skipped/changes counts, and baseline/backfill/partial
  flags. A failed connector still gets a full record — the point, after today's ADGM near-miss.
- **`ChangeEvent`** — `crm/events/<YYYY-MM>.jsonl`, appended by `base.Connector._apply_changes` for
  **every** register change, including on firms not yet in the CRM (`company_slug: null` — still a
  real market event). Dry runs write neither a run record nor an event.
- **`SourceHealth`** — deliberately *not* stored. `site_data.compute_source_health()` derives
  last-success date, consecutive failures, latest count and a run history purely from `Run` records
  plus register snapshots — no wall clock involved, so it stays deterministic. A register failing
  3 runs in a row flips to `failing`; 1–2 is `stale`; never-run is `stale`.

**`tools/site_data.py`** emits `site/public/data/`: the slim `index.json` (~784KB for 1,298
companies — larger than the plan's 307KB estimate, taken from before the CRM's 22× growth; each
row is documented and there is no low-hanging fat to cut), one `companies/<slug>.json` per firm,
`rfps.json`, `runs.json`, `events.json`, `sources.json`, `stats.json` (counts, market×segment
coverage, score-distribution bands, contact-route coverage by market), `questions.json` (parses
every markdown table in `memory/open-questions.md` into `{id, question, unblocks, status,
priority, section}` — the narrative "Answered"/"Resolved" sections are prose, not tables, and are
correctly left unparsed), and `build.json` (`schema_version`, `commit`, `company_count` — the one
place a commit sha appears). `EXAMPLE-*` records are excluded from every output (a fictional
schema-demo RFP was otherwise rendering as a real deadline).

**Determinism (plan §7) is enforced, not hoped for**: sorted keys and stable row ordering
everywhere, no wall-clock reads outside `build.json`. `tools/test_site_data.py` builds twice into
separate directories and asserts every file is byte-identical, plus asserts every emitted file is
actually written with `sort_keys=True`. 22 tests total, covering the index/detail shape, the
EXAMPLE- exclusion, SourceHealth's failing/stale/ok transitions, and the questions parser.

**A live contract, verified against its real consumer, not just its own tests.** `site/src/lib/
data.ts` (built concurrently in the same session by another agent) already defines the Zod schema
the site validates against — field names were reconciled against it (`has_phone`/`has_linkedin`
added; `sources.json` renamed to `latest_count`/`regulator`/`partial`/`note`; `stats.json` to
`coverage`/`score_distribution` as bands/`contact_route_by_market`; `questions.json` to
`priority`/`unblocks`; `runs.json` given a stable `id`). Verified for real: copied `data.ts`'s own
Zod schemas into a throwaway Node script and ran them against the actual generated files —
**all 1,298 company records, plus every other file, validate cleanly.**

**Also fixed in `tools/connectors/`:** `run_all.py`'s failure summary now reports `created`/
`skipped`/`changes`/`new_on_register` as `0` rather than `null` for a connector that never ran
(`total`/`baseline`/`backfill`/`partial` stay `null` — genuinely unknown) — a `null` there failed
Zod's `.default(0)`, which only fires on a missing key, not an explicit `null`.

**Verified:** `python tools/crm.py validate` exits 0 (1,298 real companies, 1 RFP); all 41
`tools/connectors/test_connectors.py` tests, 9 `test_run_all.py` tests and 22
`tools/test_site_data.py` tests pass; two consecutive real builds of `site/public/data/` are
byte-identical; the real output validates against the site's actual Zod contract via Node.
**Not verified:** the site itself rendering this data in a browser (P1/frontend, being built in a
parallel session) — this task was data-contract only.
