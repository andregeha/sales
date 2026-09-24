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

## 2026-09-23 — `tools/connectors/gleif_enrich.py` (C3): GLEIF enrichment + fund→manager candidates

Built and ran the third leg of `plan/source-architecture.md`'s tier 3. **GLEIF has no industry
classification** (verified against the live API), so it cannot source prospects the way the
register/SIRENE connectors do — it only ever does two narrower things well, and this tool does only
those two:

**1. Enrichment.** For each CRM record in our four markets, search GLEIF (`filter[fulltext]` +
`filter[entity.legalAddress.country]`) and accept a hit only when a normalized name from our record
(`name` or `legal_name`) matches a name GLEIF holds for that entity (its `legalName` or an
`otherNames` entry) **and** the record's own `entity.legalAddress.country` — checked again in code,
not just trusted from the query filter — agrees with ours. Two or more distinct GLEIF entities
sharing a name in the same country is logged as `ambiguous` and never guessed at. `crm/SCHEMA.md` has
no `lei` field, so per the brief nothing was added — the LEI, legal form and any asserted direct
parent go into a `research` activity entry instead; `legal_name` and `city` (which are real fields)
are filled **only where our own field was `null`**, verified by re-loading the file from disk
immediately before writing (never trusting the in-memory copy). Runs are cached in
`crm/gleif/checked.json` so a re-run only spends requests on records not yet checked; `--recheck`
overrides.

Ran the full sweep for real (`--skip-funds`, no `--limit`) against all 1,610 in-territory CRM
records. **969 matched on GLEIF (60%): 937 gained a `legal_name`, 456 gained a `city`, 25 flagged
`ambiguous` (multiple distinct GLEIF entities share the name in that country) and correctly left
untouched, 616 have no GLEIF record at all** — expected and not a tool failure: an LEI is not
universal, and plenty of real licensed managers simply never needed one. `crm.py validate` exits 0
(1,611 companies) both mid-run and after.

⚠ **The run crashed partway through** (`OSError: [Errno 22] Invalid argument`) writing
`crm/gleif/checked.json` at record 1,038 of 1,610 — a transient Windows file-lock (this working
copy is likely under antivirus or cloud-sync watch), not data loss: every CRM record already
written was intact, and the cache file itself was undamaged. Fixed before resuming: `save_cache()`
now writes to a temp file and does an atomic `replace()`, with 5 retries and backoff, and raises
(rather than silently continuing) only if all five fail. Resumed with the same command; the cache
meant it only had to re-check the 572 records not yet marked done. One cosmetic side-effect of the
crash timing: `marigny-capital` has two near-identical GLEIF activity notes (the write that crashed
had already reached the CRM file before the cache write failed, so the resume re-processed it) —
left as-is rather than edited, per the CRM's own append-only rule for `activities`.

**2. Fund → manager discovery.** A GLEIF fund record (`entity.category=FUND`) that asserts a
`fund-manager` relationship links straight to its managing entity's own lei-record — confirmed live,
not assumed (most French/UAE/Saudi funds with a manager on file expose it this way; a fund with no
such relationship key has simply never had one reported, and is skipped rather than guessed). A
manager domiciled in one of our four markets that does not match anything already in the CRM by
name + country is proposed as a candidate via the existing `tools/candidates.py` queue
(`crm/candidates/gleif-<date>.jsonl`) — same append-only, evidence-carrying, never-auto-promoted
mechanism `sirene_france.py` already established; `matched_slug` is `null` on every line by
construction. Run for real on Lebanon (1 fund), Saudi Arabia (16) and UAE (131): **148 funds walked,
107 had a fund-manager relationship, 17 distinct candidates written** — among them ALJAZIRA CAPITAL
COMPANY, Jadwa Investment Company and SNB Capital (Riyadh) for Saudi, and Abu Dhabi Commercial Bank
(7 funds) for UAE — the last one a useful, honest example of the tool's limits: ADCB's asset-
management arm is already in the CRM as `adcb-asset-management-limited`, but the parent bank is a
distinct legal entity under a different name, so it correctly did not auto-match and instead
surfaced as a candidate whose `why` text flags the possible same-group relationship for a human to
settle. **France's 19,464 GLEIF-registered funds were deliberately not swept this session** — at one
polite request per fund-with-a-link, a full pass is hours, not minutes; `--max-funds-per-country`
bounds a run, and `--countries` scopes it, for whoever schedules the full sweep.

**Tests:** `tools/connectors/test_gleif.py`, 13 tests, no network (`_get_json` is the one stubbed
seam) — name+country matching (including the wrong-country-same-name rejection, and the ambiguous-
match refusal), never-overwrite (including a simulated concurrent edit winning over the in-memory
gain), fund-manager candidates never becoming CRM records and never being proposed when already
known, and loud failure (both phases) on an unreachable API or an unexpected response shape.

**What did not survive contact with the API, worth recording so nobody re-discovers it the hard
way:** `page[size]` above 200 is rejected outright (HTTP 400) — the plan's "sliced by département"
instinct for SIRENE applies here too, just at a smaller ceiling. `filter[entity.legalName]` is an
exact-string filter, not a search — it missed the AMF's own "1 2 3 INVESTMENT MANAGERS" entirely
(that firm has no LEI at all, confirmed by a full-text search too), which is why matching goes
through `filter[fulltext]` plus our own normalization instead. The `fund-manager` relationship's
`lei-record` link returns the manager's full record directly (`{"data": {...}}`), not a list —
simpler than expected. `direct-parent`/`ultimate-parent` relationship keys are present on nearly
every record regardless of whether a parent exists; only a `links.lei-record` (vs. a
`links.reporting-exception`) means there is actually something to follow.

**Verified:** all 13 `test_gleif.py` tests pass with no network; `python tools/crm.py validate`
exits 0 after real writes (1,611 companies, 1 RFP); the full real enrichment sweep (1,610 of 1,610)
and the real Lebanon/Saudi/UAE fund-manager-discovery run both completed against the live API,
including recovering from a genuine mid-run crash (see above), and are reflected in the numbers
above.
**Not verified:** a full France fund sweep (scope decision, not a failure — see above); whether any
of the 25 `ambiguous` French names or the 17 candidates are worth pursuing is Andre's call, not
this tool's.

## 2026-09-23 — `tools/connectors/multilateral_rfp.py` (C5): RFP radar for the Gulf and Lebanon

Built the tier-4 RFP source from `plan/source-architecture.md`: local portals cover France
(TED/BOAMP) reasonably and nothing else, so the addressable public tender flow in Saudi Arabia, the
UAE and Lebanon is multilateral development banks. Read live, from the laptop, against all four
named sources:

