#!/usr/bin/env python
"""Multilateral development bank procurement notices — RFP radar for the Gulf and Lebanon.

Who this is for: Andre Geha and the research agents that keep `crm/rfps/` current. Run it daily
alongside the register connectors (`python tools/connectors/multilateral_rfp.py`).

**Why this exists.** Local tender portals cover one market of four — TED/BOAMP work for France,
Etimad blocks automation, the UAE has no single portal and its emirate-level ones are JS apps (see
`knowledge/market/rfp-sources.md`). In the Gulf and Lebanon the addressable PUBLIC tender flow is
multilateral development banks, which fund financial-sector and capital-markets modernisation in
exactly our markets. This connector reads four of them:

| Source | How it is read | What it is |
|---|---|---|
| **World Bank** | `search.worldbank.org/api/v2/procnotices` — a real, filterable JSON API. No key. | Procurement notices tied to WB-financed projects. |
| **UNGM** | `ungm.org/Public/Notice/Search` — a JSON-over-POST endpoint behind a standard ASP.NET anti-forgery token, read exactly as a browser would (token + cookie, no login). | UN-system procurement across all 32 UN organisations. |
| **EBRD** | Investigated, NOT scraped. See "EBRD: why this one is not automated" below. | Raises loudly every run — this is a known, permanent gap, not a bug. |
| **IsDB** | `isdb.org/project-procurement/tenders` — a Drupal Views tender board. | Islamic Development Bank, Jeddah-based, lends across Saudi Arabia, the UAE and Lebanon (all IsDB member states; **France is not a member and structurally never appears**). |

## What counts as a genuine hit

Both of these must hold, checked in `classify()`:
1. **Country** — the notice's stated country/locality is UAE, Saudi Arabia, Lebanon or France
   (member-state structure permitting; see the France/IsDB note above).
2. **Subject matter** — the title (and, where the source hands it to us for free, the description)
   names a category we actually sell into: portfolio/investment/asset management, fund
   administration, core banking, treasury, capital markets systems, financial-sector
   modernisation. Checked in English AND French. And it must look like a **system/software**
   procurement, not an advisory mandate — see the rejection classes below.

## Known false-positive classes — rejected explicitly, with the real example that taught us each one

These are checked by `NEGATIVE_PATTERNS` before anything is accepted. Order matters: a negative
match short-circuits regardless of how well the positive keywords match.

1. **"Portfolio management" meaning PROJECT portfolio management** (a PMO function), not
   investment portfolio management. Same trap in French: *"portefeuille de projets"*.
2. **"Asset management" meaning IT-asset, real-estate or physical-asset management.** Found live
   on IsDB/World Bank: "Establishment of Road Asset Management System (RAMS)" — a literal road
   inventory system, nothing to do with investment assets.
3. **Consultancy/advisory mandates to SELECT an asset or fund manager, or to write an investment
   policy.** We are a software vendor, not a manager. Found live on IsDB: "BCC2025-056 The
   Development of an Investment Policy for an endowment out of a Charity Program" — a policy
   document, not a system.
4. **Individual consultant hires.** "INDIVIDUAL CONSULTANT SERVICES: Tadamon Data Monitoring and
   Platform Developer" (IsDB, Saudi Arabia) is a person, not a vendor procurement — and the
   "platform" in that title is a programme M&E dashboard, not an investment system.
5. **Loan-management/servicing systems for lending programmes** — microfinance, SME or
   agricultural-credit-guarantee operations. Found live on the World Bank: "Loan Management
   system" for KAFALAT's Lebanon Green Agrifood Transformation (GATE) project — a credit-guarantee
   institution's loan book, not portfolio/investment/fund management. Outside Gaia's scope even
   though "loan management system" sounds adjacent.
6. **Grants or technical-assistance programmes that fund OTHERS to build capacity**, not a
   procurement of a system for the issuer itself. Found live on the World Bank: "Islamic Finance
   Grant for the Development of Islamic Capital Market Products — GPN" — a grant facility, not a
   system RFP.
7. **French pension/public-investor buyers that tender asset-manager MANDATES, never software**
   (FRR, ERAFP, CNBF, CAVAMAC, CIPAV, FGDR, Carpimko, CNAVPL, Ircantec — per
   `knowledge/market/rfp-sources.md`). Whoever wins one of these mandates is a buyer worth
   sourcing separately; the mandate itself is not ours to bid.

A hit that clears the country and subject-matter checks but has no system/software/platform
indicator anywhere in the text we can see is also rejected — that is what stops advisory and
policy-development mandates leaking through when they happen to use our vocabulary.

## EBRD: why this one is not automated

`https://www.ebrd.com/work-with-us/procurement.html` is a static, reachable (200) informational
page. The actual notice-search tool it links to — `https://ecepp.ebrd.com/delta/noticeSearchResults.html`
— is a different animal: a ~3.8 MB enterprise portal whose page ships a `/delta/JavaScriptServlet`
(the signature of an Oracle ADF/JSF "partial page request" application) and a `<form method="post"
action="noticeSearch.html">` with **no static field names** — the request body is assembled
entirely client-side by JavaScript against server-held view state. This is architecturally the same
trap `knowledge/market/rfp-sources.md` documents for France's PLACE (a PRADO stateful postback that
"looks like it should work and silently returns the unfiltered list instead" for every keyword
tried). Building a scraper against an unconfirmed stateful contract like this would not fail — it
would return something that *looks* like a filtered result and never actually was, forever. Per the
same rule that stopped us doing that to PLACE, and per "we do not attempt to defeat bot protection"
for Etimad, this connector does **not** guess at ecepp.ebrd.com's contract. It raises loudly, by
name, on every run, so EBRD's absence from the brief is never mistaken for "EBRD had nothing."
Closing this needs a human with a browser, or an official EBRD procurement API/feed — neither of
which this connector invents.

## IsDB: a filter that looks real and is not

The tender board's exposed filters `locality` (country) and `status` do **not** filter server-side
— `?locality=LB`, `?locality=SA` and `?locality=AE` all return byte-identical result rows (verified
by diff; only the pager's own self-referential link text changes). `tender_type` genuinely DOES
filter (verified the same way). This connector therefore never relies on `locality`/`status`: it
fetches the full unfiltered listing (confirmed small and complete — 150 records across exactly 3
pages, page 4 onward is empty) and filters by the country label IsDB prints on every row
(`field--name-field-world-country`) client-side instead. If IsDB's listing ever grows past what a
handful of pages can hold, `MAX_ISDB_PAGES` below stops the fetch and raises rather than silently
truncating — the same guard `base.py` applies to register snapshots.

## Non-negotiables (same as every connector here)
- **Read-only.** No login, no form submission that isn't a public search.
- **Never invent.** A field the source does not state is `null` — most visibly `deadline`, which
  several genuine multilateral notices (general procurement notices, grant announcements) never
  give. `tools/crm.py`'s RFP schema was changed to make `deadline` nullable for exactly this reason
  — see `crm/SCHEMA.md`.
- **Fail loudly, per source.** A source that cannot be read raises and is reported BY NAME. It is
  never folded into "zero found" — that is the one rule this whole file exists to protect.
- **A genuine zero is a valid, expected, reportable result.** Most runs will find nothing, in every
  market. That is not a bug in the connector; UAE/Saudi Arabia/France are not World Bank or EBRD
  borrowers, and this category overwhelmingly moves by direct invitation, not open tender (see
  `knowledge/market/rfp-sources.md`, "What we cannot see").
- **Deterministic, sorted output. No wall-clock timestamps in what gets written or compared.**
- **Idempotent.** Re-running never creates a second record for the same notice — checked by both
  slug and `source_url` against the existing CRM.

Run `python tools/connectors/multilateral_rfp.py --help` for usage.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import crm  # noqa: E402  (path set above so this connector reuses the CRM's own code path)

try:
    from .base import ConnectorError
except ImportError:  # run directly, not as a package
    from base import ConnectorError

# We identify ourselves honestly. These are public procurement notices being read, at most, daily.
USER_AGENT = (
    "OFS-Sales-RFPConnector/1.0 "
    "(Omega Financial Solutions; business development; contact: andre.geha@omega-financial-solutions.com)"
)
DEFAULT_TIMEOUT = 30

# Our four markets, in the CRM's own spelling (see crm/companies/*.yaml, `country:`).
MARKETS = ["UAE", "Saudi Arabia", "Lebanon", "France"]


# ---------------------------------------------------------------------------
# Subject-matter classification
# ---------------------------------------------------------------------------

#: What we sell into, checked case-insensitively, English and French.
POSITIVE_PATTERNS = [re.compile(p, re.I) for p in [
    r"portfolio management", r"investment management", r"asset management",
    r"fund administration", r"fund management", r"core banking",
    r"treasury (?:management )?system", r"capital markets?", r"order management system",
    r"wealth management", r"net asset value", r"\bnav\b calculation", r"custody system",
    r"gestion de portefeuille", r"gestion d.actifs", r"gestion de fonds",
    r"gestion de fortune", r"valeur liquidative", r"syst.me de gestion des ordres",
]]

#: A category word alone is not enough — see class 3/4/6 below. Something has to say this is a
#: system/software procurement, not an advisory, policy or grant mandate.
SYSTEM_INDICATOR = re.compile(
    r"\b(system|software|platform|solution|application|infrastructure|digitalisation|"
    r"digitalization|technology|ict\b|it solution)\b|"
    r"\b(syst.me|logiciel|plateforme|solution|application|infrastructure|technologie|"
    r"num.rique)\b",
    re.I,
)

#: Known false-positive classes. Each entry is (compiled pattern, human reason). First match wins.
#: Every one of these was learned from a real hit found while building this connector — see the
#: module docstring for the specific notice that taught us each rule.
NEGATIVE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"project portfolio management|portfolio of projects|portefeuille de projets", re.I),
     "project-portfolio-management (PMO) or a portfolio of projects, not investment portfolio "
     "management"),
    (re.compile(r"\b(it|information technology|real[- ]estate|road|fixed|physical)\s+asset"
                r"(?:s)?\s+management", re.I),
     "IT-asset, real-estate or physical-asset (e.g. road) management, not investment asset "
     "management"),
    (re.compile(r"(select(?:ion)?|appoint(?:ment)?|engag(?:e|ement)|hir(?:e|ing)|retain(?:er)?|"
                r"recruit(?:ment)?)\s+(?:of\s+)?(?:an?\s+)?(?:external\s+)?"
                r"(?:asset|investment|fund)\s+manager", re.I),
     "advisory/consultancy mandate to SELECT an asset or fund manager — we are a software vendor, "
     "not a manager"),
    (re.compile(r"development of an? investment polic", re.I),
     "developing an investment POLICY document — an advisory mandate, not a software procurement"),
    (re.compile(r"individual consultant", re.I),
     "hiring an individual consultant (a person), not a vendor software procurement"),
    (re.compile(r"loan management system|loan management and", re.I),
     "a loan-management/servicing system for a lending programme (microfinance, SME or "
     "agricultural credit-guarantee) — not investment/portfolio/fund management"),
    (re.compile(r"data monitoring (?:and|&) platform", re.I),
     "a programme monitoring & evaluation (M&E) data platform for an unrelated development "
     "project, not an investment/portfolio management system"),
    (re.compile(r"\bgrant\b.{0,40}\bdevelopment of\b", re.I),
     "a grant or technical-assistance facility funding OTHERS to build capacity, not a "
     "procurement of a system for the issuer itself"),
    (re.compile(r"portefeuille de brevets", re.I),
     "French 'portefeuille' meaning a patent portfolio, not an investment portfolio"),
]

#: French public pension/investment bodies that tender asset-manager MANDATES, never software.
#: Per knowledge/market/rfp-sources.md — whoever wins one of these is a lead, but the mandate
#: itself is not ours to bid.
FRENCH_MANDATE_ISSUERS = re.compile(
    r"\b(FRR|ERAFP|CNBF|CAVAMAC|CIPAV|FGDR|Carpimko|CNAVPL|Ircantec)\b"
)


def classify(title: str, description: str, issuer: str,
             *, require_system_indicator: bool = True) -> tuple[bool, str]:
    """(is_genuine, reason). ``reason`` is human-readable either way — it is what a person checks
    before trusting an auto-created record, and it is what a rejection log line explains.

    ``require_system_indicator=False`` is for sources (UNGM) where we only ever see the title —
    the positive match already came from the SOURCE's own full-text search, so demanding a
    system/software word in the visible title would create false negatives for genuine hits that
    simply don't repeat the word in their short title. The negative-class and country checks still
    apply in full; this only relaxes the "must look like software" gate, and the resulting record's
    `fit_assessment` says so explicitly, flagging it for a closer human look.
    """
    text = f"{title} {description}"
    if FRENCH_MANDATE_ISSUERS.search(issuer or ""):
        return False, (
            f"issuer {issuer!r} is a French public pension/investment body that tenders "
            f"asset-manager mandates or financial advisory, never software (per "
            f"knowledge/market/rfp-sources.md)"
        )
    for pattern, reason in NEGATIVE_PATTERNS:
        if pattern.search(text):
            return False, f"rejected — {reason} (matched {pattern.pattern!r})"
    hit = next((p for p in POSITIVE_PATTERNS if p.search(text)), None)
    if not hit:
        return False, "no portfolio/investment/fund/core-banking/treasury/capital-markets term matched"
    if require_system_indicator and not SYSTEM_INDICATOR.search(text):
        return False, (
            f"matched category term {hit.pattern!r} but no system/software/platform indicator — "
            f"looks like an advisory, policy or grant mandate rather than a software procurement"
        )
    return True, f"matched category term {hit.pattern!r}" + (
        "" if require_system_indicator else
        " via the source's own full-text search (title alone did not show a system/software word "
        "— confirm manually before treating as biddable)"
    )


# ---------------------------------------------------------------------------
# HTTP helpers (small and local — this connector's request shapes don't fit base.py's
# fetch-a-register-page-of-firms pipeline, but the identification and failure discipline match it)
# ---------------------------------------------------------------------------

def _urlopen(req: urllib.request.Request, timeout: int = DEFAULT_TIMEOUT):
    return urllib.request.urlopen(req, timeout=timeout)


def http_get_json(url: str, *, timeout: int = DEFAULT_TIMEOUT) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with _urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                raise ConnectorError(f"{url} returned HTTP {resp.status}")
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raise ConnectorError(f"{url} returned HTTP {e.code} ({e.reason})") from e
    except urllib.error.URLError as e:
        raise ConnectorError(f"{url} unreachable: {e.reason}") from e
    except TimeoutError as e:
        raise ConnectorError(f"{url} timed out after {timeout}s") from e
    try:
        return json.loads(raw.decode("utf-8", errors="replace"))
    except json.JSONDecodeError as e:
        raise ConnectorError(f"{url} returned unparseable JSON: {e}") from e


def http_get_text(url: str, *, timeout: int = DEFAULT_TIMEOUT,
                   cookie: Optional[str] = None, extra_headers: Optional[dict] = None) -> tuple[str, list[str]]:
    """Returns (body, set_cookie_headers)."""
    headers = {"User-Agent": USER_AGENT}
    if cookie:
        headers["Cookie"] = cookie
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers)
    try:
        with _urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                raise ConnectorError(f"{url} returned HTTP {resp.status}")
            raw = resp.read()
            cookies = resp.headers.get_all("Set-Cookie") or []
    except urllib.error.HTTPError as e:
        raise ConnectorError(f"{url} returned HTTP {e.code} ({e.reason})") from e
    except urllib.error.URLError as e:
        raise ConnectorError(f"{url} unreachable: {e.reason}") from e
    except TimeoutError as e:
        raise ConnectorError(f"{url} timed out after {timeout}s") from e
    return raw.decode("utf-8", errors="replace"), cookies


# ---------------------------------------------------------------------------
# Notices — one shape shared by every source
# ---------------------------------------------------------------------------

@dataclass
class Notice:
    source: str            # short source key, e.g. "world_bank"
    source_id: str          # the source's own id, for logging/dedup
    title: str
    issuer: str
    country: str             # canonical CRM spelling — one of MARKETS
    raw_country: str         # exactly as the source stated it, for evidence
    source_url: str
    published_date: Optional[str] = None   # YYYY-MM-DD or None — never invented
    deadline: Optional[str] = None         # YYYY-MM-DD or None — never invented
    description: str = ""
    require_system_indicator: bool = True


# ---------------------------------------------------------------------------
# Source 1 — World Bank procurement notices API
# ---------------------------------------------------------------------------

WB_PROCNOTICES = "https://search.worldbank.org/api/v2/procnotices"
WB_PROJECT_DETAIL = "https://projects.worldbank.org/en/projects-operations/procurement-detail/{id}"
WB_REQUEST_DELAY = 0.2
WB_PAGE_SIZE = 200
WB_MAX_ROWS = 1000   # a hard ceiling — if a single country×term combo needs more than this, the
                      # query is too broad to trust and the run should say so, not silently truncate

#: Notices about a tender that is already over, not one we could ever bid on.
WB_EXCLUDED_TYPES = {"Contract Award", "Contract Termination"}
WB_EXCLUDED_STATUSES = {"Cancelled"}
#: Hiring a PERSON, not procuring software from a vendor — checked on the structured field, not by
#: guessing from title text. Found live: dozens of Lebanon "Employment-…" / "PMU …" / "Selection of
#: a…" notices that only reveal themselves as individual hires through this field, not their title.
WB_EXCLUDED_METHODS = {"Individual Consultant Selection"}

WB_COUNTRY_NAMES = {
    "UAE": "United Arab Emirates",
    "Saudi Arabia": "Saudi Arabia",
    "Lebanon": "Lebanon",
    "France": "France",
}

#: The same category list `classify()` checks, used here as the source's own full-text search terms
#: so we do not have to download and inspect its entire global notice volume ourselves.
SEARCH_TERMS = [
    "portfolio management", "asset management", "investment management", "fund administration",
    "fund management", "core banking", "treasury system", "capital markets",
    "order management system", "wealth management", "NAV calculation", "custody system",
    "gestion de portefeuille", "gestion d'actifs", "gestion de fonds", "gestion de fortune",
    "valeur liquidative",
]

_WB_MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def _wb_date(s: Optional[str]) -> Optional[str]:
    """'21-Sep-2026' -> '2026-09-21'. Never guesses a locale-dependent %b — same trap dfsa_difc.py
    avoids for the same reason (this run's locale is not guaranteed to be English)."""
    if not s:
        return None
    m = re.match(r"^(\d{1,2})-([A-Za-z]{3})-(\d{4})$", s.strip())
    if not m:
        return None
    day, mon, year = m.groups()
    month = _WB_MONTHS.get(mon.title())
    if not month:
        return None
    return f"{int(year):04d}-{month:02d}-{int(day):02d}"


def _wb_iso_date(s: Optional[str]) -> Optional[str]:
    """'2026-10-21T00:00:00Z' -> '2026-10-21'."""
    if not s:
        return None
    return s[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", s) else None


def _wb_query(country_name: str, term: str) -> list[dict]:
    rows: list[dict] = []
    offset = 0
    while True:
        qs = urllib.parse.urlencode({
            "format": "json", "rows": WB_PAGE_SIZE, "os": offset,
            "project_ctry_name_exact": country_name, "qterm": term,
        })
        data = http_get_json(f"{WB_PROCNOTICES}?{qs}")
        page = data.get("procnotices") or []
        rows.extend(page)
        total = int(data.get("total") or 0)
        offset += len(page)
        if not page or offset >= total or offset >= WB_MAX_ROWS:
            if offset >= WB_MAX_ROWS and offset < total:
                raise ConnectorError(
                    f"World Bank procnotices query (country={country_name!r}, term={term!r}) has "
                    f"{total} matches, past the {WB_MAX_ROWS}-row ceiling this connector trusts. "
                    f"The query is too broad — narrow the term list before this can be trusted."
                )
            break
        time.sleep(WB_REQUEST_DELAY)
    return rows


def fetch_world_bank() -> list[Notice]:
    seen: dict[str, dict] = {}
    for market, wb_name in WB_COUNTRY_NAMES.items():
        for term in SEARCH_TERMS:
            for row in _wb_query(wb_name, term):
                nid = row.get("id")
                if nid and nid not in seen:
                    seen[nid] = {"row": row, "market": market}
            time.sleep(WB_REQUEST_DELAY)
    if not seen:
        # A structural, expected zero (UAE/Saudi Arabia/France are not World Bank borrowers; see
        # module docstring) is still a successful fetch, not a failure — an empty *list* is
        # returned, and the caller reports "0 genuine hits", never "source unreadable".
        return []

    notices = []
    for nid, bundle in seen.items():
        row, market = bundle["row"], bundle["market"]
        if row.get("notice_type") in WB_EXCLUDED_TYPES or row.get("notice_status") in WB_EXCLUDED_STATUSES:
            continue
        if row.get("procurement_method_name") in WB_EXCLUDED_METHODS:
            continue
        title = (row.get("bid_description") or row.get("noticetitle") or "").strip()
        if not title:
            continue
        issuer = (row.get("agency_name") or row.get("project_name") or "World Bank-financed project").strip()
        # Deliberately NOT `notice_text` here. It is a long administrative HTML dump (loan/credit
        # info, procurement method, the project's own name repeated) and it bled through as noise
        # while building this connector — e.g. every notice under the Lebanon GATE project matched
        # "loan management system" via notice_text even when the title was "Senior Credit Analyst",
        # and generic "Fund"-programme boilerplate matched "fund administration" for a completely
        # unrelated grant-fund communications hire. `bid_description`/`noticetitle` is short and
        # specific by World Bank convention — matching on it alone is far higher precision.
        description = ""
        notices.append(Notice(
            source="world_bank",
            source_id=nid,
            title=title,
            issuer=issuer,
            country=market,
            raw_country=row.get("project_ctry_name") or market,
            source_url=WB_PROJECT_DETAIL.format(id=nid),
            published_date=_wb_date(row.get("noticedate")),
            deadline=_wb_iso_date(row.get("submission_deadline_date")),
            description=description,
            require_system_indicator=True,
        ))
    return notices


# ---------------------------------------------------------------------------
# Source 2 — UNGM (United Nations Global Marketplace)
# ---------------------------------------------------------------------------

UNGM_NOTICE_PAGE = "https://www.ungm.org/Public/Notice"
UNGM_SEARCH = "https://www.ungm.org/Public/Notice/Search"
UNGM_NOTICE_DETAIL = "https://www.ungm.org/Public/Notice/{id}"
UNGM_REQUEST_DELAY = 4.0   # UNGM rate-limits aggressively (HTTP 429) under rapid-fire requests —
                            # verified empirically while building this connector. This is a
                            # deliberately conservative pace, not a guess.
UNGM_PAGE_SIZE = 15         # the server rejects anything larger (HTTP 400) — the UI hardcodes 15.
UNGM_MAX_PAGES = 5          # 75 notices per country is far more than this niche category needs;
                            # a genuine excess raises rather than silently stopping partway.

#: UNGM's internal numeric country ids — read once, live, from the search page's own country
#: dropdown (`<option value="…">United Arab Emirates</option>`), not guessed.
UNGM_COUNTRY_IDS = {
    "UAE": 2505,
    "Saudi Arabia": 2471,
    "Lebanon": 2405,
    "France": 2363,
}

#: ⚠ Retained only as documentation of a measured dead end. These were once passed to UNGM's own
#: `Description` filter; on 2026-09-23 all six matched nothing in all four markets while the
#: unfiltered country lists were populated. `fetch_ungm` no longer uses them — it reads whole
#: country lists and filters with our own auditable classifier. Do not reintroduce source-side
#: keyword filtering here without re-measuring: a filter that silently matches nothing reads
#: exactly like a quiet market.
UNGM_SEARCH_TERMS_UNUSED = [
    "portfolio management", "asset management", "investment management",
    "fund administration", "core banking", "capital markets",
]

_TOKEN_RE = re.compile(r'__RequestVerificationToken"\s*type="hidden"\s*value="([^"]+)"')


class _UNGMSession:
    """Reads the anti-forgery token and session cookie exactly as a browser would, then POSTs a
    JSON search. No login, no account — this is the same public search the notice page itself
    runs, just called directly."""

    def __init__(self) -> None:
        self.token: Optional[str] = None
        self.cookie: Optional[str] = None

    def open(self) -> None:
        body, cookies = http_get_text(UNGM_NOTICE_PAGE)
        m = _TOKEN_RE.search(body)
        if not m:
            raise ConnectorError(
                "UNGM notice search page has no __RequestVerificationToken field. The page has "
                "changed — this connector needs updating before UNGM's results can be trusted."
            )
        self.token = m.group(1)
        self.cookie = "; ".join(c.split(";", 1)[0] for c in cookies)

    def search(self, country_id: int, description: str, page_index: int = 0) -> str:
        if not self.token:
            self.open()
        payload = {
            "PageIndex": page_index, "PageSize": UNGM_PAGE_SIZE, "Title": None,
            "Description": description,
            "Reference": None, "PublishedFrom": None, "PublishedTo": None, "DeadlineFrom": None,
            "DeadlineTo": None, "Countries": [country_id], "Agencies": [], "UNSPSCs": [],
            "NoticeTypes": [], "SortField": "DatePublished", "SortAscending": False,
            "isPicker": False, "IsSustainable": False, "IsActive": True,
            "NoticeDisplayType": None, "NoticeSearchTotalLabelId": None, "TypeOfCompetitions": [],
        }
        req = urllib.request.Request(
            UNGM_SEARCH,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "User-Agent": USER_AGENT,
                "Content-Type": "application/json; charset=UTF-8",
                "RequestVerificationToken": self.token,
                "X-Requested-With": "XMLHttpRequest",
                "Referer": UNGM_NOTICE_PAGE,
                "Accept": "*/*",
                "Cookie": self.cookie or "",
            },
            method="POST",
        )
        try:
            with _urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
                if resp.status != 200:
                    raise ConnectorError(f"UNGM search returned HTTP {resp.status}")
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            raise ConnectorError(f"UNGM search returned HTTP {e.code} ({e.reason})") from e
        except urllib.error.URLError as e:
            raise ConnectorError(f"UNGM search unreachable: {e.reason}") from e


_UNGM_ROW_RE = re.compile(r'data-noticeid="(\d+)"\s+class="tableRow dataRow', re.S)
_UNGM_TITLE_RE = re.compile(r'ungm-title ungm-title--small">\s*(.*?)\s*</span>', re.S)
_UNGM_NOTICE_LINK_RE = re.compile(r"/Public/Notice/(\d+)'>")
_UNGM_DEADLINE_RE = re.compile(
    r'resultInfo1 deadline"[^>]*>\s*<span>\s*(\d{1,2}-[A-Za-z]{3}-\d{4})', re.S)
_UNGM_PUBLISHED_RE = re.compile(
    r'</div>\s*<div role="cell" class="tableCell">\s*<span>\s*(\d{1,2}-[A-Za-z]{3}-\d{4})', re.S)
_UNGM_AGENCY_RE = re.compile(r'resultAgency">\s*<span>(.*?)</span>', re.S)


def _ungm_date(s: Optional[str]) -> Optional[str]:
    return _wb_date(s)  # same 'DD-Mon-YYYY' shape; reuse rather than duplicate the month table


def _parse_ungm_rows(html_fragment: str) -> list[dict]:
    parts = html_fragment.split('class="tableRow dataRow notice-table">')[1:]
    out = []
    for part in parts:
        title_m = _UNGM_TITLE_RE.search(part)
        link_m = _UNGM_NOTICE_LINK_RE.search(part)
        deadline_m = _UNGM_DEADLINE_RE.search(part)
        published_m = _UNGM_PUBLISHED_RE.search(part)
        agency_m = _UNGM_AGENCY_RE.search(part)
        if not (title_m and link_m):
            continue
        out.append({
            "id": link_m.group(1),
            "title": html.unescape(title_m.group(1)).strip(),
            "agency": html.unescape(agency_m.group(1)).strip() if agency_m else "UN system",
            "deadline": _ungm_date(deadline_m.group(1)) if deadline_m else None,
            "published": _ungm_date(published_m.group(1)) if published_m else None,
        })
    return out


def fetch_ungm() -> list[Notice]:
    """Read every open notice in each of our four markets, and let OUR classifier decide.

    ⚠ **This deliberately does not use UNGM's own full-text search, and that is a correction.** An
    earlier version queried a list of curated terms and reported what came back. Measured on
    2026-09-23: that returned **zero** notices for all four markets, while an unfiltered query for
    the UAE alone returned a full page of live notices. The radar was reading a real, populated
    source and reporting an empty market.

    That failure mode is the dangerous one, because it is indistinguishable from good news. A
    source-side keyword filter is a black box we cannot audit: when it matches nothing we cannot
    tell "nothing is there" from "our words were wrong". Our own classifier is auditable — every
    rejection it makes is printed with its reason — so the whole country list is fetched and
    filtered here, exactly as the IsDB source already does.

    The per-country volume that makes this affordable is small (tens, not thousands). If it ever
    stops being small, the page guard below fails loudly rather than truncating.
    """
    session = _UNGMSession()
    session.open()
    seen: dict[str, dict] = {}
    for market, country_id in UNGM_COUNTRY_IDS.items():
        for page in range(UNGM_MAX_PAGES):
            html_fragment = session.search(country_id, "", page_index=page)
            rows = _parse_ungm_rows(html_fragment)
            for row in rows:
                if row["id"] not in seen:
                    seen[row["id"]] = {"row": row, "market": market}
            time.sleep(UNGM_REQUEST_DELAY)
            if len(rows) < UNGM_PAGE_SIZE:
                break   # a short page is the last page
        else:
            # Every page we were willing to read came back full: there is more we have not seen,
            # and silently keeping the first 75 would be exactly the quiet miss this rewrite fixes.
            raise ConnectorError(
                f"UNGM returned {UNGM_MAX_PAGES} full pages for {market!r} "
                f"({UNGM_MAX_PAGES * UNGM_PAGE_SIZE} notices) and there may be more. Raise "
                f"UNGM_MAX_PAGES or narrow the query before this market can be trusted."
            )
    notices = []
    for nid, bundle in seen.items():
        row, market = bundle["row"], bundle["market"]
        notices.append(Notice(
            source="ungm",
            source_id=nid,
            title=row["title"],
            issuer=row["agency"],
            country=market,
            raw_country=market,   # UNGM's row does not repeat the filtered country as text
            source_url=UNGM_NOTICE_DETAIL.format(id=nid),
            published_date=row["published"],
            deadline=row["deadline"],
            # ⚠ The listing carries only the title, so the classifier sees a title and nothing else.
            # That makes UNGM the one source where a genuinely relevant notice with an uninformative
            # title can be missed — recorded here rather than pretended away.
            description="",
            require_system_indicator=False,
        ))
    return notices


# ---------------------------------------------------------------------------
# Source 3 — EBRD. Investigated; deliberately not scraped. See module docstring.
# ---------------------------------------------------------------------------

EBRD_INFO_PAGE = "https://www.ebrd.com/work-with-us/procurement.html"
EBRD_PORTAL = "https://ecepp.ebrd.com/delta/noticeSearchResults.html"


def fetch_ebrd() -> list[Notice]:
    # Confirm the informational page really is up — this IS checked live, every run, so a change
    # here (e.g. EBRD finally shipping a real API) gets noticed rather than assumed away forever.
    http_get_text(EBRD_INFO_PAGE)
    raise ConnectorError(
        f"EBRD: {EBRD_INFO_PAGE} is reachable, but the actual notice search "
        f"({EBRD_PORTAL}) is a stateful enterprise JSF/ADF portal with no confirmed static "
        f"query-string or REST contract — the same shape as France's PLACE portal, which "
        f"knowledge/market/rfp-sources.md already documents as unsafe to scrape (a stateful "
        f"postback that silently returns the unfiltered list for every query tried). This "
        f"connector does not guess at that contract. Needs a human with a browser, or an official "
        f"EBRD procurement API/feed, before EBRD can be added here."
    )


# ---------------------------------------------------------------------------
# Source 4 — IsDB (Islamic Development Bank)
# ---------------------------------------------------------------------------

ISDB_TENDERS = "https://www.isdb.org/project-procurement/tenders"
ISDB_MAX_PAGES = 20   # confirmed today that the real listing is exactly 3 pages (page 3 onward is
                       # empty); this ceiling is a truncation guard, not the expected page count.

ISDB_COUNTRY_NAMES = {
    "UAE": "United Arab Emirates",
    "Saudi Arabia": "Saudi Arabia",
    "Lebanon": "Lebanon",
    # France is not an IsDB member state and structurally never appears — not a gap, a fact.
}

_ISDB_MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August", "September",
     "October", "November", "December"], 1)}

