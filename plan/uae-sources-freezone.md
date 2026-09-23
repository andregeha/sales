# UAE free-zone registries and fund registers -- live investigation

> Investigated **live, 2026-09-23**, from the laptop. Every reachability code, count and field list
> below was measured today by direct HTTP request (curl) or, where noted, by WebFetch -- never
> invented, never carried over from a cached assumption. Where I could not measure something, it
> says **unknown** and says why. No bot protection, rate limit, CAPTCHA or WAF was evaded -- where
> one was hit, it is reported as a finding, not worked around.
>
> Context already in memory before this session: the DFSA firm register (319 firms, `Managing
> Assets` 396/`Single Family Office` 41 withdrawn/`Accepting Deposits` 38/`Fund Administration` 33 --
> see `memory/facts.md`) and the FSRA firm register (497 firms, `POST /api/fsrac/firms/listing/filter`)
> are already built. This investigation is everything else DIFC, ADGM and DMCC publish.

## Summary table

| # | Source | URL | Reachable | Measured count (2026-09-23) | Bulk access | Bot-gated |
|---|---|---|---|---|---|---|
| 1 | DIFC public Company register | difc.com/business/public-register | intermittent (mostly 429) | unknown | No | Yes |
| 2 | DIFC Family Wealth Centre | difc.com/ecosystem/difc-family-wealth-centre | 200 | 0 -- no public list exists | N/A | No |
| 3 | ADGM Registration Authority (company register) | newreg.adgm.com/s/search-results | 200 page, search unusable | unknown | No | Aura session token needed |
| 3b | ADGM Registration Authority (apex domain) | registration.adgm.com | 403 | -- | -- | Yes, Akamai |
| 4a | DFSA Public Register of Funds | dfsa.ae/public-register/funds | 200 | 295 funds | Yes | No |
| 4b | ADGM FSRA fund register | adgm.com/public-registers/fsra/funds | 200 | 340 funds | Yes | No |
| 5 | DMCC business directory | dmcc.ae/business-directory | 200 | unknown, 26000+ is a marketing claim | plausible but prohibited | No |

## 1. DIFC public register / Registrar of Companies

- The domain moved. `difc.ae` now 301-redirects to `difc.com` -- confirmed live 2026-09-23.
- The whole site sits behind Vercel's bot-management challenge. A direct curl GET to the
  domain root, to /business/public-register, and to a /_next/static asset all returned
  HTTP 429 with the response header X-Vercel-Mitigated: challenge and an
  X-Vercel-Challenge-Token -- this is Vercel serving a JS challenge page instead of content, not a
  simple rate limit. Per the rules for this task, we did not attempt to solve or evade it (no
  headless browser, no header/IP rotation). Repeated identical requests, spaced out, got the same
  429 every time.
- WebFetch (a different fetch path) got through to the static shell of some pages -- e.g.
  /business/public-register and /business/registrars-and-commissioners/registrar-of-companies --
  and confirmed the register is a genuine company register distinct from the DFSA's firm
  register: it lists any entity incorporated in DIFC (PLCs, LLCs, partnerships, foundations,
  regulated or not), while the DFSA register is only DFSA-licensed financial-services firms.
  Confirmed live 2026-09-23.
- The actual search/results interface is client-rendered. /business/public-register/public-
  register-details?companyName=slug (the URL pattern for an individual company page, found via a
  Google-indexed example, rira-gallery) returned only the site's navigation shell with no company
  data through either curl or WebFetch -- the register looks up and injects data via JavaScript after
  load, and we have no way to execute that JS. No underlying JSON API endpoint was found despite
  checking robots.txt (which explicitly disallows crawling /api/ and /ajax/ -- so DIFC does
  publish API paths under those prefixes, but we did not enumerate or call them, both because the
  robots.txt disallow signals intent and because doing so would mean guessing at a private API
  through a bot-blocked front door).
- Net result: zero DIFC company-register records were read. We could not measure a count, a
  field list, or confirm pagination. This is a hard unknown, not an inferred zero.
