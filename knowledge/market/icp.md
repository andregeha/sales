# Ideal Customer Profile & scoring

> Who we chase, who we skip, and how a lead gets a number. Used by `tools/crm.py` (the `fit.score`
> field) and by every agent doing lead sourcing. Set 2026-09-22.

## Territory
**Markets:** UAE · Saudi Arabia · Lebanon · France.
**Segments:** family offices & MFOs · private and investment banks · asset & fund managers.
Anything outside this is not a lead unless Andre says otherwise — record it as `nurture`, not as
pipeline, and move on.

## The profile in one paragraph
A **regulated or family-capital investment firm managing other people's money across several asset
classes**, big enough that spreadsheets have stopped working and an auditor is asking questions, but
not so big that it has already signed a tier-one platform it cannot leave. It has a **compliance
obligation it must demonstrably meet**, **clients who expect to see their positions**, and **no
appetite for a two-year implementation**. It wants front-to-back in one system, from a vendor whose
people answer the phone and understand finance.

## Scoring — 0 to 100
Score every company. The number drives the work queue; the **reasoning is what matters** and must
always be written alongside it.

### Fit (max 60)
| Signal | Points |
|---|---|
| Segment is a priority one (family office/MFO, private or investment bank, asset/fund manager) | 20 |
| Segment is adjacent (broker, insurer, custodian, sovereign/public fund) | 10 |
| In a priority market (UAE, KSA, Lebanon, France) | 15 |
| Multi-asset — beyond a single asset class | 10 |
| Manages money for **third parties** (not purely proprietary) | 10 |
| Regulated by a named regulator (a real compliance obligation, not a nice-to-have) | 5 |

### Timing / trigger (max 25)
| Signal | Points |
|---|---|
| A **published RFP or tender** we can bid on | 25 |
| New licence granted, new entity, or a spin-out | 20 |
| Fund launch, new mandate type, or entering a new asset class | 15 |
| New COO / CIO / Head of Operations / Head of Compliance hired | 12 |
| Known incumbent system being retired, or its vendor acquired/exiting | 15 |
| Regulatory change creating reporting or compliance pressure | 10 |
| Visible growth — AUM, headcount, new office | 8 |
| No trigger identified | 0 |

### Access (max 15)
| Signal | Points |
|---|---|
| Warm route in — existing relationship, mutual contact, referral | 15 |
| A named, reachable decision-maker identified | 8 |
| Only a generic company contact | 3 |
| No route in at all | 0 |

### Bands
| Score | Meaning | What happens |
|---|---|---|
| **80–100** | Work it now | Research, draft outreach this week |
| **60–79** | Strong | Into the active queue |
| **40–59** | Worth a look | Research further before spending outreach effort |
| **20–39** | Nurture | Watch for a trigger; no outreach yet |
| **< 20** | Skip | Record it and the reason, so we do not re-find it next month |

⚠ **A high score is not permission to contact.** Without a real reason to write to *this* firm
*now*, the outreach is not ready — see the outreach rules in `CLAUDE.md`.

## Disqualify honestly
- Outside the four markets, with no expansion into them.
- Purely proprietary trading with no third-party money and no compliance driver.
- Too small to need a system — one portfolio, one person, one asset class.
- Already mid-implementation of a competitor, with no dissatisfaction signal.
- A retail brokerage or neobank wanting a consumer product, not a management platform.
- No reachable human, after genuine effort.

Record the reason in `fit.disqualified_reason`. **The reason is the point** — it stops us burning
the same hour on the same firm in three months.

## Signals that make a lead hot
A **published tender** · a **new licence** · a **fund launch** · a **senior ops or compliance hire** ·
an **incumbent vendor being acquired or sunset** · a **regulatory deadline** · a **family office
professionalising** (first CIO, first external mandate, first consolidated reporting requirement) ·
a **bank spinning out** its wealth or asset-management arm.

## What we lead with, by segment
| Segment | Open with | Proof asset |
|---|---|---|
| Family office / MFO | Consolidation across custodians and currencies; one login for the whole book; private equity and repos alongside listed assets | **Live portal demo** |
| Private / investment bank | Pre-trade compliance enforcement, audit trail, core-banking integration, branches on the portal | Compliance engine + regulatory pack |
| Asset / fund manager | NAV per share class, subscriptions/redemptions, shareholder registry, management **and performance** fees | Fund administration walkthrough |
| Lebanon, any segment | The **ready-made CMA/BDL regulatory pack** — little to build | Regulatory pack |
| Anyone on an ageing system | Front-to-back in one database, modular pricing, and a re-platform that needs no data migration | New Gaia continuity story |
