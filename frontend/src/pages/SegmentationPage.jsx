import FilterBar from "../components/FilterBar";
import { IconAI, IconCustomers, IconSegmentation } from "../components/Icons";
import "./SegmentationPage.css";

const segmentGuidance = {
  vip: {
    badge: "HIGHEST VALUE",
    meaning: "These customers generate the highest average purchase value.",
    focus: "Focus on retention and loyalty.",
    action: "RETAIN",
    actionText:
      "Protect this high-value group with loyalty benefits and personalized offers.",
  },
  regular: {
    badge: "REGULAR BUYERS",
    meaning: "These customers show consistent purchasing activity.",
    focus: "Encourage repeat purchases and loyalty.",
    action: "ENGAGE",
    actionText:
      "Keep regular shoppers active with repeat-purchase offers and loyalty incentives.",
  },
  occasional: {
    badge: "GROWTH OPPORTUNITY",
    meaning: "These customers make higher-value purchases less frequently.",
    focus: "Encourage more frequent purchases.",
    action: "GROW",
    actionText:
      "Encourage more frequent purchases through targeted promotions and cross-sell opportunities.",
  },
  atRisk: {
    badge: "NEEDS ATTENTION",
    meaning: "This group shows weaker or less recent purchasing activity.",
    focus: "Use re-engagement and retention campaigns.",
    action: "RE-ENGAGE",
    actionText:
      "Focus retention efforts on purchasing patterns that are weaker or less recent.",
  },
  other: {
    badge: "CUSTOMER GROUP",
    meaning: "This group shares similar purchasing patterns.",
    focus: "Review the group's purchasing patterns.",
    action: "REVIEW",
    actionText:
      "Use the group's recorded purchasing patterns to guide your next business review.",
  },
};

function getSegmentType(segmentName) {
  const name = segmentName.toLowerCase();
  if (name.includes("vip")) return "vip";
  if (name.includes("regular")) return "regular";
  if (name.includes("occasional")) return "occasional";
  if (name.includes("at-risk") || name.includes("inactive")) return "atRisk";
  return "other";
}

function formatCurrency(value) {
  return `₹${Number(value).toLocaleString(undefined, {
    maximumFractionDigits: 2,
  })}`;
}

function formatNumber(value) {
  return Number(value).toLocaleString(undefined, {
    maximumFractionDigits: 2,
  });
}