_ISDB_TITLE_RE = re.compile(r'<h2><a href="([^"]+)"[^>]*>([^<]*)</a>', re.S)
_ISDB_COUNTRY_RE = re.compile(
    r'field--name-field-world-country[^>]*>([^<]*)</div>', re.S)
_ISDB_CLOSE_RE = re.compile(
    r'field--name-field-close-date.*?<time[^>]*>([^<]*)</time>', re.S)


def _isdb_date(s: Optional[str]) -> Optional[str]:
    """'24 August 2025' -> '2025-08-24'. English full month name — IsDB's tenders board is
    English-first even where individual notices are in French."""
    if not s:
        return None
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$", s.strip())
    if not m:
        return None
    day, mon, year = m.groups()
    month = _ISDB_MONTHS.get(mon.title())
    if not month:
        return None
    return f"{int(year):04d}-{month:02d}-{int(day):02d}"


def fetch_isdb() -> list[Notice]:
    rows: list[dict] = []
    for page in range(ISDB_MAX_PAGES):
        body, _ = http_get_text(f"{ISDB_TENDERS}?page={page}")
        parts = body.split("views-row")[1:]
        if not parts:
            break
        for part in parts:
            title_m = _ISDB_TITLE_RE.search(part)
            country_m = _ISDB_COUNTRY_RE.search(part)
            close_m = _ISDB_CLOSE_RE.search(part)
            if not title_m:
                continue
            rows.append({
                "url": title_m.group(1),
                "title": html.unescape(title_m.group(2)).strip(),
                "country": html.unescape(country_m.group(1)).strip() if country_m else "",
                "close_date": _isdb_date(close_m.group(1)) if close_m else None,
            })
        time.sleep(0.3)
    else:
        raise ConnectorError(
            f"IsDB tender board did not end within {ISDB_MAX_PAGES} pages — the listing has grown "
            f"far past what was confirmed when this connector was built (3 pages, 150 rows). "
            f"Refusing to assume completeness; raise the ceiling only after checking why."
        )
    if not rows:
        raise ConnectorError(
            f"{ISDB_TENDERS} returned zero tenders on the very first page. IsDB's board is never "
            f"empty — treating this as a fetch or markup-change failure, not a quiet day."
        )

    by_country = {v: k for k, v in ISDB_COUNTRY_NAMES.items()}
    notices = []
    for row in rows:
        market = by_country.get(row["country"])
        if not market:
            continue
        url = row["url"]
        full_url = url if url.startswith("http") else f"https://www.isdb.org{url}"
        notices.append(Notice(
            source="isdb",
            source_id=url,
            title=row["title"],
            issuer="Islamic Development Bank (IsDB)",
            country=market,
            raw_country=row["country"],
            source_url=full_url,
            published_date=None,   # the listing does not state one
            deadline=row["close_date"],
            description="",        # listing shows title only; detail page not fetched unless the
                                     # title alone already clears classify() (kept two-stage, like
                                     # dfsa_difc.py, to stay a light touch on the source)
            require_system_indicator=True,
        ))
    return notices


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

