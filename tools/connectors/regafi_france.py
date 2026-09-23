#!/usr/bin/env python
"""ACPR / REGAFI (France) — authorised credit institutions and investment firms.

This closes the last empty cell in a market we otherwise cover well: **France × bank was zero**,
because the AMF register lists *sociétés de gestion*, not banks. Banks are the ACPR's register.

Source: `acpr.opendatasoft.com`, Opendatasoft Explore v2.1 — the same platform BOAMP runs on, with
a clean public API and no key.

**Two datasets, joined.** Neither alone is enough:
- ``prd-banque-entites`` — who the firm is: name, address, city, LEI, SIREN.
- ``prd-banque-autorisations`` — what it is authorised to do, its sub-category, the date the
  authorisation began, and crucially whether it is still ``ACTIF``.
They join on ``id_referentiel``.

⚠ **The entity list overstates the population badly.** Filtering entities by
``categorie like "Crédit"`` returns **936**, but only **323** hold a *currently active*
credit-institution authorisation — the rest have been withdrawn. Sourcing from the entity list
alone would have put 600 dead banks into the CRM. The authorisation dataset, filtered to ``ACTIF``,
is the real register.

**What we take, and what we leave.** Measured sub-category counts of the 323:

| Sub-category | Count | Taken? |
|---|---|---|
| Banque | 154 | ✅ `bank` |
| Banque mutualiste ou coopérative | 76 | ✅ `bank` |
| Établissement de crédit et d'investissement | 5 | ✅ `bank` |
| Établissement de crédit spécialisé | 69 | ❌ specialised lender, not our segment |
| Caisse de crédit municipal | 17 | ❌ municipal social lending |

Plus **99** active *Entreprise d'Investissement* → `broker` (MiFID investment firms; a few are
asset managers, which enrichment can correct — the register does not say which).

``Société de financement`` (137) is deliberately excluded: consumer and equipment finance, not
portfolio management.
"""

from __future__ import annotations

import json
import time
import urllib.parse
from typing import Any, Iterator, Optional

try:
    from .base import Connector, ConnectorError, Entry, http_get
except ImportError:  # run directly, not as a package
    from base import Connector, ConnectorError, Entry, http_get

BASE = "https://acpr.opendatasoft.com/api/explore/v2.1/catalog/datasets"
PORTAL = "https://www.regafi.fr/"
PAGE = 100
REQUEST_DELAY = 0.25

#: Sub-categories of an active credit-institution authorisation that are genuinely banks to us.
BANK_SUBCATEGORIES = {
    "Banque",
    "Banque mutualiste ou coopérative",
    "Établissement de crédit et d'investissement",
}

#: Categories we read at all, mapped to the segment their sub-category implies.
CREDIT = "Établissement de Crédit"
INVESTMENT = "Entreprise d'Investissement"

#: Where a firm must be domiciled to be French for our purposes. The register also carries
#: Monégasque banks under ACPR supervision — a separate state, and not our territory.
FRENCH_TERRITORY = {
    "FRANCE",
    "POLYNESIE FRANCAISE",
    "NOUVELLE-CALEDONIE",
    "WALLIS ET FUTUNA",
    "SAINT-PIERRE-ET-MIQUELON",
}


