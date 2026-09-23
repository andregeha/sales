# Regulator register connectors — specification

> ✅ **Built 2026-09-22.** `base.py` (shared pipeline) + `amf_france.py` (**live**) +
> `cma_saudi.py` (**written, never yet run — its API is unreachable from Europe**) + `run_all.py`
> + `test_connectors.py` (17 tests, no network needed).
>
> **Status per source**
> | Source | State | Note |
> |---|---|---|
> | **AMF France** | ✅ **Live** | 666 firms, daily CSV. First run created 10 new leads (scores 70-83). |
> | **CMA Saudi** | ✅ **Live (partial)** | Reads the register *page*, which server-renders 36 of 242 entries, newest-first. Catches new names; cannot see disappearances. Its API would be better but times out from Europe — try it from Riyadh. |
> | **DFSA (DIFC)** | ✅ **Live** | Searchable by financial service. 396 Managing Assets + 38 banks + 33 fund admin. Telephone for most. |
> | **FSRA (ADGM)** | ✅ **Live** | A clean JSON API — 497 firms with licence date, address, phone **and an email for over half**. The best source we have. |
> | UAE CMA (onshore, ex-SCA) | ⬜ Not built | The remaining UAE regulator. |
> | ACPR REGAFI | ⬜ Not built | Adjacent segments, low priority. |
>
> **Run them:** `python tools/connectors/run_all.py` (add `--dry-run` to write nothing,
> `--only amf-france` for one, `--json` for the daily brief).
> **Test them:** `python tools/connectors/test_connectors.py`.
>
> The spec below is unchanged and still governs. Two things learned in the build are worth adding
> to it:
> - ⚠ **A 200 does not mean success.** The Saudi CMA returns a styled SharePoint *error page* with
>   HTTP 200, and Etimad returns a bot challenge the same way. Check the **content**, not the code.
> - ⚠ **A baseline run must not dump the back catalogue into the CRM.** 666 French firms would bury
>   the ten that matter. Only firms licensed within `baseline_window_days` (default 180) become
>   records; everything else goes into the snapshot so the next day's diff is still correct.

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
- `python tools/crm.py validate` must exit 0 after every run.

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

## `multilateral_rfp.py` — a different shape, RFP records not company records

Everything above is about `base.py`'s Connector pipeline: one register, a snapshot, a diff, a
company record. **`multilateral_rfp.py` is deliberately not built on that pipeline** — it produces
`crm/rfps/<slug>.yaml` records (via the same code path as `crm.py rfp add`), not company records,
and there is no per-firm register to snapshot and diff; each run just asks "any genuine tender in
our markets right now?" It reads the World Bank procurement-notices API, UNGM, and IsDB's tender
board (all ✅ live), and raises loudly on EBRD by design (its real search tool is a stateful
enterprise portal with no confirmed contract — see the module's own docstring for why that was not
scraped). Run it with `python tools/connectors/multilateral_rfp.py` (`--dry-run`, `--json`).
Test it with `python tools/connectors/test_multilateral.py` (27 tests, no network). See
`memory/changelog.md`, 2026-09-23, for the full build notes and the false positives it took to get
the filtering right.

## `site_contacts.py` — a third shape: enriching records we already hold

Neither a register connector nor an RFP radar. It creates **no** records and proposes **no**
candidates: it reads a firm's own website for the contact route it publishes, and writes that onto
the record we already have.

It exists because the CRM had 1,604 firms and 119 email addresses, all of them UAE — France had 986
records and zero. A directory of firms we cannot write to is worth about the same however long it
gets, so contact routes, not more names, were the bottleneck.

**The contract, in one line: transcription, never inference.** An address is written only if it is
printed on the firm's own site, and the URL it was read from goes into the record beside it. It will
never construct `info@<domain>` or `firstname.lastname@<domain>`.

Three rules that cost real work to get right, each now a test:

- **Wrong doors are excluded.** `dpo@`, `rgpd@`, `careers@`, `press@`, `legal@` are real, published
  and exactly the wrong people to sell to — emailing a data-protection officer to pitch software
  generates a complaint, not a meeting. They are still recorded in the record's activity note; they
  are never written as the route.
- **A phone number must match the market's dialling code.** A French asset manager's page yielded
  `+1 206…`, a Seattle number almost certainly belonging to a vendor widget in the markup.
- **The national trunk prefix is stripped.** Firms print `+33 (0)1 56 88 33 00`; keeping every digit
  gives `+330156883300`, which is one digit too many and will not dial. This was the common case,
  not an edge case.

`robots.txt` is fetched first and obeyed — a site that declines is recorded as *declined* and not
retried. One request at a time, with a delay, a User-Agent naming us, GET only.

```bash
python tools/connectors/site_contacts.py --dry-run --country France --limit 20
python tools/connectors/site_contacts.py --country France      # writes
python tools/connectors/site_contacts.py --all --recheck       # revisit everything
```

⚠ **Not part of the daily run.** Like `sirene_france.py` and `gleif_enrich.py` it is a periodic
sweep over hundreds of hosts, and putting it in `run_all.py` would make the daily pass take an hour
and re-fetch other people's websites for no reason. Results are cached in
`crm/site_contacts/checked.json`.

⚠ **A contact route is not a reason to write.** This connector never touches status, stage or
triggers. It only means that when we do have a reason, the message can leave.
