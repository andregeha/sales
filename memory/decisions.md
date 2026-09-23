# Decision log

> Dated decisions and *why*. Including decisions not to do something. Newest first.

## 2026-09-22 (laptop) — How the register connectors behave, and what we will not do

- **A connector that cannot read its source raises and writes nothing.** Zero entries from a live
  register is treated as a bug, not news. *Why:* an empty diff and a dead source look identical in a
  morning brief, and the second one is a lie that gets trusted. This is the single most important
  property of the design and must not be softened for convenience.
- **A collapsed row count is refused as a truncated download, not diffed as a mass delisting** —
  but only when the drop is both proportionally large and bigger than ordinary churn, so a small
  register losing one name still works.
- **A baseline run does not dump the register's back catalogue into the CRM.** Only firms licensed
  within 180 days become records; the rest go into the snapshot so the next diff is still correct.
  *Why:* 666 French firms would bury the ten that matter, and most of the back catalogue has an
  incumbent anyway.
- **Fit points are awarded only where the register itself states the fact.** The AMF publishes each
  firm's authorised activities and instrument classes, so "multi-asset" and "manages third-party
  money" are scored from quoted evidence. Where a register is silent, the points are zero rather
  than assumed. *Why:* a score inflated by an invented fact is worse than a low score.
- **🔴 We do not attempt to defeat bot protection, WAFs or geo-restrictions.** Etimad and the Saudi
  CMA both block automated access. The answer is to report the gap honestly, and to route around it
  with a human or a Saudi network — never to disguise what we are. *Why:* these are public
  regulators in markets where our reputation is the asset, and we identify ourselves honestly in
  every request. A blocked source is a known unknown; a spoofed one is a liability.
- **Regulator-published contact details are usable; guessed ones never are.** The AMF publishes
  websites and switchboard numbers, so we store them and cite the register. We still do not
  construct an address from a pattern. *Why:* the rule was never "no contact details" — it was
  "nothing invented".
- **Deliberately NOT built:** a Lebanon connector (no usable public register exists — Lebanon stays
  relationship-driven), and any headless-browser scraper for the JS tender portals. The latter is a
  real gap, but **free saved-search email alerts on BOAMP, PLACE and TED are a better mechanism than
  scraping** and should be set up first.

## 2026-09-22 — The laptop is the primary environment
- **This workspace runs on Andre's laptop**, not in the cloud. *Why:* the cloud environment's
  network policy blocks every regulator register and tender portal. That is not a detail — register
  diffing and real RFP scanning are the highest-value automation in the whole design, and both are
  impossible there. Search-only sourcing still produced 57 companies, so the cloud is degraded
  rather than useless, but the ceiling is low.
- **Git is the spine, deliberately.** Every session works the same repo and branch, so the choice of
  machine is reversible and costs nothing. If the cloud network policy is ever widened, moving back
  (or running both) is a non-event.
- **The trade-off, stated honestly:** a laptop only runs when it is on. The unattended daily run is
  the thing we give up, and that is the one real cost of this decision. Worth it while the cloud
  cannot see the sources that matter.

## 2026-09-22 — Mission set: a continuous new-business engine
Andre's answers to the setup questions, and what follows from them.

- **Scope is NEW BUSINESS ONLY.** Existing clients (Finance House, GIMD/Dassault, Bank Audi, BLOM,
  AGPM) move to `accounts/` as **context and proof points, not pipeline**.
  *Why:* mixing them in would flatter the numbers and hide that the engine is starting from zero.
- **The mandate is broader than deliverables — it is a machine.** Find clients, find every RFP in our
  markets, build an automated lead pipeline, run inbound and outbound outreach, log everything,
  daily and continuously.
- **Territory: UAE · Saudi Arabia · Lebanon · France.** Segments: **family offices & MFOs · private
  and investment banks · asset & fund managers.**
- **This repo is the CRM.** No external system. Git-friendly YAML per company, a CLI, and a generated
  HTML brief. *Why:* Andre chose it, it is diff-able and auditable, it needs no licence or
  integration, and agents can read and write it natively.
