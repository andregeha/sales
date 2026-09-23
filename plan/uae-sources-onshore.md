# UAE onshore regulator sources -- live investigation

**Investigated:** 2026-09-23, from Andre's laptop (normal internet, no cloud network-policy block).
**Method:** read-only GET/POST against public endpoints only, polite delays (1.5-2s) between
requests, identified User-Agent (`OFS-Sales-Research/1.0 (contact: andre.geha@omega-financial-solutions.com)`).
No login, no CAPTCHA-solving, no WAF bypass attempted. All counts below are measured on this date,
not estimated.

**Context.** All 567 UAE records currently in the CRM come from DIFC (DFSA) and ADGM (FSRA) -- both
financial *free zones*. UAE **onshore** (mainland) is a genuine blind spot. This note investigates
whether it can be closed, and with what.

---

## Regulatory-change flag: SCA no longer exists as a name

**The Securities and Commodities Authority (SCA) was renamed the Capital Market Authority (CMA) of
the UAE, effective 1 January 2026**, under Federal Decree-Laws No. 32 and 33 of 2025. The new entity
is the SCA's legal successor (same registrations, same mandate, expanded). `sca.gov.ae` now
301-redirects to `www.uaecma.gov.ae`; the page title reads "Capital Market Authority" and the
meta description opens "Capital and Market Authority - UAE." (Verified live, 2026-09-23; corroborated
by law-firm client alerts -- Latham and Watkins, King and Spalding, Dechert, Al Tamimi -- dated Jan-Feb 2026.)

**This is a naming collision we must not blur, on the model of GIMD/AGPM:**
- **"UAE CMA"** (`uaecma.gov.ae`) is the onshore federal capital-markets regulator investigated here.
- **Saudi "CMA"** (`cma.org.sa`) is a completely different regulator, already tracked in our CRM
  under `connector: cma-saudi` (see `knowledge/market/source-coverage.yaml`).
- Any note, CRM field or outreach line that just says "CMA" without a country qualifier is now
  ambiguous. Recommend writing "UAE CMA (formerly SCA)" or "SCA/UAE CMA" in any client-facing or
  internal reference until the rename is common currency.

This belongs in `memory/facts.md` and `memory/open-questions.md` regardless of what happens with the
connector recommendation below -- recorded here so the orchestrator can action it.

---

## Summary ranking

| Rank | Source | Relevant firms (measured) | Reachability | Build effort |
|---|---|---|---|---|
| **1** | **UAE CMA (ex-SCA) -- Licensed Companies open-data register** | **152** (union of 8 fund/asset/advisory activity categories) out of 322 total licensed companies | Fully open, no auth for the register+detail JSON API, no CAPTCHA/WAF seen | **Low** -- one bulk JSON call for the list, one JSON call per firm for full detail (incl. named staff) |
| 2 | CBUAE -- Register of Licensed Financial Institutions | 63 banks (0 asset/fund managers -- wrong instrument for that segment, but closes the "onshore bank" gap noted in `source-coverage.yaml`) | Fully open, no auth, JSON API | Low |
| 3 | UAE CMA -- Local/Passported Mutual Funds registers | 0 currently exposed (see notes -- reachable, returns zero, not a guess) | Open but empty right now | N/A until non-zero |
| -- | Dubai DED / Invest in Dubai / DED eServices | Unknown -- could not reach | **Blocked** -- Akamai WAF, HTTP 403 on the whole app.invest.dubai.ae and eservices.dubaided.gov.ae domains | Not attempted -- would require defeating a WAF, which we do not do |
| -- | UAE Ministry of Economy -- National Economic Register (growth.gov.ae/G2C) | Unknown | Loads (200) but is an OutSystems SPA whose CSP allowlists Google reCAPTCHA -- bot-protected by design | Not attempted |
| -- | Abu Dhabi ADBC (adbc.gov.ae) | Unknown | **Unreachable** -- TCP connection times out (20s), looks decommissioned; ADDED's own site now points to TAMM instead | N/A |
| -- | Abu Dhabi TAMM licence lookup | Unknown | Loads (200), single-record lookup by reference number only (URL path is literally tahaqaq/reference-number), heavy SPA -- not explored further given it is a one-license-at-a-time verifier, not a browsable register | Not attempted |

