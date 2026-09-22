# The sales website — design plan

> Status: **plan, not built.** Written 2026-09-22; stack revised the same day.
> **All three decisions are settled (§10) — this is ready to build.**
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
crm/*.yaml  ──►  tools/site_data.py  ──►  site/public/data/*.json ──►  Vite build  ──►  site/dist/
memory/*.md      (Python owns data)       (the contract)             (React owns UI)    (the site)
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

## 6. Stack — chosen on merit, versions verified

> **Revised twice on 2026-09-22.** First from Astro to React; then again when Andre said to stop
> anchoring on New Gaia and *"take the most recent stack and the best ever"*. The house-stack
> argument is therefore withdrawn — this section stands on merit alone.
>
> **Every version below was checked against the npm registry on 2026-09-22, not recalled.**

### Is this a document site or an application?

An application. Filtering 1,299 rows, sorting, cross-navigating between a firm, its trigger feed and
the register snapshot that proves it. That rules out a content-first framework: Astro's headline
advantages — zero JS, per-route static HTML, cold first paint, SEO — are worth approximately
nothing when one reader opens it from `localhost` on the machine that built it.

### Why React, having considered the alternatives honestly

**Solid 1.x** is faster with finer-grained reactivity, and **Svelte 5**'s runes are arguably the
nicest DX available. Either would build this well. React wins on one specific lever that dominates
here: **the TanStack suite is React-first**, and Table + Virtual is the single biggest determinant
of whether a 1,299-row grid feels instant or sluggish — which is the central UI problem of this
whole project. Add **Radix** (the deepest set of genuinely accessible primitives, which §5.7's
keyboard-first requirement needs) and the ecosystem argument is decisive rather than lazy.

**React Compiler 1.0** also removes React's main historical ergonomic complaint: memoization is
automatic, so no `useMemo`/`useCallback` noise threaded through the code.

### The stack

| Layer | Choice | Version | Why this one |
|---|---|---|---|
| UI | **React** + **React Compiler** | 19.3.0 · 1.0.0 | Compiler is stable — automatic memoization, no manual memo plumbing. |
| Language | **TypeScript** | **7.0.2** | The **native Go compiler** — an order of magnitude faster to typecheck than tsc 5. |
| Build | **Vite** | **8.3.0** | **Rolldown** (Rust) is the bundler now; no separate `rolldown-vite` package needed. |
| Routing | **TanStack Router** | 1.170.38 | Type-safe routes *and* type-safe search params — filter state lives in the URL, so a shared link reproduces a view exactly. |
| Grid | **TanStack Table** + **Virtual** | 9.2.4 · 3.14.13 | Only visible rows mount. The reason the grid stays instant as the CRM grows. |
| Styling | **Tailwind** | 4.3.3 | Oxide engine, CSS-first config, no `tailwind.config.js`. |
| Components | **shadcn/ui** on Radix | — | Copied into the repo, not a dependency — ours to shape, not a library to fight. |
| Icons | **Lucide** | 1.47.0 | One consistent set, tree-shaken. |
| Validation | **Zod** | 4.6.5 | Validates the JSON contract at load; a malformed build fails loudly instead of rendering wrong. |
| Lint + format | **Biome** | 2.5.14 | Rust. Replaces ESLint *and* Prettier with one fast tool and one config. |
| Tests | **Vitest** | 5.0.1 | Same transform pipeline as the build. |
| Packages | **pnpm** | 12.5.1 | Strict — no phantom dependencies. Enabled via `corepack`, which ships with Node, so nothing to install. |

**Deliberately NOT included yet**, because a tool with one reader cannot afford a dependency per
problem:

- **TanStack Query** — there is no server, no cache invalidation and no refetching. `fetch` plus
  React 19's `use()` covers on-demand detail JSON.
- **Motion** (13.4.0) — tasteful transitions are a P4 question, not a foundation.

## 6a. Charts and grids

> Added 2026-09-22 on Andre's instruction: *"we will need graphs and top notch grids for info."*
> That is a requirement, so the earlier "no chart library" line is withdrawn. What follows is a
> choice, not an omission — and deliberately **one** chart library, not two.

### Charts — Recharts, through shadcn/ui's chart components

| Candidate | Version · licence · size | Verdict |
|---|---|---|
| **Recharts** | 3.10.1 · MIT · 7.5 MB | ✅ **Chosen.** It is what **shadcn/ui's chart components are built on**, so charts theme off the *same CSS variables* as every other component. Design-system consistency is precisely what "simple, elegant, clear, pure" demands — a chart that looks like a different product is the failure mode here. |
| **Observable Plot** | 0.6.17 · ISC · 1.5 MB | Smallest and the most concise grammar for analytical charts, with better statistical defaults. Rejected **only** to avoid a second visual language. Reconsider if we hit something Recharts genuinely cannot draw well. |
| **ECharts** | 6.1.0 · Apache-2.0 · **60 MB** | The most capable, and the right answer for very large or highly interactive datasets. Overkill at this scale, and it brings its own theming world. |
| **visx** | 4.0.0 · MIT | Maximum control, most work. Only for a bespoke visual Recharts cannot express. |

⚠ **The markets coverage matrix stays a CSS grid**, not a charting component. A heatmap of
market × segment is a styled table; routing it through a chart library would make it less clear,
not more.

### The charts that actually earn their place

Named up front so this stays a design, not a licence to add charts:

| Visualisation | Answers | Where | Phase |
|---|---|---|---|
| **Contact-route coverage** by market | *What fraction can we actually reach?* | `/` and `/markets` | P1 |
| **Source health sparklines** | *Is each register alive?* A line that flattens and stops is a dead connector — visible at a glance. | `/sources` | P1 |
| **Score distribution** | *Where is the mass?* Are we sitting on a pile of 40s? | `/companies` | P2 |
| **Coverage matrix** (CSS grid) | *Where are we thin?* Gaps render loud. | `/markets` | P2 |
| **Pipeline over time** | *Is this growing or churning?* Built from `Run` records. | `/runs` | P2 |
| **Trigger volume by week** | *Is the engine finding reasons to write, or drifting?* | `/triggers` | P2 |

The first two matter most, and both exist to make a *problem* visible rather than a success:
contact routes are the binding constraint on the whole engine, and a silently dead connector is the
failure mode this workspace has already hit once.

### Grids — TanStack Table + Virtual, kept

| Candidate | Version · licence · size | Verdict |
|---|---|---|
| **TanStack Table + Virtual** | 9.2.4 · 3.14.13 · MIT | ✅ **Kept.** Headless, so the grid is styled by *our* design system and looks like the rest of the app. Virtualised, so only visible rows mount. Column resize, reorder and CSV export are small amounts of code on top. |
| **AG Grid Community** | 36.2.0 · MIT · 21.6 MB | The enterprise gold standard, and genuinely excellent. Rejected because it brings its own visual language that must then be fought back into line with Tailwind and shadcn — and design control is the stated priority. ⚠ Also worth knowing before anyone suggests it later: **row grouping, pivoting and aggregation are AG Grid *Enterprise*, not Community** — the free tier would not give us the features it is usually recommended for. |

**Escape hatch, stated honestly:** if we ever genuinely need pivoting or aggregated grouping, that
is a real reason to revisit AG Grid — and a paid one. Not before.

## 6b. Data loading

Measured, not assumed: full export **3.7 MB**, slim index **307 KB**.

- `index.json` (307 KB) loads at boot → powers the list, search and every filter.
- `companies/<slug>.json` is fetched on demand for a detail view.

Loading all 3.7 MB at once would work fine from disk, but splitting keeps the app honest at ten
times this size — and this CRM grew 22× in a single day.

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
| **P1 — the core loop** | App shell, `/`, `/companies`, `/companies/[slug]`, `/sources`. | The daily loop, end to end, plus the honesty surface. Replaces the current brief. |
| **P2 — memory** | `/triggers`, `/runs`, `/markets`. | This is where R4 becomes visible — the engine's history becomes browsable. |
| **P3 — deal work** | `/pipeline`, `/rfps`, `/questions`, the outreach queue with its `mailto:` links. | Depends on P1's shell; less urgent while the pipeline is young. |
| **P4 — polish** | Keyboard navigation, search refinement, print/mobile, dark mode. | Deliberately last: polish on the wrong structure is wasted. |

Wiring into the daily run (R3) happens at the end of **P1**: `run_all.py` → `site_data.py` →
`npm run build` → commit. One command, no manual step.

## 10. Decisions — settled 2026-09-22

| # | Question | Decision |
|---|---|---|
| 1 | **Stack** | ✅ **React 19.3 + React Compiler · TypeScript 7 · Vite 8 (Rolldown) · TanStack Router/Table/Virtual · Tailwind 4 · shadcn/ui · Zod 4 · Biome 2 · Vitest 5 · pnpm.** Chosen on merit; all versions verified against npm. See §6. |
| 2 | **Where it lives** | ✅ **Local first.** Built to `site/dist/`, served on `localhost`. Nothing leaves the laptop. Remote access stays a separate, deliberate decision. |
| 3 | **Brand** | ✅ **Neutral.** Internal tool, not a client artifact. OFS brand can be applied later without rework. |

## 11. Risks, named honestly

- **Determinism drifts silently.** One `datetime.now()` and R2 is gone. → the double-build test.
- **Two toolchains** (Python + Node) is real complexity. Mitigated by the hard boundary at the JSON
  contract: neither side needs to understand the other.
- **Rendering 1,299 rows.** Not a build-time problem any more — it is a runtime one, and the answer
  is TanStack Virtual so only visible rows mount. It must be *measured* in P1 on the real dataset,
  not assumed. The CRM grew 22× in a day; assume it grows again.
- **Bundle weight creeping.** A React app makes it easy to add a dependency per problem. Every one
  is a tax on a tool with a single reader. The chart-library line in §6 is the standing example:
  add it when there is a chart worth drawing, not before.
- **The site quietly becoming a second source of truth.** The single most damaging failure mode
  available. → nothing is ever authored in `site/`.
- **Scope creep toward a web app.** Andre explicitly does not want to input data. Every form is a
  step toward a product we were not asked for and do not need.
