# Source architecture — how we stop missing things

> Written 2026-09-23 after Andre pushed back: *"be smart, not rely only on public sources... find a
> solution to have an exhaustive list and never miss a potential prospect or potential RFP."*
>
> Every source below was **probed today**, with counts. Scheduling is deliberately deferred until
> connectivity is complete.

## 1. Why registers alone were never going to be enough

The four connectors answer one question: **who is licensed?** That is a good question, and it built
1,227 of our 1,292 records. But it structurally cannot find:

- **Family offices**, which are usually *not licensed at all* — the single-family office is exempt
  almost everywhere. That is exactly why UAE family offices = 0 and France family offices = 0.
  ⚠ Those zeros are not a sourcing failure; they are a **wrong-instrument** failure.
- **Holding companies and investment offices** that manage real money under a corporate wrapper.
- **Firms about to be licensed** — incorporated, staffing up, not yet on a register.
- **RFPs in three of our four markets**, where the local portal is blocked, absent, or invitation-only.

**A licence register is a filter, not a census.** The fix is not a better register — it is more
kinds of source, and a way to notice when they disagree.

## 2. What I found today, with numbers

### Tier 1 — Licence registers (who is *regulated*) · built
| Source | Records | Status |
|---|---|---|
| AMF France | 666 | ✅ live |
| FSRA ADGM | 497 | ✅ live |
| DFSA DIFC | 319 | ✅ live |
| CMA Saudi | 36 of 242 | 🔴 partial, API geo-blocked |

### Tier 2 — Company registries (who *exists*, by industry) · **the missing layer**
| Source | What it gives | Verified today |
|---|---|---|
| **`recherche-entreprises.api.gouv.fr`** | **Every French company, filtered by NAF industry code. No API key.** | ✅ 200 |
| **REGAFI** (`acpr.opendatasoft.com`) | French credit institutions + investment firms | ✅ 936 + 1,002 |

French counts by NAF code, measured:

| NAF | Meaning | Count | Why it matters |
|---|---|---|---|
| `64.19Z` | Autres intermédiations monétaires | **6,938** | banks — our empty France×bank cell |
| `66.12Z` | Courtage de valeurs mobilières | **3,048** | brokers |
| `66.30Z` | Gestion de fonds | 10,000+ | fund managers, incl. **unregulated** ones the AMF list misses |
| `64.20Z` | Sociétés holding | 10,000+ | **where family offices hide** |
| `70.10Z` | Activités des sièges sociaux | 10,000+ | ditto |
| `64.30Z` | Fonds de placement | 10,000+ | funds |

⚠ **10,000 is an API cap, not a count** — several codes return exactly 10,000. Sliced by
département it goes under the cap. And ⚠ **these codes are self-declared and noisy**: `64.20Z`
contains every holding company in France, most of which are not family offices. This tier
**proposes candidates; it does not produce records.**

### Tier 3 — Global identity graph (who is *connected to whom*)
**GLEIF LEI** — free, no auth, global. Measured: FR 19,464 funds / 170,615 entities · AE 131 / 9,100 ·
SA 16 / 5,647 · LB 1 / 282.

⚠ **GLEIF has no industry classification**, so it cannot source prospects directly. Its real value
is two things registers cannot give:
1. **Enrichment** — LEI, legal address, legal form for firms we already hold.
2. **Fund → manager relationships.** A fund's LEI record points at its managing entity. 19,464
   French funds is a path to managers who never appear on a licence list under their own name.

### Tier 4 — RFPs beyond the local portals
Local portals cover one market of four: TED/BOAMP/PLACE work for France; Etimad blocks automation;
UAE portals are JS apps. **The addressable public flow in the Gulf and Lebanon is multilateral.**

| Source | Verified | Why it is relevant to us |
|---|---|---|
| **World Bank eProcure** | ✅ 200 | funds public-financial-management and capital-markets modernisation |
| **UNGM** | ✅ 200 | UN-system procurement across all four markets |
| **EBRD procurement** | ✅ 200 | financial-institution lending and modernisation |
| IsDB | 🟠 site up, procurement path not found | **Jeddah-based**, lends across exactly our markets |

