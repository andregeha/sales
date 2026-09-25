# Open questions

> Anything unknown, unverified, or needing Andre's approval. Nothing gets guessed.
> Status: 🔴 blocking · 🟠 needed soon · ⚪ nice to have. Newest first.
>
> **Stage model**: defined in `pipeline/pipeline.md` (2026-09-22) — change it if it does not match
> how you think about deals.

## ✅ Answered by Andre 2026-09-22
1. **Scope** → **new business only**. Existing clients are context/proof, not pipeline.
2. **Deliverables** → the full engine: find clients, find every RFP, automated lead pipeline,
   inbound + outbound outreach, daily and continuous, log everything, own CRM. Plus pipeline & forecast.
3. **Autonomy** → agents draft freely; **Andre approves and sends**. Give him fast, automated ways to send.
4. **System of record** → **this repo**. No external CRM.
5. **Markets** → **UAE, KSA, Lebanon, France**.
6. **Segments** → **family offices & MFOs, private/investment banks, asset & fund managers**.
7. **Media** → email, LinkedIn, and anything else sensible.
8. **Cadence** → **daily scheduled run**.

## ✅ Resolved 2026-09-22 (laptop)
- **Q0 — the network block.** Resolved by moving to the laptop. Every regulator register and tender
  portal we need is reachable. The register connectors are built and running as a result.

## 🔝 The four to answer first (2026-09-22)
These are ordered by what they unblock, not by how easy they are.

| # | Question | Why it matters | Status |
|---|---|---|---|
| 1 | **Which existing client names may we reference, and to whom?** Finance House, GIMD/Dassault, Bank Audi, BLOM, AGPM — which may be named, in which markets, and under what conditions? | Worth more for outreach credibility than anything else we could write. Every draft currently says "asset managers and banks across France and the Gulf" because naming anyone needs your approval. | 🟠 |
| 2 | **Which Lebanese banks are on the survivor track under Law 23/2025?** | **All 17 Lebanese bank records are frozen at `nurture`** because no public source resolves this, and a bank in resolution buys nothing. This is the single biggest block of stalled pipeline we have. | 🟠 |
| 3 | **Would you take a LinkedIn Sales Navigator seat?** | We now hold **many named decision-makers with a verified LinkedIn profile and no email**. A seat turns names into reachable people. Contact routes — not lead volume — are the binding constraint on the whole engine. | 🟠 |
| 4 | **Pricing guidance · any off-limits firms · do we control the OFS website?** | Without pricing every commercial question bounces to you; without an off-limits list we may approach someone we shouldn't; without the website there is **no inbound surface at all**. | 🟠 |

## 🆕 New, from this session
| # | Question | Status |
|---|---|---|
| 16 | **Will you set up the free saved-search email alerts on BOAMP and PLACE** (and My TED)? They are free, they take minutes, and **a push alert beats any scraper we could write**. They need an account in your name, so I cannot do it. Links in `knowledge/market/rfp-sources.md`. | 🟠 |
| 17 | **Should the daily run be scheduled on this laptop, and at what time?** Nothing is scheduled right now. Weekday mornings was the plan. ⚠ A laptop only runs when it is on — a missed morning is a genuinely missed day. | 🟠 |
| 18 | **Can anyone run the Saudi CMA connector from the Riyadh office** (or any Saudi network)? Its Open Data API times out from Europe. From inside the Kingdom it would probably work, and would upgrade Saudi from a partial source (36 of 242 firms) to a complete one. | ⚪ |
| 19 | **Does anyone at OFS have an Etimad supplier account?** Etimad blocks automated access with its own bot protection, which we will not try to defeat. **Saudi tender coverage is therefore zero.** A human with an account could set up its notifications. | 🟠 |
| 20 | **Do we want records for adjacent segments** — custodians and brokers — or only our three core segments? The Saudi register surfaces them and they currently land as low-scoring records. | ⚪ |

