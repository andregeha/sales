# UAE non-register sources: exchanges, associations, commercial data, trade press

> Written 2026-09-23, at Andre's request ("all sources, public or not, price the paid ones").
> Scope: UAE only, our four priority segments (asset and fund managers, family offices and MFOs,
> private and investment banks). Complements `knowledge/market/source-coverage.yaml` and
> `plan/source-architecture.md`, which cover register sources (DFSA, FSRA, SCA/uaecma). This file
> covers everything else: exchange member lists, industry bodies, commercial data vendors, and trade
> press and events.
>
> Method note. Every source below was checked today, either by direct HTTP fetch (curl with a
> browser user-agent, or the WebFetch tool) or by web search where direct fetch was blocked or would
> require an account. No sign-ups, no trials, no payment data entered anywhere. Where a price is not
> published, this file says "not published" rather than estimating one.
>
> Entity-confusion flag, resolved in section B.4: the brief that triggered this investigation
> referred to "the Arab Family Office Association (AFFO)". No organisation under that exact name was
> found. Our existing "AFFO publishes no member directory" fact (plan/source-architecture.md,
> plan/data-and-intake.md, both dated 2026-09-23) is about AFFO = Association Francaise du Family
> Office, a French body (affo.fr) with nothing to do with the UAE or Gulf. The confirmed UAE-specific
> equivalent is the Emirates Family Office Association (EFOA), a different organisation entirely.
> Do not merge these two in any future note.

---

## A. Exchanges and market infrastructure

### A.1 Dubai Financial Market (DFM), brokers directory
- URL: https://www.dfm.ae/members/brokers-directory (ranking page: /members/brokers-ranking)
- What it would add: a list of DFM-licensed brokerage firms, adjacent to but not the same as our
  priority segments (brokers are not asset or fund managers, though some UAE brokerages run an
  asset-management arm under the same group).
- Free / paid / closed: free, public, no login.
- Reachability: the page returns HTTP 200, but the broker list is entirely client-rendered. The
  static HTML contains only a "Fetching Data..." placeholder and ships as a Nuxt.js single-page app.
  Confirmed by a direct curl fetch of the raw HTML: zero broker names appear anywhere in the
  document; the data loads from a JS-invoked API (api2.dfm.ae/...) after the page executes.
- Bot protection: no CAPTCHA/challenge observed on this specific page. The site's CSP does reference
  Google reCAPTCHA elsewhere on the domain, so some DFM pages are protected; this one simply requires
  a JS-executing fetch, not a CAPTCHA-defeating one.
- Verdict: technically obtainable (would need a JS-rendering fetch, still GET-only, still public
  data) but low value for our segments. It is a broker list, not an asset-manager or family-office
  list, and DFSA/FSRA already give us the DIFC/ADGM equivalent with names, licence types, and (for
  FSRA) emails.

### A.2 Abu Dhabi Securities Exchange (ADX), trading members directory
- URL: https://www.adx.ae/en/members-and-participants/members/trading-members-directory
- What it would add: same category as DFM, ADX-listed brokers/trading members, not asset or fund
  managers as such.
