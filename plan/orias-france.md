# ORIAS (France) — reachable, not readable, and why that is the finding

> Probed live 2026-09-25. Read this before anyone tries again.

## Why we want it

French **MFOs and wealth advisers register as *conseillers en investissements financiers* (CIF)**,
not as sociétés de gestion, so they are invisible to the AMF list that gives us 666 French firms.
France is our largest market (986 records) and `France × family_office` is fed only by SIRENE
candidates. ORIAS is the register that would close that.

## What works

- `https://www.orias.fr/home/showAdvancedSearch` — HTTP 200, a normal CSRF-protected form
  (`SYNCHRONIZER_TOKEN` + `SYNCHRONIZER_URI`, both read from the page).
- `POST /home/resultAdvancedSearch` with `categorieIfinance=CIF` and `etatInscrit=true` returns
  **HTTP 200 and 20 result rows**: registration number, status, SIREN, name, and the categories the
  firm holds (with `SUPPRIMÉ` marking ones withdrawn).
- The `denominationSociale` filter **does** do partial matching — `FILIGRANE` correctly returns
  `FILIGRANE PATRIMOINE`.

## ⚠ Why it is not usable, proven rather than assumed

Every filtered search returns **only rows drawn from that same unfiltered page of 20**:

| Query | Rows | All within the unfiltered 20? |
|---|---:|---|
| *(unfiltered)* | 20 | — |
| `PATRIMOINE` | 2 | yes |
| `CONSEIL` | 2 | yes |
| `A` | **6** | **yes** |
| `GESTION` | 0 | — |
| `family office` | 0 | — |

**Searching for the single letter "A" returns six rows.** In a register of roughly 5,000 CIF
entries, that is not a query — it is a filter applied to one page the server had already decided to
send. `GESTION` returning zero across all of France proves the same thing from the other side.

The page's HTML does contain real pagination markup (`Page`, `pagination`), so the register is
paged; our POST simply is not driving it.

**Therefore: no conclusion about French family offices can be drawn from this.** "We searched ORIAS
for 'family office' and found none" would have been a false statement about the market, produced by
a filter that never reached the data — the exact failure this workspace found in UNGM on 2026-09-23,
where source-side keyword filtering returned zero from four populated markets.

## What would make it work

The pagination contract, taken from the real request rather than inferred: **ten minutes with a
browser's network tab on `resultAdvancedSearch`**, capturing the form fields the page sends when you
click through to page 2. That is the missing piece, and it is a human's ten minutes against an hour
of guessing.

## ⚠ And a judgement to make before building it anyway

Even fully readable, CIF is roughly **5,000 firms, overwhelmingly one- and two-person IFA practices
advising retail clients on life-insurance wrappers**. They are not our buyer. The valuable subset —
French MFOs — is a small minority inside it.

So the right use of ORIAS is **not** "ingest the CIF register". It is a **targeted lookup**: search
it for the specific firms we already suspect, and for segment terms, once the search genuinely
queries the register. Ingesting 5,000 micro-advisers would repeat the *Agent PSP* mistake that this
CRM was explicitly built to avoid, and would bury a 570-row review queue under ten times its size.