### Confirmed *not* available — recorded so nobody re-hunts them
- **ADGM company registrar** — only `/public-registers/fsra` and a professional-services directory.
- **DIFC public register** — rate-limited me repeatedly today (429); needs a slower retry.
- **Lebanon** — no public register of banks or managers.
- **AFFO** — publishes no member directory, by design.

## 3. The idea that actually answers "never miss"

No single source is exhaustive, and any plan that promises one is lying. But **sources disagree in
useful ways**, and that disagreement is machine-detectable.

> **Cross-source reconciliation:** a firm that appears in one source and not another is either a
> gap in our CRM or a fact about the firm. Both are worth knowing, and neither requires a human to
> notice it.

Three reconciliations worth running, in order of yield:

1. **Register ↔ company registry.** A firm with NAF `66.30Z` that is *not* on the AMF list is
   either unregulated (interesting — it may be a family office or a ManCo-in-waiting) or newly
   licensed and not yet published. Both are leads.
2. **GLEIF ↔ CRM.** A fund whose managing entity is not in our CRM is a manager we have missed.
3. **CRM ↔ CRM.** A firm on a register that has *vanished* — already built, and already reported.

**This is what makes "never miss" a process rather than a promise.** It also degrades honestly: the
reconciliation can only ever say "these two sources disagree", never "this list is complete".

⚠ And it must **propose, not create**. Tier 2 and 3 are noisy; auto-creating from them would refill
the CRM with the 22,280 *Agent PSP* problem in a different costume. Candidates land in a review
queue with their evidence, and only a scored, segmented candidate becomes a record.

## 4. What gets built, in order

| # | Build | Closes |
|---|---|---|
| **C1** | ✅ **`regafi_france.py`** — ACPR credit institutions + investment firms | France × bank = 0 → ~936 |
| **C2** | ✅ **`sirene_france.py`** — NAF-filtered French company registry, sliced by département to beat the 10k cap, **into a candidate queue not the CRM** | France family offices, unregulated managers |
| **C3** | ✅ **`gleif_enrich.py`** — LEI, legal form, address onto existing records; fund→manager relationships as candidates | Enrichment + managers we never saw |
| **C4** | ✅ **Coverage view** (`/coverage`) — every market × segment names its instrument or states why none exists; **the build fails if a cell does neither** | "never miss", operationally |
| **C5** | ✅ **`multilateral_rfp.py`** — World Bank · UNGM · EBRD, filtered to our four markets and to financial-systems scope | RFP coverage in Saudi, UAE, Lebanon |
| **C6** | Investigations, timeboxed: Saudi completeness · UAE onshore CMA · DIFC register (slow retry) · IsDB path | Known unknowns |

Scheduling comes **after** C1–C5, per Andre. The connectors are worth nothing unscheduled, but an
unscheduled connector that works beats a scheduled one that does not exist.

## 5. What "exhaustive" honestly means

It does not mean every firm. It means:

- **Every market × segment cell is fed by at least one source, or has a written reason why none exists.**
- **Two independent sources are reconciled**, so a miss in one is visible from the other.
- **Every candidate carries its evidence**, so a human decision is cheap.
- **The gaps are named**, dated, and revisited — not quietly tolerated.

Lebanon will still be relationship-driven. Invitation-only RFPs will still be invisible. Saying so
plainly is what makes the rest of the number trustworthy.

## 6. Where C1–C5 actually landed (2026-09-23)

Built and live: REGAFI (France × bank 0 → 213) · SIRENE (300 candidates) · GLEIF (969 of 1,610
records matched; 17 fund-manager candidates including SNB Capital and Jadwa) · the multilateral RFP
radar (World Bank, UNGM, IsDB readable; EBRD refused, loudly) · the coverage view · `/intake`.

**What the coverage view says, and it is the honest headline:** of 20 market × segment cells,
**7 have no instrument at all**, and those cells hold **19 records that nothing maintains** — they
cannot be refreshed, so a firm that closed would go on looking current indefinitely. The four worth
naming: UAE × family office (DIFC moved SFOs to a centre that publishes nothing), Saudi × bank (we
read no SAMA source), Saudi × family office, and all of Lebanon.

That is the real answer to "never miss": not a promise of completeness, but a page that says
exactly where we are blind, that fails the build if someone forgets to explain a blind spot, and
that distinguishes a market we looked at from a market we never had a way to look at.
