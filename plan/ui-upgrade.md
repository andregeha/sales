# UI/UX findings and upgrade plan

> Produced by running `plan/ui-audit.md` against the live site on 2026-09-22, at 375/1440, light and
> dark, on real data (1,298 companies, 4 sources, 1 run).
>
> Every finding below carries the **observation** that produced it. Nothing here is "feels cluttered".

## The findings

### 🔴 Wrong — states something untrue, or the page cannot do its job

**F1 · Grid sorting is completely broken.**
Observed: clicking `Company` gives `1 2 3 INVESTMENT MANAGERS` ascending, descending, and after
clicking `Fit`. `initialSorting: [{id:"score", desc:true}]` is ignored — the list renders in raw
index order. Five columns display sort arrows and none of them sort.
Cause: `rowModels: { sortedRowModel: createSortedRowModel() }` was removed from `useTable` to make
the file typecheck against TanStack Table v9, and sorting was never re-verified afterwards.
**Why it is the worst finding here:** it is the exact failure this workspace keeps warning about —
an affordance that looks like it works, silently doing nothing. A grid that lies about sorting is
worse than a grid with no sorting.

**F2 · Filter state does not survive navigation, but the code says it does.**
Observed: filter to France + has-a-trigger (42 records), navigate to `/markets`, return — back to
1,298 with the chips cleared.
`Companies.tsx` states *"Filter state lives in the URL hash, so a view can be shared or bookmarked
and reproduces exactly."* It is `useState`. The comment is false and the plan repeats the claim.

**F3 · The promised keyboard navigation does not exist.**
`plan/website.md` §5.7 states "keyboard first: `/` focuses search, `j`/`k` move, `Enter` opens,
`Esc` clears". None is wired. The `Kbd` component built to document it is unused — the only unused
component in the system besides `AreaSeries`.

**F4 · The score is presented as a ranking signal, and it does not rank.**
Observed: 487 records in 50–59 and 648 in 60–69 — **88% of 1,297 records in two adjacent bands**.
21 score ≥80. The UI sorts by it, badges it on every row, and leads Today with it.
Cause is upstream of the UI: register-sourced records all earn identical fit points. The site
cannot fix the model, but it must stop implying a precision the number does not have.

### 🟠 Weak — works, but costs the reader time or trust

**F5 · On mobile, `/companies` is two-thirds chrome.**
Observed at 375×812: the first data row sits at **y=537**. Twenty-plus filter chips, always
expanded, across five rows. The page's job is to show firms; it shows controls.

**F6 · One 843 KB chunk, no code splitting.**
Observed: `dist/assets/index-*.js` is a single file; Recharts appears 75 times in it. Today and
Companies pay for the charting library, and `/questions` pays for all of it.

**F7 · The grid does not adapt to narrow screens.**
Observed: the table is 1,177 px wide inside a 375 px viewport. It scrolls inside its container
(correct — no page overflow) but every column beyond `Company` is off-screen on a phone.

**F8 · Sortable headers carry no `aria-sort`.**
Observed: every `<th>` returns `null`. Compounds F1 — once sorting works, assistive tech still
cannot report its state.

**F9 · "Why now" is truncated on Today to ~34 characters** with no tooltip and no way to read the
rest without leaving the page. It is the column the page exists to show.

**F10 · Zod ships to the browser** (313 references). We generate this JSON ourselves and already
validate it in `tools/test_site_data.py`. Paying to re-validate it in the client on every load is
weight for a guarantee we already hold.

### ⚪ Polish

**F11 · Navigation is nine flat items.** Today and Companies are daily; Runs and Questions are
occasional. They are weighted identically, and on mobile the bar scrolls horizontally.

**F12 · On a company page, "Why now" has the least visual weight of anything on the screen** — a
bare line in a panel, below a wall of scoring prose.

**F13 · No link from a company to the register snapshot that proves it**, which `plan/website.md` §4
explicitly promises ("a link to the register snapshot that proves it").

---

## The upgrade plan

Ordered by consequence, not by effort.

### U1 — Make the grid tell the truth *(fixes F1, F8)*
- Restore the sorted row model with the correct v9 wiring, and **prove it with a test that asserts
  order actually changes** — not a typecheck.
- Add `aria-sort` to every sortable header.
- Verify `initialSorting` takes effect on first paint.

### U2 — Stop overstating the score *(fixes F4)*
The model is Andre's call; the UI's job is not to imply precision it lacks.
- `ScoreBadge` gains a band label, so 63 reads as *"strong fit"* rather than as a rank.
- `/companies` sorts by **trigger first, then score** — a firm with a reason to write outranks a
  firm with a marginally higher number.
- `/markets` states the plateau in words above the chart, rather than leaving the reader to spot it.

### U3 — Make filter state real *(fixes F2)*
Serialise filters into the hash (`#/companies?country=France&trigger=1`), read them back on mount.
Then the code comment becomes true and a filtered view is shareable.

### U4 — Give mobile its first screen back *(fixes F5, F7)*
- Collapse the chip rows behind a `Filters` disclosure below `md`, showing only active ones.
- Below `md` the grid drops to two columns — company (with market and segment stacked beneath) and
  fit — with the rest on the detail page. Column visibility is already a declared v9 feature.

### U5 — Split the bundle *(fixes F6, F10)*
- `React.lazy` the chart-bearing routes so Recharts loads only when a chart does.
- Drop Zod from the client. Keep the shapes as TypeScript types; the build already validates the
  data, and a second validation in the browser buys nothing.
- Target: first-load JS under 300 KB.

### U6 — Build the keyboard layer *(fixes F3, and uses `Kbd`)*
`/` focuses search · `j`/`k` move the grid selection · `Enter` opens · `Esc` clears · `g` then
`t`/`c`/`s` jump to Today/Companies/Sources. A one-line hint in the footer using the `Kbd`
component that currently has no purpose.

### U7 — Fix the hierarchy on a company page *(fixes F12, F13)*
Promote "why now" to directly under the title, at heading weight. Demote the scoring prose to a
disclosure. Add the register-snapshot link the plan promised.

### U8 — Group the navigation *(fixes F11)*
Two groups: **the work** (Today · Companies · Triggers · Pipeline · RFPs) and **the machine**
(Markets · Sources · Runs · Questions). Separated visually, not by a menu.

### What is deliberately NOT changing
- **No forms.** A12 confirmed there are none, and that stays true (R1).
- **No new dependency.** Every fix above uses what is already installed.
- **The coverage matrix stays a CSS grid.** It reads correctly; a chart library would make it worse.
