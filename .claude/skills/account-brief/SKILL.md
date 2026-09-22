---
name: account-brief
description: Produce or refresh a complete brief on an account or prospect — who they are, what they need, our angle, the decision map, and the next action. Use before a meeting, when picking up an account, or when onboarding someone to it.
---

# Account brief

## 1. Load what we already know
`accounts/<slug>/profile.md` and `engagement.md` · `memory/facts.md` · `memory/open-questions.md` ·
`pipeline/pipeline.md`. If there is no folder, create one from `accounts/_template/`.

## 2. Fill the gaps
Delegate to **`ofs-researcher`** for anything about the entity, its people or its market.
Delegate to **`ofs-solution-engineer`** for fit against their stated requirements.

## 3. Write the brief
1. **Snapshot** — entity, segment, country, regulator, size, client base, mandate mix.
2. **Relationship** — client or prospect; if a client, which version and modules, and since when.
   ⚠ Keep their installed version strictly separate from what we sell today.
3. **What they care about** — in their words, with the source.
4. **The decision map** — economic buyer, champion, technical evaluator, compliance, blocker.
   Name explicitly who we have **not** met.
5. **Our angle** — which modules lead, which value proposition, which proof asset, what to avoid.
6. **State of play** — stage, history, what is blocked on whom.
7. **Next action** — one person, one verb, one date.
8. **Unknowns** — what we could not establish, and who can answer it.

## 4. Persist
Update the account files and `pipeline/pipeline.md`. Log unknowns in `memory/open-questions.md`.

## Rules
- **Never guess an unknown.** Write "unknown" and route the question to Andre.
- Watch for ambiguous entity names — GIMD is the Dassault *family holding*, AGPM is unconfirmed.
- Dated status older than about a month is marked **⚠ needs refresh**, not presented as current.
