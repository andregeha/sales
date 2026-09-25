# Gulf RFP/tender sources — live-probed 2026-09-25

> Owner: sales research, for Andre Geha. Companion to `knowledge/market/rfp-sources.md` (France +
> multilateral, compiled 2026-09-22) and `plan/source-architecture.md` section 4 (Tier 4). This file
> covers only the gap those left: **UAE, Saudi Arabia, Lebanon** tender/procurement sources.
>
> **Method:** every row below was fetched live today with `curl`, an honest identifying User-Agent
> (`OFS-SalesResearch/1.0`), GET/POST only, no forms submitted, no accounts created, no bot
> protection defeated. Where a page is a JS app, the underlying data call was found by reading the
> page's own JS and called directly with the page's own Referer -- a normal origin check, not a
> bypass. Every count is a measurement taken today; it will drift. No connector was built and
> nothing was written to `crm/`, per the brief.

## Ranked table

| Rank | Source | Market | Reachable, no login | Real API found | Category coverage | Measured today (2026-09-25) |
|---|---|---|---|---|---|---|
| 1 | ADGPG -- Abu Dhabi Government Procurement Gateway | UAE (Abu Dhabi) | Yes | Yes -- plain JSON, POST, no auth | Financial and Insurance Services is a real filterable category (ID 84000000) | 140 open tenders total, 0 in Financial and Insurance Services, 5 in IT (none relevant) |
| 2 | PPA -- Lebanon Public Procurement Authority | Lebanon | Yes | Yes -- JSON-wrapped HTML, GET, no auth | "Banking and Financial Services" is a real filterable category (ID 2); Banque du Liban is a registered buyer (ID 199) | 30 active tenders, 90 auctions, 878 awarded, 3 Banque-du-Liban records total (2 non-relevant, 1 historical IT/licensing support agreement awarded 2025-06-20) |
| 3 | UAE Ministry of Finance -- Current Business Opportunities | UAE (federal) | Page loads | Partial -- listing is populated by a nonce'd WordPress admin-ajax call, not a stable standalone endpoint | Unknown -- page text confirms "RFQs from MoF entities" but no financial-sector RFQ was visible | Static shell only in this fetch; a prior live-browser check (2026-09-22) measured 9 open tenders, none relevant |
| 4 | Dubai eSupply (JAGGAER) | UAE (Dubai) | Blocked | Guest endpoint exists but the app runs a browser-sniffing redirect against any non-mainstream UA | Unknown | Blocked, not zero |
| 5 | Etimad | Saudi Arabia | Blocked | The visitor tender list re-serves the F5 TSPD bot challenge on every path tried | Unknown | Blocked, not zero -- reconfirms the 2026-09-22 finding |
| 6 | Central Bank of the UAE -- e-Procurement | UAE | Login-gated | Redirects straight to login.php | Unknown | No public listing exists to measure |
| 7 | SAMA -- Suppliers Management Portal | Saudi Arabia | Page loads | No -- plain SharePoint informational page, zero open-tender rows, zero mentions of "tender"/"procurement" in body text | Unknown | 0 visible (page carries no listing at all, not a search result) |
| 8 | Saudi/UAE open-data portals (data.gov.sa, open.data.gov.sa) | Saudi | Unknown | Could not connect from this network -- connection failure, not an HTTP block | Unknown | Unmeasured -- genuinely unreached, not a zero |
| 9 | Saudi Exchange (formerly Tadawul) | Saudi | Blocked | 403 on every path, including with a mainstream browser UA -- WAF/geo-block, same symptom as the already-documented cma.gov.sa API block | Unknown | Blocked |
| 10 | DEWA -- tenders and contracts | UAE (Dubai) | Blocked | 403 | Unknown | Blocked |
| 11 | DFM, ADX (exchanges) | UAE | Page loads | No -- homepages carry no "tender"/"procurement"/"supplier" text at all | -- | No procurement board found (weak test: homepage text only) |
| 12 | GOSI, PIF supplier hub | Saudi | Page loads | No -- no tender/RFP/procurement text on the pages checked | -- | Confirms existing "unknown/relationship-gated" read |
| 13 | Aggregators -- GlobalTenders, BidDetail, TendersInfo, MEED Projects, Zawya | All | Page loads | N/A -- paid products | Generic, not finance-specific | Published prices below |

