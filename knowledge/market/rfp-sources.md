# RFP / Tender Source Registry — UAE, Saudi Arabia, Lebanon, France

Owner: sales research (for Andre Geha). Purpose: where to look for procurement notices,
tenders and RFPs relevant to Gaia (portfolio management, OMS/FIX, risk & compliance, fund
administration/NAV, back office, reporting, client web portal) across OFS's four markets.

**This is a source registry, not a live scan.** It does not claim any specific tender exists
today. Re-check before relying on any single line for an active pursuit.

## ⚠ UPDATE 2026-09-22 (laptop run) — what is now LIVE-VERIFIED

The access note below was written from the cloud sandbox and its blanket "nothing was
live-verified" caveat **no longer applies to everything**. A radar pass run from Andre's laptop,
with normal internet, established the following. Treat this block as authoritative where it
conflicts with the older text.

### ⚠ What a "zero" on these portals actually means — read before quoting the result

**BOAMP, PLACE and TED carry PUBLIC procurement only.** BOAMP is the *Bulletin Officiel des Annonces
des Marchés Publics*: notices from *acheteurs publics* under the Code de la commande publique — the
State, local authorities, hospitals, public establishments, and *entités adjudicatrices* (network and
utility operators). PLACE is the State's own platform. TED is EU-wide public procurement.

**Our buyers are private firms.** Family offices, MFOs, private and investment banks, and asset and
fund managers are under no obligation to publish anything, and they do not. **No amount of coverage
on these portals will ever see them.** A "measured zero" on BOAMP and TED is therefore a genuine
zero *of French and EU public-sector tenders for this software category* — it says almost nothing
about the market we actually sell into.

Two further limits even inside the public sector: **sub-threshold purchases need not be published**
at all, and a public body can buy through an existing framework agreement (*accord-cadre*) or a
central purchasing body (UGAP) without a new notice ever appearing.

**Who this channel CAN see, and it is a short list:** public and para-public investors that genuinely
run portfolios — Caisse des Dépôts, FRR, ERAFP, Ircantec, CNBF, CAVAMAC, CIPAV, FGDR, Banque de
France, the AMF itself — plus donor-funded public-financial-management projects. Real buyers, but a
narrow and slow-moving set.

**The strategic consequence, stated plainly:** the RFP radar is a **minority channel** for us and
always will be. It is worth running because a missed public tender is unrecoverable and the alerts
are free — but **the main engine is the licence registers plus trigger-based outbound**, which is
where the build effort went. Do not let a clean radar report read as "the market is quiet".

### BOAMP vs PLACE — they are not the same thing (verified live 2026-09-22)

Andre asked whether what is on BOAMP is also on PLACE. **No — they are different kinds of thing,
and neither contains the other.**

| | **BOAMP** | **PLACE** |
|---|---|---|
| What it is | The **legal advertising bulletin** (*Bulletin Officiel des Annonces des Marchés Publics*), run by DILA. Where a notice is **published**. | A **dematerialisation platform** where the consultation is actually **hosted and run** — documents, questions, bid submission. |
| Who appears | **Every** public buyer required to advertise above threshold — State, **local authorities**, hospitals, public establishments. | Per PLACE's own scope statement: State central and deconcentrated services, State public establishments, independent public and administrative authorities, GIPs, GIEs with a national public-service mission, **social security bodies**, UCANSS, and the **Caisse des Dépôts et Consignations**. |
| Not there | Consultation documents (it is a notice, not a dossier). | **Local authorities** — communes, départements, régions — which mostly use other platforms (Maximilien, AWS-achat, e-marchespublics, achatpublic.com, Klekoon…). |

**So:** a local-authority tender appears on **BOAMP but not PLACE**. A State sub-threshold
consultation can appear on **PLACE but never on BOAMP**. Watching one does not cover the other.

**Caisse des Dépôts being on PLACE matters to us** — it is one of the few genuinely
portfolio-running public buyers in France.

### Using PLACE in practice (tested 2026-09-22)
- ✅ **No account is needed to search or browse.** An anonymous visitor gets full results —
  reference, object, buyer, deadline — and can even **download the *règlement de consultation***.
