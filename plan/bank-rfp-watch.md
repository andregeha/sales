# Bank-as-publisher RFP watch -- UAE and Saudi commercial banks, live-probed 2026-09-25

> Owner: sales research, for Andre Geha. Answers a direct requirement: "I don't want to miss any
> RFP from a bank in UAE or KSA." Tests one hypothesis -- that a bank, being a private buyer, would
> publish an RFP (if anywhere) on its own supplier/procurement/tenders page, not on a government
> tender portal. Companion to plan/gulf-rfp-sources.md (government/multilateral portals) and
> knowledge/market/rfp-sources.md.
>
> Method: every page below was fetched live today with curl, an honest identifying User-Agent
> (OFS-Research/1.0), GET only. No accounts created, no forms submitted, no CAPTCHAs or WAFs
> defeated. Where a bank runs a third-party e-sourcing platform, the platform's own "Find
> Opportunities" link (if any) was followed to see whether it resolves without a session. Every
> "none found" states what was tried. Nothing was written to crm/.

## Headline finding

Zero of the 71 banks in scope have a public, readable, unauthenticated live-notice list.
Every procurement/vendor page found is one of three things: (1) a supplier-registration form or
Oracle iSupplier/SAP Ariba/Jaggaer portal that requires a login to see anything, including any
"opportunities" list; (2) a static informational page (T&Cs, contact email, ISO-certification
news) with nothing to watch; or (3) absent -- no such page exists at all. This confirms Andre's
hypothesis about where a bank RFP would surface, and disproves the hope that it would be
watchable without a business relationship or a supplier account.

## Watchlist (best of a weak field -- ranked by how close each gets to "watchable")

None of the below currently qualify as a watchable public feed. They are listed because a login
unlocks something concrete, which is the closest thing to a lead if OFS ever registers as a
supplier (a separate decision, not made here).

