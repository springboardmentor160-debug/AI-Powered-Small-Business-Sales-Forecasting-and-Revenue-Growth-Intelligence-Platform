import React from "react";
import { IconFilter, IconRefresh } from "./Icons";

export default function FilterBar({ filters, setFilters, filterOptions, resetFilters }) {
  return (
    <div className="filter-bar-container">
      <div className="filter-bar-left">
        <div className="filter-icon-badge">
          <IconFilter size={16} color="#3b82f6" />
        </div>
        <span className="filter-title">Global Filters</span>
      </div>

      <div className="filter-controls-row">
        {/* City Filter */}
        <div className="filter-group">
          <label>City</label>
          <select
            value={filters.city}
            onChange={(e) => setFilters({ ...filters, city: e.target.value })}
          >
            <option value="All">All Cities</option>
            {filterOptions.cities.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        {/* Category Filter */}
        <div className="filter-group">
          <label>Category</label>
          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
          >
            <option value="All">All Categories</option>
            {filterOptions.categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        {/* Store Format Filter */}
        <div className="filter-group">
          <label>Store Format</label>
          <select
            value={filters.storeFormat}
            onChange={(e) =>
              setFilters({ ...filters, storeFormat: e.target.value })
            }
          >
            <option value="All">All Formats</option>
            {filterOptions.store_formats.map((sf) => (
              <option key={sf} value={sf}>
                {sf}
              </option>
            ))}
          </select>
        </div>

        {/* Channel Filter */}
        <div className="filter-group">
          <label>Channel</label>
          <select
            value={filters.channel}
            onChange={(e) => setFilters({ ...filters, channel: e.target.value })}
          >
            <option value="All">All Channels</option>
            {filterOptions.channels.map((ch) => (
              <option key={ch} value={ch}>
                {ch}
              </option>
            ))}
          </select>
        </div>

        {/* Payment Mode Filter */}
        <div className="filter-group">
          <label>Payment Mode</label>
          <select
            value={filters.paymentMode}
            onChange={(e) =>
              setFilters({ ...filters, paymentMode: e.target.value })
            }
          >
            <option value="All">All Modes</option>
            {filterOptions.payment_modes.map((pm) => (
              <option key={pm} value={pm}>
                {pm}
              </option>
            ))}
          </select>
        </div>

        <button className="reset-filters-btn" onClick={resetFilters} title="Reset all filters">
          <IconRefresh size={14} />
          <span>Reset</span>
        </button>
      </div>
    </div>
  );
}
