# Durable facts

> Cross-cutting, non-obvious things a colleague or agent must know. Newest first.
> Format: **fact** — source, date, confidence.

## Workspace & tooling
- **Andre works on Windows.** The command is `python`, not `python3`, and paths use backslashes.
  Anything we write must work on Windows.
  ✅ **Python 3.13.0 and PyYAML 6.0.2 are installed** on the laptop and `crm.py` runs — the earlier
  note that Python was missing described a different machine. Two Pythons are on PATH (3.13 first,
  then 3.11); `python` resolves to 3.13.0.
  ⚠ **The Windows console is cp1252**, so a script printing accented or Arabic text will mangle it
  or crash. Set `PYTHONIOENCODING=utf-8` when running anything that prints non-ASCII, and write
  files with an explicit `encoding="utf-8"`. — verified 2026-09-22 on the laptop, high.
- **Andre prefers the Claude Code desktop app to the terminal.** Default to giving him the
  desktop-app route first and the terminal only as an alternative. — stated 2026-09-22, high.
- **The cloud daily schedule (`trig_01R44y3zto5gaxgBChoFxy1L`) was DISABLED 2026-09-22** when the
  laptop became primary — to avoid two sessions committing to the same branch. **Disabled, not
  deleted**, so it can be re-enabled if the cloud network policy is ever widened.
  ⚠ **Nothing is scheduled right now.** The daily run must be set up on the laptop to resume.
  — 2026-09-22, high.
- **Running on Andre's laptop is the approved workaround for the blocked cloud network.** The
  desktop app runs locally, so it has his internet and can reach regulator and tender sites.
  Runbook: `RUN-ON-LAPTOP.md`. — approved by Andre 2026-09-22.
- ✅ **RESOLVED 2026-09-22 — the laptop has full internet.** Verified by live fetch:
  `geco.amf-france.org`, `data.gouv.fr`, `cma.org.sa`, `tenders.etimad.sa`, `boamp.fr`,
  `ted.europa.eu`, `dfsa.ae`, `adgm.com` all return 200. The block described below was a property
  of the **cloud** environment only. ⚠ The fact below is kept because it explains why the first 57
  CRM records are search-sourced and thinner than register-sourced ones — **it no longer describes
  where we run.** — verified 2026-09-22 on the laptop, high.

- ⚠ **A 200 does not mean success.** Three sites in our territory return HTTP 200 with a body that
  is an error or a bot challenge: the Saudi CMA's SharePoint serves a styled error page for a wrong
  URL, and Etimad serves an F5 bot-detection challenge. Any connector or scraper we write must check
  the **content**, not the status code. — observed 2026-09-22, high.

