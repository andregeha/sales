#!/usr/bin/env python
"""CMA (Saudi Arabia) — licensed Financial Market Institutions.

Saudi Arabia is our highest-priority market: a small, enumerable population that grew from ~188 to
~215 licensed institutions in a year, and **242 as at 2026-09-22**. Every new licence is a firm that
needs systems and has no incumbent.

Source: the CMA's public register page, *Financial Market Institutions* (what the CMA used to call
"Authorised Persons"), at ``/en/Market/AuthorisedPersons/Pages/default.aspx``. The entries are
server-rendered into the HTML, so no JavaScript is needed to read them.

⚠ **This is a PARTIAL source, deliberately.** The page ships the **36 most-recently-updated
entries** of 242 (it paginates the rest in with client-side JavaScript, "Total 41 Pages"). That is
enough for this connector's actual purpose, because **the list is ordered by last-update date,
newest first — so a newly licensed firm always appears at the top.** What it cannot do is notice a
firm *leaving* the register, so disappearance reporting is disabled for this source rather than
producing 200 false "gone" lines every morning.

**Why not the Open Data API.** ``opendataapi.cma.gov.sa`` publishes a swagger with a
``/api/Licenses/GetAllOrganizations`` endpoint that would give the full 242 in one call. Its
swagger file is fetchable, but **every ``/api/...`` call times out at the TCP layer after ~21s**
from Europe, repeated with backoff — the signature of a geo-restriction on the backend, not a rate
limit. If this connector is ever run from the Riyadh office or another Saudi network, **try the API
first**: it would make this a complete source and let disappearance detection be turned back on.

Also checked and rejected: the CMA's downloadable open-data files are aggregate workforce and
capital-adequacy statistics, not a register of named firms.

⚠ Two traps recorded so nobody rediscovers them: the CMA's domain moved from **cma.org.sa to
cma.gov.sa**, and its SharePoint returns a **styled error page with HTTP 200** for a wrong URL — so
this connector checks the content, never the status code.
"""

from __future__ import annotations

import html
import re
from typing import Optional

try:
    from .base import Connector, ConnectorError, Entry, http_get
except ImportError:  # run directly, not as a package
    from base import Connector, ConnectorError, Entry, http_get

REGISTER_URL = "https://cma.gov.sa/en/Market/AuthorisedPersons/Pages/default.aspx"

# One card per firm. `data-id` is the CMA's own stable identifier for the entry.
_CARD_RE = re.compile(
    r'<div class="col-12 page page-\d+" data-id="(?P<id>\d+)" data-page="\d+">'
    r'(?P<body>.*?)(?=<div class="col-12 page page-\d+" data-id=|\Z)',
    re.S,
)
_NAME_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
_DATE_RE = re.compile(r'<span class="date">(\d{2})/(\d{2})/(\d{4})</span>')
_NOTES_RE = re.compile(r"<p[^>]*>\s*Notes\s*:\s*(.*?)</p>", re.S)
_ACT_RE = re.compile(r'fw-medium[^>]*">\s*([^<]+?)\s*</li>')
_COUNT_RE = re.compile(r"Count=\s*(\d+)")

# The CMA's activity abbreviations, taken from the legend printed on the register page itself:
# "Arranging (Arr)  Advising (Adv)  Custody (C)  Dealing (D)
#  Managing Investments and Operating Funds (MIOF)  Managing Investments (MI)".
# ⚠ The cards render these inconsistently — some show the code, some the full name — so both forms
# are accepted and normalised to the code.
ACTIVITY_NAMES = {
    "MI": "Managing Investments",
    "MIOF": "Managing Investments and Operating Funds",
    "Arr": "Arranging",
    "Adv": "Advising",
    "D": "Dealing",
    "C": "Custody",
}
_BY_FULL_NAME = {v.lower(): k for k, v in ACTIVITY_NAMES.items()}

# The activities that make a firm one of ours.
_MANAGING = {"MI", "MIOF"}      # our segment: asset & fund managers
_CUSTODY = {"C"}                # adjacent
_DEALING = {"D"}                # adjacent


def _normalise_activity(raw: str) -> str:
    """Return the CMA's code for an activity, whether the card printed the code or the full name."""
    s = raw.strip()
    return _BY_FULL_NAME.get(s.lower(), s)