- 🔑 **An account IS needed for three things:** saved-search **email alerts** ("Mes alertes"), the
  *panier*, and actually **responding** to a consultation.
- ⚠ **The keyword search is NOT automatable by URL.** PLACE runs on PRADO with a stateful
  postback (`PRADO_PAGESTATE`): `…&keyWord=gestion+de+portefeuille` looks like it should work and
  **silently returns the unfiltered list instead**. Verified — three different keywords all returned
  the identical 121 results. **Do not build a scraper on that URL; it would report false positives
  forever.**
- 📉 **PLACE carried only ~121 open consultations in total** on 2026-09-22 — across every buyer and
  category. Small enough that a human can simply scan the lot periodically. That is a far better use
  of time than automating it.
- ✅ **BOAMP, by contrast, HAS a genuine Opendatasoft API** and is properly automatable — which is
  how the radar searched it. **Automate BOAMP; alert-or-eyeball PLACE.**

**Searched successfully, via each portal's real API (high confidence):**
| Portal | How | Coverage achieved |
|---|---|---|
| **TED** (`api.ted.europa.eu`) | Live search API, 15 query variants, EN + FR, date-filtered to 2025+ | Full. A genuine, measured zero for France. |
| **BOAMP** (Opendatasoft API) | Live API, 11 query variants in French, 2025+ | Full. A genuine, measured zero. |
| **UAE Ministry of Finance** | Server-rendered listing, read directly | 9 open tenders, none relevant |

**Blocked or unreachable (these are gaps, NOT zeros):**
| Portal | What happened |
|---|---|
| **Etimad** (Saudi) | The site's **own bot-detection challenge** (F5 TSPD / `APM_DO_NOT_TOUCH`) is served instead of content, on every endpoint and user agent tried. ⚠ **Saudi Arabia therefore has ZERO real tender-search coverage.** The Arabic queries were never actually run against Etimad's search. Needs a human with a browser — ideally a registered Etimad supplier account. **We do not attempt to defeat bot protection.** |
| **Abu Dhabi ADGPG**, **Dubai eSupply** | JavaScript single-page apps; a plain fetch sees no listing at all. Unreached, not checked. |
| **Saudi CMA** (`cma.gov.sa`) | WAF rejects some paths; the Open Data **API backend is unreachable from Europe** (see `tools/connectors/cma_saudi.py`). Note the domain moved: **`cma.org.sa` → `cma.gov.sa`**. |

**🎯 The most actionable finding: free saved-search EMAIL ALERTS exist and beat any scraper.**
| Portal | Mechanism | Account | Cost | Where |
|---|---|---|---|---|
| **BOAMP** | "Service d'alerte" — up to 10 saved searches, emailed on publication | Yes (email or FranceConnect) | **Free** | https://compte.boamp.fr · https://www.boamp.fr/pages/entreprise-service-dalerte/ |
| **PLACE** | "Mes alertes et recherches sauvegardées" — daily/weekly digest | Yes ("espace entreprise") | **Free** | marches-publics.gouv.fr → `?page=Entreprise.EntrepriseHome` |
| **TED** | "My TED" — save a search, up to 25 alerts, daily digest | EU Login | **Free** | https://ted.europa.eu/en/help/ted-account — ⚠ steps corroborated second-hand; verify on first login |
| **Etimad** | A notifications feature is reported to exist for registered suppliers | Supplier registration | Unconfirmed | ⚠ **Low confidence — unverified.** Do not automate against this until a human has logged in. |

**Two false-positive classes to keep rejecting** (both cost real time this run):
1. "**portefeuille**" in French public procurement usually means an **IP/patent portfolio** or
   **project** portfolio management — not investment. Same trap as the English "corporate
   portfolio management".
2. Public pension funds (**FRR, ERAFP, CNBF, CAVAMAC, CIPAV, FGDR, Carpimko, CNAVPL, Ircantec**)
   tender **asset-manager mandates and financial advisory**, never software. We do not bid on
   these — but **whoever wins one is a buyer**, and a new mandate is a trigger for lead sourcing.