- A third-party blog (Founder Connects, undated, not DIFC-published) claims "over 4,300 active
  registered companies." Do not use this number -- DIFC's own 2025 annual-results press release
  (difc.com, published 2026-02-05) states 8,844 active companies at year-end 2025, a materially
  different figure from an authoritative source. Neither figure comes from reading the register
  itself; both are aggregate claims, not a list we can act on.

## 2. DIFC Family Wealth Centre -- the family-office gap

Definitively: no public list, directory or member register exists, and DIFC says so itself.

- The Family Wealth Centre page (difc.com/ecosystem/difc-family-wealth-centre, live 2026-09-23) has
  no searchable directory, no browsable member list, and no per-family or per-office page. It
  offers only an inquiry form to "become a member."
- The DIFC Family Businesses page (difc.com/business/establish-a-business/family-businesses, live
  2026-09-23) is explicit: family arrangements are recorded on "a private register, which is
  contained on an independent server." That is DIFC's own wording for why this is not public -- it
  is a deliberate design choice, not a gap we can close by looking harder.
- The Centre does publish one people-list: an 8-person "Expert Advisory Council" (David Russell
  AM RFD KC, Chair; Alastair Glover; Dominique Leimer; Ismael Hajjar; Izabella Szadkowska; Mazy
  Moghadam; Pankaj Nagrath; Imad Khalife, Secretary), at
  difc.com/ecosystem/difc-family-wealth-centre/the-expert-advisory-council, live 2026-09-23. No
  firm affiliations are given on the page, and -- importantly -- these are advisors to the Centre
  (legal/financial/governance experts), not family-office principals. Not a lead source; noted for
  completeness only. Do not infer anyone's role or pronouns from this list.
- DIFC's own 2025 annual-results release (published 2026-02-05) puts scale numbers on the
  ecosystem without naming anyone: 1,289 family-related entities (new in that release, tied to a
  new "Strategic Advisory Committee"), 1,115 foundations (+66% YoY), and 500+ wealth and asset
  management companies (+22% in 2025). These are DIFC's own aggregate marketing figures -- good for
  sizing the opportunity in a deck, not a source of a single named prospect.
- Conclusion for the UAE family-office gap (0 records today): this specific gap cannot be closed
  from any DIFC-published source. The path that can close it is the one already in
  memory/facts.md -- the DFSA's "Single Family Office" service category is now all withdrawn, and
  no substitute public list has replaced it. Recommend: treat DIFC/UAE family offices as structurally
  invisible (matches the existing note in memory/facts.md that SFOs are exempt by design above a
  $50m/$10m threshold in DIFC/ADGM respectively) and redirect effort in this segment toward events,
  intermediary relationships (private banks, MFOs, law firms who serve them) and France's AFFO, which
  is the one segment source that actually works.

## 3. ADGM Registration Authority -- the company register

Two different domains, two different outcomes:

- registration.adgm.com -- outright blocked. A single GET returned HTTP 403 from an Akamai
  edge (Akamai-GRN header present). No content of any kind was served. This looks like a
  bot-management product blocking non-browser clients categorically, not a rate limit -- we made one
  request and stopped.
- newreg.adgm.com/s/search-results -- reachable but unreadable. This URL, surfaced by DIFC/ADGM
  guidance and third-party guides as "the" public-register search, returns HTTP 200 but is a
  Salesforce Lightning Experience / Aura application (auraFW, aura_prod.js, per-session
  fwuid tokens). Aura issues its data calls only after executing a JS bootstrap sequence that mints
  a session-bound action-signing context in the browser; there is no static endpoint to call. We
  fetched the raw HTML (confirmed via curl, not just WebFetch) and it is genuinely empty of company
  data -- a "Sorry to interrupt / CSS Error" shell, consistent with a client that only ever renders
  after live JS execution. We did not attempt to reverse-engineer or replay Aura's signed action
  protocol -- that would mean executing untrusted JS or hand-minting session tokens, which is
  materially different from reading a documented AJAX GET/POST and crosses into the kind of evasion
  this task rules out.