#: (display name, short key, fetcher). The short key is the one each `Notice.source` carries, and
#: it is here so a per-source tally can be joined back to the source that produced it — reporting
#: "0 rejected" for a source that in fact rejected 88 notices makes a working filter look idle.
SOURCES = [
    ("World Bank eProcure (procurement notices API)", "world_bank", fetch_world_bank),
    ("UNGM (UN Global Marketplace)", "ungm", fetch_ungm),
    ("EBRD procurement", "ebrd", fetch_ebrd),
    ("IsDB (Islamic Development Bank) tenders", "isdb", fetch_isdb),
]


def _existing_rfp_index() -> tuple[set[str], set[str]]:
    """(slugs, source_urls) already in the CRM, so a rerun never creates a duplicate record."""
    slugs, urls = set(), set()
    for rec in crm.load_all_rfps():
        if rec.get("slug"):
            slugs.add(rec["slug"])
        if rec.get("source_url"):
            urls.add(rec["source_url"])
    return slugs, urls


def _slug_for(issuer: str, title: str) -> str:
    return crm.slugify(f"{issuer}-{title}")


def run(*, dry_run: bool = False) -> dict:
    results = []
    failures = []
    all_notices: list[Notice] = []

    for name, key, fetch_fn in SOURCES:
        try:
            notices = fetch_fn()
            results.append({"source": name, "key": key, "found": len(notices)})
            all_notices.extend(notices)
        except ConnectorError as e:
            failures.append({"source": name, "key": key, "error": str(e)})
        except Exception as e:  # noqa: BLE001 — an unexpected bug must be loud, not silent
            failures.append({"source": name, "key": key,
                             "error": f"unexpected {type(e).__name__}: {e}"})

    existing_slugs, existing_urls = _existing_rfp_index()
    created, rejected, skipped = [], [], []

    # Sorted for deterministic output — never in fetch order, which depends on dict iteration and
    # network timing.
    all_notices.sort(key=lambda n: (n.source, n.country, n.source_id))

    for notice in all_notices:
        if notice.country not in MARKETS:
            continue  # should not happen given per-source filtering, but never trust it silently
        is_genuine, reason = classify(
            notice.title, notice.description, notice.issuer,
            require_system_indicator=notice.require_system_indicator,
        )
        if not is_genuine:
            rejected.append({"source": notice.source, "title": notice.title,
                             "country": notice.country, "reason": reason})
            continue

        slug = _slug_for(notice.issuer, notice.title)
        if slug in existing_slugs or notice.source_url in existing_urls:
            skipped.append({"slug": slug, "title": notice.title, "reason": "already in the CRM"})
            continue

        fit_assessment = (
            f"Auto-detected by tools/connectors/multilateral_rfp.py from {notice.source} "
            f"({notice.raw_country}). {reason}. Not yet human-reviewed — confirm the buyer and "
            f"subject matter before treating this as biddable."
        )
        record_kwargs = {
            "title": notice.title, "issuer": notice.issuer, "slug": None,
            "country": notice.country, "segment": None, "source_url": notice.source_url,
            "published_date": notice.published_date, "deadline": notice.deadline,
            "status": "spotted", "fit_assessment": fit_assessment, "outcome": "pending",
            "reason": None, "owner": crm.DEFAULT_OWNER,
        }
        if dry_run:
            # Still reserve the slug/url within this run, purely for reporting — two genuine
            # candidates in the same dry run that would collide should show as one "would create"
            # and one "already accounted for", the same shape a real run would produce.
            existing_slugs.add(slug)
            existing_urls.add(notice.source_url)
            created.append({"slug": slug, "title": notice.title, "country": notice.country,
                            "source": notice.source, "dry_run": True})
        else:
            ns = argparse.Namespace(**record_kwargs)
            rc = crm.cmd_rfp_add(ns)
            if rc == 0:
                existing_slugs.add(slug)
                existing_urls.add(notice.source_url)
                created.append({"slug": slug, "title": notice.title, "country": notice.country,
                                "source": notice.source, "dry_run": False})
            else:
                failures.append({"source": notice.source,
                                 "error": f"crm.py rfp add failed for {notice.title!r} (slug {slug!r})"})

    return {
        "sources_ok": results,
        "sources_failed": failures,
        "created": created,
        "rejected": rejected,
        "skipped": skipped,
        "dry_run": dry_run,
    }


