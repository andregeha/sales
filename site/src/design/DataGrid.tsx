/**
 * The grid. TanStack Table for behaviour, TanStack Virtual for scale.
 *
 * Only visible rows mount, so 1,299 rows — or 13,000 — stay instant. The CRM grew 22× in a single
 * day, so this is sized for the next order of magnitude rather than for today.
 *
 * `empty` is a REQUIRED prop. A view that says nothing when it has nothing is a bug (plan §5.6),
 * and making it required is how that is prevented structurally rather than by review.
 */
import {
  type ColumnDef,
  columnSizingFeature,
  columnVisibilityFeature,
  createSortedRowModel,
  flexRender,
  type RowData,
  rowSortingFeature,
  type SortingState,
  sortFn_alphanumeric,
  sortFn_basic,
  sortFn_text,
  tableFeatures,
  useTable,
} from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import { ArrowDown, ArrowUp, ChevronsUpDown } from "lucide-react";
import { type ReactNode, useRef, useState } from "react";
import { cn } from "./primitives";

const ROW_HEIGHT = 44;

/**
 * TanStack Table v9 opts INTO features rather than shipping them all, so a grid only pays for what
 * it uses — and the compiler refuses any API belonging to a feature you did not declare.
 *
 * ⚠ `sortedRowModel` and `sortFns` are NOT optional extras. Declaring `rowSortingFeature` alone
 * gives you the sort *API* — `getToggleSortingHandler`, `getIsSorted` — with no row model behind
 * it, so headers render arrows, respond to clicks, update state, and **the rows never move**.
 * That shipped once: five sortable columns, none of which sorted, and it typechecked perfectly.
 * A grid that lies about sorting is worse than a grid without it.
 */
export const GRID_FEATURES = tableFeatures({
  rowSortingFeature,
  columnSizingFeature,
  columnVisibilityFeature,
  sortedRowModel: createSortedRowModel(),
  sortFns: {
    alphanumeric: sortFn_alphanumeric,
    text: sortFn_text,
    basic: sortFn_basic,
  },
});

/** The column type views should use — features are fixed here so callers never spell them out. */
export type GridColumn<T extends RowData> = ColumnDef<typeof GRID_FEATURES, T>;

/**
 * How wide a column is, and how its contents line up.
 *
 * ⚠ Widths are DECLARED, never measured. `table-layout: fixed` means the browser sizes columns from
 * this list and not from the cells — which is the whole point: with `auto`, sorting reordered the
 * rows, different text landed on screen, and every column re-solved. "Why now" swung between 126px
 * and 1,166px as you clicked through sort states. Virtualisation made it worse, because the widths
 * were being solved from the ~30 rows that happened to be mounted.
 *
 * `flex` columns share whatever is left after the fixed ones, so the table always fills its
 * container exactly and never scrolls sideways on desktop.
 */
export type ColumnLayout = {
  /** Fixed pixel width, or `flex` to share the remaining space by weight. */
  width?: number;
  flex?: number;
  align?: "start" | "center" | "end";
};

