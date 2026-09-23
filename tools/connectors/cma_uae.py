#!/usr/bin/env python
"""Capital Market Authority (UAE) — open-data register of licensed companies, onshore.

This closes the UAE's biggest gap. Every UAE record we held before this connector — 682 of them —
came from the two financial **free zones** (DIFC via `dfsa_difc.py`, ADGM via `fsra_adgm.py`). Zero
came from **onshore** UAE, which every mainland brokerage, fund manager and clearing house is
licensed under. This connector reads that register.

⚠ **The regulator was renamed.** The Securities and Commodities Authority (SCA) became the
**Capital Market Authority of the UAE** effective 1 Jan 2026 (Federal Decree-Laws 32/33 of 2025).
`sca.gov.ae` now 301-redirects to `www.uaecma.gov.ae`.

⚠ **Naming collision, and it matters.** We already hold a register called `cma-saudi` (the Saudi
Capital Market Authority, `cma.org.sa`/`cma.gov.sa`) — a different regulator in a different country
with an unrelated register. This one is `cma-uae`. Everywhere a human reads this connector's output
— `regulator`, `source_name`, docstrings, log lines — the name is spelled out in full, **"Capital
Market Authority (UAE)"**, never a bare "CMA". A bare "CMA" in a report, a CRM record or anything
Andre reads is exactly the two-information-sets confusion `CLAUDE.md` warns about, and here the two
information sets are two different sovereign regulators.

**How it is read.** A single JSON API, no browser, no HTML scraping:
``POST https://www.uaecma.gov.ae/api/PublicApi/GeIntegrationResult``. Verified live on 2026-09-23.

- Parameters nest inside ``urlParameters`` — a flat payload returns ``code:400 "Invalid Integration
  Parameters"``. Confirmed:
  ``{"integrationId":2045,"urlParameters":{"pageIndex":1,"pageSize":1000000,"type":"<id>","keyword":
  "","languageId":1,"languageCode":"en"}}`` returns ``{"code":200,"data":{"items":[...]}}``, where
  each item is exactly ``code``, ``name``, ``status``, ``website``, ``year`` — nothing else. A plain
  honest ``User-Agent`` alone gets HTTP 403; this is an origin/CSRF check, not bot protection, so
  ``base.USER_AGENT`` is sent unchanged alongside the page's own ``Referer``/``Origin`` — never a
  spoofed browser UA.
- ``integrationId:2047`` (payload just ``{"languageCode":"en"}``) returns every activity category as
  ``{companyId, title}`` — 59 of them. A category's ``companyId`` is passed as ``type`` in the 2045
  call to filter to it.
- ``integrationId:2055`` — **the per-company detail call. Not documented anywhere; found by reading
  the register page's own inline JS** (a minified jQuery handler wired to a "view company" link,
  ``/en/open-data/licensed-companies?q={{code}}``) and verified live against several real companies.
  Payload: ``{"companyId": "<code>", "languageId": 1, "languageCode": "en"}``. Response:
  ``data.company.CompanyDetails`` with ``Email``, ``Telephone``, ``City``, ``CompanyAddress``,
  ``EstablishedDate`` (``dd-Mon-yyyy``, same format DFSA uses), ``Website`` and more; also
  ``data.company.LicenseActivities`` (the firm's *complete* activity list, useful only as a sanity
  check — see below). This is a genuinely good source: an email address for firms that state one,
  published by the regulator on its own register, not guessed. Two-stage by design, exactly like
  DFSA and FSRA: fetched only for firms about to become CRM candidates, never for all 322 firms on a
  routine run.

**Segment mapping — measured live on 2026-09-23, each count reproduced exactly by querying `type`
alone:**

| `type` | Category | Firms |
|---|---:|---:|
| 6  | Investment Fund Management                    | 39 |
| 7  | Portfolios management                         | 44 |
| 45 | Profit Sharing Asset Management               |  1 |
| 21 | Securities Central Clearing                   |  2 |
| 1  | Trading and clearing broker                   | 26 |
| 4  | Trading broker                                |  3 |
| 2  | Trading broker in the international markets   | 36 |

A firm can hold several of these at once (50 of the 93 unique firms across the seven do). Dedupe is
by the register's own ``code`` (e.g. ``CP-0001315``); every held category is kept, joined, in
``licence_type``. Where a firm holds more than one, the **segment follows the first match in the
table above** (fund management outranks general portfolio management, which outranks brokerage) —
the same "first service wins" convention `dfsa_difc.py` uses, made explicit here because the task
requires every category to still be recorded, not just the winning one.

⚠ **Deliberately NOT mapped, on instruction** — these are not our buyers and querying them would
bury real leads in volume, the same trade-off `dfsa_difc.py` documents for the services it refuses:
Listing advisor, Promotion, Introduction, Telemarketing of Securities and Commodities Trading
Services; every exchange-specific approval (Margin Trading, Short Selling, Market Maker, Omnibus
Accounts, Remote access, Online Trading/e-Trading, Liquidity Provision, Direct Market Access, ETF
Authorized Participant, Derivatives Trading Member, Covered Short Selling, Registered Owner
Activity, Price stabilization, Allocation Account); and every virtual-asset category (Dealing in
Virtual Assets, Providing Custody for Virtual Assets, MTF dedicated to Virtual Assets).

Two further categories exist on the register but were **not** part of the directive that produced
this connector, so they are left unmapped rather than guessed at: **"Custody"** (`type=9`, 6 firms —
distinct from `type=21` "Securities Central Clearing", which IS mapped, to `custodian`) and
**"Trading broker of OTC derivatives and currencies in the spot market"** (`type=3`, 27 firms). Both
are recorded in `memory/open-questions.md` for a human to decide, not silently added.

**Withdrawn firms.** Every entry returned by this open-data endpoint was observed to carry
``status: "Active"`` — the dataset appears to be pre-filtered to current licensees by the regulator
itself. The connector still checks ``status`` for a withdrawn/cancelled/suspended marker rather than
assuming that will always hold, exactly as `dfsa_difc.py` and `fsra_adgm.py` do for their own
registers.
"""

