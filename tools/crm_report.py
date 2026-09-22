#!/usr/bin/env python3
"""
crm_report.py — generates Andre's morning brief from the CRM in crm/.

Who this is for: Andre Geha, the only human on this sales team, every morning. Agents source
leads, research them and draft outreach; **Andre approves and sends everything himself** — this
report exists to make that approve-and-send loop as fast as physically possible, without ever
sending anything on his behalf.

What it produces: one self-contained HTML file (no external assets, no network calls, works
offline, prints cleanly) covering:
  1. Outreach waiting for his approval today (drafted emails / LinkedIn messages).
  2. RFP deadlines approaching, most urgent first.
  3. The work queue (`crm.py next`): due/overdue next actions and stalled deals.
  4. New leads added since the last time this report ran.
  5. Pipeline summary by status, segment and country.

Every drafted email gets a `mailto:` link (recipient, subject and body pre-filled and
URL-encoded) *and* a copy-to-clipboard button for the body — mailto has practical length limits
in most mail clients, so copy-to-clipboard is the reliable path and mailto is the convenience
path for short messages. Every LinkedIn action gets a direct link to the contact's profile (or a
LinkedIn people-search URL when we do not have one on file) plus a copy button for the message.

## Outreach convention this script relies on
`crm.py log <slug> --type email_drafted --summary "..." --link <path>` records a drafted email.
`--link` may point at a text/markdown file in this repo containing the draft; that file may start
with `Subject: ...` on its own line (rest of the file is the body), otherwise the whole file is
the body and the subject defaults to "Gaia — <company>". If there is no `--link`, the `--summary`
is used the same way — a leading `Subject:` line is lifted out rather than left in the body.
text itself is used as the body. A drafted email is considered **still awaiting approval** until a
later `email_sent` activity is logged for that company (matching the same `--link` if both have
one, otherwise the next `email_sent` clears every earlier pending draft for that company — a
solo-approver workflow drafts and sends one thing at a time).

The same applies to `--type linkedin`: the activity is presumed to be a pending, unsent message
unless its `--summary` starts with `Sent:` or `Completed:` (case-insensitive) — log a follow-up
`linkedin` activity that way once Andre has actually sent it.

Recipient / profile resolution is a best-effort convenience, never an invention: the report picks
the company's `economic_buyer` or `champion` contact with a non-null email/linkedin if one exists,
and says so on the card. If no such contact exists, it says exactly that instead of guessing.

Usage:
    python3 tools/crm_report.py                       # writes crm/reports/brief-YYYY-MM-DD.html
    python3 tools/crm_report.py --out /path/to/out.html
    python3 tools/crm_report.py --stalled-days 21      # passed through to `crm.py next`
    python3 tools/crm_report.py --since 2026-09-15     # override "new leads" cutoff
    python3 tools/crm_report.py --no-state             # do not read/update the last-run marker
    python3 tools/crm_report.py --open                 # also print the file:// URL for convenience

Standard library only, except that it imports `crm.py` (also standard-library-only, PyYAML aside)
from this same directory. Read-only against every client system — this script only ever reads
`crm/` and writes one HTML report plus its own small state file under `crm/`.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import crm  # noqa: E402  (local import, path adjusted above)

REPO_ROOT = crm.REPO_ROOT
REPORTS_DIR = crm.CRM_DIR / "reports"
STATE_FILE = crm.CRM_DIR / ".report_state.json"

MAILTO_BODY_LIMIT = 1500  # conservative — many mail clients truncate or reject much longer mailto: bodies
SENT_MARKERS = ("sent:", "completed:", "done:")


# ---------------------------------------------------------------------------
# Data assembly
# ---------------------------------------------------------------------------

def read_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def write_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def resolve_draft_file(link: Optional[str]) -> Optional[str]:
    """Read a linked draft artifact from the repo. Returns None if there is nothing to read."""
    if not link:
        return None
    p = (REPO_ROOT / link).resolve()
    try:
        p.relative_to(REPO_ROOT)
    except ValueError:
        return None  # never read outside the repo
    if not p.exists() or not p.is_file():
        return None
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return None


def split_subject_body(raw: str, default_subject: str) -> tuple[str, str]:
    lines = raw.splitlines()
    if lines and lines[0].lower().startswith("subject:"):
        subject = lines[0].split(":", 1)[1].strip()
        body = "\n".join(lines[1:]).lstrip("\n")
        return subject or default_subject, body
    return default_subject, raw


def pick_email_contact(company: dict) -> Optional[dict]:
    contacts = company.get("contacts") or []
    for role in ("economic_buyer", "champion"):
        for c in contacts:
            if c.get("role") == role and c.get("email"):
                return c
    for c in contacts:
        if c.get("email"):
            return c
    return None


def pick_linkedin_contact(company: dict) -> Optional[dict]:
    contacts = company.get("contacts") or []
    for role in ("economic_buyer", "champion"):
        for c in contacts:
            if c.get("role") == role and c.get("linkedin"):
                return c
    for c in contacts:
        if c.get("linkedin"):
            return c
    return None


def linkedin_search_url(query: str) -> str:
    return "https://www.linkedin.com/search/results/people/?keywords=" + quote(query)


def compute_pending_outreach(companies: list[dict]) -> list[dict]:
    """Drafted emails/LinkedIn messages that appear to still be awaiting Andre's send.

    See the module docstring for the exact convention this relies on.
    """
    items = []
    for company in companies:
        acts = [a for a in (company.get("activities") or []) if crm.is_valid_date(a.get("date"))]
        acts_sorted = sorted(enumerate(acts), key=lambda ia: (ia[1]["date"], ia[0]))

        pending_email: list[dict] = []
        pending_li: list[dict] = []

        for _, a in acts_sorted:
            atype = a.get("type")
            summary = (a.get("summary") or "")
            if atype == "email_drafted":
                pending_email.append(a)
            elif atype == "email_sent":
                link = a.get("link")
                if link:
                    pending_email = [p for p in pending_email if p.get("link") != link]
                else:
                    pending_email = []
            elif atype == "linkedin":
                if summary.strip().lower().startswith(SENT_MARKERS):
                    link = a.get("link")
                    if link:
                        pending_li = [p for p in pending_li if p.get("link") != link]
                    else:
                        pending_li = []
                else:
                    pending_li.append(a)

        for a in pending_email:
            raw = resolve_draft_file(a.get("link"))
            default_subject = f"Gaia — {company.get('name')}"
            if raw is not None:
                subject, body = split_subject_body(raw, default_subject)
            else:
                # Inline draft in the activity summary. Honour a leading "Subject:" line here too,
                # otherwise the subject is duplicated at the top of the body Andre sends.
                subject, body = split_subject_body(a.get("summary") or "", default_subject)
            contact = pick_email_contact(company)
            items.append({
                "kind": "email",
                "company_slug": company.get("slug"),
                "company_name": company.get("name"),
                "date": a.get("date"),
                "summary": a.get("summary"),
                "link": a.get("link"),
                "subject": subject,
                "body": body,
                "to_name": contact.get("name") if contact else None,
                "to_email": contact.get("email") if contact else None,
            })

        for a in pending_li:
            raw = resolve_draft_file(a.get("link"))
            message = raw if raw is not None else (a.get("summary") or "")
            contact = pick_linkedin_contact(company)
            if contact and contact.get("linkedin"):
                profile_url = contact["linkedin"]
                is_search = False
            else:
                query = f"{contact.get('name')} {company.get('name')}" if contact else company.get("name")
                profile_url = linkedin_search_url(query or "")
                is_search = True
            items.append({
                "kind": "linkedin",
                "company_slug": company.get("slug"),
                "company_name": company.get("name"),
                "date": a.get("date"),
                "summary": a.get("summary"),
                "link": a.get("link"),
                "message": message,
                "to_name": contact.get("name") if contact else None,
                "profile_url": profile_url,
                "is_search": is_search,
            })

    items.sort(key=lambda it: it["date"])
    return items


def compute_new_leads(companies: list[dict], since: str) -> list[dict]:
    out = [c for c in companies if (c.get("created") or "") >= since]
    out.sort(key=lambda c: c.get("created") or "", reverse=True)
    return out


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def esc(s: Any) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def js_str(s: Any) -> str:
    """Safe to drop inside a single-quoted JS string literal in an inline <script>."""
    return (str(s if s is not None else "")
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("\r", ""))


def mailto_link(to_email: str, subject: str, body: str) -> tuple[str, bool]:
    truncated = len(body) > MAILTO_BODY_LIMIT
    mailto_body = body[:MAILTO_BODY_LIMIT] if truncated else body
    url = f"mailto:{quote(to_email)}?subject={quote(subject)}&body={quote(mailto_body)}"
    return url, truncated


def render_pending_card(item: dict, idx: int) -> str:
    cid = f"copy-{idx}"
    header = (f'<a href="#" class="pill" title="crm.py show {esc(item["company_slug"])}">'
              f'{esc(item["company_name"])}</a>')
    if item["kind"] == "email":
        to_line = (f'{esc(item["to_name"])} &lt;{esc(item["to_email"])}&gt;'
                   if item.get("to_email") else
                   '<span class="warn">no contact email on file — resolve before sending</span>')
        body_text = item["body"]
        actions = []
        if item.get("to_email"):
            url, truncated = mailto_link(item["to_email"], item["subject"], body_text)
            note = ' <span class="muted">(body truncated in link — use Copy for the full message)</span>' if truncated else ""
            actions.append(f'<a class="btn btn-primary" href="{esc(url)}">Open email draft</a>{note}')
        actions.append(f'<button class="btn" onclick="copyText(\'{cid}\')">Copy body</button>')
        return f"""
        <div class="card">
          <div class="card-head">{header} <span class="tag tag-email">email — drafted {esc(item['date'])}</span></div>
          <div class="field"><span class="label">To</span> {to_line}</div>
          <div class="field"><span class="label">Subject</span> {esc(item['subject'])}</div>
          <div class="body-preview" id="{cid}-view">{esc(body_text)}</div>
          <textarea id="{cid}" class="hidden-copy-source">{esc(body_text)}</textarea>
          <div class="actions">{''.join(actions)}</div>
          <div class="muted small">source activity: {esc(item.get('summary'))}{f" — {esc(item['link'])}" if item.get('link') else ""}</div>
        </div>"""
    else:  # linkedin
        who = esc(item["to_name"]) if item.get("to_name") else "no linked contact on file"
        profile_label = "Search on LinkedIn" if item["is_search"] else "Open profile"
        search_note = ('<span class="warn">no profile URL on file — this is a name search, verify '
                       'the right person before sending</span>' if item["is_search"] else "")
        return f"""
        <div class="card">
          <div class="card-head">{header} <span class="tag tag-li">LinkedIn — drafted {esc(item['date'])}</span></div>
          <div class="field"><span class="label">Contact</span> {who}</div>
          {f'<div class="field">{search_note}</div>' if search_note else ""}
          <div class="body-preview" id="{cid}-view">{esc(item['message'])}</div>
          <textarea id="{cid}" class="hidden-copy-source">{esc(item['message'])}</textarea>
          <div class="actions">
            <a class="btn btn-primary" href="{esc(item['profile_url'])}" target="_blank" rel="noopener">{profile_label}</a>
            <button class="btn" onclick="copyText('{cid}')">Copy message</button>
          </div>
          <div class="muted small">source activity: {esc(item.get('summary'))}{f" — {esc(item['link'])}" if item.get('link') else ""}</div>
        </div>"""


def render_rfp_table(upcoming: list[dict]) -> str:
    if not upcoming:
        return '<p class="muted">No open tender deadlines on record.</p>'
    rows = []
    for u in upcoming:
        days = u["days_left"]
        if days < 0:
            urgency, label = "urgent", f"{-days}d overdue"
        elif days <= 7:
            urgency, label = "urgent", f"{days}d left"
        elif days <= 30:
            urgency, label = "soon", f"{days}d left"
        else:
            urgency, label = "", f"{days}d left"
        rows.append(f'<tr class="{urgency}"><td>{esc(u["deadline"])}</td><td>{esc(label)}</td>'
                    f'<td>{esc(u["title"])}</td><td><code>{esc(u["slug"])}</code></td></tr>')
    return f"""
    <table>
      <thead><tr><th>Deadline</th><th>Time left</th><th>Tender</th><th>Slug</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>"""


def render_queue_table(rows: list[dict]) -> str:
    if not rows:
        return '<p class="muted">Nothing due, overdue or stalled. The queue is clear.</p>'
    out = []
    for r in rows:
        urgency = "urgent" if r["days_overdue"] > 0 and r["reason"] == "overdue" else ""
        out.append(f'<tr class="{urgency}">'
                   f'<td><code>{esc(r["slug"])}</code><br>{esc(r["name"])}</td>'
                   f'<td>{esc(r["status"])}</td>'
                   f'<td>{esc(r["reason"])}</td>'
                   f'<td>{esc(r["who"])}</td>'
                   f'<td>{esc(r["what"])}</td>'
                   f'<td>{esc(r["due"])}</td>'
                   f'</tr>')
    return f"""
    <table>
      <thead><tr><th>Company</th><th>Status</th><th>Why it's here</th><th>Who</th><th>What</th><th>Due</th></tr></thead>
      <tbody>{''.join(out)}</tbody>
    </table>"""


def render_new_leads(leads: list[dict]) -> str:
    if not leads:
        return '<p class="muted">No new leads since the last run.</p>'
    out = []
    for c in leads:
        src = c.get("source") or {}
        fit = c.get("fit") or {}
        out.append(f'<tr>'
                   f'<td><code>{esc(c["slug"])}</code><br>{esc(c["name"])}</td>'
                   f'<td>{esc(c.get("country"))}</td>'
                   f'<td>{esc(c.get("segment"))}</td>'
                   f'<td>{esc(fit.get("score"))}</td>'
                   f'<td>{esc(src.get("channel"))} — {esc(src.get("detail"))}</td>'
                   f'<td>{esc(c.get("created"))}</td>'
                   f'</tr>')
    return f"""
    <table>
      <thead><tr><th>Company</th><th>Country</th><th>Segment</th><th>Fit</th><th>Source</th><th>Added</th></tr></thead>
      <tbody>{''.join(out)}</tbody>
    </table>"""


def render_breakdown(title: str, counts: dict) -> str:
    if not counts:
        return f'<div class="breakdown"><h3>{esc(title)}</h3><p class="muted">No data yet.</p></div>'
    total = sum(counts.values()) or 1
    rows = []
    for k, v in counts.items():
        pct = round(100 * v / total)
        rows.append(f'<div class="bar-row"><span class="bar-label">{esc(k)}</span>'
                    f'<span class="bar-track"><span class="bar-fill" style="width:{pct}%"></span></span>'
                    f'<span class="bar-value">{v}</span></div>')
    return f'<div class="breakdown"><h3>{esc(title)}</h3>{"".join(rows)}</div>'


PAGE_CSS = """
:root {
  --bg: #f6f7f9; --card-bg: #ffffff; --text: #1b1f24; --muted: #6b7280;
  --border: #e2e5ea; --accent: #1a56db; --accent-contrast: #ffffff;
  --urgent-bg: #fdecec; --urgent-border: #e2554e; --soon-bg: #fff6e0; --soon-border: #c98a05;
  --pill-bg: #eef2ff; --tag-email: #e6f4ea; --tag-li: #e8f0fe;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #14161a; --card-bg: #1d2025; --text: #e8eaed; --muted: #9aa0a6;
    --border: #30343b; --accent: #6ea8fe; --accent-contrast: #0b1220;
    --urgent-bg: #3a1f1f; --urgent-border: #e2554e; --soon-bg: #3a301a; --soon-border: #c98a05;
    --pill-bg: #232640; --tag-email: #1e2f22; --tag-li: #1c2740;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 0 0 4rem 0; background: var(--bg); color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  line-height: 1.5;
}
.wrap { max-width: 980px; margin: 0 auto; padding: 1.5rem; }
header.top { border-bottom: 1px solid var(--border); padding: 1.5rem; background: var(--card-bg); }
header.top h1 { margin: 0 0 0.25rem 0; font-size: 1.5rem; }
header.top .sub { color: var(--muted); }
.stat-strip { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1rem; }
.stat { background: var(--pill-bg); border-radius: 8px; padding: 0.5rem 0.9rem; font-size: 0.9rem; }
.stat b { font-size: 1.1rem; }
section { margin-top: 2rem; }
section h2 { font-size: 1.15rem; border-bottom: 2px solid var(--border); padding-bottom: 0.4rem; }
.card {
  background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px;
  padding: 1rem 1.2rem; margin-bottom: 1rem;
}
.card-head { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.6rem; flex-wrap: wrap; }
.pill { background: var(--pill-bg); color: var(--accent); text-decoration: none; padding: 0.15rem 0.6rem;
  border-radius: 999px; font-weight: 600; font-size: 0.95rem; }