export function DataGrid<T extends RowData>({
  data,
  columns,
  layout,
  empty,
  onRowClick,
  initialSorting = [],
  maxHeight = "calc(100vh - 20rem)",
}: {
  data: T[];
  columns: GridColumn<T>[];
  /** One entry per column, in order. Required — an undeclared width is how the old bug happened. */
  layout: ColumnLayout[];
  /** Required: what this grid says when it has nothing to show. */
  empty: ReactNode;
  onRowClick?: (row: T) => void;
  initialSorting?: SortingState;
  maxHeight?: string;
}) {
  const [sorting, setSorting] = useState<SortingState>(initialSorting);
  const [scrolled, setScrolled] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // The sticky header should read as pinned, not as a row that got stuck.
  const onScroll = () => setScrolled((scrollRef.current?.scrollTop ?? 0) > 0);

  const table = useTable<typeof GRID_FEATURES, T>({
    features: GRID_FEATURES,
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
  });

  const rows = table.getRowModel().rows;

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => scrollRef.current,
    estimateSize: () => ROW_HEIGHT,
    overscan: 12,
  });

  if (data.length === 0) return <>{empty}</>;

  const items = virtualizer.getVirtualItems();
  const paddingTop = items.length > 0 ? (items[0]?.start ?? 0) : 0;
  const paddingBottom =
    items.length > 0 ? virtualizer.getTotalSize() - (items[items.length - 1]?.end ?? 0) : 0;

  const align = (i: number) => {
    const a = layout[i]?.align ?? "start";
    return a === "center" ? "text-center" : a === "end" ? "text-right" : "text-left";
  };

  return (
    <div className="overflow-hidden rounded-[var(--radius)] border bg-surface">
      <div ref={scrollRef} onScroll={onScroll} className="overflow-auto" style={{ maxHeight }}>
        {/* `table-fixed` + colgroup: widths come from the declaration, never from the cells. */}
        <table className="w-full table-fixed border-collapse text-small">
          <colgroup>
            {layout.map((c, i) => (
              <col
                // biome-ignore lint/suspicious/noArrayIndexKey: columns are positional by definition
                key={i}
                style={
                  c.width !== undefined
                    ? { width: `${c.width}px` }
                    : { width: `${(c.flex ?? 1) * 100}%` }
                }
              />
            ))}
          </colgroup>
          <thead
            className={cn(
              "sticky top-0 z-10 bg-surface-raised",
              scrolled && "shadow-[0_1px_0_0_var(--border-strong)]",
            )}
          >
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((header, i) => {
                  const sortable = header.column.getCanSort();
                  const dir = header.column.getIsSorted();
                  return (
                    <th
                      key={header.id}
                      aria-sort={
                        !sortable
                          ? undefined
                          : dir === "asc"
                            ? "ascending"
                            : dir === "desc"
                              ? "descending"
                              : "none"
                      }
                      className={cn(
                        "border-b px-3 py-2.5 text-micro font-semibold tracking-wide text-muted uppercase",
                        align(i),
                      )}
                    >
                      {sortable ? (
                        <button
                          type="button"
                          onClick={header.column.getToggleSortingHandler()}
                          className={cn(
                            "inline-flex w-full items-center gap-1 hover:text-text",
                            layout[i]?.align === "center" && "justify-center",
                            layout[i]?.align === "end" && "justify-end",
                          )}
                        >
                          <span className="truncate">
                            {flexRender(header.column.columnDef.header, header.getContext())}
                          </span>
                          {dir === "asc" ? (
                            <ArrowUp className="size-3 shrink-0" />
                          ) : dir === "desc" ? (
                            <ArrowDown className="size-3 shrink-0" />
                          ) : (
                            <ChevronsUpDown className="size-3 shrink-0 opacity-25" />
                          )}
                        </button>
                      ) : (
                        flexRender(header.column.columnDef.header, header.getContext())
                      )}
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>
          <tbody>
            {paddingTop > 0 ? (
              <tr aria-hidden>
                <td style={{ height: paddingTop }} colSpan={columns.length} />
              </tr>
            ) : null}
            {items.map((vi) => {
              const row = rows[vi.index];
              if (!row) return null;
              return (
                <tr
                  key={row.id}
                  onClick={onRowClick ? () => onRowClick(row.original) : undefined}
                  className={cn(
                    "border-b last:border-0",
                    onRowClick && "cursor-pointer hover:bg-surface-raised",
                    "data-[selected=true]:bg-accent-weak data-[selected=true]:shadow-[inset_2px_0_0_0_var(--accent)]",
                  )}
                  style={{ height: ROW_HEIGHT }}
                >
                  {row.getVisibleCells().map((cell, i) => (
                    <td key={cell.id} className={cn("overflow-hidden px-3 align-middle", align(i))}>
                      {/* Fixed layout means content must clip — so it clips with an ellipsis and
                          keeps the full value in `title`. Nothing becomes unreadable. */}
                      <div className="truncate" title={plainText(cell.getValue())}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </div>
                    </td>
                  ))}
                </tr>
              );
            })}
            {paddingBottom > 0 ? (
              <tr aria-hidden>
                <td style={{ height: paddingBottom }} colSpan={columns.length} />
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between border-t px-3 py-1.5 text-micro text-subtle">
        <span className="tnum">{rows.length.toLocaleString("en-GB")} rows</span>
        <span className="hidden sm:inline">click a row to open it</span>
      </div>
    </div>
  );
}

/** A cell's value as a tooltip string, when it is something a tooltip can usefully show. */
function plainText(v: unknown): string | undefined {
  if (v === null || v === undefined) return undefined;
  if (typeof v === "string") return v || undefined;
  if (typeof v === "number" || typeof v === "boolean") return String(v);
  return undefined;
}

/**
 * A small static table for a handful of rows, where virtualisation would be silly.
 *
 * ⚠ Takes the same `layout` as `DataGrid`, and for the same reason. Without declared widths the
 * table is auto-laid-out, and one long cell wins: on Today a "Why now" span rendered 1,651px wide
 * inside a 1,425px viewport, because `truncate` on the cell cannot constrain a column that the
 * table is free to widen. Declared widths make truncation actually truncate.
 */
export function DataTable({
  head,
  layout,
  children,
}: {
  head: ReactNode[];
  /** One entry per column, in order. Omit only for tables of short, predictable values. */
  layout?: ColumnLayout[];
  children: ReactNode;
}) {
  const fixed = layout !== undefined;
  return (
    <div className="overflow-hidden rounded-[var(--radius)] border bg-surface">
      <table className={cn("w-full border-collapse text-small", fixed && "table-fixed")}>
        {layout ? (
          <colgroup>
            {layout.map((c, i) => (
              <col
                // biome-ignore lint/suspicious/noArrayIndexKey: columns are positional by definition
                key={i}
                style={
                  c.width !== undefined
                    ? { width: `${c.width}px` }
                    : { width: `${(c.flex ?? 1) * 100}%` }
                }
              />
            ))}
          </colgroup>
        ) : null}
        <thead className="bg-surface-raised">
          <tr>
            {head.map((h, i) => (
              <th
                // biome-ignore lint/suspicious/noArrayIndexKey: static header cells
                key={i}
                className={cn(
                  "border-b px-3 py-2 text-micro font-semibold tracking-wide text-muted uppercase",
                  layout?.[i]?.align === "center"
                    ? "text-center"
                    : layout?.[i]?.align === "end"
                      ? "text-right"
                      : "text-left",
                )}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

export function Td({
  children,
  className,
  truncate,
  title,
}: {
  children?: ReactNode;
  className?: string;
  /** Clip to one line with an ellipsis. Needs the table to have a `layout`. */
  truncate?: boolean;
  title?: string;
}) {
  return (
    <td className={cn("border-b px-3 py-2 align-middle", truncate && "overflow-hidden", className)}>
      {truncate ? (
        <div className="truncate" title={title}>
          {children}
        </div>
      ) : (
        children
      )}
    </td>
  );
}

export function Tr({ children, onClick }: { children: ReactNode; onClick?: () => void }) {
  return (
    <tr
      onClick={onClick}
      className={cn("last:[&>td]:border-0", onClick && "cursor-pointer hover:bg-surface-raised")}
    >
      {children}
    </tr>
  );
}
