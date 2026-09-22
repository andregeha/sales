#!/usr/bin/env python
"""DFSA (Dubai, DIFC) — public register of authorised firms.

The DIFC is the densest concentration of our buyers in the Gulf, and the DFSA's public register is
searchable by **financial service**, which maps almost directly onto our segments:

| DFSA financial service | Firms (2026-09-22) | Our segment |
|---|---|---|
| Managing Assets | 396 | `asset_manager` |
| Single Family Office | 41 | `family_office` |
| Accepting Deposits | 38 | `bank` |
| Providing Fund Administration | 33 | `fund_manager` |

⚠ **"Single Family Office" is the important one.** Family offices are invisible by design almost
everywhere — DIFC exempts single-family offices above a $50m net-asset threshold from much of the
regime, and no Gulf family-office association publishes a directory. But the DFSA register lists
them as a service category, so this is the one enumerable population of Gulf family offices we have
found anywhere.

**How it is read.** The register front-end calls a small AJAX API, and that is what this connector
uses — no HTML scraping of a rendered page, no browser required:
- ``/public-register/firms/getTotal?...&isAjax=true`` → the count for a filter
- ``/public-register/firms?page=N&...&isAjax=true&csrf_token=…`` → a page of 10 rows
A CSRF token is read from the register page first, exactly as a browser would.

**Two-stage by design, to be a good citizen.** The listing gives name, reference number and firm
type — enough to diff against yesterday, at roughly 50 requests. The **detail page** (address,
telephone, date of registration) is fetched **only for firms we are about to create**, not for all
500 every morning. Requests are spaced.

⚠ The listing includes **withdrawn and revoked** entries — a firm type containing "Withdrawn" or
"Revoked" is a *former* licensee and is excluded. A withdrawn firm is not a lead; it is a firm that
handed its licence back.
"""

from __future__ import annotations

import html
import re
import time
from typing import Iterable, Optional
from urllib.request import Request, urlopen

try:
    from .base import Connector, ConnectorError, Entry, http_get, USER_AGENT
except ImportError:  # run directly, not as a package
    from base import Connector, ConnectorError, Entry, http_get, USER_AGENT

BASE = "https://www.dfsa.ae"
REGISTER_PAGE = f"{BASE}/public-register/firms"
TOTAL_URL = f"{BASE}/public-register/firms/getTotal"

#: DFSA financial service → our segment. Only services that map to a segment we sell to.
SERVICES = {
    "Managing Assets": "asset_manager",
    "Single Family Office": "family_office",
    "Providing Fund Administration": "fund_manager",
    "Accepting Deposits": "bank",
}

PAGE_SIZE = 10
#: Seconds between requests. These are public pages read once a day, not something to hammer.
REQUEST_DELAY = 0.4

_ROW_RE = re.compile(
    r'href="(?P<url>[^"]+)" class="table-row">(?P<body>.*?)</a>', re.S
)
_FIELD_RE = {
    "name": re.compile(r"<span>Name:</span>\s*(.*?)\s*</p>", re.S),
    "ref": re.compile(r"<span>Reference number:</span>\s*(.*?)\s*</p>", re.S),
    "type": re.compile(r"<span>Firm Type:</span>\s*(.*?)\s*</p>", re.S),
}
_CSRF_RE = re.compile(r'name="csrf_token"[^>]*value="([^"]+)"')
_TOTAL_RE = re.compile(r'"total"\s*:\s*"?(\d+)"?')

# Detail-page fields. The page is a flat label/value layout.
_DETAIL_RE = {
    "legal_status": re.compile(r"Legal Status:\s*\|?\s*([^|]+)"),
    "address": re.compile(r"Address\s*\|\s*([^|]+)"),
    "phone": re.compile(r"Telephone Number\s*\|\s*([^|]+)"),
    "registered": re.compile(r"Date of Registration\s*\|\s*([0-9]{2}-[A-Za-z]{3}-[0-9]{4})"),
    "withdrawn": re.compile(r"Date of Withdrawal\s*\|\s*([0-9]{2}-[A-Za-z]{3}-[0-9]{4})"),
}

_MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def _strip(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", fragment)).split())


class DFSADIFCConnector(Connector):
    register = "dfsa-difc"
    regulator = "DFSA (DIFC)"
    country = "UAE"
    source_name = "DFSA public register of authorised firms (DIFC)"
    source_url = REGISTER_PAGE

    def __init__(self) -> None:
        self._csrf: Optional[str] = None
        self._cookie: Optional[str] = None
        self._details: dict[str, dict] = {}

    # -- session ----------------------------------------------------------

    def _open_session(self) -> None:
        """Read the register page for a CSRF token and a session cookie, as a browser would."""
        req = Request(REGISTER_PAGE, headers={"User-Agent": USER_AGENT})
        try:
            with urlopen(req, timeout=60) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                cookies = resp.headers.get_all("Set-Cookie") or []
        except Exception as e:  # noqa: BLE001
            raise ConnectorError(f"DFSA register page unreachable: {e}") from e

        m = _CSRF_RE.search(body)
        if not m:
            raise ConnectorError(
                "No csrf_token on the DFSA register page. The register front-end has changed — "
                "the connector needs updating before its results can be trusted."
            )
        self._csrf = m.group(1)
        self._cookie = "; ".join(c.split(";", 1)[0] for c in cookies)

    def _get(self, url: str, timeout: int = 60) -> str:
        headers = {"User-Agent": USER_AGENT, "X-Requested-With": "XMLHttpRequest"}
        if self._cookie:
            headers["Cookie"] = self._cookie
        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            raise ConnectorError(f"DFSA request failed ({url}): {e}") from e
        finally:
            time.sleep(REQUEST_DELAY)

    # -- fetching ---------------------------------------------------------

    @staticmethod
    def _service_param(service: str) -> str:
        """The front-end double-encodes the service name; replicate it rather than 'fixing' it."""
        return service.replace(" ", "%2520").replace("&", "%26")

    def _query(self, service: str, page: int) -> str:
        return (
            f"{REGISTER_PAGE}?page={page}&type=&financial_service={self._service_param(service)}"
            f"&keywords=&legal_status=&endorsement=&isAjax=true&csrf_token={self._csrf}"
        )

    def _total(self, service: str) -> int:
        url = (
            f"{TOTAL_URL}?page=0&type=&financial_service={self._service_param(service)}"
            f"&keywords=&legal_status=&endorsement=&isAjax=true"
        )
        m = _TOTAL_RE.search(self._get(url, timeout=45))
        if not m:
            raise ConnectorError(f"DFSA getTotal returned no count for {service!r}.")
        return int(m.group(1))

    def fetch(self) -> list[Entry]:
        self._open_session()
        by_ref: dict[str, Entry] = {}

        for service, segment in SERVICES.items():
            expected = self._total(service)
            if expected == 0:
                raise ConnectorError(
                    f"DFSA reports zero firms for {service!r}. That is not credible for a live "
                    f"register — treating it as a broken query rather than a quiet day."
                )
            seen_here: set[str] = set()
            pages = (expected // PAGE_SIZE) + 2   # +2 for the API's 0/1 page overlap
            for page in range(pages):
                rows = list(_ROW_RE.finditer(self._get(self._query(service, page))))
                if not rows:
                    break
                new_on_page = 0
                for m in rows:
                    e = self._row_to_entry(m, service, segment)
                    if e is None:
                        continue
                    if e.key in seen_here:
                        continue
                    seen_here.add(e.key)
                    new_on_page += 1
                    # A firm can hold several services; keep the first mapping we saw.
                    by_ref.setdefault(e.key, e)
                if new_on_page == 0 and page > 1:
                    break

        if not by_ref:
            raise ConnectorError(
                "DFSA register returned no usable rows across every service. Refusing to report "
                "zero — this is a parse or access failure, not an empty register."
            )
        return list(by_ref.values())

    def _row_to_entry(self, m: re.Match, service: str, segment: str) -> Optional[Entry]:
        body = m.group("body")
        fields = {k: (_strip(r.group(1)) if (r := rx.search(body)) else None)
                  for k, rx in _FIELD_RE.items()}
        name, ref, ftype = fields["name"], fields["ref"], fields["type"]
        if not name or not ref:
            return None
        # A withdrawn or revoked entry is a FORMER licensee, not a lead.
        if ftype and re.search(r"withdrawn|revoked", ftype, re.I):
            return None
        return Entry(
            key=ref,
            name=name,
            country="UAE",
            segment=segment,
            city="Dubai",                     # DIFC firms are Dubai by definition
            website=None,                     # the register does not publish one
            phone=None,                       # filled from the detail page, for new firms only
            licence_date=None,                # ditto
            licence_type=f"{service}" + (f" ({ftype})" if ftype else ""),
            legal_name=None,
            multi_asset=None,                 # the register does not state asset classes
            third_party=(True if segment in {"asset_manager", "fund_manager"} else None),
            evidence=({"third_party": f"DFSA-authorised for {service}"}
                      if segment in {"asset_manager", "fund_manager"} else {}),
            raw={"detail_url": m.group("url"), "firm_type": ftype, "service": service},
        )

    # -- detail enrichment, only for firms we are about to record ---------

    def _detail(self, entry: Entry) -> dict:
        url = entry.raw.get("detail_url")
        if not url or url in self._details:
            return self._details.get(url, {})
        try:
            body = self._get(url)
        except ConnectorError:
            self._details[url] = {}
            return {}
        flat = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", "", body)
        flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "|", flat))
        flat = re.sub(r"(\|\s*)+", "|", flat)
        out = {}
        for k, rx in _DETAIL_RE.items():
            mm = rx.search(flat)
            if mm:
                out[k] = mm.group(1).strip()
        self._details[url] = out
        return out

    def build_record(self, entry: Entry, snapshot_file: str) -> dict:
        d = self._detail(entry)
        if d.get("registered"):
            entry.licence_date = self._iso(d["registered"])
        if d.get("phone"):
            entry.phone = " ".join(d["phone"].split())
        if d.get("legal_status"):
            entry.legal_name = None  # legal STATUS is not a legal NAME; do not conflate them

        rec = super().build_record(entry, snapshot_file)
        if d.get("address"):
            rec["activities"][0]["summary"] += f" Registered address (per the DFSA): {d['address']}"
        if d.get("phone"):
            rec["contacts"].append({
                "name": f"{entry.name} — switchboard (register-published)",
                "title": "General enquiries",
                "role": "unknown",
                "email": None,
                "phone": entry.phone,
                "linkedin": None,
                "language": "en",
                "notes": (
                    "Telephone number as published by the DFSA on its own public register — not a "
                    "guessed number and not an individual's line. Use it to reach a named person, "
                    "not as the first touch itself."
                ),
                "source": f"DFSA public register, {entry.raw.get('detail_url')}",
            })
        return rec

    @staticmethod
    def _iso(ddmmmyyyy: str) -> Optional[str]:
        m = re.match(r"(\d{2})-([A-Za-z]{3})-(\d{4})", ddmmmyyyy)
        if not m:
            return None
        dd, mon, yyyy = m.groups()
        month = _MONTHS.get(mon.title())
        return f"{yyyy}-{month:02d}-{dd}" if month else None


CONNECTOR = DFSADIFCConnector
