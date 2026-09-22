# RFP radar

> **Not missing a tender in our markets is a core commitment of this workspace.**
> A missed deadline is the worst thing we can produce — worse than a bad draft, worse than a quiet
> day. Everything here exists to make that impossible.

## Sources
`knowledge/market/rfp-sources.md` — the registry per market, with URLs, access method, language and
whether it can be monitored automatically. Check the daily-cadence sources every run.

## What counts as in scope
Tenders for portfolio management systems · asset and wealth management platforms · fund
administration and NAV systems · order management and trading systems · custody and back-office
systems · investment reporting and client portals · and the broader "core banking / treasury /
investment management" procurements where a portfolio module is in scope.

Issued by: banks · asset and fund managers · sovereign and public funds · pension funds · insurers ·
custodians · regulators and central banks · family offices (rarely public, but it happens).

## The loop
1. **Scan** the daily sources. Search in **English, French and Arabic** — the phrasings in
   `rfp-sources.md` exist because a tender titled in Arabic will not surface on an English term.
2. **Record immediately**, before assessing: `crm.py rfp add` with title, issuer, country, source
   URL, published date and — above all — the **deadline**. Record first, judge second; an
   unrecorded tender is a missed tender.
3. **Assess fit** with **`ofs-solution-engineer`**: can Gaia genuinely do this? Honestly — including
   the parts we would have to build, and the parts we cannot do at all.
4. **Check the practicalities**: eligibility, local presence or partner requirements, registration
   on the portal (⚠ some portals require registration *weeks* before bidding — flag that the day we
   spot it, not the week of the deadline), language of submission, bid bonds, references required.
5. **Escalate to Andre** with a clear recommendation: bid, partner, or skip — and why.
6. **Decide and record.** Skipping is a fine outcome; drifting past the deadline is not.

## Deadline discipline
- Anything closing **within 14 days** appears at the top of Andre's brief **every day** until decided.
- Anything closing **within 7 days** that is still undecided is escalated explicitly as blocking.
- Registration or pre-qualification lead times are treated as the **real** deadline, because they are.

## When we bid
The RFP becomes a company record too — a tender is also an account. Run `/rfp-response` for the
answers, `ofs-solution-engineer` for the verdicts, `ofs-writer` for the prose.
⚠ **Never submit.** Andre submits. Commercials, references and any contractual commitment are his.

## Learned filters (from real runs)
- **"Corporate portfolio management" in a government or public-authority RFQ almost always means
  *project/programme* portfolio management** — a governance discipline, not investment portfolio
  management. Check the issuer: an education authority or a ministry is not our buyer.
- **Mandate calls are not software tenders.** French public pension funds (FRR, ERAFP and similar)
  publish *appels d'offres* to **select external asset managers to run investment mandates**. That is
  procurement of investment *services*, not investment *software* — so never record one as an RFP.
  **But they are a lead source**: the managers bidding for and winning those mandates are exactly our
  buyers, and **winning a new institutional mandate is a trigger** — new reporting obligations, new
  asset classes, new scrutiny. Feed these to lead sourcing, not to the RFP radar.
- **Check the deadline before anything else.** Aggregator listings routinely surface tenders that
  have already closed.
- **Aggregator data is unverified.** If a tender only appears on a third-party aggregator and not on
  the official portal, say so in the record.

## Honest limits
Many relevant RFPs in these markets are **invitation-only** and never published. The radar catches
what is public; the rest comes from relationships, partners and regulator networks.

⚠ **Measured reality, 2026-09-22:** with page-fetching blocked, the radar runs on search snippets
alone. The first live run searched all four markets in English, French and Arabic across ~19 queries
and found **zero** qualifying open tenders. That is a *"found nothing indexable"* result, **not a
confident zero** — Etimad, BOAMP and TED are session-walled and form-driven, and their tender pages
appear not to be search-indexed at all. Estimated coverage: **well under 10% of live tender flow,
and effectively 0% of invitation-only processes.** Until egress is opened (or portal accounts with
saved-search alerts are provisioned — BOAMP, PLACE, TED and Etimad all support free email alerts),
a nil return from this radar means very little. Say this plainly
rather than implying the radar is complete — and treat every published tender we *do* find as
evidence of a buying centre worth knowing, whether or not we bid on it.