**Build first: the UAE CMA (ex-SCA) licensed-companies register.** It is the only onshore source that
(a) is directly in our ICP -- Investment Fund Management, Portfolios management, Financial
Consultations, Fund Administration, Custody, Financial advisor/issuance manager, Financial Products
dealer, Profit Sharing Asset Management -- (b) is completely open with no login/CAPTCHA/WAF, and
(c) exposes a bulk JSON export plus a rich per-company detail endpoint (address, phone, email,
external auditor, board of directors, and **named accredited employees with position titles** --
e.g. Fund Investment Manager, Portfolio manager, Head Of Risk Management -- which is exactly
the kind of technical/decision-maker contact our People section needs). See section 1 for full evidence.

---

## 1. UAE CMA (formerly SCA) -- uaecma.gov.ae

**Regulator identity:** Federal capital-markets regulator. Licenses onshore brokers, asset/fund
managers, investment advisers, custodians, fund administrators, crowdfunding platforms, VASPs.
Formerly "Securities and Commodities Authority" (SCA); see rename flag above. **Not** the Saudi CMA.

### 1a. Licensed Companies register (the one to build)

- **Human page:** https://www.uaecma.gov.ae/en/open-data/licensed-companies
- **List/export endpoint (no auth required):**
  POST https://www.uaecma.gov.ae/api/PublicApi/GeIntegrationResult
  Body: {"integrationId":2045,"urlParameters":{"pageIndex":1,"pageSize":1000000,"type":"(activityId or empty)","keyword":"","languageId":1,"languageCode":"en-GB"}}
  - pageSize:1000000 returns the **entire dataset in one call** -- this is literally what the
    site's own "export to Excel" button does. No pagination needed in practice.
  - type filters by activity-category id (see below); empty string returns all.
- **Detail endpoint (no auth required):**
  POST https://www.uaecma.gov.ae/api/PublicApi/GeIntegrationResult
  Body: {"integrationId":2055,"urlParameters":{"companyId":"(code, e.g. CP-0000065)","languageId":1,"languageCode":"en-GB"}}
- **Activity-category list (no auth required):**
  POST .../api/PublicApi/GeIntegrationResult with {"integrationId":2047,"urlParameters":{"languageCode":"en-GB"}}
  -- returns all 59 licensable activities with their ids.

**Reachability:** HTTP 200 on every call made (list, detail, activity list). No CAPTCHA, no WAF
challenge, no session/cookie requirement for these three GeIntegrationResult calls (unlike the
CMS GetContentList endpoint used elsewhere on the same site, which returned 401 without a session
cookie -- see section 1b). Standard IIS/ASP.NET server, normal security headers, nothing exotic.

**Measured counts (2026-09-23):**

| Activity (id) | Firms |
|---|---|
| Total licensed companies, unfiltered | **322** |
| Financial Consultations (16) | 111 |
| Portfolios management (7) | 44 |
| Investment Fund Management (6) | 39 |
| Financial advisor / issuance manager (17) | 24 |
| Fund Administration (8) | 14 |
| Financial Products dealer (5) | 11 |
| Custody (9) | 6 |
| Crowd Funding Platform Operator (43) | 3 |
| Dealing in Virtual Assets as Agent/Matching Principal (59) | 2 |
| Profit Sharing Asset Management (45) | 1 |
| **Union of the 8 asset/fund/advisory categories above** | **152 distinct firms** |

(The other roughly 40 activity categories not listed -- e.g. exchange-membership roles like Market
Maker on Dubai Financial Market PJSC, Derivatives Trading Member -- are brokerage/exchange-
infrastructure roles, out of our ICP, and were not counted into the union.)

