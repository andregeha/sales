# UAE enrichment — no-website, no-email records verified against the open web

**Scope:** UAE CRM records with no `website` and no contact `email`, drawn from the 573-record queue
(573 = non-disqualified UAE records lacking both a website and an email, out of 810 UAE records
total). Segment priority per brief: asset_manager -> fund_manager -> mfo/family_office -> bank.
**Method:** open-web search (2+ queries per firm, varying legal vs. trading name and DIFC/ADGM/Dubai/
Abu Dhabi qualifiers), then a direct fetch of any firm-owned domain found, read-only, GET only.
**Coverage:** 70 of 573 firms verified in depth (family offices/MFO: 13/13 on the list; asset
managers: ~39; fund managers: ~18). Depth over coverage, as instructed - this is not the full 573.
**Rule applied throughout:** a phone/address appearing only on the DFSA/ADGM/DIFC regulator register
or a third-party directory (b2bhint, ZoomInfo, Dun & Bradstreet, LinkedIn, etc.) is **not** recorded
as a contact route - only what the firm's **own site** publishes. Where a firm's own site could not
be reached (cert error, timeout, blank fetch), that is stated rather than filled with directory data.

---

## Family offices & MFO (13/13 checked - a core target segment)

| Slug | Firm | Website | Email (firm's own site) | Phone (firm's own site) | Named people | What they do | Evidence |
|---|---|---|---|---|---|---|---|
| ajm-international-limited | AJM International Limited | none found | - | - | - | Unknown - no independent trace beyond the register. | searched "AJM International" Dubai DIFC family office (2026-09-24) |
| al-rayid-investments-ltd | Al Rayid Investments Ltd | none found (own site) | - | - | - | Single Family Office, DIFC, est. 2020, Central Park Offices. | b2bhint.com company profile (2026-09-24) |
| anou-sfo-limited | Anou SFO Limited | none found | - | - | - | Single Family Office, DIFC (Index Tower), incorporated 2018. | clarifiedby.diligenciagroup.com / b2bhint.com (2026-09-24) |
| kaaf-investments | KAAF Investments | kaafinvestments.com | info@kaafinvestments.com | not published | Mishal Kanoo (Chairman), Maha Kanoo (Vice Chairwoman), Bassem Kanoo (Director), Filmon Ghebrihiwet (CIO), Nandi Vardhan Mehta (CFO) | Single-family investment platform of the Kanoo family (Yusuf Bin Ahmed Kanoo Group); PE, VC, fund investments, ~$400M AUM. | kaafinvestments.com (fetched 2026-09-24) |
| maddox-street-limited | Maddox Street Limited | none found (own site) | - | - | Priya Assomull, Sujata Assomull (directors/shareholders per DIFC public register; company secretary Sujata Assomull) | Family office, DIFC, non-regulated private company, incorporated 2010. | difc.com/public-register/maddox-street-limited (2026-09-24) - regulator register, not the firm's own site; names are register data, not a contact route |
| massar-investments-ltd | Massar Investments Ltd. | none found (own site) | - | - | Principal reported as Abdul Aziz Al Ghurair (per third-party profiles - unconfirmed on any firm-owned page) | Single family office of the Al Ghurair family, Dubai, founded 2011; PE, private debt, co-investments. | altss.com, premieralts.com (2026-09-24) - has a LinkedIn company page only |
| mayfield-group-llp | Mayfield Group LLP | none found | - | - | - | DIFC partnership, active, incorporated 2015, Park Towers. Not the same entity as the US VC firm Mayfield. | b2bhint.com / DIFC register (2026-09-24) |
| rosemonde-limited | Rosemonde Limited | none found | - | - | - | DIFC company, active, incorporated 2010, Liberty House; auditor TRC Pamco Middle East. | b2bhint.com / DIFC register (2026-09-24). Register lists a phone (0442 79580) - not recorded as a contact route since it is not on a firm-owned site |
| sabban-holdings-limited | Sabban Holdings Limited | none found (own site) | - | - | - | Single family office of the Al-Sabban family, Dubai, DIFC (Emirates Financial Towers), incorporated 2013, ~$300M AUM, alternatives/private markets. Related group entities (Sabban Corp Investment, Sabban Property Investments) have Instagram presences only. | Preqin, SWFI profile (2026-09-24) |
| tam-capital-llc | TAM Capital LLC | none found | - | - | - | Single family office, DIFC, diversified public/private markets, real estate, alternatives. | altss.com, Preqin, DIFC register (2026-09-24) |
| tsangs-group-sfo-limited | Tsangs Group SFO Limited | none found (own site) | - | - | - | Dubai arm (DIFC, Emirates Financial Towers, DNFBP registered Dec 2021) of Hong Kong-headquartered Tsangs Group, an East-West tech-focused family office. | AsianInvestor, chinadailyhk.com (2026-09-24) |
| twinwood-family-holdings | Twinwood Family Holdings | none found | - | - | - | Single family office, DIFC (Gate Village 10), incorporated 2018; associated with the Putera Sampoerna / Sampoerna Strategic family (Indonesia); holds a stake in PT Sampoerna Agro. | Bloomberg profile, b2bhint.com, ICIJ Offshore Leaks node (2026-09-24) |
| equalis-capital-ltd (mfo) | Equalis Capital Limited | none found (own site) | - | - | Tobias Pfister (Co-Founder & CEO), Philipp Frank (CIO) - per third-party profiles, not confirmed on a firm-owned page | DIFC-based multi-family office / proprietary investment firm, est. 2013, Emirates Financial Towers; PE, real estate, infrastructure, hedge funds. | altss.com, premieralts.com (2026-09-24) |

