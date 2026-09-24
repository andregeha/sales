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
