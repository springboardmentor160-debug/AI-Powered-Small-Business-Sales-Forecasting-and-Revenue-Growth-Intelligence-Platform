import React, { useEffect, useState } from "react";
import { getSegmentationSummary, getSegmentationCustomers } from "../api";

export default function CustomerSegmentation() {
  const [summary, setSummary] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [sumData, custData] = await Promise.all([
          getSegmentationSummary(),
          getSegmentationCustomers(),
        ]);
        setSummary(sumData);
        setCustomers(custData);
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
      <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-200 animate-pulse">
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

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-200 mb-6">
      <div className="flex flex-wrap items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div>
          <h2 className="text-xl font-bold text-slate-900">
            🎯 Customer Segmentation & Behavioral Intelligence
          </h2>
          <p className="text-sm text-slate-500">
            K-Means ($K=4$) & Hierarchical Agglomerative Clustering (Day 1–4)
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 bg-indigo-50 text-indigo-700 text-xs font-semibold rounded-full border border-indigo-200">
            {summary?.total_customers || customers.length} Total Customers
          </span>
          <span className="px-3 py-1 bg-slate-100 text-slate-700 text-xs font-semibold rounded-full border border-slate-200">
            4 Clusters Identified
          </span>
        </div>
      </div>

      {/* Segment Summaries */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {summary?.segments?.map((seg, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:shadow-md transition-shadow"
          >
            <span
              className={`inline-block px-2.5 py-0.5 text-xs font-bold rounded-full border mb-2 ${getSegmentBadgeColor(
                seg.segment
              )}`}
            >
              {seg.segment}
            </span>
            <div className="text-2xl font-extrabold text-slate-900">
              {seg.customer_count}{" "}
              <span className="text-xs font-normal text-slate-500">
                ({Math.round((seg.customer_count / (summary?.total_customers || 1)) * 100)}%)
              </span>
            </div>
            <div className="mt-2 text-xs text-slate-600 space-y-1">
              <div className="flex justify-between">
                <span>Avg Revenue:</span>
                <span className="font-semibold text-slate-900">
                  ${seg.avg_purchase_value?.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Avg Orders:</span>
                <span className="font-semibold text-slate-900">
                  {seg.avg_purchase_frequency?.toFixed(1)}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Active Days:</span>
                <span className="font-semibold text-slate-900">
                  {seg.avg_activity_days?.toFixed(0)} days
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Segmented Customer Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="bg-slate-100 text-slate-700 font-semibold border-b border-slate-200">
              <th className="py-2.5 px-3">Customer ID</th>
              <th className="py-2.5 px-3">Orders (Frequency)</th>
              <th className="py-2.5 px-3">Total Value ($)</th>
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
                  ${c.purchase_value?.toFixed(2)}
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