export default function SegmentationPage({
  filters,
  setFilters,
  filterOptions,
  resetFilters,
  segmentationData,
  segmentationMethod,
  setSegmentationMethod,
}) {
  const currentProfiles =
    segmentationMethod === "kmeans"
      ? segmentationData?.kmeans_profiles || []
      : segmentationData?.hierarchical_profiles || [];

  const totalRecords = currentProfiles.reduce(
    (sum, profile) => sum + profile.record_count,
    0
  );
  const largestSegment =
    currentProfiles.length > 0
      ? currentProfiles.reduce((largest, profile) =>
          profile.record_count > largest.record_count ? profile : largest
        )
      : null;
  const highestValueSegment =
    currentProfiles.length > 0
      ? currentProfiles.reduce((highest, profile) =>
          profile.mean_purchase_value > highest.mean_purchase_value
            ? profile
            : highest
        )
      : null;
  const atRiskSegment =
    currentProfiles.find((profile) => getSegmentType(profile.segment_name) === "atRisk") ||
    (currentProfiles.length > 0
      ? currentProfiles.reduce((leastRecent, profile) =>
          profile.mean_customer_activity_days >
          leastRecent.mean_customer_activity_days
            ? profile
            : leastRecent
        )
      : null);

  const getProfileForType = (type) =>
    currentProfiles.find((profile) => getSegmentType(profile.segment_name) === type);

  return (
    <div className="page-container seg-page-wrap">
      <header className="seg-header-block">
        <h1 className="seg-main-title">
          <IconSegmentation size={21} color="#4776e6" />
          Customer Segmentation
        </h1>
        <p className="seg-main-subtitle">
          Understand different customer groups and where to focus your business
          efforts.
        </p>
        <p className="seg-header-explanation">
          Purchasing patterns are grouped into meaningful customer segments so
          you can decide where to retain, grow, or re-engage.
        </p>
      </header>

      <FilterBar
        filters={filters}
        setFilters={setFilters}
        filterOptions={filterOptions}
        resetFilters={resetFilters}
      />

      <section className="seg-intro-card">
        <div className="seg-intro-title">
          <span className="seg-intro-icon">
            <IconAI size={17} color="#4776e6" />
          </span>
          <h2>What does Customer Segmentation mean?</h2>
        </div>
        <p className="seg-intro-copy">
          This page groups similar purchasing behavior into customer groups. Use
          them to identify valuable shoppers, regular buyers, growth
          opportunities, and purchasing patterns that may need re-engagement.
        </p>
        <div className="seg-intro-steps">
          <div>
            <span>01</span>
            <div>
              <strong>Understand</strong>
              <p>See how different customer groups behave.</p>
            </div>
          </div>
          <div>
            <span>02</span>
            <div>
              <strong>Focus</strong>
              <p>Identify valuable and at-risk groups.</p>
            </div>
          </div>
          <div>
            <span>03</span>
            <div>
              <strong>Act</strong>
              <p>Choose a suitable business strategy for each group.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="seg-kpi-grid" aria-label="Customer group summary">
        <article className="seg-kpi-card card-seg-total">
          <div className="seg-kpi-top">
            <span className="seg-kpi-label">Customer Groups</span>
            <span className="seg-kpi-icon seg-icon-blue">
              <IconSegmentation size={16} />
            </span>
          </div>
          <div className="seg-kpi-value">{currentProfiles.length}</div>
          <span className="seg-kpi-subtext">
            Different purchasing behavior groups identified
          </span>
        </article>

        <article className="seg-kpi-card card-seg-largest">
          <div className="seg-kpi-top">
            <span className="seg-kpi-label">Largest Group</span>
            <span className="seg-kpi-icon seg-icon-green">
              <IconCustomers size={16} />
            </span>
          </div>
          <div className="seg-kpi-value">
            {largestSegment?.segment_name || "—"}
          </div>
          <span className="seg-kpi-subtext">
            Group with the most analyzed records
          </span>
        </article>

        <article className="seg-kpi-card card-seg-value">
          <div className="seg-kpi-top">
            <span className="seg-kpi-label">Highest-Value Group</span>
            <span className="seg-kpi-icon seg-icon-purple">
              <IconCustomers size={16} />
            </span>
          </div>
          <div className="seg-kpi-value">
            {highestValueSegment?.segment_name || "—"}
          </div>
          <span className="seg-kpi-subtext">
            Group with the highest average purchase value
          </span>
        </article>

        <article className="seg-kpi-card card-seg-risk">
          <div className="seg-kpi-top">
            <span className="seg-kpi-label">Needs Attention</span>
            <span className="seg-kpi-icon seg-icon-orange">
              <IconCustomers size={16} />
            </span>
          </div>
          <div className="seg-kpi-value">
            {atRiskSegment?.segment_name || "—"}
          </div>
          <span className="seg-kpi-subtext">
            Group showing weaker or less recent purchasing behavior
          </span>
        </article>
      </section>

      {currentProfiles.length === 0 ? (
        <section className="seg-empty-state">
          <IconCustomers size={22} color="#8290a2" />
          <h2>No customer groups available</h2>
          <p>
            There are no segmentation records for the selected filters and
            grouping method.
          </p>
        </section>
      ) : (
        <>
          <section className="seg-business-section">
            <div className="seg-business-section-heading">
              <div>
                <h2>Customer Groups at a Glance</h2>
                <p>
                  A plain-language summary of the groups found in the analyzed
                  sales records.
                </p>
              </div>
            </div>
            <div className="seg-glance-grid">
              {["vip", "regular", "occasional", "atRisk"].map((type) => {
                const profile = getProfileForType(type);
                if (!profile) return null;
                const guidance = segmentGuidance[type];
                return (
                  <article
                    className={`seg-glance-card seg-type-${type}`}
                    key={profile.cluster_id}
                  >
                    <div className="seg-glance-top">
                      <h3>{profile.segment_name}</h3>
                      <span className="seg-type-badge">{guidance.badge}</span>
                    </div>
                    <p>{guidance.meaning}</p>
                    <div className="seg-glance-action">
                      <span>BUSINESS FOCUS</span>
                      <strong>{guidance.focus}</strong>
                    </div>
                    <div className="seg-glance-meta">
                      {formatNumber(profile.record_count)} records
                      <span aria-hidden="true">·</span>
                      {formatNumber(profile.percentage)}% of records
                    </div>
                  </article>
                );
              })}
            </div>
          </section>

          <section className="seg-card seg-distribution-card">
            <div className="seg-section-header">
              <div>
                <h2 className="seg-card-title">
                  How Our Customer Groups Are Distributed
                </h2>
                <p className="seg-card-sub">
                  See how much of the analyzed sales records belong to each
                  group.
                </p>
              </div>
              <span className="seg-record-count">
                {formatNumber(totalRecords)} sales records analyzed
              </span>
            </div>

            <div className="seg-distribution-list">
              {currentProfiles.map((profile) => {
                const type = getSegmentType(profile.segment_name);
                const guidance = segmentGuidance[type];
                return (
                  <div className={`seg-distribution-row seg-type-${type}`} key={profile.cluster_id}>
                    <div className="seg-distribution-label">
                      <span className="seg-distribution-dot" />
                      <div>
                        <strong>{profile.segment_name}</strong>
                        <span>{guidance.meaning}</span>
                      </div>
                    </div>
                    <div className="seg-distribution-bar" aria-hidden="true">
                      <span style={{ width: `${profile.percentage}%` }} />
                    </div>
                    <strong className="seg-distribution-share">
                      {formatNumber(profile.percentage)}%
                    </strong>
                  </div>
                );
              })}
            </div>
          </section>

          <section className="seg-business-section">
            <div className="seg-business-section-heading">
              <div>
                <h2>Recommended Business Focus</h2>
                <p>Turn the observed purchasing patterns into practical next steps.</p>
              </div>
            </div>
            <div className="seg-action-grid">
              {["vip", "regular", "occasional", "atRisk"].map((type) => {
                const profile = getProfileForType(type);
                if (!profile) return null;
                const guidance = segmentGuidance[type];
                return (
                  <article className={`seg-action-card seg-type-${type}`} key={profile.cluster_id}>
                    <span className="seg-action-label">{guidance.action}</span>
                    <h3>{profile.segment_name}</h3>
                    <p>{guidance.actionText}</p>
                  </article>
                );
              })}
            </div>
          </section>

          <section className="seg-card seg-breakdown-card">
            <div className="seg-section-header">
              <div>
                <h2 className="seg-card-title">Detailed Segment Breakdown</h2>
                <p className="seg-card-sub">
                  Compare the size, purchase value, units, and last activity for
                  each group.
                </p>
              </div>
            </div>

            <div className="seg-profiles-grid">
              {currentProfiles.map((profile) => {
                const type = getSegmentType(profile.segment_name);
                const guidance = segmentGuidance[type];
                return (
                  <article
                    className={`seg-profile-card seg-type-${type}`}
                    key={profile.cluster_id}
                  >
                    <div className="seg-profile-top">
                      <div>
                        <h3 className="seg-profile-name">
                          {profile.segment_name}
                        </h3>
                        <span className="seg-profile-meaning">
                          {guidance.meaning}
                        </span>
                      </div>
                      <span className="seg-profile-badge">
                        {guidance.badge}
                      </span>
                    </div>

                    <div className="seg-why-matters">
                      <span>WHY IT MATTERS</span>
                      <p>{guidance.focus}</p>
                    </div>

                    <div className="seg-detail-metrics">
                      <div className="seg-metric-row">
                        <span
                          className="seg-metric-label"
                          title="Number of available sales records assigned to this group."
                        >
                          Records in this group
                        </span>
                        <strong className="seg-metric-val">
                          {formatNumber(profile.record_count)} ({formatNumber(profile.percentage)}%)
                        </strong>
                      </div>
                      <div className="seg-metric-row">
                        <span
                          className="seg-metric-label"
                          title="Typical value of a purchase in this group."
                        >
                          Average purchase value
                        </span>
                        <strong className="seg-metric-val">
                          {formatCurrency(profile.mean_purchase_value)}
                        </strong>
                      </div>
                      <div className="seg-metric-row">
                        <span
                          className="seg-metric-label"
                          title="Typical number of units purchased per order in this group."
                        >
                          Average units per purchase
                        </span>
                        <strong className="seg-metric-val">
                          {formatNumber(profile.mean_purchase_frequency)} units
                        </strong>
                      </div>
                      <div className="seg-metric-row">
                        <span
                          className="seg-metric-label"
                          title="Average time since the group's recorded activity."
                        >
                          Last activity
                        </span>
                        <strong className="seg-metric-val">
                          {formatNumber(profile.mean_customer_activity_days)} days ago
                        </strong>
                      </div>
                    </div>

                    <div className="seg-profile-focus">
                      <span>BUSINESS FOCUS</span>
                      <p>{guidance.actionText}</p>
                    </div>
                  </article>
                );
              })}
            </div>
          </section>

          <section className="seg-business-section">
            <div className="seg-business-section-heading">
              <div>
                <h2>What the Data Tells Us</h2>
                <p>Key observations from the current customer group results.</p>
              </div>
            </div>
            <div className="seg-insight-grid">
              {highestValueSegment && (
                <article className="seg-insight-item seg-insight-purple">
                  <span className="seg-insight-item-title">Highest Value</span>
                  <strong className="seg-insight-item-val">
                    {highestValueSegment.segment_name}
                  </strong>
                  <p className="seg-insight-item-sub">
                    Highest average purchase value:
                    {" "}
                    <strong>{formatCurrency(highestValueSegment.mean_purchase_value)}</strong>.
                  </p>
                </article>
              )}
              {largestSegment && (
                <article className="seg-insight-item seg-insight-green">
                  <span className="seg-insight-item-title">Largest Group</span>
                  <strong className="seg-insight-item-val">
                    {largestSegment.segment_name}
                  </strong>
                  <p className="seg-insight-item-sub">
                    Represents the largest share of analyzed records:
                    {" "}
                    <strong>{formatNumber(largestSegment.percentage)}%</strong>.
                  </p>
                </article>
              )}
              {atRiskSegment && (
                <article className="seg-insight-item seg-insight-orange">
                  <span className="seg-insight-item-title">Needs Attention</span>
                  <strong className="seg-insight-item-val">
                    {atRiskSegment.segment_name}
                  </strong>
                  <p className="seg-insight-item-sub">
                    Average time since recorded activity:
                    {" "}
                    <strong>
                      {formatNumber(atRiskSegment.mean_customer_activity_days)} days
                    </strong>.
                  </p>
                </article>
              )}
            </div>
          </section>
        </>
      )}

      <details className="seg-tech-panel">
        <summary className="seg-tech-summary">
          <span>
            <strong>Technical Details</strong>
            <small>
              The AI uses purchasing value, purchase frequency and activity
              recency to group similar records into four segments.
            </small>
          </span>
          <span className="seg-tech-chevron" aria-hidden="true" />
        </summary>
        <div className="seg-tech-content">
          <div className="seg-method-control">
            <span className="seg-tech-label">Grouping method</span>
            <div className="toggle-group-compact">
              <button
                className={`toggle-btn-sm ${segmentationMethod === "kmeans" ? "active" : ""}`}
                onClick={() => setSegmentationMethod("kmeans")}
              >
                K-Means
              </button>
              <button
                className={`toggle-btn-sm ${segmentationMethod === "hierarchical" ? "active" : ""}`}
                onClick={() => setSegmentationMethod("hierarchical")}
              >
                Hierarchical
              </button>
            </div>
          </div>
          <div className="seg-tech-grid">
            <div className="seg-tech-item">
              <span className="seg-tech-label">Current method</span>
              <span className="seg-tech-val">
                {segmentationMethod === "kmeans"
                  ? "K-Means (K=4)"
                  : "Hierarchical (4 groups)"}
              </span>
            </div>
            <div className="seg-tech-item">
              <span className="seg-tech-label">Purchasing measures</span>
              <span className="seg-tech-val">Value · Frequency · Recency</span>
            </div>
            <div className="seg-tech-item">
              <span className="seg-tech-label">Feature scaling</span>
              <span className="seg-tech-val">StandardScaler (Mean=0, Var=1)</span>
            </div>
            <div className="seg-tech-item">
              <span className="seg-tech-label">Sales records analyzed</span>
              <span className="seg-tech-val">
                {formatNumber(totalRecords)}
              </span>
            </div>
          </div>
          <p className="seg-data-limitation">
            <strong>Data note:</strong> The source dataset does not contain
            persistent Customer IDs, so these segments represent
            transaction/cohort-level purchasing patterns rather than
            individually tracked customers.
          </p>
          {segmentationData?.limitation_note && (
            <p className="seg-source-limitation">
              {segmentationData.limitation_note}
            </p>
          )}
        </div>
      </details>
    </div>
  );
}