## Per-source notes

### 1 -- ADGPG (build this one first)

- **Landing page:** `https://supplier.adgpg.gov.ae/pages/tender-list.html` -- a plain Alpine.js
  page, no login wall, no CAPTCHA.
- **Real endpoint**, read straight out of the page's own `assets/js/common.store.js`:
  `POST https://www.adgpg.gov.ae/SCAPI/ADGEs/AlMaqtaa/Tender/List`
  body: `status=&offset=0&limit=200&Category=&Entity=&Sorting=&DueDate=&Name=`
  (add `Category=84000000` to filter to "Financial and Insurance Services").
  A `Referer: https://supplier.adgpg.gov.ae/pages/tender-list.html` header is what the page itself
  sends -- satisfying it is a normal origin check, not a bypass.
- **Category list** (`.../Tender/Categories`) and **entity list** (`.../Tender/Entities`) follow the
  same pattern -- both plain GET, no auth. The category list is a UNSPSC-style code set; `84000000`
  = "Financial and Insurance Services", `43000000` = "Information Technology Broadcasting and
  Telecommunications".
- **Measured today:** 140 open tenders total. Filtering to Category `84000000` returns
  `{"TenderList":null,"TenderCount":0}` -- a genuine, dated zero. Filtering to `43000000` (IT)
  returns 5, none relevant (access points, ceiling lights, a drugs-inventory system, campus network
  renewal -- one is literally "RFQ-ITC/T/ITS/1237/26 - PMS for AVM & AFC", where **PMS = Project
  Management Services**, a false-positive class worth remembering, the same trap already logged for
  French "portefeuille").
- **The entity list itself is a live prospecting signal.** It carries a `TenderCount` per buyer.
  Real financial-sector Abu Dhabi buyers *are* registered on this platform, currently at zero or
  near-zero open tenders each: **Department of Finance** (id `211`, 0), **Abu Dhabi Retirement
  Pensions & Benefits Fund** (id `37`, 0), **Abu Dhabi Investment Office** (id `ADIO OU`, showed 4 in
  the entity roster snapshot, but a direct filter by that id returned zero in a follow-up call --
  the discrepancy was not resolved this session). ADIA, ADQ, Mubadala and Musanada are **not** in
  this entity list -- they run procurement outside ADGPG (confirmed by absence, not by a separate
  check of each of their own systems).
- **Why rank it 1:** no login, no bot protection encountered, a real filterable financial-services
  category, a real entity roster that already includes financial-sector buyers, and it is Abu
  Dhabi's actual government-wide procurement gateway, not a scraped mirror.
- **Caveat:** only Abu Dhabi government entities. Dubai, Sharjah and the federal layer are not
  covered by this endpoint.

### 2 -- Lebanon PPA -- reachable and live (this updates knowledge/market/rfp-sources.md)

The existing registry says Lebanon's PPA "could not confirm reachable" as of 2026-09-22. **As of
2026-09-25 it is confirmed live, actively maintained, and richer than a static notice board:**

- `https://www.ppa.gov.lb/ar` returned 1.8MB of server-rendered content with a working keyword
  navigation, a filterable tender table, buyer and category dropdowns, and a 2026 statistics page
  (`/ar/reports/tenders`).
