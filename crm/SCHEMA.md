# CRM schema

> This repo **is** the CRM — no external system. One YAML file per company under
> `crm/companies/<slug>.yaml`, one per tender under `crm/rfps/<slug>.yaml`. Git-friendly,
> diff-able, hand-editable. Read/write it with `tools/crm.py`; never hand-roll a second format.

## Why this shape
- **One file per company** so a human can open, read and edit a single record without a database,
  and `git diff`/`git log` give a free audit trail.
- **Contacts are embedded**, not a separate table — these are small B2B accounts (a handful of
  people each), not consumer lists. A join table would be pure overhead.
- **Activities are append-only.** Never edit or delete a past entry — if something was wrong, add a
  new entry that corrects it. The log is the evidence trail for "how did we get here".
- **Nothing is invented.** A missing email, phone, AUM or employee count is `null`. Never a guess,
  never a placeholder that looks real.
- **`next_action` is all-or-nothing.** Per the repo rule ("one person, one verb, one date"), the
  field is either a complete `{who, what, due}` object or `null`. A half-filled next action is
  worse than none — it looks actionable but isn't.

## Enumerations (used by `tools/crm.py validate`)

| Field | Allowed values |
|---|---|
| `segment` | `family_office`, `mfo`, `bank`, `asset_manager`, `fund_manager`, `broker`, `insurer`, `custodian` |
| `status` (company) | `new`, `researching`, `qualified`, `contacted`, `engaged`, `opportunity`, `won`, `lost`, `disqualified`, `nurture` |
| `stage` (company) | `identified`, `engaged`, `qualified`, `solution_agreed`, `proposed`, `negotiating`, `won`, `lost`, `parked` — mirrors `pipeline/pipeline.md`'s stage model |
| `contact.role` | `economic_buyer`, `champion`, `technical`, `compliance`, `blocker`, `unknown` |
| `contact.language` | `en`, `fr`, `ar` |
| `activity.type` | `research`, `email_drafted`, `email_sent`, `linkedin`, `call`, `meeting`, `demo`, `rfp`, `note` |
| `rfp.status` | `spotted`, `assessing`, `bidding`, `submitted`, `won`, `lost`, `skipped` |
| `rfp.decision.outcome` | `bid`, `no_bid`, `pending` |

Dates are always `YYYY-MM-DD`. Countries and cities are free text (this is a handful of markets —
UAE, KSA, Lebanon, France — not a geo database). `owner` is a person's name; today that is always
**Andre Geha**, but the field exists because that will not always be true.

## Company record — `crm/companies/<slug>.yaml`

Full worked example (this exact file ships as `crm/companies/EXAMPLE-oasis-family-office.yaml` so
the tooling has something real to validate against):

```yaml
slug: EXAMPLE-oasis-family-office
name: Oasis Family Office
legal_name: Oasis Family Office Ltd
country: UAE
city: Dubai
segment: family_office
regulator: DFSA
website: https://example.invalid/oasis-fo
linkedin: https://www.linkedin.com/company/example-oasis-fo
size:
  aum: null
  employees: null
  portfolios: null
description: >
  SCHEMA EXAMPLE — NOT A REAL LEAD. A fictional single-family office used to demonstrate and
  validate the CRM schema and tooling. Do not treat any field on this record as real data.
source:
  channel: web_research
  detail: "Fabricated for schema demonstration — see disqualified_reason."
  date: 2026-09-22
status: disqualified
stage: parked
owner: Andre Geha
tags:
  - schema-example
  - do-not-contact
created: 2026-09-22
updated: 2026-09-22

contacts:
  - name: Fictional Person
    title: Chief Investment Officer
    role: economic_buyer
    email: null
    phone: null
    linkedin: null
    language: en
    notes: "SCHEMA EXAMPLE — fictional contact, not a real person. Never invent contact details."
    source: "Fabricated for schema demonstration"

fit:
  score: 0
  reasoning: "Not a real company — no ICP scoring applies."
  disqualified_reason: "schema example, not a real lead"

activities:
  - date: 2026-09-22
    type: note
    summary: "Record created to demonstrate and validate crm.py and crm_report.py. Never edit past activity entries — append a new one instead."
    link: null

next_action: null
```

### Field notes
- `size.aum` / `size.employees` / `size.portfolios` — all optional and independently nullable.
  Record AUM in a plain string with currency when known (e.g. `"USD 400m"`), since precision and
  currency vary by source; leave `null` rather than guess.
- `fit.score` — 0–100 ICP score, `fit.reasoning` is required whenever `score` is not `null`.
  `fit.disqualified_reason` is required (non-null) when `status: disqualified`, and should be
  `null` otherwise.
- `activities` — newest-last (chronological append). Each entry: `date`, `type`, `summary`, and an
  optional `link` to an artifact in this repo (e.g. `accounts/<slug>/engagement.md`, a drafted
  email under an account folder) — never a link to a client system.
- `next_action` — `null`, or all three of `who`, `what` (a verb phrase), `due` (`YYYY-MM-DD`).

## RFP / tender record — `crm/rfps/<slug>.yaml`

Full worked example:

```yaml
slug: EXAMPLE-mfo-portfolio-system-rfp
title: Portfolio management system — RFP
issuer: Oasis Family Office
country: UAE
segment: family_office
source_url: https://example.invalid/rfp/oasis-pms-2026
published_date: 2026-09-01
deadline: 2026-10-15
status: skipped
fit_assessment: "SCHEMA EXAMPLE — fictional tender used only to validate rfp record structure."
decision:
  outcome: no_bid
  reason: "schema example, not a real RFP"
documents:
  - label: "RFP document (example)"
    link: null
owner: Andre Geha
created: 2026-09-22
updated: 2026-09-22
```

### Field notes
- `documents` — list of `{label, link}`. `link` should point at a file in this repo if we mirrored
  the document, or `null` if we are only recording the source URL above.
- `decision.outcome` is `pending` until a bid/no-bid call is made; `decision.reason` should explain
  the call once made (capacity, fit, timeline, relationship, etc).
- `deadline` drives `tools/crm_report.py`'s "RFP deadlines approaching" section — keep it accurate
  and update `status` as the tender moves. It is **nullable**: some genuine sources (multilateral
  development bank general procurement notices, grant announcements) never state one. Leave it
  `null` rather than invent one — a null deadline just means the record is invisible to the
  approaching-deadlines section until someone finds and fills in a real date.

## What `tools/crm.py validate` checks
1. File name (minus `.yaml`) matches the record's `slug`.
2. Every enum field holds an allowed value.
3. Every date field parses as `YYYY-MM-DD`.
4. `next_action` is `null` or has all of `who`, `what`, `due` non-null.
5. `fit.score` (company) is `null` or an integer 0–100.
6. `status: disqualified` implies a non-null `disqualified_reason`, and vice versa.
7. Every contact has a `name` and a `role` from the enum.
8. No two company records share a slug; same for RFPs.

`validate` exits non-zero if anything fails — it is the QA gate other agents and CI should call
before trusting the CRM.
