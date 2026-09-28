export default function TopProductChart({ product, totalQuantity }) {
  if (!product || !totalQuantity) {
    return <p className="empty-state">Product sales data is not available yet.</p>;
  }

  const share = Math.min(100, (product.quantity_sold / totalQuantity) * 100);

  return (
    <div className="product-chart">
      <div className="product-chart__meta">
        <div>
          <span className="muted-label">Top product</span>
          <strong>{product.product_name}</strong>
        </div>
        <div className="product-chart__value">
          {product.quantity_sold.toLocaleString()} <span>units</span>
        </div>
      </div>
      <div className="bar-track" aria-label={`${product.product_name} share of units sold`}>
        <div className="bar-fill" style={{ width: `${share}%` }} />
      </div>
      <div className="product-chart__footer">
        <span>{share.toFixed(1)}% of all units sold</span>
        <span>{product.product_id}</span>
      </div>
    </div>
  );
}