**Fields, list endpoint:** code (e.g. CP-0000065), name, status (Active seen; presumably also
carries withdrawn/other values), website, year (licence-issue year). Thin, but enough to know who
exists and filter by activity.

**Fields, detail endpoint (per company, one call each):** CompanyId, CompanyName, CompanyStatus,
City, Email, Telephone, Fax, EstablishedDate, Website, ExternalAuditor, LegalConsultant,
CompanyAddress, POBox, NumberOfBranches, full LicenseActivities array (every activity the firm
holds, not just the one it was found under), BoardOfDirectors array (name plus nationality), and
-- the most valuable field for us -- an employees array: named individuals with a PositionName
(e.g. Fund Investment Manager, Portfolio manager, Head Of Risk Management, Financial analyst) and
an AccreditationDate, grouped by the licence category they are accredited under. **No direct
personal email/phone for these named employees** -- only the company-level contact. Sample verified
live: Al Mal Capital PSC (CP-0000065), Dubai -- full profile matches a real, findable Dubai asset
manager.

**Paging / bulk:** Yes -- full bulk dump in one request via pageSize:1000000. Detail requires one
call per firm (322 calls for the full population, 152 for our relevant subset) -- same shape as the
existing DFSA/FSRA connectors, entirely feasible at a polite rate.

**Bot protection:** None observed on any of the three endpoints used. No CAPTCHA, no
Cloudflare/Akamai challenge, no rate-limit response across roughly 20 requests at 1.5-2s spacing.

### 1b. Local / Passported Mutual Funds registers -- reachable, but empty right now

- **Local funds page:** https://www.uaecma.gov.ae/en/open-data/mutual-funds/local-funds
  (content type id 1036) -- table columns are just #, Fund Name, Offering Type.
- **Passported funds page:** https://www.uaecma.gov.ae/en/open-data/mutual-funds/passporting
  (content type id 1037) -- columns Ref. No., Fund Name, Fund Domicile, Offering Type,
  Registration. (This is the register the 2018-19 SCA/DFSA/FSRA fund-passporting agreement created --
  the mechanism by which a DIFC- or ADGM-domiciled fund gets promoted onshore.)
- **Endpoint:** POST https://www.uaecma.gov.ae/api/PublicApi/GetContentList -- unlike the register
  endpoints above, this one returns HTTP 401 Authorization has been denied without a session. It
  works (HTTP 200) once the ASP.NET_SessionId and __RequestVerificationToken cookies from a prior
  GET of the page are attached -- this is ordinary ASP.NET antiforgery behaviour, not a CAPTCHA or a
  WAF, and required no login or credential.
- **Measured result, both pages, replicating the exact request the page's own JS makes:**
  code 200, records 0, totalPages 0, contents empty -- **zero items**, on both the local-funds and
  the passported-funds listing, as of 2026-09-23.
- **This is reported as a real measurement, not inferred.** It might mean the register is genuinely
  empty at present, or that content has not been migrated into this typeId since the SCA-to-CMA
  platform rebuild. We could not determine which from the outside. **Unknown -- flagged, not
  guessed.** Worth a follow-up check in a few weeks now that the rename/rebuild has landed.

### 1c. Other UAE-CMA open-data pages noted but not built out here

licensed-company-details (the detail page UI, feeds off 1a's endpoint), financial-auditors-for-pjscs-and-mutual-funds,
appraisers-of-in-kind-for-public-joint-stock-companies-and-investment-funds,
organizer-of-general-assemblies-of-public-joint-stock-companies, and a numbers/statistics dashboard
(the-number-of-licensed-companies, licensed-companies-by-emirate, licensed-companies-by-classification)
that renders via chart widgets we did not decode -- the underlying register in section 1a is
authoritative and sufficient; the dashboard would only be useful for a total-count sanity check,
which we already have directly from the register itself (322).

---

## 2. CBUAE -- Central Bank of the UAE -- centralbank.ae

**Regulator identity:** Licenses onshore banks, finance companies, exchange houses, payment-service
providers and (new, under recent payment-token rules) some virtual-asset/payment-token activities.
Domain is Cloudflare-fronted; robots.txt does not exist (404, cached).

- **Human page:** https://centralbank.ae/en/licensing/ (the actual register widget lives here, not
  on /en/register, which is a different, empty page despite the friendlier URL).
