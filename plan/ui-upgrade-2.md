# UI upgrade, round two — the grid

> Andre: *"Grid still looks bad, in sorting width changes."* He is right, and the measurement is
> worse than the complaint. Round one fixed what sorting *did*; it did not fix what sorting *looked
> like*.

## What was measured

Companies grid, desktop, 1,298 rows:

| Observation | Value |
|---|---|
| "Why now" column width, sorting through four states | **1166 → 126 → 474 → 1166 px** |
| "Company" column across the same | 264 → 255 → 299 → 264 px |
| Table width vs its container | **1,881 px inside 871 px** |
| `table-layout` | `auto` |
| Header/body column alignment | aligned ✓ |
| Sticky header | working ✓ |
| Cells clipping their content | 0 of 40 sampled |

## Root cause — one bug, two symptoms

`table-layout: auto` sizes every column from the **content currently rendered**. Two consequences,
and they are the whole complaint:

1. **Sorting reorders rows → different text is on screen → the browser re-solves every column.**
   The layout visibly jumps on every sort. Nothing is wrong with the sort; the table is measuring
   itself against whatever happens to be visible.
2. **Virtualisation makes it worse.** Only ~30 of 1,298 rows exist in the DOM, so the widths are
   solved from a *sample* — and the sample changes as you scroll.
3. The same auto-sizing lets "Why now" claim 1,166 px, pushing the table to 1,881 px inside an
   871 px container. The grid horizontally scrolls **on desktop**, which is the "looks bad".

The explicit `size` values in the column definitions were being ignored: they were applied only
when `getSize() !== 150`, a guard written for a v8 default that v9 does not share.

## The fix

**G1 · `table-layout: fixed`, widths declared in a `<colgroup>`.**
Widths then depend on the declaration, never on the content. Sorting and scrolling cannot move a
column, because the browser is no longer measuring cells.

**G2 · Widths that sum to the container.**
One flexible column (Company), one that takes the remaining space (Why now), everything else fixed.
`width: 100%` on the table plus fixed layout means it fits exactly at any container width — no
horizontal scroll on desktop, and the narrow layout keeps its three columns.

**G3 · Truncate, and never lose the text.**
Fixed layout means content must clip. Every cell truncates with an ellipsis **and carries the full
value in `title`**, so nothing becomes unreadable — which matters most for "Why now", the column
the page exists to show.

**G4 · Alignment belongs to the column, not the cell.**
`align: "start" | "center" | "end"` on the column definition, applied to header and body together,
so a numeric column is aligned consistently instead of inheriting `start` by accident. Fit and
Reach become centred; numbers keep tabular figures.

**G5 · Density that holds.**
One row height, declared once, matching the virtualiser's estimate — a mismatch there makes
scrolling drift. Comfortable padding, a clearer header, and a shadow under the sticky header once
the body scrolls, so the header reads as pinned rather than as a stuck row.

## Not changing

- The three-column narrow layout — measured good (377 px against a 375 px viewport).
- The simple `DataTable` used on Today, Runs and Questions — measured, fits its container, and its
  variable row heights are correct for prose.
- Virtualisation — working, and the reason the grid stays usable at this size.

## How this gets verified

Not by looking at it. By measuring, as above:
1. Column widths **identical** before, during and after sorting every sortable column.
2. Column widths identical after scrolling 4,000 px.
3. Table width ≤ container width at 1440, 768 and 375.
4. Row heights all equal to the declared constant.
5. Header and body columns still aligned.