from __future__ import annotations

import json
import re
import time
from typing import Optional
from urllib.request import Request, urlopen

try:
    from .base import Connector, ConnectorError, Entry, USER_AGENT
except ImportError:  # run directly, not as a package
    from base import Connector, ConnectorError, Entry, USER_AGENT

BASE = "https://www.uaecma.gov.ae"
REGISTER_PAGE = f"{BASE}/en/open-data/licensed-companies"
API_URL = f"{BASE}/api/PublicApi/GeIntegrationResult"

REGULATOR_NAME = "Capital Market Authority (UAE)"  # never abbreviate this where a human reads it

#: Activity category (`type` id on integrationId 2045) -> (register's own title, our segment).
#: Order matters: it is the priority a firm's segment is resolved in when it holds more than one.
#: See the module docstring for the measured count of each and why the rest are excluded.
CATEGORIES: dict[str, tuple[str, str]] = {
    "6": ("Investment Fund Management", "fund_manager"),
    "7": ("Portfolios management", "asset_manager"),
    "45": ("Profit Sharing Asset Management", "asset_manager"),
    "21": ("Securities Central Clearing", "custodian"),
    "1": ("Trading and clearing broker", "broker"),
    "4": ("Trading broker", "broker"),
    "2": ("Trading broker in the international markets", "broker"),
}

#: Seconds between requests. Public data, read once a day — not something to hammer.
REQUEST_DELAY = 0.4

_MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

_WITHDRAWN_RE = re.compile(r"withdraw|cancel|suspend|revoke", re.I)