class CMASaudiConnector(Connector):
    register = "cma-saudi"
    regulator = "CMA (Saudi Arabia)"
    country = "Saudi Arabia"
    source_name = "Saudi CMA register of licensed Financial Market Institutions"
    source_url = REGISTER_URL

    #: See the module docstring — we read the newest slice, not the whole register.
    partial_source = True

    def fetch(self) -> list[Entry]:
        raw = http_get(REGISTER_URL, timeout=90)
        text = raw.decode("utf-8", errors="replace")

        # ⚠ HTTP 200 is not success on this site. Check the content.
        if "<title>" in text[:2000] and re.search(r"<title>\s*Error\s*</title>", text[:2000], re.I):
            raise ConnectorError(
                f"{REGISTER_URL} returned a SharePoint error page with HTTP 200. The register URL "
                f"has probably moved again (it already moved from cma.org.sa to cma.gov.sa)."
            )
        if "requested URL was rejected" in text:
            raise ConnectorError(
                f"{REGISTER_URL} was rejected by the CMA's WAF. We do not attempt to work around "
                f"bot protection — this needs a human with a browser."
            )

        cards = list(_CARD_RE.finditer(text))
        if not cards:
            raise ConnectorError(
                f"{REGISTER_URL} loaded but no register entries could be parsed from it. The page "
                f"markup has changed. Refusing to report zero — that would read as a quiet day when "
                f"in fact we cannot read the register at all."
            )

        declared = _COUNT_RE.search(text)
        self._declared_total = int(declared.group(1)) if declared else None

        entries = [self._to_entry(m) for m in cards]
        return [e for e in entries if e.name]

    # -- mapping ----------------------------------------------------------

    def _to_entry(self, m: re.Match) -> Entry:
        body = m.group("body")
        name = self._clean(_NAME_RE.search(body))
        notes = self._clean(_NOTES_RE.search(body))
        acts = [_normalise_activity(a) for a in _ACT_RE.findall(body) if a.strip()]

        licence_type = "; ".join(ACTIVITY_NAMES.get(a, a) for a in acts) or None
        if notes:
            licence_type = f"{licence_type} (register note: {notes})" if licence_type else \
                f"register note: {notes}"

        return Entry(
            key=m.group("id"),
            name=name,
            country="Saudi Arabia",
            segment=self._segment(acts),
            city=None,                       # the register card does not publish an address
            website=None,                    # nor a website
            phone=None,                      # nor a phone number
            licence_date=self._last_update(body),
            licence_type=licence_type,
            legal_name=None,
            # The register states the authorised activities but not the asset classes or whose money
            # is managed, so neither flag is set. Awarding those points would be inventing evidence.
            multi_asset=None,
            third_party=None,
            evidence={},
            raw={"activities": acts, "notes": notes, "cma_entry_id": m.group("id")},
        )

    @staticmethod
    def _clean(match: Optional[re.Match]) -> Optional[str]:
        if not match:
            return None
        s = html.unescape(re.sub(r"<[^>]+>", "", match.group(1)))
        s = " ".join(s.split())
        return s or None

    @staticmethod
    def _last_update(body: str) -> Optional[str]:
        """The card's 'Last update' date, dd/mm/yyyy, as ISO.

        ⚠ This is the date the CMA last **updated the entry**, which for a new firm is effectively
        its licence date but for an existing firm may be any amendment. It is stored in
        ``licence_date`` because that is what drives the trigger score, and the scoring reasoning
        says plainly what the date means.
        """
        m = _DATE_RE.search(body)
        if not m:
            return None
        dd, mm, yyyy = m.groups()
        return f"{yyyy}-{mm}-{dd}"

    @staticmethod
    def _segment(acts: list[str]) -> Optional[str]:
        s = set(acts)
        if s & _MANAGING:
            return "asset_manager"
        if s & _CUSTODY:
            return "custodian"
        if s & _DEALING:
            return "broker"
        return None

    # -- scoring ----------------------------------------------------------

    def _trigger_points(self, entry: Entry) -> tuple[int, str]:
        """Same age bands as the base class, but honest about what the date actually means."""
        pts, why = super()._trigger_points(entry)
        if pts:
            why = why.replace("new licence granted", "register entry last updated")
            why += (
                " — ⚠ this is the CMA's 'last update' date for the entry, which is the licence date "
                "for a new firm but may be an amendment for an existing one. Confirm before using "
                "it as a reason to write"
            )
        return pts, why


CONNECTOR = CMASaudiConnector
