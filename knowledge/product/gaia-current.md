# Gaia (current / latest) — what we sell today

> Sales source of truth for the shipping product. Distilled from the official brochure,
> the OFS website and the OFS module documentation. Last synced: 2026-09-22.
> ⚠ This is **today's product**. For the web re-platform see `gaia-new.md` (roadmap).

## One-liner
A customizable, **modular, multi-asset, multi-currency front-to-back portfolio & fund management
platform** — real-time portfolio management + OMS at the core, with fund administration,
shareholder registry, subscriptions/redemptions and NAV. Covers all verticals of asset management.

## Technology (client-safe)
- **Microsoft .NET / C#**, **Microsoft SQL Server**, **open SQL database schema**.
- Deployment **on-premise or cloud**. Access: **thick client · thin client (TSE/Citrix) · cloud**.
- Authentication: Windows **or** SQL. Data transfer: **OLEDB / SOAP / REST**.
- Integration toolbox: web services, procedures, functions, batches, interfaces + the open SQL schema.

## The module set
| Module | What it does |
|---|---|
| **Portfolio Management** (essentials) | Real-time positions & valuation, simulated orders, projections, risk, benchmark comparison, constraint testing, performance ratios. Equity, Fixed Income, Funds, Futures, Options, FX, Commodities, **Private Equity, Repos**. |
| **Order Management System (OMS)** | Trading desk, **FIX protocol**, connected to **Bloomberg / Reuters / Six Telekurs**, portfolio rebalancing, **leverage & margin trading**, legal & management constraints. |
| **Risk & Compliance** | Legal + custom constraints, **pre-trade and post-trade**, breach follow-up, risk indices, **counterparty limits**, **liquidity risk**, audit. |
| **Performance & Simulations** | Performance calculation, valuation, **contribution**, **attribution**, market & FX scenarios, simulations, rebalancing. |
| **Back Office & Custody** | Portfolio administration, **automated reconciliations**, custody operations, accounting. |
| **Cash & Collateral** | Cash management, **repo and collateral**. |
| **Reporting Toolbox** | Customizable analytical views, multi-criteria inventory analysis, client & stakeholder reports. |
| **Connectivity** | Interfaces, **SWIFT**, open SQL schema, FIX, web services, SMS, email confirmations, **core-banking** links. |
| **Fund Administration** | Subscriptions/redemptions, shareholder registry, **NAV calculation**, multi-share & multi-currency, fund accounting, **management & performance fees**. |

> ⚠ **The Web Portal is a SEPARATE PRODUCT, not a Gaia module.** It runs on the **same database**
> as Gaia. Sold and positioned as its own product — see `web-portal.md`. Do not list it as a Gaia
> module, and do not describe Gaia as "including" it. (Corrected by Andre, 2026-09-22.)

## The five workflow steps (how we tell the story)
**① ONBOARD** (CIF/KYC/CRM) → **② MANAGE** (front office, valuation, performance) →
**③ EXECUTE** (OMS, FIX, SWIFT, rebalancing) → **④ PROCESS** (recon, fees, custody, accounting,
confirmations, audit) → **⑤ ANALYSE** (performance, attribution, AUM & profitability reporting),
with **compliance** running across all five. The **Web Portal is a separate product** on the same
database — it is the client/manager-facing channel onto this lifecycle, not a layer of Gaia.