class CMAUAEConnector(Connector):
    register = "cma-uae"
    regulator = REGULATOR_NAME
    country = "UAE"
    source_name = f"{REGULATOR_NAME} open-data register of licensed companies"
    source_url = REGISTER_PAGE

    def __init__(self) -> None:
        self._details: dict[str, dict] = {}

    # -- the API call, shared by the listing and the detail lookup --------

    def _call(self, integration_id: int, params: dict) -> dict:
        body = json.dumps({"integrationId": integration_id, "urlParameters": params}).encode()
        req = Request(API_URL, data=body, headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Referer": REGISTER_PAGE,
            "Origin": BASE,
            "X-Requested-With": "XMLHttpRequest",
        })
        try:
            with urlopen(req, timeout=90) as resp:
                parsed = json.loads(resp.read().decode("utf-8", errors="replace"))
        except Exception as e:  # noqa: BLE001
            raise ConnectorError(
                f"{REGULATOR_NAME} API call (integrationId={integration_id}, params={params}) "
                f"failed: {e}"
            ) from e
        finally:
            time.sleep(REQUEST_DELAY)

        if parsed.get("code") != 200:
            raise ConnectorError(
                f"{REGULATOR_NAME} API returned code {parsed.get('code')!r} for "
                f"integrationId={integration_id}, params={params}: {parsed}"
            )
        return parsed.get("data") or {}

    # -- fetching -----------------------------------------------------------

    def fetch(self) -> list[Entry]:
        cats_by_code: dict[str, list[str]] = {}
        seg_by_code: dict[str, str] = {}
        row_by_code: dict[str, dict] = {}

        for cat_id, (title, segment) in CATEGORIES.items():
            data = self._call(2045, {
                "pageIndex": 1, "pageSize": 1000000, "type": cat_id,
                "keyword": "", "languageId": 1, "languageCode": "en",
            })
            items = data.get("items") or []
            if not items:
                raise ConnectorError(
                    f"{REGULATOR_NAME} returned zero firms for category {title!r} (type={cat_id}). "
                    f"That category held firms as of 2026-09-23 — this is a broken query, not a "
                    f"quiet day."
                )
            for row in items:
                code = (row.get("code") or "").strip()
                name = (row.get("name") or "").strip()
                if not code or not name:
                    continue
                status = (row.get("status") or "").strip()
                if status and _WITHDRAWN_RE.search(status):
                    # A firm that handed its licence back is not a lead.
                    continue
                cats_by_code.setdefault(code, [])
                if title not in cats_by_code[code]:
                    cats_by_code[code].append(title)
                seg_by_code.setdefault(code, segment)  # first category in table order wins
                row_by_code.setdefault(code, row)

        if not row_by_code:
            raise ConnectorError(
                f"{REGULATOR_NAME} returned no usable rows across every mapped category. Refusing "
                f"to report zero — this is a fetch or parse failure, not an empty register."
            )

        entries = []
        for code, row in row_by_code.items():
            segment = seg_by_code[code]
            licence_type = "; ".join(cats_by_code[code])
            third_party = segment in {"asset_manager", "fund_manager"}
            entries.append(Entry(
                key=code,
                name=(row.get("name") or "").strip(),
                country="UAE",
                segment=segment,
                city=None,                        # not in the listing; filled from detail (2055)
                website=self._clean_website(row.get("website")),
                phone=None,                        # ditto
                licence_date=None,                 # ditto — "year" alone is not a date, see below
                licence_type=licence_type,
                legal_name=None,
                multi_asset=None,                  # the register does not state asset classes
                third_party=third_party or None,
                evidence=({"third_party": f"authorised by {REGULATOR_NAME} for {licence_type}"}
                          if third_party else {}),
                raw={
                    "listing_year": (row.get("year") or "").strip() or None,
                    "status": (row.get("status") or "").strip() or None,
                },
            ))
        return entries

    @staticmethod
    def _clean_website(v: Optional[str]) -> Optional[str]:
        v = (v or "").strip()
        if not v:
            return None
        return v if v.lower().startswith(("http://", "https://")) else "https://" + v.lstrip("/")

    # -- detail enrichment, only for firms we are about to record ------------

    def _detail(self, code: str) -> dict:
        """`CompanyDetails` for one firm via integrationId 2055 — email, phone, city, address, the
        established date. Failure here must NOT look like "this firm publishes nothing": `{}` means
        "we could not find out", used the same way for every field it would have supplied.
        """
        if code in self._details:
            return self._details[code]
        try:
            data = self._call(2055, {"companyId": code, "languageId": 1, "languageCode": "en"})
        except ConnectorError:
            self._details[code] = {}
            return {}
        cd = ((data or {}).get("company") or {}).get("CompanyDetails") or {}
        self._details[code] = cd
        return cd

    def build_record(self, entry: Entry, snapshot_file: str) -> dict:
        d = self._detail(entry.key)
        if d.get("EstablishedDate"):
            entry.licence_date = self._iso(d["EstablishedDate"])
        if (d.get("Telephone") or "").strip():
            entry.phone = " ".join(d["Telephone"].split())
        if (d.get("City") or "").strip():
            entry.city = d["City"].strip()
        email = (d.get("Email") or "").strip() or None
        address = (d.get("CompanyAddress") or "").strip() or None

        rec = super().build_record(entry, snapshot_file)
        if address:
            rec["activities"][0]["summary"] += (
                f" Registered address (per the {REGULATOR_NAME}): {address}"
            )
        if email or entry.phone:
            rec["contacts"].append({
                "name": f"{entry.name} — contact published on the {REGULATOR_NAME} register",
                "title": "General enquiries",
                "role": "unknown",
                "email": email,
                "phone": entry.phone,
                "linkedin": None,
                "language": "en",
                "notes": (
                    f"Email and/or telephone exactly as the {REGULATOR_NAME} publishes them on its "
                    f"own open-data register — not guessed, not pattern-inferred. Confirm who it "
                    f"belongs to before writing; it may be a named individual rather than a general "
                    f"inbox."
                ),
                "source": f"{REGULATOR_NAME} open-data register, company {entry.key}",
            })
        return rec

    @staticmethod
    def _iso(ddmmmyyyy: str) -> Optional[str]:
        m = re.match(r"(\d{1,2})-([A-Za-z]{3})-(\d{4})", ddmmmyyyy.strip())
        if not m:
            return None
        dd, mon, yyyy = m.groups()
        month = _MONTHS.get(mon.title())
        return f"{yyyy}-{month:02d}-{int(dd):02d}" if month else None

    def tags_for(self, entry: Entry) -> list[str]:
        return super().tags_for(entry) + ["uae", "onshore", "cma-uae"]


CONNECTOR = CMAUAEConnector
