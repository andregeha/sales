# The sales website — design plan

> Status: **plan, not built.** Written 2026-09-22. Needs three decisions from Andre (§10) before
> any code is written.
>
> This replaces the single generated `crm/reports/brief-*.html` with a real, durable surface over
> everything this workspace knows.

## 1. What it has to be

Andre's brief: *a real website, persistent memory, modern stack, perfect/simple/elegant/clear UI and
UX — "key, key, key". No data entry: he asks me to change things in chat. Every run updates the
data, and the site updates automatically and deterministically.*

Read literally, that gives five hard requirements:

| # | Requirement | What it rules out |
|---|---|---|
| R1 | **Read-only for Andre.** He asks, I edit. | Forms, auth, write APIs, a server that accepts input |
| R2 | **Deterministic.** Same data in → same site out. | Anything time-dependent or randomly ordered in the output |
| R3 | **Automatic.** Every run refreshes it, with no manual step. | A build Andre has to remember to run |
| R4 | **Persistent memory.** It accumulates; it is not a throwaway artifact. | Regenerating "today" and losing yesterday |
| R5 | **UI/UX is the point**, not a wrapper on a data dump. | The current brief, which is a report |

R4 is the one that changes the architecture, and it is the one worth dwelling on. Today the engine
has no memory *of itself*. It knows about companies; it does not know what it did on Tuesday, which
source was dead on Wednesday, or that a firm's score moved on Thursday. Git holds that implicitly
in 38 commits, and `memory/changelog.md` holds it in prose. **Neither is queryable, and neither
survives contact with a question like "what changed in Saudi Arabia this month?"**

## 2. The central decision: the site is DERIVED, never a second source of truth

**YAML in git stays the system of record.** Andre chose it deliberately (`memory/decisions.md`,
2026-09-22): diff-able, auditable, no licence, and agents read and write it natively. Nothing here
changes that.

The site is a **read model** built from it. That gives us determinism for free (R2), keeps the
CRM agent-native, and means the site can be deleted and rebuilt from scratch at any time with
identical output.

```
crm/*.yaml  ──►  tools/site_data.py  ──►  site/src/data/*.json  ──►  Astro build  ──►  site/dist/
memory/*.md      (Python owns data)       (the contract)            (Node owns UI)     (the site)
git history
```

**The boundary is the JSON contract.** Python owns data; Node owns presentation; the two only ever
meet at generated JSON. Practical consequences worth having:

- Agents never touch the website. They write YAML, as they do now.
- The UI can be rebuilt, restyled or replaced without touching the CRM.
- The contract is versioned and testable on its own.
- A broken site can never corrupt a record.

⚠ **The one rule that must not bend: nothing is authored in `site/`.** The moment a fact exists only
in the website, we have two sources of truth and the CRM stops being trustworthy.

## 3. What is missing from the data model today

Three entities the site needs that **do not exist yet**. This is real work, not just rendering.

### 3.1 `Run` — the engine's memory of itself
Every execution should leave a structured record: which connectors ran, what each returned, what
**failed**, what changed, how long it took, which commit it produced.

Today `run_all.py` prints a report to stdout and forgets it. That is why "was the radar actually
looking last Tuesday?" is currently unanswerable — and after today's ADGM bug, where a run reported
a confident `0 created, 412 skipped` while never having looked, **that question is not academic.**

→ `crm/runs/<YYYY-MM-DD-HHMM>.json`, appended, never rewritten.

### 3.2 `SourceHealth` — is each register actually alive?
Derived from run records and snapshots: last successful fetch, entry count, delta, consecutive
failures. This becomes the site's **honesty surface** (§5, `/sources`). A connector that has been
failing for four days must be impossible to miss.

### 3.3 `ChangeEvent` — the trigger feed
The register-change detection built today writes prose into a company's `activities`. That is right
for the record but useless as a feed. The same event should also land as a structured row so
"everything that changed this week, across 1,299 firms" is one query.

→ `crm/events/<YYYY-MM>.jsonl`, append-only.

**All three are append-only.** That is what makes R4 real: the site's memory is not "the current
YAML", it is the accumulated history of runs, events and snapshots. Nothing is ever overwritten,
so nothing is ever lost.

## 4. Information architecture

