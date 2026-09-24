# UAE private banks, bank wealth arms, MFOs and EAMs -- open-web sweep

> Written 2026-09-24, at Andre's request. Scope: **UAE private-banking and wealth end only** --
> private banks, banks' private-banking/wealth-management arms, multi-family offices (MFOs) and
> external asset managers (EAMs). A colleague is covering non-register asset managers and
> investment firms separately; this file does not duplicate that.
>
> **Do not re-run the family-office/MFO search** -- `plan/uae-family-offices.md` (written earlier
> today) already did a wide, verified sweep of UAE SFOs/MFOs. This file cross-references it rather
> than repeating it, and adds only what that file did not cover: private banks, bank wealth arms,
> and EAMs.
>
> Method: wide web search (many query variants, English + one Arabic pass), then every firm's own
> site or the DFSA/FSRA public register was opened directly (WebFetch, or curl with a browser
> user-agent where WebFetch was blocked -- the DFSA register blocks WebFetch's own fetcher but not a
> plain browser-UA GET; consistent with the existing note in `memory/facts.md`). No firm, person,
> URL, or AUM figure below is invented. Where a fact came only from a search-result snippet and
> could not be opened directly, that is stated.
>
> **CRM overlap checked first.** Before treating anything as a new candidate, `crm/companies/*.yaml`
> was grepped for the firm name. A large number of the UAE banks a search turns up are **already in
> the CRM** -- mostly register-sourced generic bank records (segment `bank`/`fund_manager`/`broker`
> depending on how the connector mapped their DFSA licence category), typically with no
> description and no website. Those are listed below as "already tracked" with what this pass adds
> (what the bank says about its own private-banking/wealth arm), not as new records -- nothing was
> written to `crm/`.

---

## A. International private banks / EAMs with a UAE booking presence -- NOT yet in the CRM

These are the real gap this task was meant to close: independent Swiss/European private banks and
wealth managers with a Dubai or Abu Dhabi presence. For each, the critical question is **what kind
of presence** -- see the rep-office flag column.

