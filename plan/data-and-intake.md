# Finishing the data, and the machinery that keeps it fed

> Written 2026-09-23. The website is usable, so the question is no longer "can we see it" but
> "is what it shows complete, and does it stay complete without anyone remembering to do anything".
>
> Every source named below was **probed today**. Nothing here is planned against a URL I have not
> opened.

## 1. Where we actually are

| | |
|---|---|
| Active records | **1,292** |
| Register-sourced | **1,227 (95%)** — the connectors are now the engine, not the agents |
| With a real trigger | **168** |
| With an email address | **119** |
| Connectors live | 4 — AMF · CMA Saudi (partial) · DFSA · FSRA |
| Register snapshots | 1 per source — **no history yet, so no diff has ever run for real** |
| Runs recorded | **1** · Change events recorded: **0** |
| Scheduled jobs | **none** |

Coverage, by market × segment:

| | family office | MFO | bank | asset mgr | fund mgr | total |
|---|---|---|---|---|---|---|
| **France** | 0 | 5 | **0** | 326 | 343 | 674 |
| **UAE** | **0** | 4 | 34 | 319 | 176 | 533 |
| **Saudi Arabia** | 2 | 1 | **0** | 26 | 5 | **34** |
| **Lebanon** | 0 | 0 | 14 | 2 | 0 | **16** |

**The honest reading:** France and the UAE are genuinely covered for asset and fund managers.
Everything else is either a gap with a known source, or a market where no register exists.

## 2. The gaps, each with a source I verified today

| Gap | Now | Source | Verified | Est. |
|---|---|---|---|---|
| **France banks** | 0 | **REGAFI** `prd-banque-entites` on `acpr.opendatasoft.com` — Explore v2.1 API, same platform as BOAMP | ✅ 200, 25,660 records, `categorie` filterable | **936** *Établissement de Crédit* |
| **France investment firms** | — | same dataset | ✅ | **1,002** *Entreprise d'Investissement* |
| **Saudi CMIs (completeness)** | 34 | CMA register page renders only 36 of 242; its API is geo-blocked from Europe | 🔴 confirmed blocked | **+206** |
| **Saudi banks** | 0 | SAMA — homepage 200, register path not yet found | 🟠 needs a look | ~30 |
| **UAE onshore** | 1 | `uaecma.gov.ae` (ex-SCA) | 🟠 200, structure unknown | unknown |
| **UAE family offices** | 0 | **NOT the DFSA** — all 41 entries there are withdrawn. DIFC **Family Wealth Centre** is the successor regime | 🟠 429 today, retry | unknown |
| **Lebanon** | 16 | No public register exists | ✅ confirmed absent | — |
| **France family offices** | 0 | AFFO publishes no member directory | ✅ confirmed absent | — |

⚠ **Two of these are not gaps to close, they are facts to accept.** Lebanon and French family
offices have no enumerable public source. Pretending a connector will one day fix that is how a
backlog item becomes permanent. They are **relationship-driven and correctly manual**.

⚠ **REGAFI's 25,660 records are mostly noise** — 22,280 are *Agent PSP*. Ingesting the dataset
wholesale would swamp the CRM the way the AMF back-catalogue nearly did. Only *Établissement de
Crédit* and *Entreprise d'Investissement* are ours.

## 3. The machinery — what must exist for this to stay fed

Today, **nothing runs unless I am asked to run it.** That is the real gap; the data gaps are
finite and closeable, this one recurs every day it is not fixed.

### 3.1 Cadence

| When | What runs | Why that cadence |
|---|---|---|
| **Weekday morning** | `run_all.py` → `enrich_from_registers.py` → RFP alert triage → `build_site.py` → commit | Registers change daily and deadlines do not wait. ~2 new licences/month/market means most days are legitimately "no change" — and that is a result, not a failure. |
| **Weekly** | Full backfill reconciliation · coverage report · contact-route sweep | Catches a firm the daily diff missed because a name changed rather than appeared. |
| **Monthly** | Source health review · dead-source escalation · scoring-model sanity check | A source failing for four weeks needs a decision, not another retry. |
| **On demand** | Intake of something Andre heard | Market intelligence arrives in conversations, not on a schedule. |