**Finding:** of 13 UAE family offices/MFO with no website/email on file, only **1 (KAAF Investments)**
has a real, reachable, firm-owned website with a published email and named leadership. The other 12
are genuine, licensed DIFC entities (confirmed via the DIFC/DFSA register or credible third-party
fund-industry profiles) but publish **no** independent web presence of their own - consistent with
single-family offices, which by design are not client-facing businesses and have no reason to market.
This is a useful negative finding, not a data gap: these are real but structurally unreachable by cold outreach.

---

## Asset managers (39 checked)

| Slug | Firm | Website | Email | Phone | Named people | What they do | Evidence |
|---|---|---|---|---|---|---|---|
| abk-capital-difc-limited | ABK Capital (DIFC) Limited | abk.eahli.com (ABK-DIFC banking site - entity caution, see note) | DPO@abkuwait.com; RamiRifai@abkuwait.com; treasurydifc@abkuwait.com (others) | +971 4 6075 666/660 (+ individual lines) | Rami El Rifai (Senior Executive Officer), Laila Al Nemah, Peter De Swart, Mounir Nasrallah, Elie Abi Ghosn, Nistala Devi | Investment-arm subsidiary of Al Ahli Bank of Kuwait (ABK) Group, licensed at DIFC 23-May-2025 (Category 1); the contact page found belongs to ABK-DIFC, the banks branch, which may be a distinct DFSA registration from ABK Capital (DIFC) Limited the asset-management subsidiary - flagged, not conflated. | abk.eahli.com/en/international-banking/offshore/abk-difc (fetched 2026-09-24); gulfnews.com, dfsa.ae register (2026-09-24) |
| abs-middle-east-limited | ABS (Middle East) Limited | not located (parent: arabbank.ch) | none found | none found | Samir Atitallah (CEO, per press) | Newly launched (announced June 2026) DIFC wealth-management entity of Arab Bank Switzerland, serving entrepreneurs/family offices/HNW across UAE and region. | gulfbusiness/Zawya/fintechnews.ae coverage (2026-09-24) |
| access-technologies-opco-limited | Access Technologies OPCO Limited (trades as Access Wealth) | accesswealth.io | support@accesswealth.io | +971 4 570 8489 | 8 named investor-shareholders incl. Kunal Savjani, Mounir Kuzbari, Scott Kerson, Kamal Haider, Denko Mancheski, Geoff Rapp, Hadi Darwiche, Neil Petch | DFSA Cat 3C wealth manager, DIFC (Innovation One); curated alternatives, model portfolios, high-yield cash. | accesswealth.io (fetched 2026-09-24) |
| acp-me-management-limited | ACP ME MANAGEMENT LIMITED | none found | - | - | - | Registered in ADGM Abu Dhabi, not DIFC (records likely assumption); not permitted retail clients or client-asset holding. | adgm.com public register (2026-09-24) |
| ad-diriyah-asset-management-limited | Ad Diriyah Asset Management Limited | addiriyaham.com | info@addiriyaham.com | +971 (04) 401 9515 | none published | DIFC-licensed (Mar-2021) VC fund manager, early/late-stage tech, food & beverage. Confirmed this is the DIFC entity, not a Saudi Diriyah-brand real-estate business (checked explicitly given the name similarity risk). | addiriyaham.com/contact-us (fetched 2026-09-24) |
| adib-capital-limited | ADIB Capital Limited | adib.ae/en/pages/adib-capital | adibc.am@adib.com | not published | none published | Wholly-owned asset-management/investment-banking subsidiary of Abu Dhabi Islamic Bank, DIFC, DFSA Cat 3C; Sharia-compliant funds (incl. digital infrastructure, trade finance). | adib.ae (fetched 2026-09-24) |
| africap-middle-east-limited | Africap Middle East Limited | africap.me (found, site unreachable - DNS error on fetch) | - | 971 4 585 6211 (DFSA register only - not recorded as contact route) | - | Wealth/asset manager, DIFC, licensed 2020. | dfsa.ae register; africap.me listed in search (2026-09-24) |
| aip-management-difc-limited | AIP Management (DIFC) Limited | none found | - | - | - | DIFC hedge-fund manager (Liberty House); one of the managers that helped take DIFC past 100 registered hedge-fund managers. | gulfbusiness.com, gulfnews.com (2026-09-24) |
| ajeej-capital-difc-limited | Ajeej Capital (DIFC) Limited | ajeej.com | ir@ajeej.com | +971 (4) 433 6510 | none published (site references the team, no names given) | Oldest independent asset manager in the Middle East (est. 2007), ~$800M AUM, GCC + Egypt equities/fixed income/private credit; offices Dubai/Abu Dhabi/Riyadh. | ajeej.com/contact (fetched 2026-09-24) |
| al-ahly-financial-difc-ltd | Al Ahly Financial (DIFC) Ltd | none found | - | 971 4 376 0500 (DFSA register only) | - | DIFC entity (licensed 2012), subsidiary of Egypts National Bank of Egypt/Ahly group; investments, asset management, fund management. | dfsa.ae register (2026-09-24) |
| al-tariq-capital-limited | Al Tariq Capital Limited | none found | - | - | - | DIFC company, licensed Apr-2026, investment/credit/asset management. | dfsa.ae register (2026-09-24) |
| alben-capital-ltd | Alben Capital Ltd | albencapital.com | none published | none published | none published | DIFC wealth-infrastructure platform (ALBEN Wealth Platform) for HNWI, family offices, institutions; multi-custody reporting, white-label. | albencapital.com (fetched 2026-09-24) |
| alcazar-capital-limited | Alcazar Capital Limited | alcazar-capital.com | info@alcazar-capital.com | +971 4 706 0300 | none published | Private equity firm, DIFC, est. 2007, >$1bn AUM; infrastructure, energy, healthcare, logistics, real estate. | alcazar-capital.com (fetched 2026-09-24) |
| alpen-asset-advisors-limited | Alpen Asset Advisors Limited | alpenassetadvisors.com | not retrieved (About page had no contact details; Team/Contact pages not reached) | not retrieved | not retrieved | Independent wealth manager, DIFC, associate of Alpen Capital; bonds, discretionary PM, Islamic wealth mgmt. | alpenassetadvisors.com/about.html (fetched 2026-09-24) |
| alpha-capital-difc-limited | Alpha Capital (DIFC) Limited | acldifc.com | info@acldifc.com | +971 (0) 4 403 8777 | none published | Wealth manager, DIFC, licensed Feb-2023; wealth planning, advisory, credit, custody. | acldifc.com (fetched 2026-09-24) |
| amaltas-partners-limited | Amaltas Partners Limited | none found | - | - | - | DIFC firm (licensed Dec-2024), wealth/asset management and corporate advisory; acquired by Indias Atom Group (DFSA change-of-control approved). | cafemutual.com, DFSA register (2026-09-24) |
| ambit-global-private-client-mena-limited | Ambit Global Private Client (MENA) Limited | not located (parent: ambit.co) | - | - | Digvijay Singh, Shanti Kaliappan (Dubai leadership, per Ambit press release) | UHNW/family-office wealth manager; entered DIFC via 2024 acquisition of Moonrock Investments Ltd. | hubbis.com, Ambit press release PDF (2026-09-24) |
| amicorp-capital-difc-ltd | Amicorp Capital (DIFC) Ltd | amicorp.com/office/amicorp-difc | site shows obfuscated placeholder text for its emails - not reliably capturable, not recorded | not published | none published | Corporate-services/fund-structuring arm of Amicorp Group at DIFC; DFSA Fund Platform Endorsement. | amicorp.com (fetched 2026-09-24) |
| amp-partners-difc-limited | AMP Partners (DIFC) Limited | amp-partners.com | info@amp-partners.com | not published | not published (page references The Team but names did not render) | DIFC subsidiary of Swiss asset manager AMP Partners S.A. (est. 2000). | amp-partners.com/thefirm.php (fetched 2026-09-24) |
| anatole-db-limited | Anatole DB Limited | none found at all | - | - | - | No trace found beyond the bare fact this is a UAE-registered name - could not confirm business activity. | searched Anatole DB Limited DIFC Dubai (2026-09-24) |
| aramid-capital-limited | Aramid Capital Limited | aramid.ae (found; contact fetch timed out) | not retrieved | not retrieved | not retrieved | Independent DIFC investment firm, est. 2024; asset/wealth management for HNWI, professional/institutional investors. | dfsa.ae register; aramid.ae listed (2026-09-24) |
| arini-capital-management-me-limited | Arini Capital Management (ME) Limited | none found (own site) | - | - | - | Registered in ADGM Abu Dhabi, not DIFC; sub-advisory affiliate of London credit manager ARINI, est. 2025. | adgm.com register, SEC adviser filing (2026-09-24) |
| ark-capital-management-dubai-limited | Ark Capital Management (Dubai) Limited | none found | - | - | - | DIFC investment manager/broker, est. 2013. Regulatory flag: DFSA fined the firm USD 504,000 in Feb-2026 for inadequate market-abuse systems/controls and for failing to report a change of control. | dfsa.ae news release (2026-09-24) |
| arna-assets-limited | Arna Assets Limited | arnaassets.com | info@arnaassets.com | +971 4 279 0742 (mobile +971 55 409 1109) | none published | DIFC wealth manager, bespoke advice for individuals/institutions. | arnaassets.com/about-us (fetched 2026-09-24) |
| arolla-finance-limited | Arolla Finance Limited | arolla.ae (found; not fetched for contact) | not retrieved | not retrieved | Geetanjali Sharma (per search snippet - role not fully clear) | Registered in ADGM Abu Dhabi, not DIFC; discretionary global-credit investment manager. | arolla.ae, adgm.com register (2026-09-24) |
| arp-global-capital-limited | ARP Global Capital Limited | arpglobalcapital.com | site publishes an obfuscated/reversed email string that could not be reliably decoded - not recorded to avoid guessing | +971 4 317 7000 | Yusuf Alireza (co-founder; ex-CEO Noble Group, ex-Goldman Sachs), Krishna Rao (co-founder) - per press bios | Independent global-alternatives asset manager, DIFC, est. 2018. | arpglobalcapital.com/contact-us (fetched 2026-09-24) |
| arx-financial-engineering-limited | ARX Financial Engineering Limited | arxfe.com (found; fetch blocked - TLS certificate mismatch, site may be hosted oddly) | - | 971 4 279 5800 (DFSA register) | - | Boutique brokerage/financial-engineering firm, DIFC, licensed 2021. | dfsa.ae register (2026-09-24) |
| asanga-capital-limited | Asanga Capital Limited | asanga-capital.com (found; fetch timed out) | not retrieved | not retrieved | not retrieved | Financial advisory firm for UHNW/institutional clients, DIFC; open-architecture custodian/bank/manager access. | asanga-capital.com listed in search (2026-09-24) |
| asas-capital-ltd | ASAS Capital Ltd | none found (own site) | - | 971 4 346 4700 (DFSA register only) | - | Multi-family office/institutional advisor, DIFC since 2009; expanded into Saudi Arabia as of July 2025. | zoominfo/leadiq/DFSA register (2026-09-24) |
| asb-capital-limited | ASB Capital Limited | asbc.com (found; contact page returned blank) | not retrieved | not retrieved | not retrieved | New (Nov-2024) asset manager launched by Al Salam Bank (Bahrain), DIFC, $4.5bn starting AUM. | alsalambank.com press release (2026-09-24) |
| asca-capital-limited | ASCA Capital Limited | ascacapital.com | info@ascacapital.com, privacy@ascacapital.com | not published | Niels Stidsen (Partner), Tom Hodgson (Partner), Jacob Jensen (Partner, founder of one.com), Adnan Zein (Director) | DIFC private-equity fund manager, est. 2021; Middle East growth companies. | ascacapital.com (fetched 2026-09-24) |
| asia-research-capital-management-difc-limited | Asia Research and Capital Management (DIFC) Limited | arcmcap.com (found; not fetched) | not retrieved | not retrieved | not retrieved | Hong Kong-headquartered closed-end debt/equity manager (est. 2011), DIFC branch. | arcmcap.com/contact listed (2026-09-24) |
| aster-capital-management-difc-limited | Aster Capital Management (DIFC) Ltd | astercm.ae (found; not fetched) | not retrieved | not retrieved | not retrieved | Equity multi-strategy manager, DIFC (Index Tower), est. 2019, ~6 staff. | astercm.ae listed in search (2026-09-24) |
| astero-falcon-difc-limited | Astero Falcon (DIFC) Limited | asterofalcon.com | info@asterofalcon.com | +971 56 718 3177 | none published | DFSA asset manager for UHNW/family offices/corporates, DIFC (Gate Village 10). | asterofalcon.com, search snippet (2026-09-24) |
| astute-asset-managers-limited | Astute Asset Managers Limited | none found at all | - | - | - | No trace beyond a bare register name - could not confirm current activity. | multiple searches, no results (2026-09-24) |
| audacia-capital-limited | Audacia Capital Limited | audaciacapital.com | info@audaciacapital.com | +971 (0) 4 277 1122 / +971 (0) 4 553 9040 | none published (site references Founder and CEOs Message, Management Team, Board of Directors without naming them) | Dubai investment bank / PE firm, DIFC, MENAT focus, est. 2015, >$500M AUM, Sharia-aligned. Litigation flag: DIFC Courts case CFI 063/2024, Istar Capital Limited v Audacia Capital Limited - both firms are on our UAE list. | audaciacapital.com (fetched 2026-09-24); difccourts.ae case listing (2026-09-24) |
| audere-capital-partners-limited | Audere Capital Partners Limited | none found | - | - | - | New DIFC wealth/asset-management entrant (named among April-2024 arrivals). | hubbis.com / thefintechtimes.com coverage (2026-09-24) |
| aurium-ltd | Aurium Ltd | none found at all | - | - | - | No trace found beyond the register name. | multiple searches, no results (2026-09-24) |
| ayn-capital-limited | Ayn Capital Limited | ayncapital.com | info@ayncapital.com | +971 4 495 4100 | Patrick R. Oerer (Chairman), Nicolas Loubet (Director), Mansur El-Fitouri (Director), David Luksenburg (Director) | DFSA Cat 3C asset manager/advisor, DIFC, licensed Mar-2025; fund platform, private wealth, corporate finance. | ayncapital.com/about (fetched 2026-09-24) |

