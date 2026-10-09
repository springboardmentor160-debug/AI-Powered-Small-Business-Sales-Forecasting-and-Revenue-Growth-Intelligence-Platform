import FilterBar from "../components/FilterBar";
import { IconAI, IconArrowRight, IconCustomers } from "../components/Icons";
import "./CustomersPage.css";

const formatNumber = (value, digits = 0) =>
  Number(value || 0).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });

const formatCurrency = (value, digits = 0) =>
  `₹${formatNumber(value, digits)}`;

const getWeightedAverage = (profiles, field) => {
  const weightedTotal = profiles.reduce(
    (total, profile) =>
      total + Number(profile[field] || 0) * Number(profile.record_count || 0),
    0
  );
  const recordCount = profiles.reduce(
    (total, profile) => total + Number(profile.record_count || 0),
    0
  );

  return recordCount ? weightedTotal / recordCount : null;
};

export default function CustomersPage({
  filters,
  setFilters,
  filterOptions,
  resetFilters,
  demographicIntel,
  segmentationData,
  segmentationMethod,
  setActivePage,
}) {
  const profiles =
    segmentationMethod === "hierarchical"
      ? segmentationData?.hierarchical_profiles || []
      : segmentationData?.kmeans_profiles || [];
  const totalRecords = profiles.reduce(
    (total, profile) => total + Number(profile.record_count || 0),
    0
  );
  const averagePurchaseValue = getWeightedAverage(profiles, "mean_purchase_value");
  const averageFrequency = getWeightedAverage(profiles, "mean_purchase_frequency");
  const averageActivity = getWeightedAverage(
    profiles,
    "mean_customer_activity_days"
  );

  const demographicGroups = [
    {
      key: "age_group",
      label: "Age Groups",
      values: demographicIntel?.by_age_group || [],
      name: (item) => `${item.age_group} years`,
    },
    {
      key: "gender",
      label: "Gender",
      values: demographicIntel?.by_gender || [],
      name: (item) =>
        item.gender === "M"
          ? "Male"
          : item.gender === "F"
            ? "Female"
            : item.gender === "O"
              ? "Other"
              : "Unspecified",
    },
    {
      key: "loyalty_status",
      label: "Loyalty",
      values: demographicIntel?.by_loyalty || [],
      name: (item) => item.loyalty_status,
    },
  ];

  const strongestValueProfile = profiles.reduce(
    (strongest, profile) =>
      !strongest ||
      Number(profile.mean_purchase_value || 0) >
        Number(strongest.mean_purchase_value || 0)
        ? profile
        : strongest,
    null
  );
  const mostFrequentProfile = profiles.reduce(
    (strongest, profile) =>
      !strongest ||
      Number(profile.mean_purchase_frequency || 0) >
        Number(strongest.mean_purchase_frequency || 0)
        ? profile
        : strongest,
    null
  );
  const leastRecentlyActiveProfile = profiles.reduce(
    (leastRecent, profile) =>
      !leastRecent ||
      Number(profile.mean_customer_activity_days || 0) >
        Number(leastRecent.mean_customer_activity_days || 0)
        ? profile
        : leastRecent,
    null
  );
  const loyaltyGroups = demographicIntel?.by_loyalty || [];
  const loyalGroup = loyaltyGroups.find(
    (group) => group.loyalty_status === "Loyal"
  );
  const nonLoyalGroup = loyaltyGroups.find(
    (group) => group.loyalty_status === "Non-Loyal"
  );
  const segmentPreview = [...profiles]
    .sort(
      (first, second) =>
        Number(second.record_count || 0) - Number(first.record_count || 0)
    )
    .slice(0, 3);

  return (
    <div className="page-container customer-page">
      <FilterBar
        filters={filters}
        setFilters={setFilters}
        filterOptions={filterOptions}
        resetFilters={resetFilters}
      />

      <section className="customer-page-heading">
        <div className="customer-title-icon">
          <IconCustomers size={22} color="#6558d3" />
        </div>
        <div>
          <h2>Customer Intelligence</h2>
          <p>Understand customer behavior, value and engagement patterns.</p>
        </div>
      </section>

      <section className="customer-kpi-grid" aria-label="Customer cohort summary">
        <article className="customer-kpi-card customer-kpi-purple">
          <span className="customer-kpi-icon"><IconCustomers size={18} /></span>
          <span className="customer-kpi-label">Cohort Records</span>
          <strong>{formatNumber(totalRecords)}</strong>
          <small>Transaction records grouped into cohorts</small>
        </article>
        <article className="customer-kpi-card customer-kpi-blue">
          <span className="customer-kpi-icon"><span aria-hidden="true">₹</span></span>
          <span className="customer-kpi-label">Average Purchase Value</span>
          <strong>
            {averagePurchaseValue === null
              ? "—"
              : formatCurrency(averagePurchaseValue)}
          </strong>
          <small>Average value per transaction</small>
        </article>
        <article className="customer-kpi-card customer-kpi-green">
          <span className="customer-kpi-icon"><span aria-hidden="true">↗</span></span>
          <span className="customer-kpi-label">Purchase Frequency</span>
          <strong>
            {averageFrequency === null
              ? "—"
              : `${formatNumber(averageFrequency, 1)} units`}
          </strong>
          <small>Average units per transaction</small>
        </article>
        <article className="customer-kpi-card customer-kpi-amber">
          <span className="customer-kpi-icon"><span aria-hidden="true">◷</span></span>
          <span className="customer-kpi-label">Average Activity / Recency</span>
          <strong>
            {averageActivity === null
              ? "—"
              : `${formatNumber(averageActivity, 1)} days`}
          </strong>
          <small>Average days since transaction</small>
        </article>
      </section>

      <section className="customer-panel customer-overview">
        <div className="customer-panel-heading">
          <div>
            <span className="customer-eyebrow">Customer behavior overview</span>
            <h3>Customer Cohorts by Demographic</h3>
            <p>Revenue and transaction activity across the available sales records.</p>
          </div>
          <span className="customer-data-chip">Filtered view</span>
        </div>
        <div className="customer-dimension-grid">
          {demographicGroups.map((group) => {
            const maxRevenue = Math.max(
              0,
              ...group.values.map((item) => Number(item.revenue || 0))
            );

            return (
              <div className="customer-dimension" key={group.key}>
                <h4>{group.label}</h4>
                {group.values.length ? (
                  <div className="customer-dimension-list">
                    {group.values.map((item) => {
                      const revenue = Number(item.revenue || 0);
                      const width =
                        maxRevenue > 0 ? (revenue / maxRevenue) * 100 : 0;

                      return (
                        <div className="customer-dimension-row" key={item[group.key]}>
                          <div className="customer-dimension-row-top">
                            <span>{group.name(item)}</span>
                            <strong>{formatCurrency(revenue)}</strong>
                          </div>
                          <div
                            className="customer-bar-track"
                            role="img"
                            aria-label={`${group.name(item)} revenue: ${formatCurrency(revenue)}`}
                          >
                            <span style={{ width: `${width}%` }} />
                          </div>
                          <small>
                            {formatNumber(item.transactions)} transactions
                            {item.avg_ticket !== undefined &&
                              ` · ${formatCurrency(item.avg_ticket)} avg purchase`}
                          </small>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="customer-empty-state">No data for this selection.</p>
                )}
              </div>
            );
          })}
        </div>
      </section>

      <section className="customer-panel customer-segments">
        <div className="customer-panel-heading">
          <div>
            <span className="customer-eyebrow">Customer cohort preview</span>
            <h3>Customer Segment Preview</h3>
            <p>Prioritized by transaction volume, with value and recent activity.</p>
          </div>
          <button
            className="customer-link-button"
            type="button"
            onClick={() => setActivePage("segmentation")}
          >
            View all segments <IconArrowRight size={16} />
          </button>
        </div>
        {segmentPreview.length ? (
          <div className="customer-segment-list">
            <div className="customer-segment-header" aria-hidden="true">
              <span>Segment</span>
              <span>Cohort records</span>
              <span>Avg. purchase</span>
              <span>Activity</span>
            </div>
            {segmentPreview.map((profile) => (
              <div className="customer-segment-row" key={profile.cluster_id}>
                <strong>{profile.segment_name}</strong>
                <span>
                  {formatNumber(profile.record_count)}{" "}
                  <small>({formatNumber(profile.percentage, 1)}%)</small>
                </span>
                <span>{formatCurrency(profile.mean_purchase_value)}</span>
                <span>{formatNumber(profile.mean_customer_activity_days, 1)} days ago</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="customer-empty-state">
            Segment insights will appear when cohort data is available.
          </p>
        )}
      </section>

      {(strongestValueProfile || loyalGroup || mostFrequentProfile || leastRecentlyActiveProfile) && (
        <section className="customer-insights-panel">
          <div className="customer-insights-icon"><IconAI size={20} color="#6558d3" /></div>
          <div className="customer-insights-content">
            <span className="customer-eyebrow">Customer behavior insights</span>
            <div className="customer-insights-grid">
              {strongestValueProfile && (
                <article>
                  <small>Strongest value cohort</small>
                  <strong>{strongestValueProfile.segment_name}</strong>
                  <p>
                    Highest average purchase value at{" "}
                    {formatCurrency(strongestValueProfile.mean_purchase_value)}.
                  </p>
                </article>
              )}
              {loyalGroup && (
                <article>
                  <small>Loyalty behavior</small>
                  <strong>
                    {formatCurrency(loyalGroup.revenue)} loyal-group revenue
                  </strong>
                  <p>
                    {nonLoyalGroup
                      ? `Average purchase: ${formatCurrency(loyalGroup.avg_ticket)} loyal vs. ${formatCurrency(nonLoyalGroup.avg_ticket)} non-loyal.`
                      : `${formatNumber(loyalGroup.transactions)} transactions in the loyal group.`}
                  </p>
                </article>
              )}
              {mostFrequentProfile && (
                <article>
                  <small>Purchase pattern</small>
                  <strong>{mostFrequentProfile.segment_name}</strong>
                  <p>
                    Highest average purchase frequency at{" "}
                    {formatNumber(mostFrequentProfile.mean_purchase_frequency, 1)}{" "}
                    units per transaction.
                  </p>
                </article>
              )}
              {leastRecentlyActiveProfile && (
                <article>
                  <small>Activity to watch</small>
                  <strong>{leastRecentlyActiveProfile.segment_name}</strong>
                  <p>
                    Longest average recency:{" "}
                    {formatNumber(leastRecentlyActiveProfile.mean_customer_activity_days, 1)}{" "}
                    days since transaction.
                  </p>
                </article>
              )}
            </div>
          </div>
        </section>
      )}

      <p className="customer-data-note">
        <span aria-hidden="true">i</span>
        Customer analytics are cohort-based because the source dataset does not
        contain persistent Customer IDs.
      </p>
    </div>
  );
}