## For Andre — still open
| # | Question | Status |
|---|---|---|
| 5 | **Pricing** — is there a price book, list price or discount policy I may hold here, even internal-only? Without it I cannot qualify on budget, and every commercial question bounces to you. | 🟠 |
| 5a | **Is there an email-sending or sequencing tool** you would connect (Outlook send, a sequencer), or does every message go out by hand from your mailbox? This changes how I build the approval queue. | 🟠 |
| 5b | **Do you have a LinkedIn Sales Navigator seat?** It would materially improve lead sourcing and contact discovery in all four markets. | 🟠 |
| 5c | **Any markets, firms or people that are off-limits** — conflicts, existing partner territories, someone we must not approach? | 🟠 |
| 5d | **Inbound — do we control the OFS website** enough to add pages, a lead form and analytics? Right now I have no inbound surface at all, so "inbound marketing" produces nothing. See `playbooks/inbound.md`. | 🟠 |
| 5e | **Will you publish on LinkedIn** under your own name at a regular cadence? It is the cheapest, highest-leverage inbound channel we have, and the material is already written in `knowledge/`. | 🟠 |
| 5f | **Budget for events or paid search**, or organic only? | ⚪ |
| 5g | **Who answers an inbound enquiry within the hour?** An inbound lead that waits a day is lost. | ⚪ |
| 6 | **Competitors** — who do we actually meet, where do we win and lose? (`knowledge/positioning/competitors.md` is an empty placeholder.) | 🟠 |
| 9 | **Arabic** — do we need Arabic client-facing material for the Gulf, or is English sufficient there? (Gaia and the portal support Arabic/RTL, so it is a real option.) | 🟠 |
| 10 | **Referenceable clients** — which names may we say out loud, to whom, and under what conditions? This is the single most useful thing I am missing for outreach credibility. | 🟠 |
| 11 | **Team** — is anyone else going to use this repo, or is it you plus the agents? | ⚪ |
| 12 | **Targets** — is there a revenue/quota number the pipeline should be measured against? | ⚪ |

## Product gaps to confirm with R&D
| # | Question | Status |
|---|---|---|
| 13 | Exact FIX venue/broker coverage we can claim in writing (beyond Bloomberg EMSX + direct broker integration). | 🟠 |
| 14 | Whether a **dedicated profitability/RoA view** exists beyond the profitability report, for a client asking specifically. | ⚪ |
| 15 | The **digital onboarding flow** screens in the portal — we have not seen them; get access before demoing onboarding end to end. | 🟠 |

## Sourcing gaps (opened 2026-09-23)
| # | Question | Status |
|---|---|---|
| 16 | **EBRD procurement** — the notice search is a stateful JSF/ADF portal with no query contract, the same shape as France's PLACE. Needs a human with a browser, or an official EBRD feed, before it can be read. It is `failing` on the Sources view until then, deliberately. | 🔴 |
| 17 | **UNGM sees titles only.** The listing carries no description, so our classifier judges a title alone — a genuinely relevant notice with an uninformative title will be missed. Reading each notice's detail page would fix it at ~60 extra requests per run; not yet judged worth the load. | 🟠 |
| 18 | **286 candidates are not in the CRM**, now scored so the queue sorts by likelihood. Nobody has reviewed them. The eight scoring 60+ are the ones worth Andre's eyes first. | 🟠 |
| 19 | **France's 19,464 GLEIF funds have not been swept** for fund→manager relationships — hours at a polite rate. Saudi, UAE and Lebanon are done (17 candidates, incl. SNB Capital and Jadwa). | ⚪ |

## Commercial data sourcing (opened 2026-09-23)
| # | Question | Status |
|---|---|---|
| 23 | **Should we buy a UAE-specific family-office data product** (e.g. allfamilyoffices.com's "171 UAE family offices / 501 contacts" download, or Praxis Rock's comparable UAE dataset) to close the UAE × family office cell, which has zero coverage and no register instrument by structural design? Neither vendor's price was found published — needs a direct pricing-page check, then Andre's approval before any purchase. See `plan/uae-sources-commercial.md`. | 🟠 |
| 24 | **None of the global data platforms (Preqin, PitchBook, S&P Capital IQ, With Intelligence, Bureau van Dijk, Refinitiv/LSEG Workspace, Wealth-X) were found to justify their five-figure annual cost for our UAE segments** — confirmed today, not estimated. This closes the question rather than opening it further, recorded here so it is not re-investigated without new information. | ⚪ |

