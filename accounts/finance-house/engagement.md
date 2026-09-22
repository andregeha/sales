# Finance House — engagement

## Current state
- **Stage:** active client, expansion/upgrade decision pending.
- **Opportunity:** approval to move to the **latest Gaia version**, which unlocks five pending
  projects; plus in-flight product development (Loan on Gold, Crypto).
- **Next action:** ⚠ **needs refresh from Andre** — the status below is as of the 2026-07-24 meeting
  and is now two months old.
- **Blocked on:** FH's go-ahead on the upgrade.

## The upgrade economics (as stated to FH)
On approval and scheduling: **~1.5 months** of deep testing on the OFS side to reach a UAT version,
then **~1 month** of FH testing (IT + business) to validate.

## Ball in FH's court (as of 2026-07-24)
| # | Item |
|---|---|
| 1 | **Go-ahead to move to the latest version** — unlocks EOD automation, Web Portal, trade confirmation, corporate actions, FIX routing |
| 2 | Updated specs for **Bloomberg Pricing** automation |
| 3 | Updated specs + confirmation for the **Crypto** product |
| 4 | **Template** for the Prop Books Excel reports |
| 5 | **Broker + Bloomberg (EMSX)** conversation for FIX order routing |

## Ball in our court
| # | Item | Status as of 2026-07-24 |
|---|---|---|
| 1 | **Loan on Gold** product | Pending tests; UAT expected first week of August |
| 2 | **Crypto** product | Proposal sent; UAT mid-September if accepted |
| 3 | **Recon module** (positions + cash, all products) | Delivered with crypto; global module usable across all of Gaia |
| 4 | Gold/silver accounting · Portfolio Report · Prop Books Excel reports | Not prioritized |

## Risks
| Risk | Impact | Mitigation |
|---|---|---|
| The upgrade decision stalls indefinitely | Five projects stay frozen; relationship drifts | Make the cost of *not* upgrading explicit — list what stays manual each month |
| Status is two months stale | We walk into a meeting with wrong facts | **Refresh with Andre before any FH action** |
| Discovery depth is internal-only | Accidental leakage into client material | Client-facing material is built from `knowledge/`, never from the discovery notes |

## Deliverables produced (in `ofs-marketing`)
| What | Where |
|---|---|
| Upgrade deck (current vs latest vs New Gaia) | `prospects/finance-house/finance-house-upgrade.pptx` |
| Pending-projects status + recap email | `prospects/finance-house/pending-projects-status.md`, `status-email.html` |
| Process knowledge base + read-API mapping | `prospects/finance-house/how-fh-uses-gaia.md`, `read-apis.md` |
| Shareable knowledge document | `prospects/finance-house/FH-Gaia-Knowledge.html` |
