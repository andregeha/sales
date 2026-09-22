# Open questions

> Anything unknown, unverified, or needing Andre's approval. Nothing gets guessed.
> Status: 🔴 blocking · 🟠 needed soon · ⚪ nice to have. Newest first.
>
> **Stage model**: defined in `pipeline/pipeline.md` (2026-09-22) — change it if it does not match
> how you think about deals.

## ✅ Answered by Andre 2026-09-22
1. **Scope** → **new business only**. Existing clients are context/proof, not pipeline.
2. **Deliverables** → the full engine: find clients, find every RFP, automated lead pipeline,
   inbound + outbound outreach, daily and continuous, log everything, own CRM. Plus pipeline & forecast.
3. **Autonomy** → agents draft freely; **Andre approves and sends**. Give him fast, automated ways to send.
4. **System of record** → **this repo**. No external CRM.
5. **Markets** → **UAE, KSA, Lebanon, France**.
6. **Segments** → **family offices & MFOs, private/investment banks, asset & fund managers**.
7. **Media** → email, LinkedIn, and anything else sensible.
8. **Cadence** → **daily scheduled run**.

## For Andre — still open
| # | Question | Status |
|---|---|---|
| 0 | 🔴 **The environment blocks general web access** — only package registries are allowed; every other host is refused by the egress policy. Agents can search, but cannot open a tender portal or a regulator register. **The RFP radar and lead sourcing cannot work properly until this is widened.** Can you change the environment's network policy? (https://code.claude.com/docs/en/claude-code-on-the-web) | 🔴 |
| 5 | **Pricing** — is there a price book, list price or discount policy I may hold here, even internal-only? Without it I cannot qualify on budget, and every commercial question bounces to you. | 🟠 |
| 5a | **Is there an email-sending or sequencing tool** you would connect (Outlook send, a sequencer), or does every message go out by hand from your mailbox? This changes how I build the approval queue. | 🟠 |
| 5b | **Do you have a LinkedIn Sales Navigator seat?** It would materially improve lead sourcing and contact discovery in all four markets. | 🟠 |
| 5c | **Any markets, firms or people that are off-limits** — conflicts, existing partner territories, someone we must not approach? | 🟠 |
| 5d | **Inbound — do we control the OFS website** enough to add pages, a lead form and analytics? Right now I have no inbound surface at all, so "inbound marketing" produces nothing. See `playbooks/inbound.md`. | 🟠 |
| 5e | **Will you publish on LinkedIn** under your own name at a regular cadence? It is the cheapest, highest-leverage inbound channel we have, and the material is already written in `knowledge/`. | 🟠 |
| 5f | **Budget for events or paid search**, or organic only? | ⚪ |
| 5g | **Who answers an inbound enquiry within the hour?** An inbound lead that waits a day is lost. | ⚪ |
| 6 | **Competitors** — who do we actually meet, where do we win and lose? (`knowledge/positioning/competitors.md` is an empty placeholder.) | 🟠 |
| 9 | **Arabic** — do we need Arabic client-facing material for the Gulf, or is English sufficient there? (Gaia and the portal support Arabic/RTL, so it is a real option.) | 🟠 |
| 10 | **Referenceable clients** — which names may we say out loud, to whom, and under what conditions? This is the single most useful thing I am missing for outreach credibility. | 🟠 |
| 11 | **Team** — is anyone else going to use this repo, or is it you plus the agents? | ⚪ |
| 12 | **Targets** — is there a revenue/quota number the pipeline should be measured against? | ⚪ |

## Product gaps to confirm with R&D
| # | Question | Status |
|---|---|---|
| 13 | Exact FIX venue/broker coverage we can claim in writing (beyond Bloomberg EMSX + direct broker integration). | 🟠 |
| 14 | Whether a **dedicated profitability/RoA view** exists beyond the profitability report, for a client asking specifically. | ⚪ |
| 15 | The **digital onboarding flow** screens in the portal — we have not seen them; get access before demoing onboarding end to end. | 🟠 |