## Contact reachability (opened 2026-09-23)
| # | Question | Status |
|---|---|---|
| 20 | **1,146 of 1,604 records publish no website we know of** (UAE 543 of 567, France 578 of 986), so the website sweep structurally cannot reach them. **Checked and ruled out as sources of a website:** the ADGM snapshot carries only 13, and DFSA, CMA, REGAFI and SIRENE carry none at all — SIRENE has no URL field of any kind. Finding one per firm would mean search, which is bot-protected and risks attributing the wrong firm's site. **No instrument exists for this today.** | 🔴 |
| 21 | **Only 38 records have a real named human**; 887 "contacts" are switchboards. The website sweep collects published *routes*, not people. Named decision-makers need a different instrument — LinkedIn Sales Navigator is the obvious one and is blocked on a seat. | 🔴 |
| 22 | **GDPR posture on published business addresses.** We collect role addresses (`contact@`) by preference, which are not personal data, and write a named individual's address only where a firm publishes no role address. Worth a decision from Andre on whether that line is where he wants it before any France outreach goes out. | 🟠 |
| 25 | **`crm/SCHEMA.md` has no segment for a service provider.** DIFC fund *administrators* (33 records) are currently `fund_manager`, which is factually wrong — administration is NAV/registrar/reporting, not management. They are still plausible Gaia buyers, so dropping them is wrong too. Needs either a new segment (`fund_administrator`) or a decision to leave them mis-labelled knowingly. Not re-segmented on a connector's say-so. | 🟠 |
| 26 | ✅ RESOLVED 2026-09-24: Custody (9) and OTC/spot broking (3) are now mapped — the audit showed their exclusion was an inconsistency, not a scope decision. Commodity brokerage (22/23/24) stays excluded on purpose. Original: | **`cma_uae.py` (Capital Market Authority (UAE), onshore) deliberately does not map two categories it found on the register**: "Custody" (`type=9`, 6 firms — distinct from "Securities Central Clearing", `type=21`, which IS mapped to `custodian`) and "Trading broker of OTC derivatives and currencies in the spot market" (`type=3`, 27 firms). Neither was part of the directive that produced the connector. Worth a decision on whether either belongs before a future run adds it. | ⚪ |
| 27 | ✅ **AUDITED 2026-09-24 — the fear was wrong.** Of 164 ADGM firms outside the CRM: **106 have all their authorisations WITHDRAWN** (correctly excluded), 20 list no regulated activity at all (reinsurance, payments, tech), 38 hold activities we do not map, and **zero were unreadable and zero should have matched but didn't**. The FSRA connector is sound — this is NOT the DIFC problem repeated. The only real gaps are ~10 fund administrators and 12 *Arranging Deals* firms, the latter being the same low-precision category we deliberately refuse in DIFC. Original concern below. ~~162 of 414 ADGM firms are not in the CRM and nobody has audited why.~~ The FSRA connector maps only **6** regulated activities and skips anything else — the same under-reading the DIFC register turned out to have, where we were asking 4 of ~50 questions. The connector does correctly distinguish "detail page unreachable" from "read it, no match", but which bucket the 162 fall into has **not** been measured. Measured symptom: Banco Santander was skipped as "activities (none stated)". ⚠ ADGM's activity list could not be enumerated cheaply — the register page is a JS app with no options in static HTML. | 🔴 |
| 28 | **UAE CMA onshore: we map 7 of 59 published activity categories.** Same question as #27 in a different register. 322 licensed firms exist; we hold 88. | 🟠 |