- The ADGM public-registers landing page (adgm.com/public-registers, live 2026-09-23, read via
  WebFetch) confirms the company register sits alongside four other named registers: the FSRA
  Financial Services Firms Register (already built), an Audit Register, an Authorised
  Individuals Register, and a Professional Services Providers Directory -- none of these last
  three were investigated further; they are out of scope for this task (not company or fund
  registers) but are worth a line in memory/open-questions.md if we ever want CSP/audit-firm leads.
- Net result: the ADGM non-financial company register is unread, and -- on the evidence gathered --
  not readable without running a real browser. This is an unknown, with a specific, named
  blocker (Aura session tokens), not a guess.

## 4. Fund registers -- the route from fund to manager

Both fund registers are on the same technical platform as the firm registers already built, and
both are genuinely bulk-readable. This is the strongest new finding of the day.

### 4a. DFSA Public Register of Funds (DIFC-domiciled + Cayman-domiciled funds registered with the DFSA)

- URL: https://www.dfsa.ae/public-register/funds -- live 2026-09-23, HTTP 200.
- Measured count: 295 funds (GET /public-register/funds/getTotal?...&isAjax=true returns
  {"success":true,"total":295}), read the same way the existing DFSA firm connector does -- no CSRF
  token was even required for this particular AJAX call (it worked with the query params alone).
- Listing fields: Name, Reference number (C0000xx format), Fund Type (Registered Fund /
  Sub Fund / External Fund). Filterable by: fund type, jurisdiction (DIFC / Cayman
  Islands), status (Active / Withdrawn / Winding up).
