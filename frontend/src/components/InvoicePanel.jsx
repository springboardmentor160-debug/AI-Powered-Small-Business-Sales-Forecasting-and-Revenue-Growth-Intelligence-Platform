import { useEffect, useState } from "react";

import { createInvoice, downloadInvoice, fetchInvoices } from "../api";
import SectionHeading from "./SectionHeading";

function formatAmount(value) {
  return Number(value || 0).toFixed(2);
}

export default function InvoicePanel({ token }) {
  const [invoices, setInvoices] = useState([]);
  const [transactionId, setTransactionId] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [downloadingId, setDownloadingId] = useState(null);
  const [error, setError] = useState(null);

  function loadInvoices() {
    setIsLoading(true);
    setError(null);
    return fetchInvoices(token)
      .then((data) => setInvoices(data.invoices || []))
      .catch((requestError) => setError(requestError.message || "Invoices could not be loaded."))
      .finally(() => setIsLoading(false));
  }

  useEffect(() => {
    let isCurrent = true;
    fetchInvoices(token)
      .then((data) => {
        if (isCurrent) setInvoices(data.invoices || []);
      })
      .catch((requestError) => {
        if (isCurrent) setError(requestError.message || "Invoices could not be loaded.");
      })
      .finally(() => {
        if (isCurrent) setIsLoading(false);
      });
    return () => {
      isCurrent = false;
    };
  }, [token]);

  function handleCreate(event) {
    event.preventDefault();
    const normalizedTransactionId = transactionId.trim();
    if (!normalizedTransactionId) {
      setError("Enter a transaction ID to create an invoice.");
      return;
    }
    setIsCreating(true);
    setError(null);
    createInvoice(normalizedTransactionId, token)
      .then(() => {
        setTransactionId("");
        return loadInvoices();
      })
      .catch((requestError) => setError(requestError.message || "The invoice could not be created."))
      .finally(() => setIsCreating(false));
  }

  function handleDownload(invoice) {
    setDownloadingId(invoice.invoice_id);
    setError(null);
    downloadInvoice(invoice.invoice_id, token)
      .then(({ blob, filename }) => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
      })
      .catch((requestError) => setError(requestError.message || "The invoice could not be downloaded."))
      .finally(() => setDownloadingId(null));
  }

  return (
    <article className="panel panel--invoices">
      <SectionHeading eyebrow="BUSINESS RECORDS" title="Invoices" action="Issued snapshots" />
      <form className="invoice-create" onSubmit={handleCreate}>
        <label htmlFor="invoice-transaction-id">Source transaction ID</label>
        <div className="invoice-create__controls">
          <input id="invoice-transaction-id" value={transactionId} onChange={(event) => setTransactionId(event.target.value)} placeholder="T000001" maxLength="30" />
          <button className="button button--dark" disabled={isCreating} type="submit">{isCreating ? "Creating..." : "Create invoice"}</button>
        </div>
      </form>
      {error ? <p className="invoice-message invoice-message--error" role="alert">{error}</p> : null}
      {isLoading ? <p className="invoice-message">Loading invoices...</p> : null}
      {!isLoading && !error && invoices.length === 0 ? <p className="invoice-message">No invoices have been issued yet.</p> : null}
      {!isLoading && invoices.length > 0 ? (
        <div className="invoice-table-wrap">
          <table className="invoice-table">
            <thead><tr><th>Invoice</th><th>Transaction</th><th>Customer</th><th>Issued</th><th>Total</th><th>Status</th><th>Payment</th><th /></tr></thead>
            <tbody>
              {invoices.map((invoice) => (
                <tr key={invoice.invoice_id}>
                  <td>{invoice.invoice_number}</td><td>{invoice.transaction_id}</td><td>{invoice.customer_name}</td>
                  <td>{invoice.issued_at.slice(0, 10)}</td><td>{formatAmount(invoice.total_amount)}</td>
                  <td>{invoice.status}</td><td>{invoice.payment_status}</td>
                  <td><button className="invoice-download" disabled={downloadingId === invoice.invoice_id} onClick={() => handleDownload(invoice)} type="button">{downloadingId === invoice.invoice_id ? "..." : "Download"}</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </article>
  );
}