## UAE private-banking/wealth sourcing (opened 2026-09-24)
| # | Question | Status |
|---|---|---|
| 29 | **A wide open-web sweep for UAE private banks, bank wealth arms, MFOs and EAMs is done and written up in `plan/uae-web-wealth.md`.** It found roughly a dozen international private banks/EAMs with a real UAE booking presence (Julius Baer, Lombard Odier, EFG (Middle East) Limited, Edmond de Rothschild (Middle East) Ltd, Rothschild & Co Wealth Management Dubai, Coutts, LGT, BNP Paribas Wealth Management (DIFC) Limited, Nomura International plc's DIFC wealth arm, Almha Capital) that are **not yet in the CRM** — none were added, per the task's read-only instruction. Needs a decision on whether/how to add them. | 🟠 |
| 30 | **Rep-office trap, three fresh cases**: Pictet's Dubai presence is a Central Bank of UAE-regulated representative office (confirmed by fetching Pictet's own page), RBC's Dubai wealth lead carries the title "Chief Representative" (press), and CA Indosuez's Abu Dhabi office is explicitly a representative office on Indosuez's own site (its Dubai DIFC branch is real and separate). None of these three should be treated as a live prospect without further confirmation. | 🟠 |
| 31 | **CRM hygiene, found but not fixed (out of scope for a read-only research task)**: `first-abu-dhabi-bank-p-j-s-c.yaml` and `first-abu-dhabi-bank.yaml` look like duplicate records for the same bank. Separately, `j-p-morgan-middle-east-limited.yaml` is recorded as Abu Dhabi, but J.P. Morgan Private Bank's own site places its DIFC private-banking office in Dubai — unclear if these are the same legal entity or two distinct JPM UAE entities. | 🟠 |
| 32 | **Two name-collision risks to keep in mind for any future UAE outreach**: (1) EFG (Middle East) Limited (Swiss EFG International, new candidate) vs. EFG Hermes UAE Limited (Egyptian investment bank, already tracked) — unrelated firms sharing "EFG"; (2) Vault Wealth Limited (ADGM-regulated wealth manager, already tracked) vs. Vault22 (a DIFC-based personal budgeting app, not a wealth manager) — unrelated firms sharing "Vault". | ⚪ |

## Saudi register connectors (opened 2026-09-25)
| # | Question | Status |
|---|---|---|
| 33 | **`cma_saudi_xlsx.py` has no stable per-firm ID to join or diff on.** The workbook's own row-order `#` column is not confirmed stable across quarterly editions (would need two editions captured over time to check), so the connector keys each CRM record on the *normalised English name* instead. Accepted trade-off, not a defect: a firm that changes its registered English name between one quarterly edition and the next will look like one firm disappearing and a different one appearing, rather than a rename being detected. Worth revisiting once a second quarterly edition has actually been captured and the `#` column's behaviour can be measured directly. | ⚪ |
| 34 | **Two connectors close most, not all, of the Saudi gap.** `sama_saudi.py` (39 banks, closes Saudi × bank completely) and `cma_saudi_xlsx.py` (144 firms across AUM/fund-count/custody) were built per `plan/saudi-sources.md`. `--backfill --dry-run` previews 31 net-new banks and 132 net-new CMA-workbook firms (163 net-new total) — Andre still needs to run the real `--backfill` to actually populate the CRM, since neither source publishes a licence date and a plain run therefore creates zero records by design. | 🟠 |
| 35 | ✅ **WORKED AROUND 2026-09-25 — not by defeating the block, by changing instrument.** GLEIF's identity graph was scanned for active UAE entities with a bank-like legal name: 19 found that we did not hold, 18 created. UAE banks 40 → 57, including Emirates Islamic, Sharjah Islamic, RAKBANK, Wio, Ajman Bank, Bank of Sharjah and United Arab Bank. ⚠ GLEIF carries NO industry classification, so every segment here is inferred from the legal name and must be confirmed before the record is worked — it also swept in the Central Bank of the UAE itself, now flagged as the regulator. The original CBUAE block stands: ~~CBUAE is bot-protected and UAE onshore banks stay unenumerable.~~ 403 to an honest User-Agent on the API *and* on the plain homepage (probed 2026-09-25), so the earlier "fully open JSON, 267 institutions" finding does not hold for a client that identifies itself. We hold 40 UAE banks; CBUAE licenses ~60. ⚠ Directly limits Andre's "never miss a bank RFP": we cannot watch a bank we cannot name. Needs either an official CBUAE data feed, or someone opening the register in a browser and saving the list once. | 🔴 |