- **World Bank** — the real procurement-notices API is `search.worldbank.org/api/v2/procnotices`
  (JSON, no key), **not** the Projects & Operations API the brief also named (that one is a project
  pipeline — no procurement notices in it at all). Filterable by `<field>_exact` + free-text `qterm`,
  confirmed by empirical testing (the intuitive `countryshortname_exact` is silently ignored;
  `project_ctry_name_exact` genuinely filters). ✅ Live.
- **UNGM** — the notice page is a JS SPA, but it calls a real JSON-over-POST endpoint
  (`/Public/Notice/Search`) behind a standard ASP.NET anti-forgery token, read exactly as a browser
  would (GET the page for a token + cookie, then POST — no login, no account). Rate-limits
  aggressively (HTTP 429) under rapid requests — paced deliberately slowly (4s/request, a short
  curated term list) rather than fixed with retries. ✅ Live.
- **EBRD** — investigated, **not** automated, on purpose. The informational page (`.../work-with-
  us/procurement.html`) is a static 200; the actual search tool (`ecepp.ebrd.com/delta/
  noticeSearchResults.html`) is a ~3.8MB Oracle ADF/JSF enterprise portal (`/delta/
  JavaScriptServlet`) with no confirmed static query contract — architecturally the same trap
  `knowledge/market/rfp-sources.md` already documents for France's PLACE (a stateful postback that
  silently returns the unfiltered list for every query tried). The connector checks the info page is
  still up, then **raises loudly by name every run** rather than guess at the real portal's
  contract. This is a permanent, documented gap, not a bug — closing it needs a human with a browser
  or an official API.
- **IsDB** — found the procurement path the brief asked me to investigate:
  `isdb.org/project-procurement/tenders`, a Drupal Views tender board. Its exposed `locality`
  (country) and `status` filters **do not actually filter** — `?locality=LB/SA/AE` all return
  byte-identical rows, confirmed by diff — while `tender_type` genuinely does. The connector never
  relies on the broken filters: it fetches the whole listing (confirmed small and complete — exactly
  150 records over 3 pages, page 4+ empty) and filters on the country label every row already prints.
  ✅ Live. France is not an IsDB member state and structurally never appears — a fact, not a gap.

**Filtering.** `classify()` requires a country match (UAE/Saudi Arabia/Lebanon/France) **and** a
portfolio/investment/asset/fund/core-banking/treasury/capital-markets category term (English **and**
French) **and** a system/software/platform indicator — the last one is what stops an advisory or
policy mandate leaking through just because it uses our vocabulary. Nine named false-positive
classes are rejected explicitly, each traced to a real notice found while building this
(`Loan Management system` for a Lebanese agri-credit guarantee fund; `Establishment of Road Asset
Management System` — a road inventory, not investment assets; `Development of an Investment Policy`
— an advisory mandate; `INDIVIDUAL CONSULTANT SERVICES` — a person, not a vendor; a World Bank
grant facility that funds *others* to build capacity; the French public-pension mandate-tenderers
named in `rfp-sources.md`; and more — see the module docstring). World Bank's `notice_type`/
`notice_status`/`procurement_method_name` structured fields are used to exclude Contract
Awards/Terminations, Cancelled notices and Individual Consultant Selections directly, rather than
guessing from title text — an earlier version that also fed the World Bank's full `notice_text`
blob into `classify()` created three false positives from generic project boilerplate (a "B5 Fund"
communications hire that only *mentioned* "fund administration" in passing, an unrelated financial
auditor engagement, and a "PMU and Credit Manager" post) before this was caught and fixed by
inspecting the output by hand rather than trusting a clean run.

**Schema change required, and made:** `crm.py rfp add`'s `--deadline` was `required=True`, but
several genuine multilateral notices (general procurement notices, grant announcements) never state
one, and the one rule that matters most here is **never invent a deadline**. `deadline` is now
nullable end to end — `tools/crm.py` (argparse, `cmd_rfp_add`, `validate_rfp`) and `crm/SCHEMA.md`
— with `compute_stats()`'s approaching-deadlines section already handling a null gracefully (it did
before this change too; no null deadline was ever going to appear in `crm/rfps/` until now).

**Live run result, 2026-09-23:** World Bank ✅ (0 genuine hits — Saudi Arabia/UAE/France are not
World Bank borrowers; Lebanon's real WB portfolio is microfinance, tax administration, roads and
individual hires, not portfolio/investment software), UNGM ✅ (0 genuine hits), IsDB ✅ (0 genuine
hits — Saudi Arabia carries 19 of IsDB's own Jeddah-HQ corporate tenders, none of them software;
Lebanon and UAE: none in the current window), EBRD ❌ (fails loudly by design, every run, until a
human or an API closes it). **Zero RFP records created — a correct, reported-plainly result, not a
sourcing failure.** `python tools/crm.py validate` exits 0 unchanged (1,611 companies, 1 RFP).

**Tests:** `tools/connectors/test_multilateral.py`, 27 tests, no network — every named
false-positive class rejected on its real example text, a genuine hit still accepted, a source
raising is reported by name and never folded into "zero found", one source failing does not silence
another, zero genuine matches writes nothing, a genuine hit produces a schema-valid null-deadline
record, dry-run writes nothing, and a rerun does not duplicate (checked by both slug and
`source_url`).

## 2026-09-23 — candidate scoring, source health, and two silent bugs

**Candidate scoring.** 317 candidates were an unreviewable queue sorted by name. `Candidate.score()`
now ranks a *proposal* 0–100 with its reasoning, and the queue sorts best-first: GLEIF fund managers
(SNB Capital, Jadwa) at the top, a retirement residence and a Chinese logistics firm at the bottom.
Kept deliberately separate from the ICP score, in model, docstring and UI vocabulary.

**Every source now reports into the run record.** `run_all.py` gained `AUX_MODULES`, so the
multilateral RFP radar's four organisations report health beside the registers. EBRD — unreadable by
design, a stateful JSF portal we refuse to guess at — renders as `failing` on the website instead of
existing only in a terminal.

**Two silent bugs found and fixed, both of which looked like good news:**

1. **UNGM was reading zero and reporting a quiet market.** It delegated filtering to UNGM's own
   `Description` search; all six curated terms matched nothing in all four markets, while an
   unfiltered UAE query returned a full page. `fetch_ungm` now reads whole country lists (63
   notices) and applies our own auditable classifier. The dead-end term list is retained, renamed,
   with the measurement that killed it.
