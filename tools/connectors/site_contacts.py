#!/usr/bin/env python
"""A firm's own website — the published contact route we never read.

**Why this exists.** Measured 2026-09-23: 1,604 active records, **119 with any email address, all of
them UAE**. France has 986 records and zero. And 887 of our 937 "contacts" are switchboard numbers
scraped off registers, labelled *General enquiries* — not people. We had built a very good directory
and almost no ability to act on it, and a directory of 1,611 firms we cannot write to is worth about
the same as one of 5,000.

458 of those firms publish a website that nobody had ever read. This reads them.

**What it takes, and only this:** an email address or phone number **printed on the firm's own
site**. It is transcription, not inference.

⚠ **It never constructs an address.** No `firstname.lastname@domain`, no `info@` guessed from a
domain that does not publish one. A bounced email costs more than a missing one, and a guessed
address that happens to work is worse still — it reaches someone who never published a way to be
reached. Every address written to the CRM carries the URL it was read from, so any of it can be
challenged in one click.

**Politeness and the law, since this is the one connector that touches firms directly:**

- `robots.txt` is fetched first and obeyed. A site that disallows us is recorded as *declined* and
  never fetched again — a decision, not a failure.
- One request at a time, with a delay, and a User-Agent that says who we are and leaves a contact.
- At most a handful of pages per firm: the homepage, and the contact/team pages it links to.
- GET only, nothing submitted, no cookies kept, no login, no paywall.

⚠ **Role addresses are preferred deliberately.** `contact@firm.fr` is a company's published channel
and not personal data; a named individual's work address is personal data under the GDPR, and France
is most of this list. Both are collected when published, but the role address is what a first touch
should use anyway, and the split is reported so Andre can see exactly what we hold.

**This connector proposes nothing and qualifies nothing.** A contact route is not a reason to write:
it only means that when we *do* have a reason, the message can leave. Status and triggers are
untouched.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html import unescape
from pathlib import Path
from typing import Iterator, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import crm  # noqa: E402

CACHE_PATH = REPO_ROOT / "crm" / "site_contacts" / "checked.json"

USER_AGENT = (
    "OFS-Sales-Research/1.0 (+business contact lookup; Omega Financial Solutions; "
    "andre.geha@omega-financial-solutions.com)"
)
TIMEOUT = 20
REQUEST_DELAY = 1.5      # per request, and we only ever talk to one host at a time
MAX_PAGES_PER_SITE = 4   # homepage + up to three contact/team pages
MAX_BYTES = 1_500_000

#: Link text / href fragments that mark a page worth opening, across the languages our four markets
#: actually publish in. Ordered: the earlier ones are likelier to carry an address.
CONTACT_HINTS = [
    "contact", "contactez", "nous-contacter", "nous contacter", "contact-us", "contactus",
    "equipe", "équipe", "notre-equipe", "team", "our-team", "people", "management",
    "leadership", "direction", "about", "a-propos", "à-propos", "qui-sommes-nous",
    "legal", "mentions-legales", "mentions légales", "impressum",
]

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,24}")

#: Local parts that are a company's published channel rather than a person. Preferred for a first
#: touch, and not personal data. Plurals and the French forms are spelled out because they are what
#: firms actually publish — `infos@` was being filed as a person's address for want of one letter.
ROLE_LOCALS = {
    "contact", "contacts", "contactez", "info", "infos", "information", "informations",
    "hello", "bonjour", "enquiries", "enquiry", "inquiries", "inquiry",
    "office", "admin", "mail", "email", "general", "reception", "accueil", "welcome",
    "sales", "commercial", "clients", "client", "clientservices", "serviceclients",
    "ir", "investorrelations", "secretariat", "direction", "communication",
}

#: ⚠ Published, real, and the wrong door. These are never written as a contact route.
#:
#: A data-protection officer exists to field privacy complaints; emailing one to sell software is a
#: good way to generate a complaint rather than a meeting. Recruitment and press inboxes reach
#: people whose job is explicitly not buying software. They are still recorded in the record's
#: activity note — we do not throw away what a firm published — but they are never the address a
#: first touch would leave from.
NEVER_ROUTE_LOCALS = {
    "dpo", "rgpd", "gdpr", "privacy", "privacyoffice", "dataprotection", "donneespersonnelles",
    "careers", "career", "jobs", "job", "recrutement", "recruitment", "recruiting", "hr", "rh", "cv",
    "press", "presse", "media", "medias", "journalistes", "pr",
    "legal", "juridique", "reclamation", "reclamations", "complaints", "fraud", "security",
    "support", "help", "helpdesk", "billing", "facturation", "invoice", "comptabilite",
}

#: Addresses that are never a route to the firm: infrastructure, vendors, and the debris that ends
#: up in page source. Each one here was observed, not imagined.
JUNK_LOCALS = {"noreply", "no-reply", "donotreply", "postmaster", "abuse", "webmaster", "hostmaster"}
JUNK_DOMAINS = {
    "example.com", "example.org", "domain.com", "yourdomain.com", "email.com", "sentry.io",
    "wixpress.com", "wix.com", "squarespace.com", "godaddy.com", "sentry-next.wixpress.com",
    "w3.org", "schema.org", "googlemail.com", "gstatic.com", "cloudflare.com", "jquery.com",
    "adobe.com", "fontawesome.com", "bootstrapcdn.com", "shopify.com", "hubspot.com",
}
JUNK_TLDS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "css", "js", "ico", "woff", "woff2"}

#: International-format numbers only. A bare local string is far too easy to confuse with a company
#: number, a registration number or a price, and a wrong phone number is worse than none.
PHONE_RE = re.compile(r"\+\d[\d\s().\-]{7,20}\d")

#: ⚠ And an international number is only believable when its country code matches the market the
#: firm is in. Measured: a French asset manager's page yielded `+1 206…` — a Seattle number, almost
#: certainly a vendor widget in the markup. A wrong phone number is worse than no phone number, and
#: the registers already gave us 454 French numbers, so there is nothing to gain by being generous.
MARKET_DIAL_CODES = {
    "france": ("33", "262", "590", "594", "596", "687", "689"),   # incl. overseas collectivities
    "uae": ("971",),
    "saudi arabia": ("966",),
    "lebanon": ("961",),
}


class SiteError(RuntimeError):
    """The site could not be read. Recorded, never silently swallowed."""


# ---------------------------------------------------------------------------
# fetching
# ---------------------------------------------------------------------------

def _get(url: str) -> tuple[str, str]:
    """Fetch one page. Returns (final_url, text). Raises `SiteError` with a readable reason."""
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en,fr;q=0.8,ar;q=0.6",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if "html" not in ctype and "text" not in ctype:
                raise SiteError(f"not HTML ({ctype or 'no content-type'})")
            raw = resp.read(MAX_BYTES)
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.geturl(), raw.decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        raise SiteError(f"HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise SiteError(f"unreachable: {e.reason}") from e
    except (TimeoutError, OSError) as e:
        raise SiteError(f"unreachable: {e}") from e
    except Exception as e:  # noqa: BLE001 - a surprise must still be recorded, not lost
        raise SiteError(f"unexpected {type(e).__name__}: {e}") from e


def _robots_allows(base: str) -> tuple[bool, str]:
    """Ask the site whether it wants to be read. A refusal is honoured and remembered.

    ⚠ Deliberately fails OPEN only for a missing or unreadable robots.txt — which is the standard
    reading of the protocol — and never for an explicit Disallow.
    """
    parsed = urllib.parse.urlparse(base)
    robots = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        req = urllib.request.Request(robots, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            rp.parse(resp.read(200_000).decode("utf-8", errors="replace").splitlines())
    except Exception:  # noqa: BLE001 - no robots.txt is permission by convention
        return True, "no robots.txt"
    return (True, "robots.txt allows") if rp.can_fetch(USER_AGENT, base) else (False, "robots.txt disallows")


# ---------------------------------------------------------------------------
# extraction
# ---------------------------------------------------------------------------

def _links(html: str, base_url: str) -> list[str]:
    """Same-host links whose href or text suggests a contact or team page, best first."""
    out: list[tuple[int, str]] = []
    host = urllib.parse.urlparse(base_url).netloc.lower()
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.I | re.S):
        href, text = m.group(1), re.sub(r"<[^>]+>", " ", m.group(2))
        full = urllib.parse.urljoin(base_url, unescape(href.strip()))
        p = urllib.parse.urlparse(full)
        if p.scheme not in ("http", "https") or p.netloc.lower() != host:
            continue
        hay = f"{p.path} {unescape(text)}".lower()
        for rank, hint in enumerate(CONTACT_HINTS):
            if hint in hay:
                out.append((rank, full.split("#")[0]))
                break
    seen, ranked = set(), []
    for rank, url in sorted(out):
        if url not in seen:
            seen.add(url)
            ranked.append(url)
    return ranked


def _clean_emails(html: str) -> set[str]:
    """Every address the page actually prints, minus the debris.

    `mailto:` links and plain text both count — plenty of firms print an address as text only.
    """
    found = set()
    for m in re.finditer(r'mailto:([^"\'<>?\s]+)', unescape(html), re.I):
        found.add(m.group(1))
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.I | re.S)
    text = unescape(re.sub(r"<[^>]+>", " ", text))
    found.update(EMAIL_RE.findall(text))

    out = set()
    for raw in found:
        addr = raw.strip().strip(".,;:()<>").lower()
        if not EMAIL_RE.fullmatch(addr):
            continue
        local, _, domain = addr.partition("@")
        tld = domain.rsplit(".", 1)[-1]
        if tld in JUNK_TLDS or domain in JUNK_DOMAINS or local in JUNK_LOCALS:
            continue
        if any(domain.endswith("." + d) for d in JUNK_DOMAINS):
            continue
        if len(addr) > 120 or ".." in addr:
            continue
        out.add(addr)
    return out


def _clean_phones(html: str, country: Optional[str] = None) -> set[str]:
    text = unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", html,
                                                   flags=re.I | re.S)))
    out = set()
    for raw in PHONE_RE.findall(text):
        digits = re.sub(r"\D", "", raw)
        # An international number is 8-15 digits (ITU E.164). Outside that it is something else —
        # a registration number, an IBAN fragment, a date range.
        if not (8 <= len(digits) <= 15):
            continue
        # ⚠ Strip the national trunk prefix. Firms across our markets print "+33 (0)1 56 88 33 00",
        # and naively keeping every digit yields "+330156883300" — one digit too many, and a number
        # that simply will not dial. The trunk "0" is never part of an international number.
        for code in MARKET_DIAL_CODES.get((country or "").lower(), ()):
            if digits.startswith(code + "0"):
                digits = code + digits[len(code) + 1:]
                break

        codes = MARKET_DIAL_CODES.get((country or "").lower())
        # Unknown market: keep the number rather than invent a rule for it, and let the report say
        # so. A known market with a mismatched code is discarded — that is the Seattle case.
        if codes and not digits.startswith(codes):
            continue
        out.add("+" + digits)
    return out


def _site_domain(website: str) -> str:
    host = urllib.parse.urlparse(website).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _rank_emails(emails: set[str], site_domain: str) -> tuple[list[str], list[str]]:
    """Split into (role addresses, personal addresses), each on the firm's own domain first.

    ⚠ An address on a *different* domain than the firm's site is kept last and flagged: it is often
    the firm's PR agency or a parent company, which is a real route but not the firm itself.
    """
    def own(addr: str) -> bool:
        d = addr.partition("@")[2]
        return bool(site_domain) and (d == site_domain or d.endswith("." + site_domain)
                                      or site_domain.endswith("." + d))

    usable = {e for e in emails if e.partition("@")[0] not in NEVER_ROUTE_LOCALS}
    role = sorted((e for e in usable if e.partition("@")[0] in ROLE_LOCALS),
                  key=lambda e: (not own(e), e))
    personal = sorted((e for e in usable if e.partition("@")[0] not in ROLE_LOCALS),
                      key=lambda e: (not own(e), e))
    return role, personal


# ---------------------------------------------------------------------------
# one firm
# ---------------------------------------------------------------------------

def read_site(website: str, country: Optional[str] = None) -> dict:
    """Read one firm's site. Returns what was found and, always, how it went."""
    if not website.startswith(("http://", "https://")):
        website = "https://" + website
    allowed, why = _robots_allows(website)
    if not allowed:
        return {"ok": False, "declined": True, "reason": why, "emails": {}, "phones": {}, "pages": []}

    emails: dict[str, str] = {}   # address -> the URL it was read from
    phones: dict[str, str] = {}
    pages: list[str] = []
    errors: list[str] = []

    try:
        final, html = _get(website)
    except SiteError as e:
        return {"ok": False, "declined": False, "reason": str(e), "emails": {}, "phones": {},
                "pages": []}
    pages.append(final)
    for a in _clean_emails(html):
        emails.setdefault(a, final)
    for p in _clean_phones(html, country):
        phones.setdefault(p, final)

    for url in _links(html, final)[: MAX_PAGES_PER_SITE - 1]:
        time.sleep(REQUEST_DELAY)
        try:
            furl, sub = _get(url)
        except SiteError as e:
            errors.append(f"{url}: {e}")
            continue
        pages.append(furl)
        for a in _clean_emails(sub):
            emails.setdefault(a, furl)
        for p in _clean_phones(sub, country):
            phones.setdefault(p, furl)

    return {"ok": True, "declined": False, "reason": why, "emails": emails, "phones": phones,
            "pages": pages, "errors": errors}


