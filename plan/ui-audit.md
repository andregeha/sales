# UI/UX audit — method

> Written 2026-09-22 before running it, so the findings are the product of a method rather than of
> whatever happened to catch my eye. Findings land in §B; the remediation plan is
> `plan/ui-upgrade.md`.

## A. What gets tested, and how

Every check below is **observed**, not reasoned about. A claim like "it works on mobile" that has not
been rendered at 375px does not go in the findings.

### A1. Routes — all ten
For each: `/`, `/companies`, `/companies/:slug`, `/triggers`, `/pipeline`, `/rfps`, `/markets`,
`/sources`, `/runs`, `/questions`.

| Check | Pass condition |
|---|---|
| Renders with real data | No blank, no error, no `undefined` in the DOM |
| **Empty state** | Says what is empty *and why that might be legitimate* |
| **Error state** | Names the failure and the fix, not a stack trace |
| First screen earns itself | The top 600px answers the page's stated question |
| Lede matches reality | The one-line promise in `PageHeader` is actually what the page does |

### A2. Responsive — 375 / 768 / 1440
The claim in `plan/website.md` §5.8 is "readable on a phone". That is tested, not assumed.
- No horizontal page scroll at any width (a grid may scroll inside its own container).
- Data visible in the first screen — controls must not push content below the fold.
- Nav reachable without horizontal scrolling.

### A3. Theme — light and dark
Every route in both. Watching specifically for: contrast on badges and weak backgrounds, chart
axes and gridlines, and anything that only got checked in light.

### A4. Components, in situ
`Stat` · `Callout` · `EmptyState` · `ErrorState` · `Field` · `Unknown` · `Button` · `Panel` ·
`Section` · `PageHeader` · `SourceLink` · `Prose` · `Kbd` · and every domain component
(`StatusBadge`, `ScoreBadge`, `SegmentTag`, `MarketTag`, `ContactRoute`, `TriggerLine`,
`SourceHealth`, `Mono`).
For each: is it used consistently, is it used *anywhere*, and does anything bypass it?

### A5. Grid
Sorting (every sortable column, both directions) · virtualisation under 1,298 rows ·
horizontal overflow · row click · sticky header · the row-count footer · keyboard reachability.

### A6. Filters
Chips (single, combined, toggle off) · text search across the fields it claims · `clear` ·
whether filter state survives navigation · whether an impossible combination explains itself.

### A7. Charts
Axis labels and units · tooltip legibility · dark mode · behaviour with 0 and 1 data points ·
whether the caption says something the chart cannot.

### A8. Icons
One set, one weight, one size scale · every icon semantic rather than decorative ·
no icon carrying meaning that the text does not also carry.

### A9. Typography and density
Heading hierarchy actually distinguishable · line length under ~75ch for prose ·
truncation that never hides the only copy of a fact · tabular numerals wherever numbers align.

### A10. Accessibility
Visible focus ring on every interactive element · keyboard reachability · the `/` and `j/k`
bindings the plan promises · contrast of muted/subtle text · `aria` on icon-only controls ·
`prefers-reduced-motion`.

### A11. Forms
There are none by design (R1 — Andre asks, I edit). **The audit confirms none exist**, and treats a
form as a finding.

### A12. Performance
Bundle size and what is in it · time to interactive with 1,298 rows · whether a route with no chart
still pays for the chart library.

## B. Findings

Recorded in `plan/ui-upgrade.md`, each with severity:

- 🔴 **Wrong** — states something untrue, or the page cannot do its job.
- 🟠 **Weak** — works, but costs the reader time or trust.
- ⚪ **Polish** — real, not urgent.

Every finding carries the observation that produced it. "Feels cluttered" is not a finding;
"five rows of filter chips before the first record at 375px" is.
