#!/usr/bin/env python
"""AMF (France) — licensed sociétés de gestion de portefeuille.

Source: the AMF's own dataset on data.gouv.fr, "Liste des sociétés de gestion de portefeuille (SGP)
agréées par l'AMF". Updated daily by the regulator, published as CSV, and it carries far more than a
list of names: licence date, authorised activities, authorised instrument classes, and — for many
firms — a website and a switchboard number **published by the regulator itself**.

That last point matters. Those contact details are not guessed or pattern-inferred; they are what
the AMF publishes. They are the one legitimate source of a contact route we have.

⚠ The download URL is **timestamped and changes every day**, so it is resolved through the
data.gouv.fr API on each run rather than hardcoded.
"""

from __future__ import annotations

import csv
import io
import json
from collections import defaultdict
from typing import Optional

try:
    from .base import Connector, ConnectorError, Entry, http_get
except ImportError:  # run directly, not as a package
    from base import Connector, ConnectorError, Entry, http_get

DATASET_ID = "651427eaf6eab90fa3db2da3"
DATASET_API = f"https://www.data.gouv.fr/api/1/datasets/{DATASET_ID}/"
DATASET_PAGE = (
    "https://www.data.gouv.fr/datasets/"
    "liste-des-societes-de-gestion-de-portefeuille-sgp-agreees-par-lamf"
)

# Activities that prove the firm manages money for third parties.
_THIRD_PARTY_MARKERS = (
    "gestion de portefeuille pour le compte de tiers",
    "gestion de fia",
    "opcvm",
)

# Instrument classes, as the AMF labels them. A firm authorised across several of these is
# genuinely multi-asset — this is the register stating it, not us inferring it.
_MIN_INSTRUMENT_CLASSES_FOR_MULTI_ASSET = 3


class AMFFranceConnector(Connector):
    register = "amf-france"
    regulator = "AMF"
    country = "France"
    source_name = "AMF register of licensed sociétés de gestion de portefeuille (via data.gouv.fr)"
    source_url = DATASET_PAGE

    def _resolve_csv_url(self) -> tuple[str, Optional[str]]:
        """Ask the dataset API for today's CSV resource. The URL is timestamped and moves daily."""
        raw = http_get(DATASET_API, accept="application/json")
        try:
            meta = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ConnectorError(f"data.gouv.fr dataset API returned unparseable JSON: {e}") from e

        resources = meta.get("resources") or []
        for r in resources:
            if (r.get("format") or "").lower() == "csv" and r.get("url"):
                return r["url"], r.get("last_modified")
        raise ConnectorError(
            f"No CSV resource on the AMF dataset ({DATASET_PAGE}). The regulator may have changed "
            f"the publication format — this needs a human look, not a retry."
        )

    def fetch(self) -> list[Entry]:
        csv_url, last_modified = self._resolve_csv_url()
        raw = http_get(csv_url)

        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("cp1252", errors="replace")

        reader = csv.DictReader(io.StringIO(text), delimiter=";")
        if not reader.fieldnames or "no_amf" not in reader.fieldnames:
            raise ConnectorError(
                f"AMF CSV did not have the expected columns (got {reader.fieldnames!r}). "
                f"The schema has changed — do not trust a diff until this is checked by hand."
            )

        rows = list(reader)
        if not rows:
            raise ConnectorError(f"AMF CSV at {csv_url} parsed to zero rows.")

        # The CSV is one row per (firm x activity x instrument class). Fold it back to one per firm.
        by_firm: dict[str, dict] = {}
        activities: dict[str, set[str]] = defaultdict(set)
        instruments: dict[str, set[str]] = defaultdict(set)

        for r in rows:
            key = (r.get("no_amf") or "").strip()
            if not key:
                continue
            by_firm.setdefault(key, r)
            kind = (r.get("libelle_type_activite") or "").strip()
            label = (r.get("libelle_activite") or "").strip()
            if not label:
                continue
            if kind == "Activité":
                activities[key].add(label)
            elif kind == "Instrument financier":
                instruments[key].add(label)

        entries = []
        for key, r in by_firm.items():
            acts = activities.get(key, set())
            insts = instruments.get(key, set())
            entries.append(self._to_entry(key, r, acts, insts, last_modified))
        return entries

    # -- mapping ----------------------------------------------------------

    def _to_entry(self, key: str, r: dict, acts: set[str], insts: set[str],
                  last_modified: Optional[str]) -> Entry:
        name = (r.get("entite_nom") or "").strip()

        acts_l = " | ".join(sorted(acts)).lower()
        third_party = any(m in acts_l for m in _THIRD_PARTY_MARKERS)
        multi_asset = len(insts) >= _MIN_INSTRUMENT_CLASSES_FOR_MULTI_ASSET

        evidence = {}
        if third_party:
            evidence["third_party"] = (
                "AMF-authorised for " + "; ".join(sorted(acts)[:3])
            )
        if multi_asset:
            evidence["multi_asset"] = (
                f"AMF-authorised across {len(insts)} instrument classes including "
                + "; ".join(sorted(insts)[:3])
            )

        return Entry(
            key=key,
            name=name,
            country="France",
            segment=self._segment(acts),
            city=None,                       # the dataset does not publish an address
            website=self._website(r.get("site_internet")),
            phone=self._phone(r.get("telephone")),
            licence_date=(r.get("date_debut_autorisation") or "").strip() or None,
            licence_type="; ".join(sorted(acts)) or None,
            legal_name=None,
            multi_asset=multi_asset or None,
            third_party=third_party or None,
            evidence=evidence,
            raw={
                "forme_juridique": (r.get("forme_juridique") or "").strip() or None,
                "siret": (r.get("siret") or "").strip() or None,
                "lei": (r.get("lei") or "").strip() or None,
                "activites": sorted(acts),
                "instruments": sorted(insts),
                "dataset_last_modified": last_modified,
            },
        )

    @staticmethod
    def _segment(acts: set[str]) -> str:
        """Mandates make it an asset manager; funds alone make it a fund manager.

        A firm doing both is recorded as ``asset_manager`` — the mandate business is the broader
        multi-client operation, and the fund activity is captured in ``licence_type`` either way.
        """
        joined = " | ".join(acts).lower()
        has_mandates = "gestion des mandats" in joined or "compte de tiers" in joined
        has_funds = "gestion de fia" in joined or "opcvm" in joined
        if has_mandates:
            return "asset_manager"
        if has_funds:
            return "fund_manager"
        return "asset_manager"

    @staticmethod
    def _website(value: Optional[str]) -> Optional[str]:
        v = (value or "").strip()
        if not v:
            return None
        if not v.lower().startswith(("http://", "https://")):
            v = "https://" + v.lstrip("/")
        return v

    @staticmethod
    def _phone(value: Optional[str]) -> Optional[str]:
        """Normalise the AMF's phone formatting without changing the digits.

        The dataset contains entries like ``+033 1 85 73 62 56`` — a ``+`` in front of a French
        trunk prefix, which is not a valid E.164 number. We correct that one known malformation and
        otherwise leave the value exactly as published. We never fabricate a missing number.
        """
        v = (value or "").strip()
        if not v:
            return None
        if v.startswith("+0"):
            v = "+33 " + v[len("+033"):].strip() if v.startswith("+033") else v[1:]
        return " ".join(v.split())


CONNECTOR = AMFFranceConnector
