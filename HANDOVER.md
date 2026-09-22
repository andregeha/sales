# Handover — updated 2026-09-22 (first laptop session)

The cloud session built this workspace; the first laptop session made it work. This is what is
true now.

## The headline
**The network block is gone, and the register engine is built, tested and running.** That was the
entire premise of moving to the laptop, and it held. Every regulator register and tender portal we
need is reachable.

## State
- **Branch:** `claude/dreamy-rubin-v70dkq` · ⚠ **committed locally, NOT pushed** — the sandbox
  blocked `git push`. **Push before starting anywhere else**, or work will diverge.
- **CRM:** **104 companies** (was 57) · 1 RFP (a schema example only) · `crm.py validate` exits 0.
  - 58 qualified · 36 nurture · 7 disqualified · 2 researching · 1 new.
  - Saudi Arabia 37 · France 28 · Lebanon 17 · UAE 22.
  - **39 records carry a named person, 23 of them with a real contact route** (was 20 and 0).
  - **Still zero invented contact details.** Every email and phone is either sourced or `null`.
- **Nothing is scheduled.** Still the case. See question 17.

## What works now
| Thing | State |
|---|---|
| **AMF France connector** | ✅ Live. 666 firms, daily CSV. ~2 new licences/month. Publishes websites and phone numbers. |
| **Saudi CMA connector** | ✅ Live but **partial** — reads the 36 most-recently-updated of 242, newest-first. Catches new names; cannot see disappearances. |
| **Register enrichment** | ✅ Fills website/phone gaps on existing records from regulator-published fields. |
| **RFP radar** | ✅ TED + BOAMP searched through their real APIs. France is a **measured zero**. |
| **Outreach** | ✅ Four drafts ready in `outreach/2026-09-22-top-leads.md`. |

Run it all: `python tools/connectors/run_all.py` then `python tools/connectors/enrich_from_registers.py`.
Test it: `python tools/connectors/test_connectors.py` (25 tests, no network).

## What does NOT work, stated plainly
1. **Saudi tender coverage is ZERO.** Etimad serves its own bot-detection challenge. **We do not
   attempt to defeat bot protection.** This needs a human with an Etimad supplier account.
2. **Abu Dhabi ADGPG and Dubai eSupply are JS single-page apps** — unreached, not checked.
3. **The Saudi CMA Open Data API times out from Europe.** It would give all 242 firms in one call
   and allow disappearance detection. **Try it from the Riyadh office.**
4. **Three market × segment combinations are still empty:** Saudi banks, Lebanese family offices,
   French banks.
5. **Contact routes remain the binding constraint** — not lead volume. 39 names, 23 routes, and
   most of those routes are LinkedIn rather than email.

## Hard-won facts — do not relearn these
- **A 200 does not mean success.** The Saudi CMA returns a styled error page with HTTP 200; Etimad
  returns a bot challenge the same way. Check the **content**, never the status code.
- **An API being dead does not mean the register is unreachable.** I wrote Saudi off on the strength
  of its timing-out API; the register *page* server-renders its entries perfectly well. Check the
  page before concluding a source is blocked.
- **The Saudi CMA moved from `cma.org.sa` to `cma.gov.sa`** and calls licensed firms **"Financial
  Market Institutions"** (formerly "Authorised Persons"), not "CMI".
- **The AMF's CSV URL is timestamped and changes daily** — resolve it via the dataset API each run.
- **Registers publish contact details.** Storing a regulator-published website or switchboard number
  is *not* the same as guessing an email pattern. The rule was never "no contact details" — it was
  **"nothing invented"**.
- **A connector that cannot read its source must raise and write nothing.** Zero entries from a live
  register is a bug, not a quiet day.
- **The Web Portal is a SEPARATE PRODUCT from Gaia**, on the same database. Not a module.
- **Windows:** `python`, not `python3`. The console is **cp1252** — set `PYTHONIOENCODING=utf-8`
  before printing anything accented or Arabic, or it will crash or mangle.
- ⚠ **The handover's "Barjeel Geojit has a fund open for subscription right now" was STALE** — that
  NFO closed 2026-02-13. Their website banner still says otherwise. **Check dates against a live
  source before building outreach on them.**

## What Andre owes us — the four that matter
1. **Which client names may we reference, and to whom.**
2. **Which Lebanese banks are on the survivor track** — unblocks 17 frozen records.
3. **A LinkedIn Sales Navigator seat** — turns names into reachable people.
4. **Pricing · off-limits firms · do we control the OFS website.**

Plus, new and cheap: **set up the free BOAMP and PLACE saved-search email alerts.** They take
minutes, they are free, and a push alert beats any scraper we could write. Full list (20 open) in
`memory/open-questions.md`.

## The rules that do not change
Agents **never** contact anyone — draft, queue, hand to Andre. Never invent a company, person,
contact detail, metric, date or tender. **Never attempt to defeat bot protection or a WAF.** Ground
every client-facing claim in `knowledge/`. The New Gaia is roadmap (Jan 2027 demo · Jun 2027 alpha ·
Q4 2027 deploy). Log every touch. **A quiet day reported honestly is worth more than a padded one —
and a source we could not read is not a quiet day.**
