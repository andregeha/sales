#!/usr/bin/env python3
"""
crm.py — the CRM for the OFS sales workspace.

This repo IS the system of record for new-business demand generation on Gaia. There is no
external CRM: every company we are pursuing lives as one hand-readable YAML file under
`crm/companies/<slug>.yaml`, every tender/RFP under `crm/rfps/<slug>.yaml`. See `crm/SCHEMA.md`
for the full record shape and a worked example of each.

Who this is for: Andre Geha (the only human), and the research/outreach agents that source leads,
log activity and maintain the pipeline on his behalf. Every subcommand is designed to be run
non-interactively and to produce output that is easy for both a human and another script to read
(`--format json` almost everywhere that lists things).

This tool only ever reads and writes files inside this repo. It never touches a client system,
never sends anything, and never invents a fact — a missing value is `null`, not a guess.

Run `crm.py --help` or `crm.py <subcommand> --help` for usage.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "error: PyYAML is required (`pip install pyyaml`). It is near-universal and this tool "
        "does not attempt to reimplement a YAML parser.\n"
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
CRM_DIR = REPO_ROOT / "crm"
COMPANIES_DIR = CRM_DIR / "companies"
RFPS_DIR = CRM_DIR / "rfps"

SEGMENTS = [
    "family_office", "mfo", "bank", "asset_manager", "fund_manager",
    "broker", "insurer", "custodian",
]
COMPANY_STATUSES = [
    "new", "researching", "qualified", "contacted", "engaged", "opportunity",
    "won", "lost", "disqualified", "nurture",
]
COMPANY_STAGES = [
    "identified", "engaged", "qualified", "solution_agreed", "proposed",
    "negotiating", "won", "lost", "parked",
]
CONTACT_ROLES = ["economic_buyer", "champion", "technical", "compliance", "blocker", "unknown"]
CONTACT_LANGUAGES = ["en", "fr", "ar"]
ACTIVITY_TYPES = [
    "research", "email_drafted", "email_sent", "linkedin", "call", "meeting",
    "demo", "rfp", "note",
]
RFP_STATUSES = ["spotted", "assessing", "bidding", "submitted", "won", "lost", "skipped"]
RFP_OUTCOMES = ["bid", "no_bid", "pending"]

DEFAULT_OWNER = "Andre Geha"
STALLED_STATUSES = {"contacted", "engaged"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def today() -> str:
    return date.today().isoformat()


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def is_valid_date(s: Any) -> bool:
    if not isinstance(s, str) or not DATE_RE.match(s):
        return False
    try:
        parse_date(s)
        return True
    except ValueError:
        return False


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "record"


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def dump_yaml(data: dict) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)


def save_yaml(path: Path, data: dict) -> None:
    path.write_text(dump_yaml(data), encoding="utf-8")


def company_path(slug: str) -> Path:
    return COMPANIES_DIR / f"{slug}.yaml"


def rfp_path(slug: str) -> Path:
    return RFPS_DIR / f"{slug}.yaml"


def all_company_files() -> list[Path]:
    return sorted(COMPANIES_DIR.glob("*.yaml"))


def all_rfp_files() -> list[Path]:
    return sorted(RFPS_DIR.glob("*.yaml"))


def load_all_companies() -> list[dict]:
    out = []
    for p in all_company_files():
        try:
            d = load_yaml(p)
        except yaml.YAMLError as e:
            sys.stderr.write(f"warning: could not parse {p}: {e}\n")
            continue
        d["_path"] = str(p.relative_to(REPO_ROOT))
        out.append(d)
    return out


def load_all_rfps() -> list[dict]:
    out = []
    for p in all_rfp_files():
        try:
            d = load_yaml(p)
        except yaml.YAMLError as e:
            sys.stderr.write(f"warning: could not parse {p}: {e}\n")
            continue
        d["_path"] = str(p.relative_to(REPO_ROOT))
        out.append(d)
    return out


def set_dotted(d: dict, dotted_key: str, value: Any) -> None:
    """Set d['a']['b'] from dotted_key='a.b', creating dicts as needed."""
    parts = dotted_key.split(".")
    cur = d
    for part in parts[:-1]:
        if part not in cur or not isinstance(cur[part], dict):
            cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value


def coerce_value(raw: str) -> Any:
    """Turn a --set VALUE string into null / bool / int / str, so the CLI stays flag-only."""
    if raw is None:
        return None
    low = raw.strip().lower()
    if low in ("null", "none", "~"):
        return None
    if low == "true":
        return True
    if low == "false":
        return False
    if re.match(r"^-?\d+$", raw):
        return int(raw)
    return raw


def print_out(text: str) -> None:
    sys.stdout.write(text if text.endswith("\n") else text + "\n")


# ---------------------------------------------------------------------------
# Record builders
# ---------------------------------------------------------------------------

def new_company_record(args: argparse.Namespace) -> dict:
    name = args.name
    slug = args.slug or slugify(name)
    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    d = today()
    return {
        "slug": slug,
        "name": name,
        "legal_name": args.legal_name,
        "country": args.country,
        "city": args.city,
        "segment": args.segment,
        "regulator": args.regulator,
        "website": args.website,
        "linkedin": args.linkedin,
        "size": {
            "aum": args.aum,
            "employees": args.employees,
            "portfolios": args.portfolios,
        },
        "description": args.description,
        "source": {
            "channel": args.source_channel,
            "detail": args.source_detail,
            "date": args.source_date or d,
        },
        "status": args.status,
        "stage": args.stage,
        "owner": args.owner,
        "tags": tags,
        "created": d,
        "updated": d,
        "contacts": [],
        "fit": {"score": args.score, "reasoning": args.score_reasoning, "disqualified_reason": None},
        "activities": [],
        "next_action": None,
    }


def new_rfp_record(args: argparse.Namespace) -> dict:
    slug = args.slug or slugify(f"{args.issuer}-{args.title}")
    d = today()
    return {
        "slug": slug,
        "title": args.title,
        "issuer": args.issuer,
        "country": args.country,
        "segment": args.segment,
        "source_url": args.source_url,
        "published_date": args.published_date,
        "deadline": args.deadline,
        "status": args.status,
        "fit_assessment": args.fit_assessment,
        "decision": {"outcome": args.outcome, "reason": args.reason},
        "documents": [],
        "owner": args.owner,
        "created": d,
        "updated": d,
    }


# ---------------------------------------------------------------------------
# Subcommand: add
# ---------------------------------------------------------------------------

def cmd_add(args: argparse.Namespace) -> int:
    rec = new_company_record(args)
    path = company_path(rec["slug"])
    if path.exists():
        sys.stderr.write(f"error: {path} already exists — refusing to clobber. Use `update`.\n")
        return 1
    if rec["segment"] and rec["segment"] not in SEGMENTS:
        sys.stderr.write(f"error: invalid --segment {rec['segment']!r}. Allowed: {SEGMENTS}\n")
        return 1
    if rec["status"] not in COMPANY_STATUSES:
        sys.stderr.write(f"error: invalid --status {rec['status']!r}. Allowed: {COMPANY_STATUSES}\n")
        return 1
    if rec["stage"] not in COMPANY_STAGES:
        sys.stderr.write(f"error: invalid --stage {rec['stage']!r}. Allowed: {COMPANY_STAGES}\n")
        return 1
    COMPANIES_DIR.mkdir(parents=True, exist_ok=True)
    save_yaml(path, rec)
    print_out(f"created {path.relative_to(REPO_ROOT)}  (slug={rec['slug']})")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: show
# ---------------------------------------------------------------------------

def cmd_show(args: argparse.Namespace) -> int:
    path = company_path(args.slug)
    if not path.exists():
        sys.stderr.write(f"error: no company record for slug {args.slug!r}\n")
        return 1
    rec = load_yaml(path)
    if args.format == "yaml":
        print_out(dump_yaml(rec))
        return 0
    if args.format == "json":
        print_out(json.dumps(rec, indent=2))
        return 0
    # pretty
    lines = []
    lines.append(f"{rec.get('name')}  [{rec.get('slug')}]")
    lines.append(f"  {rec.get('segment')} · {rec.get('city') or '?'}, {rec.get('country') or '?'} "
                 f"· regulator: {rec.get('regulator') or 'unknown'}")
    lines.append(f"  status={rec.get('status')}  stage={rec.get('stage')}  owner={rec.get('owner')}")
    tags = rec.get("tags") or []
    if tags:
        lines.append(f"  tags: {', '.join(tags)}")
    size = rec.get("size") or {}
    lines.append(f"  size: aum={size.get('aum')}  employees={size.get('employees')}  "
                 f"portfolios={size.get('portfolios')}")
    if rec.get("website"):
        lines.append(f"  website: {rec['website']}")
    if rec.get("linkedin"):
        lines.append(f"  linkedin: {rec['linkedin']}")
    if rec.get("description"):
        lines.append(f"  description: {rec['description'].strip()}")
    src = rec.get("source") or {}
    lines.append(f"  source: {src.get('channel')} — {src.get('detail')} ({src.get('date')})")
    fit = rec.get("fit") or {}
    lines.append(f"  fit: score={fit.get('score')}  reasoning={fit.get('reasoning')}")
    if fit.get("disqualified_reason"):
        lines.append(f"  disqualified_reason: {fit['disqualified_reason']}")
    lines.append("")
    contacts = rec.get("contacts") or []
    lines.append(f"  Contacts ({len(contacts)}):")
    for c in contacts:
        lines.append(f"    - {c.get('name')} — {c.get('title') or '?'} [{c.get('role')}] "
                     f"· {c.get('email') or 'no email'} · {c.get('phone') or 'no phone'} "
                     f"· lang={c.get('language')}")
        if c.get("notes"):
            lines.append(f"      notes: {c['notes']}")
    lines.append("")
    acts = rec.get("activities") or []
    lines.append(f"  Activities ({len(acts)}):")
    for a in acts:
        link = f" -> {a.get('link')}" if a.get("link") else ""
        lines.append(f"    - {a.get('date')} [{a.get('type')}] {a.get('summary')}{link}")
    lines.append("")
    na = rec.get("next_action")
    if na:
        lines.append(f"  Next action: {na.get('who')} — {na.get('what')} — due {na.get('due')}")
    else:
        lines.append("  Next action: none")
    lines.append(f"  created={rec.get('created')}  updated={rec.get('updated')}")
    print_out("\n".join(lines))
    return 0


# ---------------------------------------------------------------------------
# Subcommand: list
# ---------------------------------------------------------------------------

def _csv_set(raw: Optional[str]) -> Optional[set[str]]:
    """--status a,b,c -> {'a','b','c'}. None if the flag was not given."""
    if not raw:
        return None
    return {v.strip() for v in raw.split(",") if v.strip()}


def cmd_list(args: argparse.Namespace) -> int:
    statuses = _csv_set(args.status)
    if statuses:
        bad = statuses - set(COMPANY_STATUSES)
        if bad:
            sys.stderr.write(f"error: invalid --status value(s) {sorted(bad)}. Allowed: {COMPANY_STATUSES}\n")
            return 1
    segments = _csv_set(args.segment)
    if segments:
        bad = segments - set(SEGMENTS)
        if bad:
            sys.stderr.write(f"error: invalid --segment value(s) {sorted(bad)}. Allowed: {SEGMENTS}\n")
            return 1
    stages = _csv_set(args.stage)
    if stages:
        bad = stages - set(COMPANY_STAGES)
        if bad:
            sys.stderr.write(f"error: invalid --stage value(s) {sorted(bad)}. Allowed: {COMPANY_STAGES}\n")
            return 1
    countries = _csv_set(args.country)
    tags = _csv_set(args.tag)

    recs = load_all_companies()

    def keep(r: dict) -> bool:
        if countries and (r.get("country") or "").lower() not in {c.lower() for c in countries}:
            return False
        if segments and r.get("segment") not in segments:
            return False
        if statuses and r.get("status") not in statuses:
            return False
        if stages and r.get("stage") not in stages:
            return False
        if args.owner and (r.get("owner") or "").lower() != args.owner.lower():
            return False
        if tags and not (tags & set(r.get("tags") or [])):
            return False
        if args.min_score is not None:
            score = ((r.get("fit") or {}).get("score"))
            if score is None or score < args.min_score:
                return False
        return True

    recs = [r for r in recs if keep(r)]

    sort_key = args.sort or "name"

    def sk(r: dict):
        if sort_key == "score":
            return -((r.get("fit") or {}).get("score") or -1)
        if sort_key == "updated":
            return r.get("updated") or ""
        if sort_key == "next_due":
            na = r.get("next_action")
            return na.get("due") if na else "9999-99-99"
        return (r.get(sort_key) or "")

    recs.sort(key=sk)

    rows = []
    for r in recs:
        na = r.get("next_action")
        rows.append({
            "slug": r.get("slug"),
            "name": r.get("name"),
            "country": r.get("country"),
            "segment": r.get("segment"),
            "status": r.get("status"),
            "stage": r.get("stage"),
            "owner": r.get("owner"),
            "score": (r.get("fit") or {}).get("score"),
            "tags": ",".join(r.get("tags") or []),
            "next_action_due": na.get("due") if na else "",
        })

    return _emit_rows(rows, args.format,
                       columns=["slug", "name", "country", "segment", "status", "stage",
                                "owner", "score", "next_action_due", "tags"])


def _emit_rows(rows: list[dict], fmt: str, columns: list[str]) -> int:
    if fmt == "json":
        print_out(json.dumps(rows, indent=2))
        return 0
    if fmt == "csv":
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=columns)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in columns})
        print_out(buf.getvalue())
        return 0
    # table
    if not rows:
        print_out("(no matching records)")
        return 0
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}
    header = "  ".join(c.upper().ljust(widths[c]) for c in columns)
    print_out(header)
    print_out("  ".join("-" * widths[c] for c in columns))
    for r in rows:
        print_out("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns))
    return 0


# ---------------------------------------------------------------------------
# Subcommand: update
# ---------------------------------------------------------------------------

SCALAR_ENUM_CHECKS = {
    "segment": SEGMENTS,
    "status": COMPANY_STATUSES,
    "stage": COMPANY_STAGES,
}


def cmd_update(args: argparse.Namespace) -> int:
    path = company_path(args.slug)
    if not path.exists():
        sys.stderr.write(f"error: no company record for slug {args.slug!r}\n")
        return 1
    rec = load_yaml(path)

    if args.status:
        if args.status not in COMPANY_STATUSES:
            sys.stderr.write(f"error: invalid --status {args.status!r}. Allowed: {COMPANY_STATUSES}\n")
            return 1
        rec["status"] = args.status
    if args.stage:
        if args.stage not in COMPANY_STAGES:
            sys.stderr.write(f"error: invalid --stage {args.stage!r}. Allowed: {COMPANY_STAGES}\n")
            return 1
        rec["stage"] = args.stage
    if args.owner:
        rec["owner"] = args.owner
    if args.add_tag:
        tags = rec.setdefault("tags", [])
        for t in args.add_tag:
            if t not in tags:
                tags.append(t)
    if args.remove_tag:
        tags = rec.setdefault("tags", [])
        rec["tags"] = [t for t in tags if t not in args.remove_tag]
    if args.score is not None:
        rec.setdefault("fit", {})["score"] = args.score
    if args.score_reasoning:
        rec.setdefault("fit", {})["reasoning"] = args.score_reasoning
    if args.disqualified_reason:
        rec.setdefault("fit", {})["disqualified_reason"] = args.disqualified_reason
    if args.next_who or args.next_what or args.next_due:
        if not (args.next_who and args.next_what and args.next_due):
            sys.stderr.write(
                "error: next_action needs all three of --next-who --next-what --next-due "
                "(one person, one verb, one date) — or use --clear-next-action.\n"
            )
            return 1
        rec["next_action"] = {"who": args.next_who, "what": args.next_what, "due": args.next_due}
    if args.clear_next_action:
        rec["next_action"] = None
    for kv in args.set or []:
        if "=" not in kv:
            sys.stderr.write(f"error: --set expects KEY=VALUE, got {kv!r}\n")
            return 1
        key, _, raw = kv.partition("=")
        value = coerce_value(raw)
        top = key.split(".")[0]
        if top in SCALAR_ENUM_CHECKS and value not in SCALAR_ENUM_CHECKS[top] and value is not None:
            sys.stderr.write(f"error: invalid {top}={value!r}. Allowed: {SCALAR_ENUM_CHECKS[top]}\n")
            return 1
        set_dotted(rec, key, value)

    rec["updated"] = today()
    save_yaml(path, rec)
    print_out(f"updated {path.relative_to(REPO_ROOT)}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: log (activity)
# ---------------------------------------------------------------------------

def cmd_log(args: argparse.Namespace) -> int:
    path = company_path(args.slug)
    if not path.exists():
        sys.stderr.write(f"error: no company record for slug {args.slug!r}\n")
        return 1
    if args.type not in ACTIVITY_TYPES:
        sys.stderr.write(f"error: invalid --type {args.type!r}. Allowed: {ACTIVITY_TYPES}\n")
        return 1
    rec = load_yaml(path)
    entry = {
        "date": args.date or today(),
        "type": args.type,
        "summary": args.summary,
        "link": args.link,
    }
    rec.setdefault("activities", []).append(entry)
    rec["updated"] = today()
    save_yaml(path, rec)
    print_out(f"logged activity on {args.slug}: [{entry['type']}] {entry['summary']}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: contact
# ---------------------------------------------------------------------------

def cmd_contact(args: argparse.Namespace) -> int:
    path = company_path(args.slug)
    if not path.exists():
        sys.stderr.write(f"error: no company record for slug {args.slug!r}\n")
        return 1
    if args.role and args.role not in CONTACT_ROLES:
        sys.stderr.write(f"error: invalid --role {args.role!r}. Allowed: {CONTACT_ROLES}\n")
        return 1
    if args.language and args.language not in CONTACT_LANGUAGES:
        sys.stderr.write(f"error: invalid --language {args.language!r}. Allowed: {CONTACT_LANGUAGES}\n")
        return 1
    rec = load_yaml(path)
    contacts = rec.setdefault("contacts", [])
    existing = next((c for c in contacts if c.get("name", "").lower() == args.name.lower()), None)
    if existing is None:
        entry = {
            "name": args.name,
            "title": args.title,
            "role": args.role or "unknown",
            "email": args.email,
            "phone": args.phone,
            "linkedin": args.linkedin,
            "language": args.language or "en",
            "notes": args.notes,
            "source": args.source,
        }
        contacts.append(entry)
        action = "added"
    else:
        for field, val in (
            ("title", args.title), ("role", args.role), ("email", args.email),
            ("phone", args.phone), ("linkedin", args.linkedin),
            ("language", args.language), ("notes", args.notes), ("source", args.source),
        ):
            if val is not None:
                existing[field] = val
        action = "updated"
    rec["updated"] = today()
    save_yaml(path, rec)
    print_out(f"{action} contact {args.name!r} on {args.slug}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: next (work queue)
# ---------------------------------------------------------------------------

def cmd_next(args: argparse.Namespace) -> int:
    recs = load_all_companies()
    d_today = date.today()
    rows = []
    for r in recs:
        na = r.get("next_action")
        if na and na.get("due") and is_valid_date(na["due"]):
            due = parse_date(na["due"])
            days = (d_today - due).days
            if days >= 0:
                rows.append({
                    "slug": r.get("slug"), "name": r.get("name"), "reason": "due" if days == 0 else "overdue",
                    "who": na.get("who"), "what": na.get("what"), "due": na.get("due"),
                    "days_overdue": days, "status": r.get("status"),
                })
        # stalled check
        if r.get("status") in STALLED_STATUSES:
            acts = sorted(
                [a for a in (r.get("activities") or []) if is_valid_date(a.get("date"))],
                key=lambda a: a["date"],
            )
            last_date = parse_date(acts[-1]["date"]) if acts else None
            stalled_days = (d_today - last_date).days if last_date else None
            if last_date is None or stalled_days >= args.days:
                rows.append({
                    "slug": r.get("slug"), "name": r.get("name"),
                    "reason": f"stalled (no activity in {args.days}+ days)" if last_date
                              else "stalled (no activity logged)",
                    "who": r.get("owner"), "what": "re-engage", "due": "",
                    "days_overdue": stalled_days if stalled_days is not None else 9999,
                    "status": r.get("status"),
                })

    rows.sort(key=lambda r: -r["days_overdue"])
    return _emit_rows(
        rows, args.format,
        columns=["slug", "name", "status", "reason", "who", "what", "due", "days_overdue"],
    )


# ---------------------------------------------------------------------------
# Subcommand: rfp add|list|show|update
# ---------------------------------------------------------------------------

def cmd_rfp_add(args: argparse.Namespace) -> int:
    rec = new_rfp_record(args)
    path = rfp_path(rec["slug"])
    if path.exists():
        sys.stderr.write(f"error: {path} already exists — refusing to clobber. Use `rfp update`.\n")
        return 1
    if rec["status"] not in RFP_STATUSES:
        sys.stderr.write(f"error: invalid --status {rec['status']!r}. Allowed: {RFP_STATUSES}\n")
        return 1
    if rec["decision"]["outcome"] not in RFP_OUTCOMES:
        sys.stderr.write(f"error: invalid --outcome {rec['decision']['outcome']!r}. Allowed: {RFP_OUTCOMES}\n")
        return 1
    if args.published_date and not is_valid_date(args.published_date):
        sys.stderr.write("error: --published-date must be YYYY-MM-DD\n")
        return 1
    if not is_valid_date(args.deadline):
        sys.stderr.write("error: --deadline must be YYYY-MM-DD\n")
        return 1
    RFPS_DIR.mkdir(parents=True, exist_ok=True)
    save_yaml(path, rec)
    print_out(f"created {path.relative_to(REPO_ROOT)}  (slug={rec['slug']})")
    return 0


def cmd_rfp_list(args: argparse.Namespace) -> int:
    recs = load_all_rfps()

    def keep(r: dict) -> bool:
        if args.country and (r.get("country") or "").lower() != args.country.lower():
            return False
        if args.segment and r.get("segment") != args.segment:
            return False
        if args.status and r.get("status") != args.status:
            return False
        return True

    recs = [r for r in recs if keep(r)]
    recs.sort(key=lambda r: r.get("deadline") or "9999-99-99")
    rows = [{
        "slug": r.get("slug"), "title": r.get("title"), "issuer": r.get("issuer"),
        "country": r.get("country"), "segment": r.get("segment"), "status": r.get("status"),
        "deadline": r.get("deadline"),
    } for r in recs]
    return _emit_rows(rows, args.format,
                       columns=["slug", "title", "issuer", "country", "segment", "status", "deadline"])


def cmd_rfp_show(args: argparse.Namespace) -> int:
    path = rfp_path(args.slug)
    if not path.exists():
        sys.stderr.write(f"error: no RFP record for slug {args.slug!r}\n")
        return 1
    rec = load_yaml(path)
    if args.format == "yaml":
        print_out(dump_yaml(rec))
        return 0
    if args.format == "json":
        print_out(json.dumps(rec, indent=2))
        return 0
    lines = [
        f"{rec.get('title')}  [{rec.get('slug')}]",
        f"  issuer: {rec.get('issuer')}  ({rec.get('country')}, {rec.get('segment')})",
        f"  status: {rec.get('status')}   deadline: {rec.get('deadline')}   "
        f"published: {rec.get('published_date')}",
        f"  source: {rec.get('source_url')}",
        f"  fit_assessment: {rec.get('fit_assessment')}",
    ]
    dec = rec.get("decision") or {}
    lines.append(f"  decision: {dec.get('outcome')} — {dec.get('reason')}")
    docs = rec.get("documents") or []
    lines.append(f"  documents ({len(docs)}):")
    for doc in docs:
        lines.append(f"    - {doc.get('label')}: {doc.get('link')}")
    lines.append(f"  owner={rec.get('owner')}  created={rec.get('created')}  updated={rec.get('updated')}")
    print_out("\n".join(lines))
    return 0


def cmd_rfp_update(args: argparse.Namespace) -> int:
    path = rfp_path(args.slug)
    if not path.exists():
        sys.stderr.write(f"error: no RFP record for slug {args.slug!r}\n")
        return 1
    rec = load_yaml(path)
    if args.status:
        if args.status not in RFP_STATUSES:
            sys.stderr.write(f"error: invalid --status {args.status!r}. Allowed: {RFP_STATUSES}\n")
            return 1
        rec["status"] = args.status
    if args.deadline:
        if not is_valid_date(args.deadline):
            sys.stderr.write("error: --deadline must be YYYY-MM-DD\n")
            return 1
        rec["deadline"] = args.deadline
    if args.fit_assessment:
        rec["fit_assessment"] = args.fit_assessment
    if args.outcome:
        if args.outcome not in RFP_OUTCOMES:
            sys.stderr.write(f"error: invalid --outcome {args.outcome!r}. Allowed: {RFP_OUTCOMES}\n")
            return 1
        rec.setdefault("decision", {})["outcome"] = args.outcome
    if args.reason:
        rec.setdefault("decision", {})["reason"] = args.reason
    if args.add_document:
        label, _, link = args.add_document.partition("|")
        rec.setdefault("documents", []).append({"label": label or "document", "link": link or None})
    for kv in args.set or []:
        if "=" not in kv:
            sys.stderr.write(f"error: --set expects KEY=VALUE, got {kv!r}\n")
            return 1
        key, _, raw = kv.partition("=")
        set_dotted(rec, key, coerce_value(raw))
    rec["updated"] = today()
    save_yaml(path, rec)
    print_out(f"updated {path.relative_to(REPO_ROOT)}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: stats
# ---------------------------------------------------------------------------

def cmd_stats(args: argparse.Namespace) -> int:
    companies = load_all_companies()
    rfps = load_all_rfps()

    def counts(items: list[dict], field: str) -> dict:
        out: dict[str, int] = {}
        for it in items:
            key = it.get(field) or "unknown"
            out[key] = out.get(key, 0) + 1
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    result = {
        "companies_total": len(companies),
        "by_status": counts(companies, "status"),
        "by_segment": counts(companies, "segment"),
        "by_country": counts(companies, "country"),
        "rfps_total": len(rfps),
        "rfps_by_status": counts(rfps, "status"),
    }

    upcoming = []
    d_today = date.today()
    for r in rfps:
        if r.get("status") in ("won", "lost", "skipped"):
            continue
        dl = r.get("deadline")
        if dl and is_valid_date(dl):
            days = (parse_date(dl) - d_today).days
            upcoming.append({"slug": r.get("slug"), "title": r.get("title"), "deadline": dl, "days_left": days})
    upcoming.sort(key=lambda u: u["days_left"])
    result["rfp_deadlines_approaching"] = upcoming

    if args.format == "json":
        print_out(json.dumps(result, indent=2))
        return 0

    lines = [f"Companies: {result['companies_total']}   RFPs: {result['rfps_total']}", ""]
    lines.append("By status:")
    for k, v in result["by_status"].items():
        lines.append(f"  {k:15s} {v}")
    lines.append("By segment:")
    for k, v in result["by_segment"].items():
        lines.append(f"  {k:15s} {v}")
    lines.append("By country:")
    for k, v in result["by_country"].items():
        lines.append(f"  {k:15s} {v}")
    lines.append("")
    lines.append("RFP deadlines approaching (open tenders):")
    if not upcoming:
        lines.append("  (none)")
    for u in upcoming:
        flag = "OVERDUE" if u["days_left"] < 0 else f"{u['days_left']}d left"
        lines.append(f"  {u['deadline']}  [{flag:9s}]  {u['title']}  ({u['slug']})")
    print_out("\n".join(lines))
    return 0


# ---------------------------------------------------------------------------
# Subcommand: validate
# ---------------------------------------------------------------------------

def _err(errors: list[str], path: Path, msg: str) -> None:
    errors.append(f"{path.relative_to(REPO_ROOT)}: {msg}")


def validate_company(path: Path, rec: dict, errors: list[str], seen_slugs: set[str]) -> None:
    slug = rec.get("slug")
    if not slug:
        _err(errors, path, "missing 'slug'")
    elif path.stem != slug:
        _err(errors, path, f"file name does not match slug ({path.stem!r} vs {slug!r})")
    if slug in seen_slugs:
        _err(errors, path, f"duplicate slug {slug!r}")
    if slug:
        seen_slugs.add(slug)

    for field in ("name", "country", "segment", "status", "stage", "owner"):
        if not rec.get(field):
            _err(errors, path, f"missing required field '{field}'")

    if rec.get("segment") and rec["segment"] not in SEGMENTS:
        _err(errors, path, f"invalid segment {rec['segment']!r}")
    if rec.get("status") and rec["status"] not in COMPANY_STATUSES:
        _err(errors, path, f"invalid status {rec['status']!r}")
    if rec.get("stage") and rec["stage"] not in COMPANY_STAGES:
        _err(errors, path, f"invalid stage {rec['stage']!r}")

    for field in ("created", "updated"):
        v = rec.get(field)
        if v is not None and not is_valid_date(v):
            _err(errors, path, f"'{field}' is not a valid YYYY-MM-DD date: {v!r}")

    src = rec.get("source") or {}
    if src.get("date") is not None and not is_valid_date(src["date"]):
        _err(errors, path, f"source.date is not a valid date: {src.get('date')!r}")

    fit = rec.get("fit") or {}
    score = fit.get("score")
    if score is not None and not (isinstance(score, int) and 0 <= score <= 100):
        _err(errors, path, f"fit.score must be null or an integer 0-100, got {score!r}")
    if rec.get("status") == "disqualified" and not fit.get("disqualified_reason"):
        _err(errors, path, "status is 'disqualified' but fit.disqualified_reason is empty")
    if rec.get("status") != "disqualified" and fit.get("disqualified_reason"):
        _err(errors, path, "fit.disqualified_reason is set but status is not 'disqualified'")

    for i, c in enumerate(rec.get("contacts") or []):
        if not c.get("name"):
            _err(errors, path, f"contacts[{i}] missing 'name'")
        role = c.get("role")
        if role and role not in CONTACT_ROLES:
            _err(errors, path, f"contacts[{i}] invalid role {role!r}")
        lang = c.get("language")
        if lang and lang not in CONTACT_LANGUAGES:
            _err(errors, path, f"contacts[{i}] invalid language {lang!r}")

    for i, a in enumerate(rec.get("activities") or []):
        if a.get("type") not in ACTIVITY_TYPES:
            _err(errors, path, f"activities[{i}] invalid type {a.get('type')!r}")
        if not is_valid_date(a.get("date")):
            _err(errors, path, f"activities[{i}] invalid date {a.get('date')!r}")
        if not a.get("summary"):
            _err(errors, path, f"activities[{i}] missing summary")

    na = rec.get("next_action")
    if na is not None:
        missing = [k for k in ("who", "what", "due") if not na.get(k)]
        if missing:
            _err(errors, path, f"next_action must be null or have who+what+due; missing {missing}")
        elif not is_valid_date(na["due"]):
            _err(errors, path, f"next_action.due is not a valid date: {na['due']!r}")


def validate_rfp(path: Path, rec: dict, errors: list[str], seen_slugs: set[str]) -> None:
    slug = rec.get("slug")
    if not slug:
        _err(errors, path, "missing 'slug'")
    elif path.stem != slug:
        _err(errors, path, f"file name does not match slug ({path.stem!r} vs {slug!r})")
    if slug in seen_slugs:
        _err(errors, path, f"duplicate slug {slug!r}")
    if slug:
        seen_slugs.add(slug)

    for field in ("title", "issuer", "deadline", "status"):
        if not rec.get(field):
            _err(errors, path, f"missing required field '{field}'")

    if rec.get("status") and rec["status"] not in RFP_STATUSES:
        _err(errors, path, f"invalid status {rec['status']!r}")

    for field in ("published_date", "deadline", "created", "updated"):
        v = rec.get(field)
        if v is not None and not is_valid_date(v):
            _err(errors, path, f"'{field}' is not a valid date: {v!r}")

    dec = rec.get("decision") or {}
    if dec.get("outcome") and dec["outcome"] not in RFP_OUTCOMES:
        _err(errors, path, f"decision.outcome invalid {dec['outcome']!r}")


def cmd_validate(args: argparse.Namespace) -> int:
    errors: list[str] = []
    seen_company_slugs: set[str] = set()
    seen_rfp_slugs: set[str] = set()

    for p in all_company_files():
        try:
            rec = load_yaml(p)
        except yaml.YAMLError as e:
            _err(errors, p, f"YAML parse error: {e}")
            continue
        validate_company(p, rec, errors, seen_company_slugs)

    for p in all_rfp_files():
        try:
            rec = load_yaml(p)
        except yaml.YAMLError as e:
            _err(errors, p, f"YAML parse error: {e}")
            continue
        validate_rfp(p, rec, errors, seen_rfp_slugs)

    if errors:
        for e in errors:
            print_out(f"FAIL  {e}")
        print_out(f"\n{len(errors)} error(s) across "
                   f"{len(seen_company_slugs)} companies, {len(seen_rfp_slugs)} RFPs.")
        return 1
    print_out(f"OK — {len(seen_company_slugs)} companies, {len(seen_rfp_slugs)} RFPs validated.")
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crm.py",
        description="The CRM for the OFS sales workspace — companies and RFPs as YAML records "
                    "in this repo. See crm/SCHEMA.md for the record shape.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # add
    sp = sub.add_parser("add", help="Create a new company record.")
    sp.add_argument("--name", required=True, help="Company display name.")
    sp.add_argument("--slug", help="Override the auto-generated slug.")
    sp.add_argument("--legal-name")
    sp.add_argument("--country")
    sp.add_argument("--city")
    sp.add_argument("--segment", choices=SEGMENTS)
    sp.add_argument("--regulator")
    sp.add_argument("--website")
    sp.add_argument("--linkedin")
    sp.add_argument("--aum", help="Free text, e.g. 'USD 400m'. Leave unset if unknown.")
    sp.add_argument("--employees")
    sp.add_argument("--portfolios")
    sp.add_argument("--description")
    sp.add_argument("--source-channel", default="web_research",
                     help="Where we found them, e.g. linkedin_search, referral, rfp_portal, "
                          "conference, inbound.")
    sp.add_argument("--source-detail", help="Free text detail on the source.")
    sp.add_argument("--source-date", help="YYYY-MM-DD, defaults to today.")
    sp.add_argument("--status", default="new", choices=COMPANY_STATUSES)
    sp.add_argument("--stage", default="identified", choices=COMPANY_STAGES)
    sp.add_argument("--owner", default=DEFAULT_OWNER)
    sp.add_argument("--tags", help="Comma-separated tags.")
    sp.add_argument("--score", type=int, help="ICP fit score 0-100.")
    sp.add_argument("--score-reasoning", help="Why this score.")
    sp.set_defaults(func=cmd_add)

    # show
    sp = sub.add_parser("show", help="Pretty-print one company record.")
    sp.add_argument("slug")
    sp.add_argument("--format", choices=["pretty", "yaml", "json"], default="pretty")
    sp.set_defaults(func=cmd_show)

    # list
    sp = sub.add_parser("list", help="List/filter company records.")
    sp.add_argument("--country", help="Comma-separated for multiple, e.g. UAE,KSA.")
    sp.add_argument("--segment", help=f"Comma-separated. Allowed: {', '.join(SEGMENTS)}.")
    sp.add_argument("--status", help=f"Comma-separated. Allowed: {', '.join(COMPANY_STATUSES)}.")
    sp.add_argument("--stage", help=f"Comma-separated. Allowed: {', '.join(COMPANY_STAGES)}.")
    sp.add_argument("--tag", help="Comma-separated — matches any of the given tags.")
    sp.add_argument("--owner")
    sp.add_argument("--min-score", type=int)
    sp.add_argument("--sort", choices=["name", "status", "stage", "score", "updated", "next_due"],
                     default="name")
    sp.add_argument("--format", choices=["table", "json", "csv"], default="table")
    sp.set_defaults(func=cmd_list)

    # update
    sp = sub.add_parser("update", help="Update fields on a company record.")
    sp.add_argument("slug")
    sp.add_argument("--status", choices=COMPANY_STATUSES)
    sp.add_argument("--stage", choices=COMPANY_STAGES)
    sp.add_argument("--owner")
    sp.add_argument("--add-tag", action="append")
    sp.add_argument("--remove-tag", action="append")
    sp.add_argument("--score", type=int)
    sp.add_argument("--score-reasoning")
    sp.add_argument("--disqualified-reason")
    sp.add_argument("--next-who")
    sp.add_argument("--next-what")
    sp.add_argument("--next-due", help="YYYY-MM-DD")
    sp.add_argument("--clear-next-action", action="store_true")
    sp.add_argument("--set", action="append", metavar="KEY=VALUE",
                     help="Generic field set, dotted path for nested fields "
                          "(e.g. size.aum='USD 400m'). Repeatable.")
    sp.set_defaults(func=cmd_update)

    # log
    sp = sub.add_parser("log", help="Append an activity to a company record.")
    sp.add_argument("slug")
    sp.add_argument("--type", required=True, choices=ACTIVITY_TYPES)
    sp.add_argument("--summary", required=True)
    sp.add_argument("--date", help="YYYY-MM-DD, defaults to today.")
    sp.add_argument("--link", help="Path (relative to repo root) to a related artifact.")
    sp.set_defaults(func=cmd_log)

    # contact
    sp = sub.add_parser("contact", help="Add or update a contact on a company record.")
    sp.add_argument("slug")
    sp.add_argument("--name", required=True, help="Matches an existing contact by name, or creates one.")
    sp.add_argument("--title")
    sp.add_argument("--role", choices=CONTACT_ROLES)
    sp.add_argument("--email")
    sp.add_argument("--phone")
    sp.add_argument("--linkedin")
    sp.add_argument("--language", choices=CONTACT_LANGUAGES)
    sp.add_argument("--notes")
    sp.add_argument("--source")
    sp.set_defaults(func=cmd_contact)

    # next
    sp = sub.add_parser("next", help="Work queue: due/overdue next actions + stalled deals.")
    sp.add_argument("--days", type=int, default=14,
                     help="Days without activity before a contacted/engaged deal is 'stalled'.")
    sp.add_argument("--format", choices=["table", "json", "csv"], default="table")
    sp.set_defaults(func=cmd_next)

    # rfp
    rfp = sub.add_parser("rfp", help="Manage RFP/tender records.")
    rfp_sub = rfp.add_subparsers(dest="rfp_command", required=True)

    sp = rfp_sub.add_parser("add", help="Create a new RFP record.")
    sp.add_argument("--title", required=True)
    sp.add_argument("--issuer", required=True)
    sp.add_argument("--slug")
    sp.add_argument("--country")
    sp.add_argument("--segment", choices=SEGMENTS)
    sp.add_argument("--source-url")
    sp.add_argument("--published-date", help="YYYY-MM-DD")
    sp.add_argument("--deadline", required=True, help="YYYY-MM-DD")
    sp.add_argument("--status", default="spotted", choices=RFP_STATUSES)
    sp.add_argument("--fit-assessment")
    sp.add_argument("--outcome", default="pending", choices=RFP_OUTCOMES)
    sp.add_argument("--reason")
    sp.add_argument("--owner", default=DEFAULT_OWNER)
    sp.set_defaults(func=cmd_rfp_add)

    sp = rfp_sub.add_parser("list", help="List/filter RFP records, soonest deadline first.")
    sp.add_argument("--country")
    sp.add_argument("--segment", choices=SEGMENTS)
    sp.add_argument("--status", choices=RFP_STATUSES)
    sp.add_argument("--format", choices=["table", "json", "csv"], default="table")
    sp.set_defaults(func=cmd_rfp_list)

    sp = rfp_sub.add_parser("show", help="Pretty-print one RFP record.")
    sp.add_argument("slug")
    sp.add_argument("--format", choices=["pretty", "yaml", "json"], default="pretty")
    sp.set_defaults(func=cmd_rfp_show)

    sp = rfp_sub.add_parser("update", help="Update fields on an RFP record.")
    sp.add_argument("slug")
    sp.add_argument("--status", choices=RFP_STATUSES)
    sp.add_argument("--deadline", help="YYYY-MM-DD")
    sp.add_argument("--fit-assessment")
    sp.add_argument("--outcome", choices=RFP_OUTCOMES)
    sp.add_argument("--reason")
    sp.add_argument("--add-document", metavar="LABEL|LINK")
    sp.add_argument("--set", action="append", metavar="KEY=VALUE")
    sp.set_defaults(func=cmd_rfp_update)

    # stats
    sp = sub.add_parser("stats", help="Counts by status/segment/country + approaching RFP deadlines.")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_stats)

    # validate
    sp = sub.add_parser("validate", help="Schema check across every record. Non-zero exit on error.")
    sp.set_defaults(func=cmd_validate)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