- Detail-page fields (fetched one fund, mena-infrastructure-fund-lp, as a spot check): Legal
  Status, DFSA Reference Number, Address, Telephone, Fax, Date of Incorporation, Appointed Agent,
  Fund Manager (with the manager's own DFSA reference number, e.g. "MENA Infrastructure Fund
  (GP) Ltd - F000314"), Jurisdiction. The fund manager is named on every fund's detail page,
  exactly the route to managers this task was looking for -- and the manager's reference number lets
  it be cross-checked against the firm register directly.
- Two sibling registers on the same tab bar, not previously catalogued: Passported Funds
  (/public-register/passport-funds, measured 149) and a general Individuals register
  (/public-register/individuals, measured 4,088 -- almost certainly too broad/noisy to be a
  segment source, flagged but not investigated further).
- Bulk access: yes, page-by-page exactly like the firm connector (10 rows/page, ~30 pages).

### 4b. ADGM (FSRA) fund register

- URL: https://www.adgm.com/public-registers/fsra/funds -- live 2026-09-23, HTTP 200.
  (adgm.com/public-registers/fsra/cif, the URL named in the task brief, 301-redirects here.)
- The listing table is empty in the raw HTML -- it is populated by a script,
  /js/FSRA/fund-listing.js, which calls a JSON API: POST /api/fsrac/funds/listing/filter,
  the fund-register sibling of the firm-register API already in memory/facts.md.
- Measured count: 340 funds in one request ({"resultsperpage":500,"currentpage":1}, no filters
  needed -- the endpoint's default with no filterType returns every category combined). Broken down
  by the data itself: 279 Active, 60 "Withdrawn", 1 "Withdrawn " (note the trailing-space variant
  -- a data-quality wrinkle to handle if this is ever connectorised), and by type: Qualified Investor
  Fund 213, Exempt Fund 90, Public Fund 8, blank 29.
  Note: this POST call mirrors exactly what the page's own JavaScript does (same as the already-approved
  FSRA firm-register connector, which is also POST) -- no login, no session needed, no CSRF token
  required; it worked from a cold connection.
- Every single record names its Fund Manager in the listing itself -- no detail-page visit
  needed. Among the 279 active funds this is 109 distinct fund-manager names (e.g. "9Unicorns
  Global Capital Management Limited", "Ajeej Capital (DIFC) Limited", "Aliph Capital Limited" --
  sampled, not exhaustive). Fields per record: fundName, referenceNumber (F-0xxx), fundType,
  fundStatus, fundUrl (detail-page slug), fundManager, passportedTo, datePassported,
  dateWithdrawn, homeRegulator, fundCategory. 32 records carry a passportedTo value and 22 a
  homeRegulator value (funds passported out of, or into, ADGM).
- Bulk access: yes, trivially -- one POST, no pagination required in practice (resultsperpage
  up to 500 was accepted and returned everything without truncation).

Why this matters for the family-office/manager gap: neither register lists family offices
directly, but the fund manager names on both registers are a legitimate, low-noise way to surface
asset/fund managers that may not appear, or may appear incompletely, on the firm registers -- worth
cross-referencing the ~109 ADGM fund-manager names and the DFSA funds' named managers against the
existing 319/497 firm-register records to find any that are not yet in the CRM.

## 5. DMCC -- business/member directory and public register

- Reachable, HubSpot-hosted marketing site with two embedded Salesforce "Sites" apps:
  dmcc.ae/business-directory embeds dmccsf.my.salesforce-sites.com/Business_directory_Page, and
  dmcc.ae/public-register embeds dmccsf.my.salesforce-sites.com/DMCCPublicDirectoryPage. Both
  return HTTP 200, live 2026-09-23.
- Searchable by name and licence number (DMCCPublicDirectoryPage exposes plain customerName
  and licenseNumber input fields) -- no sector/category filter was found on either page, so
  "searchable by sector" is no, on the evidence gathered.
- The directory page is built on Salesforce Visualforce Remoting, not a plain REST API: the page
  declares a controller, Business_directory_Controller, with five callable methods --
  fetchActivities, fetchAllCompanies, fetchByAdvSearchValue, fetchByAlphabets,
  fetchBySearchValue -- each requiring a per-page-load CSRF token and a signed JWT
  "authorization" value minted at load time, sent as a POST to /apexremote. The existence of a
  fetchAllCompanies method means bulk access is architecturally plausible -- but invoking it
  correctly means replaying a signed remoting protocol tied to a specific page session, which is a
  materially different and heavier thing than reading a documented GET/AJAX endpoint. Given this
  task's read-only/GET-only brief, we did not attempt to call it, so the actual record count,
  per-record fields and any true page cap remain unknown -- DMCC's own marketing claims "more than
  26,000 businesses," which is unverified and almost certainly includes every category of tenant
  (restaurants, retail, hotels), not just financial/commodity-trading firms as the task hoped.
- The decisive finding is contractual, not technical. dmcc.ae/business-directory (live
  2026-09-23) carries this notice verbatim, under the heading "Safeguarding your details":

  "The DMCC member directory is proprietary information and published with the express consent of
  our member companies. It is expressly forbidden to copy, download, store, reproduce, resell,
  license, distribute, disseminate, transmit or otherwise deal with the DMCC member directory for
  email or telephone marketing. Nor is it permitted to download, copy or reproduce the directory
  for use on your own website, database or products."

  This directly and explicitly bars the two things we would do with it: ingest it into the CRM
  ("your own... database") and use it for outreach ("email or telephone marketing"). Recommend: do
  not build a DMCC connector, regardless of how easy the fetchAllCompanies call turns out to be.
  This should go in memory/decisions.md as a closed question, not just an open one -- the blocker is
  DMCC's terms, not our tooling.

## What this closes and what it doesn't

| Task goal | Outcome |
|---|---|
| DIFC public company register | Not closed. Bot-gated; zero records read; no API found. |
| DIFC family-office gap | Closed -- the answer is "no public source exists." DIFC itself confirms the family register is private, by design. Redirect effort elsewhere (see section 2). |
| ADGM company register | Not closed. One domain outright blocked (403), the other needs a real browser session we do not have. |
| DFSA fund register | Closed and worth building. 295 funds, bulk-readable, same platform as the existing firm connector, names the fund manager per fund. |
| ADGM fund register | Closed and worth building. 340 funds in one request, names the fund manager on every row -- better than DFSA's, since no detail-page visit is needed. |
| DMCC directory | Not closed, and shouldn't be pursued even if it could be -- DMCC's own terms forbid the exact uses (database ingestion, marketing) this repo exists to do. |

## Unknowns (explicit)

1. Whether DIFC's /api/ or /ajax/ paths (referenced only in robots.txt) carry the public
   register data -- not enumerated, both because the front door is bot-gated and because guessing at
   endpoints behind a robots.txt disallow was judged the wrong side of "inspect network requests."
2. The DIFC public company register's true record count, field list and pagination -- no record was
   ever successfully read.
3. The ADGM company register's true record count, field list and search capability -- the page never
   rendered data for us.
4. The DMCC directory's true record count and per-record fields -- fetchAllCompanies was identified
   but not called (see section 5); DMCC's own "26,000+" is an unverified marketing figure covering all
   tenant types, not a measured count of financial-sector members.
5. Whether ADGM's Audit Register, Authorised Individuals Register or Professional Services Providers
   Directory are readable -- out of scope for this task, not investigated.
6. Whether any of the 109 ADGM fund-manager names or the DFSA funds' named managers are net-new
   against the existing 319 DFSA-firm / 497 FSRA-firm CRM records -- not cross-referenced yet.
7. Dubai Pulse (dubaipulse.gov.ae), which hosts a DIFC "Licensed Activities Master" open dataset with
   a documented CSV download and API, was identified via search as a possible sixth route in but
   could not be tested: the laptop's connection to www.dubaipulse.gov.ae (91.73.143.12) timed out on
   every attempt (curl: "Could not connect to server"; WebFetch: ECONNREFUSED). This reads as a
   connectivity/availability problem from our network at the time of testing, not a measurement of
   the dataset -- worth a retry another day before concluding anything about it.

---

## ⚠ Verification pass on the fund registers (orchestrator, 2026-09-23)

The investigation's headline for the ADGM fund register was **"109 distinct managers among the 279
active funds"**, presented as the most actionable new finding. I read the register myself before
building anything on it. The mechanics check out exactly as reported — `POST
/api/fsrac/funds/listing/filter`, `totalItems: 340`, 279 active, 109 distinct `fundManager` values,
and the manager is named on the listing row with no detail fetch needed.

**But 109 is the wrong number to act on. The number that matters is 16** — the managers not already
in the CRM. And that 16 does not survive contact either:

- **Spelling variants inflate it.** `BlackRock Fund Managers Limited` and `Blackrock Fund Managers
  Ltd` are one firm; so are `Chimera Capital Limited` and `Chimera Capital Ltd`. The true count is
  around a dozen.
- **Most of the remainder are not Gulf firms.** Avenue Capital Management II L.P., Blackstone Real
  Estate Advisors L.P., EIG Management Company, Falcon Edge Capital LP, Hollis Park Partners LP,
  McKinley Capital Management LLC — US and offshore managers of ADGM-*domiciled* funds. A fund being
  domiciled in ADGM says where the vehicle is registered, not where the manager buys software. This
  is the same trap as the DIFC representative offices: recognisable names, decisions made elsewhere.

⚠ One caveat in the other direction, worth stating: `itemsPerPage` in the request is **ignored** —
the API returns 10 rows per page whatever you ask for, so anything that reads one page and trusts
`itemsPerPage` will silently see 10 of 340. Page until `len(collected) == totalItems`.

**Conclusion: not worth a register connector.** A dozen mostly-foreign names does not justify a
daily-run source, and creating records from them would put Blackstone in the pipeline again. If it
is read at all it should feed the **candidate queue**, where a human decides. The DFSA fund register
(295 funds) is worth the same check before assuming otherwise.

This is exactly why a measured claim gets re-measured before it becomes code: the mechanics were
right, the conclusion was not.
