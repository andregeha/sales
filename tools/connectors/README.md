# Regulator register connectors — specification

> ⚠ **Not built yet.** They cannot be built or tested in the cloud environment, which blocks access
> to every regulator website. Build and test them from Andre's laptop — see `RUN-ON-LAPTOP.md`.
> This file is the spec so that session starts from a design, not a blank page.

## The idea, in one line
**Every morning: pull each regulator's list of licensed firms, diff it against yesterday's, and
create a CRM record for every new name.** A firm that has just been licensed needs a portfolio
system and has no incumbent to displace — it is the single best lead signal available to us, and it
arrives on a schedule rather than being hunted for.

## Sources, in build order (easiest and highest-value first)
| # | Regulator | What it publishes | Why this order |
|---|---|---|---|
| 1 | **AMF (France)** — GECO / data.gouv.fr | Licensed *sociétés de gestion de portefeuille*, as a **downloadable dataset** | A real dataset, no scraping, ~227 firms. Build this first and prove the pattern. |
| 2 | **CMA (Saudi Arabia)** | Licensed Capital Market Institutions and investment funds | Our highest-priority market; the population grew from ~188 to ~215 in a year. |
| 3 | **UAE Capital Market Authority** (formerly SCA) | Open-data list of licensed companies | Published as open data. ⚠ Renamed from SCA effective 2026-01-01 — the URL moved. |
| 4 | **DFSA (DIFC)** and **FSRA (ADGM)** | Public registers of authorised firms | Register pages rather than datasets; harder, and the two are separate and non-overlapping. |
| 5 | **ACPR (France)** — REGAFI | Authorised credit and payment institutions | Adjacent segments; lower priority. |

⚠ Lebanon's CMA and Banque du Liban have **no usable public register** we could find. Lebanon stays
relationship-driven — do not build a connector for it.

## How each one must behave
1. **Fetch** the current list. Prefer a published dataset over scraping a page; scrape only if there
   is no dataset.
2. **Snapshot** it to `crm/registers/<regulator>/<YYYY-MM-DD>.json`, raw and unmodified. The
   snapshot is the evidence — it is what lets a future run prove a firm is genuinely new rather
   than newly noticed.
3. **Diff** against the most recent previous snapshot.
4. **For each new entry**, create a CRM record via the same code path as `crm.py add`:
   name, country, segment (derived from the licence type where the register states it), regulator,
   `source.channel: register`, `source.detail` naming the register and the snapshot file, and
   `source.date`. Leave everything the register does not state as `null`.
5. **Score** it. A newly licensed firm in a priority market and segment should land in the 60s before
   any enrichment, on the strength of the licence trigger alone.
6. **Report** what changed: how many entries, how many new, how many disappeared (a firm leaving a
   register is also a signal — a licence surrendered, or an acquisition).

## Non-negotiables
- **Read-only.** Never submit anything to a regulator site, never log in, never create an account.
- **Respect the source.** Reasonable request rates, honour `robots.txt`, identify honestly. These
  are public registers being read once a day, not something to hammer.
- **Never invent.** If the register does not give a website, a contact or an address, the field is
  `null`. A register entry is proof a firm *exists*, not a complete profile.
- **Never silently succeed.** ⚠ This one matters most: in the cloud the fetch **will** fail. The
  connector must exit non-zero and put a clear line in Andre's brief —
  *"AMF register unreachable — run from laptop"* — never return an empty diff that looks like a
  quiet day. A radar that fails silently is worse than no radar, because it is trusted.
- **Deduplicate.** Check the CRM before creating; firms get re-licensed, renamed and re-listed.
- `python3 tools/crm.py validate` must exit 0 after every run.

## Suggested shape
```
tools/connectors/
  base.py          # fetch → snapshot → diff → create → report; the shared pipeline
  amf_france.py    # build and prove this one first
  cma_saudi.py
  cma_uae.py
  run_all.py       # what the daily run calls; reports per-source success or failure
```
Keep it dependency-light and readable. Each connector should be a small file that only knows how to
get its own source's list and map it onto our fields — everything else belongs in `base.py`.