### ① ONBOARD — CIF/KYC/CRM
Multi-channel client creation (manually, **API**, **web portal self-onboarding**, core system,
mobile app). Staged **onboarding workflow** with role-gated validation levels that **email the next
team** at each hop (Prospect Registered → Compliance Screened → Documents Uploaded → RM Approval →
Risk Assigned → RM Signature → SEO Signature → Fees Assigned → Final Approval). Full KYC: parties
& UBOs, IDs/passports with expiry, Arabic names/addresses, occupation, net worth, dependants,
**FATCA / CRS / TIN (+ real-time TIN-check API) / PEP / World-Compliance**, suitability
(knowledge & experience), W-8BEN/W-9. **Risk scoring → CRA/CCA** with MLRO override driving
diligence level + review period. **Document management**: configurable types, mandatory /
prerequisite-to-status flags, versioning, expiry monitoring, stored in the DB, publishable to the
portal. **Expiry/échéance engine**: multi-threshold rules per document type, one action each —
**email · SMS · auto-suspend the client** — to client/RM/ARM/service, with audit + contact note.
**CRM**: contact notes (manual, from the order screen, or auto-created when an advice/valuation is
emailed), CRM blotter, to-dos with deadlines. Governance: client-name encryption right,
data-masking for non-prod copies, dormant-account handling.

### ② MANAGE — front office, valuation, performance
**Front Office cockpit**: real-time auto-refreshing positions, cash, orders, P&L by portfolio,
group, strategy or sub-portfolio. Tabs for allocation, FX coverage, forward FX, intraday,
corporate actions, repos, constraints (ante & ex-post), private equity (commitments, capital calls,
distributions, IRR), projections. **Right-click simulation** of buys/sells/derivatives showing
impact on value, P&L and risk. Risk indicators: duration, convexity, sensitivity, WARF, VaR —
before/after simulation. **Valuation engine**: multi-source pricing profiles (price type ·
counterparty · days-back, with an ordered fallback chain), FX-by-evaluator with pivot currency,
multi-share/multi-class fund NAV, sicavisation. **Performance engine**: time-weighted
**Modified Dietz**; ratio library (std dev, tracking error, **Sharpe, Treynor, Jensen's alpha**,
information ratio, beta, R², **VaR 99%**, volatility); **contribution**; **Brinson attribution**
(allocation / selection / interaction / currency / fee effects). Also ESG & carbon indicators
(Mirova, SDSN, Sustainalytics, Beyond Ratings, Carbon4, CDP, Trucost, temperature alignment) —
available, but only present it when the account asks.

### ③ EXECUTE — OMS, FIX, SWIFT, rebalancing
**Trading desk** blotter (New / Work / partial / filled / suspended) with compliance-approval
status. Order types: **Simple · Bloc** (one security, many portfolios, pro-rata allocation) ·
**Basket** (many securities, one portfolio) · by-security-by-account-group. Attributes: market or
limit, **stop-loss**, market-on-open/close, market-if-touched, %-of-volume, **all-or-nothing**,
**iceberg**; validity **Day / GTC / GTD / GTC-EOY**; broker + brokerage %, custodian, FIGI.
**FIX** message and order-audit tabs when the FIX module is on; routing via **Bloomberg EMSX** or
direct broker integration. Pre-trade **constraints tab** (green = ok, red = breach) on every
channel including the portal. Automatic order emails on save/validate/modify/cancel.
**Rebalancing** to index, investment grid or model portfolio (up to 5 weighted models), exposure-
aware (futures, options-delta), generating **orders, transactions or simulations**.
**SWIFT**: settlement instructions **MT540 / 541 / 542 / 543**, **MT300** FX confirmations, MT535
holdings, ACK/REJ acknowledgement workflow with a follow-up blotter, SSI per trade, host-to-host /
SFTP; CSV instruction files for custodians without SWIFT.

