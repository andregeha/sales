# Changelog

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