- **Endpoint (no auth required):**
  GET https://centralbank.ae/umbraco/api/CBuaeregister/Get?language=en&ContentId=10202&institutionName=&liceseType=&headOffice=
  (Umbraco CMS backend; note the API's own typo, liceseType not licenseType -- confirmed live, not
  assumed from documentation.)
- **Reachability:** HTTP 200, plain JSON, no CAPTCHA, no WAF challenge.
- **Measured count (2026-09-23): 267 licensed institutions total**, all currently active (there is
  no explicit status field but the endpoint returns exactly what the live public register shows --
  no way to see withdrawn entries from this call).

| Licence type | Count |
|---|---|
| Bank | 63 |
| Exchange Business | 63 |
| Representative Office | 54 |
| Retail Payment Services | 39 |
| Stored Value Facility | 23 |
| Finance Company | 20 |
| Dirham Payment Token Issuance | 3 |
| Payment Token Conversion | 1 |
| Payment Token Custody and Transfer | 1 |

**Relevance to our segments:** the **63 Banks** are onshore commercial/investment banks and directly
close the gap flagged in knowledge/market/source-coverage.yaml (UAE onshore banks are supervised by
the Central Bank of the UAE, which we do not yet read). **No asset-manager, fund-manager or
portfolio-management category exists in this register** -- that activity is licensed by the UAE CMA
(section 1), not CBUAE. Finance Companies, Exchange Businesses and payment-service categories are
adjacent fintech/lending, not core ICP.

**Fields:** InstitutionName, LicenceType, HeadOffice (city only, not a full address),
IdentificationNumber (a structured licence code, e.g. 01.02.01.001.1946.02). **No website, no
email, no phone, no licence date** in this JSON -- thinner than the UAE CMA detail record. CBUAE
also publishes periodic static PDF snapshots (e.g. centralbank.ae/media/415puykl/cb-register-january-2025.pdf,
found via search, HTTP 301 to a valid file) with presumably the same three fields -- the live JSON
endpoint above is current as of today and preferable to any dated PDF.

**Paging / bulk:** The single unfiltered call already returns the full 267-row register -- no
pagination required.

**Bot protection:** None observed.

---

## 3. Mainland company / trade-licence lookups (Ministry of Economy, Dubai DED, Abu Dhabi DED)

None of these could be turned into a "query by activity, get a list" instrument -- every one we
could reach is a one-license-at-a-time verifier by design, and two of the three domains actively
block automated access.

| Portal | URL | Result |
|---|---|---|
| Invest in Dubai (Dubai DED) | app.invest.dubai.ae/search-license | **Blocked.** HTTP 403 Access Denied from an Akamai edge (errors.edgesuite.net) on **every** path tried, including the bare domain root. This is WAF/bot-management, and per instructions we stopped rather than work around it. |
| Dubai DED eServices | eservices.dubaided.gov.ae | **Blocked.** Same Akamai 403 on the domain root. |
| UAE Ministry of Economy, National Economic Register (Growth) | growth.gov.ae/G2C | Loads (HTTP 200), but is an OutSystems single-page app whose Content-Security-Policy explicitly allowlists google.com/recaptcha -- i.e. the search interaction is designed to sit behind reCAPTCHA. We did not attempt to solve or bypass it, per instructions. Also, per u.ae's own description of this tool and the sibling Abu Dhabi tool's URL pattern (tahaqaq/reference-number), these are built to **verify a licence you already have a name/number for**, not to browse a population by activity -- even fully open, this would not give us an enumerable list the way DFSA/FSRA/CMA registers do. |
| Abu Dhabi Business Center (ADBC) | adbc.gov.ae/CitizenAccess/CustomPage/LicenseDetails.aspx | **Unreachable.** TCP connection times out after 20s (not a WAF response -- no response at all). ADDED's own current website no longer links to ADBC and instead points every service to TAMM, consistent with ADBC being a decommissioned legacy system. |
| Abu Dhabi TAMM, licence enquiry | tamm.abudhabi/wb/ded/tahaqaq/reference-number | Loads (HTTP 200), heavy Angular/React-style SPA shell (85KB, no server-rendered content). URL path confirms it is a reference-number verifier, not a name/activity search. Not explored further -- even if reachable, it is the wrong instrument (one-record lookup, not a register). |
| Sharjah SEDD, Ajman DED | eservices.sedd.ae, eservices.ajmanded.ae | Named by u.ae as the equivalent portals for those emirates; **not tested live** -- out of scope once the pattern (single-licence verifiers, several behind WAFs) was established for the two largest emirates. |

