# UAE family offices, sourced through families and corporate structures

> Written 2026-09-24, at Andre's request: find UAE family offices by a different route from
> trade press and conference lists (a colleague covers that separately) - through the merchant
> families and their named investment vehicles, GLEIF, and government/official sources.
> Scope: UAE only. Read-only - no writes to crm/, no connector built.
>
> Context this responds to: our UAE family-office count in the CRM is 0, MFO count is 4
> (corecam-family-office-ltd, msm-investment-advisors-difc-limited,
> patrimium-asset-management-difc, the-family-office-company-b-s-c-c-difc-branch - all DFSA/DIFC
> licensed MFOs, unrelated to the merchant-family route below), out of 767 UAE records. No register
> lists single-family offices (memory/facts.md, 2026-09-22: DIFC moved SFOs out of the DFSA regime
> in 2023; ADGM/DIFC exempt SFOs above $10m/$50m net assets from licensing entirely).
>
> **Method note.** Every entity below was checked against at least one of: (a) the family group's
> own website, (b) GLEIF (`api.gleif.org`, free, no auth — legal name, LEI, registered address,
> status), or (c) a named, dated press source. Where the *only* source is a data-aggregator profile
> page (Preqin, Altss, PipelineRoad, SWFInstitute, Crunchbase) that does not itself cite a primary
> source, this is stated explicitly and the entry is marked **aggregator-only, not independently
> verified** — these compile from public signals we could not always retrace, and their "single vs
> multi-family" labelling in particular should be treated as unconfirmed until checked against the
> family's own site.
>
> **GLEIF caveat.** A GLEIF `registration.status` of `LAPSED` means the **LEI registration** lapsed
> (nobody paid the annual renewal) — it does **not** mean the company is defunct. GLEIF carries no
> industry classification, so it confirms a legal entity exists at a given name/address but never
> confirms what it does; that always comes from a second source here.

---

## A. Verified named vehicles

