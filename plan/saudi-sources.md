# Saudi Arabia regulator & registry sources -- live investigation

**Investigated:** 2026-09-24, from Andre's laptop (normal internet).
**Method:** read-only GET only, honest identifying User-Agent
(`OFS-Sales-RegisterConnector/1.0 (Omega Financial Solutions; business development; contact:
andre.geha@omega-financial-solutions.com)`), no login, no CAPTCHA-solving, no WAF/geo-block bypass.
All counts below are **measured live on this date**, not estimated or carried over from memory
unless explicitly marked "prior finding, reconfirmed."

**Context.** Saudi holds 39 CRM records against 810 for the UAE, and Saudi x bank = 0 records with
no instrument at all. This note found the mechanism to close most of that gap.

---

## Headline finding

**The CMA publishes a genuinely open, bulk-downloadable, per-firm Excel workbook that the existing
connector's docstring does not mention and that is a different file from the ones it examined.**
Found by following exactly the method that worked for the UAE -- **sitemap.xml, not the nav menu** --
to `AboutCMA/ResearchAndReports/opendata/Pages/default.aspx`, which links a set of `.xlsx` files.
One of them, **"Institutions under supervision of CMA"**, is a per-firm quarterly workforce/AUM
report covering **~219 named Capital Market Institutions by Arabic and English name** -- roughly
90% of the CMA's declared population of 242 -- with **no authentication, no WAF, no CAPTCHA, and no
JavaScript required.** It is a plain HTTP GET of a static file.

This does not replace the existing `cma_saudi.py` HTML connector -- that one still uniquely provides
per-firm **licensed-activity codes** (MI/MIOF/Arr/Adv/D/C) and register notes for the 36-firm
"recently updated" slice. The Excel workbook instead provides **name-completeness** (219 vs 36) and,
critically, **activity segmentation through which sub-table a firm appears in** (see section 1.2)
plus a genuinely useful **AUM figure per asset manager** -- a scoring signal we don't currently have
for Saudi at all.

Separately, **SAMA's "Licensed Entities" page is also a JS shell wired to a plain, unauthenticated
JSON endpoint** (found by reading its own script, not by guessing) that returns the **full 39
licensed banks** and 91 licensed finance/finance-support companies, each with English/Arabic name,
website, licence number and CR-linked "unified number." This closes the Saudi-bank gap completely.

---

## Summary ranking

| Rank | Source | Firms in our segments (measured) | Reachability | Build effort |
|---|---|---|---|---|
| **1** | **CMA "Institutions under supervision of CMA" quarterly Excel** (opendata section) | **~219 named CMIs** (universe); of which **~122 appear in the AUM/"Managing" table** (asset & fund managers -- our top segment) and **~44 in the custody-AUM table** | Fully open -- plain GET of a static `.xlsx`, HTTP 200, no auth, no WAF, no CAPTCHA | **Low** -- one file download + `openpyxl` parse per quarter |
| **2** | **SAMA Licensed Entities -- `PortalHandler.ashx` JSON API** | **39 banks** (11 local, 24 foreign branches, 4 digital) -- closes the Saudi-bank=0 gap entirely; **91 finance/finance-support companies** (adjacent, not core segment) | Fully open -- plain GET, JSON, no auth, no Referer/Origin check needed | **Low** -- two GET calls, one per tab |
| 3 | CMA Authorised Persons register (existing connector) | 36 of 242 (unchanged, reconfirmed live today) | Open, HTML, no auth | Already built |
| -- | CMA Public Investment Funds register (`Market/imf/Pages/Public_IMF.aspx`) | Unknown -- page is a client-rendered placeholder, page metadata says "last modified 2016," no data or API call visible in static HTML | Loads (200) but empty without executing JS; no API endpoint discoverable from source alone | Not attempted -- would need a browser, which we don't run |
| -- | Saudi Exchange / Tadawul (`saudiexchange.sa`) | Unknown | **Blocked** -- Akamai edge WAF returns HTTP 403 "Access Denied" on **every** path tried, including the homepage and `robots.txt` | Not attempted -- bot protection |
| -- | CMA Open Data API (`opendataapi.cma.gov.sa`) | Unknown (would be 242 if reachable) | **Unreachable** -- TCP connect times out after ~21s (reconfirmed live today); geo-restriction signature, not a rate limit | N/A from Europe -- try from Riyadh/Saudi network |
| -- | `data.gov.sa` (national open-data platform) | Unknown | **Unreachable** -- TCP connect times out on both IPv4 and IPv6 (same signature as the CMA API) | N/A from Europe |
| -- | Ministry of Commerce -- "Inquire about commercial register data" | Unknown | Loads (200) but the search form requires a **Verification Code** (CAPTCHA) before any query runs | Not attempted -- bot/CAPTCHA protection |
| -- | Wathq (`api.wathq.sa`) -- CR lookup API | Unknown | Apigee API gateway; root path returns `ApplicationNotFound` -- requires a registered app/API key, and is a lookup-by-known-CR-number service, not a browsable directory | Not attempted -- access-gated by design |
| -- | CMA Statistical Bulletins / Annual Statistical Appendix (also in the opendata section) | 0 named firms | Open, downloadable `.xlsx`, but every sheet checked is an aggregate time series (industry totals, not per-firm rows) -- confirms, for these specific files, what the existing connector docstring already said; it just doesn't apply to the CMI-report file above | N/A |