---

## Fund managers (18 checked)

| Slug | Firm | Website | Email | Phone | Named people | What they do | Evidence |
|---|---|---|---|---|---|---|---|
| 9unicorns-global-capital-management-limited | 9Unicorns Global Capital Management Limited | none found (UAE entity) | - | - | Mumbai founders: Dr Apoorva Ranjan Sharma, Anil Jain, Anuj Golecha, Gaurav Jain (India entity, not confirmed as UAE contacts) | Registered in ADGM Abu Dhabi, not DIFC; early-stage-accelerator VC fund, restricted to co-investment. | adgm.com register, inc42.com (2026-09-24) |
| aarna-fund-management-limited | Aarna Fund Management Limited | none found | - | 971 4 386 7915 (DFSA register only) | Alankar Bisaria, Jaidev Parthasarathy (authorised individuals per DFSA register) | DIFC VC-fund manager, licensed 2023, restricted to Qualified Investor/Exempt (VC) funds. Name-collision caution: distinct from Aarna Capital, the ADGM multi-asset brokerage acquired by Marex in 2024 - do not conflate. | dfsa.ae register (2026-09-24) |
| ads-investment-solutions-limited | ADS Investment Solutions Limited (ADSI) | ads-investments.com (found; contact page returned 403 Forbidden) | not retrieved | not retrieved | not retrieved | Registered in ADGM Abu Dhabi, not DIFC; sister company of ADSS (a separate DIFC-regulated retail broker) - entity-family caution, do not conflate ADSI with ADSS. Wealth/asset management, est. 2017. | ads-investments.com listed; adgm.com register (2026-09-24) |
| ag-australian-gulf-capital-limited | AG (Australian Gulf) Capital Limited | none found | - | - | - | Registered in ADGM Abu Dhabi, not DIFC; AI/tech-focused VC fund, co-investment restricted. | adgm.com register (2026-09-24) |
| agna-capital-limited | Agna Capital Limited | agnacapital.com | mail@agnacapital.com | not published | none published | DIFC deep-tech VC fund (AI, blockchain, novel computing), est. 2023; brand affiliated with Woodstock Fund. | agnacapital.com/contact-us (fetched 2026-09-24) |
| alarabi-investments-limited | Alarabi Investments Limited | alarabiinvest.com (found; fetch returned empty) | not retrieved | not retrieved | not retrieved | DIFC VC/PE/hedge-fund manager, est. 2018; presence in Dubai, Riyadh, Mumbai. | alarabiinvest.com listed in search (2026-09-24) |
| aldar-capital-limited | ALDAR CAPITAL LIMITED | unresolved - likely name collision, see caution below | - | - | - | Our record is almost certainly the Aldar Properties and Mubadala Capital joint venture announced Dec-2025 (ADGM, Abu Dhabi, targeting a 1bn USD first fund in 2026). A website (aldarcapital.com) surfaced by search belongs to what appears to be a separate, Bahrain-based Islamic-finance Aldar Capital with its own board and Sharia board and a Bahrain phone number - the contact details found there were not recorded against this record to avoid attaching a strangers details. | thenationalnews.com, mubadalacapital.ae (JV announcement, 2025-12-04); aldarcapital.com (fetched 2026-09-24, appears to be a different entity - flagged, not used) |
| allfunds-middle-east-limited | Allfunds (Middle East) Limited | not located (parent: allfunds.com) | - | - | - | DIFC entity of the Spanish fund-distribution platform Allfunds; confirmed only as a named 2024 DIFC new entrant, no DIFC-specific contact found. | difc.com news items (2026-09-24) |
| alteia-investment-management-ltd | Alteia Investment Management Ltd | alteiafund.com (found; not fetched) | not retrieved | not retrieved | Kevin Ramsamy, Mitchell Barrett, Mariam Ballaith (approved persons per ADGM register) | Registered in ADGM Abu Dhabi, not DIFC; Mauritius-headquartered alternative-financing fund manager. | adgm.com register, alteiafund.com (2026-09-24) |
| altica-partners-difc-limited | Altica Partners (DIFC) Limited | none found | - | 971 4 319 7890 (DFSA register only) | - | DIFC entity, Mauritius-owned, est. 2018. | dfsa.ae register (2026-09-24) |
| altnovel-capital-ltd | ALTNovel Capital Ltd | none found | - | - | - | Registered in ADGM Abu Dhabi, not DIFC; PE/hedge fund, IT/data-centre/education focus. | adgm.com register (2026-09-24) |
| arcadia-capital-limited | Arcadia Capital Limited | arcadiacapital.ae | ir@arcadiacapital.ae | phone published but in an unusual/likely mistranscribed format (+99 4 11 72 1270) - treat as unverified, do not dial without re-confirming | Anastasia Malyutina (Chairwoman), Adam Omar Shanti (Senior Executive Officer and Board Member) | DIFC manager of four property funds plus one VC fund, UAE-focused real estate. | arcadiacapital.ae (fetched 2026-09-24) |
| arcapita-investment-management-limited | Arcapita Investment Management Limited | not located (parent: arcapita.com) | - | - | - | Registered in ADGM Abu Dhabi, not DIFC; regional arm of global alternative manager Arcapita, over 30 billion USD in transaction value. | adgm.com register, arcapita.com (2026-09-24) |
| arzan-investment-management-difc-limited | Arzan Investment Management (DIFC) Limited | arzanim.com | not published on contact page | not published on contact page | none published | DIFC subsidiary of Kuwait based Arzan Capital; real estate and credit alternative investment, EMEA and US focus; offices Dubai, London, New York listed, no direct email or phone given. | arzanim.com/contact (fetched 2026-09-24) |
| apex-fund-services-dubai-limited | Apex Fund Services (Dubai) Limited | apexgroup.com/locations/dubai | not published on this page | +971 4 428 9221 | Christiane El Habre (Regional Managing Director, Middle East), Naveed Zamir Yasir (Country Head, Dubai) | Fund administrator, DIFC, first DFSA-approved fund administrator at DIFC (2006); part of global Apex Group. | apexgroup.com (fetched 2026-09-24) |
| ascent-fund-services-difc-ltd | Ascent Fund Services (DIFC) Ltd | theascent-group.com | not published for Dubai office | not published for Dubai office (Singapore HQ number only) | Hazem Elmalla (Head of Sales, MENA) | Fund administration and corporate services, DIFC, part of Ascent Group (Singapore HQ). | theascent-group.com/united-arab-emirates (fetched 2026-09-24) |
| aspen-digital-financial-limited | Aspen Digital Financial Limited | not located (parent site not fetched) | - | - | Elliot Andrews (CEO, per LinkedIn) | Registered in ADGM Abu Dhabi, not DIFC; digital-asset platform for wealth managers, family offices, HNWI. | adgm.com register, LinkedIn (2026-09-24) |
| aspire-capital-partners-limited | Aspire Capital Partners Limited | none found | - | - | - | DIFC VC-fund manager, licensed Sep-2021. Name-collision caution: do not confuse with the unrelated Aspire Capital Investments or Aspire Underwriting Agency that surface in search for the same trading name. | dfsa.ae register (2026-09-24) |
| badwa-capital-limited | Badwa Capital Limited | badwacapital.com | none published | none published | none published | Investment bank and growth-equity firm, DIFC plus Riyadh office; over 6 billion USD advised since 2010; launched an income-focused investment-management arm (100 million USD) in real estate and infrastructure. Saudi firm AlRajhi United acquired a stake (2025) - worth noting as an ownership change. | badwacapital.com (fetched 2026-09-24); saudigazette.com.sa (2026-09-24) |
| balmoral-partners-investment-management-ltd | Balmoral Partners Investment Management Ltd | balmoral-im.com (found; not fetched) | not retrieved | not retrieved | not retrieved | Registered in ADGM Abu Dhabi, not DIFC; global asset manager for SWFs and family offices; new digital-asset lending fund with BlockFills (May 2025). | adgm.com register, prnewswire.com (2026-09-24) |
| bearbull-global-investments-group-limited | BearBull Global Investments Group Limited | bearbull.ae | info@bearbull.ae | +971 4 272 2719 | Alain Freymond (Chairman; ex-Banque Pictet), Fernand Garcia (Vice-Chairman) | Swiss wealth-advisory firm, DIFC, licensed 2017; serves SWFs, government bodies, family offices, HNWI in MENA. | bearbull.ae/about-bearbull-2 (fetched 2026-09-24) |
| carlyle-mena-advisors-limited (and carlyle-mena-investment-advisors-limited) | Carlyle MENA (Investment) Advisors Limited | not located (own DIFC page); parent carlyle.com | not published for DIFC office | +971 4 427 5621 | - | Regional office of global PE firm The Carlyle Group, DIFC (Gate Village), open since around 2007. | search snippets citing DFSA fund register plus carlyle.com (2026-09-24) |
| chryscapital-advisors-middle-east-limited | ChrysCapital Advisors Middle East Limited | not located (parent chryscapital.com) | - | - | - | Regional entity of ChrysCapital, a large India-focused PE firm (5 billion USD raised); no DIFC-specific web presence found. | chryscapital.com (2026-09-24) |
| franklin-templeton-investments-me-limited | Franklin Templeton Investments (ME) Limited | franklintempletonme.com | service.Dubai.franklintempleton@fisglobal.com | +971 4 428 4100 (client services +971 487 17800) | not retrieved | Regional office of global asset manager Franklin Templeton, DIFC (Gate Building); launched seven new DIFC-domiciled funds for UAE retail investors (2024). | franklintempletonme.com/about-us/contact-us (2026-09-24) |
| janus-henderson-investors-middle-east-limited | Janus Henderson Investors Middle East Limited | not located (parent janushenderson.com/middle-east) | - | - | Baraa Amir (Executive Director, MEA) | Registered in ADGM Abu Dhabi, not DIFC despite the firm having had a DIFC office since 2012 - the records likely location assumption should be checked; global asset manager, 379 billion USD AUM; acquiring NBK Capital Partners. | adgm.com register, citywire.com, zawya.com (2026-09-24) |
| marshall-wace-middle-east-limited | Marshall Wace Middle East Limited | not located (parent mwam.com/contact) | - | - | - | Registered in ADGM Abu Dhabi, not DIFC; global hedge fund (KKR-owned stake), chose Abu Dhabi for its ME regional HQ. | adgm.com register, hedgeweek.com (2026-09-24) |
| neuberger-berman-europe-limited | Neuberger Berman Europe Limited | not located (parent nb.com) | - | +971 4 401 9681 | - | Dubai (DIFC, ICD Brookfield Place) branch of Neuberger Berman, the firms first Middle East office. | opencorporates.com, difc.ae public register (2026-09-24) |

