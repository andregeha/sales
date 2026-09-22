# Decision log

> Dated decisions and *why*. Including decisions not to do something. Newest first.

## 2026-09-22 — Workspace founded
- **The sales workspace is a separate repo from `ofs-marketing`.** Sales owns pipeline, accounts,
  qualification, positioning and commercial strategy; marketing owns brand, deck production and QA.
  *Why:* different cadence, different guardrails, and sales knowledge should not be lost inside a
  deck-build repo.
- **`knowledge/` here is a self-sufficient distillation, not a pointer.** The marketing repo is cloned
  per session and cannot be assumed present. *Why:* a sales workspace that breaks when another repo
  is missing is not a workspace.
- **The marketing repo's golden rules are inherited verbatim**: never mix information sets, no
  internal-only references in client material, ground every claim, roadmap labelled as roadmap.
  *Why:* they are correct, already battle-tested, and consistency across the two repos matters.
- **Deck production stays in `ofs-marketing`.** Sales specifies and reviews; marketing builds.
  *Why:* the brand kit, build scripts and QA gates live there and should not be forked.