**Build first: the CMA "Institutions under supervision of CMA" Excel.** It adds roughly **five times**
as many named Saudi firms as we currently hold from CMA (219 vs 36), sits squarely in our
highest-priority segment (asset & fund managers, via the AUM table), requires no authentication or
workaround of any kind, and is quarterly-refreshed at a fixed URL -- a scheduled re-download and diff
is all a connector needs to do. It should ship *alongside*, not instead of, the existing HTML
connector, since only the HTML page carries per-firm licensed-activity codes.

---

## 1. CMA (`cma.gov.sa`)

### 1.0 How it was found
`https://cma.gov.sa/sitemap.xml` returns HTTP 200 (measured 2026-09-24) and lists 690 URLs invisible
from the site's own navigation, exactly as with the UAE regulator. Filtering the sitemap for
`market|fund|imf|open|data|register` surfaced `AboutCMA/ResearchAndReports/opendata/Pages/default.aspx`
-- the open-data landing page, itself not linked from the main menu structure that the existing
connector's docstring describes checking.

### 1.1 The open-data landing page
- **URL:** `https://cma.gov.sa/AboutCMA/ResearchAndReports/opendata/Pages/default.aspx`
- **Reachability:** HTTP 200, 253,043 bytes (measured 2026-09-24).
- Links ten downloadable `.xlsx` files plus a PDF user manual. Nine of the ten (the Annual
  Statistical Appendix and the seven Statistical Bulletins) were downloaded and opened -- **every
  sheet checked in these nine is an aggregate time series** (industry totals, counts by category,
  aggregated income statements) with no per-firm rows. This matches what the existing connector's
  docstring already concluded about "the CMA's downloadable open-data files."
- The tenth file is different, and was apparently not previously examined:

### 1.2 "Institutions under supervision of CMA" -- the file to build on
- **URL:** `https://cma.gov.sa/AboutCMA/ResearchAndReports/opendata/Documents/CMI%20report/excel/Institutions%20under%20supervision%20of%20CMA.xlsx`
- **Reachability:** HTTP 200, 806,724 bytes, valid `.xlsx` (measured 2026-09-24). No auth, no WAF
  response, no bot-detection page -- a plain static-file GET.
- **Structure:** 17 sheets, bilingual (Arabic sheet/column names, English alongside). Cover sheet
  says "31st Issue -- Second Quarter 2025," but the data columns inside run to Q1 2026 -- an observed
  mismatch between the cover title and the data, not resolved here; treat the *data* as current
  through Q1 2026, not the cover date.
