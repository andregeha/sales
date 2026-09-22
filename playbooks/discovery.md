# Discovery playbook

> Goal: understand the business well enough that the solution becomes obvious to *them*.
> Ask conversationally. This is a map, not a script to read aloud.

## A. The business — ask first, it shapes everything
1. What is the entity, and what is its **licence/regulator**?
2. Which country, and is there cross-border activity?
3. Roughly what **AUM**, how many portfolios, clients, funds — and the growth plan?
4. **Client base**: retail, HNW/private, institutional, intra-group?
5. **Mandate mix**: discretionary, advisory, execution-only?

## B. Systems and pain
6. What runs portfolio, orders and back office **today** — a legacy system, spreadsheets, nothing yet?
7. Where does time and risk actually leak? What breaks at month end?
8. **Timeline** — when do they need to be live, and what is forcing it (launch, audit, regulator,
   contract expiry)?
9. On-premise or cloud — and what constrains that (data residency, IT team size)?

## C. Asset classes and trading
10. Which asset classes? (Equity, fixed income, funds, FX, futures/options, commodities,
    **private equity, repos** — we cover all of these.)
11. Do they route orders to brokers or venues via **FIX**, or manually? Do they need a full OMS?
12. Execution model: in-house dealing desk, outsourced, custodian-routed?

## D. Compliance, KYC and risk
13. Which constraints must be enforced **pre-trade** and which **post-trade** — mandate limits,
    regulatory limits, concentration?
14. **KYC/CIF**: onboarding workflow, document management, **expiry/échéance reminders**?
15. Reporting obligations to the regulator? What does their auditor ask for?
16. What happens today when someone breaches a limit — who finds out, and when?

## E. Fees, valuation, performance
17. Which **fee types** — management, **performance/incentive**, custody, brokerage,
    **IB/retrocession**? How are they calculated and booked today?
18. Pricing sources and data feeds — Bloomberg, Reuters, Six Telekurs, local exchanges?
19. How do they measure **performance** and **profitability** — per client, portfolio, desk, RM?
20. **Reconciliation** — against which custodians and banks, how often, and how painful?

## F. Reporting and client experience
21. What client reporting goes out today, and how — PDF, email, portal?
22. Is a **client portal** with real-time positions and document delivery interesting? For which tier?
23. Branding and **languages** — English, French, Arabic?

## G. Decision and commercials
24. Who are the decision-makers and influencers — IT, operations, compliance, investment?
25. Start with the essentials and grow, or full front-to-back from day one?
26. What would make this a personal success for our champion in the first 6–12 months?
27. **What happens if they do nothing?** (The real competitor is usually inertia.)

## Answer → what to lead with
| If they say | Lead with |
|---|---|
| Heavy compliance / KYC burden | Risk & Compliance + the constraint engine + CMA/BDL pack + CRM |
| Active trading, FIX, brokers | OMS, trading desk, order types, EMSX/direct routing |
| Funds, NAV, subscriptions | Fund Administration, multi-share NAV, fees |
| Many custodians | Back office & custody, **reconciliation** |
| Client experience / EAM | **Web portal** (demo it) + Reporting Toolbox |
| Lean new entity, fast start | Modular essentials + cloud |
| Existing Gaia, old version | Upgrade to latest now → New Gaia later, same database |
