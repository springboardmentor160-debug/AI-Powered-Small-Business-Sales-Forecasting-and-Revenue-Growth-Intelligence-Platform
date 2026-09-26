import React, { useEffect, useState } from "react";
import { getSegmentationSummary, getSegmentationCustomers, getSegments } from "../api";

export default function CustomerSegmentation() {
  const [summary, setSummary] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [segmentsAgg, setSegmentsAgg] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [sumData, custData, segsData] = await Promise.all([
          getSegmentationSummary(),
          getSegmentationCustomers(),
          getSegments(),
        ]);
        setSummary(sumData);
        setCustomers(custData);
        setSegmentsAgg(segsData);
      } catch (err) {
        setError(err.message || "Failed to load customer segmentation data.");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-200 animate-pulse mb-6">
        <div className="h-6 bg-slate-200 rounded w-1/4 mb-4"></div>
        <div className="h-20 bg-slate-100 rounded mb-4"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-700 p-4 rounded-xl border border-red-200 mb-6">
        <p className="font-medium">Customer Segmentation Notice:</p>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  const getSegmentBadgeColor = (segmentName) => {
    if (segmentName.includes("VIP") || segmentName.includes("Loyal")) {
      return "bg-purple-100 text-purple-800 border-purple-200";
    }
    if (segmentName.includes("Regular")) {
      return "bg-blue-100 text-blue-800 border-blue-200";
    }
    if (segmentName.includes("Occasional")) {
      return "bg-emerald-100 text-emerald-800 border-emerald-200";
    }
    return "bg-amber-100 text-amber-800 border-amber-200";
  };

  const maxCustCount = Math.max(...(segmentsAgg.map(s => s.customer_count) || [1]), 1);

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-200 mb-6">
      <div className="flex flex-wrap items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div>
          <h2 className="text-xl font-bold text-slate-900">
            🎯 Customer Segments & Behavioral Intelligence
          </h2>
          <p className="text-sm text-slate-500">
            K-Means ($K=4$) & Hierarchical Clustering with Aggregated Performance Metrics (Milestone 2)
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 bg-indigo-50 text-indigo-700 text-xs font-semibold rounded-full border border-indigo-200">
            {summary?.total_customers || customers.length} Total Customers
          </span>
          <span className="px-3 py-1 bg-slate-100 text-slate-700 text-xs font-semibold rounded-full border border-slate-200">
            4 Segments Active
          </span>
        </div>
      </div>

      {/* Segment Distribution Chart & Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Left 2 Cols: Cards */}
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {summary?.segments?.map((seg, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-2">
                <span
                  className={`inline-block px-2.5 py-0.5 text-xs font-bold rounded-full border ${getSegmentBadgeColor(
                    seg.segment
                  )}`}
                >
                  {seg.segment}
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  {Math.round((seg.customer_count / (summary?.total_customers || 1)) * 100)}% of total
                </span>
              </div>
              <div className="text-2xl font-extrabold text-slate-900">
                {seg.customer_count}{" "}
                <span className="text-xs font-normal text-slate-500">Customers</span>
              </div>
              <div className="mt-3 text-xs text-slate-600 space-y-1.5 pt-2 border-t border-slate-200">
                <div className="flex justify-between">
                  <span>Avg Purchase Value:</span>
                  <span className="font-semibold text-slate-900">
                    ₹{seg.avg_purchase_value?.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Avg Order Frequency:</span>
                  <span className="font-semibold text-slate-900">
                    {seg.avg_purchase_frequency?.toFixed(1)} orders
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Activity Span:</span>
                  <span className="font-semibold text-slate-900">
                    {seg.avg_activity_days?.toFixed(0)} days
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Right 1 Col: Customer Count by Segment Chart */}
        <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-1">
              📊 Customer Count by Segment
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Real-time distribution from <code>/segments</code> API
            </p>
            <div className="space-y-3">
              {segmentsAgg.map((seg, idx) => {
                const pct = Math.round((seg.customer_count / maxCustCount) * 100);
                return (
                  <div key={idx}>
                    <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                      <span className="truncate max-w-[140px]">{seg.segment}</span>
                      <span className="font-bold text-slate-900">{seg.customer_count} cust (₹{seg.avg_purchase_value})</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
                      <div
                        className="bg-indigo-600 h-2.5 rounded-full transition-all duration-500"
                        style={{ width: `${Math.max(pct, 15)}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-200 text-xs text-slate-500 text-center">
            Segmented via K-Means & Hierarchical ML
          </div>
        </div>
      </div>

      {/* Segmented Customer Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="bg-slate-100 text-slate-700 font-semibold border-b border-slate-200">
              <th className="py-2.5 px-3">Customer ID</th>
              <th className="py-2.5 px-3">Orders (Frequency)</th>
              <th className="py-2.5 px-3">Total Value</th>
              <th className="py-2.5 px-3">Activity Days</th>
              <th className="py-2.5 px-3">K-Means Cluster</th>
              <th className="py-2.5 px-3">Hierarchical Cluster</th>
              <th className="py-2.5 px-3">Assigned Segment</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {customers.map((c, i) => (
              <tr key={i} className="hover:bg-slate-50 transition-colors">
                <td className="py-2.5 px-3 font-mono font-semibold text-slate-900">
                  {c.customer_id}
                </td>
                <td className="py-2.5 px-3 text-slate-700">{c.purchase_frequency}</td>
                <td className="py-2.5 px-3 text-slate-900 font-semibold">
                  ₹{c.purchase_value?.toFixed(2)}
                </td>
                <td className="py-2.5 px-3 text-slate-700">{c.customer_activity_days} days</td>
                <td className="py-2.5 px-3">
                  <span className="px-2 py-0.5 text-xs rounded font-mono bg-slate-100 text-slate-800">
                    Cluster {c.cluster}
                  </span>
                </td>
                <td className="py-2.5 px-3">
                  <span className="px-2 py-0.5 text-xs rounded font-mono bg-slate-100 text-slate-800">
                    Cluster {c.cluster_hierarchical}
                  </span>
                </td>
                <td className="py-2.5 px-3">
                  <span
                    className={`px-2.5 py-0.5 text-xs font-semibold rounded-full border ${getSegmentBadgeColor(
                      c.segment
                    )}`}
                  >
                    {c.segment}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