.tag { font-size: 0.78rem; padding: 0.15rem 0.5rem; border-radius: 6px; color: var(--muted); }
.tag-email { background: var(--tag-email); }
.tag-li { background: var(--tag-li); }
.field { margin: 0.25rem 0; }
.label { color: var(--muted); font-size: 0.85rem; margin-right: 0.4rem; }
.body-preview {
  white-space: pre-wrap; background: var(--bg); border: 1px dashed var(--border); border-radius: 8px;
  padding: 0.75rem; margin: 0.5rem 0; max-height: 280px; overflow-y: auto; font-size: 0.92rem;
}
.hidden-copy-source { position: absolute; left: -9999px; top: -9999px; }
.actions { display: flex; gap: 0.6rem; align-items: center; flex-wrap: wrap; margin-top: 0.4rem; }
.btn {
  display: inline-block; padding: 0.45rem 0.9rem; border-radius: 8px; border: 1px solid var(--border);
  background: var(--card-bg); color: var(--text); cursor: pointer; font-size: 0.9rem; text-decoration: none;
}
.btn-primary { background: var(--accent); color: var(--accent-contrast); border-color: var(--accent); }
.btn.copied { background: #1a7f37; color: white; border-color: #1a7f37; }
.warn { color: #b45309; }
.muted { color: var(--muted); }
.small { font-size: 0.8rem; }
table { width: 100%; border-collapse: collapse; background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
th, td { text-align: left; padding: 0.5rem 0.7rem; border-bottom: 1px solid var(--border); font-size: 0.92rem; vertical-align: top; }
tr:last-child td { border-bottom: none; }
tr.urgent { background: var(--urgent-bg); }
tr.soon { background: var(--soon-bg); }
code { background: var(--pill-bg); padding: 0.05rem 0.35rem; border-radius: 4px; font-size: 0.85em; }
.breakdown { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; margin-bottom: 1rem; }
.breakdown h3 { margin-top: 0; font-size: 1rem; }
.bar-row { display: grid; grid-template-columns: 140px 1fr 2.5rem; align-items: center; gap: 0.5rem; margin: 0.3rem 0; font-size: 0.88rem; }
.bar-track { background: var(--bg); border-radius: 4px; height: 10px; overflow: hidden; }
.bar-fill { display: block; height: 100%; background: var(--accent); }
.bar-value { text-align: right; color: var(--muted); }
.breakdown-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }
footer.foot { max-width: 980px; margin: 2rem auto 0 auto; padding: 0 1.5rem; color: var(--muted); font-size: 0.85rem; }
@media (max-width: 640px) {
  .bar-row { grid-template-columns: 90px 1fr 2rem; }
}
@media print {
  body { background: white; }
  .btn, .actions a.btn, header.top { box-shadow: none; }
  .card { break-inside: avoid; border-color: #ccc; }
  a.pill { color: black; background: none; }
}
"""

PAGE_JS = """
function copyText(id) {
  var el = document.getElementById(id);
  var btn = event ? event.target : null;
  var text = el.value;
  function done(ok) {
    if (!btn) return;
    var original = btn.textContent;
    btn.textContent = ok ? 'Copied' : 'Copy failed — select manually';
    btn.classList.toggle('copied', ok);
    setTimeout(function () { btn.textContent = original; btn.classList.remove('copied'); }, 1500);
  }
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(function () { done(true); }, function () { fallbackCopy(el, done); });
  } else {
    fallbackCopy(el, done);
  }
}
function fallbackCopy(el, done) {
  try {
    el.style.position = 'fixed';
    el.style.left = '0';
    el.style.top = '0';
    el.focus();
    el.select();
    var ok = document.execCommand('copy');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    done(ok);
  } catch (e) {
    done(false);
  }
}
"""


def render_page(ctx: dict) -> str:
    pending = ctx["pending"]
    stats = ctx["stats"]
    queue = ctx["queue"]
    new_leads = ctx["new_leads"]
    upcoming = stats["rfp_deadlines_approaching"]

    pending_html = ("\n".join(render_pending_card(it, i) for i, it in enumerate(pending))
                    if pending else '<p class="muted">Nothing drafted and waiting on you right now.</p>')

    stat_strip = f"""
      <div class="stat"><b>{stats['companies_total']}</b> companies tracked</div>
      <div class="stat"><b>{len(pending)}</b> waiting on your approval</div>
      <div class="stat"><b>{len(queue)}</b> in the work queue</div>
      <div class="stat"><b>{stats['rfps_total']}</b> RFPs on record</div>
      <div class="stat"><b>{len(new_leads)}</b> new leads since last run</div>
    """

    breakdowns = f"""
      <div class="breakdown-grid">
        {render_breakdown("By status", stats["by_status"])}
        {render_breakdown("By segment", stats["by_segment"])}
        {render_breakdown("By country", stats["by_country"])}
      </div>
    """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OFS Sales — Daily Brief — {esc(ctx['date'])}</title>
<style>{PAGE_CSS}</style>
</head>
<body>
<header class="top">
  <div class="wrap" style="padding:0;">
    <h1>OFS Sales — Daily Brief</h1>
    <div class="sub">{esc(ctx['date'])} · generated {esc(ctx['generated_at'])} · this repo is the system of record</div>
    <div class="stat-strip">{stat_strip}</div>
  </div>
</header>
<div class="wrap">

  <section id="approvals">
    <h2>Needs your approval today</h2>
    {pending_html}
  </section>

  <section id="rfps">
    <h2>RFP deadlines approaching</h2>
    {render_rfp_table(upcoming)}
  </section>

  <section id="queue">
    <h2>Work queue — due, overdue and stalled</h2>
    {render_queue_table(queue)}
  </section>

  <section id="new-leads">
    <h2>New leads since last run{f" ({esc(ctx['since'])})" if ctx.get('since') else ""}</h2>
    {render_new_leads(new_leads)}
  </section>

  <section id="pipeline">
    <h2>Pipeline summary</h2>
    {breakdowns}
  </section>

</div>
<footer class="foot">
  Generated by <code>tools/crm_report.py</code> from <code>crm/</code>. Nothing on this page was sent —
  every send action is yours. Regenerate any time with <code>python3 tools/crm_report.py</code>.
</footer>
<script>{PAGE_JS}</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crm_report.py",
        description="Generate Andre's self-contained HTML daily brief from the CRM in crm/.",
    )
    p.add_argument("--out", help="Output HTML path. Defaults to crm/reports/brief-YYYY-MM-DD.html.")
    p.add_argument("--stalled-days", type=int, default=14,
                    help="Days without activity before a contacted/engaged deal counts as stalled "
                         "(passed through to the same logic as `crm.py next`). Default 14.")
    p.add_argument("--since", help="YYYY-MM-DD override for the 'new leads' cutoff. Defaults to the "
                                    "last time this report was run, or today if never run before.")
    p.add_argument("--no-state", action="store_true",
                    help="Do not read or update the last-run marker (crm/.report_state.json).")
    p.add_argument("--open", action="store_true", help="Print a file:// URL for the report on stdout.")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    companies = crm.load_all_companies()
    rfps = crm.load_all_rfps()

    state = {} if args.no_state else read_state()
    since = args.since or state.get("last_run_date") or date.today().isoformat()

    pending = compute_pending_outreach(companies)
    stats = crm.compute_stats(companies=companies, rfps=rfps)
    queue = crm.compute_next(days=args.stalled_days, companies=companies)
    new_leads = compute_new_leads(companies, since)

    ctx = {
        "date": date.today().isoformat(),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "since": since,
        "pending": pending,
        "stats": stats,
        "queue": queue,
        "new_leads": new_leads,
    }

    out_path = Path(args.out) if args.out else REPORTS_DIR / f"brief-{ctx['date']}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_page(ctx), encoding="utf-8")

    if not args.no_state:
        write_state({"last_run_date": date.today().isoformat(),
                     "last_run_at": ctx["generated_at"]})

    sys.stdout.write(f"wrote {out_path}\n")
    if args.open:
        sys.stdout.write(f"file://{out_path.resolve()}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