- 🔴 **This session's environment blocks general web access.** The egress policy allows package
  registries (pypi, npm, crates) and Anthropic APIs only; every other host gets a **403 on CONNECT**
  from the proxy. Verified 2026-09-22: `pypi.org` → 200, `amf-france.org` → blocked,
  `en.wikipedia.org` → blocked, and the proxy logged denials for `etimad.sa`, `ppa.gov.lb`,
  `boamp.fr`, `ted.europa.eu`.
  **What still works:** `WebSearch` (it goes through the Anthropic API, not the proxy), so agents can
  search and read result snippets. **What does not:** `WebFetch` and `curl` against tender portals,
  regulator registers and company sites — so we cannot load a tender page, confirm a deadline, or
  read a register directly.
  **Impact:** the RFP radar and lead sourcing run on search snippets alone, which is materially
  weaker and cannot be trusted for deadlines. **Fix:** Andre widens the environment's network policy
  (see https://code.claude.com/docs/en/claude-code-on-the-web). Do **not** attempt to route around it.
  — verified 2026-09-22, high.

- **This repo (`andregeha/sales`) is the sales brain; `andregeha/ofs-marketing` is the
  marketing/deck-production workspace.** Sales consumes its product knowledge and commissions decks
  from it. — established 2026-09-22, high.
- **`ofs-marketing` is not permanently on disk.** It is cloned per session to `/home/user/ofs-marketing`
  via `add_repo` + `git clone`. Anything we must not lose gets copied into `knowledge/` here.
  — observed 2026-09-22, high.
- **PowerPoint duplicates the last word of every soft-wrapped line on PNG/PDF/print export.** The
  `.pptx` text itself is correct. Fix: hard-wrap with the `hb()` helper in the marketing repo's build
  scripts. The QA gates cannot catch it — a **visual render check is mandatory** before shipping.
  ⚠ Do not tell Andre "just open it in PowerPoint" — **PDF and print double too**.
  — `ofs-marketing/notes/ppt-wrap-doubling.md`, 2026-09-22, high.

## RFP radar — measured performance
- ✅ **Second run (2026-09-22, from the laptop) is the first trustworthy one.** TED and BOAMP were
  searched through their **real APIs** — 15 and 11 query variants respectively, English and French,
  date-filtered to 2025+. **The France result is a genuine, measured zero**, not "nothing indexable".
- 🔴 **But BOAMP, PLACE and TED are PUBLIC-procurement only** — *acheteurs publics* under the Code de
  la commande publique, and EU public procurement. ⚠ **Our buyers are private firms with no
  obligation to publish, so these portals can never see them.** Andre made this point 2026-09-22 and
  it is the correct frame: a zero there is a zero *of public-sector tenders*, which says almost
  nothing about our actual market. Even within the public sector, **sub-threshold buys need not be
  published** and a body can buy through an existing *accord-cadre* or UGAP with no new notice.
  **Consequence: the RFP radar is a minority channel and always will be. The main engine is the
  licence registers plus trigger-based outbound.** Run the radar because a missed public tender is
  unrecoverable and the alerts are free — but never let a clean radar report read as "quiet market".
  — Andre 2026-09-22, high.
- 🔴 **Saudi Arabia still has ZERO tender-search coverage.** Etimad serves its **own bot-detection
  challenge** (F5 TSPD / `APM_DO_NOT_TOUCH`) instead of content, to every endpoint and user agent.
  This is the site blocking automation, not a network policy. **We do not attempt to defeat bot
  protection** — it needs a human with a browser and ideally a registered supplier account.
  ⚠ Never report "no Saudi tenders" off this radar; we are not looking.
- 🟠 **Abu Dhabi ADGPG and Dubai eSupply are JS single-page apps** — a plain fetch sees no listing.
  Unreached, not checked. A headless browser would be needed.
- 🎯 **Free saved-search email alerts are confirmed on BOAMP and PLACE, and exist on TED.** This is
  a better mechanism than any scraper we could write and costs nothing. Andre (or whoever holds the
  France supplier identity) should set them up — see `knowledge/market/rfp-sources.md`.
- **Two false-positive classes, both expensive:** (1) French "portefeuille" usually means an
  IP/patent or **project** portfolio, not investment; (2) public pension funds (FRR, ERAFP, CNBF,
  CIPAV, FGDR, Carpimko, Ircantec…) tender **asset-manager mandates and advisory**, never software —
  we never bid, but **the winner of one is a buyer** and the award is a trigger.
- **Proof the category does appear on TED:** the Council of Europe Development Bank (Paris) ran a
  genuine "capital markets and loan operations management system" procurement (TED `288127-2025`) —
  but it closed 2025-06-06. KfW (Germany, deadline 2026-08-10) is real but outside our markets.

## Register connectors — built and measured
- ✅ **AMF France is live and is our best lead source.** The AMF publishes its register of licensed
  sociétés de gestion as a **daily-updated CSV on data.gouv.fr** (dataset `651427eaf6eab90fa3db2da3`).
  **666 live firms.** ⚠ The download URL is **timestamped and changes every day** — resolve it
  through the dataset API each run, never hardcode it.
  **Flow is ~2 new licences a month** (16 in 2026 to date) — a realistic, workable signal.
  The dataset also publishes **licence date, authorised activities, authorised instrument classes,
  and for many firms a website and switchboard number** — regulator-published contact routes, which
  is the one legitimate source of contact detail we have. — built and run 2026-09-22, high.
- ✅ **The Saudi CMA register IS readable — via its web page, not its API.** ⚠ I got this wrong
  first time and the correction is the useful part: *the API being dead does not mean the register
  is unreachable.* The **Financial Market Institutions** page (still on the old `AuthorisedPersons`
  URL) **server-renders its entries into the HTML** — no JavaScript needed. **242 licensed firms.**
  ⚠ It ships only the **36 most-recently-updated** of them; the rest paginate in via JavaScript
  ("Total 41 Pages"). That is a **partial source**: it catches every new name, because the list is
  ordered newest-first, but it **cannot detect a firm leaving** the register.
  Its activity legend is printed on the page: **Arranging (Arr) · Advising (Adv) · Custody (C) ·
  Dealing (D) · Managing Investments and Operating Funds (MIOF) · Managing Investments (MI)** — and
  the cards mix codes with full names. **MI/MIOF is what makes a firm ours.**
  ⚠ The card's date is the CMA's **"last update" for the entry** — the licence date for a new firm,
  but possibly an amendment for an existing one. Do not quote it as a licence date unchecked.
  — built and run 2026-09-22, high.
- 🟠 **The Saudi CMA Open Data API is unreachable from Europe**, though it would be the better
  source if it worked (it would give all 242 in one call and allow disappearance detection).
  `opendataapi.cma.gov.sa` serves its swagger, but every `/api/...` call **times out at the TCP
  layer after ~21s** with backoff — a geo-restriction on the backend, not a rate limit.
  **Try it first from the Riyadh office or any Saudi network.**
  Its downloadable open-data files were checked and are **aggregate statistics**, not a register of
  named firms — they cannot substitute. — 2026-09-22, high.
- ⚠ **The Saudi CMA domain moved: `cma.org.sa` → `cma.gov.sa`**, and its term for a licensed firm is
  **"Authorised Persons" / "Financial Market Institutions"**, not "CMI", in its own navigation.
  — 2026-09-22, high.
- **Design rule that must not be softened:** a connector that cannot read its source **raises and
  writes nothing**; zero entries from a live register is treated as a **bug, not a quiet day**; and a
  collapsed row count is refused as a truncated download rather than diffed as a mass delisting.
  A radar that fails silently is worse than no radar, because it is trusted.

## Markets & regulators
- ⚠ **Three different regulators share the acronym "CMA"** — Lebanon's Capital Markets Authority
  (`cma.gov.lb`), Saudi Arabia's Capital Market Authority (`cma.org.sa`), and now the UAE's.
  Always qualify which one. Confusing them in front of a client would be badly damaging.
  — research 2026-09-22, medium-high (search-verified, not page-verified).
- **The UAE's SCA was renamed to the "Capital Market Authority" effective 1 January 2026**
  (Federal Laws No. 32 and 33 of 2025; `uaecma.gov.ae`). This is both a naming trap and a genuine
  **regulatory-change trigger** worth watching — renames of this kind usually come with new or
  restated obligations. — research 2026-09-22, medium (search-verified only, confirm before citing).
- **Lebanon is relationship-driven, not tender-driven** for this software category. No public tender
  board could be confirmed for Banque du Liban or Lebanon's CMA, and the status of the Public
  Procurement Authority portal is unconfirmed. Work Lebanon through relationships, not portals.
  — research 2026-09-22, medium.
- **The best public lead sources are licence registers, not tender boards**: the AMF's GECO register
  of licensed French asset managers, Saudi CMA's licensed Capital Market Institutions and funds, and
  the UAE regulator's licensed-companies open data. — research 2026-09-22, medium.
- **Most PMS/OMS/fund-administration RFPs in all four markets are invitation-only and never
  published.** The radar catches the public minority — mostly government, sovereign-fund,
  central-bank and regulator procurement. Say this plainly rather than implying coverage is
  complete. — research 2026-09-22, high.

## Live buying triggers (as at 2026-09-22)
> ⚠ All of these are **search-verified only** — the environment blocked page loads. Confirm before
> citing any of them to a prospect. They are strong enough to *prioritise* work, not to quote.

- 🔥 **Lebanon — the strongest trigger in our whole territory.** Banking secrecy was lifted
  (2025-04-24) and a **bank-resolution law (Law 23/2025, July 2025)** forces every Lebanese bank onto
  a viability, recapitalisation or liquidation track; a further "financial gap" law was drafted in
  Dec 2025. Combined with our **ready-made CMA/BDL regulatory pack**, a Beirut office and existing
  bank clients, this is unusually well-matched.
  ⚠ **But qualification matters more than need here**: a bank on the resolution track buys nothing.
  Establish which track a bank is on *before* spending effort. Also: the widely-quoted "61 Lebanese
  banks" figure is from 2022 and is stale — do not use it.
- 🔥 **Saudi Arabia — the fastest-growing enumerable population.** Licensed Capital Market
  Institutions went from **188 (Feb 2025) to 215 (end-2025)** — 32 new licences in a year. Small,
  fully enumerable, and every new licence is a firm that needs systems and has no incumbent.
  Local-content rules (a 30% minimum on government-linked procurement) are real friction — and our
  **Riyadh office is the answer to it**.
- **UAE — CBUAE Decree-Law 6/2025** carried a compliance deadline of **2026-09-16**, six days ago.
  Worth investigating as a live driver.
- **France — DORA has applied since 2025-01-17**, with the AMF requiring documented digital-resilience
  arrangements. An ongoing, system-touching obligation. The French market is mature and slowly
  consolidating (roughly 700 → 697 sociétés de gestion, 2023 → 2024) — steady, not fast.
- **Vendor consolidation:** Temenos sold Multifonds to Montagu (Feb 2025, ~$400m). Vendor ownership
  changes unsettle installed bases and are worth watching as displacement opportunities.

## Market structure notes
- **The UAE has four separate regulators whose registers do not overlap** — SCA/CMA (onshore),
  **DFSA (DIFC)**, **FSRA (ADGM)** and **CBUAE**. Never conflate them; which one licenses a firm
  determines how we approach it. Published firm counts for DIFC and ADGM **conflict between sources**
  — do not average them, and do not quote a number we have not verified.
- **Family offices are invisible by design.** DIFC exempts single-family offices above a $50m
  net-asset threshold, ADGM above $10m — so only **multi-family offices** appear on registers.
  No Gulf family-office association with a public directory was found.
  **AFFO** (France, est. 2001, 100+ member structures, publishes an annual barometer with EY) is the
  one genuinely usable family-office association across all four markets.
- **Where the density is** — the researched recommendation: work **Saudi CMIs hardest**, then
  **Lebanese banks** (with hard survivor/resolution qualification), then **UAE DIFC family offices
  and MFOs**, then **France** as a steady lower-intensity lane. Deprioritise Lebanese BDL "financial
  institutions" and Saudi consumer-finance companies — adjacent, not our segments.

## Product
- ⚠ **The Web Customer Portal is a SEPARATE PRODUCT from Gaia** — not a module, not a layer of it.
  It runs on the **same database** as Gaia, which is why the two stay in step with no integration
  project (and that is the selling point). Positioned and sold in its own right.
  I had it wrong and wrote it into the knowledge base as a Gaia module; corrected across
  `CLAUDE.md`, `knowledge/product/gaia-current.md` and `knowledge/product/web-portal.md`.
  — corrected by Andre 2026-09-22, high.
- **The New Gaia runs on the unchanged database.** This is the single most valuable sentence we have
  for an existing client: no data migration, additive changes only, legacy rights model reused,
  desktop and web coexist during migration. — `knowledge/product/gaia-new.md`, 2026-09-22, high.
- **The Gaia Web Portal is live today** — not part of the 2027 roadmap. It is the proof asset that
  defuses "your product is a desktop app". — verified live in the test portal, 2026-09-22, high.
- **The constraint/prudential rule library is maintained by OFS**, including a ready-made **CMA/BDL
  (Lebanon)** regulatory pack. Strong differentiator for regulated Lebanese houses.
  — `knowledge/product/gaia-current.md`, 2026-09-22, high.
- **Client-facing New Gaia timeline: Ready now · Jan 2027 demo · Jun 2027 alpha · Q4 2027 deploy.**
  Set by Andre. Do not vary it. — 2026-09-22, high.

## Commercial guardrails
- **Never quote a price or discount.** Modular pricing exists ("pay only for what you need") but every
  number goes through Andre. — standing rule, high.
- **Read-only on any client system.** Gaia can place real orders, post accounting and send SMS/email.
  — standing rule, high.
