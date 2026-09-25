#!/usr/bin/env python
"""SAMA (Saudi Central Bank) — register of licensed banks.

Closes **Saudi Arabia x bank**, which stood at zero: nothing we read before this connector covered
deposit-taking institutions in the Kingdom — the CMA register (`cma_saudi.py`, `cma_saudi_xlsx.py`)
is capital-markets activity, not banking licences.

**How it was found.** The human-facing page — `.../en-US/supervision/licenseentities/pages/
default.aspx` (Banks tab) — is an empty SharePoint/SPA shell; no bank name is server-rendered. It
loads `licensedentities.js`, which calls a generic list-loader against a plain, unauthenticated JSON
endpoint, found by reading that script rather than guessing:

    GET https://www.sama.gov.sa/_LAYOUTS/15/SAMA.Portal/PortalHandler.ashx
        ?op=LoadItems&listUrl=<listUrl>&viewName=Archive

``listUrl`` is read from each page's own `data-list` HTML attribute, not guessed:
- Banks:   `/ar-sa/Supervision/LicenseEntities/Lists/LicensedBanks`   -> **39** rows (measured
  2026-09-24: 11 Local Banks, 24 Foreign Bank Branches, 4 Digital Banks).
- Finance: `/ar-sa/Supervision/LicenseEntities/Lists/LicensedFinance` -> 91 rows (78 Finance
  Companies, 13 Finance Support Companies) — **not read by this connector**, see the decision below.

Verified live: a plain `base.USER_AGENT` alone gets HTTP 200 JSON — no Referer/Origin check (unlike
the UAE CMA API), no auth, no pagination parameter; the whole list returns in one call.

⚠ **`sitemap.xml` is not real on this domain.** `https://www.sama.gov.sa/sitemap.xml` returns HTTP
200 but is in fact the homepage served as a catch-all fallback for any unrecognised path — the same
"200 for a wrong URL" trap `cma_saudi.py` already documents for a different SharePoint site, seen
here too on `/robots.txt` and every locale variant of `/sitemap.xml` tried. Not relevant to this
connector (it never touches that path), recorded here so nobody rediscovers it by tripping over it.

**Fields, exactly as the API returns them** (one live row, translated field by field):
``ID`` (SharePoint list item id — stable, used as the register key), ``Title`` (Arabic name),
``TitleEn`` (English name), ``UrlLinkAr`` / ``UrlLinkEn`` (website, Arabic/English page), it
``ActivityType`` / ``ActivityType_x003a_TitleEn`` (Arabic/English activity — "Banking Business" for
every row, so not useful for segmentation on its own), ``Categories`` / ``Categories_x003a_TitleEn``
(Arabic/English category — "Local Banks" / "Foreign Bank Branches" / "Digital Banks", the field this
connector actually uses to describe a licence), ``LicensingNumber``, ``UnifiedNumber`` (the CR-linked
identifier), and ``Created``.

⚠ **`Created` is a CMS record-creation date, NOT the licence date, and is never mapped to
`licence_date`.** Measured values (`24/02/2022`, `26/10/2025`, ...) are day-first (`DD/MM/YYYY`) —
day `24` proves it, since no month runs past 12 — but the format doesn't matter because the field is
not trustworthy as a licence date in the first place: every SAMA-licensed bank's record could have
been touched by an unrelated CMS edit at any time, and a change to *when the page was last saved* is
not a business event. `licence_date` is left `None` rather than record something false; the trigger
score therefore never fires from this source, which is honest — we cannot say from this register
alone that any of these 39 banks is newly licensed.

**Decision: banks only, never the 91 finance/finance-support companies.** `knowledge/market/
landscape.md` already classes SAMA-licensed finance companies as adjacent, not core: they write
consumer and SME lending (the `SubCategories` field on that list literally reads things like
"Finance lease, Consumer finance, SME's Finance"), which is not portfolio management and not a
Gaia buyer profile. Ingesting all 91 would double the register's record count with firms outside
every segment we sell to, for no scoring benefit — `Entry.segment` would have nowhere honest to
point them, and the base pipeline drops an unsegmented candidate anyway (see `Connector.run`). So
this connector fetches only the banks list; the finance list is not called at all.

**Segment.** All 39 rows map to `bank` — SAMA's licensed-bank register has no sub-population that
isn't a bank in our sense (it is not split, the way UAE's onshore CMA register is, into brokers,
asset managers and banks under one roof). This closes `Saudi Arabia x bank` completely: SAMA
licenses every Saudi bank, so there is no larger population to still be missing.

**Website.** `UrlLinkEn` is a real value published by the regulator for every row checked, not
guessed — genuinely useful, since most Saudi records we hold have no website at all
(`memory/open-questions.md` #20). Kept as `website`; the Arabic-language URL is kept in `raw` only.

**Name fields.** `TitleEn` is used as `name`. `Title` (Arabic) is kept as `legal_name` — a Saudi
bank's Arabic name on its own regulator's licence *is* its registered legal name (English is the
marketing/trading translation), the same call this workbook's sibling connector
(`cma_saudi_xlsx.py`) makes for the same reason. If that assumption is ever shown wrong for a
specific firm, correcting one `legal_name` is a one-line fix; it is not treated as fact anywhere
scoring depends on it.
"""

