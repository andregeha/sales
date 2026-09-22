# The daily run

> The heartbeat of this workspace. Runs every working day, scheduled. Roughly 30–45 minutes of
> agent work, ending in **one brief Andre can action in ten minutes**.
> If a step finds nothing, say so — a quiet day is a legitimate result, and inventing activity to
> look busy is the one failure mode that would make this whole thing worthless.

## 0. Load
```bash
python3 tools/crm.py stats
python3 tools/crm.py next
python3 tools/crm.py rfp list --status spotted,assessing,bidding
```
Read `memory/open-questions.md` for anything blocking, and `memory/changelog.md` for where
yesterday ended.

## 1. RFP radar — first, because deadlines are unforgiving
Work `knowledge/market/rfp-sources.md`. Check the daily-cadence sources for UAE, KSA, Lebanon and
France. For anything plausibly in scope:
- Record it: `python3 tools/crm.py rfp add ...` with the **deadline**, the issuer and the source URL.
- Assess fit with **`ofs-solution-engineer`** — can Gaia genuinely do this, honestly?
- **A missed deadline is the worst outcome this workspace can produce.** Anything closing within
  14 days goes to the top of Andre's brief, every single day, until it is decided.
- Deciding **not** to bid is a fine outcome — but it is a *decision*, recorded with its reason,
  never a drift into silence.

## 2. Trigger scan — the reason-to-write engine
Watch for the buying triggers in `knowledge/market/icp.md`: new licences granted by SCA, DFSA,
FSRA, CMA Saudi, CMA Lebanon or AMF · fund launches · senior operations, COO, CIO or compliance
hires · spin-outs and acquisitions · incumbent vendors being acquired or sunset · regulatory
changes creating reporting pressure.
Every trigger either **creates a new lead** or **wakes a `nurture` record** — and it becomes the
first line of the outreach, because it is the honest answer to "why are you writing to me now?"

## 3. Source new leads
Work one market × segment combination per day rather than skimming all of them — depth beats
breadth, and the registers do not change fast enough to re-scan daily.
Use the regulator registers and directories in `knowledge/market/landscape.md`. For each candidate:
`crm.py add`, score against `knowledge/market/icp.md`, and **write the reasoning, not just the
number**. Delegate enrichment to **`ofs-researcher`**.

## 4. Research the top of the queue
Take the highest-scoring `new` and `researching` records. Establish: what they run today, who
decides, the route in, and the reason to write now. Anything you cannot establish is written as
unknown — never filled in with a plausible guess.

## 5. Draft outreach
For records that are qualified **and** have a real trigger, delegate to **`ofs-writer`** using
`playbooks/outreach.md`. Draft to the medium that fits the person — email, LinkedIn, or whatever
else makes sense for that market and role. Log each draft with `crm.py log`.

## 6. Move the pipeline
Anything stalled: chase it, change the approach, or park it honestly. A record with no next action
is parked, and says so. Update statuses to reflect reality, not hope.

## 7. Produce the brief
```bash
python3 tools/crm_report.py
```
Ordered by what costs us most if ignored: **RFP deadlines → outreach awaiting approval → the work
queue → new leads → pipeline summary**. Every action one click: pre-filled `mailto:`, copy-ready
body, direct profile link.

## 8. Persist and close
Update `memory/changelog.md`, log new facts and open questions, run `python3 tools/crm.py validate`
(**must exit 0**), then commit and push.

## The standard the run is held to
- **Never invent a lead, a contact, a trigger or an RFP.** Empty is a result; fabricated is a fraud.
- **Never send anything.** Draft, queue, hand over.
- **Never let a deadline pass unflagged.**
- **Log every touch**, so nobody gets contacted twice by accident.
- **Report honestly** — "three sources unreachable, two leads added, no new tenders" is a good day's
  report. A padded one is not.
