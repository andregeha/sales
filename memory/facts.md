# Durable facts

> Cross-cutting, non-obvious things a colleague or agent must know. Newest first.
> Format: **fact** — source, date, confidence.

## Workspace & tooling
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