from __future__ import annotations

import json
from typing import Optional

try:
    from .base import Connector, ConnectorError, Entry, http_get
except ImportError:  # run directly, not as a package
    from base import Connector, ConnectorError, Entry, http_get

BASE = "https://www.sama.gov.sa"
API_URL = f"{BASE}/_LAYOUTS/15/SAMA.Portal/PortalHandler.ashx"
BANKS_LIST_URL = "/ar-sa/Supervision/LicenseEntities/Lists/LicensedBanks"
HUMAN_PAGE = f"{BASE}/en-US/supervision/licenseentities/pages/default.aspx"

REGULATOR_NAME = "SAMA (Saudi Central Bank)"


class SAMASaudiConnector(Connector):
    register = "sama-saudi"
    regulator = REGULATOR_NAME
    country = "Saudi Arabia"
    source_name = f"{REGULATOR_NAME} register of licensed banks"
    source_url = HUMAN_PAGE

    # -- fetching -----------------------------------------------------------

    def fetch(self) -> list[Entry]:
        url = f"{API_URL}?op=LoadItems&listUrl={BANKS_LIST_URL}&viewName=Archive"
        raw = http_get(url, accept="application/json", timeout=60)
        try:
            rows = json.loads(raw.decode("utf-8", errors="replace"))
        except json.JSONDecodeError as e:
            raise ConnectorError(f"{url} did not return parseable JSON: {e}") from e
        if not isinstance(rows, list) or not rows:
            raise ConnectorError(
                f"{url} returned no bank entries. SAMA licenses 39 banks as of 2026-09-24 — a live "
                f"register is never empty, so this is a fetch or parse failure, not a quiet day."
            )

        entries = [e for e in (self._to_entry(row) for row in rows) if e is not None]
        if not entries:
            raise ConnectorError(
                f"{url} returned {len(rows)} row(s) but none carried a usable name — the JSON "
                f"schema has changed since this connector was written."
            )
        return entries

    def _to_entry(self, row: dict) -> Optional[Entry]:
        name_en = (row.get("TitleEn") or "").strip()
        if not name_en:
            return None
        item_id = row.get("ID")
        key = str(item_id) if item_id is not None else name_en
        name_ar = (row.get("Title") or "").strip() or None
        category_en = (row.get("Categories_x003a_TitleEn") or "").strip() or None
        activity_en = (row.get("ActivityType_x003a_TitleEn") or "").strip() or None

        return Entry(
            key=key,
            name=name_en,
            country="Saudi Arabia",
            segment="bank",
            city=None,                    # not published by this register
            website=self._clean_website(row.get("UrlLinkEn")),
            phone=None,                   # not published by this register
            # ⚠ See the module docstring: `Created` is a CMS date, never the licence date.
            licence_date=None,
            licence_type=category_en or activity_en,
            legal_name=name_ar,
            # A deposit-taking bank is not "third-party portfolio management" in the sense the rest
            # of the CRM uses that flag, and the register does not state asset classes either.
            multi_asset=None,
            third_party=None,
            evidence={},
            raw={
                "activity_type_en": activity_en,
                "licensing_number": (row.get("LicensingNumber") or "").strip() or None,
                "unified_number": (row.get("UnifiedNumber") or "").strip() or None,
                "website_ar": self._clean_website(row.get("UrlLinkAr")),
                # Kept verbatim, DD/MM/YYYY, and clearly labelled as a CMS date so nobody downstream
                # mistakes it for something it is not.
                "created_cms_date_ddmmyyyy": (row.get("Created") or "").strip() or None,
            },
        )

    @staticmethod
    def _clean_website(v: Optional[str]) -> Optional[str]:
        v = (v or "").strip()
        if not v:
            return None
        return v if v.lower().startswith(("http://", "https://")) else "https://" + v.lstrip("/")

    def tags_for(self, entry: Entry) -> list[str]:
        return super().tags_for(entry) + ["saudi-arabia", "sama"]


CONNECTOR = SAMASaudiConnector