### ④ PROCESS — reconciliation, fees, custody, accounting, confirmations, audit
**Reconciliation**: positions vs custodian statements (file import + column mapping, difference
report), operations vs **core banking** (colour-coded match states), and **accounting
reconciliation on FIFO stacks** (match / split / merge / cancel-and-rebuild).
**Fee engine** — the full stack: broker fees, client fees, **bank commission = client − broker**;
% / fixed-per-unit / lump-sum with thresholds on gross, price or quantity and minimums; setup by
broker → security type → quotation place → fees category → fund group; VAT handling; discounts on
bank commission; **spread pricing**; income fees, cash-transfer and securities-transfer-out fees.
**Introducing-broker (IB) retrocession**: up to 2 IBs per strategy with split %, AUM-based
calculation with thresholds and accruals. **Custody & fiduciary fees**: 8 parameterization levels
with strict priority, 3 calculation methods (average market value / nominal / last market value),
thresholds, min/max, detachment treatment auto-generating fee operations; **SRD II**.
**Operation flow & validation ladder**: `Saved → Transferred to Middle Office → Validated (MO) →
Confirmed → Exported → Accounted / Settled`, multi-level, password required to revert; a missing
account number blocks final validation. Changing a fee after first save **reroutes the trade to
Middle Office** — anti-tampering control. **Double-entry accounting**: ledger root accounts, lines
generated automatically at final validation, monthly **revaluation**, **trial balance** with
local-currency conversion. **Client confirmations/advices**: a format per transaction type,
pre-settlement (excl. fees) vs settled (incl. fees), emailed (optionally password-protected),
each one auto-creating a CRM contact note. **Audit trail**: screen open/close, command-bar actions,
SQL queries, exports, emails, printing, imports, **login attempts**, change-history tables on all
key tables, follow-up audit blotter.

### ⑤ ANALYSE — performance, attribution, AUM, profitability, reporting
**AUM report**: market value of all assets under management, weekly/monthly/yearly, by asset class
and security type, filtered by group, client, **RM**, category, custodian, country, market, branch
and client classification; multi-grid dashboard, YTD/MTD returns, RM asset mix, activity report.
**Profitability report**: all fees & charges between two dates in three parts — transaction fees
(client, broker, **bank commission**, VAT), periodic fees (custody, DPM management, IB, maintenance),
and total — by RM / client / branch / custodian / strategy, weekly to yearly, with a manager summary.
**Client reporting**: valuation report, client investment report, statement of account, realized
P/L journal, coupon & redemption schedule, position reports, calculated security allocation.
**Report engine**: Microsoft **SSRS/RDL** master + sub-reports, multi-language, charts, conditional
visibility, **password-protected PDF**, **fully customizable and branded per client**. Generated
three ways — interactively, by **batch**, or by **web service** — then printed, saved, emailed
(auto CRM note) or **published to the web portal**, with daily/weekly/monthly auto-send.

## Compliance & constraints engine (the cross-cutting differentiator)
**Four constraint types**: by sub-group (user-built), by inventory (position-based), by operation
(judges the trade itself), **by rule** (hard-coded prudential library **maintained by OFS**).
**Two control levels**: **ante/pre-trade** (fires on save of an order, transaction or simulation;
tests calculated positions + pending orders + this order) and **ex-post** (EOD recheck).
**Action on breach**: **warning** (pop-up) · **password** (force-save, admin-controlled) ·
**blocking** · plus **additional-status routing** for four-eyes escalation, a mandatory
authorization comment, and colour-coded statements.
**Measured in**: %, portfolio net asset, quantity, number of holdings, duration, sensitivity,
omicron, **WAM**, **WAL**, volatility. Includes the UCITS-style **5/10/40** issuer-group rule.
**Ready-made CMA/BDL regulatory pack (Lebanon)** — a genuine differentiator for a Beirut,
CMA-regulated house: US securities require a valid **W-8BEN/W-9**; **insider blackout periods**
with an insiders register; **bank-share pre-approval** (BDL) and the 5%-of-floating test;
shareholders rule; **product suitability** (client risk score vs security risk score, with a
printed acknowledgement form); securities and client **watch-lists**; blacklist import.
Also: cash-availability control, **Shariah screening**, automatic breach emails routed to
modelled services (Compliance, Risk Committee), and a **Compliance Manager Blotter** where
compliance approves or rejects trades, with full ex-ante and ex-post audit.

## Data feeds & connectivity (confirmed)
Bloomberg · Reuters · Six Telekurs (prices, characteristics, corporate actions) · **FIX** ·
**SWIFT** · SMS · email confirmations · core-banking interfaces (accounting / reval / datawarehouse) ·
web services · open SQL schema.
