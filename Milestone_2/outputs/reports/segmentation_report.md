# Customer Segmentation Analysis Report (Milestone 2)

## Executive Summary
This report presents the empirical customer segmentation results generated for MarketMind AI using machine learning clustering algorithms (**K-Means** and **Hierarchical Agglomerative Clustering**) on historical transaction data from **793** unique customers.

## Key Segmentation Metrics
* **Total Customers Analyzed:** 793
* **Optimal Cluster Count (k):** 2
* **K-Means Silhouette Score:** 0.2733
* **Hierarchical Clustering Silhouette Score:** 0.3013

---

## Segment Breakdown & Behavioral Profiles

### Segment: High-Value Champions (Cluster 0)
* **Customer Count:** 528 (66.58% of customer base)
* **Total Revenue Generated:** $2,058,205.12 (89.60% of total revenue)
* **Mean Recency:** 92.6 days
* **Mean Order Frequency:** 7.4 orders
* **Mean Customer Spend:** $3,898.12
* **Average Order Value (AOV):** $568.87
* **Average Discount Received:** 14.9%

### Segment: Low-Activity / At-Risk Customers (Cluster 1)
* **Customer Count:** 265 (33.42% of customer base)
* **Total Revenue Generated:** $238,995.75 (10.40% of total revenue)
* **Mean Recency:** 257.7 days
* **Mean Order Frequency:** 4.2 orders
* **Mean Customer Spend:** $901.87
* **Average Order Value (AOV):** $243.53
* **Average Discount Received:** 17.5%

---

## Business Insights & Strategic Recommendations
1. **High-Value Champions Drive Business Revenue:** The primary customer cluster accounts for almost 90% of total revenue ($2,058,205.12) despite comprising ~66.6% of the customer base. These high-frequency buyers have high average order values ($568.87) and low sensitivity to heavy discounts.
   * **Action:** Launch a VIP Loyalty Program offering early product access and dedicated support to preserve retention.
2. **At-Risk / Low-Activity Customer Win-Back:** Approximately 33.4% of customers haven't purchased in over 250 days and generate only 10.4% of revenue.
   * **Action:** Trigger targeted re-engagement email campaigns with personalized discounts on their historically purchased categories.