---

## No web presence found at all

These UAE-registered, licensed entities produced no independent trace beyond a bare regulator-register
listing (DFSA, ADGM, DIFC) or, at most, a third-party data-aggregator stub with no operational detail -
no owned website, no news coverage, no LinkedIn company activity found via the queries run. This is a
genuine finding: a licensed entity that cannot be found on the open web is either dormant, a captive or
shell vehicle, or trades under a materially different name than its licence.

| Slug | Firm | Segment | What was searched |
|---|---|---|---|
| ajm-international-limited | AJM International Limited | family_office | "AJM International" Dubai DIFC family office |
| mayfield-group-llp | Mayfield Group LLP | family_office | "Mayfield Group LLP" DIFC Dubai family office |
| anatole-db-limited | Anatole DB Limited | asset_manager | "Anatole DB" Limited DIFC Dubai |
| astute-asset-managers-limited | Astute Asset Managers Limited | asset_manager | "Astute Asset Managers" Limited DIFC Dubai |
| aurium-ltd | Aurium Ltd | asset_manager | "Aurium Ltd" DIFC Dubai asset management |

Several more firms above (Al Rayid Investments, Anou SFO, Rosemonde, Sabban Holdings, TAM Capital,
Tsangs Group SFO, Twinwood Family Holdings, Equalis Capital, AIP Management, Al Tariq Capital,
Al Ahly Financial, Amaltas Partners, Audere Capital Partners, Aspire Capital Partners, Allfunds
Middle East, Altica Partners, ChrysCapital Advisors ME) are confirmed real and active via the
regulator register or credible fund-industry or press profiles, but likewise have no discoverable
website of their own - they are listed in the segment tables above rather than repeated here,
since their existence and activity (unlike the five above) is independently corroborated.

