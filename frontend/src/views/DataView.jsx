import { useMemo } from "react";
import { Boxes, ReceiptText, Table2 } from "lucide-react";
import Badge from "../components/ui/Badge";
import { Card, CardHeader } from "../components/ui/Card";
import DataTable from "../components/ui/DataTable";
import { formatCurrency, formatDate, formatNumber } from "../lib/format";

const LOW_STOCK_LEVEL = 100;

const STOCK_FILTER = {
  id: "stock",
  label: "stock levels",
  options: [
    { value: "low", label: "Low stock" },
    { value: "ok", label: "In stock" },
  ],
  predicate: (row, value) =>
    value === "low" ? row.inventory_level < LOW_STOCK_LEVEL : row.inventory_level >= LOW_STOCK_LEVEL,
};

function InventoryBar({ value, max }) {
  const low = value < LOW_STOCK_LEVEL;
  return (
    <div className="flex items-center justify-end gap-3">
      <div className="hidden h-1.5 w-20 overflow-hidden rounded-full bg-slate-100 dark:bg-white/10 sm:block">
        <div
          className={low ? "h-full rounded-full bg-amber-500" : "h-full rounded-full bg-indigo-500"}
          style={{ width: `${Math.max((value / max) * 100, 2)}%` }}
        />
      </div>
      <span
        className={
          low
            ? "w-12 font-semibold text-amber-700 dark:text-amber-300"
            : "w-12 font-medium text-slate-900 dark:text-white"
        }
      >
        {formatNumber(value)}
      </span>
    </div>
  );
}

export default function DataView({ role, salesData, myTransactions, loading }) {
  const maxInventory = useMemo(
    () => Math.max(1, ...salesData.map((r) => Number(r.inventory_level) || 0)),
    [salesData],
  );

  const storeFilter = useMemo(() => {
    const stores = [...new Set(salesData.map((r) => String(r.store_id)))].sort((a, b) =>
      a.localeCompare(b, undefined, { numeric: true }),
    );
    return {
      id: "store",
      label: "stores",
      options: stores.map((s) => ({ value: s, label: `Store ${s}` })),
      predicate: (row, value) => String(row.store_id) === value,
    };
  }, [salesData]);

  if (role === "sales_exec") {
    return (
      <Card>
        <CardHeader
          icon={ReceiptText}
          title="My customer transactions"
          description="Invoices for customers assigned to you"
          actions={<Badge tone="neutral">{formatNumber(myTransactions.length)} rows</Badge>}
        />
        <DataTable
          loading={loading && myTransactions.length === 0}
          rows={myTransactions}
          rowKey={(row) => row.id}
          searchPlaceholder="Search invoice, customer or item"
          searchText={(row) => `${row.invoice_no} ${row.customer_id} ${row.description}`}
          emptyTitle="No transactions yet"
          emptyDescription="Transactions for your customers will appear here."
          columns={[
            {
              key: "invoice_no",
              header: "Invoice",
              cell: (row) => (
                <span className="font-semibold text-slate-900 dark:text-white">{row.invoice_no}</span>
              ),
            },
            { key: "customer_id", header: "Customer" },
            {
              key: "description",
              header: "Item",
              className: "max-w-xs truncate",
              cell: (row) => <span title={row.description}>{row.description}</span>,
            },
            { key: "quantity", header: "Qty", align: "right", cell: (row) => formatNumber(row.quantity) },
            {
              key: "total_amount",
              header: "Total",
              align: "right",
              cell: (row) => (
                <span className="font-semibold text-slate-900 dark:text-white">
                  {formatCurrency(row.total_amount, { decimals: 2 })}
                </span>
              ),
            },
          ]}
        />
      </Card>
    );
  }

  if (role === "store_manager") {
    return (
      <Card>
        <CardHeader
          icon={Boxes}
          title="Inventory overview"
          description="Lowest stock first, so reorders are easy to spot"
          actions={<Badge tone="neutral">{formatNumber(salesData.length)} rows</Badge>}
        />
        <DataTable
          loading={loading && salesData.length === 0}
          rows={salesData}
          rowKey={(row) => row.id}
          defaultSort={{ key: "inventory_level", dir: "asc" }}
          searchPlaceholder="Search store or product"
          searchText={(row) => `${row.store_id} ${row.product_id}`}
          filters={[STOCK_FILTER]}
          emptyTitle="No inventory data yet"
          emptyDescription="Stock levels will appear here once sales data is loaded."
          columns={[
            { key: "store_id", header: "Store" },
            { key: "product_id", header: "Product" },
            {
              key: "inventory_level",
              header: "Inventory",
              align: "right",
              cell: (row) => <InventoryBar value={Number(row.inventory_level) || 0} max={maxInventory} />,
            },
            { key: "units_sold", header: "Units sold", align: "right", cell: (row) => formatNumber(row.units_sold) },
            {
              key: "status",
              header: "Status",
              sortValue: (row) => (row.inventory_level < LOW_STOCK_LEVEL ? 0 : 1),
              cell: (row) =>
                row.inventory_level < LOW_STOCK_LEVEL ? (
                  <Badge tone="warning" dot>Reorder soon</Badge>
                ) : (
                  <Badge tone="success" dot>In stock</Badge>
                ),
            },
          ]}
        />
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader
        icon={Table2}
        title="Sales transactions"
        description="Units sold and stock levels by store and product"
        actions={<Badge tone="neutral">{formatNumber(salesData.length)} rows</Badge>}
      />
      <DataTable
        loading={loading && salesData.length === 0}
        rows={salesData}
        rowKey={(row) => row.id}
        defaultSort={{ key: "date", dir: "desc" }}
        searchPlaceholder="Search store or product"
        searchText={(row) => `${row.store_id} ${row.product_id}`}
        filters={[storeFilter, STOCK_FILTER]}
        emptyTitle="No sales data yet"
        emptyDescription="Sales transactions will appear here once they are recorded."
        columns={[
          { key: "store_id", header: "Store" },
          { key: "product_id", header: "Product" },
          {
            key: "date",
            header: "Date",
            sortValue: (row) => Date.parse(row.date) || 0,
            cell: (row) => formatDate(row.date),
          },
          { key: "units_sold", header: "Units sold", align: "right", cell: (row) => formatNumber(row.units_sold) },
          {
            key: "inventory_level",
            header: "Inventory",
            align: "right",
            cell: (row) => (
              <div className="flex items-center justify-end gap-2">
                {row.inventory_level < LOW_STOCK_LEVEL && <Badge tone="warning">Low</Badge>}
                <span
                  className={
                    row.inventory_level < LOW_STOCK_LEVEL
                      ? "font-semibold text-amber-700 dark:text-amber-300"
                      : "font-medium text-slate-900 dark:text-white"
                  }
                >
                  {formatNumber(row.inventory_level)}
                </span>
              </div>
            ),
          },
        ]}
      />
    </Card>
  );
}
