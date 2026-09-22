# Web Customer Portal — feature map (live today)

> ⚠ **A SEPARATE PRODUCT from Gaia** — sold and positioned in its own right. It runs on the
> **same database** as Gaia, which is why the two stay in step with no integration project.
> Never describe it as a Gaia module or as part of Gaia. (Confirmed by Andre, 2026-09-22.)
>
> For **clients, managers/EAMs and branches**.
> This is our proof that "Gaia becomes a fast web app" — it exists now, not in 2027.
> Verified by live exploration of the test portal. Last synced: 2026-09-22.

## What it is
A modern web portal backed by a **.NET web app (ASP.NET Core, EF Core, CQRS/MediatR, SQL Server)**.
Omega-branded, **multilingual (EN + Arabic/RTL)**, **dark/light mode**, responsive, HTTPS.

## The two experiences
- **Client** — sees their own portfolio(s).
- **Manager / EAM / branch** — **one login, the whole book**: every client portfolio they manage,
  consolidated or any subset, with drill-down into any single client.
- **Portfolio Selection** pane: tick any combination of strategies (check/uncheck all + search) →
  **Validate** → a single consolidated view (NAV, unrealized P/L, cash, allocation, positions,
  cash accounts, schedule, transactions, statements). Note: entries labelled "portfolios" in the
  selector are really **strategies / sub-portfolios**.
- Some views (**Performance**) require exactly one strategy.

## Dashboard
As-of date + refresh; quick actions **KYC** and **NEW ORDER**; KPI cards — **Net Asset Value,
Unrealized P/L, Cash, Available Cash**; allocation **donut charts** by asset class, currency and sector.

## The tabs
1. **Positions** — holdings grouped by asset class; security, currency, quantity, cost/market price,
   total cost/value, **unrealized P&L and P&L %**, accrued interest, **allocation %**, ISIN, price
   date. Per-line **Buy/Sell**, column filters, pagination, export.
2. **Current Accounts** — multi-currency cash balances with per-account movements.
3. **Schedule** — upcoming events/échéances: coupons, dividends, maturities.
4. **Transactions** — date-range filter; trade/value date, type, shares, unit/gross amount,
   **total fees**, net amount, **realized P/L**.
5. **Performance** — per-strategy performance analytics.
6. **Client Statement** — **self-service report generation** (portfolio / strategy / date range →
   Generate) **plus** a repository of statements pushed by the manager; downloadable PDFs.
7. **Orders** — client order blotter with the execution lifecycle, including **partial fills**
   (executed vs to-be-executed nominal).

## Order entry
A full order ticket: strategy, Buy/Sell, **ISIN lookup**, quantity, validity type
(**Day, GTC, GTD, GTC EOY, GTM, IOC**), order type (market/limit), price. Orders flow into Gaia's
OMS, are **checked against the same pre-trade constraint engine**, and appear in the blotter.

## KYC / CIF centre
- **Client Docs** — document repository with per-document **type, file, doc date, expiry date,
  mandatory flag, Replace, version History**, per-type upload/drag-drop, **bulk upload**, search.
  Document types are **configurable per firm**.
- Sub-tabs: **KYC**, **Portfolio**, **Knowledge & Experience** (MiFID suitability), **Net Worth**,
  **Dependants**, **Nationalities**, **Phones**, **Tax Countries** (CRS/FATCA), **Insiders** (PEP/
  insider), **Arabic Information**.
- A guided **digital onboarding flow** also exists in the portal — get access to those screens
  before demoing onboarding in detail.

## Account self-service
Profile (national ID, email, name, job title, mobile), **self-service password change**, avatar,
dark-mode toggle, notifications bell, language selector.

## Why it matters in a pitch
- Proof the modern web experience is **real today**, not a 2027 promise.
- **EAM/multi-family-office ready**: one login, many clients, consolidated or drilled down.
- **Self-service**: clients place orders, generate statements, upload KYC documents.
- **Compliance-friendly and visible**: mandatory documents, expiry tracking, suitability, CRS/FATCA, PEP.
- **Bilingual EN/Arabic + dark mode** — fits a Gulf and Levant client base.

## Access
The test portal URL and credentials are **internal only** and live in the marketing repo
(`ofs-marketing/knowledge/portal-access.md`). Never put them in a deliverable.
