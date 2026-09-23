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

## ✅ Resolved 2026-09-22 (laptop)
- **Q0 — the network block.** Resolved by moving to the laptop. Every regulator register and tender
  portal we need is reachable. The register connectors are built and running as a result.

## 🔝 The four to answer first (2026-09-22)
These are ordered by what they unblock, not by how easy they are.

| # | Question | Why it matters | Status |
|---|---|---|---|
| 1 | **Which existing client names may we reference, and to whom?** Finance House, GIMD/Dassault, Bank Audi, BLOM, AGPM — which may be named, in which markets, and under what conditions? | Worth more for outreach credibility than anything else we could write. Every draft currently says "asset managers and banks across France and the Gulf" because naming anyone needs your approval. | 🟠 |
| 2 | **Which Lebanese banks are on the survivor track under Law 23/2025?** | **All 17 Lebanese bank records are frozen at `nurture`** because no public source resolves this, and a bank in resolution buys nothing. This is the single biggest block of stalled pipeline we have. | 🟠 |
| 3 | **Would you take a LinkedIn Sales Navigator seat?** | We now hold **many named decision-makers with a verified LinkedIn profile and no email**. A seat turns names into reachable people. Contact routes — not lead volume — are the binding constraint on the whole engine. | 🟠 |
| 4 | **Pricing guidance · any off-limits firms · do we control the OFS website?** | Without pricing every commercial question bounces to you; without an off-limits list we may approach someone we shouldn't; without the website there is **no inbound surface at all**. | 🟠 |

## 🆕 New, from this session
| # | Question | Status |
|---|---|---|
| 16 | **Will you set up the free saved-search email alerts on BOAMP and PLACE** (and My TED)? They are free, they take minutes, and **a push alert beats any scraper we could write**. They need an account in your name, so I cannot do it. Links in `knowledge/market/rfp-sources.md`. | 🟠 |
| 17 | **Should the daily run be scheduled on this laptop, and at what time?** Nothing is scheduled right now. Weekday mornings was the plan. ⚠ A laptop only runs when it is on — a missed morning is a genuinely missed day. | 🟠 |
| 18 | **Can anyone run the Saudi CMA connector from the Riyadh office** (or any Saudi network)? Its Open Data API times out from Europe. From inside the Kingdom it would probably work, and would upgrade Saudi from a partial source (36 of 242 firms) to a complete one. | ⚪ |
| 19 | **Does anyone at OFS have an Etimad supplier account?** Etimad blocks automated access with its own bot protection, which we will not try to defeat. **Saudi tender coverage is therefore zero.** A human with an account could set up its notifications. | 🟠 |
| 20 | **Do we want records for adjacent segments** — custodians and brokers — or only our three core segments? The Saudi register surfaces them and they currently land as low-scoring records. | ⚪ |

## For Andre — still open
| # | Question | Status |
|---|---|---|
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

## Sourcing gaps (opened 2026-09-23)
| # | Question | Status |
|---|---|---|
| 16 | **EBRD procurement** — the notice search is a stateful JSF/ADF portal with no query contract, the same shape as France's PLACE. Needs a human with a browser, or an official EBRD feed, before it can be read. It is `failing` on the Sources view until then, deliberately. | 🔴 |
| 17 | **UNGM sees titles only.** The listing carries no description, so our classifier judges a title alone — a genuinely relevant notice with an uninformative title will be missed. Reading each notice's detail page would fix it at ~60 extra requests per run; not yet judged worth the load. | 🟠 |
| 18 | **286 candidates are not in the CRM**, now scored so the queue sorts by likelihood. Nobody has reviewed them. The eight scoring 60+ are the ones worth Andre's eyes first. | 🟠 |
| 19 | **France's 19,464 GLEIF funds have not been swept** for fund→manager relationships — hours at a polite rate. Saudi, UAE and Lebanon are done (17 candidates, incl. SNB Capital and Jadwa). | ⚪ |
