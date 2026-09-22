# Finance House (FH / FHC) — profile

> Source: `ofs-marketing/prospects/finance-house/` (README, how-fh-uses-gaia, pending-projects-status,
> latest-version-features), synced 2026-09-22. **The most active engagement.**

## Snapshot
- **Finance House (FHC)** — UAE. An existing **Gaia client and an expansion prospect**.
- Runs Gaia across **three environments**:
  1. **InvestNation** — their **flagship** retail investing app. A vendor mobile neobank/investing
     app that calls Gaia through the **FH Web API** via middleware. In the app's own diagrams Gaia is
     labelled "FH Capital Wealth Management Platform".
  2. **Private Wealth Management** — leveraged discretionary client portfolios.
  3. **Prop books** — their own proprietary/treasury books.

## Systems
- **T24** — core banking, the cash truth.
- **SCB (Standard Chartered)** — custody and settlement.
- **Bloomberg EMSX** — the intended FIX order-routing path.
- **FH Virtual Card** — wallet reconciled to the custodian.
- Gaia version: **older than the current latest** — the upgrade is the central commercial question.

## The commercial picture
Two workstreams run in parallel:
1. **Upgrade** — a three-way story: FH's *current* Gaia · the *latest* version (same WPF/.NET
   technology, new features, **available now**) · the *New Gaia* (future web re-platform).
   Framing: **"upgrade to the latest now, move to the New Gaia later."**
2. **Process/technical discovery** — mapping exactly how FH uses Gaia, down to code and database,
   to ground the conversation and de-risk delivery.

## What the upgrade unlocks for them
Web Portal (new for FH) · EOD automation · trade confirmation · corporate-action automation ·
**FIX/EMSX order routing** · OMS automatic emails on modify/cancel · a new rebalancing module for
wealth management · CRM document-expiry tracking on **any** document type · TIN-check and new KYC
APIs · onboarding comments + automatic emails · Bloomberg corporate-actions and reference-data APIs ·
faster valuation with accrued dividends · faster prop-book risk indicators · new constraints and
breach-management workflow · broker-fee deviation report · IB referral fees · automatic settlement
instructions to SCB · CRS report · dormant-account management.

## Our angle
The **single biggest unlock is FH approving the move to the latest** — it releases five pending
items at once. Everything else is downstream of that one decision. Lead every conversation there.

## ⚠ Internal only — never client-facing
The FH discovery involved **read-only** work against FH UAT databases and the FH Web API source.
Server names, database names, connection files, API endpoints/ports, table and column names,
stored-procedure names and operation IDs are **internal grounding only**. All Gaia database work
stays **read-only** — Gaia can place real orders, post accounting and send SMS/email.
Detail lives in `ofs-marketing/prospects/finance-house/`, not here.
