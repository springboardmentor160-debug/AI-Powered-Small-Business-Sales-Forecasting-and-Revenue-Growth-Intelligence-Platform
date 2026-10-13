import { useCallback, useEffect, useState } from "react";
import { AlertCircle, Boxes, Download, RefreshCw } from "lucide-react";
import {
  ApiRequestError,
  getInventoryPreview,
  type InventoryPreview,
} from "./lib/api";

interface InventoryPanelProps {
  token: string;
}

function formatNumber(value: number): string {
  return Number(value).toLocaleString(undefined, {
    maximumFractionDigits: 2,
  });
}

export default function InventoryPanel({ token }: InventoryPanelProps) {
  const [data, setData] = useState<InventoryPreview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadInventory = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const result = await getInventoryPreview(token);
      setData(result);
    } catch (cause: unknown) {
      setError(
        cause instanceof ApiRequestError
          ? cause.message
          : "Unable to load inventory data.",
      );
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    let active = true;
    void Promise.resolve().then(() => {
      if (active) void loadInventory();
    });
    return () => {
      active = false;
    };
  }, [loadInventory]);

  function downloadJson() {
    if (!data) return;

    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "marketmind-inventory-preview.json";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="inventory-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">STOCK INTELLIGENCE</p>
          <h2>
            <Boxes size={22} /> Inventory overview
          </h2>
        </div>
        <div className="inventory-actions">
          <button
            type="button"
            className="button button-secondary"
            onClick={() => void loadInventory()}
            disabled={loading}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
          <button
            type="button"
            className="button button-primary"
            onClick={downloadJson}
            disabled={!data || loading}
          >
            <Download size={16} />
            Export JSON
          </button>
        </div>
      </div>

      <p className="inventory-warning">
        Estimates only — these values are not verified physical stock counts.
      </p>

      {loading && <p>Loading inventory preview from the backend...</p>}

      {error && (
        <p className="inventory-error" role="alert">
          <AlertCircle size={17} /> {error}
        </p>
      )}

      {data && !loading && (
        <>
          <div className="inventory-metrics">
            <article>
              <span>Total products</span>
              <strong>{formatNumber(data.total_products)}</strong>
            </article>
            <article>
              <span>Total units sold</span>
              <strong>{formatNumber(data.total_units_sold)}</strong>
            </article>
            <article>
              <span>Estimated initial stock</span>
              <strong>
                {formatNumber(data.total_estimated_initial_stock)}
              </strong>
            </article>
            <article>
              <span>Estimated remaining stock</span>
              <strong>
                {formatNumber(data.total_estimated_remaining_stock)}
              </strong>
            </article>
          </div>

          <p className="inventory-method">{data.inventory_method}</p>
          <p className="inventory-note">{data.note}</p>
          <p className="inventory-sources">
            Source files: {data.source_files.join(", ")}
          </p>

          <div className="forecast-table-wrap">
            <table className="forecast-table inventory-table">
              <thead>
                <tr>
                  <th>Product ID</th>
                  <th>Description</th>
                  <th>Units sold</th>
                  <th>Estimated initial stock</th>
                  <th>Estimated remaining stock</th>
                </tr>
              </thead>
              <tbody>
                {data.products.map((product, index) => (
                  <tr key={`${product.ProductID}-${index}`}>
                    <td>{product.ProductID}</td>
                    <td>{product.ProductDescription || "No description"}</td>
                    <td>{formatNumber(product.TotalUnitsSold)}</td>
                    <td>{formatNumber(product.InitialStock)}</td>
                    <td>
                      {formatNumber(product.EstimatedRemainingStock)}
                    </td>
                  </tr>
                ))}
                {data.products.length === 0 && (
                  <tr>
                    <td colSpan={5}>No inventory records were returned.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}