| Firm | Emirate | Entity / licence type | What it says about itself | Website | Published contact | Named people (title, source) | Grade | Evidence |
|---|---|---|---|---|---|---|---|---|
| Julius Baer (Middle East) Limited | Dubai (DIFC) | DIFC Company (subsidiary, not a branch or rep office). DFSA ref F000001, licensed 20-Sep-2004. Endorsements include Advising on Financial Products, Arranging Deals/Custody, Arranging Credit, Providing Trust Services (non-trustee), Islamic Window. ~200 staff per own "20 years in Dubai" page. | Swiss private bank; own site frames Dubai as a full-service wealth hub | juliusbaer.com | none published found | Multiple DFSA-authorised individuals on register incl. Bryan Dale Stirewalt (I022385) -- same name as DFSA's own former Managing Director of Supervision, unconfirmed if same person, do not assert | Verified | DFSA register (curl, 2026-09-24): dfsa.ae/public-register/firms/julius-baer-middle-east-limited |
| Lombard Odier (Middle East) Ltd | Dubai (DIFC) | DIFC Company, Cat 4 licence granted 12-Sep-2023 (advisory only, no discretionary endorsement seen) | Swiss private bank; ~30 regional staff per press | lombardodier.com | Phone +971 4 509 0200 | Amer Malik, Local Managing Director | Verified | lombardodier.com/home/contact/private-clients/dubai.html (fetched 2026-09-24) |
| EFG (Middle East) Limited | Dubai (DIFC) | DIFC Company, DFSA ref F003291, licensed 27-Oct-2019, advisory endorsements only. Entity-confusion flag: an older, unrelated, now-WITHDRAWN entity "EFG Bank Ltd" (F000083, withdrawn 2012) also exists; also distinct from EFG Hermes UAE Limited, already tracked (`efg-hermes-uae-limited.yaml`) -- unrelated Egyptian investment bank | Swiss private banking group (EFG International, Zurich-listed) | efginternational.com | none published found | none named this pass | Verified, flag the name collision | DFSA register (curl, 2026-09-24): dfsa.ae/public-register/firms/efg-middle-east-limited |
| Edmond de Rothschild (Middle East) Ltd | Dubai (DIFC) | DIFC Company, Cat 4 advisory licence, opened 28-Feb-2023, replacing a prior representative office (press states this explicitly) | French-Swiss private banking group | edmond-de-rothschild.com | not established | Ali Raza Syed, Senior Executive Officer | Verified | gulfbusiness.com/edmond-de-rothschild-opens-office-in-difc/ -- CRM's existing edmond-de-rothschild-*-france.yaml records are separate French entities |
| Rothschild and Co Wealth Management -- Dubai | Dubai (DIFC) | Cat 4 licence, office opened Nov-2024 | Independent investment advice to ultra-high-net-worth families, entrepreneurs, charities, foundations | rothschildandco.com | not established | Sascha Benz, relocated from Switzerland to head the office | Verified | rothschildandco.com/en/newsroom/press-releases/2024/11/ -- existing CRM rothschild-co-*.yaml records are all French entities |
| Coutts and Co (Dubai, DIFC) | Dubai (DIFC) | Upgraded from a representative office to a Cat 4 branch on its move into DIFC (press: "as a representative office previously, it was permitted only to tell clients about its products but not to advise on them") | UK private bank/wealth manager (NatWest Group) | coutts.com | not established | not established | Verified (rep-office trap resolved correctly) | privatebankerinternational.com/uncategorized/coutts-relocates-offices-in-dubai/ |
| LGT (Middle East) Ltd | Dubai (DIFC) | DIFC Company regulated by DFSA | Liechtenstein princely-family-owned private bank; ~70-84 staff per press | lgt.com | Phone +971 4 436 7000 | not established | Verified | lgt.com/global-en/about-lgt/lgt-worldwide/united-arab-emirates (fetched 2026-09-24) |
| BNP Paribas Wealth Management (DIFC) Limited | Dubai (DIFC) | DIFC Company, DFSA ref F001482 | BNP Paribas's dedicated wealth arm, distinct from the general BNP Paribas S.A. entity already in the CRM | wealthmanagement.bnpparibas/middleeast | Phone +971 4 374 5911 | Antoine Chemali, CEO Middle East and Africa | Verified | dfsa.ae register (search-confirmed, register throttled on repeat fetch); hubbis.com/news/bnp-paribas-wealth-management-announces-new-ceo-for-middle-east-operations |
| Nomura International plc (DIFC branch, wealth arm) | Dubai (DIFC) | Non-DIFC Company (branch), DFSA ref F001008; Cat 4 wealth licensing dates to 2023 | International Wealth Management arm serves HNWIs, SFOs and EAMs across GCC/North Africa/Levant | nomuraholdings.com | not established | not established | Verified | dfsa.ae register (search-confirmed); nomuraholdings.com/en/news/nr/news20230720103068.html |
| GSB Capital Ltd | Dubai (DIFC) | Dual-regulated EAM, DFSA licence F006321. Already in the CRM (`gsb-capital-ltd.yaml`) | Fee-based EAM/private-banking advisory for HNWIs and family offices, claims ~$4-5bn advisory / ~$1bn AUM (not independently corroborated) | gsbglobal.com | compliance@gsbglobal.com | Ross Whatnall, founding partner (founded 2021) | Verified (already tracked) | gsbglobal.com (fetched 2026-09-24) |
| Almha Capital Limited | Abu Dhabi (ADGM) | FSRA-regulated; not found in the CRM -- new candidate | Independent Advisory and Investment Firm -- proprietary investment, strategic consultancy, capital raising, fund distribution, investment advisory; claims ~$6bn AUM across 8 offices (not corroborated) | almhacapital.com | info@almhacapital.com; +971 26 67 24 30 | H.E. Hareb Al Darmaki, Founder (ex-ADIA, ex-Gulf Capital per own site) | Verified | almhacapital.com (fetched 2026-09-24) |

### Doubtful / rejected -- the representative-office trap and other cautions