| Entity (exact name) | Family / group | What it actually is | Emirate | Evidence | LEI | Website |
|---|---|---|---|---|---|---|
| **Al Ghurair Investment LLC** | Al Ghurair family — the branch descending from **Abdulla Al Ghurair** (distinct from his brother Saif's branch, see §C below) | Single-family investment holding company; owns Al Ghurair Resources, Al Ghurair Foods, Al Ghurair Construction among 14+ businesses in 8 sectors (per aggregator profiles — not independently confirmed on a primary site, see note) | Dubai (Al Ghurair Center, Muraqqabat, Deira) | GLEIF record; corroborating narrative from [Wikipedia: Al Ghurair Group](https://en.wikipedia.org/wiki/Al_Ghurair_Group), checked 2026-09-24 | `8945003WF54E8AH08I08` | Not confirmed reachable — `alghurairinvest.com` returned HTTP 404 on a direct fetch 2026-09-24. Do not treat this domain as live without re-checking. |
| **Abdulla Ahmed Al Ghurair Investment Co. LLC** | Al Ghurair family (see §C — unclear if this is the same legal entity as the row above under an older name, or a separate one; GLEIF gives it a different LEI and legal name) | Unknown — GLEIF confirms the entity exists; no independent description of its activity was found in this pass | Dubai | GLEIF record only | `8945003W420UYBT8XE71` | Unknown |
| **Abdulla & Hamad Al Ghurair Investment LLC** ("A&H Investment") | Al Ghurair family — a *third*, distinct branch, led by **Abdulla Majed Al Ghurair** (Chairman & Co-Managing Director) and **Hamad Majed Al Ghurair** (Vice Chairman & Co-Managing Director) | Holding company (self-described — its own site does **not** use the words "family office"); 30+ operating companies in manufacturing, FMCG, construction/contracting, logistics, education, hospitality, media; ~AED 1bn turnover, 3,000+ people, per its own site | Dubai | Own site, fetched directly: [ahinvestment.ae](https://www.ahinvestment.ae/), checked 2026-09-24 | Not checked | https://www.ahinvestment.ae/ (live, confirmed 2026-09-24) |
| **Al Majid Investment Co. (L.L.C.)** | Juma Al Majid Holding Group (founder: the late Juma Al Majid) | Single-family investment arm of the Holding Group, founded 1999, "to expand and diversify the group's investments in global equity markets, money market, fixed income, and private equity, as well as in direct equity" (own site's wording) | Dubai | Own site, fetched directly: [al-majid.com/group_businesses/investment-company-uae](http://www.al-majid.com/group_businesses/investment-company-uae), checked 2026-09-24; GLEIF | `549300ZQX9O2YCGSCE59` | https://www.al-majid.com/ |
| **Investment Trading Group LLC ("ITG")** | Al Tayer Group (Chairman: Obaid Al Tayer) | Single-family investment office of Al Tayer Group; per [Clyde & Co's 2024 deal announcement](https://www.clydeco.com/en/about/news/2024/3/clydeco-advises-itg-on-sale-of-shares), ITG sold its 60% stake in a Dubai logistics company in 2024 — a live, active investing vehicle, not a dormant holding shell | Dubai (Garhoud, per search-sourced address — not independently confirmed) | GLEIF (LEI status **ISSUED**, i.e. currently maintained, not lapsed); Clyde & Co press release, checked 2026-09-24 | `2138004OYKF5RZS4A645` | Not found as a standalone site — operates from Al Tayer Group's own site, [altayer.com](https://www.altayer.com/) |
| **Al Habtoor Investment (LLC)** | Al Habtoor Group (founder: Khalaf Ahmad Al Habtoor) | Self-described on its own site as "the international investment arm of the Group"; subsidiary managing a global property portfolio across multiple countries | Dubai | Own site, fetched directly: [alhabtoorinvestment.com](https://www.alhabtoorinvestment.com/), checked 2026-09-24 | No exact-name match found in GLEIF (checked both fulltext and exact-legalname search, 2026-09-24) — two Dubai-registered entities at an "Al Habtoor Motors Bldg" address (**Skylark Investment Limited**, LEI `529900N3HRJFPU3RXD03`, and **Padar Investment Limited**, LEI `529900DW5C0CYIC4BO45`) share the group's building address but neither name was corroborated as an Al Habtoor vehicle by any other source in this pass — flagged, not claimed | https://www.alhabtoorinvestment.com/ (live, confirmed 2026-09-24) |
| **Seddiqi & Sons Investment (L.L.C.)** ("SSI") | Seddiqi Holding (Ahmed Seddiqi family; Chairman Abdul Hamied Seddiqi) | Real-estate/investment arm of Seddiqi Holding since the group's 2007 reorganisation; owns Seddiqi Properties (founded 2016 as SSI's property-management entity) | Dubai | GLEIF; [seddiqiholding.com/about](https://seddiqiholding.com/about) and [seddiqiproperties.com/about-us](https://seddiqiproperties.com/about-us), checked 2026-09-24 | `254900PTK8IBLE2KPN31` | https://seddiqiholding.com/ · https://seddiqiproperties.com/ |
| **Al Ghurair Group — "Family Office"** (internal function, no separate legal name confirmed) | Al Ghurair Group proper (Chairman: Abdul Aziz Al Ghurair — the *other* branch from the Al Ghurair Investment LLC row above) | Explicitly named as a function on the group's own site: "Portfolio investments are managed through the Group's **Family Office** and cover a variety of public and private market investments," alongside separate "strategic" holdings (Mashreq Bank, National Cement Company). Single-family. **Not a separately incorporated, named vehicle** — this is a division, not an entity, so treat it as a description of function, not a company to add to the CRM as its own record | Dubai | Own site, fetched directly: [alghurair.com/business/investments](https://www.alghurair.com/business/investments/), checked 2026-09-24 | n/a (not a distinct legal entity) | https://www.alghurair.com/ |

---

## B. Named vehicles found, but not independently verified beyond an aggregator

These are real signals worth a light follow-up, but every one of them rests on a data-aggregator
profile (Preqin, Altss, PipelineRoad, SWFInstitute, Arabian Business's own company database) that
does not itself cite a primary source, or on a single press mention that names an *individual* who
is titled as chairman of a company we could not otherwise confirm. Do **not** treat the "single vs
multi-family" labels here as settled — aggregators disagree with each other on this point for more
than one entry below.

| Entity (as named) | Family / group | What it is said to be | Emirate | Evidence | Confidence |
|---|---|---|---|---|---|
| **Landmark Family Office** | Landmark Group (Chairman: Micky Jagtiani) | Single-family office reported to manage ~US$5bn of Jagtiani family assets globally | Dubai | The one primary-ish source, [Private Banker International, 2014-04-07](https://www.privatebankerinternational.com/news/landmark-group-chairman-taps-jm-financial-top-executive-to-launch-family-office-070414-4210298/), explicitly says the office was **"yet-to-be-named"** at launch (hiring Sameer Lumba from JM Financial to run it). The name "Landmark Family Office" appears only in later aggregator profiles (Preqin), which do not explain where the name came from. Real family office confirmed to exist since 2014; its name is not confirmed by the family or group directly. | Medium (existence) / Low (the name) |
| **Galadari Investment Office** | Galadari family — the branch controlled by **Rashid AW Galadari** | Single-family investment vehicle, said to hold luxury real estate | Dubai | Arabian Business's own company-profile database only ([arabianbusiness.com/companies/galadari-investment-office-76339](https://www.arabianbusiness.com/companies/galadari-investment-office-76339)), checked via search snippet, not independently fetched | Low |
| **Ilyas & Mustafa Galadari Group** | Galadari family — a different branch from the row above | Family-owned conglomerate across real estate, trading, manufacturing, transportation; Preqin profiles it as a family office | Dubai | Preqin and Altss aggregator profiles only | Low |
| **AWGAL Investments** | Galadari family — run by **Abdulwahab Ilyas Galadari**, a third branch | Investment vehicle | Dubai | Single search-result mention, not independently fetched | Very low |
| **Sharaf HQ Investment** | Sharaf Group — led by **Yasser Sharaf** | Family business entity established May 2014, spanning retail, automotive services, hospitality, spa/leisure, IT consultancy, media production | Dubai | Its own [LinkedIn company page](https://www.linkedin.com/company/sharaf-hq-investment) — a company-controlled but not a primary corporate website | Low-medium |
| **Sharaf Investment (L.L.C.)** | Sharaf Group | Investment entity — relationship to Sharaf HQ Investment above (same thing, or a separate entity) is unclear | Dubai | Dun & Bradstreet company-profile listing only | Low |
| **Sharafi Group Investments** | Reported in press with name similarity to "Sharaf" — **not confirmed as the same family; needs a direct check before assuming any link** | Family business; reported by the UAE Ministry of Economy as one of the first companies registered in the **Unified Family Business Registry** (see §D) | Dubai | [moet.gov.ae press release](https://www.moet.gov.ae/en/-/ministry-of-economy-announces-registration-of-first-batch-of-national-companies-in-the-unified-family-business-registry), title only confirmed via search snippet — the direct fetch of this page failed (connection reset) in this session and was not retried successfully | Low — **name-collision risk flagged, not resolved** |
| **Al Naboodah Investments LLC** | Al Naboodah Group — **Abdullah Saeed Al Naboodah**, described as its Chairman | Investment vehicle; Abdullah Saeed Al Naboodah separately founded **Phoenix Capital** (2007), a private investment firm connecting Gulf family offices to Israeli tech investments | Dubai | [Businesswire press release, 2020-10-05](https://www.businesswire.com/news/home/20201005005741/en/OurCrowd-Abdullah-Saeed-Al-Naboodah-Create-Partnership-to-Develop-Tech-Investment-Ties-Between-Gulf-Region-Israel) — a primary press release, but only the OurCrowd side is corroborated; Al Naboodah Group's own site (alnaboodah.com, fetched directly 2026-09-24) makes **no mention** of "Al Naboodah Investments" or a family-office arm anywhere on it | Low-medium |
| **Saeed & Mohammed Al Naboodah Group** | Al Naboodah family (the group's full legal/trading name) | Aggregators (Preqin, Altss, LeadIQ) label this a single-family office; it is at minimum the family's main operating holding | Dubai | Aggregator profiles only; GLEIF fulltext search for "Al Naboodah Investments" returned no relevant match (only an unrelated Arabic-named firm) | Low |
| **Al Rostamani Group / "AW Rostamani Group"** | Al Rostamani family | Aggregators call this a single-family office; no separately named investment arm found — it appears the operating group itself is the vehicle | Dubai | GLEIF confirms **"A W ROSTAMANI GROUP L.L.C"** exists (LEI `213800JOWSO4NEI6MG37`, Dubai) as a legal entity, but GLEIF carries no activity classification so this confirms existence only, not that it functions as a family office | Low-medium (existence) |
| **Al Serkal Group** | Al Serkal family (Chairman: Ahmad Bin Eisa Al Serkal) | Aggregators (Altss, SWFInstitute, PitchBook) call this a multi-family office; GLEIF has a separate, smaller **"Al Serkal Consultancy"** (Arabic: السركال للاستشارات ذ.م.م), LEI `984500D8D91RC0A96B82`, Dubai — relationship between this and "the family office" is not established | Dubai | Aggregator profiles + GLEIF (existence of a differently-named consultancy entity only) | Low |

---

## C. A resolved-and-unresolved name-collision, worth flagging like GIMD/AGPM

**"Al Ghurair" names at least three legally and financially separate things, and press/aggregator
sources routinely blur them:**

1. **Al Ghurair Group** — the conglomerate chaired by **Abdul Aziz Al Ghurair** (descended from
   Saif Ahmad Al Ghurair's branch, per [Wikipedia: Al Ghurair Group](https://en.wikipedia.org/wiki/Al_Ghurair_Group)).
   Runs an internal, unnamed **"Family Office" function** per its own site (§A above) that manages
   portfolio investments alongside its strategic stakes in Mashreq Bank and National Cement Company.
2. **Al Ghurair Investment LLC** — a formally separate company built by the *other* branch of the
   family (Abdullah/Abdulla Al Ghurair's line), per Wikipedia's account of a 1990s split between
   brothers Saif and Abdullah. Confirmed to exist via GLEIF (§A). A near-identically-named GLEIF
   record, **"Abdulla Ahmed Al Ghurair Investment Co. LLC,"** may or may not be the same legal
   entity under an earlier name — **this was not resolved in this pass** and should not be assumed
   either way.
3. **Abdulla & Hamad Al Ghurair Investment LLC** ("A&H Investment") — a *third*, distinct and
   confirmed-live holding company (§A), run by **Abdulla Majed** and **Hamad Majed Al Ghurair**, a
   different generation/branch again. Its own site never uses the words "Al Ghurair Group" or
   "Al Ghurair Investment" — it presents as its own thing.
4. A fourth website, **al-ghurairinvestmentgroup.com** ("Al-Ghurair Investment," chairman named as
   "Ahmad Al Ghurair"), surfaced in search and was fetched directly. **Flagged as suspicious, not
   reported as a real prospect**: the site's own language — offering "Bank Guarantee (BG), Standby
   Letter of Credit (SBLC), Medium Term Notes (MTN)... at discounted rates" as a service it
   provides — is a pattern strongly associated with advance-fee/trade-finance scam sites, not a
   reputable family investment office. Whether "Ahmad Al Ghurair" here has any real connection to
   the Al Ghurair family is unconfirmed and, given the site's content, should not be assumed. **Do
   not contact or reference this site.**

**Do not treat any "Al Ghurair" record found elsewhere (press, LinkedIn, a future register hit) as
self-evidently one of the above four without checking which one it names.** This is exactly the
GIMD/AGPM trap the brief warned about, playing out inside a single Emirati family name.

---

## D. A genuine structural signal, not a name list

The UAE Ministry of Economy has been building a **"Unified Family Business Registry"** since a
Cabinet decision in December 2023 ([The National, 2023-12-27](https://www.thenationalnews.com/business/economy/2023/12/27/uae-launches-unified-registry-to-boost-family-businesses/)),
under a Family Business Law. The Ministry announced it had started accepting applications
([moet.gov.ae](https://www.moet.gov.ae/en/-/ministry-of-economy-starts-accepting-applications-for-registration-of-family-businesses-in-the-unified-registry))
and later announced registration of a "first batch" of national companies
([moet.gov.ae](https://www.moet.gov.ae/en/-/ministry-of-economy-announces-registration-of-first-batch-of-national-companies-in-the-unified-family-business-registry)).
**No public, browsable list of registered names was found** — search results confirm the registry's
existence and purpose but not a directory. One direct fetch attempt at the Ministry's press release
page failed with a connection reset in this session and was not successfully retried.

This belongs in the "regulatory/ownership change" category the brief asks us to flag: a government
registry that requires family businesses to formalise governance (a Family Business Law) is exactly
the kind of event that tends to accompany, or precede, professionalising financial infrastructure —
worth a light watch, and worth someone with laptop access re-attempting the direct fetch, since a
government source naming registrants (if it ever becomes public) would be categorically better than
any aggregator on this whole page.

---

## E. Families looked at, no named vehicle found

Checked directly (official site, or a targeted search plus at least one official-site fetch attempt)
and found **no named family office or investment-arm entity** — only the operating conglomerate
itself, sometimes informally called a "family office" by aggregators with no vehicle name attached:

- **Easa Saleh Al Gurg Group (ESAG)** — ZoomInfo lists a "Head of Family Office" *role* (Mohammed
  Al Shaibani) but algurg.com's own leadership page (fetched directly, 2026-09-24) names no separate
  family-office entity. Treat as: a family-office *function* exists, no distinctly named vehicle
  confirmed.
- **Chalhoub Group** — aggregators (Altss, SWFInstitute) call it a single-family office; no named
  investment arm found in this pass, and no attempt yet to fetch chalhoub.com directly.
- **Al Tayer Group** — the operating group itself (see Investment Trading Group in §A for its
  confirmed investment office).
- **Al Habtoor Group** — the operating group itself (see Al Habtoor Investment in §A for its
  confirmed investment arm).

## F. Families named in the brief that are out of UAE scope

- **YBA Kanoo / Yusuf Bin Ahmed Kanoo Group** — headquartered in **Bahrain**, not the UAE, per its
  own "About Us" page (kanoo.com) and Forbes Middle East. It does run named divisions — **Kanoo
  Capital** (established 2016) and **Kanoo Global Investments** — but neither was confirmed as a
  UAE-registered entity in this pass (no GLEIF match for either name under the UAE country filter).
  Not included in the tables above; worth a separate Bahrain-scoped look if that market opens up.
- **Alshaya Group** — headquartered in **Kuwait**; operates across the UAE and other GCC markets but
  no UAE-specific named investment vehicle was found. Out of scope for this UAE-specific task.
- **Olayan Group, Al Bin Laden Group, Alghanim Industries** — Saudi/Kuwaiti families named in the
  brief's example list; not pursued here as they are not UAE entities. (Note: **The Olayan Group**
  already has a CRM record, `the-olayan-group.yaml`, presumably from Saudi-market work — not
  duplicated here.)

---

## Unknowns (explicit)

- Whether **Al Ghurair Investment LLC** and **Abdulla Ahmed Al Ghurair Investment Co. LLC** (two
  different GLEIF records) are the same legal entity under two names, or genuinely two entities —
  unresolved.
- Any live, reachable website for **Al Ghurair Investment LLC** — `alghurairinvest.com` 404'd on a
  direct fetch 2026-09-24; do not assume it is dead permanently, but do not cite it as live either.
- Whether **Skylark Investment Limited** and **Padar Investment Limited** (GLEIF entities sharing an
  "Al Habtoor Motors Bldg" address) are actually Al Habtoor-family vehicles — address proximity only,
  no corroborating source.
- The true relationship between **Sharaf HQ Investment**, **Sharaf Investment (L.L.C.)**, and
  **Sharafi Group Investments** — are these the same thing, sibling entities, or three unrelated
  companies that happen to share a name pattern? Not resolved. **Sharafi Group Investments** in
  particular needs a direct check against the Sharaf family before being treated as part of the same
  group at all — flagged as a live name-collision risk, not a confirmed fact either way.
- Whether the Galadari family's four differently-named entities (**Galadari Brothers**, **Ilyas &
  Mustafa Galadari Group**, **Galadari Investment Office**, **AWGAL Investments**) map to four
  distinct branches or overlap — not independently confirmed; only aggregator-sourced.
- Any public, named list from the UAE's **Unified Family Business Registry** — confirmed to exist,
  contents not public as far as this pass could establish; the Ministry's own announcement page
  could not be fetched directly in this session (connection reset) and should be retried.
- Whether any of the entities in §A or §B are **single** or **multi**-family in the strict sense
  used elsewhere in our CRM (an MFO manages third-party money) — every one identified here that has
  a primary-source description is proprietary/single-family; none was found, in this pass, to
  describe itself as managing money for families other than its own. That is itself a finding: the
  "named investment vehicle of a named merchant family" route surfaced **single**-family vehicles
  almost exclusively — it is not, on this evidence, a good route to *multi*-family offices, which
  remain the better commercial prospect per `memory/facts.md`.
- Kanoo Capital / Kanoo Global Investments' exact registration jurisdiction — not confirmed as UAE
  or Bahrain-only; GLEIF found nothing under either name in the UAE.

---

## Recommendation for whoever picks this up next

None of the entities in §A are, on present evidence, immediately actionable Gaia prospects — every
one confirmed here is a **single-family, proprietary** vehicle (the same shape as
`al-muhaidib-investment-office.yaml`, already in our CRM from the Saudi side), and per
`knowledge/market/icp.md`'s own scoring logic a proprietary single-family office scores materially
lower than a multi-family office managing third-party money, precisely because there is no
third-party money, no external client reporting obligation, and often no regulator to force a
system decision. They are worth holding as **named, sourced records** (not inventing contacts or
triggers for them) rather than as active pipeline. The one genuinely new **channel** this pass
opened is GLEIF's ability to walk a family name to its registered vehicles cheaply and repeatably —
worth reusing for Saudi and Lebanese family names too, not just UAE ones.