- **Agents draft freely; Andre approves and sends.** No agent contacts anyone in any medium.
  *Why:* it is the right control for a small market where one bad first touch is unrecoverable —
  and Andre's name is on every message.
- **Sending must be near-frictionless for Andre** — pre-filled `mailto:` links, copy-ready bodies,
  direct profile URLs. *Why:* he explicitly asked for fast, automated ways to send; an approval
  queue that requires retyping will not get used.
- **The engine runs daily on a schedule**, not on demand. *Why:* RFP deadlines do not wait for
  someone to remember to look.
- **Deliberately NOT doing:** automated sending, scraped contact lists, or guessed email patterns.
  *Why:* a bounced or unwanted message costs more than the lead is worth, and in these markets
  reputation is the asset.

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

## Sourcing and data integrity (2026-09-23)
- **Noisy sources propose candidates; they never create records.** SIRENE, GLEIF and anything keyed
  on self-declared industry codes land in `crm/candidates/`, not the CRM. *Why:* NAF `64.20Z` is
  every holding company in France. Auto-creating from it would refill the CRM with noise and destroy
  the only property that makes a record here worth trusting — that it means something.
- **A candidate's likelihood score is deliberately NOT the ICP score.** Separate vocabulary in the
  UI ("likely ours" vs "work now"), separate model, separate docstring warning. *Why:* they answer
  different questions — one ranks a researched firm and says what to do; the other ranks an
  unreviewed guess. Sharing a badge would let a guess wear a researched record's authority.
- **We filter with our own classifier, not the source's keyword search.** Measured on 2026-09-23:
  UNGM's own `Description` filter returned zero notices across all four markets while the unfiltered
  country lists held 63. *Why:* a source-side filter is a black box — when it matches nothing we
  cannot tell "nothing is there" from "our words were wrong", and that failure looks exactly like
  good news. Our classifier prints a reason for every rejection.
- **Every source reports its health into the same run record**, registers and RFP sources alike
  (`AUX_MODULES` in `run_all.py`). *Why:* a dead source visible only in someone's terminal is a dead
  source nobody knows about. EBRD's failure now renders on the website beside the registers.
- **A source never once read successfully reports as `failing`, not `stale`.** *Why:* "stale" invites
  waiting for a recovery that cannot happen; "failing" invites fixing.
- **Generated data is not a Tailwind source.** `site/public/data/` is excluded in `tokens.css`.
  *Why:* it was being scanned, so the built CSS changed whenever a company or candidate did —
  breaking the determinism contract silently, in output nobody inspects.

## UAE sourcing (2026-09-23)
- **We will never build a DMCC business-directory connector**, however easy it becomes technically.
  Verified against DMCC's own published terms, read directly: the directory is "published with the
  express consent of our member companies" and it is "expressly forbidden to copy, download, store,
  reproduce … or otherwise deal with the DMCC member directory for email or telephone marketing",
  nor to "reproduce the directory for use on your own website, database or products". *Why:* that
  bars both of the things this repo exists to do — ingesting firms into a CRM and contacting them.
  This is a permissions decision, not an engineering one, so no amount of technical ease reopens it.
- **Representative offices are candidates, never records.** A DIFC representative office cannot
  conduct financial business; it is marketing and liaison, and the parent's platform decision is
  made abroad. *Why:* 195 of them would add T. Rowe Price, Blackstone and Euroclear to our pipeline
  and convert at approximately zero, which would make every coverage number we report less honest.
- **A family office in the UAE is not findable from any register, and we stop looking for one.**
  DIFC states family arrangements sit on "a private register … on an independent server"; the
  Family Wealth Centre publishes no directory; the DFSA's Single Family Office category is wholly
  withdrawn; EFOA is approval-only with a no-solicitation policy. *Why:* this cell is not a sourcing
  failure to be fixed with a better scraper — it is a market that deliberately does not publish, and
  the realistic routes are events, referrals and engagement.
