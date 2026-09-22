#!/usr/bin/env python
"""CMA (Saudi Arabia) — licensed Financial Market Institutions.

Saudi Arabia is our highest-priority market: a small, fully enumerable population that grew from
~188 to ~215 licensed institutions in a year. Every new licence is a firm that needs systems and has
no incumbent.

Source: the CMA's own Open Data API, ``https://opendataapi.cma.gov.sa``, documented at
``/swagger/index.html``. Endpoint ``/api/Licenses/GetAllOrganizations?lang=en`` — the CMA's Arabic
summary for it is "استرجاع مؤسسات السوق المالية" (retrieve the financial market institutions).

⚠ **STATUS AS AT 2026-09-22: the API endpoint could not be reached from France/Europe.**
``GET /swagger/v1/swagger.json`` on that host succeeded (which is how the endpoints below are known
to be correct), but every call to ``/api/...`` times out at the TCP layer after ~21s — a SYN with no
response, repeated over several minutes with backoff. That is the signature of a firewall or
geo-restriction on the API backend, not of a rate limit or a bad request.

Consequences, stated plainly:
- **This connector has never run against live data.** The field mapping below is written against the
  endpoint's documented purpose, not against an observed payload.
- It is therefore written to **fail loudly and specifically**: if the payload arrives but does not
  contain a recognisable name field, it raises with the actual keys it received, so the first
  successful run tells us exactly what to correct instead of quietly writing junk into the CRM.
- **Do not report "no new Saudi firms today" on the strength of this connector until it has
  succeeded at least once.** Until then a failure here means *we did not look*, not *nothing
  happened*.

Routes worth trying to make it work: run it from the Riyadh office or any Saudi network; or ask the
CMA whether the Open Data API is intended to be reachable from outside the Kingdom. The
alternative published files (``/AboutCMA/ResearchAndReports/opendata/...``) were checked and are
**aggregate statistics** — workforce and capital-adequacy indicators — not a register of named
firms, so they cannot substitute.

We do not attempt to work around the CMA's bot protection or its network restrictions. These are
public registers being read once a day, with an honest user agent.
"""

from __future__ import annotations

import json
from typing import Any, Optional

try:
    from .base import Connector, ConnectorError, Entry, http_get
except ImportError:  # run directly, not as a package
    from base import Connector, ConnectorError, Entry, http_get

API_ROOT = "https://opendataapi.cma.gov.sa"
ORGANIZATIONS_URL = f"{API_ROOT}/api/Licenses/GetAllOrganizations?lang=en"
SWAGGER_URL = f"{API_ROOT}/swagger/index.html"

# Field-name candidates. The API's payload shape is not yet observed (see the module docstring), so
# each of these is a guess at a conventional spelling — and if none of them match, we raise rather
# than fall back to something arbitrary.
_NAME_KEYS = ("name", "organizationName", "entityName", "companyName", "nameEn", "englishName",
              "OrganizationName", "Name")
_LICENCE_KEYS = ("licenseNumber", "licenceNumber", "licenseNo", "license_number", "number",
                 "LicenseNumber", "id", "Id")
_DATE_KEYS = ("licenseDate", "licenceDate", "issueDate", "licenseIssueDate", "date",
              "LicenseDate", "IssueDate")
_WEBSITE_KEYS = ("website", "webSite", "url", "Website")
_PHONE_KEYS = ("phone", "telephone", "phoneNumber", "Phone")
_ACTIVITY_KEYS = ("activities", "licensedActivities", "activity", "services", "Activities")
_CITY_KEYS = ("city", "cityName", "City")


def _first(d: dict, keys: tuple[str, ...]) -> Optional[Any]:
    for k in keys:
        if k in d and d[k] not in (None, "", []):
            return d[k]
    # case-insensitive second pass
    lower = {str(k).lower(): v for k, v in d.items()}
    for k in keys:
        v = lower.get(k.lower())
        if v not in (None, "", []):
            return v
    return None