| Firm | What was found | Grade | Reason |
|---|---|---|---|
| Pictet (Dubai) | Own site, fetched directly, states in its own words: "Representative office", regulated by the Central Bank of UAE (not DFSA/DIFC), at One Za'abeel -- distinct from a separate, older Zawya/Khaleej Times story about "Pictet Asset Management" opening in DIFC, not confirmed as currently active and separately licensed | Doubtful | Textbook rep-office case: cannot conduct financial business itself, platform decision sits with Geneva. Do not present as a live prospect without confirming a separate DIFC-licensed entity exists. |
| RBC Wealth Management (Dubai) | Press names RBC's Dubai lead with the title "Chief Representative for Dubai Office" -- rep-office-style title, not a branch CEO/SEO title. No current DFSA register entry found under an active RBC wealth/private-bank name (the only DFSA-linked history, "RBC Dexia", is a defunct 2008-era custody JV, absorbed into CACEIS) | Doubtful | The "Chief Representative" title is the same signal the brief warned about. Treat as marketing/liaison presence until a DFSA Cat-3/4 licence for a current RBC private-banking entity is confirmed. |
| CA Indosuez (Switzerland) SA -- Abu Dhabi office | Indosuez's own UAE site names this "CA Indosuez (Switzerland) SA, Abu Dhabi Representative Office" explicitly, distinct from the Dubai DIFC Branch (a real branch, verified separately) | Rejected for Abu Dhabi; verified for the Dubai DIFC branch | Own-site language is unambiguous. Dubai DIFC branch (Rolf Schilde SEO, Charles Tort Deputy CEO, both named in press) is a new candidate not yet in the CRM -- existing ca-indosuez.yaml / ca-indosuez-gestion.yaml records are the French entities. |
| Falcon Private Wealth (Dubai, DIFC) | Parent Falcon Private Bank (Zurich) collapsed under money-laundering enforcement action (Swiss/Singapore regulators, 1MDB-linked) and wound down from 2020. DFSA register now shows the Dubai entity renamed to "ONE Swiss Private Wealth Limited" | Rejected as "Falcon"; unresolved as "ONE Swiss Private Wealth" | Do not approach as "Falcon" -- reputationally dead, parent bank no longer exists. Whether the renamed entity is a live, differently-owned going concern was not established this pass. |
| Vault22 | AI-powered personal budgeting/finance app, DIFC-headquartered, founder Benito Mable | Rejected | A consumer budgeting app, not a wealth manager managing client assets. Do not confuse with Vault Wealth Limited (ADGM, FSRA Cat 3C/4, already tracked in the CRM) -- two different companies, confusingly similar names. |

---

## B. UAE local banks' private-banking / wealth-management arms -- mostly ALREADY in the CRM

Every one of these banking groups is already a CRM record (register-sourced, generic `bank` entry,
usually with no website and no description). This section confirms what each bank's own site says
about its private-banking/wealth arm specifically, for whoever later enriches these records -- it is
not a list of new leads, and nothing was added or changed in `crm/`.