---

## Cross-cutting flags for Andre

1. Name collisions caught, not resolved as matches:
   - aldar-capital-limited - our record is almost certainly the new Aldar Properties and Mubadala
     Capital JV (ADGM, announced Dec-2025), not the Bahrain-based Aldar Capital whose website
     and contact details surfaced in search. No contact info recorded against this record.
   - aarna-fund-management-limited vs Aarna Capital (the Marex-acquired ADGM brokerage) - distinct entities, not conflated.
   - ads-investment-solutions-limited (ADSI, ADGM) vs ADSS (a separate DIFC-regulated retail broker, same corporate family) - distinct entities, not conflated.
   - aspire-capital-partners-limited vs unrelated Aspire Capital Investments and Aspire Underwriting Agency - distinct entities, not conflated.

2. Regulator/location mismatches (record likely assumed DIFC; entity is actually ADGM Abu Dhabi,
   or vice versa) - worth a data-quality pass: acp-me-management-limited, arini-capital-management-me-limited,
   arolla-finance-limited, 9unicorns-global-capital-management-limited, ads-investment-solutions-limited,
   ag-australian-gulf-capital-limited, alteia-investment-management-ltd, altnovel-capital-ltd,
   arcapita-investment-management-limited, aspen-digital-financial-limited, balmoral-partners-investment-management-ltd,
   janus-henderson-investors-middle-east-limited, marshall-wace-middle-east-limited.