- Free / paid / closed: free, public, no login required in principle.
- Reachability, inconsistent and worth flagging: WebFetch (our tool's own fetcher) received HTTP 403
  Forbidden on two separate attempts against two different URL forms. A plain curl request with a
  standard browser user-agent got HTTP 200 both times. The response is a Next.js app behind
  Cloudflare bot management (a __cf_bm cookie is set) with Dynatrace RUM instrumentation; the member
  list itself is not present in the raw HTML (client-rendered, like DFM) - no names found by grepping
  the fetched body.
- Bot protection: yes, Cloudflare bot management is active on this domain and selectively blocked our
  AI-fetch tool while allowing a plain scripted request through. Treat ADX as bot-sensitive: a
  scheduled or automated scrape is more likely to be blocked than a one-off manual check.
- Verdict: same low-value read as DFM, brokers rather than our segments, and effort would go into
  defeating client rendering plus inconsistent bot protection for a list that largely duplicates
  FSRA/ADGM's own register in substance.

### A.3 Nasdaq Dubai, list of members
- URL: https://www.nasdaqdubai.com/members/list-of-members
- What it would add: 25+ named members split into Regular Members (brokers), Market Makers,
  Custodians, and Settlement Banks (equities and derivatives). The custodian and settlement-bank
  categories are the interesting ones here, as these are frequently the same institutions active in
  private banking or fund administration, i.e. adjacent to our segments.
- Free / paid / closed: free, public, no login.
- Reachability: good. Unlike DFM/ADX, member names render in static HTML with a simple filter UI
  (Storyblok-served logos and names, standard img/text tags, no JS execution required to see the
  list).
- Bot protection: none observed.
- Verdict: the one exchange source actually worth a manual pull. Small (dozens, not hundreds) but
  clean, free, and gives us named custodians and settlement banks we would not otherwise see on a
  licence register, since a custodian role is not the same permission as "managing assets".

---

## B. Industry bodies and associations

### B.1 CFA Society Emirates
- What it would add: more than 1,500 investment professionals in the UAE are members, per the
  society's own "who we are" page checked today. These are individuals, not firms, and skew toward
  analysts and portfolio managers rather than principals.
- Directory: the site links a "Member Directory", but it redirects (HTTP 302) straight to
  cfainstitute.org/en/membership/directory, the global CFA Institute member directory, which is
  login-gated (members-only, worldwide, not UAE-specific or publicly browsable).
- Free / paid / closed: membership itself is paid (CFA Institute dues); the directory is closed to
  non-members.
- Verdict: not usable as a sourcing list. Useful only indirectly, as a venue (events, job board) where
  UAE investment professionals can be found named in press coverage of society events.

### B.2 MEIRA (Middle East Investor Relations Association)
- What it would add: MEIRA's members are IR professionals at listed companies, plus a "Service
  Providers / Advisor Partners" page listing named firms, checked directly at meira.me/service-providers/.
  That page lists categories like Financial PR, Corporate Access, Depositary Banks, IR Apps/Terminals,
  Proxy Advisors, and Executive Search, not asset managers or family offices as a category, though two
  firms shown as "Financial Services Providers" (Beltone, Al Ramz) do describe themselves as offering
  asset management alongside other services. MEIRA also just accepted its first buy-side member
  (Mayar Capital), per its own press release, a signal that buy-side/asset-manager membership is new
  and still thin.
- Free / paid / closed: the "About" and "Service Providers" pages are free/public; a "Member Area" is
  password-gated.
- Verdict: low yield for our segments today. It is an issuer-side / IR-industry association, not an
  asset-manager or family-office one. Worth a light annual re-check given the stated intent to grow
  buy-side membership, not worth building anything around now.

### B.3 MENA Private Equity Association (menapea.com)
- What it would add: per search results (not independently fetched today, flagged as
  search-confirmed, not click-verified), the association runs a free public directory of roughly 50+
  VC firms, angel investors, incubators and tech parks, with "more detailed data" behind a paid
  subscription. This is VC/incubator-oriented, adjacent to but not the same as our asset/fund manager
  and family-office segments.
- Free / paid / closed: mixed. A free directory tier exists per search snippets; paid-tier price not
  published.
- Verdict: worth a direct look before building anything (unverified today), but its VC skew makes it a
  secondary source at best for Gaia's target segments.

### B.4 Family-office associations: the AFFO name collision, resolved
- "Arab Family Office Association": no organisation under this exact name was found in today's
  search. This appears to be either a slip conflating the French AFFO with a Gulf body, or a
  reference to something too obscure to surface in general search, flagged as unknown, possibly does
  not exist as a named, distinct entity. Do not assume it exists; do not build against it.
- Emirates Family Office Association (EFOA), the real, confirmed UAE body:
  - Launched at ADGM (Gulf News coverage confirms an ADGM launch event); an independent, not-for-
    profit platform for UAE family offices, per its own site emiratesfoa.com/about.
  - Explicitly, by its own published policy: "does not charge any membership fees... membership is by
    approval only" and operates a "strict no-solicitation policy", i.e. a closed, vetted community,
    not a marketing directory.
  - No public member list found, confirmed absent across its own site and third-party profiles
    (ZoomInfo, D&B, Crunchbase, LinkedIn) checked today; none show a browsable roster.
  - Verdict: same shape as our AFFO (France) finding, a real, credible association that structurally
    will not hand over a member list. The realistic access path, if any, is relationship or
    introduction through its events, not a scrape or a request.
- No other MENA/Gulf private-equity, hedge-fund, or family-office association with a public member
  directory was found in this pass, beyond the PE-council/leadership page noted below.

### B.5 Global Private Capital Association, Middle East Council
- URL: https://www.globalprivatecapital.org/team/mena-council/ (checked directly today)
- What it would add: a small, named, public list of 9 senior individuals at MENA private-capital
  firms: Dr Karim El Solh (Gulf Capital), Taimoor Labib (Affirma Capital), Hoda Abou-Jamra (TVM
  Capital Healthcare Partners), Romen Mathieu (EuroMena Funds), Nabil Triki (SPE Capital Partners),
  Shahm Al-Wir (Foursan Group), Zahid Kamal (Fajr Capital), Sikander Ahmed (Janus Henderson Emerging
  Markets Private Capital), and Aamir Rehan (Humania). This is a leadership council, not a membership
  register, but every name is real, named, titled, and dated (page as checked 2026-09-23).
- Free / paid / closed: free, public, no login.
- Verdict: small but genuinely useful. Nine qualified, named contacts at MENA-focused private-capital
  firms, several UAE-based, with zero cost and zero access friction. Worth adding as individual
  candidate contacts, sourced and dated as such.

---

## C. Commercial data providers

For each: UAE / our-segment coverage as we could establish it, free tier, and published price only.

| Provider | UAE / our-segment coverage | Free tier / trial | Price (published only) |
|---|---|---|---|
| Zawya (LSEG) | MENA Company Data / "Find Companies" tool lets you search and build lists of MENA companies; described by LSEG as covering "all major sectors", now folded into LSEG Workspace. Could not confirm from the free-access page whether family offices or asset managers are separately filterable, unknown, would need a logged-in session to check. | Free news content exists (zawya.com articles); the company-data/List Builder tool's access tier is unclear, not confirmed free or gated in this pass. | Not published. LSEG sells this via Workspace bundles negotiated directly; no public price list found. |
| Preqin | Global alternative-assets data (funds, fund managers, LPs incl. family offices); has GCC/MENA coverage as part of its global dataset, exact UAE count unknown without an account. | A free account exists ("Preqin Free Account"); scope of free content unknown, not tested (no sign-up performed per the rules of this task). | Published only via third-party trackers, not Preqin's own price page: roughly US$25,000-$80,000+/year depending on asset-class modules and seats (2026 vendor-cost trackers, Vendr/Costbench). Preqin itself does not publish pricing. |
| With Intelligence | Markets itself as having "the largest" family-office dataset, single- and multi-family offices, globally. UAE-specific coverage not stated on public pages. | Not established, no free tier found. | Not published anywhere found. |
| Bureau van Dijk / Orbis (Moody's) | Global company ownership/financial data; would cover UAE-registered entities generically (a registry-style source, not segment-filtered for asset managers/family offices specifically). | No free tier found. | Not published. Third-party trackers describe tiered/custom annual and monthly plans plus a 20% multi-product discount, but no anchor figure could be confirmed. |
| Crunchbase | Startup/company data; weak fit for regulated asset managers or private family offices (its own listing for "Emirates Family Office Association" turned up in search, sourced from public press, i.e. it is aggregating the same public signals we already have, not exclusive data). | Free basic search exists; Crunchbase Pro is published: $49/month billed annually (about $588/year), $99/month billed monthly (Crunchbase's own site, current as of this search). | Published: about $588/year (Pro individual tier). Team/Enterprise tiers exist but price not published. |
| PitchBook | PE/VC/M&A-oriented; weak fit for family offices and traditional asset managers as a discovery tool (it is a deal database, not a regulatory or wealth database). | No free tier. | Not published by PitchBook. Third-party buyer reports cluster around $15,000-$30,000/year per seat, up to $100,000+ for enterprise multi-seat deals, consistent across four independent trackers checked today, but none of these are PitchBook's own price sheet, so treat as indicative, not authoritative. |
| Refinitiv / LSEG Workspace | Broad financial-markets data platform; MENA Company Data (i.e. Zawya's dataset, see above) is now delivered through Workspace. | No free tier. | Not published by LSEG. Third-party cost trackers cluster around $10,000-$22,000/year per named user for a standard package, materially more for larger/multi-package deployments, again third-party estimates, not LSEG's own list price. |
| S&P Capital IQ (Pro) | Global company financials/ownership; not segment-built for family offices, weak on private/unlisted UAE family offices specifically. | No free tier. | Not published by S&P Global. Procurement-data trackers report actual signed contracts from about $14,800 to $215,000/year (median about $53,000), i.e. highly negotiated, no single number to quote. |
| Wealth-X | Purpose-built HNW/UHNWI intelligence, used by private banks; would plausibly help profile UAE-based principals once named, less useful for discovering unnamed family offices. | No free tier found; a historical (2014, stale, do not use) reference put an annual subscription at about $18,000, noted only to show that no current figure is published, not as a usable price. | Not published; current figure unknown. |
| Campden Wealth | The leading family-office research house (Global Family Office Report series), valuable for market-level insight and benchmarks, not a prospect list. Membership ("Campden Club") is a network of families, not a data product, and by nature will not hand over a directory of family offices to a software vendor. | Individual research reports are sometimes purchasable/available via partner banks (e.g. RBC has hosted a full free PDF of a regional report); membership itself is not a discovery tool. | Not published. And structurally the wrong kind of product for lead-sourcing, see the recommendation below. |
| allfamilyoffices.com / Family Office Database (a smaller commercial data broker, found via search, not affiliated with any of the above) | Sells a UAE-specific product: "171 verified UAE family offices, 501 named decision-maker contacts", delivered as an Excel/CSV download (per the vendor's own marketing copy, found via search). This is the most directly on-target, UAE-specific, segment-matched commercial product found in this whole exercise. | Not established, pricing page not reached in this pass (search-confirmed only). | Not published in the search results retrieved; the vendor's page would need a direct (still read-only, no purchase) check to find a listed price. Flagged for a follow-up look, given how precisely it matches our stated gap (UAE family offices = 0 in our CRM). |
| Praxis Rock | Similarly a boutique LP/investor-intelligence data broker; publishes free-to-browse pages naming "52 family offices in Dubai" / "29 in UAE" with some names and AUM figures visible directly on the page (Dubai Holding, YBA Kanoo, SEED Group, MSA Capital were named in search results), i.e. some UAE family-office names are visible without paying, functioning as a lead-generation teaser for a paid deeper product. | A visible teaser list is free; deeper/full data is paid. | Not published for this specific product; a general market reference elsewhere on the same site cites $10,000-$25,000/year for a comparable subscription tier, not confirmed as Praxis Rock's own UAE-product price, flagged as an adjacent estimate only. |
| FINTRX | Family-office and RIA database; explicitly weak on the Middle East by its own comparison content, MENA/LatAm/Oceania/Africa together are described as about 8% of FINTRX's global coverage, and a third-party comparison states FINTRX's MENA coverage runs at "50-60% of what comparable platforms surface" in the region. | Starting price is stated (third-party, not FINTRX's own page) around $8,000/year, range $5,000-$20,000/year. | Not FINTRX's own published number, but a more concrete range than most peers, and explicitly weak for our region, not recommended for UAE. |
| LinkedIn Sales Navigator | Not a family-office/asset-manager database as such, but the standard route to named individuals at firms we already hold (from registers) or find elsewhere (from this file); already flagged as a pending decision in plan/data-and-intake.md (M6). | Free LinkedIn search exists at reduced depth/volume. | Published, LinkedIn's own pricing page: Core $1,079.88/year, Advanced $1,799.88/year, Advanced Plus custom (enterprise deals reported $11,750-$26,500+/year), checked 2026-09-23. |

On Bureau van Dijk, S&P Capital IQ, PitchBook, Wealth-X, and With Intelligence generally: these are
built for global M&A, credit, or UHNWI research, not for enumerating a specific small country's
licensed-and-unlicensed financial firms. None publishes UAE-segment coverage counts we could verify,
and every price we found was a third-party estimate, not the vendor's own number; a sales call would
be needed to get a real quote, which is out of scope for this investigation.

---

## D. Trade press and event sources

### D.1 AGBI (agbi.com)
- Machine-readable: no RSS/API found via search.
- Reachability: a direct curl fetch with a standard browser user-agent got HTTP 200. Our WebFetch
  tool's own fetcher got HTTP 403 Forbidden on the same URL. This inconsistency is unexplained and
  worth flagging: treat AGBI as reachable by a normal browser/GET, but unreliable via automated
  tooling.
- Paywall: appears open/free based on the successful curl fetch; no paywall banner text was confirmed
  since the content did not render through WebFetch.
- What it adds: a UK/Dubai newsroom covering the Gulf economy and business, a plausible trigger source
  (hires, launches, restructurings) but not a structured company list.

### D.2 Zawya news
- Machine-readable: no API found; same LSEG umbrella as the commercial data product in section C.
- Paywall: free news articles; the data tools are likely gated (see section C).
- What it adds: trigger-style news (licence grants, hires, fund launches), same value class as AGBI.

### D.3 The National / Gulf News (business sections)
- Machine-readable: no structured feed identified in this pass.
- Paywall: free, standard news sites.
- What it adds: general business press, same trigger-style value, lower specialisation than AGBI or
  Zawya for our segments.

### D.4 Citywire Middle East
- Machine-readable: no public API.
- Access: registration is explicitly invitation/nomination-based for fund selectors ("ask someone
  attending to nominate them" or apply to be considered), i.e. genuinely semi-closed, not just a
  free-registration wall.
- What it adds: a free news tier likely exists; the fund-selector database and events layer is gated
  behind vetted registration. If access were obtained, Citywire's stated target audience is explicitly
  "family offices, external asset managers, wealth management firms", i.e. our exact segments, making
  its event/attendee base a strong lead surface if Andre or someone at OFS can get invited. That is a
  relationship question, not a research one.

### D.5 Conference and exhibitor lists (Dubai/Abu Dhabi family-office summits)
- Machine-readable: none found with a public, machine-readable exhibitor or attendee list.
- Events identified: Family Office Summit Dubai (Feb 2026, named participants incl. KCAP Holdings,
  DAWOOD GROUP, Veddis Family Office, Sarasin Family Office, visible in a search snippet, not
  independently fetched), Private Wealth Middle East Forum, Dubai Family Wealth Summit (Nov 2026),
  Middle East Family Office Investment Summit (13th edition, Dec 2026), ADFO Summit.
- Access: exhibitor/speaker lists typically sit behind an event registration form, occasionally a
  downloadable agenda PDF.
- What it adds: confirms the pattern already noted in knowledge/market/landscape.md section 1.2, named
  family-office participants surface through conference marketing pages far more reliably than through
  any register. Each event's own site should be checked individually and dated; this file does not
  certify any specific named firm above as click-verified, only as search-surfaced.

---

## E. Summary table

| Source | Segment fit | Access | Price (published) | Bot-protected? |
|---|---|---|---|---|
| DFM brokers directory | Low (brokers) | Free, JS-rendered | not applicable | No CAPTCHA seen; site uses reCAPTCHA elsewhere |
| ADX trading members | Low (brokers) | Free, JS-rendered | not applicable | Yes, Cloudflare bot mgmt, inconsistent 403s |
| Nasdaq Dubai members | Medium (custodians/settlement banks) | Free, static HTML | not applicable | No |
| CFA Society Emirates | Low (individuals, closed directory) | Directory closed (redirects to gated CFA Institute directory) | not applicable | No |
| MEIRA | Low (issuer IR, not our segments) | Free pages / gated member area | not applicable | No |
| MENA PE Association | Medium-low (VC-skewed) | Free tier + paid tier (unverified today) | Not published | Unknown |
| Emirates Family Office Association | High segment fit, but closed by design | No public directory; approval-only membership | not a data product | No |
| GPCA Middle East Council | High (named individuals) | Free, public | not applicable | No |
| Zawya / LSEG Workspace | Medium-high (if segment-filterable, unconfirmed) | Gated | Not published | Unknown |
| Preqin | Medium-high (global alt-assets, UAE subset) | Free account exists, scope untested | ~$25k-$80k+/yr (third-party estimate) | Unknown |
| With Intelligence | High (family offices specifically) | Gated | Not published | Unknown |
| Bureau van Dijk/Orbis | Low-medium (generic registry data) | Gated | Not published | Unknown |
| Crunchbase Pro | Low (startup-oriented) | Free basic + paid Pro | $588/yr (published) | No |
| PitchBook | Low-medium (deal-oriented) | Gated | Not published (~$15k-$30k/yr est.) | Unknown |
| S&P Capital IQ | Low-medium (generic) | Gated | Not published (~$53k/yr median est.) | Unknown |
| Wealth-X | Medium (individuals, not firm discovery) | Gated | Not published | Unknown |
| Campden Wealth | Low as a lead source (research, not directory) | Reports sometimes free via partners; membership closed | Not published | No |
| allfamilyoffices.com UAE product | High, exact segment/geo match | Paid, direct purchase, no account needed to view marketing page | Not published (needs a direct look) | Unknown |
| Praxis Rock | High (some names free) | Free teaser + paid full data | Not published for this product | Unknown |
| FINTRX | Explicitly weak for MENA | Gated | ~$5k-$20k/yr (third-party) | Unknown |
| LinkedIn Sales Navigator | High (people, not firms) | Free tier + paid | Published: $1,080-$1,800/yr Core/Advanced | No |
| AGBI | Trigger/press value | Free (curl 200; WebFetch tool 403, inconsistent) | not applicable | Possibly, inconsistently |
| Citywire Middle East | High segment match, but semi-closed (invite/nominate) | Gated beyond news | Not published (event-based) | No |
| Conference exhibitor lists | High (names appear opportunistically) | Mostly registration-gated | not applicable | No |

---

## Recommendation

If Andre spends money on exactly one source, it should be a small, UAE-specific family-office data
product, not one of the global platforms (Preqin, PitchBook, S&P Capital IQ, With Intelligence,
Bureau van Dijk).

Reasoning:
- Our own coverage file (knowledge/market/source-coverage.yaml) states plainly: UAE x family office
  equals 0 records, no instrument, by structural design (DIFC moved single-family offices out of the
  DFSA register entirely in 2023). This is the one cell in our whole CRM where "no register can ever
  fix this" is a structural fact, not a gap to close with more crawling.
- Every global commercial platform we priced (Preqin $25k-80k+/yr, PitchBook $15k-30k+/yr, S&P
  Capital IQ about $53k/yr median, With Intelligence and Bureau van Dijk with no published price at
  all) is built for a much bigger job, global PE/credit/M&A research, and none publishes UAE
  family-office coverage counts we could verify. FINTRX, which is at least family-office-focused,
  explicitly says its own MENA coverage is thin (about 8% of its global base, 50-60% of what
  comparable platforms show). Paying five figures a year for a platform that is honest about being
  weak exactly where we are weak is not a good trade.
- The one thing found in this pass that is precisely sized to our actual gap is a boutique,
  UAE-specific product like allfamilyoffices.com's "171 UAE family offices, 501 contacts" Excel/CSV
  download, or the comparable teaser-plus-paid model at Praxis Rock (which already shows some UAE
  family-office names, Dubai Holding, YBA Kanoo, SEED Group, MSA Capital, for free). Neither vendor's
  exact price was found published in this pass; that is the one open item worth a direct (still
  read-only) follow-up look before any decision.
- Roughly what it would cost: based on the general pattern these boutique family-office data brokers
  follow elsewhere (one-off dataset purchases, not annual platform subscriptions), expect a
  low-four-to-low-five-figure one-time purchase, not a five-figure-a-year platform contract. This is a
  pattern inference from adjacent products, not a confirmed price for this specific product, and
  should not be treated as one.
- What it would give us that free sources cannot: a named, structured list of roughly 170 UAE family
  offices with roughly 500 contacts, in a format that drops straight into the CRM, closing exactly the
  cell that our registers structurally cannot reach, at a fraction of the cost and complexity of a
  global platform subscription built for a different job entirely.

Honest caveat, stated as plainly as the rest of this file: no price for that specific product was
found published today, its methodology and freshness are unverified, and a boutique data broker's
"501 verified contacts" claim should be treated as a marketing claim until sampled and checked against
our own registers. Some overlap with existing DFSA/FSRA MFO records should be expected and is not a
sign of a bad purchase. It is the best-targeted option found, not a verified one.

If Andre is asking whether any of the big-name platforms (Preqin, PitchBook, S&P Capital IQ,
Refinitiv/LSEG Workspace, Bureau van Dijk, With Intelligence, Wealth-X) are worth it purely to find
UAE asset managers and family offices: on today's evidence, no. They are priced for, and built for, a
much larger and more general research job than "find UAE family offices and asset managers", none
publishes the UAE-segment coverage that would justify the price, and our registers (DFSA, FSRA)
already give free, current, structured coverage of the licensed half of our target population (asset
managers, fund managers, MFOs). The only real gap they might close, unlicensed UAE family offices, is
better and far more cheaply addressed by a boutique, UAE-specific product or by relationship access to
EFOA/Citywire ME's events, not by a global data-terminal subscription.

---

## Unknowns (explicit)

- Whether Zawya's free "Find Companies" / List Builder tool is genuinely free or requires a paid
  Workspace login, not established without a logged-in session.
- The exact UAE/GCC record counts inside Preqin, With Intelligence, Bureau van Dijk, PitchBook, S&P
  Capital IQ, and Wealth-X, none publishes this, and none was checked with an account (out of
  scope/against the rules for this task).
- The actual published price of the allfamilyoffices.com UAE product and the Praxis Rock UAE/Dubai
  product, search-confirmed to exist, price not found in this pass, needs one more direct (read-only)
  look at the checkout/pricing page.
- Whether MENA Private Equity Association's free directory is still live and in what format, not
  independently fetched today, search-confirmed only.
- Whether AGBI is genuinely open-access or paywalled beyond a free-article allowance, curl reached it
  (200) but our AI-fetch tool did not (403 twice); the discrepancy itself is unexplained.
- Whether any UAE-specific hedge-fund association (distinct from MEIRA, CFA Society Emirates, MENA PE
  Association) exists, none was found in this pass, but the search was not exhaustive on this specific
  sub-category.