**Near-misses, recorded so they are not re-found:**
- **Council of Europe Development Bank** (Paris) — a real "capital markets and loan operations
  management system" procurement, TED `140323-2025` and `288127-2025`. **Deadline 2025-06-06 —
  closed over a year ago.** Proof that this category *does* surface on TED occasionally.
- **KfW Bankengruppe** (Germany) — "Investment management software package — Portfolio Management
  System", TED `479374-2026` / `498376-2026`, deadline 2026-08-10. **Germany is outside our
  markets.** Awareness only.

## Verification / access note — read this first

Every source below was identified and corroborated via web search on **2026-09-22**. In this
research session, direct page loads (browser-fetch tool and `curl`) to essentially all external
domains were **blocked by the sandbox's outbound network policy** — including to completely
uncontroversial sites such as `en.wikipedia.org`. That block is a property of this session's
environment, not of the target sites.

Practically, this means: every URL below is "**search-verified 2026-09-22**" — i.e. it appeared,
with a matching description, in indexed search results on that date — but **no URL here was
confirmed by an actual live page load in this session**. Search-engine indexes lag reality by
days to months, and government/financial-sector portals in these markets change URLs relatively
often (two are flagged below as having changed within the last two years).

**Before wiring any automated monitoring (RSS, saved search, scraper) off this file, load each
URL once from a normal internet connection to confirm it resolves and matches the description.**
Where I could not even find a search-indexed candidate for something the brief asked for, I have
written **unknown** rather than guess — see "What we cannot see" at the end.

---

## 1. United Arab Emirates

Note on structure: the UAE has **no single national tender portal**. Procurement is split
federal / emirate (Abu Dhabi, Dubai) / free-zone (DIFC, ADGM), each with its own system.

