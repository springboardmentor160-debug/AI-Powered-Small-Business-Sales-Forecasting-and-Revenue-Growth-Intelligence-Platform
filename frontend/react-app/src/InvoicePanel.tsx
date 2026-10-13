import { useCallback, useEffect, useState, type FormEvent } from "react";
import { AlertCircle, Download, FileText, Plus, RefreshCw } from "lucide-react";
import {
  ApiRequestError,
  createInvoice,
  getInvoices,
  type InvoiceCreateRequest,
  type InvoiceListResponse,
  type PaymentStatus,
  type UserRole,
} from "./lib/api";

interface InvoicePanelProps {
  token: string;
  role: UserRole;
}

const paymentStatuses: PaymentStatus[] = ["Pending", "Paid", "Cancelled"];

function money(value: number): string {
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export default function InvoicePanel({ token, role }: InvoicePanelProps) {
  const [data, setData] = useState<InvoiceListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [customerName, setCustomerName] = useState("");
  const [productName, setProductName] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [unitPrice, setUnitPrice] = useState("1.00");
  const [paymentStatus, setPaymentStatus] = useState<PaymentStatus>("Pending");

  const canCreate = role === "sales_executive" || role === "admin";

  const loadInvoices = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      setData(await getInvoices(token));
    } catch (cause: unknown) {
      setError(
        cause instanceof ApiRequestError
          ? cause.message
          : "Unable to load invoices.",
      );
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => {
      if (active) void loadInvoices();
    });
    return () => {
      active = false;
    };
  }, [loadInvoices]);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setNotice("");

    const parsedQuantity = Number(quantity);
    const parsedUnitPrice = Number(unitPrice);

    if (
      !Number.isInteger(parsedQuantity) ||
      parsedQuantity < 1 ||
      parsedQuantity > 1_000_000
    ) {
      setError("Quantity must be a whole number between 1 and 1,000,000.");
      return;
    }

    if (
      !Number.isFinite(parsedUnitPrice) ||
      parsedUnitPrice <= 0 ||
      parsedUnitPrice > 100_000_000
    ) {
      setError("Unit price must be greater than 0 and at most 100,000,000.");
      return;
    }

    const invoice: InvoiceCreateRequest = {
      customer_name: customerName.trim(),
      product_name: productName.trim(),
      quantity: parsedQuantity,
      unit_price: parsedUnitPrice,
      payment_status: paymentStatus,
    };

    setSaving(true);

    try {
      const result = await createInvoice(invoice, token);
      setNotice(`${result.message} Invoice ID: ${result.invoice.invoice_id}`);
      setCustomerName("");
      setProductName("");
      setQuantity("1");
      setUnitPrice("1.00");
      setPaymentStatus("Pending");
      await loadInvoices();
    } catch (cause: unknown) {
      setError(
        cause instanceof ApiRequestError
          ? cause.message
          : "Unable to create the invoice.",
      );
    } finally {
      setSaving(false);
    }
  }

  function exportCsv() {
    if (!data) return;

    const columns = [
      "invoice_id",
      "customer_name",
      "product_name",
      "quantity",
      "unit_price",
      "total_amount",
      "payment_status",
      "created_by",
      "created_at",
    ] as const;

    const escapeCsv = (value: unknown) =>
      `"${String(value ?? "").replace(/"/g, '""')}"`;

    const rows = [
      columns.join(","),
      ...data.invoices.map((invoice) =>
        columns.map((column) => escapeCsv(invoice[column])).join(","),
      ),
    ];

    const blob = new Blob(["\uFEFF", rows.join("\r\n")], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "marketmind-invoices.csv";
    anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  return (
    <section className="invoice-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">TRANSACTION MANAGEMENT</p>
          <h2><FileText size={22} /> Invoice registry</h2>
        </div>
        <div className="inventory-actions">
          <button
            type="button"
            className="button button-secondary"
            onClick={() => void loadInvoices()}
            disabled={loading}
          >
            <RefreshCw size={16} /> Refresh
          </button>
          <button
            type="button"
            className="button button-primary"
            onClick={exportCsv}
            disabled={!data || loading}
          >
            <Download size={16} /> Export CSV
          </button>
        </div>
      </div>

      {canCreate && (
        <form className="invoice-form" onSubmit={handleCreate}>
          <h3><Plus size={18} /> Create invoice</h3>

          <div className="invoice-form-grid">
            <label>
              Customer name
              <input
                value={customerName}
                onChange={(event) => setCustomerName(event.target.value)}
                minLength={1}
                maxLength={150}
                required
              />
            </label>

            <label>
              Product name
              <input
                value={productName}
                onChange={(event) => setProductName(event.target.value)}
                minLength={1}
                maxLength={200}
                required
              />
            </label>

            <label>
              Quantity
              <input
                type="number"
                min={1}
                max={1_000_000}
                step={1}
                value={quantity}
                onChange={(event) => setQuantity(event.target.value)}
                required
              />
            </label>

            <label>
              Unit price
              <input
                type="number"
                min="0.01"
                max={100_000_000}
                step="0.01"
                value={unitPrice}
                onChange={(event) => setUnitPrice(event.target.value)}
                required
              />
            </label>

            <label>
              Payment status
              <select
                value={paymentStatus}
                onChange={(event) =>
                  setPaymentStatus(event.target.value as PaymentStatus)
                }
              >
                {paymentStatuses.map((status) => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
            </label>
          </div>

          <p className="invoice-total-preview">
            Total preview: {money(
              Math.max(0, Number(quantity) || 0) *
              Math.max(0, Number(unitPrice) || 0),
            )}
          </p>

          <button
            type="submit"
            className="button button-primary"
            disabled={saving}
          >
            {saving ? "Saving invoice..." : "Create invoice"}
          </button>
        </form>
      )}

      {!canCreate && (
        <p className="invoice-readonly">
          Your role has read-only access to the invoice registry.
        </p>
      )}

      {notice && <p className="invoice-success" role="status">{notice}</p>}

      {error && (
        <p className="invoice-error" role="alert">
          <AlertCircle size={17} /> {error}
        </p>
      )}

      {loading ? (
        <p>Loading invoice records...</p>
      ) : data ? (
        <>
          <p className="segmentation-note">
            Total invoices: {data.total_invoices.toLocaleString()}
          </p>

          <div className="forecast-table-wrap">
            <table className="forecast-table invoice-table">
              <thead>
                <tr>
                  <th>Invoice ID</th>
                  <th>Customer</th>
                  <th>Product</th>
                  <th>Quantity</th>
                  <th>Unit price</th>
                  <th>Total</th>
                  <th>Status</th>
                  <th>Created by</th>
                  <th>Created at</th>
                </tr>
              </thead>
              <tbody>
                {data.invoices.map((invoice) => (
                  <tr key={invoice.invoice_id}>
                    <td>{invoice.invoice_id}</td>
                    <td>{invoice.customer_name}</td>
                    <td>{invoice.product_name}</td>
                    <td>{invoice.quantity.toLocaleString()}</td>
                    <td>{money(invoice.unit_price)}</td>
                    <td>{money(invoice.total_amount)}</td>
                    <td>{invoice.payment_status}</td>
                    <td>{invoice.created_by}</td>
                    <td>{new Date(invoice.created_at).toLocaleString()}</td>
                  </tr>
                ))}
                {data.invoices.length === 0 && (
                  <tr>
                    <td colSpan={9}>No invoices have been recorded.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </section>
  );
}