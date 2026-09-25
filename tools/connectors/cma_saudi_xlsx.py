#!/usr/bin/env python
"""CMA (Saudi Arabia) — "Institutions under supervision of CMA" quarterly Excel workbook.

⚠ **Distinct from, and coexists with, `cma_saudi.py`.** That connector reads the CMA's *Authorised
Persons* HTML page — a partial, newest-first slice (36 of 242) that uniquely carries per-firm
licensed-activity codes (MI/MIOF/Arr/Adv/D/C). This connector reads a completely different document
this workbook's own docstring did not know about: a bulk, per-firm Excel workbook the CMA publishes
in its open-data section. Neither replaces the other — they are kept side by side under different
register names (`cma-saudi` vs **`cma-saudi-xlsx`**) precisely because they see different, only
partially overlapping, slices of the same regulator's population. Do not merge them.

**How it was found.** `https://cma.gov.sa/sitemap.xml` (690 URLs, genuinely present — unlike SAMA's
fallback, see `sama_saudi.py`) surfaced `AboutCMA/ResearchAndReports/opendata/Pages/default.aspx`,
which links ten downloadable `.xlsx` files. Nine are aggregate time series (industry totals) with no
per-firm rows — this matches, and does not contradict, what `cma_saudi.py`'s docstring already
concluded about "the CMA's downloadable open-data files". The tenth, **"Institutions under
supervision of CMA"**, is different: a per-firm quarterly report.

    GET https://cma.gov.sa/AboutCMA/ResearchAndReports/opendata/Documents/CMI%20report/excel/
        Institutions%20under%20supervision%20of%20CMA.xlsx

Verified live 2026-09-24: HTTP 200, 806,724 bytes, a plain static-file GET — no auth, no WAF, no
CAPTCHA, no JavaScript. 17 sheets, bilingual, sheet names in Arabic (so this connector locates sheets
by **position**, verified against each sheet's own printed "Table (N):" title before it is read —
see `_verify_table_title` — rather than trusting sheet-name strings or position alone to still be
right in a future edition).

⚠ **Cover-sheet date is wrong; trust the data, not the cover.** The cover sheet reads "31st Issue —
Second Quarter 2025", but every per-firm sheet's quarterly columns run through **Q1 2026** — measured
directly from the column headers, not inferred. This is an observed discrepancy the file itself does
not explain; treated here as "the data is current to Q1 2026", stated plainly rather than silently
trusting either the cover or the columns.

**Three sheets read, three different things they tell us:**

| Table | Sheet content | Measured firms | Segment |
|---|---|---:|---|
| **8**  | AUM per CMI (public/private funds + discretionary portfolio management), SAR million/quarter | 122 | `asset_manager` |
| **14** | Number of public/private funds per CMI, per quarter | 127 | `fund_manager` (see priority note below) |
| **15** | AUM under custodial activity, SAR million/quarter | 43 | `custodian` |

A fourth per-firm sheet, **Table 1 — Indicators of Workforce at Capital Market Institutions** (~219
firms, the closest thing to the CMA's full population), is deliberately **not read**: headcount alone
is not a segment, and inventing one from it would be a guess dressed up as data. It exists in the
workbook as context for how much of the CMA's population these three tables reach (roughly 60%), not
as a fourth source of records.

**Segment priority when a firm appears in more than one table** — same convention `cma_uae.py` uses
for its overlapping licence categories: a firm actually running public/private funds (Table 14) is a
`fund_manager` even if it also shows a portfolio-management AUM figure (Table 8); a firm with an AUM
figure but no funds is an `asset_manager`; a firm appearing only in the custody table is a
`custodian`. Measured overlap: of 144 total distinct firms across the three tables, 127 land as
`fund_manager`, 11 as `asset_manager` (in Table 8 but not 14), 6 as `custodian`-only.

**"Latest non-empty quarter", not the first or last column found — and why.** Every sheet's columns
run oldest-to-newest, but a newer entrant to the register has blank cells for quarters before it
existed, and (rarely) a firm can have a gap in a single quarter's filing. Taking the right-most
column blindly would silently record `None` for a firm that stopped reporting one quarter early; this
connector walks each firm's row from the newest quarter backward and takes the first cell that holds
an actual number (Excel string values like `"NA"` — the workbook's own marker for "not licensed at
the time" — are explicitly not numbers and are skipped, not coerced to zero).

**Join key.** No stable per-firm ID is confirmed across quarterly editions — the workbook's own
row-order `#` column resets and reorders release to release, so it is not used as a key at all. This
connector joins the three tables, and keys the CRM record, on the **normalised English name**
(`base.normalize_name`), the same folding the rest of this codebase uses for deduplication. This is
an accepted, explicit trade-off: a firm that changes its registered English name between one
quarterly edition and the next will look like one firm disappearing and a different one appearing,
rather than a rename being detected. Recorded in `memory/open-questions.md` rather than silently
assumed away.

**What this file does NOT publish, and therefore never appears on a record from it:** address, phone,
email, website, or licence date. Every record from this connector is a name, a segment, and (where
Table 8 or 15 supplied one) an AUM or custodial-AUM figure in SAR million — nothing invented to fill
the gap. Because no licence date is published, **the automatic trigger score from this source is
always zero** and a baseline run creates no CRM records at all (the base pipeline's baseline window
is licence-date-gated); a `--backfill` run is what actually populates the CRM from this source, the
same one-time step the connector's own module docstring in `run_all.py`'s README describes for other
date-less registers.

**Names.** `TitleEn`'s counterpart in this workbook is the English company name; kept as `name`. The
Arabic name is kept as `legal_name` — the same call `sama_saudi.py` makes and for the same reason: a
Saudi capital-market institution's Arabic name on its own regulator's filing is its registered legal
name, English being the trading translation.
"""