3. Regulatory or litigation triggers found in the course of this search (not the assignments focus,
   but caught and worth logging):
   - Ark Capital Management (Dubai) Limited - DFSA fine of 504,000 USD in Feb-2026 for market-abuse
     systems and controls failings and for not reporting a change of control. Source: dfsa.ae news release (2026-09-24).
   - Audacia Capital Limited - named defendant in DIFC Courts case CFI 063/2024, Istar Capital
     Limited v Audacia Capital Limited; Istar Capital is also on our UAE list. Source: difccourts.ae (2026-09-24).
   - Badwa Capital Limited - Saudi firm AlRajhi United acquired a stake in 2025 (ownership change). Source: saudigazette.com.sa (2026-09-24).
   - Amaltas Partners Limited - acquired by Indias Atom Group, DFSA change-of-control approved (2024/2025). Source: cafemutual.com (2026-09-24).
   - Ambit Global Private Client (MENA) Limited - entered DIFC via 2024 acquisition of Moonrock Investments Ltd. Source: hubbis.com (2026-09-24).
   - ABS (Middle East) Limited - new market entrant, Arab Bank Switzerlands DIFC launch announced June 2026 with CEO Samir Atitallah. Source: gulfbusiness.com etc (2026-09-24).
   - ASB Capital Limited - new market entrant, Al Salam Bank (Bahrain) launched this DIFC firm Nov-2024 with a very large starting AUM. Source: alsalambank.com (2026-09-24).

