# Decision log

> Dated decisions and *why*. Including decisions not to do something. Newest first.

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
