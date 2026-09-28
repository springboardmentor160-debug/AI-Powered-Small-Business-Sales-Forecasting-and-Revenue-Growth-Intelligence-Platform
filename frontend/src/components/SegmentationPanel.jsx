function formatNumber(value) {
  return new Intl.NumberFormat("en-IN").format(value || 0);
}

function formatValue(value) {
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(value || 0);
}

export default function SegmentationPanel({ report }) {
  const largestSegment = report.segments[0];
  const largestCount = Math.max(...report.segments.map((segment) => segment.customer_count), 1);

  return (
    <article className="panel panel--segmentation">
      <div className="section-heading">
        <div>
          <p className="section-heading__eyebrow">CUSTOMER SEGMENTATION</p>
          <h2>Who is in the room</h2>
        </div>
        <span className="section-heading__action">{formatNumber(report.customers_processed)} customers</span>
      </div>
      <div className="segment-list">
        {report.segments.map((segment) => (
          <div className="segment-row" key={segment.segment_name}>
            <div className="segment-row__heading">
              <strong>{segment.segment_name}</strong>
              <span>{formatNumber(segment.customer_count)}</span>
            </div>
            <div className="segment-row__track">
              <div className="segment-row__fill" style={{ width: `${(segment.customer_count / largestCount) * 100}%` }} />
            </div>
            <div className="segment-row__details">
              <span>Avg value {formatValue(segment.average_purchase_value)}</span>
              <span>Activity {formatValue(segment.average_customer_activity)} days</span>
            </div>
          </div>
        ))}
      </div>
      <p className="report-note"><strong>{largestSegment.segment_name}</strong> is the largest observed segment in the generated customer output.</p>
    </article>
  );
}