### 3.2 What has to be built

**M1 · The scheduler.** Nothing else matters until this exists. Weekday mornings, running the
`/daily-run` skill on this laptop. ⚠ **A laptop only runs when it is on** — the run must therefore
record *that it ran*, and the site must show when it last did, so a silent week is visible rather
than assumed. `Run` records and `/sources` already do exactly this; they have simply never been
exercised.

**M2 · `regafi_france.py`** — the France banks connector. Opendatasoft Explore v2.1, filtered to
the two categories that are ours. Same `base.py` pipeline, same fail-loud contract.

**M3 · `/intake` skill — the one genuinely new idea here.**
Andre hears things: a hire, a fund launch, a bank restructuring, a name at a conference. Right now
that lands in a chat message and dies there, which contradicts the workspace's own first rule
("nothing important lives only in a conversation"). `/intake` takes free text, resolves it against
the CRM, verifies what can be verified, and files it — as an activity on the right record, a new
record, a `memory/facts.md` line, or an open question if it cannot be confirmed. It **never**
invents the parts it cannot check.

**M4 · The trigger scan.** The biggest unbuilt piece of the original design. 1,124 records sit at
`nurture` with no reason to write; a trigger is what moves one into the queue. Register diffs
already catch licence and permission changes. What is missing is everything else: senior hires,
fund launches, vendor changes, regulatory deadlines. ⚠ This is the least deterministic thing in the
plan — news is not a register — so it must be built to **propose, never to auto-qualify**, and
every trigger it raises must carry a source URL a human can open.

**M5 · RFP alerts.** BOAMP and PLACE saved searches are free and take ten minutes, but need an
account in Andre's name. Until then the radar re-searches from scratch daily, which is strictly
worse. **Blocked on Andre.**

**M6 · Enrichment beyond registers.** 119 emails of 1,292 records. Register-published contacts are
exhausted; the next tier is LinkedIn (needs a Sales Navigator decision) and firm websites —
which are reachable now, and where a published `contact@` is a legitimate, non-invented route.

### 3.3 The determinism contract, extended

The site build is already deterministic. The **intake** side needs the same discipline, and does
not have it yet:

1. **Every write carries its source and date.** Already true for connectors; must become true for
   `/intake` and the trigger scan.
2. **Every run leaves a record, success or failure** — including the ones that find nothing.
3. **Re-running is safe.** Connectors are idempotent today; `/intake` must be too, or the same
   conference conversation gets filed three times.
4. **Nothing that cannot be verified becomes a fact.** It becomes an open question, with the
   unverified claim quoted rather than paraphrased into apparent certainty.

## 4. Order of work

Ordered by what unblocks the most, not by effort.

| # | Work | Why here |
|---|---|---|
| **1** | **M1 scheduler** | Everything already built is worth nothing on a machine that never runs it. It also starts the run/event history the site needs before `/triggers` and `/runs` can be judged at all. |
| **2** | **M2 REGAFI** | The one large, clean, verified gap. ~936 banks closes France's last empty cell. |
| **3** | **M3 `/intake`** | Stops knowledge dying in chat. Cheap, and it compounds from the first use. |
| **4** | Saudi completeness · UAE onshore · Family Wealth Centre | Three investigations, each may or may not yield a connector. Timeboxed — an unreachable source is a finding, not a failure. |
| **5** | **M4 trigger scan** | Highest ceiling, least deterministic. Deliberately after the plumbing is proven. |
| **6** | M6 enrichment tier two | Partly gated on the Sales Navigator decision. |

**Blocked on Andre, and worth repeating because two of them have been open since day one:**
the off-limits list, the referenceable client names, the Lebanese survivor-track question, the
BOAMP/PLACE alert accounts, and whether anyone can run the Saudi connector from Riyadh.

## 5. What "finished" means

Not "every firm in four markets", which is unachievable and not the point. Finished is:

- **Every market × segment cell either has records or a written reason why it never will.**
- **Every source is either connected, or has a dated note saying why it cannot be.**
- **The engine runs without being asked, and says so when it does not.**
- **Anything Andre learns has a one-command home.**
