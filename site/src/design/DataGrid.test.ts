/**
 * Guards the bug that shipped: a grid whose headers sorted nothing.
 *
 * `rowSortingFeature` alone gives you the sorting *API* — `getToggleSortingHandler`, `getIsSorted`,
 * arrows that respond to clicks and update state — with **no row model behind it**. The rows never
 * move. It typechecks, it renders, it looks correct, and it is a lie. That is exactly what shipped:
 * five sortable columns, none of which sorted.
 *
 * ⚠ What this file does and does not cover, stated honestly:
 *  - It DOES assert the two things whose absence caused the bug: the sorted row model and the sort
 *    functions being registered on the feature set. Removing either to make the file typecheck —
 *    the precise thing that happened — fails here.
 *  - It DOES assert the sort functions order values correctly, including numerically rather than
 *    lexically.
 *  - It does NOT drive a real table: `constructTable` needs the React adapter's atom wiring, and
 *    mounting one would mean adding jsdom and a testing library for a single assertion. End-to-end
 *    sorting was verified in the browser instead (ascending, descending, `aria-sort`, and
 *    `initialSorting` taking effect on first paint).
 */
import { sortFn_alphanumeric, sortFn_basic, sortFn_text } from "@tanstack/react-table";
import { describe, expect, it } from "vitest";
import { GRID_FEATURES } from "./DataGrid";

describe("DataGrid feature set", () => {
  it("declares a sorted row model — without one, every header sorts nothing", () => {
    expect(GRID_FEATURES).toHaveProperty("sortedRowModel");
    expect(typeof (GRID_FEATURES as { sortedRowModel?: unknown }).sortedRowModel).toBe("function");
  });

  it("declares the sorting feature itself", () => {
    expect(GRID_FEATURES).toHaveProperty("rowSortingFeature");
  });

  it("registers the sort functions the columns rely on", () => {
    const fns = (GRID_FEATURES as { sortFns?: Record<string, unknown> }).sortFns ?? {};
    expect(Object.keys(fns).sort()).toEqual(["alphanumeric", "basic", "text"]);
  });

  it("declares column sizing and visibility, which the grid's markup calls", () => {
    // `getSize()` and `getVisibleCells()` throw at runtime if their features are not declared.
    expect(GRID_FEATURES).toHaveProperty("columnSizingFeature");
    expect(GRID_FEATURES).toHaveProperty("columnVisibilityFeature");
  });
});

describe("sort functions order correctly", () => {
  const cmp = (fn: (a: unknown, b: unknown, id: string) => number, values: unknown[]) =>
    [...values].sort((a, b) =>
      fn({ getValue: () => a } as never, { getValue: () => b } as never, "x"),
    );

  it("sorts text alphabetically", () => {
    expect(cmp(sortFn_text as never, ["Zeta", "Alpha", "Mid"])).toEqual(["Alpha", "Mid", "Zeta"]);
  });

  it("sorts numbers numerically, not lexically — 90 must beat 100 only if 90 < 100 is respected", () => {
    // Lexical ordering would put "100" before "90". This is the trap the Fit column would hit.
    expect(cmp(sortFn_basic as never, [90, 100, 10])).toEqual([10, 90, 100]);
  });

  it("sorts alphanumeric values with embedded numbers sensibly", () => {
    expect(cmp(sortFn_alphanumeric as never, ["Fund 10", "Fund 2", "Fund 1"])).toEqual([
      "Fund 1",
      "Fund 2",
      "Fund 10",
    ]);
  });
});