from __future__ import annotations

import re
from io import BytesIO
from typing import Optional

import openpyxl

try:
    from .base import Connector, ConnectorError, Entry, http_get, normalize_name
except ImportError:  # run directly, not as a package
    from base import Connector, ConnectorError, Entry, http_get, normalize_name

WORKBOOK_URL = (
    "https://cma.gov.sa/AboutCMA/ResearchAndReports/opendata/Documents/CMI%20report/excel/"
    "Institutions%20under%20supervision%20of%20CMA.xlsx"
)
PORTAL = "https://cma.gov.sa/AboutCMA/ResearchAndReports/opendata/Pages/default.aspx"

REGULATOR_NAME = "CMA (Saudi Arabia)"

#: Sheet positions (0-based, `Workbook.worksheets` order) as measured 2026-09-24. Sheet *names* are
#: Arabic and not used for lookup; instead `_verify_table_title` checks each sheet's own printed
#: "Table (N):" title before any row is read, so a re-ordered future edition fails loudly here
#: rather than silently reading the wrong table.
SHEET_AUM = 8          # Table 8  — AUM per CMI
SHEET_FUNDS = 14       # Table 14 — number of public/private funds per CMI
SHEET_CUSTODY = 15     # Table 15 — AUM under custodial activity

#: A quarter header carries both an Arabic and an English rendering of "Quarter N ... YYYY", in
#: slightly different punctuation per sheet ("Quarter 4 \n 2017", "Quarter 1-2018", "Quarter 1\n2026
#: "). This matches the English fragment in all of them without depending on exact whitespace.
_QUARTER_RE = re.compile(r"Quarter\s*(\d+)[\s\S]{0,15}?(\d{4})")

#: A sub-column that totals a quarter's public+private figures, as opposed to the "Public"/"Private"
#: columns either side of it (Table 14 only). Matches the English "Total" whole word; the Arabic
#: equivalent (الإجمالي) always appears alongside it in this
#: workbook, so matching the English half is sufficient and avoids an encoding-fragile literal.
_TOTAL_COL_RE = re.compile(r"\bTotal\b", re.I)

_NAME_HEADER_MARKER = "Capital Market Institution"  # present, verbatim, on every sheet we read


def _quarter_key(header: str) -> Optional[tuple[int, int]]:
    """(year, quarter) from a header string, or `None` if it does not look like one at all."""
    m = _QUARTER_RE.search(header or "")
    if not m:
        return None
    return int(m.group(2)), int(m.group(1))


def _quarter_label(key: tuple[int, int]) -> str:
    year, quarter = key
    return f"Q{quarter} {year}"


