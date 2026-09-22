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

## Honest limits
Many relevant RFPs in these markets are **invitation-only** and never published. The radar catches
what is public; the rest comes from relationships, partners and regulator networks. Say this plainly
rather than implying the radar is complete — and treat every published tender we *do* find as
evidence of a buying centre worth knowing, whether or not we bid on it.
