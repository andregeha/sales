---
name: memory-keeper
description: Capture what was learned and decided into the workspace's durable memory, and audit memory for staleness or contradiction. Use at the end of any working session, after a meeting or research pass, or when knowledge has piled up in conversation but not on disk.
---

# Memory keeping

Knowledge that exists only in a conversation is knowledge we are about to lose.

## The capture pass
1. **New durable facts** → `memory/facts.md`. Each with its **source, date and confidence**.
   Account-specific facts go to `accounts/<slug>/` instead.
2. **Decisions** → `memory/decisions.md`. What we decided, **why**, and what we rejected.
   Include decisions *not* to do something — those are the ones that get re-litigated.
3. **Unknowns and approval-needed items** → `memory/open-questions.md`, with a status
   (🔴 blocking · 🟠 needed soon · ⚪ nice to have) and who can answer.
4. **Resolved questions** → answer them in place with a date. Do not delete silently.
5. **Session log** → `memory/changelog.md`.
6. **Pipeline or account changes** → `pipeline/pipeline.md`, `accounts/<slug>/engagement.md`.

## The audit pass
- Anything dated more than about a month back that reads as current → mark **⚠ needs refresh**.
- Contradictions between `memory/` and `knowledge/` → fix `knowledge/`, log the change.
- Unsourced claims → find the source or downgrade them to open questions.
- Orphaned open questions nobody owns → assign an owner or close them honestly.

## Rules
- **Source and date, always.** Without them it is a rumour.
- **Never overwrite history** — supersede with a date and say what changed.
- **Never invent** to fill a gap. "Unknown" and "needs refresh" are always available.
- Prefer **fewer, sharper entries** over an unreadable log. Memory nobody reads is not memory.