| Source | Covers | URL | Access | Language | Monitorable | Notes |
|---|---|---|---|---|---|---|
| UAE federal government — official portal (u.ae) | Explains the federal tendering/supplier-registration framework; gateway page, not a live tender list itself | https://u.ae/en/information-and-services/business/government-tendering-and-awarding | Free | English/Arabic | No (informational page) | Points to the Ministry of Finance's federal e-Procurement/Digital Procurement Platform for actual tenders |
| UAE Ministry of Finance — Digital Procurement Platform / current opportunities | Federal government tenders and auctions | https://mof.gov.ae/tenders-and-auctions/ | Free to view; registration to bid (Federal Supplier Register) | English/Arabic | Manual check; unknown if RSS/email alerts exist | Governed by Federal Decree-Law No. 11 of 2023 on Federal Government Procurement; SME bidders get a scoring bonus |
| Abu Dhabi Government Procurement Gate (ADGPG) | All Abu Dhabi government-entity tenders (SAP Ariba-based, ~run by Department of Government Support) | https://www.adgpg.gov.ae/ (supplier tender list: https://supplier.adgpg.gov.ae/pages/tender-list.html) | Tender list viewable; registration (ADERP) required to bid | English/Arabic | Email alert subscription available after registration, per the portal's own description | **Caveat:** search also surfaced `https://beta.adgpg.gov.ae/`, apparently a redesigned version of the same portal — unknown which is now canonical; confirm before relying on either |
| Dubai eSupply (JAGGAER) | Bidding tenders/RFx from ~40 major Dubai government entities, incl. Dubai Municipality | https://esupply.dubai.gov.ae/ | Registration required to bid; tender listing viewable | English/Arabic | Likely — registered suppliers can receive notifications (unconfirmed in detail) | Central hub; Dubai Municipality tenders (dm.gov.ae/municipality-business/tenders-biddings/) also route through it |
| Digital Dubai — iSupplier | Tenders specific to Digital Dubai (the government's digital-transformation entity) | https://www.digitaldubai.ae/tenders | Registration to bid | English/Arabic | Unknown | Narrower scope than eSupply; relevant if Digital Dubai runs cross-government fintech/data initiatives |
| UAE Ministry of Finance — federal current business opportunities | Overlaps with the "Digital Procurement Platform" entry above | https://mof.gov.ae/tenders-and-auctions/ | Free | English/Arabic | Manual | Same portal, listed once above; kept here for completeness of search trail |
| Central Bank of the UAE (CBUAE) — e-Procurement | CBUAE's own vendor tenders (its IT, market-infrastructure and services procurement) | https://eservices.centralbank.ae/eprocurement/ | Registration required | English/Arabic | Unknown (portal-based, no confirmed alert feature) | High-value signal source: a central bank tendering for market/payment infrastructure is a strong "reason to buy" trigger if it ever touches investment/portfolio systems |
| UAE Securities & Commodities Authority (SCA) → renamed **Capital Market Authority** 1 Jan 2026 | **Not a tender board.** Open-data register of licensed companies/entities (brokers, asset managers, etc.) | Old: https://www.sca.gov.ae/en/open-data/licensed-companies.aspx · New: https://www.uaecma.gov.ae/en/open-data/licensed-companies.aspx | Free | English/Arabic | Yes — a static list; re-pull monthly and diff for new entrants | **Disambiguation:** per Federal Laws No. 32 and No. 33 of 2025, the SCA was renamed/restructured into a body called "Capital Market Authority" effective 1 Jan 2026. Do **not** confuse this UAE CMA with Saudi Arabia's Capital Market Authority (cma.org.sa) or Lebanon's Capital Markets Authority (cma.gov.lb) — three unrelated regulators share the acronym. This is itself a regulatory-change trigger worth a line in `memory/open-questions.md` if it affects any current UAE contact's registration |
| DFSA (DIFC's regulator) | Regulates DIFC-based firms | https://www.dfsa.ae | — | English | — | **No public procurement/tender board for DFSA itself was found.** Unknown whether one exists. Its value to us is as a **register of newly authorised DIFC firms** (prospecting signal), not as an RFP source |
| ADGM / FSRA (Abu Dhabi Global Market) | Regulates ADGM-based firms | https://www.adgm.com | — | English | — | Same caveat as DFSA: **no public tender board found**; treat as unknown, not "none." Register of authorised persons is the useful signal |
| Sovereign wealth funds — ADIA | Abu Dhabi Investment Authority | https://www.adia.ae | — | English | — | **No public vendor/RFP portal found.** Unknown whether one exists behind a vendor login |
| Sovereign wealth funds — Mubadala | Mubadala Investment Company and its operating companies | https://www.mubadala.com/en/a-guide-for-suppliers (energy arm: https://mubadalaenergy.com/supplier-connect/) | Supplier guidance published; ICV/localisation certificate typically required | English/Arabic | Unknown | General supplier-registration guidance is public; no evidence of open software/IT RFPs being posted — likely invitation-driven per portfolio company |
| Sovereign wealth funds — ADQ | Abu Dhabi holding company | https://www.adq.ae (unverified) | — | — | — | **No procurement portal found.** Unknown |
| Third-party aggregators (backstop, not official) | Mirror/scrape official UAE tenders, add search/filter | uaetenders.com · tendersontime.com/uae-tenders · globaltenders.com/united-arab-emirates-tenders · openopps.com/sources/uae-federal | Mostly paid/freemium | English | Yes — this is their business model | Useful as a keyword-alert backstop across scattered official portals, but always confirm against the primary source before acting |

## 2. Saudi Arabia

| Source | Covers | URL | Access | Language | Monitorable | Notes |
|---|---|---|---|---|---|---|
| **Etimad** (اعتماد) | National unified e-procurement platform for essentially all Saudi government tenders, operated by the National Center for Government Resource Systems (NCGRS) under the Ministry of Finance | https://etimad.sa (English gateway also referenced via my.gov.sa: https://my.gov.sa/en/content/e-procurement) | Free to browse; supplier registration + prequalification to bid | Arabic (primary), English portions available | Yes — supports keyword search and, per third-party guides, saved searches/alerts | Since 2018; central point covering essentially all ministries and many public entities. **Primary daily-check source for KSA.** SAMA and other public financial bodies' larger tenders are expected to route through here (unconfirmed for SAMA specifically — see below) |
| Ministry of Finance — Tenders and Procurement | MoF's own tenders page, largely a gateway | https://www.mof.gov.sa/en/tenders/Pages/default.aspx | Free | English/Arabic | Manual | Likely links back into Etimad for the live workflow |
| SAMA (Saudi Central Bank) — Suppliers Management Portal | SAMA's own procurement and vendor relations (its IT, market-infrastructure and services purchases) | https://www.sama.gov.sa/en-us/services/procurementandvendorrelations/pages/default.aspx | Registration required | English/Arabic | Unknown | High-value signal: SAMA procuring payment/market-infrastructure technology is a strong contextual trigger even when it's not directly a Gaia-shaped RFP |
| Saudi **Capital Market Authority** (CMA) — cma.org.sa | Securities regulator. **Not a tender board** — publishes the official list of licensed Capital Market Institutions (CMIs, incl. asset managers) and licensed investment funds | https://cma.org.sa/en (licensed funds: https://cma.gov.sa/en/Market/imf/Pages/default.aspx — note: two live domains, `cma.org.sa` and `cma.gov.sa`, both surfaced in search; confirm which is current) | Free | English/Arabic | Yes — static/registry pages, diff monthly for new licensees | **Disambiguation:** this is the Saudi securities regulator, distinct from SAMA (the central bank) and from Lebanon's and the UAE's differently-named "CMA"s. As of Feb 2025 reporting, ~188 CMIs were listed. New CMI or fund-manager licences are a direct prospecting signal — a newly licensed asset manager needs a PMS |
| Public Investment Fund (PIF) — "Become a supplier" / MUSAHAMA | PIF and portfolio-company ("giga-project": NEOM, Red Sea, Qiddiya, etc.) supplier onboarding | https://www.pif.gov.sa/en/private-sector-hub/become-a-supplier/ | Registration; Saudi legal entity + localisation commitment generally expected | English/Arabic | Unknown | No evidence of a centralised, browsable software/IT RFP list; each PIF portfolio company appears to run its own procurement. Treat as **relationship/localisation-gated**, not a source to monitor for open tenders |
| Third-party aggregators (backstop) | Mirror Saudi tenders with search/filter | selltostate.com/blog/country/saudi-arabia · protenders.com · tendersontime.com/saudi-arabia-tenders · tendersinfo.com/global-saudi-arabia-tenders.php · globaltenders.com/government-tenders-saudi-arabia | Mostly paid/freemium | English | Yes | Backstop only; Etimad is the primary source |

## 3. Lebanon

Context that matters for how to read this table: Lebanon has been in an unresolved banking and
financial crisis since 2019 (capital controls, no functioning secondary market for most bank
assets). This is **industry-wide public knowledge, not a specific claim about any OFS client**,
and it materially affects how procurement actually happens here — see "What we cannot see" below.

| Source | Covers | URL | Access | Language | Monitorable | Notes |
|---|---|---|---|---|---|---|
| Public Procurement Authority / Central Tender Board (PPA/CTB) | Lebanon's central public-procurement portal under Public Procurement Law No. 244/2021 — notices, plans, documents, data and reports | https://ppa.gov.lb | Free (expected) | Arabic primary; French/English coverage unconfirmed | Unknown — could not confirm RSS/email alert features | **Could not verify the site is currently reachable or actively maintained in this session** (see verification note above) — flagged, not asserted as broken. This is the legally correct body ("Tender Board") for Lebanese public procurement |
| Banque du Liban (BDL) | Lebanon's central bank | https://www.bdl.gov.lb | Free | Arabic/French/English (site generally) | Unknown | **No dedicated public tender/RFP board found.** BDL issues circulars and decisions publicly but no evidence of an open vendor-procurement portal; unknown whether one exists |
| Capital Markets Authority — Lebanon (CMA) | Securities regulator, chaired by the BDL Governor | https://www.cma.gov.lb | Free | Arabic/English (site generally) | Unknown | **No procurement/tender section found.** Disambiguation: this is **not** Saudi Arabia's CMA or the UAE's newly-renamed CMA — three separate bodies. Worth monitoring for licensing announcements as a prospecting signal, not as an RFP source |
| Association of Banks in Lebanon (ABL) | Lebanese banking-sector trade association | https://www.abl.org.lb | Free | English/Arabic | No (not a tender source) | Not a procurement channel, but the sector's own network/publications and the practical route for introductions given the opacity noted below |
| World Bank Projects & Operations — Lebanon | Donor-funded (World Bank, and similarly EU-funded) Lebanese government IT/institutional-strengthening projects, which do publish formal procurement plans | https://projects.worldbank.org (search "Lebanon") | Free | English | Partially — World Bank procurement notices are indexed and searchable | Relevant if any donor-funded public-financial-management or capital-markets modernisation project ever includes an investment-systems component; worth a periodic keyword search rather than a standing watch |
| Third-party aggregators (backstop) | Mirror Lebanese tenders | lebanontenders.com · tendersontime.com/lebanon-tenders · biddetail.com/lebanon-tenders · tendersinfo.com/global-lebanon-tenders.php · globaltenders.com/government-tenders-lebanon | Mostly paid/freemium | English | Yes | Given uncertainty over ppa.gov.lb's current state, these aggregators may currently be the more practically checkable window into Lebanese public tenders — but they are unofficial and unverified as to how they source their data |

## 4. France

France is comparatively well-instrumented: procurement is centralised through statutory,
free, alert-capable platforms.

| Source | Covers | URL | Access | Language | Monitorable | Notes |
|---|---|---|---|---|---|---|
| **BOAMP** (Bulletin Officiel des Annonces des Marchés Publics) | Mandatory publication channel for French public contracts between national and EU thresholds — all levels of government, ministries to communes | https://www.boamp.fr | Free | French | **Yes — saved searches + email alerts**, per the platform's own functionality | Run by DILA (Direction de l'Information Légale et Administrative). The single best French discovery layer; contracts above EU thresholds are also forwarded to TED |
| **PLACE** (Plateforme des Achats de l'État) | The State's own dematerialised procurement platform — central administrations, decentralised services, some public bodies host their consultation documents and receive bids here | https://www.marches-publics.gouv.fr | Free | French | Yes — "espace entreprise" with saved alerts, per AIFE's own description | Operated by AIFE (Agence pour l'Informatique Financière de l'État). As of end-2025 reporting: ~4,759 purchasing entities, 344,000 registered companies |
| **TED** (Tenders Electronic Daily) | EU-wide notices above EU procurement thresholds, incl. French contracting authorities | https://ted.europa.eu | Free | All 24 EU languages, incl. French | Yes — "My TED" saved searches with email alerts | Publishes ~700,000 notices/year across the EU; useful for the larger French IT/financial-infrastructure tenders that clear EU thresholds |
| Banque de France — Achats et marchés publics | Banque de France's own procurement (IT, market-infrastructure and services purchases) | https://www.banque-france.fr/fr/a-votre-service/achats-et-marches-publics — live consultations via https://achats-consultations.banque-france.fr and a legacy platform at https://banque-france.achatpublic.com for pre-Sept-2020 consultations | Free registration for alerts | French | Yes — "s'inscrire gratuitement pour recevoir les alertes de consultations lancées par la Banque de France" per the portal's own text | High-value signal: the central bank buying market/financial-infrastructure software is directly relevant context even when the tender itself isn't Gaia-shaped |
| ACPR (banking & insurance supervisor, part of Banque de France) — Registre officiel / listes d'agréments | **Not a tender board** — official list of authorisations and withdrawals of authorisation for credit institutions, payment institutions, e-money institutions, insurers | https://acpr.banque-france.fr/fr/reglementation/registre-officiel/listes | Free | French | Yes — static list, updated regularly (examples seen dated Feb–Mar 2026); diff periodically | Newly authorised credit/payment/insurance institutions are a prospecting signal, not an RFP feed |
| AMF (Autorité des marchés financiers) — GECO / open data | **Not primarily a tender board for us** — GECO is the AMF's registry of licensed "sociétés de gestion de portefeuille" (asset managers); the same list is republished as open data | https://geco.amf-france.org/liste-des-societes-de-gestion-agrees-francaise and https://www.data.gouv.fr/datasets/liste-des-societes-de-gestion-de-portefeuille-sgp-agreees-par-lamf | Free, downloadable dataset | French | Yes — dataset can be re-pulled and diffed | As of Feb 2026 reporting, 227 licensed asset managers in France. This is the **single best French prospecting signal**: a newly licensed asset manager will need a portfolio-management system. (Note: the AMF itself also occasionally appears as a *buyer* on BOAMP/e-marchespublics for its own internal IT — not relevant to us) |
| L'Agefi / NewsManagers | French financial-sector trade press; asset management, institutional investors, wealth management | https://www.agefi.fr and https://www.newsmanagers.com | Largely subscription/paid; some free headlines | French | Manual monitoring; NewsManagers publishes frequent short articles well-suited to a periodic scan | Best press source for "X selects Y platform" / new-fund-launch / new-licence signals in the French market |
| Third-party/generic aggregators (France) | Mirror BOAMP/PLACE notices with added search/filter | e-marchespublics.com · marchesonline.com · marches-publics.com · achatpublic.com | Mostly free tiers with paid upgrades | French | Yes | Useful as a keyword-alert backstop layered on top of BOAMP/PLACE, e.g. to filter specifically for financial-sector buyers |

---

## What to search for

Use these as saved-search / alert keywords on the platforms above (BOAMP, PLACE, TED, Etimad,
and any aggregator with keyword alerts). Combine with the buyer type where the platform allows
sector filters (banks, asset managers, insurers, public funds).

**English**
- "portfolio management system" RFP / tender
- "asset management platform" tender / selects
- "fund administration system" procurement
- "order management system" OMS tender bank
- "core investment management system" replacement
- "NAV calculation system" RFP
- "front-to-back office system" bank / asset manager
- "wealth management platform" selects / RFP
- "custody system" tender
- "investment management software" vendor selection

**French**
- "appel d'offres système de gestion de portefeuille"
- "appel d'offres logiciel de gestion d'actifs"
- "marché public système d'information gestion de fonds"
- "consultation système front office trading"
- "RFP système de gestion des ordres"
- "logiciel back-office gestion d'actifs" appel d'offres
- "système de calcul de la valeur liquidative" (VL) appel d'offres
- "plateforme de gestion de fortune" appel d'offres

**Arabic**
- مناقصة نظام إدارة المحافظ الاستثمارية (tender — portfolio management system)
- طرح نظام إدارة الأصول (RFP — asset management system)
- مناقصة نظام إدارة الصناديق الاستثمارية (tender — fund management system)
- نظام إدارة أوامر التداول (order management system)
- نظام الحفظ الأمين (custody system)
- منصة إدارة الثروات (wealth management platform)
- نظام صافي قيمة الأصول (NAV system)

---

## Monitoring recommendation

**Daily automated (RSS / saved-search email — worth subscribing to directly):**
- BOAMP — saved search + email alert (France)
- PLACE — company-space alert (France)
- TED — "My TED" saved search alert (France / EU-threshold notices)
- Etimad — saved search, once a supplier account exists (Saudi Arabia)

**Weekly manual scan (lower volume, each hit highly qualified — worth a person's time, not worth building a scraper for):**
- SAMA Suppliers Management Portal, CBUAE e-Procurement, Banque de France procurement portal —
  central-bank-level tenders are rare but significant context even when not Gaia-shaped
- Dubai eSupply and Abu Dhabi ADGPG tender lists (once the ADGPG canonical URL is confirmed)
- MEED tenders section, *if* a subscription exists or is acquired — best-in-class for MENA
  finance-sector project/tender tracking, but paid

**Monthly (registries move slowly; a daily check would be wasted effort):**
- AMF GECO / data.gouv.fr list of licensed French asset managers — diff for new entrants
- ACPR list of new authorisations/withdrawals (France)
- Saudi CMA list of licensed CMIs and licensed funds
- UAE SCA/Capital Market Authority open-data list of licensed companies
- These four are **prospecting signals, not RFP feeds** — a new licence means a buyer will
  eventually need a system, not that a tender exists today

**Opportunistic / press-scanning (manual, judgement-based):**
- L'Agefi / NewsManagers (France), Executive Magazine (Lebanon), Zawya / Argaam (Gulf), and
  LinkedIn posts from banks'/asset managers' own accounts — the classic "X selects Y platform" /
  "X launches fund" / "X gets licence" signal, best caught by a human reading trade press, not
  by an automated feed
- PIF / Mubadala / ADIA / ADQ supplier pages — low signal for our category specifically
  (mostly construction/services procurement); a quarterly glance is enough

**Realistically not automatable at all, in any market:**
- Anything invitation-only (the majority of PMS/OMS/fund-admin RFPs — see below)
- Lebanon generally, given the unresolved status of ppa.gov.lb in this check and the
  relationship-driven nature of the sector post-2019

---

## What we cannot see

- **The great majority of relevant RFPs are never published anywhere public.** Banks, asset
  managers, family offices and fund managers overwhelmingly run PMS/OMS/fund-administration
  selections by direct invitation to a shortlist, not by open tender. This is true in all four
  markets and is the global norm for this software category. Public portals mostly surface: (a)
  government- or SWF-owned entities' IT procurement, (b) large central-bank market-infrastructure
  projects, (c) a regulator's own internal IT. The practical alternative is what OFS already
  does — direct relationships with banks/asset managers (see `accounts/`), local partners and
  integrators in KSA/UAE, and the regulator/industry-association networks (SAMA and Saudi CMA in
  KSA; CBUAE and the UAE's Capital Market Authority in the UAE; ABL in Lebanon; Banque de France,
  ACPR and AMF-adjacent bodies such as Paris Europlace or France Fintech in France) — reacting to
  the *licensing* signal (new CMI/AMC/asset-manager registrations) before an RFP is even drafted.
- **Lebanon — ppa.gov.lb:** could not confirm in this session whether the site is currently live,
  actively maintained, or in which languages. Flagged, not asserted as broken. Independently,
  Lebanon's banking sector has been in an unresolved, publicly documented financial crisis since
  2019; whether any Lebanese financial institution currently has budget/appetite for a PMS
  procurement is **unknown** and not something this registry can or should imply either way.
- **ADIA, ADQ, DIFC/ADGM (DFSA/FSRA):** no public procurement or tender board was found for any
  of these via search. Unknown whether one exists behind a pre-registered-vendor login, as
  opposed to not existing at all — treat as "unknown," not "closed."
- **Saudi PIF and its giga-project subsidiaries (NEOM, Red Sea, Qiddiya, etc.):** procurement is
  heavily gated by Saudization/localisation requirements and appears to be run per-subsidiary;
  no centralised, browsable software/IT RFP list was found. Unknown whether investment-systems
  procurement for PIF's own portfolio-management function is ever put to open tender.
- **Verification depth generally:** as stated at the top of this file, no URL here was confirmed
  by a live page load in this session because outbound access to essentially all external
  domains was blocked by this sandbox's network policy. Confirm each URL loads before relying
  on it operationally.

---

*Compiled 2026-09-22 by sales research, for Andre Geha / OFS Business Development. Sources are
search-indexed as of that date (see verification note above) — re-verify before operational use.*

## Correction, 2026-09-25 — Lebanon's PPA IS reachable

This file previously recorded Lebanon's Public Procurement Authority as unconfirmed/unreachable.
**That is wrong.** Probed live 2026-09-25: the PPA portal is up, structured, and carries a
**"Banking and Financial Services" category** with **Banque du Liban as a registered buyer** — and
BDL's own homepage links its Procurement page straight to a filtered PPA URL. Measured: 30 active
tenders, 3 of them BDL (one a historical IT/licensing-support award).

⚠ It remains a thin signal, not a feed: central-bank IT procurement surfacing publicly is rare, and
our actual buyers — private banks, family offices, asset and fund managers — publish nothing in any
of the four markets. But "we could not reach it" was simply untrue and would have stopped someone
looking again.