### Entities
| Entity | Lives in | Notes |
|---|---|---|
| **Company** | `crm/companies/*.yaml` | 1,299. The spine. |
| **Contact** | nested in Company | 937. Never invented. |
| **Activity** | nested in Company | 1,754. The per-firm timeline. |
| **RFP** | `crm/rfps/*.yaml` | Deadline-driven. |
| **Snapshot** | `crm/registers/<reg>/<date>.json` | Evidence. Proves a firm is *newly* licensed, not newly noticed. |
| **Run** 🆕 | `crm/runs/*.json` | What the engine did. |
| **ChangeEvent** 🆕 | `crm/events/*.jsonl` | What moved, across all firms. |
| **SourceHealth** 🆕 | derived | Is each register alive? |
| **Question** | `memory/open-questions.md` | What's blocked on Andre. |

### The ten views

Ordered by how often Andre will use them, which is also the order they should be built.

| Route | Answers | Why it exists |
|---|---|---|
| `/` **Today** | *What needs me now?* | Approvals waiting · what changed since the last run · deadlines inside 14 days · **any source that failed**. Nothing else. If there is nothing, it says so in one line. |
| `/companies` | *Who is in our universe?* | 1,299, searchable and filterable: market, segment, status, score band, **has a contact route**, **has a trigger**. |
| `/companies/[slug]` | *Everything about this firm* | Facts, contacts, the fit reasoning in full, the complete timeline, and a link to the register snapshot that proves it. |
| `/triggers` | *What moved?* | The change feed. New licences, activity changes, woken records — chronological, across every market. |
| `/sources` | *Is the machine actually working?* | Per connector: last success, count, delta, consecutive failures. **The honesty surface.** |
| `/pipeline` | *What is actually live?* | The handful of real deals by stage. Deliberately small. |
| `/rfps` | *What closes soon?* | Soonest first. A missed deadline is the worst thing this workspace can produce. |
| `/markets` | *Where are we thin?* | Market × segment coverage matrix. Gaps are the point, so gaps are visually loud. |
| `/runs` | *What has the engine been doing?* | Run history, each with its full report. |
| `/questions` | *What is blocked on me?* | Open questions by priority, with what each one unblocks. |

Two of these — `/sources` and `/runs` — exist because of what today taught us. A radar that fails
silently is worse than no radar, and the only defence is making failure *visible by default*.

## 5. UI/UX principles

Andre said this three times, so it gets its own section with real rules rather than adjectives.

1. **One question per screen.** `/` answers "what do I do today?" and nothing else. Resist the urge
   to put stats on it.
2. **Typography over chrome.** Hierarchy comes from size, weight and space — not from borders,
   cards-inside-cards, or colour. The current brief's stat strip is exactly the thing to avoid.
3. **Never show a number without its meaning.** "1,299 companies" is noise. "166 with a reason to
   write" is information. Today's brief fix proved this.
4. **Failure is as prominent as success.** A dead connector, a firm with no contact route, a market
   with no coverage — these render loudly, not in grey at the bottom.
5. **Density where it earns its place.** Tables are good; 1,299 rows of cards are not.
6. **Instant.** It is static. No spinners, no skeletons, no loading states — there is nothing to
   load.
7. **Keyboard first.** `/` focuses search, `j`/`k` move, `Enter` opens, `Esc` clears.
8. **Readable on a phone.** He will read `/` on his phone before he opens a laptop.
9. **Light and dark**, following the system. No toggle to maintain.
10. **Every claim traceable.** A score shows its reasoning; a fact shows its source; a register
    entry links to the snapshot that proves it. This is the workspace's constitution applied to UI.

## 6. Stack

**Astro 5 + TypeScript + Tailwind 4.** Node 22.21.1 and npm 10.9.4 are **already installed** on the
laptop, so this adds no new runtime dependency.

| Choice | Why | What was rejected and why |
|---|---|---|
| **Astro** | Content-driven, **ships zero JS by default**, static output, islands only where interactivity is genuinely needed (the company filter). Generates 1,299 static pages happily. | **Next.js** — built for a server we do not want and will not have. **SvelteKit** — fine, but Astro's zero-JS default matches a read-only site better. **Plain HTML from Python** — cannot hit the UI bar he set. |
| **TypeScript** | The JSON contract gets real types; a data-shape change breaks the build instead of the page. | — |
| **Tailwind 4** | Design tokens in one place; no CSS drift across ten views. | Hand-rolled CSS — drifts. Component libraries — heavy, generic, and they *look* like component libraries. |
| **Client-side filtering** | The slim index is **307 KB** (~70 KB gzipped) — small enough to ship and filter in the browser with no server. | A search service — needless infrastructure for one reader. |
| **Python for data** | Agents already write Python; `crm.py` owns the schema. | Rewriting the data layer in Node — pointless churn and a second schema. |