class REGAFIFranceConnector(Connector):
    register = "regafi-france"
    regulator = "ACPR (France)"
    country = "France"
    source_name = "ACPR REGAFI register of authorised credit institutions and investment firms"
    source_url = PORTAL

    def __init__(self) -> None:
        self._entities: dict[str, dict] = {}

    # -- fetching ---------------------------------------------------------

    def _records(self, dataset: str, where: str) -> Iterator[dict]:
        """Page through a dataset. Opendatasoft caps `limit` at 100."""
        offset = 0
        while True:
            qs = urllib.parse.urlencode({"where": where, "limit": PAGE, "offset": offset})
            raw = http_get(f"{BASE}/{dataset}/records?{qs}", accept="application/json", timeout=60)
            try:
                page = json.loads(raw)
            except json.JSONDecodeError as e:
                raise ConnectorError(f"REGAFI {dataset} returned unparseable JSON: {e}") from e
            results = page.get("results") or []
            if not results:
                return
            yield from results
            offset += len(results)
            total = page.get("total_count") or 0
            if offset >= total:
                return
            # Opendatasoft refuses offsets beyond 10,000; our filtered sets are far smaller, but
            # fail loudly rather than silently truncating if that ever changes.
            if offset >= 10000:
                raise ConnectorError(
                    f"REGAFI {dataset} exceeded the 10,000-row offset ceiling with {total} matches. "
                    f"The query needs slicing before this can be trusted."
                )
            time.sleep(REQUEST_DELAY)

    def _load_entities(self, ids: list[str]) -> None:
        """Entity details for exactly the ids we need, fetched by id rather than by category.

        ⚠ An earlier version pre-filtered entities with ``categorie like "Crédit"`` and silently
        lost 27 authorised firms whose entity row is categorised differently. Fetching by the ids
        the authorisation set actually produced cannot miss one — and if an id has no entity row,
        that is now visible rather than absorbed.
        """
        CHUNK = 60
        for i in range(0, len(ids), CHUNK):
            batch = ids[i : i + CHUNK]
            quoted = ",".join(f'"{x}"' for x in batch)
            for r in self._records("prd-banque-entites", f"id_referentiel in ({quoted})"):
                key = str(r.get("id_referentiel") or "")
                if key:
                    self._entities.setdefault(key, r)
        if not self._entities:
            raise ConnectorError(
                "REGAFI returned no entity rows for any authorised firm. A live register is never "
                "empty — treating this as a fetch failure, not a quiet day."
            )

    def fetch(self) -> list[Entry]:
        where = (
            f'(categorie="{CREDIT}" or categorie="{INVESTMENT}") and situation="ACTIF"'
        )
        auths = list(self._records("prd-banque-autorisations", where))
        if not auths:
            raise ConnectorError(
                "REGAFI returned no ACTIVE authorisations. That is not credible for France — "
                "treating it as a broken query rather than an empty register."
            )

        # A firm can hold several authorisations; keep the earliest start date, which is when it
        # became authorised at all.
        best: dict[str, dict] = {}
        for a in auths:
            key = str(a.get("id_referentiel") or "")
            if not key:
                continue
            prev = best.get(key)
            if prev is None or str(a.get("date_debut") or "9999") < str(prev.get("date_debut") or "9999"):
                best[key] = a

        self._load_entities(sorted(best))
        missing = [k for k in best if k not in self._entities]
        if missing:
            # Not fatal — but it must not be silent, because it is exactly how 27 firms went
            # missing before anyone noticed.
            print(
                f"  note: {len(missing)} authorised firm(s) have no REGAFI entity row and were skipped"
            )

        entries = []
        for key, a in best.items():
            e = self._to_entry(key, a)
            if e is not None:
                entries.append(e)
        if not entries:
            raise ConnectorError(
                f"REGAFI matched {len(best)} authorisations but none survived mapping. That is a "
                f"schema change, not an empty register."
            )
        return entries

    # -- mapping ----------------------------------------------------------

    def _to_entry(self, key: str, auth: dict) -> Optional[Entry]:
        ent = self._entities.get(key)
        if not ent:
            return None
        name = (ent.get("denomination") or "").strip()
        if not name:
            return None

        # ⚠ "France" includes its overseas collectivities — a bank in Nouméa is a French bank,
        # ACPR-authorised. Monaco is NOT: it is a separate sovereign state and outside our
        # territory, and 13 of these firms are Monégasque.
        pays = (ent.get("pays") or "").strip().upper()
        if pays and pays not in FRENCH_TERRITORY:
            return None

        category = (auth.get("categorie") or "").strip()
        sub = (auth.get("sous_categorie") or "").strip()
        segment = self._segment(category, sub)
        if segment is None:
            return None

        lei = (ent.get("lei") or "").strip() or None
        return Entry(
            key=key,
            name=name,
            country="France",
            segment=segment,
            city=(ent.get("ville") or "").strip().title() or None,
            website=None,                       # REGAFI publishes none
            phone=None,                         # nor a phone number
            licence_date=(auth.get("date_debut") or "").strip() or None,
            licence_type=f"{category}" + (f" — {sub}" if sub else ""),
            legal_name=None,
            # The register states what a firm is authorised to DO, not what it manages or for whom,
            # so neither fit flag is asserted. Awarding them would be inventing evidence.
            multi_asset=None,
            third_party=None,
            evidence={},
            raw={
                "lei": lei,
                "siren": (ent.get("siren") or "").strip() or None,
                "forme_juridique": (ent.get("forme_juridique") or "").strip() or None,
                "adresse": (ent.get("adresse") or "").strip() or None,
                "code_postal": (ent.get("code_postal") or "").strip() or None,
                "sous_categorie": sub,
                "nature_autorisation": (auth.get("nature_autorisation") or "").strip() or None,
            },
        )

    @staticmethod
    def _segment(category: str, sub: str) -> Optional[str]:
        if category == CREDIT:
            return "bank" if sub in BANK_SUBCATEGORIES else None
        if category == INVESTMENT:
            # MiFID investment firms. Some manage portfolios, some only broker; REGAFI does not
            # distinguish, so the conservative reading is `broker` and enrichment can promote it.
            return "broker"
        return None

    def tags_for(self, entry: Entry) -> list[str]:
        tags = super().tags_for(entry)
        sub = (entry.raw or {}).get("sous_categorie")
        if sub:
            tags.append(sub.lower().replace(" ", "-")[:40])
        return tags + ["france", "acpr"]


CONNECTOR = REGAFIFranceConnector