| Bank | CRM record | What its own site says about private banking / wealth | Named leadership found | Evidence |
|---|---|---|---|---|
| Abu Dhabi Commercial Bank (ADCB) | abu-dhabi-commercial-bank.yaml | "ADCB Private and Wealth Management" -- Euromoney's 2025 Middle East Best Private Bank winner; also runs a dedicated ADGM branch for private-banking clients | Mahmoud Ezzedine, Group Head of Private Banking and Wealth Management (2025 press) | euromoney.com/article/2eegv5linr5ht9smwnkld/ ; adcb.com/en/private/adgm-branch/ |
| Emirates NBD | emirates-nbd-bank-pjsc.yaml | Private Banking division, threshold USD 5 million AUM; investment advisory, trust/estate planning, external asset management, lending | Two names found, not reconciled: Mohammad Al Bastaki (Group Head since Aug-2023 per one source) and Saod Obaidalla ("promoted to global Head of Private Banking", undated) -- check the dated press release before outreach | emiratesnbd.com/en/private-banking (fetched 2026-09-24) |
| Mashreq | mashreqbank-psc.yaml | Mashreq Private Banking / "Mashreq Gold" -- investment solutions, family-office-style legacy/trust/estate planning | Three names surfaced, not reconciled: Rajesh Malkani (Head of Private Banking and Wealth Management per press), Hazem Fouad (Investment Business for Private Banking/Mashreq Gold), Vipul Kapur (also "Head of Private Banking" per company Instagram) | mashreq.com/en/uae/private/ (fetched 2026-09-24) |
| First Abu Dhabi Bank (FAB) | first-abu-dhabi-bank-p-j-s-c.yaml and first-abu-dhabi-bank.yaml (two CRM records appear to be the same bank -- not resolved here) | FAB Private Banking -- investment advisory, discretionary portfolio management, Lombard lending; integrated with FAB Private Bank (Suisse) SA Geneva | none named on the page | bankfab.com/en-ae/private (fetched 2026-09-24); PB@bankfab.com published |
| Commercial Bank of Dubai (CBD) | commercial-bank-of-dubai.yaml | Private Banking with dedicated Relationship Manager; "CBD Invest" digital wealth platform; separate "Al Islami Private" Sharia-compliant brand | not established | cbd.ae/personal/private-banking (403 to fetcher; via search cache) |
| National Bank of Ras Al Khaimah (RAKBANK) | national-bank-of-ras-al-khaimah.yaml | "RAKBANK Elite" private banking (AED 3.5m+ threshold) plus general Wealth Management | not established | rakbank.ae/en/wealth (JS-heavy, did not render) |
| Dubai Islamic Bank (DIB) | not found under this name in the CRM grep -- check before assuming a gap | "Wajaha" invitation-only UHNW wealth service; general "Al Islami" brand; "Aayan Exclusive Banking" centres | not established | paminsight.com/twn/article/dubai-bank-launches-uhnw-service-to-supplement-private-banking-offering |
| Emirates Islamic | emirates-islamic-bank.yaml | "Shariah-Compliant Private Banking and Wealth Management" | not established | emiratesislamic.ae/en/private-banking |
| Habib Bank AG Zurich | habib-bank-ag-zurich.yaml | New DIFC branch (effective 1-Nov-2025) inside its "Wealth Management Switzerland" branch; Shariah-compliant "Sirat" brand | not established | habibbank.com/ch/difc/ (fetched 2026-09-24) |
| Standard Chartered | standard-chartered-bank.yaml | Standard Chartered Private Bank operates from the DIFC branch | not established | sc.com/en/wealth-retail-banking/private-banking/contact-us/ |
| Barclays | barclays-bank-plc.yaml | Barclays Bank PLC (DIFC Branch): Investment Bank, International Corporate Banking, and Private Banking and Wealth Management per own UAE contact page | not established | ib.barclays/contact-us/ae.html |
| Deutsche Bank | deutsche-bank-ag.yaml | Wealth Management arm in Dubai (DIFC) and Abu Dhabi (ADGM); regional head chain (2019-era, stale) ran Fred Hilal then Mubashar Ayoob reporting to Loic Voide | stale 2019 sourcing, do not quote as current | wealth.db.com/en/locations/europe-middle-east-and-africa/united-arab-emirates.html |
| Citibank | citibank-n-a.yaml | Citi Private Bank operates from the same Citibank N.A. UAE entity; "Citigold Private Client" threshold USD 1,000,000 | not established | privatebank.citibank.com/office-locations/dubai |
| HSBC | hsbc-bank-middle-east-limited.yaml (onshore) | Two distinct HSBC private-banking entities per own page: onshore HSBC Bank Middle East Limited (Emaar Square) and offshore "HSBC PB (Suisse) SA DB" at DIFC -- offshore entity not obviously the same CRM record, not separately confirmed | not established | privatebanking.hsbc.com/hsbc-private-banking-uae/ (fetched 2026-09-24) |
| J.P. Morgan | j-p-morgan-middle-east-limited.yaml (CRM lists as Abu Dhabi; own site places Private Bank office at ICD Brookfield Place, DIFC -- reconciliation not resolved here) | J.P. Morgan Private Bank, DIFC | not established | privatebank.jpmorgan.com/eur/en/locations/emea/dubai |
| Mirabaud | not new -- already mirabaud-middle-east-limited.yaml | Cat 1 DFSA licence; discretionary management, advisory, wealth planning, EAM support; ~40 staff; WealthBriefing MENA 2023 award | Georges Khoueiri, CEO Mirabaud Middle East | mirabaud.com/en/mirabaud-group/contact/our-offices/dubai (fetched 2026-09-24) |
| Union Bancaire Privee (UBP) | not new -- already union-bancaire-privee-middle-east-limited.yaml | ~USD 12bn ME AUM, ~USD 4.5bn booked in Dubai per press (not corroborated); DIFC branch since 2011 | Mohamed Shoukry, CEO UBP Middle East (from 2024) | ubp.com/en/contact/our-offices/ubp-dubai |

---

## C. Multi-family offices (MFO) -- see plan/uae-family-offices.md, not repeated here