| Rank | Bank | Country | Platform | What's behind the login |
|---|---|---|---|---|
| 1 | Emirates NBD | UAE | Jaggaer/BravoSolution ("esop") | A "Find Opportunities" link exists at `/esop/guest/go/public/opportunity/current`, redirecting to a real tender-list URL (`/esop/toolkit/opportunity/current/list.si`) -- but it returns HTTP 401 without a session. The feature exists; it is not public. |
| 2 | Dubai Islamic Bank | UAE | Jaggaer/BravoSolution ("esop"), same platform as ENBD, different tenant | Identical pattern: opportunity-list endpoint returns HTTP 401. |
| 3 | Al Rajhi Bank | Saudi Arabia | Oracle EBS iSupplier | "Register new supplier" and "Login to the supplier portal" only; no notice list visible pre-login. |
| 4 | Riyad Bank | Saudi Arabia | Oracle iSupplier (isupplier.riyadbank.com) | Same pattern -- registration + login, no visible notices. |
| 5 | Alinma Bank | Saudi Arabia | Oracle iSupplier (supplierportal.alinma.com) | Same pattern. |
| 6 | Bank AlBilad | Saudi Arabia | Oracle iSupplier (same template as Al Rajhi/Riyad/Alinma) | Same pattern. |
| 7 | Central Bank of the UAE (CBUAE) | UAE | Two separate systems: eservices.centralbank.ae/eprocurement/ (username+password+CAPTCHA+security token) and supplier-portal.cbuae.gov.ae (separate BI-styled portal) | Login-gated; no public tender list on either. |
| 8 | SAMA (Saudi Central Bank) | Saudi Arabia | "Suppliers Management Portal", SharePoint | "Login (Registered Supplier)" / "Request to register a new supplier" only. Confirms the 2026-09-22/25 finding already logged in plan/gulf-rfp-sources.md row 7 -- zero live listing, static page. |
| 9 | ADCB | UAE | Own supplier portal (adcb.com/en/suppliers/) | Page itself could not be fetched -- HTTP 403 (WAF/bot-protection block, confirmed a block not an absence). Search evidence (ADCB's own FAQ) describes a "Supplier Self-Registration Request Form," i.e. registration only. |
| 10 | ADIB | UAE | SAP Ariba (per ADIB's own page text) | The bank's own page names SAP Ariba but exposes no portal link -- only mailto:vendor.registration@adib.com. Registration by email, not a self-service notice board. |
| 11 | National Bank of Fujairah | UAE | vendorportal.nbf.ae/VendorPortalWeb/ | Bare login shell, title "Vendor Portal" only -- no content pre-login. |
| 12 | Gulf International Bank - Saudi Arabia | Saudi Arabia | gib.com/en/procurement (static) + Coupa (per a 2019 Coupa press release) | The public page only offers downloadable Bahrain/KSA standard supplier T&C PDFs -- no Coupa portal link exposed, no notices. |

## Confirmed absent -- no procurement/supplier page found anywhere on the bank's own site

Search (site: queries, generic queries) and direct path probing (/suppliers, /vendors,
/procurement, /tenders, /about-us/... variants) both came back empty. Listed with what was tried.

| Bank | Country | What was tried | Result |
|---|---|---|---|
| First Abu Dhabi Bank (FAB) | UAE | bankfab.com path guesses (all 404); site search | No general vendor/procurement page. The only supplier-facing system found is FBMS (FAB Building Management System, fbms.bankfab.com) -- but that is specifically for classified housing-loan consultants/contractors (nominated/invited only, Microsoft-authenticated), not a general IT/RFP channel. |
| Mashreq Bank | UAE | mashreqbank.com path guesses (all 404); site search | None found. (collections.mashreq.com is a client-facing trade-collections product, unrelated.) |
| RAKBANK | UAE | Site search only (no stable domain-path pattern found to probe) | None found -- only an internal "Procurement Committee" description and a "VP - Vendor Management" job ad surfaced. |
| Commercial Bank of Dubai (CBD) | UAE | cbd.ae path guesses (all 404); site search | None found. |
| Emirates Islamic Bank | UAE | Homepage and path guesses | HTTP 403 on every request (Cloudflare/WAF) -- a confirmed block, not a confirmed absence. |
| Sharjah Islamic Bank (SIB) | UAE | sib.ae/en/about-us/suppliers (200 but is the site's own branded 404 page); full site nav extracted, no supplier/procurement/tender item in the menu | None found. |
| Ajman Bank | UAE | Path guesses (all 404); site search | None found. |
| Banque Saudi Fransi (BSF) | Saudi Arabia | Path guesses on bsf.sa (all resolve to an identical 3,976-byte page -- a soft-404); site search found only a general "Register your enterprise's details" partnership form (bsf.sa/english/corporateapply, for business banking, not vendor onboarding) and a "Manager - Procurement Relationship" job ad | None found. |
| Saudi Awwal Bank (SAB) | Saudi Arabia | Site search | None found -- only newsroom coverage of SAB's ISO 20400 sustainable-procurement certification (2025), no portal. |
| Saudi National Bank (SNB) | Saudi Arabia | alahli.com path guesses (all 404); site search | None found. |
| Arab National Bank (ANB) | Saudi Arabia | anb.com.sa path guesses -- all returned an identical 24,842-byte page (soft-404) | None found. |
| Bank AlJazira | Saudi Arabia | bankaljazira.com path guesses -- returned near-identical large pages (homepage fallback); site search | None found. |
| Saudi Investment Bank (SAIB) | Saudi Arabia | Path guesses (all 404); site search | None found beyond general "responsible procurement" language in sustainability material. |
| D360 Bank | Saudi Arabia | Site search | None found -- only careers postings for internal procurement roles. |
| STC bank | Saudi Arabia | Site search | None found for the bank entity. Caution: do not confuse with stc Group (the telecom parent)'s own supplier portal at solutions.com.sa/suppliers -- that belongs to the telecom company, not the digital bank. |

## Blocked (not the same as absent)

| Bank | Country | Evidence |
|---|---|---|
| ADCB | UAE | adcb.com/en/suppliers/ -- HTTP 403 on a plain GET with an honest UA. |
| Emirates Islamic Bank | UAE | HTTP 403 on the homepage itself and on every guessed path. |

## Not independently deep-dived this session (spot-checked or reasoned by category)

The remaining ~45 of the 71 CRM-listed banks are overwhelmingly single/limited branches of
foreign banking groups, or DIFC/ADGM private-banking arms -- Citibank N.A., J.P. Morgan Middle
East, BNP Paribas, Credit Agricole CIB, Intesa Sanpaolo, MUFG, Sumitomo Mitsui, Natixis, DBS
(DIFC), the Chinese state banks (Agricultural Bank of China, Bank of China, China Construction
Bank, Bank of Communications, ICBC), the Indian PSU/private banks (Bank of Baroda, Bank of India,
Punjab National Bank, Canara Bank, Union Bank of India, State Bank of India, ICICI, Axis), the
Korean banks (Shinhan, Woori), and a cluster of DIFC/ADGM private banks and boutiques (Julius Baer,
LGT, Lombard Odier, EFG, Edmond de Rothschild, Capital Union, S.P. Hinduja Advisory, Al Ahli Bank
of Kuwait, BankMed SAL, FFA Private Bank, Rasmala Investment Bank, Bank of Palestine Global). Also
in this set: several small foreign branches licensed in Saudi Arabia (Deutsche Bank, UBS AG, J.P.
Morgan Chase N.A., National Bank of Bahrain, National Bank of Egypt, National Bank of Iraq, Trade
Bank of Iraq, National Bank of Pakistan, T.C. Ziraat Bankasi, PT Bank Syariah Indonesia, Muscat
Bank, Qatar National Bank, National Bank of Kuwait's Saudi branch, and Gulf International Bank's
parent group).

Three of these were spot-checked directly (National Bank of Bahrain's homepage, Bank Muscat's
homepage, J.P. Morgan's Saudi "about us" page) -- none carry a supplier/vendor/procurement/tender
link in their site navigation. This is consistent with the pattern for every branch-office entity
found in this exercise: procurement for a branch of a global banking group is run by the group at
head-office level (where a page exists at all, it is a global one, not a UAE/KSA-specific notice
board), and a single-purpose branch or a DIFC/ADGM private bank simply has no local buying function
large enough to publish. This is a reasoned generalisation from the pattern observed across every
bank actually checked, not a claim independently verified for each of the ~45 unchecked names --
flagged per the "say unknown loudly" rule rather than silently assumed.

Qatar National Bank is a partial exception worth a follow-up: QNB's own site names the Coupa
Supplier Portal as its procurement channel (qnb.com/.../encoupasupplierportal.html) -- Coupa CSP
is a real, named system, but by design it is supplier-login/invitation-gated, and no live fetch was
made this session to confirm there is no public tender board layered on top of it (unlikely, but
not measured).

## Two identity flags (per the "don't conflate similarly named entities" rule)

1. "Vision Bank" is two unrelated entities. The CRM's UAE row, "Vision Bank Limited" (website
   not on record), is Vision Bank Limited -- an ADGM Category-1 Islamic bank for corporate
   banking, founded 2022, website vision-bank.com, regulated by the FSRA (confirmed via search,
   2026-09-25). Andre's brief lists "Vision Bank" among the Saudi digital banks -- that is a
   different, unrelated bank: Saudi Arabia's SAMA-licensed digital consumer bank (formerly
   "Saudi Digital Bank"), website visionbank.com.sa, which received SAMA's non-objection to launch
   in 2024. The Saudi entity does not appear to be in the CRM at all under Saudi Arabia. Neither
   entity's site was checked for a procurement page this session -- flagged as an open item, not
   assumed.
2. "Dhabi LTD" (CRM UAE row, website recorded as https://www.dhabi.com) -- the domain does
   not resolve (getaddrinfo ENOTFOUND www.dhabi.com, tested 2026-09-25, both via curl and via
   an independent fetch tool). Unknown what this entity actually is or whether the recorded website
   is simply wrong. Flagged as a CRM data-quality issue, not resolved here.

## One trigger worth surfacing, unrelated to the RFP-watch question

EZ Bank (CRM Saudi row, website recorded as SAMA's own site -- reasonable for now, see below) is
a brand-new entity: SAMA announced its licensing as a new Saudi digital bank in late September
2025, a joint venture between Ajlan & Bros Holding Group and Qatar National Bank, with SAR 2.5bn
capital (sources: SAMA newsroom, Argaam, FinTech Futures -- all dated September 2025). A bank this
new plausibly has no public website yet at all, which is why the CRM's placeholder (SAMA's page) is
not obviously wrong -- but it also means EZ Bank is, by definition, still choosing its core
systems. Worth a dedicated look outside this RFP-watch exercise; not something a procurement page
would show yet regardless.

## Recommendation

Realistic coverage of "never miss a bank RFP" via bank-run procurement pages: effectively zero
today, for UAE and Saudi Arabia specifically:

- 0 of 71 banks expose a live, unauthenticated notice list.
- 12 of 71 run a real e-sourcing/procurement platform where a login would unlock more (ranked
  table above) -- the practical implication is that the only way to ever see a live notice on one
  of these is to hold or obtain a supplier account, which is a registration decision for Andre,
  not a watch mechanism.
- ~14 of 71 confirmed to have no such page at all, by direct search and path-probing.
- ~45 of 71 were not checked individually (foreign branches/private banks); the pattern
  observed everywhere else strongly suggests the same "no local page" result, but this is not
  independently confirmed for each name.

Conclusion for Andre: a bank-website-watch cannot be the mechanism for "never miss a bank RFP" in
UAE/KSA. The two live findings that matter more for that goal are (1) the Emirates NBD / DIB
finding that both run the same Jaggaer e-sourcing platform with a nominally public "Find
Opportunities" feature that is actually gated -- worth knowing if OFS ever registers as a supplier
with either, since that one login would then show real live tenders; and (2) the existing
government-portal findings in plan/gulf-rfp-sources.md (ADGPG, Lebanon's PPA) remain the only
actually watchable feeds surveyed to date, and neither is bank-specific. The realistic path to
"never miss a bank RFP" is relationship-driven (a banker or an incumbent-vendor contact tips OFS
off, or OFS proactively registers as a supplier on the handful of live portals identified above),
not a scrapeable public feed.

---

## Orchestrator verification and the decision this forces, 2026-09-25

I re-probed the two banks that looked closest to watchable, with our own honest `USER_AGENT`:

| | |
|---|---|
| `emiratesnbd.bravosolution.com/esop/.../opportunity/current` | **HTTP 412 Precondition Failed** |
| `dib.bravosolution.com/esop/.../opportunity/current` | **HTTP 412 Precondition Failed** |
| Emirates NBD's public supplier-relations page | HTTP 200 — informational only, no notices |

(The sweep reported 401; it is 412. Same conclusion: no session, no access.)

### The answer to "I don't want to miss any RFP from a bank in UAE or KSA"

**There is no scraping route. Zero of 71 banks publish an open notice list.** Every one is a
login-gated e-sourcing platform (Jaggaer/BravoSolution, Oracle iSupplier, SAP Ariba, Coupa), a static
page, or nothing. Both central banks run registration-only supplier portals. Building a monitor
against bank websites would produce a feed that is permanently empty, and — worse — would *look*
like coverage.

**The route is supplier registration, and it is a business decision, not an engineering one.**
Registering OFS as a vendor with Emirates NBD and Dubai Islamic Bank would unlock the "Find
Opportunities" list on the platform they share, which IS then watchable. That is the single
highest-value action available on this question, and only Andre can take it — ⚠ this workspace does
not create accounts or submit registration forms anywhere, by rule.

### What can honestly be promised
- **Watchable today: nothing bank-specific.** The only genuinely readable tender feeds found in any
  of our markets are government portals (Abu Dhabi's ADGPG, Lebanon's PPA), and no commercial bank
  posts to them.
- **Watchable after registration:** whatever ENBD/DIB expose to logged-in suppliers. Unknown until
  someone registers; it may well be substantial.
- **Never watchable:** the rest. A bank that runs a closed vendor portal invites the suppliers it
  already knows. That is reached by being known, not by scraping.

⚠ So "never miss a bank RFP" cannot be delivered by this workspace as an automated guarantee. It can
be delivered as: *be registered where registration is possible, be known where it is not, and watch
the two government feeds for the rare public case.* Saying so plainly is worth more than a monitor
that returns zero every morning and implies we looked everywhere.

### Caught in passing
- **EZ Bank** — a brand-new SAMA-licensed digital bank (Ajlan & Bros / QNB joint venture, announced
  September 2025). A licensed, pre-launch bank is choosing core systems *now*, with no incumbent.
  Recorded as a 20/25 trigger. Its website field also pointed at `sama.gov.sa`, the regulator's own
  site rather than the bank's — removed, as it would have sent outreach to the central bank.
- **Vision Bank** is two unrelated entities — ADGM corporate banking in the UAE (what we hold) and a
  SAMA-licensed digital consumer bank in Saudi Arabia. Flagged on the record.
- **Dhabi Ltd**'s website fails DNS resolution. Flagged, not deleted.