- **Per-firm sheets found, with measured row counts (unique firm names, "Total" rows excluded):**

  | Sheet (English title) | Named firms | What it tells us |
  |---|---:|---|
  | Table 1 -- Indicators of Workforce at Capital Market Institutions | ~219 | The closest thing to the full CMI universe; headcount + Saudization % per quarter, Q4 2017-Q1 2026 |
  | Table 5 -- Capital Adequacy (Dealing, Managing and/or Custody) | ~108 | Firms licensed in one of these three core activities |
  | Table 8 -- AUM per CMI (public/private funds + DPM) | ~122 | Asset & fund managers specifically -- our top segment -- with an actual AUM figure (SAR million) per firm per quarter, a real scoring signal we do not currently have for Saudi |
  | Table 14 -- Number of public/private funds per CMI | ~127 | Corroborates Table 8's population and gives fund counts, not just AUM |
  | Table 15 -- AUM under custodial activity | ~44 | Custodians |
  | Table 6/7 -- Trading values per broker (local / local+foreign) | ~37-38 | Brokers/dealing agents -- adjacent |
  | Table 2 -- Credit rating agencies | small | Not our segment |
  | Table 3 -- Market infrastructure institutions | 3 (Tadawul, Edaa/depository, Muqassa/clearing) | Not our segment, but named exactly |
  | Table 4 -- Fintech companies (sandbox) | dozens | Adjacent, monitor for graduations |

- **Fields available:** Arabic name, English name, a row-order numeric id (not confirmed stable
  across quarterly editions -- would need two editions over time to check), and whichever quarterly
  metric the sheet tracks (headcount, Saudization %, AUM in SAR million, fund count, capital-adequacy
  ratio, or trading value). **No address, phone, email, website, or licence date is published in
  this file** -- for those, the existing HTML register or the per-firm CMA page would still be needed.
- **What names some of these firms are, to ground the count:** SNB Capital, Al Rajhi Capital, Riyad
  Capital, HSBC Saudi Arabia, Jadwa Investment, Alinma Capital -- and, in the capital-adequacy and
  trading tables, international entities with Saudi subsidiaries: Credit Suisse Saudi Arabia,
  Morgan Stanley Saudi Arabia, J.P. Morgan Saudi Arabia, Merrill Lynch KSA, Deutsche Securities
  Saudi Arabia, UBS Saudi Arabia -- confirming this file captures the market's larger players, not
  only small/local ones.

### 1.3 Authorised Persons register (existing connector, reconfirmed)
- **URL:** `https://cma.gov.sa/en/Market/AuthorisedPersons/Pages/default.aspx`
- **Reachability today:** HTTP 200; **36 of a declared 242** (`Count=242` still present in the page),
  unchanged from the existing connector's documented baseline.
- **Arabic-language equivalent tried per this task's instruction:**
  `https://cma.gov.sa/ar/Market/AuthorisedPersons/Pages/default.aspx` returns HTTP 200 but the body
  is the CMA's own WAF rejection page -- "The requested URL was rejected" -- a **soft block that
  returns 200**, exactly the kind of trap the existing connector's docstring already warns about for
  a different URL. Confirmed live 2026-09-24. Per the rules for this task, this is reported and not
  worked around.

### 1.4 CMA Open Data API (existing gap, reconfirmed)
- `https://opendataapi.cma.gov.sa/swagger/index.html` -- TCP connect **times out after ~21 seconds**
  (reconfirmed live 2026-09-24, unchanged from prior finding). This is the backend that would return
  all 242 firms in one call per the existing connector's docstring. Still worth trying from a Saudi
  network or the Riyadh office.

### 1.5 Public Investment Funds register -- new attempt, inconclusive
- **URL:** `https://cma.gov.sa/en/Market/imf/Pages/Public_IMF.aspx` ("Publicly Offered Funds"),
  found via the sitemap alongside a sibling `Market/imf/Pages/default.aspx`.
- **Reachability:** HTTP 200, 151,969 bytes. But the rendered text content is only the page chrome
  (menus, cookie banner, footer) plus a message that reads, translated: "You may be trying to
  access this site from a secure browser on the server. Please enable scripts and reload this page."
  The page's own metadata states it was last modified **09/10/2016**.