**Conclusion for this whole category:** none of it is a source of new leads. At best (if unblocked)
these are a way to *confirm* a company we already found elsewhere actually holds a mainland trade
licence -- not a way to discover companies we do not know about. We should not spend more effort
here until/unless a specific need for licence verification (not lead discovery) arises.

---

## Recommendation

**Build the UAE CMA (ex-SCA) licensed-companies connector first**, modelled directly on the existing
dfsa_difc.py / fsra_adgm.py connectors:
1. Bulk-pull the full 322-row list once (integrationId 2045, pageSize 1000000, no type filter).
2. Keep only the rows whose licence activities intersect our 8 relevant categories (152 firms) -- or
   simply fetch the detail record for every one of the 322 and let LicenseActivities in the detail
   response do the filtering with full fidelity, since that field lists *all* activities a firm
   holds, not just the one used to find it.
3. Enrich each kept firm from the detail endpoint: address, phone, email, website, established date,
   external auditor, board, and named accredited staff with position titles -- several of these
   (Portfolio manager, Fund Investment Manager, Head of Risk Management) are exactly the technical
   evaluators/decision-makers our People sections need.
4. Log the source in knowledge/market/source-coverage.yaml as kind: register, connector: cma-uae
   (recommended name) -- but note prominently in the connector's own docstring that it must never
   be confused with cma-saudi (Saudi CMA is a different regulator entirely).

**Second priority: CBUAE.** Trivial to build (one unfiltered call, 267 rows, no auth), and it closes
the UAE-onshore-bank gap explicitly called out as open in source-coverage.yaml. Lower priority than
number one only because none of its licence categories overlap our highest-value segments (asset/fund
managers) -- it feeds bank only.

**Do not build a UAE DED/Ministry of Economy connector now.** Two of three are WAF-blocked outright,
the third is architecturally a one-at-a-time verifier behind reCAPTCHA and would not enumerate a
population even if it were not.

---

## Unknowns (explicit)

- Whether the UAE CMA's local-funds and passported-funds registers (section 1b) are genuinely empty
  right now, or mid-migration after the SCA-to-CMA platform rebuild. Not established either way.
- Whether the UAE CMA status field on the list endpoint ever shows anything other than Active
  (e.g. withdrawn/suspended) -- only active-looking entries were seen in the samples pulled.
- Whether CBUAE's register endpoint has an equivalent withdrawn history, or only ever shows
  currently-licensed institutions.
- Whether Sharjah's SEDD and Ajman's DED eServices portals are reachable or WAF-blocked like Dubai's --
  not tested.
- Whether Abu Dhabi's TAMM has any non-reference-number way to browse licensed companies by
  activity -- not established; the one page found is explicitly a reference-number verifier, but
  TAMM is a large omnibus portal and other paths were not explored.
- Exact reconciliation between the UAE CMA's live register total (322, measured) and any headline
  figure the site's own statistics dashboard might show -- the dashboard renders via chart widgets
  we did not decode, so no second figure was actually obtained to compare against.
