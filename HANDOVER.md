# Handover — 2026-09-22

The cloud session that built this workspace is ending. This is what exists, what is true, and what
to do next. The paste-in prompt is at the bottom.

## State
- **Branch:** `claude/dreamy-rubin-v70dkq` · 19 commits · 119 files · all pushed.
- **CRM:** 57 companies · 1 RFP (a schema example only) · `crm.py validate` exits 0.
  - 22 qualified · 2 researching · 28 nurture · 5 disqualified.
  - Lebanon 17 · UAE 14 · France 14 · Saudi Arabia 12.
  - 20 records carry a named person. **Zero invented contact details — every email and phone is `null`.**
- **Nothing is scheduled.** The cloud daily run (`trig_01R44y3zto5gaxgBChoFxy1L`) was disabled when
  the laptop became primary. Disabled, not deleted.

## What was built
`CLAUDE.md` (the constitution) · `knowledge/` (company, product, positioning, market — ICP with a
0–100 score, landscape, a 30-URL RFP source registry) · `crm/` (the system of record) ·
`tools/crm.py` + `tools/crm_report.py` · `memory/` (facts, decisions, 19 open questions, changelog) ·
`playbooks/` (daily-run, lead-sourcing, outreach, rfp-radar, inbound, discovery, demo, qualification) ·
7 agents · 8 skills.

## The five best leads
| Score | Firm | Market | Why now |
|---|---|---|---|
| 93 | Patrimium Asset Management | UAE (DIFC) | Converted single→multi-family office; $100m NAV facility |
| 88 | Hope Asset Management | France | New AMF licence + multi-asset fund launch (PE, infra, RE, listed, commodities) |
| 88 | Capital Asset Management | UAE (DIFC) | New DFSA licence Mar 2024 — no incumbent |
| 83 | Barjeel Geojit | UAE | **Fund open for subscription now** — fund administration is a direct fit |
| 78 | Fundcraft France | France | New AIFM licence; a ManCo-as-a-service is itself a multi-fund admin buyer |

**Barjeel Geojit is the one with something happening this month.** Everything else is a standing reason.

## What is NOT done — the real backlog
1. **Register connectors — not built.** The single highest-value automation. Spec in
   `tools/connectors/README.md`. Impossible in the cloud; possible on the laptop. **Do this first.**
2. **RFP radar has found nothing.** One run, ~19 searches, zero tenders. That is a *"found nothing
   indexable"* result, **not a confident zero** — Etimad, BOAMP and TED could not be opened at all.
   Re-run properly from the laptop.
3. **No outreach drafted.** 20 firms have a named person and **no contact route**. This is the
   binding constraint on the whole engine, not lead volume.
4. **Lebanon needs Andre.** All 17 banks are `nurture` because no public source says which Law
   23/2025 restructuring track any of them is on. A bank in resolution buys nothing.
5. **8 of 12 market × segment combinations unsourced** — UAE banks & asset managers, KSA banks &
   family offices, Lebanon family offices & asset managers, France banks & family offices.
6. **The daily run is not scheduled on this machine.**
7. **`competitors.md` is thin** — one real sighting (Amwal Capital → Broadridge IMS, May 2024).

## Hard-won facts — do not relearn these
- **The Web Portal is a SEPARATE PRODUCT from Gaia**, on the **same database**. Not a module.
  Andre corrected this; it was wrong in four files.
- **Never invent a contact detail.** No guessed email patterns. Unknown is `null`. This rule has
  held across 57 records under real pressure — keep it.
- **PyYAML parses unquoted dates into `date` objects** and used to break everything. Fixed by
  normalising on load. Don't undo it.
- **`--website null` used to store the string `"null"`.** Fixed. An unknown must *look* unknown.
- **Three regulators share the acronym "CMA"** — Lebanon, Saudi Arabia, and the UAE's (renamed from
  SCA on 2026-01-01). Confusing them in front of a client would be badly damaging.
- **The UAE has four non-overlapping regulators**: SCA/CMA onshore, DFSA (DIFC), FSRA (ADGM), CBUAE.
- **Licence registers beat tender boards** as a lead source. A newly licensed firm needs a system
  and has no incumbent.
- **Most RFPs in these markets are invitation-only** and never published anywhere.
- **Andre is on Windows** — `python`, not `python3` — and prefers the Claude Code desktop app.

## What Andre owes us (see `memory/open-questions.md` — 19 open)
Highest value first:
1. **Which client names may we reference, and to whom.** Worth more than anything else for outreach.
2. **Which Lebanese banks are on the survivor track.** Unblocks 17 records.
3. **A LinkedIn Sales Navigator seat** — would turn 20 names into 20 reachable people.
4. Pricing guidance · off-limits firms · whether we control the OFS website (no inbound surface today).

## The rules that do not change
Agents **never** contact anyone — draft, queue, hand to Andre. Never invent a company, person,
contact detail, metric, date or tender. Ground every client-facing claim in `knowledge/`. The New
Gaia is roadmap (Jan 2027 demo · Jun 2027 alpha · Q4 2027 deploy). No internal references in client
material. Log every touch. A quiet day reported honestly is worth more than a padded one.