- No `data-id` cards (unlike the Authorised Persons page, which embeds its data server-side despite
  needing JS for pagination) and no API endpoint visible anywhere in the static HTML or its linked
  scripts. This looks like either a genuinely stale/abandoned page or a client-side widget whose data
  call cannot be seen without executing JavaScript in a real browser -- which we do not do.
- **Unknown, honestly:** whether a Saudi public-funds register exists at all in a form we could read.
  Not resolved by this investigation; would need a human with a browser's network tab open.

### 1.6 Credit Rating Agencies page -- checked, not pursued
`https://cma.gov.sa/en/Market/AuthorisedPersons/Pages/CRAsCompanies.aspx` returns HTTP 200,
125,171 bytes, no `data-id` cards, no `Count=` marker found. Not investigated further -- credit
rating agencies are not one of our segments.

---

## 2. SAMA -- Saudi Central Bank (`sama.gov.sa`)

### 2.0 The trap: `sitemap.xml` is not real here
`https://www.sama.gov.sa/sitemap.xml` returns **HTTP 200** but is in fact SAMA's own homepage HTML
served as a catch-all fallback for any unrecognised path -- the same "200 for a wrong URL" trap
already known for the CMA's SharePoint. **Do not trust a 200 status alone on this domain; check the
content.** (Same fallback observed for `/robots.txt` and for `/en-US/sitemap.xml`, `/ar-sa/sitemap.xml`.)

### 2.1 Licensed Entities page -- a JS shell, but a fully open API behind it
- **Human page:** `https://www.sama.gov.sa/en-US/supervision/licenseentities/pages/default.aspx`
  (Banks tab) and `.../pages/FinanceLicencedEntities.aspx` (Non-Banks tab).
- **Reachability:** HTTP 200, but the page body is an empty SharePoint/SPA shell -- no bank names are
  server-rendered. It loads `/_layouts/15/SAMA.Portal/assets/js/licensedentities.js`, which calls a
  generic data-loading function (`LoadData`, in `utils.js`) against:
  `GET https://www.sama.gov.sa/_LAYOUTS/15/SAMA.Portal/PortalHandler.ashx?op=LoadItems&listUrl=<listUrl>&viewName=Archive`
- **`listUrl` values, read directly from each page's own `data-list` HTML attribute (not guessed):**
  - Banks: `/ar-sa/Supervision/LicenseEntities/Lists/LicensedBanks`
  - Non-banks: `/ar-sa/Supervision/LicenseEntities/Lists/LicensedFinance`
- **Verified live 2026-09-24:** both calls return **HTTP 200 JSON**, no authentication, no
  Referer/Origin check needed (unlike the UAE CMA API, a plain honest User-Agent alone is sufficient
  here), no pagination parameters required -- the full list comes back in one call.

- **Measured counts and fields:**

  | List | Count | Breakdown | Fields per record |
  |---|---:|---|---|
  | Licensed Banks | **39** | 11 Local Banks, 24 Foreign Bank Branches, 4 Digital Banks | Arabic name, English name, Arabic website URL, English website URL, activity type (AR/EN), category (AR/EN), licensing number, "unified number" (CR-linked), a `Created` date (record-creation date in the CMS -- not confirmed to be the licence date, do not treat it as one) |
  | Licensed Finance / Finance-Support Companies | **91** | 78 "Finance Companies," 13 "Finance Support Companies" | Same field set, plus a free-text `SubCategories`/`SubCategoriesEn` listing which finance activities each firm holds (e.g. "Finance lease, Consumer finance, SME's Finance") |

- **This closes the Saudi-bank=0 gap completely** -- SAMA licenses all 39 Saudi banks and there is no
  larger population to be missing. The 39 figure also matches the pre-existing secondary-source
  estimate in `knowledge/market/landscape.md` (Wikipedia/press, 2025/2026) -- now upgraded from an
  estimate to a directly regulator-published, machine-readable list.
- **Finance companies are adjacent, not core** per the existing market landscape note (consumer/SME
  lending, not asset management) -- the 91 figure is higher than the previously recorded "71 as of
  April 2026" press figure, most likely because it includes the 13 "Finance Support Companies"
  sub-category and/or newer licences; not reconciled further here.