2. **The built CSS depended on the CRM's contents.** Tailwind 4 auto-discovers sources by scanning
   the project, and `site/public/data/` is generated but not gitignored — so editing one candidate's
   text changed the CSS hash. Excluded in `tokens.css`, with a regression test.

**Also fixed:** an RFP with no stated deadline was filed as *closed* (the nullable-deadline change
had not been traced into the UI) — it is now open, marked "none stated"; per-source tallies in the
radar joined on the display name instead of the short key and silently reported "0 rejected" for
sources that rejected 88; a source never once read successfully reported as `stale` rather than
`failing`; and `test_run_all` was dialling four real organisations because `main()` now runs the
aux sources.

**State:** 1,611 companies · 317 candidates (286 not in the CRM, 8 scoring 60+) · 118 tests green ·
site build deterministic · full pass reads 151 notices across three live sources, EBRD loudly dead.

## 2026-09-23 (later) — `/intake`, and the resolver it stands on

**`/intake` skill built** (`.claude/skills/intake/SKILL.md`). Connectors sweep sources; intake
captures what a human saw. Free text in — a hire, a fund launch, a name at a conference — and
exactly one of four outcomes out, named: an activity on an existing record, a new record, a
candidate, or a fact/open question. It separates what Andre *said* from what was *verified*, never
invents a contact detail, and refuses to qualify a record on hearsay.

**`crm.py find` added**, because intake's real risk is the duplicate, not the miss — a second record
for a firm we already hold splits its history so the activity, the contact and the trigger end up on
different copies, and both look fine. Fuzzy resolution across 1,611 records, ranked, deliberately
returning several: it ranks, it does not decide.

Getting it right took three corrections, each kept as a test in `tools/test_crm_find.py`:
- matching on generic industry vocabulary made "Zzz Nonexistent Capital" return eight confident
  matches — sharing the word "capital" with 200 records is not evidence;
- whole-string similarity rated "ASB Capital" and "SNB Capital" at 0.91, so a one-letter-different
  firm tied with the real one. Comparison now runs on each name's *distinctive* core;
- raw substring containment matched "one" inside "n**one**xistent", and a single-letter core like
  "G" (from "G Capital") matched nearly the whole CRM. Containment is now by whole words with a
  minimum length.

Verified against real data: "banque audi" → `bank-audi-france` (1.00) across language and legal
form; "Jadwa" → `jadwa-investment-difc-limited`; a firm that does not exist returns nothing.

127 tests green · CRM validates at 1,611 · site build deterministic.

## 2026-09-23 (later still) — the coverage view: where we are blind

`/coverage` answers the question the Markets view cannot. Counting records treats two opposite
situations identically: a market we looked at and found empty, and a market we never had a way to
look at. France × family office read as thin for weeks when it was a *wrong-instrument* failure —
a family office is usually unlicensed, so no licence register can ever find one, and running the
AMF connector harder would never have produced a record.

Every market × segment now names its instrument or states in writing why none can exist
(`knowledge/market/source-coverage.yaml`), and **`site_data.py` fails the build if a cell does
neither**. "Never miss" is only a process if forgetting is impossible.

**The honest headline: 7 of 20 cells have no instrument at all, holding 19 records that nothing
maintains.** UAE × family office, Saudi × bank, Saudi × family office, and all of Lebanon. Those
records cannot be refreshed, so a firm that closed would go on looking current — which the page
calls out as its own warning rather than leaving to inference.

Two design-system additions rather than ad-hoc markup, per the site rules: `SourceKindTag`
(register / registry / graph are not interchangeable, and a reader who cannot tell them apart will
over-trust the noisy one) and `NoInstrumentBadge`. Also fixed: YAML block scalars kept the author's
hard line wraps, so the page wrapped mid-sentence — how the source file is wrapped must not change
how the site reads.

Verified live in the browser at desktop and 375px, light and dark. 129 tests green.

## 2026-09-23 (fix) — "The data layer could not be loaded"

Andre hit a hard failure on the site: `sources.json does not match the expected contract: expected
number, received null`. My own regression from the same session.

**The bug.** EBRD has never once been read, so its run history carries `count: null` for every run.
That is the honest value — a day we could not read the source has no entry count — but `schemas.ts`
demanded a number. Writing `0` instead would have been far worse: the sparkline would draw to the
floor and read as "the register emptied overnight".

**Fixed** by making `history[].count` nullable, breaking the sparkline across a null rather than
connecting through it (`connectNulls={false}` — joining across would invent a trend through a day
we were blind), and rendering "never read" instead of an empty box for a source with no successful
run at all.

**Also fixed:** `multilateral_rfp:EBRD procurement` — an internal module key I had leaked into the
UI. Aux sources are now keyed `rfp:ebrd`, `rfp:world-bank`, `rfp:ungm`, `rfp:isdb` and carry the
organisation's name. Today's two earlier run records were migrated to the new keys, which is a
rename and not a rewrite: every count, error and timestamp is exactly as recorded. Without it the
Sources view showed four phantom sources that never existed.

**Why it escaped every check, which matters more than the bug.** `build_site.py --check` passed,
`tsc` passed, the site built and deployed. Zod validation is dev-only at runtime, so the contract
between `site_data.py` and `schemas.ts` was only ever tested by opening the exact page that broke —
and I had verified `/coverage`, not `/sources`.

`site/src/lib/contract.test.ts` now validates every emitted file, and every company record, against
the schemas with no browser involved — including an assertion that the file list matches, so a new
emitted file cannot be added untested. Confirmed it reproduces the original error when the fix is
reverted. Cost: `@types/node`, dev-only, documented in `plan/website.md`.

## 2026-09-23 — the website sweep: 7% reachable → 22%

Andre pushed back that the CRM was not producing new companies and the gaps were obvious. The
measurement behind that was worse than my earlier summaries implied: 1,604 records, **119 email
addresses, all UAE**, France 986 records and **zero** — and 887 of our 937 "contacts" were
switchboard numbers off registers, labelled *General enquiries*, not people. We had built a very
good directory and almost no ability to act on it.

**Built `tools/connectors/site_contacts.py`**, a third connector shape: it creates no records and
proposes no candidates, it reads the contact route a firm publishes on its own site and writes it
onto the record we already hold. Transcription, never inference — a page with no address yields
nothing, asserted in a test that says to revert if it ever fails.

**Result, measured:**

| | before | after |
|---|---|---|
| France with an email | 0 | **245** |
| All markets | 119 (7%) | **367 (22%)** |
| Qualified *and* contactable | 54 | 67 |

**Four defects the first live batches caught, each now a test.** Every one would have produced a
wrong action, not just a wrong number:

1. `+1 206…` on a French asset manager — a Seattle number from a vendor widget. Phones must match
   the market's dialling code.
2. `+33 (0)1 56 88 33 00` became `+330156883300` — one digit too many, **undiallable**. The trunk
   `0` is never part of an international number, and every French site prints it that way. The
   common case, not an edge case.
3. `dpo@`, `rgpd@`, `careers@`, `press@` — real, published, and the wrong door.
4. `infos@` filed as personal data for want of one letter.

**And one that got through to live records:** `dataprivacy@` was written because the exclusion list
matched exact local parts only. Wrong doors are now matched as substrings of 4+ characters, and a
cleanup removed **17** such addresses — `compliance@`, `legal@`, `support@`, `reclamation@`.
⚠ Most of those were UAE records from the FSRA register, not from this sweep: the 119 UAE emails we
had been counting all along included compliance inboxes.

**Two hard limits, written down rather than left to be rediscovered** (open questions 20–22):
1,146 of 1,604 records publish **no website we know of**, and no instrument exists for that — ADGM's
snapshot carries 13, DFSA/CMA/REGAFI none, and SIRENE has no URL field at all, all checked. And only
38 records have a real named human; this connector collects routes, not people.

`robots.txt` obeyed (5 firms declined and are not retried), one request at a time, GET only.
157 Python tests · 19 site tests · build deterministic.

## 2026-09-23 — the queue is not sendable, and why

Checked whether the 67 "qualified and contactable" records could actually be written to. They
cannot, and the reason matters more than the number.

**Zero records carry a trigger. Zero.** What makes those 67 `qualified` is an ICP *fit* score —
"priority segment fund_manager (20) + priority market France (15) + multi-asset" — which describes
what a firm **is**, not why we are writing to it **now**. Our own outreach rule 4 is explicit: if we
cannot name why we are writing to this firm at this moment, we are not ready to write. So the
pipeline currently has contact routes and fit, and no reason to send anything.

That makes the trigger scan (`plan/data-and-intake.md` M4) the binding constraint, not more
sourcing and not more addresses.

**Fixed first, because the trigger scan would have been built on it:** `append_events` appended
blindly. A day's snapshot is overwritten by each run while the diff baseline stays yesterday's, so
every run of the same day re-detects the same change — three runs on 2026-09-23 logged one phone
change on SEVENTURE PARTNERS three times. Events are now deduplicated on (date, register, firm,
field, before, after); `woke` is deliberately excluded from that identity, since it describes our
state rather than the event. The three existing duplicates were collapsed to one.

An inflated trigger feed is worse than a quiet one: the entire value of a trigger is that it means
something happened.

## 2026-09-23 — UAE non-register sources investigated: exchanges, associations, commercial data, press

Andre asked for every non-register UAE source for asset managers, fund managers, family offices and
MFOs, paid options in scope, priced where possible. Full findings in
`plan/uae-sources-commercial.md`.

**Resolved a name-collision that could have caused a bad claim later:** "Arab Family Office
Association" does not appear to exist. Our standing "AFFO publishes no member directory" fact is
about the French AFFO (Association Française du Family Office). The real UAE body is the Emirates
Family Office Association (EFOA) — separately confirmed, also with no public member directory,
approval-only membership, explicit no-solicitation policy. `memory/facts.md` updated so the two are
never merged again.

**What's actually usable, free:** Nasdaq Dubai's member list (clean static HTML, custodians and
settlement banks named) and the Global Private Capital Association's Middle East Council page (9
named individuals at MENA private-capital firms). DFM and ADX broker directories exist but are
JS-rendered and, for ADX, sit behind Cloudflare bot management that blocked our fetch tool twice
while a plain `curl` got through — flagged as bot-sensitive, not defeated.

**Priced what could be priced, honestly labelled by source:** Crunchbase Pro ($588/yr, published)
and LinkedIn Sales Navigator ($1,080–$1,800/yr, published) are the only two providers with a real
published price. Preqin, PitchBook, S&P Capital IQ, Bureau van Dijk, With Intelligence, Wealth-X,
Refinitiv/LSEG Workspace, Campden Wealth, FINTRX — none publishes a price; every figure quoted for
them is a third-party estimate, labelled as such.