def format_report(result: dict) -> str:
    lines = ["Multilateral RFP radar — World Bank / UNGM / EBRD / IsDB"]
    for r in result["sources_ok"]:
        lines.append(f"  [ok]     {r['source']}: {r['found']} candidate notice(s) in our markets")
    for f in result["sources_failed"]:
        lines.append(f"  [FAILED] {f['source']}")
        lines.append(f"           {f['error']}")
        lines.append("           This is NOT a quiet day for this source — it could not be read.")
    lines.append("")
    if result["created"]:
        for c in result["created"]:
            tag = "WOULD CREATE" if c["dry_run"] else "CREATED"
            lines.append(f"  + {tag}  [{c['country']}] {c['title']}  (via {c['source']}, {c['slug']})")
    else:
        lines.append("  0 genuine hits created this run.")
    if result["skipped"]:
        lines.append(f"  {len(result['skipped'])} candidate(s) already in the CRM, skipped.")
    if result["rejected"]:
        lines.append(f"  {len(result['rejected'])} candidate(s) rejected after filtering:")
        for r in result["rejected"]:
            lines.append(f"    - [{r['country']}] {r['title']!r} ({r['source']}) — {r['reason']}")
    lines.append("")
    lines.append(
        "A zero here across every reachable source is expected and honest — see the module "
        "docstring's 'What we cannot see' equivalent: UAE, Saudi Arabia and France are not World "
        "Bank/EBRD borrowers, this category moves overwhelmingly by direct invitation, and a clean "
        "run is not the same claim as 'the market is quiet'."
    )
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--dry-run", action="store_true",
                    help="fetch, filter and report what would be created; write nothing")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a text report")
    args = ap.parse_args(argv)

    result = run(dry_run=args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result))

    if result["sources_failed"]:
        print(f"\n{len(result['sources_failed'])} of {len(SOURCES)} sources FAILED.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