### 2.2 Other SAMA pages tried
- `https://www.sama.gov.sa/en-US/Regulatory%20Sandbox/pages/permitted-fintechs.aspx` (the URL on
  record in `knowledge/market/landscape.md`) now returns the **same generic-homepage fallback**
  described in section 2.0 -- the path appears to have moved or been retired since that note was
  written. Not chased further, as sandbox fintechs are adjacent, not core.

---

## 3. Tadawul / Saudi Exchange (`saudiexchange.sa`)

**Blocked outright.** Every path tried -- the bare domain, `/wps/portal/tadawul/home`, `/robots.txt`,
`/sitemap.xml` -- returns **HTTP 403 "Access Denied"** from an Akamai edge node
(`errors.edgesuite.net` reference IDs seen in the response body), regardless of path. This is
edge-level bot protection applied to the entire site, not a page-specific rule. Per this task's
rules, this is reported and not investigated further -- no member list, broker list, or listed-company
data could be measured.

---

## 4. Saudi national open-data portal (`data.gov.sa`)

**Unreachable.** `https://data.gov.sa/` and `https://data.gov.sa/en` both fail at the TCP layer --
connection attempts to both the IPv4 (`78.93.109.93`) and IPv6 addresses time out after the full
curl timeout. This is the identical signature already documented for `opendataapi.cma.gov.sa` --
consistent with a geo-restriction on the hosting/CDN layer rather than a site-specific block. Not
measurable from this network; worth trying from a Saudi network or the Riyadh office, same
recommendation as for the CMA API.

---

## 5. Ministry of Commerce / national commercial register

- **`mc.gov.sa`** itself is reachable (HTTP 200/302, has a real sitemap.xml with 700+ URLs -- genuine
  this time, unlike SAMA's fallback).
- Its **"Inquire about commercial register data"** e-service
  (`https://mc.gov.sa/en/eservices/Pages/Commercial-data.aspx`, HTTP 200) is the closest thing to a
  company lookup, but the search form itself states a firm must be found by at least one of:
  commercial activity, commercial entity (name), or city -- and requires solving a **"Verification
  Code"** (CAPTCHA) before any query executes. This is not a browsable or bulk-exportable register;
  per this task's rules, we do not attempt the CAPTCHA, so this source is reported as **gated**, not
  measured.
- **`api.wathq.sa`** (the Ministry of Commerce's separate CR-verification API platform, "Wathq")
  is a live Apigee API gateway (`api.wathq.sa` resolves; the bare root path returns a structured
  `ApplicationNotFound` fault, confirming a real, running gateway that requires a registered
  application/API key to route any request). By design and by its own public positioning, Wathq is a
  lookup-by-known-CR-number verification service, not a searchable directory -- it could not add
  new names even with credentials, only verify names we already have. Not pursued further.
- **Net effect:** no browsable, filterable-by-sector national company register was found. A firm
  must already be named (from CMA, SAMA, press, or an event list) before either of these tools is
  useful.

---

## Unknowns -- explicit

- Whether the CMA's per-firm numeric IDs in the "Institutions under supervision" workbook (section
  1.2) are stable across successive quarterly editions of the same file -- would need two editions
  captured over time to check; not something a single snapshot can establish.
- Why the workbook's cover sheet says "31st Issue -- Second Quarter 2025" while its data columns run
  through Q1 2026 -- observed, not explained.
- Whether the CMA Public Investment Funds register (section 1.5) has any real content behind its
  JavaScript -- the static HTML gives no evidence either way, and the page's own "last modified 2016"
  stamp suggests it may simply be abandoned.
- Why SAMA's finance-company count (91, measured today) differs from the "71 as of April 2026" press
  figure already on record -- not reconciled; could be scope (support companies included/excluded),
  timing, or both.
- Whether `data.gov.sa` and `opendataapi.cma.gov.sa` are reachable from inside Saudi Arabia -- both
  time out identically from Europe; untested from a Saudi network.
- Whether Tadawul's member/broker/custodian data is published anywhere else (e.g., in a CMA table)
  given that `saudiexchange.sa` itself is fully blocked -- not found in this pass.