- **Live counts on the homepage** (server-rendered, not JS): 30 active tenders, 90 auctions, 878
  awarded results, 557 "consensual agreement" tenders (Lebanon's negotiated/direct-award route), 144
  amended, 168 not-awarded, 162 cancelled.
- **A real AJAX endpoint**, read out of `assets/js/home.js`:
  `GET https://www.ppa.gov.lb/ar/tender/get-tenders-home/{status}` where `status` is `active`,
  `auction`, `awarded`, `cancelled`, etc. Returns `{"html": "...<table>..."}` -- HTML-in-JSON, GET,
  no auth, no CSRF token required for this route.
- **Category and buyer are both real, filterable fields.** The category dropdown includes a value
  meaning "Banking and Financial Services" (id `2`). The buyer dropdown includes Banque du Liban
  (id `199`) and the Housing Bank (id `198`).
- **Confirmed straight from BDL's own site:** BDL's homepage (`bdl.gov.lb`) links its "Procurement"
  menu item directly to `https://www.ppa.gov.lb/ar/tenders?procuring_entity=199` -- i.e. **Banque du
  Liban itself points suppliers at PPA**, not at any BDL-hosted procurement page (none exists).
- **Measured for BDL specifically, today:** 3 records total under entity 199 -- cleaning services
  (ref SD00767-2026, open), packaging supplies for banknote wrapping (ref SD00768-2026, open), and a
  **"consensual agreement contract to secure support for all operational systems and IT licences for
  Banque du Liban"** -- this one is historical, already awarded 2025-06-20, not a live opportunity,
  but it is direct proof that BDL's own operational/IT-licensing procurement does surface on this
  channel occasionally. Worth a saved search on entity 199, not a standing expectation.
- **A global keyword search endpoint exists** (`GET /ar/search?query=...&searchTable=home`) but
  returned an empty JSON array for every query tried, including generic words the homepage's own
  news feed uses -- it likely needs a session/CSRF context this fetch did not have. **Do not rely on
  it as tested; the status-filtered endpoint above is the reliable one.**
- **Practical monitoring recipe:** poll `get-tenders-home/active` and check for "Banking and
  Financial Services" category rows, and separately watch
  `ppa.gov.lb/ar/tenders?procuring_entity=199` for BDL directly -- both GET, no auth, no bot
  protection encountered.

### 3 -- UAE Ministry of Finance

Loads fine (200, 293KB). The static HTML explicitly states "All tenders & invoices are available
through the Digital Procurement Platform" and the visible RFQ table is a template -- actual rows are
populated by `wp-admin/admin-ajax.php` using a per-page-load nonce, which means it cannot be called
standalone without first loading the page for a fresh token. This is ordinary WordPress behaviour,
not bot protection, but it does mean the source is only "load the page, then read the rendered
table" -- not one stable URL to poll forever. The 2026-09-22 laptop run already did this properly
with a real browser render and measured 9 open tenders, none relevant -- that number stands; this
session did not re-measure it because reproducing a browser render was out of scope for a curl-only
pass.

### 4 -- Dubai eSupply (JAGGAER)

The landing page itself is a thin static shell that JS-redirects to `/etenders/web/index.html` or
`/esupply/web/index.html` depending on path. That page carries a genuine, no-login **guest**
opportunity link: `/esop/guest/go/public/opportunity/current?...&customGuest=etenders`. Following it
(with a cookie jar, so session state was preserved across the two-step navigation) landed on
`/esop/guest/pages/browserNotSupported.jsp` -- the JAGGAER ESM application does User-Agent sniffing
and refuses anything but a small set of recognised browser strings. **We did not spoof a browser
identity to get past this**, per the brief's rule. This is a block, not a zero -- a human opening it
in an actual browser would very likely see the same kind of public guest listing PLACE-style portals
show. Worth a manual check by Andre from a normal browser rather than automation effort.

The same eSupply landing page also surfaced several buyer-run Jaggaer instances worth knowing about
as **direct-relationship targets, not tender feeds**: `esourcing.mubadala.ae` (did not resolve
today -- may be a stale or renamed link), `eprocurement.musanada.com` (200, Abu Dhabi's
shared-services company, not finance), and `proc.buyer.emiratesnbd.uae.app.jaggaer.com` (connection
failed today) -- **Emirates NBD runs its own supplier portal on the same JAGGAER platform**, which is
a relationship lead (a bank that already does structured e-procurement) rather than an RFP source we
can watch.

### 5 -- Etimad

Reconfirms the existing finding exactly. `login.etimad.sa` issued an OIDC `login_required` redirect
for the portal itself, and the dedicated public visitor path,
`tenders.etimad.sa/Tender/AllTendersForVisitor`, served the same F5 TSPD bot-challenge signature
already logged on 2026-09-22. **We do not attempt to defeat this.** No RSS or open-data export was
found anywhere on `etimad.sa`, `mof.gov.sa`, or in search results.

### Central banks, exchanges, SWFs -- mostly non-findings, stated plainly

- **SAMA**'s "Suppliers Management Portal" page is a live SharePoint page with zero mentions of
  "tender" or "procurement" anywhere in its body -- it is a description of how to register as a
  vendor, not a listing. No open-tender board exists at this URL.
- **CBUAE** e-Procurement redirects straight to a login page -- no public listing exists to check.
- **Saudi Exchange** (the renamed Tadawul) returned 403 even with a mainstream browser User-Agent --
  a WAF or geo-block, the same symptom already logged for the Saudi CMA API. Unknown whether this is
  specific to this network (consistent with the already-documented Europe-side block on CMA's Open
  Data API -- see `plan/source-architecture.md`).
- **DEWA**'s tender page also returned 403.
- **DFM and ADX** homepages carry no "tender"/"procurement"/"supplier" text at all (a weak test --
  only the homepage was checked, not a full site crawl) -- no dedicated procurement board was found
  via search either.
- **GOSI and PIF**'s supplier-facing pages carry no tender/RFP text -- consistent with the existing
  registry's read that PIF portfolio-company procurement is relationship/localisation-gated, not
  openly listed.
- **data.gov.sa and open.data.gov.sa** could not be connected to at all today (a connection failure,
  distinct from the 403/bot-challenge blocks above). This is a gap, not a measured absence -- worth
  a retry, ideally from inside Saudi Arabia per the open question already logged about the CMA
  connector.

### Aggregators -- published prices only, nothing estimated

| Aggregator | Published price | What it covers |
|---|---|---|
| GlobalTenders.com | USD 399/month billed monthly, or USD 334/month billed annually (about USD 4,008/year) for "Global Tenders Premium" -- full global database, all countries/sectors | Generic worldwide tenders, not finance-specific; would need in-platform filtering to test for our category, which requires paying first |
| BidDetail.com | Seven published annual tiers: USD 249 (single country) -> USD 495 (single region) -> USD 695 (Global Basic) -> USD 995 (Global Economy) -> USD 1,395 (Global Business) -> USD 1,995 (Global Premium) -> USD 2,495 (Global Corporate, 5 users) | Same shape -- generic global tender mirror |
| TendersInfo.com | Not published. The subscription page offers only a free trial / demo request; no price appears anywhere on it | -- |
| MEED Projects | Not published -- quote-based, "tell us your countries/sectors and we'll call you." (MEED.com's separate news subscription is $175/month, but that is a different product from the project-tracking tool the brief asked about.) | Best-in-class MENA project tracking per its own marketing, but priced only by quote |
| Zawya | No independent tender-subscription product was found. Search results returned only Zawya's own press coverage of Bahrain's government "Tender Board", not a Zawya product -- an ambiguity risk if anyone assumes "Zawya tenders" is a purchasable feed | -- |

## What remains genuinely unknown (not guessed)

- Whether **DFSA (DIFC)** or **FSRA (ADGM)** operate a procurement/tender board at all -- no search
  hit and no page found in this pass either; unchanged from the existing registry's "unknown, not
  closed" position.
- Whether **data.gov.sa** carries an Etimad-adjacent open-data export -- connection failed outright,
  so this is unresolved, not a confirmed absence.
- Whether **Saudi Exchange / DEWA's 403s** are geo-blocks specific to this network or a blanket
  WAF -- unknown; would need testing from a different network (e.g. inside Saudi/UAE) to tell apart.
- Whether **Mubadala's Jaggaer eSourcing instance** exists at a different, current URL -- the one
  found on the Dubai eSupply landing page did not resolve today and may be stale.
- **Sharjah's** procurement portal -- no working domain was found (`shjgov.ae` did not resolve); the
  correct current URL is unknown, not confirmed absent.
- ADGPG's **entity-level tender-count field is not fully reliable** -- Abu Dhabi Investment Office
  showed a nonzero count in the entity roster but a direct filter by that entity id returned zero;
  the discrepancy was not resolved in this session.

## The honest statement on private-sector RFP visibility

**None of this changes the fundamental picture.** Every portal above, working or not, is a
government or quasi-government procurement channel. Our actual buyers -- family offices, MFOs,
private and investment banks, asset and fund managers -- are private firms with no duty to publish
anything, in the UAE, Saudi Arabia, Lebanon, or anywhere else. A PMS/OMS/fund-administration
selection at a private bank or asset manager is run by direct invitation to a shortlist. This session
found zero new public sources for that segment because none exist to find. The one partial exception
uncovered today is the two or three occasions a year a central bank's own IT/licensing procurement
(like BDL's) surfaces on a public register -- real signal, but rare, and about the buyer's
back-office systems in general, not evidence of a portfolio/fund-management RFP specifically. The
realistic route into our actual segment remains what `knowledge/market/rfp-sources.md` already says:
relationships, licensing-signal triggers (new CMI/asset-manager registrations), and local partners --
not a portal, in any of the four markets.

---

*Compiled 2026-09-25 by sales research, for Andre Geha / OFS Business Development. Every count is a
live measurement taken today via curl, not a search-indexed estimate -- see the method note above.
Re-verify before relying on any single figure for an active pursuit; portals in these markets change
endpoints and nonces without notice.*

---

## Orchestrator verification, 2026-09-25 — and a decision not to build yet

I re-probed the two new finds before committing to either.

### ADGPG (Abu Dhabi) — real, open, and NOT yet safely readable
Confirmed with our own honest `USER_AGENT`, no auth, no Referer needed:
`POST https://www.adgpg.gov.ae/SCAPI/ADGEs/AlMaqtaa/Tender/List` → HTTP 200, `TenderCount: 140`,
fields `TenderID / TenderName / TenderNumber / EntityName / BiddingOpenDate / DueDate / entityId`.

⚠ **It returns 10 rows and I could not page it.** Every JSON variant I tried —
`PageNumber/PageSize`, `pageIndex`, `Skip/Take`, `Start/Length` — returned the identical first
`TenderID`. Reading the site's own bundle
(`/-/media/Themes/AlMaqtaa/AlMaqtaa/AlMaqtaa/Scripts/optimized-min.js`) shows the call is
`$.ajax({url: bt, type:"Post", data: n})` — jQuery sends an object **form-encoded**, not as JSON,
which is very likely why every JSON payload was ignored. The minified state variables are visible
(`t`=page, `y`=10, `b`="OPEN", `l`="LAST_CREATED") but the wire field names are not, and I did not
pin them down.

**Decision: do not build it yet.** A connector reading 10 of 140 would report "no financial tenders
in Abu Dhabi" from a 7% sample — which is precisely the UNGM failure this workspace fixed on
2026-09-23, where a partial read was presented as a clean scan. That bug is not worth repeating for
a source whose measured yield in our category is **currently zero**.

**Build it when** the form-encoded contract is pinned down — ideally by watching the real request in
a browser's network tab rather than inferring it from minified source, which is ten minutes of a
human's time against an hour of guessing.

### Value, stated honestly
Even fully read, ADGPG holds **0 finance-adjacent notices of 140 today**, and the buyer roster is
municipalities, transport and education. Its worth is as a **radar** — Abu Dhabi's Department of
Finance, its pension fund and its Investment Office are registered buyers, so a relevant notice
*could* appear — not as a source of volume. That is a reason to build it eventually, not urgently.