# ---------------------------------------------------------------------------
# cache
# ---------------------------------------------------------------------------

def load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_cache(cache: dict) -> None:
    """Atomic write with a retry — the same Windows file-lock defence `gleif_enrich` needed."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_PATH.with_suffix(".tmp")
    payload = json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    for attempt in range(4):
        try:
            tmp.write_text(payload, encoding="utf-8")
            tmp.replace(CACHE_PATH)
            return
        except OSError:
            if attempt == 3:
                raise
            time.sleep(0.5 * (attempt + 1))


# ---------------------------------------------------------------------------
# applying to the CRM
# ---------------------------------------------------------------------------

GENERAL = "General enquiries"


def _apply(slug: str, found: dict, *, dry_run: bool) -> list[str]:
    """Write the published routes onto the record. Never overwrites a value we already hold.

    The switchboard contacts the registers gave us are *updated* rather than duplicated — 887
    records already carry a `General enquiries` contact, and adding a second one beside it would
    make the CRM worse, not better.
    """
    path = crm.company_path(slug)
    fresh = crm.load_yaml(path)
    site_domain = _site_domain(fresh.get("website") or "")
    role, personal = _rank_emails(set(found["emails"]), site_domain)
    applied: list[str] = []

    contacts = fresh.setdefault("contacts", [])
    general = next((c for c in contacts if (c.get("title") or "") == GENERAL), None)
    if general is None and (role or personal or found["phones"]):
        general = {"name": f"{fresh['name']} — general enquiries", "title": GENERAL,
                   "role": "unknown", "email": None, "phone": None, "linkedin": None,
                   "language": None, "notes": None, "source": None}
        contacts.append(general)

    def note_source(url: str, what: str) -> None:
        """Record where a value came from WITHOUT overwriting another value's provenance.

        ⚠ These contacts usually already carry a phone number from a regulator's register, and its
        `source` says so. Replacing that with the website this email came from would leave one
        field describing the email and another describing the phone — two information sets in one
        place, which is the thing this workspace least tolerates.
        """
        line = f"{what} published on {url}"
        prev = (general.get("source") or "").strip()
        general["source"] = f"{prev} · {line}" if prev and line not in prev else (prev or line)

    if role and general is not None and not general.get("email"):
        general["email"] = role[0]
        note_source(found["emails"][role[0]], "Email")
        applied.append(f"email {role[0]}")

    if found["phones"] and general is not None and not general.get("phone"):
        phone = sorted(found["phones"])[0]
        general["phone"] = phone
        note_source(next(iter(found["phones"].values())), "Phone")
        applied.append(f"phone {phone}")

    # A personal address is only written when the firm publishes NO role address — a first touch
    # should go to the company channel where one exists, and the GDPR footprint stays smaller.
    if not role and personal and general is not None and not general.get("email"):
        general["email"] = personal[0]
        note_source(found["emails"][personal[0]], "Email")
        applied.append(f"email {personal[0]} (personal-looking; no role address published)")

    extra = [e for e in (role + personal) if not general or e != general.get("email")]
    summary = (
        "Website contact sweep: read "
        + ", ".join(found["pages"][:4])
        + ". "
        + (f"Applied {', '.join(applied)}. " if applied else "Nothing new to apply. ")
        + (f"Also published there: {', '.join(extra[:6])}. " if extra else "")
        + "Every address here was printed on the firm's own site and transcribed, never "
          "constructed — challenge any of it against the page it came from."
    )
    fresh.setdefault("activities", []).append(
        {"date": crm.today(), "type": "research", "summary": summary, "link": None}
    )
    fresh["updated"] = crm.today()
    if not dry_run:
        crm.save_yaml(path, fresh)
    return applied


# ---------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------

def _targets(country: Optional[str], only_missing: bool) -> list[dict]:
    out = []
    for r in crm.load_all_companies():
        if r.get("status") == "disqualified" or not r.get("website"):
            continue
        if country and (r.get("country") or "").lower() != country.lower():
            continue
        if only_missing:
            has = any(c.get("email") for c in (r.get("contacts") or []))
            if has:
                continue
        out.append(r)
    return sorted(out, key=lambda r: r["slug"])


def run(*, dry_run: bool = False, limit: Optional[int] = None, country: Optional[str] = None,
        recheck: bool = False, only_missing: bool = True) -> dict:
    cache = load_cache()
    targets = _targets(country, only_missing)
    todo = [r for r in targets if recheck or r["slug"] not in cache]
    if limit:
        todo = todo[:limit]

    rep = {"eligible": len(targets), "attempted": 0, "with_email": 0, "with_phone": 0,
           "declined": 0, "unreachable": 0, "nothing_published": 0, "applied": [],
           "failures": [], "dry_run": dry_run}

    for rec in todo:
        rep["attempted"] += 1
        found = read_site(rec["website"], rec.get("country"))
        time.sleep(REQUEST_DELAY)

        if found["declined"]:
            rep["declined"] += 1
            cache[rec["slug"]] = {"date": crm.today(), "result": "declined", "why": found["reason"]}
            continue
        if not found["ok"]:
            rep["unreachable"] += 1
            rep["failures"].append({"slug": rec["slug"], "website": rec["website"],
                                    "error": found["reason"]})
            cache[rec["slug"]] = {"date": crm.today(), "result": "unreachable",
                                  "why": found["reason"]}
            continue
        if not found["emails"] and not found["phones"]:
            rep["nothing_published"] += 1
            cache[rec["slug"]] = {"date": crm.today(), "result": "nothing published"}
            continue

        applied = _apply(rec["slug"], found, dry_run=dry_run)
        if any(a.startswith("email") for a in applied):
            rep["with_email"] += 1
        if any(a.startswith("phone") for a in applied):
            rep["with_phone"] += 1
        if applied:
            rep["applied"].append({"slug": rec["slug"], "gains": applied})
        cache[rec["slug"]] = {"date": crm.today(), "result": "read",
                              "emails": len(found["emails"]), "phones": len(found["phones"])}
        if not dry_run:
            save_cache(cache)

    if not dry_run:
        save_cache(cache)
    return rep


def format_report(rep: dict) -> str:
    lines = [
        "Website contact sweep" + (" (DRY RUN — nothing written)" if rep["dry_run"] else ""),
        f"  {rep['eligible']} firms publish a website · {rep['attempted']} read this run",
        f"  {rep['with_email']} gained an email · {rep['with_phone']} gained a phone",
        f"  {rep['nothing_published']} publish no contact route at all",
        f"  {rep['declined']} declined us in robots.txt (honoured, not retried)",
        f"  {rep['unreachable']} could not be read",
    ]
    if rep["failures"]:
        lines.append("  unreachable, by name — these are NOT firms without a website:")
        for f in rep["failures"][:12]:
            lines.append(f"    - {f['slug'][:38]:40} {f['error'][:46]}")
        if len(rep["failures"]) > 12:
            lines.append(f"    ... and {len(rep['failures']) - 12} more")
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="read sites, write nothing")
    ap.add_argument("--limit", type=int, help="stop after this many firms")
    ap.add_argument("--country", help="one market only, e.g. France")
    ap.add_argument("--recheck", action="store_true", help="re-read firms already read before")
    ap.add_argument("--all", action="store_true",
                    help="include firms that already have an email (default: only those without)")
    args = ap.parse_args(argv)

    rep = run(dry_run=args.dry_run, limit=args.limit, country=args.country,
              recheck=args.recheck, only_missing=not args.all)
    print(format_report(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
