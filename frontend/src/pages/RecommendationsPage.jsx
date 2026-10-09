import FilterBar from "../components/FilterBar";
import {
  IconAI,
  IconRecommendations,
  IconSales,
} from "../components/Icons";
import "./RecommendationsPage.css";

const tabs = [
  {
    key: "collaborative",
    title: "Recommended Products",
    subtitle: "Similar products",
    dataKey: "recommendations",
    cardType: "similar",
  },
  {
    key: "cross_sell",
    title: "Frequently Bought Together",
    subtitle: "Cross-sell",
    dataKey: "cross_sell_recommendations",
    cardType: "cross-sell",
  },
  {
    key: "upsell",
    title: "Best Upsell Opportunities",
    subtitle: "Higher-value options",
    dataKey: "upsell_recommendations",
    cardType: "upsell",
  },
];

function formatCurrency(value) {
  if (value === undefined || value === null || value === "") return null;
  const amount = Number(value);
  return Number.isFinite(amount)
    ? `₹${amount.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
    : null;
}

function formatRevenue(value) {
  if (value === undefined || value === null || value === "") return null;
  const amount = Number(value);
  return Number.isFinite(amount)
    ? `₹${Math.round(amount / 1000).toLocaleString()}k`
    : null;
}

function CategoryIllustration({ category }) {
  const normalizedCategory = category?.toLowerCase() || "";
  let artwork;

  if (normalizedCategory.includes("dairy")) {
    artwork = (
      <>
        <path d="M39 30h42l-4 11v68a7 7 0 0 1-7 7H50a7 7 0 0 1-7-7V41z" fill="#fff" stroke="currentColor" strokeWidth="2.5" />
        <path d="M39 30h42v13H39z" fill="#cfe5ff" stroke="currentColor" strokeWidth="2.5" />
        <path d="M48 30v-9h24v9" fill="#e8f4ff" stroke="currentColor" strokeWidth="2.5" />
        <path d="M50 66h20v22H50z" rx="4" fill="#eaf3ff" />
        <path d="M54 77c4-7 9-7 13 0" fill="none" stroke="#6994d8" strokeWidth="2" strokeLinecap="round" />
      </>
    );
  } else if (normalizedCategory.includes("grocery")) {
    artwork = (
      <>
        <path d="m31 50 10 55h51l10-55z" fill="#fff" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" />
        <path d="M48 52V40a18 18 0 0 1 36 0v12" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
        <path d="M43 71h48" stroke="#86ad8e" strokeWidth="3" strokeLinecap="round" />
        <circle cx="53" cy="62" r="7" fill="#f3a168" />
        <path d="M67 58c8 0 12 6 12 13-8 0-13-5-12-13z" fill="#85b996" />
        <circle cx="78" cy="84" r="7" fill="#efc45f" />
      </>
    );
  } else if (normalizedCategory.includes("personal care")) {
    artwork = (
      <>
        <path d="M42 43h36l5 62a9 9 0 0 1-9 10H46a9 9 0 0 1-9-10z" fill="#fff" stroke="currentColor" strokeWidth="2.5" />
        <path d="M48 43v-9a8 8 0 0 1 8-8h9a8 8 0 0 1 8 8v9" fill="#e8ddff" stroke="currentColor" strokeWidth="2.5" />
        <path d="M53 71h15" stroke="#a187d6" strokeWidth="3" strokeLinecap="round" />
        <path d="M49 81h22" stroke="#c5b4e8" strokeWidth="2" strokeLinecap="round" />
        <path d="M60 58c-8 5-8 12 0 16 8-4 8-11 0-16z" fill="#dbcdf5" />
      </>
    );
  } else if (normalizedCategory.includes("beverage")) {
    artwork = (
      <>
        <path d="M42 36h37l-4 69a9 9 0 0 1-9 9H55a9 9 0 0 1-9-9z" fill="#fff" stroke="currentColor" strokeWidth="2.5" />
        <path d="m57 36 13-17" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
        <path d="M49 65h24l-2 23H51z" fill="#e1f2ff" />
        <path d="M53 77h16" stroke="#6ca6d4" strokeWidth="2" strokeLinecap="round" />
        <path d="M61 57c-7-6-13 3-4 7m5-7c7-6 13 3 4 7" fill="none" stroke="#87b6d8" strokeWidth="2" strokeLinecap="round" />
      </>
    );
  } else if (normalizedCategory.includes("snack")) {
    artwork = (
      <>
        <path d="m40 29 42 4 8 76-27 12-30-17z" fill="#fff" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" />
        <path d="m40 29 42 4-2 14-42-4z" fill="#f7d99a" />
        <path d="m37 104 31 17 27-12-2-15-53-5z" fill="#f4c76e" />
        <circle cx="60" cy="72" r="16" fill="#fff3d8" />
        <path d="M53 74c4-7 10-8 15-2m-13 8c4-3 8-3 12 0" fill="none" stroke="#d69a41" strokeWidth="2" strokeLinecap="round" />
      </>
    );
  } else if (normalizedCategory.includes("fruit")) {
    artwork = (
      <>
        <circle cx="49" cy="76" r="21" fill="#f6aa70" stroke="currentColor" strokeWidth="2" />
        <circle cx="75" cy="80" r="19" fill="#f4cf62" stroke="currentColor" strokeWidth="2" />
        <path d="M58 56c-1-13 7-20 18-19-2 10-8 16-18 19z" fill="#8fbd85" stroke="currentColor" strokeWidth="1.5" />
        <path d="M61 58c4-9 9-14 15-17" fill="none" stroke="#658f6c" strokeWidth="2" />
        <path d="M35 103h56" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
      </>
    );
  } else if (normalizedCategory.includes("vegetable")) {
    artwork = (
      <>
        <path d="M61 106c-25-6-30-31-12-46 8 7 13 17 12 46z" fill="#87bd82" stroke="currentColor" strokeWidth="2" />
        <path d="M62 105c-3-26 12-48 33-47 2 23-9 41-33 47z" fill="#73aa78" stroke="currentColor" strokeWidth="2" />
        <path d="M62 108c-14-21-7-43 9-51 12 16 11 34-9 51z" fill="#9bc982" stroke="currentColor" strokeWidth="2" />
        <path d="M61 111V56m0 42 23-31m-23 27L47 68" fill="none" stroke="#4f885e" strokeWidth="2" strokeLinecap="round" />
      </>
    );
  } else if (normalizedCategory.includes("home care")) {
    artwork = (
      <>
        <path d="M47 45h35l6 60a9 9 0 0 1-9 10H49a9 9 0 0 1-9-10z" fill="#fff" stroke="currentColor" strokeWidth="2.5" />
        <path d="M54 45v-8a7 7 0 0 1 7-7h10v15" fill="#d8f0e8" stroke="currentColor" strokeWidth="2.5" />
        <path d="M52 69h24v23H52z" fill="#e8f7f2" />
        <path d="M57 80h14m-11-6h8" stroke="#64ae91" strokeWidth="2" strokeLinecap="round" />
        <path d="M39 48h50" stroke="#78bea0" strokeWidth="3" />
      </>
    );
  } else {
    artwork = (
      <>
        <path d="m32 53 9 53h48l9-53z" fill="#fff" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" />
        <path d="M47 54V42a17 17 0 0 1 34 0v12" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
        <circle cx="53" cy="72" r="7" fill="#f0c36b" />
        <path d="M66 67c8 0 12 6 12 13-8 0-13-5-12-13z" fill="#86b590" />
        <path d="M48 91h30" stroke="#b5c7e6" strokeWidth="3" strokeLinecap="round" />
      </>
    );
  }

  return (
    <svg viewBox="0 0 120 140" className="rec-category-illustration" role="img" aria-label={`${category || "Product"} category illustration`}>
      <ellipse cx="60" cy="120" rx="39" ry="7" fill="rgba(44, 68, 107, 0.08)" />
      {artwork}
    </svg>
  );
}

function RecommendationVisual({ brand, category, rank, score, type }) {
  return (
    <div className={`rec-product-visual rec-visual-${type}`}>
      <CategoryIllustration category={category} />
      <span className="rec-visual-rank">#{rank}</span>
      {score && (
        <span className="rec-visual-score">
          <IconAI size={12} color="currentColor" />
          <span><small>AI Match</small><strong>{score}</strong></span>
        </span>
      )}
      <span className="rec-visual-caption">
        {brand && <strong>{brand}</strong>}
        <small>{category || "Category visual"} · not a product photo</small>
      </span>
    </div>
  );
}

function RecommendationMetricIcon({ type }) {
  if (type === "crossSell") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M3 9h18l-2 10H5L3 9Z" />
        <path d="m6 9 3-5m9 5-3-5M8 13v3m4-3v3m4-3v3" />
      </svg>
    );
  }
  if (type === "upsell") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M3 17 9 11l4 4 8-9" />
        <path d="M15 6h6v6" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3Z" />
      <path d="m19 14 .9 2.1L22 17l-2.1.9L19 20l-.9-2.1L16 17l2.1-.9L19 14Z" />
    </svg>
  );
}

function RecommendationSkeletons() {
  return (
    <div className="rec-cards-grid-3col rec-skeleton-grid" aria-label="Loading recommendations">
      {[0, 1, 2].map((item) => (
        <div className="rec-skeleton-card" key={item} aria-hidden="true">
          <span className="rec-skeleton-visual" />
          <span className="rec-skeleton-line rec-skeleton-short" />
          <span className="rec-skeleton-line rec-skeleton-title" />
          <span className="rec-skeleton-line rec-skeleton-price" />
          <span className="rec-skeleton-box" />
          <span className="rec-skeleton-line rec-skeleton-footer" />
        </div>
      ))}
    </div>
  );
}

function getProductBrandAndCategory(item) {
  const productClass = item.product_class || item.product_label || "";
  const parts = productClass.split(/\s+-\s+/);
  return {
    brand: parts.length > 1 ? parts[0] : "",
    category: parts.length > 1 ? parts.slice(1).join(" - ") : "",
    label: productClass,
  };
}

function getMatchScore(item) {
  if (item.similarity_percentage === undefined || item.similarity_percentage === null) {
    return null;
  }
  const value = String(item.similarity_percentage);
  return value.includes("%") ? value : `${value}%`;
}

export default function RecommendationsPage({
  filters,
  setFilters,
  filterOptions,
  resetFilters,
  recBrand,
  setRecBrand,
  recCategory,
  setRecCategory,
  recTopN,
  setRecTopN,
  recTab,
  setRecTab,
  recLoading,
  recError,
  recData,
  fetchRecommendations,
}) {
  const activeTab = tabs.find((tab) => tab.key === recTab) || tabs[0];
  const currentRecommendations = recData?.[activeTab.dataKey] || [];
  const counts = tabs.map((tab) => ({
    ...tab,
    count: recData?.[tab.dataKey]?.length || 0,
  }));
  const selectedProduct = recData?.input_product;
  const selectedCategory = selectedProduct?.category || recCategory;
  const selectedProductLabel =
    selectedProduct?.brand && selectedProduct?.category
      ? `${selectedProduct.brand} - ${selectedProduct.category}`
      : selectedProduct?.product_label || `${recBrand} - ${recCategory}`;

  return (
    <div className="page-container rec-page-wrap">
      <header className="rec-header-block">
        <h1 className="rec-main-title">
          <span className="rec-title-icon">
            <IconRecommendations size={19} color="#6b56b7" />
            <span aria-hidden="true">✦</span>
          </span>
          Product Recommendations
        </h1>
        <p className="rec-main-subtitle">
          Turn purchase patterns into smarter cross-sell and upsell opportunities.
        </p>
        <p className="rec-header-explanation">
          Discover products relevant to your selection and identify
          opportunities to increase basket value.
        </p>
      </header>

      <FilterBar
        filters={filters}
        setFilters={setFilters}
        filterOptions={filterOptions}
        resetFilters={resetFilters}
      />

      <section className="rec-selection-card">
        <div className="rec-section-heading">
          <span className="rec-setup-icon">
            <IconAI size={17} color="#4776e6" />
          </span>
          <div>
            <h2>Recommendation Setup</h2>
            <p>
              Choose a product to discover similar products and sales
              opportunities.
            </p>
          </div>
        </div>
        <div className="rec-selection-grid">
          <div className="rec-input-group">
            <label className="rec-label" htmlFor="rec-brand">Target Brand</label>
            <select
              id="rec-brand"
              className="rec-select"
              value={recBrand}
              onChange={(event) => setRecBrand(event.target.value)}
            >
              {[
                "Amul",
                "Britannia",
                "HUL",
                "ITC",
                "Nestle",
                "Parle",
                "PepsiCo",
                "Tata",
              ].map((brand) => (
                <option key={brand} value={brand}>{brand}</option>
              ))}
            </select>
          </div>

          <div className="rec-input-group">
            <label className="rec-label" htmlFor="rec-category">Category</label>
            <select
              id="rec-category"
              className="rec-select"
              value={recCategory}
              onChange={(event) => setRecCategory(event.target.value)}
            >
              {[
                "Beverages",
                "Dairy",
                "Fruits",
                "Grocery",
                "Home Care",
                "Personal Care",
                "Snacks",
                "Vegetables",
              ].map((category) => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          <div className="rec-input-group">
            <label className="rec-label" htmlFor="rec-top-n">Top Recommendations</label>
            <select
              id="rec-top-n"
              className="rec-select"
              value={recTopN}
              onChange={(event) => setRecTopN(Number(event.target.value))}
            >
              {[3, 5, 8, 10].map((count) => (
                <option key={count} value={count}>Top {count}</option>
              ))}
            </select>
          </div>

          <button
            className="btn-primary rec-action-btn"
            onClick={() => fetchRecommendations(recBrand, recCategory, recTopN)}
            disabled={recLoading}
          >
            <IconAI size={16} color="currentColor" />
            {recLoading ? "Generating..." : "Generate Insights"}
          </button>
        </div>
      </section>

      {recError && (
        <div className="callout-banner banner-danger rec-error" role="alert">
          {recError}
        </div>
      )}

      {recLoading && !recData && (
        <section className="rec-loading-section" role="status">
          <div className="rec-loading-heading">
            <span className="rec-state-spinner" />
            <div>
              <strong>Preparing recommendations</strong>
              <p>Analyzing available product purchasing patterns.</p>
            </div>
          </div>
          <RecommendationSkeletons />
        </section>
      )}

      {recData && !selectedProduct && (
        <div className="rec-empty-state">
          <IconRecommendations size={22} color="#8290a2" />
          <h3>Recommendations are unavailable</h3>
          <p>The recommendation response did not include a selected product.</p>
        </div>
      )}

      {recData && selectedProduct && (
        <div className="rec-results-section">
          <section className="rec-selected-hero">
            <div className="rec-selected-visual">
              <CategoryIllustration category={selectedCategory} />
              <span className="rec-selected-visual-label">{selectedCategory}</span>
              <span className="rec-selected-image-note">
                Category illustration · not a product photo
              </span>
            </div>
            <div className="rec-selected-info">
              <div className="rec-selected-heading">
                <span className="rec-summary-tag">Selected Product</span>
                <span className="rec-ai-badge">
                  <IconAI size={12} color="currentColor" /> AI Recommendation
                </span>
              </div>
              <h2>{selectedProductLabel}</h2>
              <p className="rec-selected-description">
                AI is finding products that best match this product.
              </p>
              <span className="rec-selected-class">
                Product Class: {selectedProduct.product_class || selectedProductLabel}
              </span>
            </div>
            <div className="rec-selected-metrics">
              {formatCurrency(selectedProduct.avg_selling_price) && (
                <div>
                  <span>Average Selling Price</span>
                  <strong>{formatCurrency(selectedProduct.avg_selling_price)}</strong>
                </div>
              )}
              {selectedProduct.avg_margin_pct !== undefined &&
                selectedProduct.avg_margin_pct !== null && (
                  <div>
                    <span>Average Margin</span>
                    <strong>{selectedProduct.avg_margin_pct}%</strong>
                  </div>
                )}
              <div>
                <span>Recommendation Engine</span>
                <strong className="rec-engine-pill">
                  {recData.model_type ? "Hybrid ML Engine" : "Collaborative & Basket AI"}
                </strong>
              </div>
            </div>
          </section>

          <section className="rec-summary-counts" aria-label="Recommendation counts">
            <div className="rec-count-intro">
              <span className="rec-eyebrow">At a glance</span>
              <h2>AI Recommendation Summary</h2>
            </div>
            {counts.map((tab) => {
              const metricIconType =
                tab.key === "cross_sell" ? "crossSell" :
                tab.key === "upsell" ? "upsell" : "similar";
              const summaryLabel =
                tab.key === "cross_sell" ? "Cross-Sell Opportunities" :
                tab.key === "upsell" ? "Upsell Opportunities" : "Similar Products";
              return (
                <div className={`rec-count-card rec-count-${metricIconType}`} key={tab.key}>
                  <span className="rec-count-icon">
                    <RecommendationMetricIcon type={metricIconType} />
                  </span>
                  <strong>{tab.count}</strong>
                  <span>{summaryLabel}</span>
                </div>
              );
            })}
          </section>

          <section className="rec-recommendation-section">
            <div className="rec-recommendation-heading">
              <div>
                <span className="rec-eyebrow">Product opportunities</span>
                <h2>Explore Recommendations</h2>
              </div>
              <span className="rec-results-count">
                {currentRecommendations.length} results
              </span>
            </div>

            <div className="rec-tabs-container">
              <div className="rec-tabs-nav" role="tablist" aria-label="Recommendation type">
                {tabs.map((tab) => (
                  <button
                    key={tab.key}
                    className={`rec-tab-btn ${recTab === tab.key ? "active" : ""}`}
                    onClick={() => setRecTab(tab.key)}
                    role="tab"
                    aria-selected={recTab === tab.key}
                  >
                    <span className="rec-tab-copy">
                      <strong>{tab.title}</strong>
                      <small>{tab.subtitle}</small>
                    </span>
                    <span className="rec-tab-count">
                      {recData[tab.dataKey]?.length || 0}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {recLoading ? (
              <RecommendationSkeletons />
            ) : currentRecommendations.length > 0 ? (
              <div className="rec-cards-grid-3col">
                {currentRecommendations.map((item, index) => {
                  const product = getProductBrandAndCategory(item);
                  const score =
                    activeTab.cardType === "similar" ? getMatchScore(item) : null;
                  const rationale = item.rationale || item.rule_explanation;
                  const topChannel = item.top_fulfillment_channel;
                  const revenue = formatRevenue(item.total_revenue);
                  const margin =
                    item.avg_margin_pct !== undefined &&
                    item.avg_margin_pct !== null
                      ? `${item.avg_margin_pct}%`
                      : null;
                  const isCrossSell = activeTab.cardType === "cross-sell";
                  const isUpsell = activeTab.cardType === "upsell";

                  return (
                    <article className={`rec-hero-card rec-card-${activeTab.cardType}`} key={item.rank || item.product_class || index}>
                      <RecommendationVisual
                        brand={product.brand}
                        category={product.category}
                        rank={item.rank || index + 1}
                        score={score}
                        type={activeTab.cardType}
                      />

                      <div className="rec-card-content">
                        <div className="rec-card-top-bar">
                          <span className="rec-card-kind">
                            {isCrossSell
                              ? "Frequently Bought Together"
                              : isUpsell
                                ? "Upsell Opportunity"
                                : "Similar Product"}
                          </span>
                          {isUpsell && (
                            <span className="rec-opportunity-badge">Higher Value</span>
                          )}
                        </div>

                        <h3 className="rec-card-product-title">
                          {product.label || "Product name unavailable"}
                        </h3>
                        <p className="rec-card-product-class">
                          {product.category && product.brand
                            ? `${product.category} · ${product.brand}`
                            : product.category || product.brand || item.product_label || ""}
                        </p>

                        <div className="rec-card-price-row">
                          {formatCurrency(item.avg_selling_price) && (
                            <div>
                              <strong>{formatCurrency(item.avg_selling_price)}</strong>
                              <span>Average Selling Price</span>
                            </div>
                          )}
                          {isUpsell &&
                            item.price_diff_val !== undefined &&
                            item.price_diff_val !== null && (
                              <span className="rec-price-difference">
                                Price difference: {formatCurrency(item.price_diff_val)}
                              </span>
                            )}
                        </div>

                        {isCrossSell && (
                          <p className="rec-cross-sell-intro">
                            Products customers also tend to buy.
                          </p>
                        )}
                        {isUpsell && (
                          <p className="rec-cross-sell-intro">
                            A higher-value option identified by the existing recommendations.
                          </p>
                        )}

                        <div className="rec-why-box">
                          <div className="rec-why-label">
                            <IconAI size={13} color="currentColor" />
                            Why This Product?
                          </div>
                          <p className="rec-why-text">
                            {rationale || "No recommendation rationale was returned."}
                          </p>
                        </div>

                        <div className="rec-card-meta-footer">
                          {!isCrossSell && (
                            <div className="rec-business-metrics">
                              {topChannel && (
                                <div>
                                  <span>Top Channel</span>
                                  <strong>{topChannel}</strong>
                                </div>
                              )}
                              {revenue && (
                                <div>
                                  <span>Revenue</span>
                                  <strong>{revenue}</strong>
                                </div>
                              )}
                              {margin && (
                                <div>
                                  <span>Margin</span>
                                  <strong>{margin}</strong>
                                </div>
                              )}
                            </div>
                          )}
                          {isCrossSell && (
                            <div className="rec-purchase-pattern">
                              <span className="rec-purchase-pattern-title">Purchase Pattern</span>
                              <div className="rec-meta-pills-row">
                              {item.confidence_pct !== undefined &&
                                item.confidence_pct !== null && (
                                  <span className="rec-submeta-tag">
                                    Confidence <strong>{item.confidence_pct}</strong>
                                  </span>
                                )}
                              {item.confidence !== undefined &&
                                item.confidence !== null &&
                                item.confidence_pct === undefined && (
                                  <span className="rec-submeta-tag">
                                    Confidence <strong>{`${Math.round(item.confidence * 100)}%`}</strong>
                                  </span>
                                )}
                              {item.lift !== undefined && item.lift !== null && (
                                <span className="rec-submeta-tag">
                                  Lift <strong>{item.lift}x</strong>
                                </span>
                              )}
                              {(item.support_pct ?? item.support) !== undefined &&
                                (item.support_pct ?? item.support) !== null && (
                                  <span className="rec-submeta-tag">
                                    Support <strong>{item.support_pct ?? item.support}</strong>
                                  </span>
                                )}
                              </div>
                            </div>
                          )}
                          {isUpsell && (
                            <div className="rec-meta-pills-row">
                              {margin && (
                                <span className="rec-submeta-tag">
                                  Margin <strong>{margin}</strong>
                                </span>
                              )}
                              {item.margin_diff_pct !== undefined &&
                                item.margin_diff_pct !== null && (
                                  <span className="rec-submeta-tag">
                                    Margin difference <strong>{item.margin_diff_pct}%</strong>
                                  </span>
                                )}
                              {topChannel && (
                                <span className="rec-submeta-tag">
                                  Top Channel <strong>{topChannel}</strong>
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="rec-empty-state">
                <IconRecommendations size={22} color="#8290a2" />
                <h3>No recommendations found</h3>
                <p>Try another product or adjust your filters.</p>
              </div>
            )}
          </section>

          <aside className="rec-business-note">
            <span className="rec-business-note-icon">
              <IconSales size={17} color="#4776e6" />
            </span>
            <div>
              <strong>How to Use These Recommendations</strong>
              <p>
                Use similar-product recommendations to expand product
                discovery, cross-sell suggestions to increase basket size, and
                upsell opportunities to guide customers toward higher-value
                purchases.
              </p>
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}
