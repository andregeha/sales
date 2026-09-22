#!/usr/bin/env python
"""FSRA (Abu Dhabi, ADGM) — public register of financial firms.

ADGM is the other half of the UAE's onshore-free-zone picture and does not overlap with the DIFC at
all — a firm is licensed by one or the other, never both. **497 firms** on the register as at
2026-09-22.

**This is the best-quality source we have found anywhere**, because the FSRA's own listing API
returns, for each firm: name, permission number, status, full address, **date the financial-services
permission was granted** (`fspDate`), legal status, telephone number — and, for over half of them,
**an email address**. Published by the regulator, on its own register, for the firm's own contact.

That last point is worth stating plainly: it is the difference between having a name and being able
to write to someone. Nothing here is guessed or pattern-inferred.

**How it is read.** A single JSON API, no browser and no scraping of rendered HTML:
``POST /api/fsrac/firms/listing/filter`` with ``{"currentPage": N, "itemsPerPage": 100}``.
Five requests return the whole register.

**Two-stage, because the listing has no activities.** The CRM requires a segment, and the listing
does not say what a firm is *authorised to do*. The **detail page** does, so it is fetched **only
for firms we are about to create** — never for all 497 on a routine run. Requests are spaced.

⚠ The listing includes **withdrawn** firms (``companyStatus``/``withdrawnDate``). A withdrawn firm
handed its licence back; it is not a lead and is excluded.
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

BASE = "https://www.adgm.com"
LISTING_API = f"{BASE}/api/fsrac/firms/listing/filter"
REGISTER_PAGE = f"{BASE}/public-registers/fsra"

PAGE_SIZE = 100
REQUEST_DELAY = 0.4

#: FSRA regulated activities → our segments. Ordered: the first match wins, most specific first.
ACTIVITY_SEGMENTS = [
    ("managing a collective investment fund", "fund_manager"),
    ("managing assets", "asset_manager"),
    ("managing a profit sharing investment account", "asset_manager"),
    ("accepting deposits", "bank"),
    ("providing custody", "custodian"),
    ("dealing in investments", "broker"),
]

def _flatten(html_text: str) -> str:
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", "", html_text)
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "|", t))
    return re.sub(r"(\|\s*)+", "|", t)


class FSRAADGMConnector(Connector):
    register = "fsra-adgm"
    regulator = "FSRA (ADGM)"
    country = "UAE"
    source_name = "FSRA public register of financial firms (ADGM)"
    source_url = REGISTER_PAGE

    def __init__(self) -> None:
        self._activities: dict[str, list[str]] = {}

    # -- fetching ---------------------------------------------------------

    def _post(self, page: int) -> dict:
        body = json.dumps({"currentPage": page, "itemsPerPage": PAGE_SIZE}).encode()
        req = Request(LISTING_API, data=body, headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        try:
            with urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8", errors="replace"))
        except Exception as e:  # noqa: BLE001
            raise ConnectorError(f"FSRA listing API failed on page {page}: {e}") from e
        finally:
            time.sleep(REQUEST_DELAY)

    def _get(self, url: str) -> str:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urlopen(req, timeout=60) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            raise ConnectorError(f"FSRA detail page failed ({url}): {e}") from e
        finally:
            time.sleep(REQUEST_DELAY)

    def fetch(self) -> list[Entry]:
        first = self._post(1)
        total = first.get("totalItems")
        if not total:
            raise ConnectorError(
                "FSRA listing API reported no firms. A live register is never empty — treating "
                "this as a broken query, not a quiet day."
            )

        rows = list(first.get("firmListingVM") or [])
        pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
        for p in range(2, pages + 1):
            rows.extend(self._post(p).get("firmListingVM") or [])

        if not rows:
            raise ConnectorError("FSRA listing API returned no rows despite a non-zero total.")

        entries = []
        for r in rows:
            e = self._row_to_entry(r)
            if e is not None:
                entries.append(e)
        if not entries:
            raise ConnectorError(
                f"FSRA returned {len(rows)} rows but none survived parsing. This is a schema "
                f"change, not an empty register."
            )
        return entries

    def _row_to_entry(self, r: dict) -> Optional[Entry]:
        name = (r.get("company") or "").strip()
        key = (r.get("permissionNumber") or r.get("firmID") or "").strip()
        if not name or not key:
            return None
        # A withdrawn firm handed its licence back. Not a lead.
        if (r.get("companyStatus") or "").strip().lower() != "active":
            return None
        if (r.get("withdrawnDate") or "").strip():
            return None

        return Entry(
            key=key,
            name=name,
            country="UAE",
            segment=None,                       # filled from the detail page, for new firms only
            city=(r.get("citi") or "Abu Dhabi").strip() or "Abu Dhabi",
            website=self._clean_url(r.get("website")),
            phone=(r.get("phoneNumber") or "").strip() or None,
            licence_date=(r.get("fspDate") or "").strip() or None,
            licence_type=None,                  # ditto
            legal_name=None,
            multi_asset=None,
            third_party=None,
            evidence={},
            raw={
                "detail_url": BASE + (r.get("pageUrl") or ""),
                "email": (r.get("email") or "").strip() or None,
                "address": (r.get("address") or "").strip() or None,
                "legal_status": (r.get("legalStatus") or "").strip() or None,
                "firm_id": r.get("firmID"),
            },
        )

    @staticmethod
    def _clean_url(v: Optional[str]) -> Optional[str]:
        v = (v or "").strip()
        if not v:
            return None
        return v if v.lower().startswith(("http://", "https://")) else "https://" + v.lstrip("/")

    # -- detail: regulated activities, only for firms we are about to record

    def _load_activities(self, entry: Entry) -> Optional[list[str]]:
        url = entry.raw.get("detail_url")
        if not url:
            return None
        if url in self._activities:
            return self._activities[url]
        try:
            flat = _flatten(self._get(url))
        except ConnectorError:
            # ⚠ A failed detail fetch must NOT look like "this firm does nothing we sell to".
            # None means "we could not find out"; [] means "we looked and it does not match".
            self._activities[url] = None
            return None
        # Scan the whole page rather than trying to isolate the activities table. Verified safe:
        # the page's filter controls do NOT contain activity names, so a match is a real
        # authorisation and not a dropdown option. Isolating the table by its heading was tried
        # first and broke, because "Regulated Activities" is also a tab label above the data.
        text = flat.lower()
        found = [needle for needle, _seg in ACTIVITY_SEGMENTS if needle in text]
        self._activities[url] = found
        return found

    def build_record(self, entry: Entry, snapshot_file: str) -> dict:
        acts = self._load_activities(entry)
        if acts is None:
            # Unknown, not absent. It will be skipped for lack of a segment, and the reason will
            # say why — so a transient network failure is never mistaken for a firm we assessed.
            entry.licence_type = "⚠ detail page unreachable — activities NOT established"
            return super().build_record(entry, snapshot_file)
        for needle, seg in ACTIVITY_SEGMENTS:
            if needle in acts:
                entry.segment = seg
                break
        entry.licence_type = "; ".join(a.title() for a in acts) or None
        if entry.segment in {"asset_manager", "fund_manager"}:
            entry.third_party = True
            entry.evidence = {"third_party": f"FSRA-authorised for {entry.licence_type}"}

        rec = super().build_record(entry, snapshot_file)

        addr = entry.raw.get("address")
        if addr:
            rec["activities"][0]["summary"] += f" Registered address (per the FSRA): {addr}"

        email, phone = entry.raw.get("email"), entry.phone
        if email or phone:
            rec["contacts"].append({
                "name": f"{entry.name} — contact published on the FSRA register",
                "title": "General enquiries",
                "role": "unknown",
                "email": email,
                "phone": phone,
                "linkedin": None,
                "language": "en",
                "notes": (
                    "Email and/or telephone exactly as the FSRA publishes them on its own public "
                    "register — not guessed, not pattern-inferred. ⚠ The address the regulator "
                    "holds is often a named individual's work address rather than a general inbox; "
                    "check who it belongs to before writing, and treat it as a real person."
                ),
                "source": f"FSRA public register, {entry.raw.get('detail_url')}",
            })
        return rec

    def tags_for(self, entry: Entry) -> list[str]:
        return super().tags_for(entry) + ["uae", "adgm", "fsra"]


CONNECTOR = FSRAADGMConnector
