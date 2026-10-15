import { useMemo, useState } from "react";
import {
  ArrowDown,
  ArrowUp,
  ChevronLeft,
  ChevronRight,
  ChevronsUpDown,
  Inbox,
  Search,
  SearchX,
} from "lucide-react";
import { cn, formatNumber } from "../../lib/format";
import Button from "./Button";
import EmptyState from "./EmptyState";
import { Input, Select } from "./Field";
import Skeleton from "./Skeleton";

const ALIGN = { left: "text-left", right: "text-right", center: "text-center" };

function compareValues(a, b) {
  if (a == null && b == null) return 0;
  if (a == null) return 1;
  if (b == null) return -1;
  if (typeof a === "number" && typeof b === "number") return a - b;
  return String(a).localeCompare(String(b), undefined, { numeric: true });
}

/**
 * columns: [{ key, header, cell?(row), sortValue?(row), align?, className?, sortable? }]
 * filters: [{ id, label, options: [{ value, label }], predicate(row, value) }]
 */
export default function DataTable({
  columns,
  rows,
  rowKey,
  loading = false,
  searchPlaceholder = "Search",
  searchText,
  filters = [],
  defaultSort = null,
  pageSizes = [10, 25, 50],
  emptyTitle = "Nothing here yet",
  emptyDescription,
  maxHeight = "30rem",
}) {
  const [query, setQuery] = useState("");
  const [filterValues, setFilterValues] = useState({});
  const [sort, setSort] = useState(defaultSort);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(pageSizes[0]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows.filter((row) => {
      if (q && searchText && !searchText(row).toLowerCase().includes(q)) return false;
      return filters.every((f) => {
        const value = filterValues[f.id];
        return !value || value === "all" || f.predicate(row, value);
      });
    });
  }, [rows, query, filterValues, filters, searchText]);

  const sorted = useMemo(() => {
    if (!sort) return filtered;
    const column = columns.find((c) => c.key === sort.key);
    if (!column) return filtered;
    const get = column.sortValue ?? ((row) => row[column.key]);
    const direction = sort.dir === "asc" ? 1 : -1;
    return [...filtered].sort((a, b) => compareValues(get(a), get(b)) * direction);
  }, [filtered, sort, columns]);

  const pageCount = Math.max(1, Math.ceil(sorted.length / pageSize));
  const currentPage = Math.min(page, pageCount - 1);
  const start = currentPage * pageSize;
  const visible = sorted.slice(start, start + pageSize);
  const hasActiveFilters =
    query.trim() !== "" ||
    filters.some((f) => filterValues[f.id] && filterValues[f.id] !== "all");

  function toggleSort(key) {
    setSort((current) => {
      if (!current || current.key !== key) return { key, dir: "asc" };
      if (current.dir === "asc") return { key, dir: "desc" };
      return null;
    });
  }

  function clearFilters() {
    setQuery("");
    setFilterValues({});
    setPage(0);
  }

  const showToolbar = Boolean(searchText) || filters.length > 0;

  return (
    <div>
      {showToolbar && (
        <div className="flex flex-wrap items-center gap-3 border-y border-slate-200 px-5 py-3 dark:border-white/10 sm:px-6">
          {searchText && (
            <div className="min-w-[12rem] flex-1 sm:max-w-xs">
              <Input
                icon={Search}
                type="search"
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setPage(0);
                }}
                placeholder={searchPlaceholder}
                aria-label={searchPlaceholder}
                className="h-9"
              />
            </div>
          )}
          {filters.map((f) => (
            <Select
              key={f.id}
              aria-label={`Filter by ${f.label}`}
              value={filterValues[f.id] ?? "all"}
              onChange={(event) => {
                setFilterValues((current) => ({ ...current, [f.id]: event.target.value }));
                setPage(0);
              }}
            >
              <option value="all">All {f.label}</option>
              {f.options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
          ))}
          {hasActiveFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              Clear filters
            </Button>
          )}
        </div>
      )}

      <div className="overflow-auto" style={{ maxHeight }}>
        <table className="w-full border-separate border-spacing-0 text-sm">
          <thead>
            <tr>
              {columns.map((column) => {
                const sortable = column.sortable !== false;
                const active = sort?.key === column.key;
                const ariaSort = active
                  ? sort.dir === "asc"
                    ? "ascending"
                    : "descending"
                  : "none";
                return (
                  <th
                    key={column.key}
                    scope="col"
                    aria-sort={sortable ? ariaSort : undefined}
                    className={cn(
                      "sticky top-0 z-10 whitespace-nowrap border-b border-slate-200 bg-slate-50 px-4 py-2.5 text-xs font-semibold text-slate-500 first:pl-5 last:pr-5 dark:border-white/10 dark:bg-slate-900 dark:text-slate-400 sm:first:pl-6 sm:last:pr-6",
                      ALIGN[column.align ?? "left"],
                    )}
                  >
                    {sortable ? (
                      <button
                        type="button"
                        onClick={() => toggleSort(column.key)}
                        className={cn(
                          "-mx-1.5 inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 transition-colors hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 dark:hover:text-white",
                          column.align === "right" && "flex-row-reverse",
                          active && "text-slate-900 dark:text-white",
                        )}
                      >
                        {column.header}
                        {active ? (
                          sort.dir === "asc" ? (
                            <ArrowUp aria-hidden="true" className="size-3.5" />
                          ) : (
                            <ArrowDown aria-hidden="true" className="size-3.5" />
                          )
                        ) : (
                          <ChevronsUpDown aria-hidden="true" className="size-3.5 opacity-40" />
                        )}
                      </button>
                    ) : (
                      column.header
                    )}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {loading &&
              Array.from({ length: 6 }, (_, i) => (
                <tr key={`skeleton-${i}`}>
                  {columns.map((column, j) => (
                    <td
                      key={column.key}
                      className="border-b border-slate-100 px-4 py-3.5 first:pl-5 last:pr-5 dark:border-white/5 sm:first:pl-6 sm:last:pr-6"
                    >
                      <Skeleton
                        className={cn(
                          "h-4",
                          column.align === "right" && "ml-auto",
                          (i + j) % 3 === 0 ? "w-24" : (i + j) % 3 === 1 ? "w-16" : "w-20",
                        )}
                      />
                    </td>
                  ))}
                </tr>
              ))}

            {!loading &&
              visible.map((row) => (
                <tr
                  key={rowKey(row)}
                  className="transition-colors even:bg-slate-50/70 hover:bg-indigo-50/70 motion-reduce:transition-none dark:even:bg-white/[0.025] dark:hover:bg-indigo-400/[0.08]"
                >
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={cn(
                        "border-b border-slate-100 px-4 py-3 align-middle text-slate-700 first:pl-5 last:pr-5 dark:border-white/5 dark:text-slate-300 sm:first:pl-6 sm:last:pr-6",
                        ALIGN[column.align ?? "left"],
                        column.align === "right" && "tabular-nums",
                        column.className,
                      )}
                    >
                      {column.cell ? column.cell(row) : (row[column.key] ?? "—")}
                    </td>
                  ))}
                </tr>
              ))}
          </tbody>
        </table>

        {!loading && sorted.length === 0 && (
          <EmptyState
            icon={rows.length === 0 ? Inbox : SearchX}
            title={rows.length === 0 ? emptyTitle : "No matching rows"}
            description={
              rows.length === 0
                ? emptyDescription
                : "Try a different search or clear your filters."
            }
            action={
              rows.length > 0 && (
                <Button variant="secondary" size="sm" onClick={clearFilters}>
                  Clear filters
                </Button>
              )
            }
          />
        )}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 px-5 py-3 text-xs text-slate-500 dark:border-white/10 dark:text-slate-400 sm:px-6">
        <p aria-live="polite">
          {loading
            ? "Loading rows…"
            : sorted.length === 0
              ? "0 rows"
              : `Showing ${formatNumber(start + 1)}–${formatNumber(start + visible.length)} of ${formatNumber(sorted.length)}${
                  sorted.length !== rows.length ? ` (filtered from ${formatNumber(rows.length)})` : ""
                }`}
        </p>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2">
            <span>Rows per page</span>
            <Select
              aria-label="Rows per page"
              value={pageSize}
              className="h-8 w-[4.5rem] text-xs"
              onChange={(event) => {
                setPageSize(Number(event.target.value));
                setPage(0);
              }}
            >
              {pageSizes.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </Select>
          </label>
          <span className="tabular-nums">
            Page {currentPage + 1} of {pageCount}
          </span>
          <div className="flex gap-1">
            <Button
              variant="secondary"
              size="icon"
              className="size-8"
              aria-label="Previous page"
              disabled={currentPage === 0}
              onClick={() => setPage(currentPage - 1)}
            >
              <ChevronLeft aria-hidden="true" className="size-4" />
            </Button>
            <Button
              variant="secondary"
              size="icon"
              className="size-8"
              aria-label="Next page"
              disabled={currentPage >= pageCount - 1}
              onClick={() => setPage(currentPage + 1)}
            >
              <ChevronRight aria-hidden="true" className="size-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