class CMASaudiXLSXConnector(Connector):
    register = "cma-saudi-xlsx"
    regulator = REGULATOR_NAME
    country = "Saudi Arabia"
    source_name = "CMA \"Institutions under supervision of CMA\" quarterly Excel workbook"
    source_url = PORTAL

    # -- fetching -----------------------------------------------------------

    def fetch(self) -> list[Entry]:
        raw = http_get(WORKBOOK_URL, timeout=90)
        try:
            wb = openpyxl.load_workbook(BytesIO(raw), data_only=True, read_only=True)
        except Exception as e:  # noqa: BLE001 - any parse failure is the same story: not a workbook
            raise ConnectorError(
                f"{WORKBOOK_URL} did not parse as an Excel workbook ({len(raw)} bytes fetched): {e}"
            ) from e

        try:
            ws_aum = wb.worksheets[SHEET_AUM]
            ws_funds = wb.worksheets[SHEET_FUNDS]
            ws_custody = wb.worksheets[SHEET_CUSTODY]
        except IndexError as e:
            raise ConnectorError(
                f"{WORKBOOK_URL} has only {len(wb.worksheets)} sheet(s) — expected at least "
                f"{SHEET_CUSTODY + 1}. The workbook's structure has changed: {e}"
            ) from e

        self._verify_table_title(ws_aum, 8)
        self._verify_table_title(ws_funds, 14)
        self._verify_table_title(ws_custody, 15)

        aum = self._read_value_sheet(ws_aum, "Table 8 (AUM per CMI)")
        funds = self._read_value_sheet(ws_funds, "Table 14 (fund count per CMI)", totals_only=True)
        custody = self._read_value_sheet(ws_custody, "Table 15 (custodial AUM)")

        all_keys = set(aum) | set(funds) | set(custody)
        if not all_keys:
            raise ConnectorError(
                f"{WORKBOOK_URL} parsed but yielded zero firms across all three tables read. A live "
                f"quarterly workbook is never empty — this is a parse failure, not a quiet quarter."
            )

        entries = []
        for key in sorted(all_keys):
            entries.append(self._to_entry(key, aum.get(key), funds.get(key), custody.get(key)))
        return entries

    @staticmethod
    def _verify_table_title(ws, table_number: int) -> None:
        """Confirm the sheet at this position still prints "Table (N):" before trusting its rows.

        Sheet names in this workbook are Arabic and not used for lookup (see module docstring), so
        position is all we have. This is the guard against a future quarterly edition inserting or
        reordering a sheet: it fails loudly here, on a clear message, rather than quietly reading
        (say) the credit-rating-agency sheet as if it were AUM.
        """
        pat = re.compile(rf"Table\s*\(\s*{table_number}\s*\)", re.I)
        for r in range(1, 13):
            for c in range(1, 10):
                v = ws.cell(row=r, column=c).value
                if v and pat.search(str(v)):
                    return
        raise ConnectorError(
            f"Expected sheet at position {table_number} of the CMA workbook to print \"Table "
            f"({table_number}):\" somewhere in its first 12 rows, and it did not (sheet title: "
            f"{ws.title!r}). The workbook's sheet order has probably changed — this connector's "
            f"SHEET_* constants need updating, not a silent read of the wrong table."
        )

    def _read_value_sheet(self, ws, label: str, *, totals_only: bool = False) -> dict[str, dict]:
        """One per-firm sheet -> `{normalized_english_name: {name_en, name_ar, value, quarter}}`.

        ``totals_only`` selects Table 14's shape, where each quarter is three columns (Public,
        Private, Total) rather than one — only the Total sub-column is read.
        """
        header_row, name_en_col = self._find_name_column(ws, label)
        name_ar_col = name_en_col - 1
        cols = self._value_columns(ws, header_row, name_en_col, totals_only=totals_only)
        if not cols:
            raise ConnectorError(
                f"{label}: no parseable quarterly column found in sheet {ws.title!r}. The header "
                f"layout has changed."
            )

        firms: dict[str, dict] = {}
        blank_streak = 0
        r = header_row + 1
        # A generous but finite ceiling — real data never runs anywhere near this many rows in this
        # workbook (largest table read here is ~140 rows); it exists only so a pathological file
        # cannot spin the loop forever.
        while r <= header_row + 2000 and blank_streak < 5:
            name_en = ws.cell(row=r, column=name_en_col).value
            if not name_en or not str(name_en).strip():
                blank_streak += 1
                r += 1
                continue
            blank_streak = 0
            text = str(name_en).strip()
            if text.lower() == "total":
                # The workbook's own aggregate row. It is never a firm, and it is always the last
                # row of real data in these three tables — safe, and correct, to stop here.
                break
            # ⚠ Some names on Tables 8 and 14 carry a trailing "*" — the workbook's own footnote
            # marker (Table 14 defines it: "holders of an investment fund management licence"). It
            # is punctuation about the row, not part of the firm's name, so it is stripped before
            # the name is used anywhere (as `name`, as the dedupe/join key, or in a CRM slug) — but
            # never silently: `footnoted` records that this firm carried the marker, and the
            # `licence_type` sentence built in `_to_entry` says what it means.
            footnoted = text.endswith("*")
            text = text.rstrip("*").strip()
            name_ar_raw = ws.cell(row=r, column=name_ar_col).value
            name_ar = str(name_ar_raw).strip() if name_ar_raw else None
            if name_ar:
                footnoted = footnoted or name_ar.endswith("*")
                name_ar = name_ar.rstrip("*").strip() or None
            value, quarter = self._latest_numeric(ws, r, cols)
            key = normalize_name(text)
            firms[key] = {
                "name_en": text,
                "name_ar": name_ar,
                "value": value,
                "quarter": quarter,
                "footnoted": footnoted,
            }
            r += 1

        if not firms:
            raise ConnectorError(
                f"{label}: sheet {ws.title!r} printed its header but no firm rows were found under "
                f"it. That is not credible for a live quarterly edition of this workbook."
            )
        return firms

    @staticmethod
    def _find_name_column(ws, label: str) -> tuple[int, int]:
        """(header_row, english_name_column). The Arabic name is always the column just before it —
        true on all three sheets read here, checked directly rather than assumed on sight.

        ⚠ The sheet's own title row (e.g. "Table(8): ... Per Capital Market Institution(AUM)...")
        also contains the marker phrase as a fragment of a longer sentence — matched on ``in`` alone
        this finds the title, three rows above the real header, and every subsequent column offset
        is wrong. The real header cell holds the marker and *nothing else*, so an equality check
        (after stripping the optional plural "s") is what actually disambiguates the two.
        """
        for r in range(1, 25):
            for c in range(1, 12):
                v = ws.cell(row=r, column=c).value
                if v and str(v).strip().rstrip("s") == _NAME_HEADER_MARKER:
                    return r, c
        raise ConnectorError(
            f"{label}: could not find the '{_NAME_HEADER_MARKER}' header in sheet {ws.title!r} "
            f"within its first 25 rows / 12 columns. The header layout has changed."
        )

    @staticmethod
    def _value_columns(ws, header_row: int, name_en_col: int, *,
                        totals_only: bool) -> list[tuple[int, tuple[int, int]]]:
        """`[(column, (year, quarter))]`, ascending, for every quarterly value column after the
        name columns. ``totals_only`` restricts Table 14's triples to just the Total sub-column."""
        out = []
        c = name_en_col + 1
        max_col = ws.max_column
        while c <= max_col:
            header = ws.cell(row=header_row, column=c).value
            key = _quarter_key(header or "")
            if key and (not totals_only or _TOTAL_COL_RE.search(str(header))):
                out.append((c, key))
            c += 1
        out.sort(key=lambda t: t[1])
        return out

    @staticmethod
    def _latest_numeric(ws, row: int, cols: list[tuple[int, tuple[int, int]]]
                        ) -> tuple[Optional[float], Optional[str]]:
        """The value and label of the most recent quarter that actually holds a number.

        Walks newest-first. A cell holding the string "NA" (this workbook's own "not licensed at
        the time" marker) or anything else non-numeric is skipped, never coerced to zero or treated
        as the latest figure.
        """
        for col, key in reversed(cols):
            v = ws.cell(row=row, column=col).value
            if isinstance(v, (int, float)):
                return float(v), _quarter_label(key)
        return None, None

    # -- mapping --------------------------------------------------------------

    _TABLE_LABEL = {
        "aum": "AUM per Capital Market Institution (Table 8)",
        "funds": "Number of public/private funds per CMI (Table 14)",
        "custody": "AUM under custodial activity (Table 15)",
    }

    def _to_entry(self, key: str, aum: Optional[dict], funds: Optional[dict],
                 custody: Optional[dict]) -> Entry:
        base_rec = funds or aum or custody
        name = base_rec["name_en"]
        name_ar = base_rec["name_ar"]

        # Segment priority: a firm actually running funds outranks one that merely shows a
        # portfolio-management AUM figure, which outranks a custody-only appearance. See the module
        # docstring for the measured breakdown this produces.
        if funds is not None:
            segment = "fund_manager"
        elif aum is not None:
            segment = "asset_manager"
        else:
            segment = "custodian"

        licence_types = []
        if aum is not None:
            licence_types.append(self._TABLE_LABEL["aum"])
        if funds is not None:
            licence_types.append(self._TABLE_LABEL["funds"])
        if custody is not None:
            licence_types.append(self._TABLE_LABEL["custody"])
        footnoted = any((d or {}).get("footnoted") for d in (aum, funds, custody))
        if footnoted:
            licence_types.append(
                "footnoted by the CMA as a holder of an investment fund management licence"
            )

        third_party = segment in {"asset_manager", "fund_manager"}
        evidence = {}
        if third_party:
            proof_source, proof = ("aum", aum) if aum is not None else ("funds", funds)
            if proof.get("value") is not None:
                evidence["third_party"] = (
                    f"SAR {proof['value']:,.1f}m per {self._TABLE_LABEL[proof_source]}, "
                    f"{proof['quarter']}, per the CMA's own quarterly report"
                )
            else:
                evidence["third_party"] = f"appears in {self._TABLE_LABEL[proof_source]} (no figure for any quarter)"

        return Entry(
            key=key,
            name=name,
            country="Saudi Arabia",
            segment=segment,
            city=None,             # not published by this workbook
            website=None,          # ditto
            phone=None,            # ditto
            licence_date=None,     # ditto — see module docstring
            licence_type="; ".join(licence_types) or None,
            legal_name=name_ar,
            multi_asset=None,      # the workbook states a figure, not what asset classes it covers
            third_party=third_party or None,
            evidence=evidence,
            raw={
                "aum_sar_million": aum["value"] if aum else None,
                "aum_quarter": aum["quarter"] if aum else None,
                "fund_count_total": funds["value"] if funds else None,
                "fund_count_quarter": funds["quarter"] if funds else None,
                "custody_aum_sar_million": custody["value"] if custody else None,
                "custody_aum_quarter": custody["quarter"] if custody else None,
            },
        )

    # -- record creation --------------------------------------------------

    def build_record(self, entry: Entry, snapshot_file: str) -> dict:
        rec = super().build_record(entry, snapshot_file)
        raw = entry.raw or {}

        # `size.aum` is a plain currency string per `crm/SCHEMA.md` — the only money figure this
        # source publishes. Preference: a real AUM figure (Table 8) over a custody figure (Table 15),
        # since custody balances are not the same thing as assets managed and would overstate an
        # asset manager's book if the two were ever conflated.
        if raw.get("aum_sar_million") is not None:
            rec["size"]["aum"] = (
                f"SAR {raw['aum_sar_million']:,.1f}m ({raw['aum_quarter']}, discretionary/fund AUM "
                f"per the CMA's quarterly Institutions-under-supervision report)"
            )
        elif raw.get("custody_aum_sar_million") is not None:
            rec["size"]["aum"] = (
                f"SAR {raw['custody_aum_sar_million']:,.1f}m ({raw['custody_aum_quarter']}, assets "
                f"under custody, not assets managed — per the CMA's quarterly report)"
            )

        extra = []
        if raw.get("fund_count_total") is not None:
            extra.append(
                f"Runs {raw['fund_count_total']:.0f} public/private fund(s) as of "
                f"{raw['fund_count_quarter']} per the CMA's fund-count table."
            )
        if raw.get("aum_sar_million") is not None and entry.segment != "asset_manager":
            extra.append(
                f"Also shows SAR {raw['aum_sar_million']:,.1f}m in discretionary/fund AUM as of "
                f"{raw['aum_quarter']}."
            )
        if extra:
            rec["activities"][0]["summary"] += " " + " ".join(extra)

        return rec

    def tags_for(self, entry: Entry) -> list[str]:
        return super().tags_for(entry) + ["saudi-arabia", "cma-xlsx"]


CONNECTOR = CMASaudiXLSXConnector
