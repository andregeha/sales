---
name: daily-run
description: Run the daily new-business cycle — RFP radar, trigger scan, lead sourcing, research, outreach drafting, pipeline movement, and Andre's brief. Use every working day, or whenever asked to "do the daily run" or "check for new leads and RFPs".
---

# Daily run

Follow `playbooks/daily-run.md` in full. In short:

1. **Load** — `crm.py stats`, `crm.py next`, `crm.py rfp list`, `memory/open-questions.md`.
2. **RFP radar first** — deadlines are unforgiving. Anything closing within 14 days goes to the top
   of the brief every day until it is decided. Record before assessing.
3. **Trigger scan** — new licences, fund launches, senior hires, spin-outs, regulatory change.
4. **Source leads** — one market × segment, worked properly. Delegate to `ofs-lead-sourcer`.
5. **Research** the top of the queue. Delegate to `ofs-researcher`.
6. **Draft outreach** for qualified records that have a real trigger. Delegate to `ofs-writer`.
7. **Move the pipeline** — chase, re-angle, or park honestly.
8. **Produce the brief** — `python3 tools/crm_report.py`.
9. **Persist** — changelog, facts, open questions, `crm.py validate` (must exit 0), commit and push.

## The standard
- **Never invent a lead, a contact, a trigger or an RFP.** A quiet day is a legitimate result;
  a padded one destroys the value of every other day's report.
- **Never send anything.** Draft, queue, hand to Andre.
- **Never let a deadline pass unflagged.**
- Report what you actually did, including what failed or was unreachable.
