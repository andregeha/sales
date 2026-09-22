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
  flexRender,
  type RowData,
  rowSortingFeature,
  type SortingState,
  type TableFeatures,
  useTable,
} from "@tanstack/react-table";
import { useVirtualizer } from "@tanstack/react-virtual";
import { ArrowDown, ArrowUp, ChevronsUpDown } from "lucide-react";
import { type ReactNode, useRef, useState } from "react";
import { cn } from "./primitives";

const ROW_HEIGHT = 44;

/**
 * TanStack Table v9 opts INTO features rather than shipping them all, so a grid only pays for what
 * it uses — and the compiler refuses any API belonging to a feature you did not declare. These
 * three are exactly what this grid calls: sorting, column widths, visible cells.
 */
const FEATURES = {
  rowSortingFeature,
  columnSizingFeature,
  columnVisibilityFeature,
} satisfies TableFeatures;

/** The column type views should use — features are fixed here so callers never spell them out. */
export type GridColumn<T extends RowData> = ColumnDef<typeof FEATURES, T>;

export function DataGrid<T extends RowData>({
  data,
  columns,
  empty,
  onRowClick,
  initialSorting = [],
  maxHeight = "calc(100vh - 20rem)",
}: {
  data: T[];
  columns: GridColumn<T>[];
  /** Required: what this grid says when it has nothing to show. */
  empty: ReactNode;
  onRowClick?: (row: T) => void;
  initialSorting?: SortingState;
  maxHeight?: string;
}) {
  const [sorting, setSorting] = useState<SortingState>(initialSorting);
  const scrollRef = useRef<HTMLDivElement>(null);

  const table = useTable<typeof FEATURES, T>({
    features: FEATURES,
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

  return (
    <div className="overflow-hidden rounded-[var(--radius)] border bg-surface">
      <div ref={scrollRef} className="overflow-auto" style={{ maxHeight }}>
        <table className="w-full border-collapse text-small">
          <thead className="sticky top-0 z-10 bg-surface-raised">
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((header) => {
                  const sortable = header.column.getCanSort();
                  const dir = header.column.getIsSorted();
                  return (
                    <th
                      key={header.id}
                      style={{ width: header.getSize() === 150 ? undefined : header.getSize() }}
                      className="border-b px-3 py-2 text-left text-micro font-semibold tracking-wide text-muted uppercase"
                    >
                      {sortable ? (
                        <button
                          type="button"
                          onClick={header.column.getToggleSortingHandler()}
                          className="inline-flex items-center gap-1 hover:text-text"
                        >
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          {dir === "asc" ? (
                            <ArrowUp className="size-3" />
                          ) : dir === "desc" ? (
                            <ArrowDown className="size-3" />
                          ) : (
                            <ChevronsUpDown className="size-3 opacity-30" />
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
              <tr>
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
                  )}
                  style={{ height: ROW_HEIGHT }}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-3 align-middle">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              );
            })}
            {paddingBottom > 0 ? (
              <tr>
                <td style={{ height: paddingBottom }} colSpan={columns.length} />
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between border-t px-3 py-1.5 text-micro text-subtle">
        <span className="tnum">{rows.length.toLocaleString("en-GB")} rows</span>
        <span>click a row to open it</span>
      </div>
    </div>
  );
}

/** A small static table for a handful of rows, where virtualisation would be silly. */
export function DataTable({ head, children }: { head: ReactNode[]; children: ReactNode }) {
  return (
    <div className="overflow-hidden rounded-[var(--radius)] border bg-surface">
      <table className="w-full border-collapse text-small">
        <thead className="bg-surface-raised">
          <tr>
            {head.map((h, i) => (
              <th
                // biome-ignore lint/suspicious/noArrayIndexKey: static header cells
                key={i}
                className="border-b px-3 py-2 text-left text-micro font-semibold tracking-wide text-muted uppercase"
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

export function Td({ children, className }: { children?: ReactNode; className?: string }) {
  return <td className={cn("border-b px-3 py-2 align-middle", className)}>{children}</td>;
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