That file (written earlier today) already ran a wide, verified search across UAE SFOs and MFOs --
Abbey Road Investment Group, Pharos MFO, McFaddens and Co (UAE), Advani Family Office, Equalis
Capital Ltd, The Family Office Company (DIFC branch), Corecam, MSM Investment Advisors, Patrimium
Asset Management, and others, each graded with evidence. Nothing new was found in this pass beyond
what that file already documents. One point worth restating here because it is squarely in this
task's territory: "Al Qasimi Family Office", which some third-party MFO listicles
(familyofficehub.io, andsimple.co) assert is a Dubai-headquartered MFO founded 1982 --
plan/uae-family-offices.md already flagged this name as unresolved, finding no independent primary
source distinguishing a formal "Al Qasimi Family Office" entity from the Sharjah/RAK ruling family's
general holdings. This pass found the same vendor claim repeated but no better primary source, so
the existing "do not treat as verified" caution stands.

---

## D. Dead-end / low-yield routes this pass, do not repeat

- DFSA's own register pages (dfsa.ae/public-register/firms/...) block WebFetch outright (403) but
  respond normally to a plain curl with a standard browser User-Agent -- and even curl was
  rate-limited/blocked on back-to-back requests without a short pause. Anyone re-running this should
  space out register lookups.
- Several bank sites blocked WebFetch specifically (403) while being reachable in a normal browser --
  adcb.com/en/private/, cbd.ae/personal/private-banking, efginternational.com, juliusbaer.com
  (locations page), rothschildandco.com (office page 404'd, likely a stale URL rather than
  blocking) -- consistent with the bot-sensitivity pattern already logged in memory/facts.md for
  other UAE financial sites (DFM, ADX, AGBI).
- rakbank.ae/en/wealth is JS-heavy; a plain fetch returns "Loading..." placeholders with no
  substantive content -- same class of problem as DFM/ADX noted in plan/uae-sources-commercial.md.
- A generic Arabic-language search surfaced only general explainer content (DIFC/DWTC regulatory
  framework, tax-efficiency pieces) and one Arabic-language MFO name already covered elsewhere
  (Dawia Family Office, dawiafo.com) -- not independently verified this pass, flagged as unknown
  rather than added as a graded candidate.

---

## Unknowns (explicit)

- Whether a separate, currently-licensed Pictet DIFC entity (distinct from the Central
  Bank-regulated representative office confirmed above) exists -- one older press piece (Zawya)
  refers to "Pictet Asset Management" opening in DIFC, which was not independently re-confirmed as
  still active and separately licensed in this pass.
- RBC's current UAE legal/licensing status -- whether any DFSA Cat-3/4 entity exists today under an
  active RBC private-banking name, beyond the "Chief Representative" title found in press. Not
  established.
- Whether "ONE Swiss Private Wealth Limited" (the DFSA register's current name for the former Falcon
  Private Wealth Limited entity) is a live, differently-owned, evaluable prospect in its own right --
  not established, would need its own pass.
- Emirates NBD's current Group Head of Private Banking -- press gives two names (Mohammad Al
  Bastaki, since Aug-2023; Saod Obaidalla, "promoted to global Head of Private Banking", undated
  snippet) without dates that reconcile cleanly. Do not draft outreach to either without checking
  the dated Emirates NBD press release directly.
- Mashreq's current Head of Private Banking -- three names surfaced (Rajesh Malkani, Hazem Fouad,
  Vipul Kapur) at what read as different levels of seniority/scope; not reconciled into a single
  current org chart.
- Whether HSBC's offshore DIFC private-banking entity ("HSBC PB (Suisse) SA DB") is the same CRM
  record as hsbc-bank-middle-east-limited.yaml (the onshore entity) or a separate, currently
  untracked legal entity -- not established.
- Whether J.P. Morgan Middle East Limited, which the CRM records as Abu Dhabi, is the same legal
  entity that books J.P. Morgan Private Bank's Dubai DIFC office, or whether JPM operates two
  separate UAE entities -- not established; worth reconciling before treating either as duplicate or
  distinct.
- CRM hygiene note, not investigated further here: first-abu-dhabi-bank-p-j-s-c.yaml and
  first-abu-dhabi-bank.yaml appear to be two records for the same bank. Flagging only; not fixed,
  per this task's "do not write to crm/" instruction.
- No AUM figures quoted anywhere in this file (GSB's "$4-5bn advisory / ~$1bn AUM", Almha's "~$6bn",
  UBP's "$12bn ME / $4.5bn Dubai") were independently corroborated beyond the firm's own site or a
  single press mention -- treat as claimed, not verified, figures.