⚠ **Measured, not assumed:** full JSON export is 3.7 MB, so it is **never shipped whole**. The list
view gets the 307 KB slim index; each company's full detail is baked into its own static page.

## 7. The determinism contract

R2 is a promise that has to be enforced, not hoped for.

- `site_data.py` emits JSON with **sorted keys and stable ordering**, and no wall-clock timestamps.
- The single permitted non-deterministic input is the **git commit SHA** the build came from, which
  is recorded explicitly in one place (`build.json`) rather than smeared through the output.
- **Test: build twice, hash both output trees, assert identical.** In the test suite, not in a
  README.
- Because the output is deterministic, `git diff` on the built site is meaningful — you can see
  exactly what a run changed in the UI, which is itself a useful record.

## 8. Privacy and hosting

⚠ **This is commercial pipeline data: 1,299 named firms, 937 contacts, live deal reasoning.**
`CLAUDE.md` forbids creating a public site without Andre's explicit approval, and that rule is
right. The plan assumes **private** unless Andre says otherwise.

| Option | Verdict |
|---|---|
| **Local only** — built to `site/dist/`, served on `localhost` | ✅ **Recommended to start.** Private by construction, zero cost, zero setup, works offline. |
| **Private deploy** (Cloudflare Access / Netlify or Vercel with password) | 🟠 Possible later — but the data leaves the laptop, so it needs Andre's explicit decision. |
| **GitHub Pages** | 🔴 **No.** Pages on a private repo needs a paid plan, and a misconfiguration publishes the whole pipeline. |
| **Public anything** | 🔴 **Never.** |

## 9. Phasing

Each phase is independently useful. Nothing is built that a later phase throws away.

| Phase | What lands | Why this order |
|---|---|---|
| **P0 — the contract** | `site_data.py`, the JSON schema, the `Run`/`ChangeEvent`/`SourceHealth` entities, the determinism test. **No UI.** | Everything depends on it, and it is where the genuinely new work is. It also improves the engine on its own: run records exist whether or not a site is ever built. |
| **P1 — the core loop** | Astro skeleton, `/`, `/companies`, `/companies/[slug]`, `/sources`. | The daily loop, end to end, plus the honesty surface. Replaces the current brief. |
| **P2 — memory** | `/triggers`, `/runs`, `/markets`. | This is where R4 becomes visible — the engine's history becomes browsable. |
| **P3 — deal work** | `/pipeline`, `/rfps`, `/questions`, the outreach queue with its `mailto:` links. | Depends on P1's shell; less urgent while the pipeline is young. |
| **P4 — polish** | Keyboard navigation, search refinement, print/mobile, dark mode. | Deliberately last: polish on the wrong structure is wasted. |

Wiring into the daily run (R3) happens at the end of **P1**: `run_all.py` → `site_data.py` →
`npm run build` → commit. One command, no manual step.

## 10. Decisions needed from Andre

| # | Question | Recommendation |
|---|---|---|
| 1 | **Stack** — Astro + TypeScript + Tailwind, building a static site? | **Yes.** Node is already installed, so the cost is a `node_modules` folder and nothing else. |
| 2 | **Where does it live?** Local-only to start, or do you want it reachable from your phone? | **Local first.** Phone access means the data leaves the laptop and needs a deliberate decision, not a default. |
| 3 | **Brand** — should it use OFS brand (the kit lives in `ofs-marketing`), or stay neutral and functional? | **Neutral to start.** This is an internal tool, not a client artifact; brand can be applied in P4 without rework. |

## 11. Risks, named honestly

- **Determinism drifts silently.** One `datetime.now()` and R2 is gone. → the double-build test.
- **Two toolchains** (Python + Node) is real complexity. Mitigated by the hard boundary at the JSON
  contract: neither side needs to understand the other.
- **Build time at 1,299 pages.** Astro handles this scale, but it must be *measured* in P1, not
  assumed. If it is slow, detail pages can be rendered on demand from the index.
- **The site quietly becoming a second source of truth.** The single most damaging failure mode
  available. → nothing is ever authored in `site/`.
- **Scope creep toward a web app.** Andre explicitly does not want to input data. Every form is a
  step toward a product we were not asked for and do not need.