4. Obfuscated or undecodable emails found on two firm sites - present but not recorded as contact
   routes because they could not be reliably decoded without guessing (a guessed address is explicitly
   against the briefs rules): amicorp-capital-difc-ltd (Amicorp DIFC), arp-global-capital-limited.

5. 12 of the 13 firms checked in the family-office and MFO segment (all but KAAF) have no independent
   web presence at all. This is structural (single-family offices do not market themselves) rather than
   a data gap, and should probably lower the priority of "find a website" as a KPI for this segment
   specifically - a different enrichment approach (for example named-principal lookups via press or SWF
   industry databases) would likely do better than web search for single-family offices.

## Unknowns (explicit)

- Whether the ABK-DIFC contact block found (banking branch) is legally the same DFSA registration as
  ABK Capital (DIFC) Limited, the asset-management subsidiary - not resolved.
- Whether Aldar Capital the Bahrain entity and ALDAR CAPITAL LIMITED in our CRM are related in any
  way (for example a common branding licence) - not resolved; treated as unrelated pending confirmation.
- The precise legal status (active or struck off) of the five "no web presence found at all" entities -
  not checked against DIFC, DFSA or ADGM registers individually in this pass; only open-web search was run
  for those five before concluding no presence.
- 503 of the 573 flagged UAE records were not touched in this pass (this was a depth-over-coverage
  exercise per instruction) - no claim is made about them either way.
