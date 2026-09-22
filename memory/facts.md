# Durable facts

> Cross-cutting, non-obvious things a colleague or agent must know. Newest first.
> Format: **fact** — source, date, confidence.

## Workspace & tooling
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

## Product
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
