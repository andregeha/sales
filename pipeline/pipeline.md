# Pipeline

> ⚠ **The CRM is the system of record.** The live numbers come from `crm/`, not from this file:
> ```bash
> python3 tools/crm.py stats
> python3 tools/crm.py list --status qualified,contacted,engaged,opportunity
> python3 tools/crm.py next
> ```
> This file holds the **narrative** — the stage model, the standards, and anything a table cannot say.

## Scope
**New business only.** Existing clients (Finance House, GIMD/Dassault, Bank Audi, BLOM, AGPM) are
**not pipeline** — see `accounts/README.md`. Putting them here would flatter the numbers and hide
the fact that the new-business engine is only just starting.

## Stage model
| Stage | What it means | Exit criterion |
|---|---|---|
| `new` | Sourced, not yet looked at | Someone has actually read it |
| `researching` | Being enriched and scored | Scored, with a route in identified |
| `qualified` | Fits the ICP, has a trigger, has a reachable person | Ready to contact |
| `contacted` | Outreach sent by Andre | A reply, or the sequence completes |
| `engaged` | They replied and a conversation is live | A real meeting happens |
| `opportunity` | A defined thing we could win, with a decision process | Proposal issued |
| `won` / `lost` / `disqualified` / `nurture` | Signed · declined · not a fit · watch for a trigger | — |

## Standards
1. **Next action is a person, a verb and a date.** "Follow up" is not a next action. A record
   without all three is **parked**, and says so.
2. **Stage is evidence-based.** It moves when the exit criterion is met, not when we feel good
   about a conversation.
3. **Value and probability come from Andre**, never from an agent. Unknown is written as unknown.
4. **Disqualify out loud, with the reason.** It is the cheapest thing in sales and the most skipped.
5. **Update in the same session as the event.** A pipeline reconstructed from memory a week later
   is fiction.

## Current state
**The new-business pipeline is empty — the engine was built on 2026-09-22 and has not yet run.**
First real leads arrive with the first daily run. This line should be replaced with a date and a
count the moment that is no longer true.