class CMASaudiConnector(Connector):
    register = "cma-saudi"
    regulator = "CMA (Saudi Arabia)"
    country = "Saudi Arabia"
    source_name = "Saudi CMA register of licensed Financial Market Institutions (Open Data API)"
    source_url = SWAGGER_URL

    # The Saudi population is small (~215), so ordinary churn is a smaller absolute number than for
    # a 666-firm register. Keep the proportional floor but tighten the churn allowance.
    normal_churn = 3

    def fetch(self) -> list[Entry]:
        raw = http_get(
            ORGANIZATIONS_URL,
            accept="application/json",
            timeout=90,
        )
        try:
            payload = json.loads(raw.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise ConnectorError(
                f"Saudi CMA Open Data API returned something that is not JSON ({e}). "
                f"First 200 bytes: {raw[:200]!r}"
            ) from e

        records = self._unwrap(payload)
        if not records:
            raise ConnectorError(
                f"Saudi CMA Open Data API returned no records. The licensed-institution register is "
                f"never empty, so this is a fetch or schema problem — not a quiet day."
            )

        sample = records[0]
        if not isinstance(sample, dict) or _first(sample, _NAME_KEYS) is None:
            raise ConnectorError(
                f"Saudi CMA payload parsed, but no recognisable firm-name field was found. "
                f"This connector has never seen live data from this endpoint (see the module "
                f"docstring), so the mapping needs correcting against what actually arrived. "
                f"Observed keys on the first record: "
                f"{sorted(sample.keys()) if isinstance(sample, dict) else type(sample).__name__}. "
                f"Refusing to create records from a mapping we cannot trust."
            )

        return [self._to_entry(r) for r in records if isinstance(r, dict)]

    @staticmethod
    def _unwrap(payload: Any) -> list:
        """The API may return a bare list or wrap it in a envelope. Accept either; invent neither."""
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("data", "result", "items", "Data", "Result", "records"):
                v = payload.get(key)
                if isinstance(v, list):
                    return v
            # a dict of one list value is unambiguous enough to accept
            lists = [v for v in payload.values() if isinstance(v, list)]
            if len(lists) == 1:
                return lists[0]
        return []

    def _to_entry(self, r: dict) -> Entry:
        name = str(_first(r, _NAME_KEYS) or "").strip()
        key = str(_first(r, _LICENCE_KEYS) or name).strip()
        activities = _first(r, _ACTIVITY_KEYS)
        if isinstance(activities, list):
            acts = [str(a) for a in activities if a]
        elif activities:
            acts = [str(activities)]
        else:
            acts = []

        return Entry(
            key=key,
            name=name,
            country="Saudi Arabia",
            segment=self._segment(acts),
            city=(str(_first(r, _CITY_KEYS)).strip() if _first(r, _CITY_KEYS) else None),
            website=self._website(_first(r, _WEBSITE_KEYS)),
            phone=(str(_first(r, _PHONE_KEYS)).strip() or None) if _first(r, _PHONE_KEYS) else None,
            licence_date=self._date(_first(r, _DATE_KEYS)),
            licence_type="; ".join(acts) or None,
            legal_name=None,
            # Deliberately not set: the register's activity vocabulary is unobserved, so asserting
            # multi-asset or third-party money here would be inventing evidence. Enrichment can
            # raise the score once a human or a researcher has seen the data.
            multi_asset=None,
            third_party=None,
            evidence={},
            raw={"api_record": r},
        )

    @staticmethod
    def _segment(acts: list[str]) -> Optional[str]:
        """Map CMA licensed activities onto our segments.

        The CMA's licensed activities are Dealing, Arranging, Managing, Advising and Custody.
        "Managing" is the one that matters to us. This mapping is written against the CMA's
        published activity vocabulary but has NOT been checked against a live payload.
        """
        joined = " | ".join(acts).lower()
        if not joined:
            return None
        if "manag" in joined or "إدارة" in joined:
            return "asset_manager"
        if "custod" in joined or "حفظ" in joined:
            return "custodian"
        if "deal" in joined or "broker" in joined or "تعامل" in joined:
            return "broker"
        return None

    @staticmethod
    def _website(value: Any) -> Optional[str]:
        v = str(value or "").strip()
        if not v:
            return None
        if not v.lower().startswith(("http://", "https://")):
            v = "https://" + v.lstrip("/")
        return v

    @staticmethod
    def _date(value: Any) -> Optional[str]:
        """Accept an ISO-ish date; return None rather than guessing at an unfamiliar format."""
        v = str(value or "").strip()
        if not v:
            return None
        if len(v) >= 10 and v[4] == "-" and v[7] == "-":
            return v[:10]
        return None


CONNECTOR = CMASaudiConnector