**Recommendation, if one purchase were made:** a boutique, UAE-specific family-office dataset (e.g.
allfamilyoffices.com's "171 UAE family offices / 501 contacts") over any global platform — it targets
the one CRM cell (UAE × family office) that has zero coverage by structural design, at a fraction of
the cost of a global terminal built for a different job. Its own price was not found published;
logged as open question #23.

New open questions #23–24 in `memory/open-questions.md`.

## 2026-09-23 — UAE source investigation, and the register we were under-reading

Andre redirected: stop on triggers, grow the database, start with UAE, find every source "public or
not". Three parallel investigations plus my own check of what we already hold.

**The biggest win was a source we already read.** The DFSA publishes ~50 financial-service
categories; our connector queried **four**. Five unqueried ones held 613 firms not in the CRM.
Extended to nine services — measured result: **UAE 570 → 682 records, CRM 1,611 → 1,723**
(fund managers +57, brokers +46, custodians +8).

⚠ **Precision was chosen over volume, and the refusals matter more than the additions:**
- **Representative offices (200 firms, 195 new)** — T. Rowe Price, Blackstone, Euroclear, Baring,
  Partners Group. A representative office **cannot conduct financial business**; the platform
  decision sits at the parent abroad. Magnificent in a pipeline report, ~zero conversion.
- **Advising on Financial Products (810)** and **Arranging Deals (817)** — mixed with insurance and
  credit advisers. Volume without precision; the *Agent PSP* mistake in better clothing.
These belong in the candidate queue, not the CRM. Recorded as a decision, not a backlog item.

**A mis-mapping found:** we label fund *administrators* `fund_manager`. Administration is
NAV/registrar/reporting, not management — and the genuine service, *Managing a Collective Investment
Fund* (213 firms), was never queried. Logged as open question #25 rather than silently re-segmenting
33 live records on a connector's say-so.

**Onshore UAE — verified live, and the agent's claim needed correcting.** SCA was renamed the
**Capital Market Authority (UAE)** on 1 Jan 2026; `sca.gov.ae` redirects to `uaecma.gov.ae`. ⚠ That
collides with the Saudi CMA we already track: every reference must now carry a country.
The bulk endpoint the investigation reported did not reproduce for me — a flat payload returns
`400 Invalid Integration Parameters`. Reading the register page's own JS gave the real shape:
parameters nest inside `urlParameters`. **Confirmed: 322 onshore-licensed companies**, fields
`code/name/status/website/year` — and `website` is published, which matters because 543 of 567 UAE
records had none. ~113 new firms in our segments.
⚠ An honest User-Agent alone gets HTTP 403; sending the page's own Referer/Origin returns 200. That
is an origin check, not bot protection — we send the correct request context and do **not** spoof a
browser identity.

**Three dead ends, closed with evidence rather than left to be re-hunted:**
- **DMCC** — verified in their own terms: forbidden to reproduce the directory "for use on your own
  website, database or products" or to use it "for email or telephone marketing". That is exactly
  what we would do with it, so it is a permanent decision, not a technical backlog item.
- **DIFC company register** (Vercel challenge) and **ADGM Registration Authority** (Akamai 403) —
  blocked, reported, not evaded.
- **UAE family offices: no register exists anywhere.** DIFC states family arrangements sit on "a
  private register … on an independent server"; the Family Wealth Centre publishes no directory; the
  DFSA's Single Family Office category is wholly withdrawn; EFOA is approval-only with a
  no-solicitation policy. Not a scraping problem — a market that deliberately does not publish.

**A correction to my own work:** `plan/source-architecture.md` listed "AFFO publishes no member
directory" in a Gulf context. **AFFO is French** — `knowledge/market/landscape.md` had this right
all along and my plan doc conflated it with a Gulf body. The UAE association is **EFOA**
(`emiratesfoa.com`, verified reachable). Fixed.

**Still to read:** the fund registers, which name their managers and which we do not touch at all —
ADGM 340 funds via a single POST (109 distinct managers among 279 active), DFSA 295 funds.

## 2026-09-23 (later) — `tools/connectors/cma_uae.py`: UAE onshore, the first non-free-zone source

Built the connector the investigation above scoped, and went one step further: `integrationId 2055`
— the per-company detail call the investigation flagged as unverified — was found in the register
page's own inline JS (a "view company" handler) and confirmed live against real firms. It is a
genuinely good source: `CompanyDetails` carries `Email`, `Telephone`, `City`, `CompanyAddress` and
`EstablishedDate`, published by the regulator on its own register, for firms that state one — the
same shape of win FSRA (ADGM) already gave us, now also onshore.

**Segments — measured live, matching the directive exactly:** Investment Fund Management (39) →
`fund_manager`; Portfolios management (44) and Profit Sharing Asset Management (1) → `asset_manager`;
Securities Central Clearing (2) → `custodian`; Trading and clearing broker (26), Trading broker (3)
and Trading broker in the international markets (36) → `broker`. 93 unique firms across the seven,
50 of them holding more than one — deduped by the register's `code`, every held category kept in
`licence_type`, segment resolved by the priority order in the table above (fund management outranks
general portfolio management, which outranks brokerage).

**Deliberately left unmapped** (open question #26): "Custody" (`type=9`, 6 firms, distinct from the
mapped "Securities Central Clearing") and "Trading broker of OTC derivatives and currencies in the
spot market" (`type=3`, 27 firms) — neither was part of the directive, so neither was guessed at.

Registered in `run_all.py`'s `CONNECTOR_MODULES` and in `knowledge/market/source-coverage.yaml`
(UAE × asset_manager, fund_manager, mfo). 17 new tests in `test_cma_uae.py`, no network, stubbing the
one seam (`_call`) both the listing and the detail lookup pass through — `python -m pytest tools/ -q`
stays green at 176. `--only cma-uae --dry-run` runs clean: 93 entries, correctly a baseline run.

⚠ Not run for real and not committed, on instruction — Andre runs the backfill himself. One thing to
know before he does: like `dfsa_difc.py`, this connector only learns a firm's licence date from the
per-candidate detail call, so a plain (non-`--backfill`) first run would create nothing — the listing
alone has no date field to filter on. Run `--backfill` for the first pass, exactly as DFSA and FSRA
needed.

## 2026-09-23 — UAE onshore connected: 1,611 → 1,811 records

`tools/connectors/cma_uae.py` is live. UAE **570 → 767** active records; the CRM **1,611 → 1,811**.
UAE contact routes: email **119 → 197**, website **24 → 99**.

⚠ **The regulator renamed itself.** SCA became the **Capital Market Authority (UAE)** on 1 Jan 2026
(Federal Decree-Laws 32/33 of 2025); `sca.gov.ae` redirects to `uaecma.gov.ae`. That collides with
the Saudi CMA we already read, so the register is `cma-uae` and the regulator string is always
spelled "Capital Market Authority (UAE)" — never a bare "CMA" anywhere a human will read it.

Two things the build got right that are worth keeping: the per-company detail endpoint returns
`Email`, `Telephone` and `City`, so onshore firms arrive with a contact route rather than just a
name; and a flat payload returns `400 Invalid Integration Parameters` — the parameters nest inside
`urlParameters`, which only reading the register page's own JS revealed.

⚠ **An honest User-Agent alone gets HTTP 403 here; adding the page's own Referer/Origin returns
200.** That is an origin check, not bot protection, so we send the correct request context and do
**not** spoof a browser identity. Worth stating because the distinction is the whole line we hold.

### The fund registers: a headline that did not survive checking
The investigation's most actionable finding was "109 distinct fund managers" on the ADGM fund
register. The mechanics were exactly right — 340 funds, 279 active, manager named on every row — but
the number to act on is **16**, the managers not already held, and 16 does not survive either:
spelling variants (`BlackRock Fund Managers Limited` / `Blackrock Fund Managers Ltd`, two Chimeras)
collapse it to about a dozen, and most of the remainder are US managers of ADGM-**domiciled** funds
— Avenue, Blackstone Real Estate, EIG, Falcon Edge, Hollis Park, McKinley. Where a vehicle is
registered says nothing about where its manager buys software: the representative-office trap again.
**Not worth a connector.** If read at all it feeds the candidate queue.
⚠ Gotcha for whoever does read it: the API **ignores `itemsPerPage`** and returns 10 rows whatever
you ask for, so anything trusting that field silently sees 10 of 340.
The DFSA fund register (295 funds) stands as the investigation measured it — I could not verify it
myself, its funds page uses a different token pattern from the firms page, and it is recorded as
unverified rather than assumed.

## 2026-09-23 — the DIFC firms we refused, actually written down

I said the DFSA's broad service categories "belong in the candidate queue, not the CRM" and then did
not write them there. That is the worst of both worlds: the firms are neither recorded nor visible,
and a deliberate judgement looks like an oversight. Fixed — `dfsa_difc.py --candidates` proposes
them with the reason attached. **1,134 written, 715 not already in the CRM.**

| Service | Candidates | Why it is not a record |
|---|---:|---|
| Advising on Financial Products | 421 | mixes wealth managers with insurance and credit advisers |
| Operating a Representative Office | 195 | **cannot conduct financial business** — a liaison presence |
| Arranging Custody | 60 | arranging, not providing — a referral relationship |
| Arranging Deals in Investments | 39 | same mix as advising |

⚠ **And the queue did not sort.** All 715 landed in a 16-point band with 342 tied at exactly 20 —
identical fields from one register, so the generic signals could not tell a representative office
from an advisory firm. A queue where nothing is above anything else is a pile with a number on it.
Candidates now carry optional `weak_signal` / `strong_signal` in `extra`, which the score moves ±12
and names in the reasoning; the DFSA connector sets it for representative offices and arranging-
custody. The spread is now 8–32 and the things we documented as near-worthless sit at the bottom.

### France: checked, and the answer is no
The DIFC lesson was that we under-read a source we already had, so I checked the AMF the same way.
**It is fully read** — the AMF publishes exactly five datasets on data.gouv.fr (short positions,
blacklists, the SGP list we take, the crypto PSAN whitelist, "biens divers") and only one is ours.
No hidden categories, unlike DIFC.

**ORIAS** (`orias.fr`) is the genuine remaining French gap — French MFOs and wealth advisers register
as *conseillers en investissements financiers* rather than as SGPs, so they are invisible to the AMF
list. Its advanced search is a CSRF-protected POST form (`SYNCHRONIZER_TOKEN`, `categorieIfinance`
checkbox with value `CIF`); a first probe returned a page but no usable result count, so the required
criteria are not yet understood. **Parked, not abandoned** — and worth noting the population is
thousands of mostly small IFAs, so like *Advising on Financial Products* it should propose
candidates, never create records.

## 2026-09-24 — the promotion path, and what we decided to dismiss

Andre: decide and promote yourself, do the research, and **show me what you dismissed** — the
website is a view of structured data.

**Decisions are now data.** `crm/candidates/decisions.jsonl`, append-only, last-write-wins, with
`accept` / `reject` / `defer` and a **mandatory reason**. A rejection without a reason is
indistinguishable from an oversight: six months on, nobody could tell whether a firm was examined
and turned down or simply never looked at. The site renders it — Candidates now has waiting /
dismissed / promoted tabs, and a dismissal shows its reason beside the firm.

**265 dismissed, each with a reason.** 195 DIFC representative offices (a rep office cannot conduct
financial business; the parent may be a prospect, this entity is not) and 60 arranging-custody firms
(arranging is a referral, not a custody operation).

**5 promoted**, after verifying the ambiguous ones against GLEIF rather than trusting my own reading:
Alinma Investment, AlJazira Capital, Stronghold Capital Management, **SNB Capital** and **Jadwa
Investment Company**. Three rejected with specific reasons — BlackRock Saudi Arabia (builds and sells
Aladdin, structurally not a buyer), the Saudi Real Estate Development Fund (GLEIF categorises it as a
FUND; a government housing programme), OMF (ME) JV GP (the general-partner SPV of a single JV fund).
One deferred: GLEIF publishes only an Arabic legal name and my transliteration is not a verified fact.

⚠ **A real error, caught and corrected.** The duplicate check first dismissed SNB Capital and Jadwa
Investment as duplicates of `snb-capital-difc-limited` and `jadwa-investment-difc-limited`. Those are
the groups' **DIFC subsidiaries** — UAE, DFSA-regulated. The candidates were the **Saudi parents** in
Riyadh: different country, different regulator, different legal person, and two of the largest
managers in our thinnest market. `find_companies` now takes a `country` and caps a cross-country
namesake below the duplicate threshold, with a test naming the firms it cost us. Saudi 35 → 41.

⚠ **And a bug I introduced an hour earlier:** `load_all()` globs `*.jsonl` in the candidates
directory, so `decisions.jsonl` was being read as a candidate file — decision rows have no `source`
and broke every reader. Fixed and tested.

### Family offices: my earlier conclusion was wrong
I wrote that "no register anywhere will produce named UAE family offices". **The DFSA still lists 41
by name**, and none were in the CRM — Binghatti Holding, Al Murjan International Holding, Chanrai
Investments, Stephens Investments Holdings, Massar Investments and 36 more. I read *Withdrawn* as
"the source is dead"; the **category** was withdrawn, not the firms. DIFC moved single-family offices
to the Family Wealth Centre in 2023, so this is a frozen 2023 snapshot — stale, needing verification,
and the only enumerable list of named Gulf family offices found anywhere. Ingested as candidates at
score 54, the highest-ranked block in the queue after GLEIF.

## 2026-09-24 — UAE family offices: 0 records → 66 named candidates

Andre: "there are much more in the UAE, much more. Can't you find them via web search, checking
website? LinkedIn? other solutions?" He was right.

**66 named UAE family offices and MFOs now in the queue**, from three routes, none of them a register:

| Route | Found | Note |
|---|---:|---|
| DFSA Single Family Office listing | 41 | the withdrawn *category*, not withdrawn firms — a frozen 2023 snapshot |
| Trade press, conference and own-site research | 18 | incl. 6 genuine **MFOs**, which manage third-party money and are the better prospects |
| Family groups and GLEIF corporate structures | 7 | Al Majid Investment, Al Tayer's ITG, Al Habtoor Investment, Seddiqi & Sons, three Al Ghurair branches |

Named MFOs found: Abbey Road Investment Group, Pharos MFO, McFaddens & Co (UAE), Advani Family
Office, Equalis Capital, Charles Park. Named SFOs include Apeiron (Christian Angermayer, ADGM),
KAAF (Mishal Kanoo), Vivium (Elie Khouri), Almulla Capital, Boschen, 76Columbus, Daher.

⚠ **Three traps caught by the research and preserved in the candidate text rather than smoothed over:**
- Dubai's **Equalis Capital Ltd** (DIFC, equalis.ch) is a completely different company from
  `equalis-capital-france` already in the CRM (Paris, AMF-licensed). Do not merge.
- **"Al Ghurair" names at least three legally separate entities** across different family branches,
  plus a fourth domain flagged as a likely scam site trading on the name, which was NOT ingested.
- Al Ghurair Group's "Family Office" is a **function on an org chart, not an incorporated entity** —
  deliberately not added as a record.

On LinkedIn: public company URLs surfaced by a search engine were recorded; the site itself was not
scraped and no login was used. That line does not move.

### A false positive that would have hidden a real firm
`crm.py find` matched **"Small House Capital (Single Family Office FZE)"** to **"Finance House
Securities"** at a confident 0.90. Cause: once generic industry words are stripped, Finance House
Securities reduces to the single word **"house"** — and a one-word core contained in a six-word name
scored full containment. Single-token containment is genuinely needed ("Jadwa" → "Jadwa Investment
(DIFC) Limited"), so the fix is about distance: one word may stand for a name of at most two words.
Both cases are now tests. ⚠ Without this, a real Dubai family office would have been silently
absorbed into an unrelated broker's record.

⚠ **Known performance limit:** `find_companies` reloads all 1,816 YAML records on every call, so
bulk re-resolution of 25 candidates times out. Fine for the one-at-a-time use it was built for;
it needs a cached index before any bulk promotion pass.

## 2026-09-24 — UAE family offices: 0 records → 22

Promoted from the candidate queue after verification. **UAE family_office 0 → 13, mfo 4 → 9.**

**The 9 MFOs are the better prospects** — an MFO manages several families' money by way of business,
which is the multi-portfolio, multi-currency problem Gaia exists for. Promoted: Abbey Road
Investment Group, Pharos MFO, McFaddens & Co (UAE), Advani Family Office, Equalis Capital Ltd.

**Family offices promoted:** Apeiron (ADGM's own announcement), Vivium, Almulla Capital, Al-Kabir,
Daher Investments, 76Columbus, Boschen, KAAF (Mishal Kanoo), Stonegate Capital, plus three family
investment vehicles verified against primary sources — Al Majid Investment (the group's own site
describes multi-asset management), Al Tayer's ITG (a 2024 deal record proves it is active, not a
dormant shell), Al Habtoor Investment and Seddiqi & Sons.

**The dividing line was evidence, not enthusiasm.** 8 deferred with reasons rather than recorded:
- **All three Al Ghurair entities.** The name covers at least three legally separate branches, one
  domain 404s, and one self-describes as a holding company that never uses the words "family
  office". Creating records now risks attaching activity to the wrong branch.
- **Sabban Holdings** — a single aggregator profile. Everything else promoted rests on the firm's
  own site or a primary source, and that bar is worth keeping.
- **Small House Capital** and **Advantage Family Office** — strong names, quoted CIOs, and no
  findable website or LinkedIn page at all. A record nobody can reach is not yet an asset.
- **Charles Park Family Office** — entered Dubai only through a partnership; no UAE entity of its own.

### The resolver had to be made usable before any of this
`find_companies` re-read all 1,821 YAML records on **every call**, so a bulk pass over 25 candidates
timed out outright — fine for the one-at-a-time use it was built for, useless for the promotion pass
it was needed by. Records are now parsed once per process.

⚠ **The dangerous half is the invalidation, not the cache.** A promotion pass creates a record and
then resolves the NEXT candidate against the CRM; a stale index would not see what it had just
written and would create the same firm twice — reintroducing the exact failure the resolver exists
to prevent. `save_yaml` therefore invalidates it, and a test asserts both halves. The cache also
leaked between tests until an autouse fixture cleared it, which is the same bug wearing a different
hat.

## 2026-09-24 — the 41 verified: UAE family offices 0 → 37

All 41 DFSA-listed Dubai family offices were checked against public sources before any became a
record. **UAE family_office 0 → 28, mfo 4 → 9 — 37 in a segment that held nothing this morning.**
Named humans in the UAE went 19 → 25, which matters more than the firm count: we had almost none.

| Verification outcome | Count | What we did |
|---|---:|---|
| Confirmed active family offices | 19 | promoted, with named people where published |
| Confirmed closed or dissolved | 3 | rejected — Merriment (dissolved 2015), Tree Tops (in liquidation), Turtle Management (ceased as an FO Jan 2019) |
| Exist, but not investment-managing FOs | 5 | 2 rejected, 3 deferred |
| Unconfirmed | 14 | deferred |

**Rejected despite being active**, because the DFSA category misleads: **Binghatti Holding** is the
group holding company of a Dubai property developer with ~10,000 employees, and **Himalaya Global
Holdings** the same for a pharma/FMCG group. Both are family-GOVERNANCE structures over operating
conglomerates, not portfolio-managing family offices.

**14 deferred as unconfirmed.** No website, no LinkedIn, no press, no current GLEIF record — only the
frozen 2023 listing. They may well exist; we cannot show it, and a record we cannot stand behind is
worse than none.

⚠ **A decision reversed, which is what the append-only log is for.** Sabban Holdings was deferred
hours earlier on a single aggregator source. Verification confirmed it active — Al-Sabban family,
DIFC since October 2013 — so it is now accepted, and the reasoning says the bar was right and the
evidence has now met it.

⚠ **Entity traps caught and written into the records rather than smoothed away:** The KEF Company's
GLEIF record is a DIFFERENT, retired BVI entity; Massar Investments' LEI shows LAPSED, which means an
unrenewed LEI and **not** a closed firm; Blu Stone Management and Blu Stone Capital are distinct DFSA
entities at one address; Dubai Wing is yet another Al Ghurair branch; Maddox Street's licence date is
two years stale and is flagged on the record.

⚠ **AC Limited is recorded but is not an ordinary prospect.** It is the family office of Sheikh
Mohamed bin Zayed Al Nahyan, President of the UAE. It is in the CRM because it is a real, active
entity in our segment — the record says explicitly that any contact at all is Andre's decision alone.

**Two process bugs, both mine:** `cmd_contact` needs a `source` argument and the script died at the
second record without it; and re-running would then have flipped the two already-created records into
"duplicate" rejections, because a firm we had just created ourselves looks exactly like one that was
already there. The re-run now skips anything already accepted.

## 2026-09-24 — the ADGM audit: I was wrong, and that is the useful result

I told Andre that 162 ADGM firms sat outside the CRM and that it looked like "the same shape as
DIFC", where we had been querying 4 of ~50 service categories. **The audit says otherwise.**

Read every missing firm's detail page and classified it structurally — reading the register's own
activity table rather than testing our six needles against it, because the point was to discover
names we do not know:

| Why it is missing | Count |
|---|---:|
| **All authorisations WITHDRAWN** | **106** |
| Holds activities we do not map | 38 |
| Lists no regulated activity at all | 20 |
| **Detail page unreadable** | **0** |
| **Should have matched and didn't** | **0** |

**The FSRA connector is sound.** Zero unreadable pages, zero wrong skips. 106 of the 164 are simply
withdrawn firms, correctly excluded, and the 20 with no activity are reinsurers, payment and tech
companies (ADNOC Reinsurance, Hubpay, Lean Technologies) — not our segments.

The real gap is small and specific: **10 fund administrators** ("Acting as the Administrator of a
Collective Investment Fund") and **12 *Arranging Deals in Investments*** firms — the latter being
exactly the low-precision category we already refuse to create records from in DIFC, so refusing it
here is consistency rather than an oversight.

⚠ Fund administrators are deliberately NOT added yet. `crm/SCHEMA.md` has no segment for a service
provider, DIFC's 33 administrators are already mis-labelled `fund_manager` (open question #25), and
adding ten more would compound an error rather than fix it.

**Banco Santander**, the case that prompted this, falls in the withdrawn or no-activity bucket — not
a silently dropped bank.

### Meanwhile the onshore CMA does have the DIFC shape
52 unmapped categories hold firms, 906 firm-slots in total. Most is correctly out of scope
(Introduction 186, Promotion 137, Telemarketing 57, exchange-access permissions). But three are
genuine inconsistencies with segments we already carry elsewhere: **Custody** (6 firms), **Trading
broker of OTC derivatives and currencies** (27) and **Commodity Brokerage** (6). We map custody in
DIFC and brokers in three other categories here.

**Acted on it:** mapped Custody (id 9) and OTC-derivatives/spot broking (id 3) in `cma_uae.py`.
UAE 801 → 810 records; custodians 23 → 25, brokers 103 → 110. The connector's own test asserted
those two were *deliberately* left open, so the test was updated to record that the decision
changed and why — the exclusion was an inconsistency, not a scope judgement.

⚠ **Commodity brokerage (ids 22, 23, 24) stays excluded, and that IS a scope judgement.** Our other
brokers trade securities and currencies, instruments a multi-asset portfolio holds; a commodity
broker clearing physical trades is an execution business. Mapping it would widen `broker` until the
segment stopped meaning anything — the same reasoning that refuses DIFC representative offices.

## 2026-09-24 — Saudi: 39 → 47 records, and a merge rule that had to change

The UAE playbook applied to our thinnest market. Two investigations; the family-office one is in,
the regulator one has landed and is not yet built.

**8 verified Saudi family offices and investment arms promoted**, each from the firm's own site or a
primary source: **MASIC** (explicitly "to exclusively manage the assets of the family of the late
Mohammed I. Alsubeaei"; CEO Ihsan Abbas Bafakih), **AlTouq Group** (self-described Saudi family
office since the 1970s), **Alajlan Family Office**, **AlRajhi Partners** (CEO Saad AlGheriri plus two
MDs), **Majd Investment** (Almajdouie), **Zahrat Al Amaal** (Fawaz Alhokair — and it carries a dated
trigger, a March 2024 direct-lending JV with Z Capital Group), **Zamil Group Investment Company**,
**Abunayyan Investment Company**. Saudi named humans 0 → 7. Four hybrids deferred where
conglomerate-versus-investment-office status is genuinely mixed: Xenel, Al Fozan, Khaled Juffali,
JIMCO.

⚠ **Two wrong auto-merges, and the second was flagged in advance by our own research.**
- "Alajlan Family Office" was folded into `the-family-office-ksa` — The Family Office International
  Investment Company, an unrelated firm sharing only the words *family office*.
- "AlRajhi Partners" was folded into `sulaiman-alrajhi-holding-financial-investments` — a different
  Al Rajhi branch. The research file had explicitly warned the Al Rajhi name covers four entities.

**Root cause: my promotion scripts treated the resolver's top hit at 0.90 as identity**, while
`find_companies`' own docstring says it ranks and does not decide. Callers kept ignoring that.
`crm.same_firm()` is now the decision, made once and conservatively: it resolves only at 0.97+, and
returns the near-misses so the caller can see what it nearly matched rather than getting a silent
`None`. Both records were created properly afterwards.

⚠ A consequence worth knowing: short-form resolution ("Jadwa" → "Jadwa Investment (DIFC) Limited")
scores 0.90 and therefore no longer auto-resolves. That is correct for a machine promoting in bulk
and wrong for a human typing a name — which is why `find_companies` stays the tool for `/intake`
and `same_firm` the tool for automation.

### The Saudi regulator investigation — found, not yet built
Following the same method that cracked the UAE (read `sitemap.xml`, not the navigation) surfaced two
sources the existing connector never mentioned:
1. **CMA "Institutions under supervision" .xlsx** — a plain unauthenticated download with **~219
   named Capital Market Institutions**, of which **~122 are asset/fund managers WITH AUM figures**.
   We currently read 36 of 242 from the HTML page. AUM is a scoring signal we have for no other
   Saudi record.
2. **SAMA `PortalHandler.ashx`** — an open JSON endpoint returning **all 39 licensed Saudi banks**
   plus 91 finance companies. ⚠ This closes `Saudi × bank = 0`, which the coverage view currently
   reports as having **no instrument at all**.

Confirmed blocked and not pursued: Tadawul (Akamai 403 on every path, including robots.txt),
`data.gov.sa` (TCP timeout, same geo-block signature as the CMA API), Ministry of Commerce (CAPTCHA).

## 2026-09-24 — the UAE web sweep: registers validated, two claims checked and dropped

Andre pushed: "you don't scan Google or LinkedIn?!" He was right about the imbalance — **773 of our
810 UAE records came from registers and only 30 from web research**. I had been reaching for search
only when a register failed me, rather than treating it as a source.

**First sweep back, and its headline is reassuring rather than exciting: the open web kept
re-surfacing firms we already hold.** HK Asset Management, Introspect Capital, GSB Capital, Century
Financial, Al Mal Capital, SHUAA, Noor Capital, Al Ramz and others all turned up and are all already
in the CRM via the DFSA/FSRA/CMA connectors. That is a genuine independent check that the register
connectors are working. Only **3 verified new firms** outside those registers.

⚠ **One of those three is worth more than a firm: Finsbury Associates is licensed by the UAE
INSURANCE AUTHORITY** — a regulator we read nothing from. That is a missing instrument, not a
missing record.

### Two claims from the research, both checked and both dropped
1. **"152 relevant CMA firms vs 97 in the CRM — an ingestion gap."** Checked: every one of the 103
   snapshot entries is in the CRM; there is no gap. The 152 is a **sum of category counts**, which
   double-counts firms holding several licences. The distinct union is 103 — exactly the trap
   `plan/uae-sources-dfsa.md` already warns about ("the sum is meaningless and only the measured
   union counts").
2. **"Abacus Financial Consultants (CP-0000182) is registered but not ingested."** Checked against
   the full 322-row register: **no firm matching that name exists on it**. Not a missed ingestion.

Both were plausible, specific and wrong. Logging them as open questions would have sent someone
chasing a gap that is not there.
