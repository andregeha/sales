---
name: intake
description: Turn something Andre heard, read or was sent into durable CRM state — a hire, a fund launch, a restructuring, a name at a conference, a forwarded email, a LinkedIn profile, a URL. Resolves it against the CRM, verifies what can be verified, files it, and says plainly what it could not confirm. Use whenever a fact arrives in conversation rather than from a connector.
---

# Intake

Connectors sweep sources on a schedule. **Intake is the other half: it captures what a human saw.**

Andre hears things — a CIO hire, a fund launch, a bank restructuring, a name at a conference, a
throwaway line in a meeting. Right now that lands in a chat message and dies there, which breaks
this workspace's first rule: *nothing important lives only in a conversation.*

Intake takes free text and turns it into exactly one of four outcomes, and says which:

| Outcome | When |
|---|---|
| **Activity on an existing record** | The firm is already in the CRM. This is the common case. |
| **A new company record** | The firm is real, in our territory and segments, and verifiable. |
| **A candidate** | Might be ours, but cannot be verified right now. `crm/candidates/`. |
| **A fact or an open question** | Market intelligence with no single firm attached, or a claim we could not confirm. |

## The rules that make this safe

1. **Resolve before you create.** Always run `crm.py find` first. The real risk here is not missing
   a firm — it is creating a *second* record for one we already hold, which splits its history in
   two so that the activity, the contact and the trigger end up on different copies and nobody
   notices, because both records look fine.
2. **Never invent the parts you cannot check.** No guessed email patterns, no inferred job titles,
   no assumed AUM, no date you were not told. Unknown is `null`. This is the whole reason intake is
   a skill and not a paste.
3. **Separate what Andre said from what you verified.** An activity note records *both*, labelled.
   "Andre heard X at a conference" and "the AMF register confirms X" are different kinds of fact and
   must never be merged into one confident sentence.
4. **A trigger needs a source.** `status: qualified` requires a real, datable trigger with a URL a
   human can open. Hearsay is worth recording — it is not worth qualifying on.
5. **Re-running is safe.** Intake of the same text twice must not produce two activities. Check the
   record's recent activities before appending.
6. **Nothing is sent.** Intake never contacts anyone. If the intake implies outreach, draft it and
   put it in the queue for Andre.

## The steps

**1 · Read what you were given, and say what you think it is.**
Name the firm(s), the person(s), the event and the date, as *claims*. If the text is ambiguous about
which firm is meant, say so now rather than picking.

**2 · Resolve every named firm.**
```bash
python tools/crm.py find "<the name as Andre wrote it>"
```
It ranks; it does not decide. Read the candidates and choose, or conclude it is new. If two records
look like the same firm, say so — a duplicate already in the CRM is worth reporting.

**3 · Verify what can be verified.**
Use the register connectors' own sources, the firm's website, or the regulator. Delegate to
`ofs-researcher` for anything that needs real research. Verify:
- that the firm exists and is in our territory and segments;
- the person's role, if a person is named;
- the event, if it is the kind of thing that gets published.

Record what you checked **and what you could not check**. "Not found on the AMF register" is a
result worth writing down; it is not proof of absence.

**4 · File it.**

Existing firm:
```bash
python tools/crm.py log <slug> --type <research|call|meeting|demo|linkedin|rfp|note> --summary "..." --date YYYY-MM-DD
```
(`email_drafted` and `email_sent` also exist, but only Andre sends — see the outreach rules.)
New person on an existing firm — `--title` is the job title, `--role` is their role in *our* deal
(`economic_buyer`, `champion`, `technical`, `compliance`, `blocker`, `unknown`). Omit `--email`
entirely rather than guessing one:
```bash
python tools/crm.py contact <slug> --name "..." --title "..." --role unknown
```
New firm — only when verified. `--source-channel` is where it came from (e.g. `conference`,
`referral`, `register`), `--source-detail` the specific evidence, `--source-date` when:
```bash
python tools/crm.py add --name "..." --country "..." --segment "..." \
  --source-channel "..." --source-detail "..." --source-date YYYY-MM-DD
```
Cannot verify → write a candidate to `crm/candidates/` with its evidence URL and why, via
`tools/candidates.py`. Unattached market intelligence → `memory/facts.md`. Unresolved claim →
`memory/open-questions.md`.

**5 · Update the trigger, if there is one.**
A hire, a launch, a licence, a restructuring, a vendor change — that is a reason to write. Set it on
the record with its source, and only then consider `qualified`.

**6 · Validate and report.**
```bash
python tools/crm.py validate
```
Then tell Andre, in this order: what you filed and where · what you verified · **what you could not
confirm** · anything that now warrants outreach. Keep it short — he gave you one sentence; do not
return three paragraphs unless the intake genuinely produced them.

## Worked example

> Andre: *"Met someone from Jadwa in Riyadh, they said they're launching a new fund vehicle and are
> unhappy with their current PMS."*

- `crm.py find "Jadwa"` → `jadwa-investment-difc-limited`, 0.90. One match, take it.
- Verify the fund launch: check the CMA register and the firm's own site. **If you cannot confirm
  it, it stays hearsay** — log it as such, do not put "launching a new fund" in the record as fact.
- `crm.py log jadwa-investment-difc-limited --type meeting --summary "Andre met [person] in Riyadh.
  CLAIMED (unverified): launching a new fund vehicle; dissatisfied with current PMS. Not confirmed
  on the CMA register as of <date>."`
- "Unhappy with their current PMS" is the most valuable sentence in the message and is **pure
  hearsay** — an open question, not a trigger: *"What PMS does Jadwa run today, and what is the
  dissatisfaction?"*
- Report to Andre: filed; fund launch unconfirmed; and the one thing worth asking on the next call.

Note what did *not* happen: no email was drafted to a person whose name and address we do not have,
and the record did not become `qualified` on the strength of a corridor conversation.
