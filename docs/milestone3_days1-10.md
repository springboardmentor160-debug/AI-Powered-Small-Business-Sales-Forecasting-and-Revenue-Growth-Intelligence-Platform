# Milestone 3 (Days 1–10) Technical Documentation & Review Guide
## MarketMind AI — Small Business Sales Intelligence Platform

**Author**: Sultan  
**Branch**: `feature/milestone-3-sultan`  
**Milestone Focus**: Product Recommendations, Churn Prediction & Retention Intelligence, Sales Anomaly Detection  

---

## Executive Summary

Milestone 3 extends the **MarketMind AI** platform from the data foundation (Milestone 1) and customer segmentation & multi-model sales forecasting (Milestone 2) into operational predictive intelligence. It introduces three core AI capabilities:

1. **Hybrid Product Recommendation Engine**: Combines User-Based Collaborative Filtering (Cosine Similarity) with Market Basket Association Rule Mining (`mlxtend` Apriori) to recommend personalized, unseen products to retail clients.
2. **Customer Churn Prediction & Retention Risk Modeling**: Formulates customer inactivity into a verifiable binary churn target, trains and compares three classifiers (**Logistic Regression**, **Random Forest**, and **XGBoost**), selects the winning model prioritizing **Recall**, predicts continuous churn probabilities, and maps customers into actionable risk categories cross-referenced with Milestone 2 segments.
3. **Multi-Method Anomaly Detection & Review Alert System**: Pairs 1D Statistical Z-Score tracking on transaction revenue with 3D **Isolation Forest** outlier modeling across `[quantity, unit_price, total_amount]`, generating human-in-the-loop review alerts with transparent priority ratings.

All implementations strictly use real dataset records without fabrication, respect small-data statistical realities, maintain role-based access control (RBAC), and integrate into the existing FastAPI backend and React frontend.

---

## 1. Recommendation Engine Architecture

The recommendation engine answers two complementary commercial questions for small business operators:
- *"What did similar customers buy that this customer hasn't purchased yet?"* &rarr; **Collaborative Filtering**
- *"What products are frequently purchased together in transactions?"* &rarr; **Association Rule Mining**

```
+-------------------------------------------------------------+
|                  Clean Sales Transactions                   |
|           (order_id, customer_id, product_name, quantity)   |
+------------------------------+------------------------------+
                               |
        +----------------------+----------------------+
        |                                             |
        v                                             v
+-------------------------------+             +-------------------------------+
|    Customer-Product Matrix    |             |      Order Basket Matrix      |
|  (customer_id x product_name) |             |   (order_id x product_name)   |
+---------------+---------------+             +---------------+---------------+
                |                                             |
                v                                             v
+-------------------------------+             +-------------------------------+
|   Cosine Similarity Matrix    |             |     Apriori Frequent Itemsets |
|    (User-Based Filtering)     |             |    & Association Rules (AR)   |
+---------------+---------------+             +---------------+---------------+
                |                                             |
                +----------------------+----------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |    Hybrid Combination Engine      |
                     |  - Candidate Item Pooling         |
                     |  - Exclusion of Already Purchased |
                     |  - Synergy Boost for Both Sources |
                     |  - Top N Ranked Recommendations   |
                     +-----------------------------------+
```

---

## 2. Customer-Product Matrix

The customer-product matrix summarizes total unit demand per customer across all unique catalog items:

$$\mathbf{M}_{i, j} = \sum \text{quantity of product } j \text{ purchased by customer } i$$

Missing combinations are filled with `0.0`. In the project's cleaned sales data:

| Customer ID | Marker Box | Notebook A | Pen Set | Stapler |
|:---|:---:|:---:|:---:|:---:|
| **C001** | 0.0 | 4.0 | 0.0 | 0.0 |
| **C002** | 0.0 | 0.0 | 12.0 | 0.0 |
| **C003** | 8.0 | 0.0 | 0.0 | 0.0 |
| **C004** | 0.0 | 0.0 | 0.0 | 1.0 |
| **C005** | 0.0 | 0.0 | 4.0 | 0.0 |

---

## 3. Cosine Similarity

Customer purchasing profiles are compared using pairwise cosine similarity:

$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \frac{\sum_{k=1}^P u_k v_k}{\sqrt{\sum_{k=1}^P u_k^2} \sqrt{\sum_{k=1}^P v_k^2}}$$

- **0.0**: Completely orthogonal buying patterns (no shared items).
- **1.0**: Identical product purchasing proportion.

### Pairwise Customer Similarity Matrix:

| Customer | C001 | C002 | C003 | C004 | C005 |
|:---|:---:|:---:|:---:|:---:|:---:|
| **C001** | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| **C002** | 0.00 | 1.00 | 0.00 | 0.00 | **1.00** |
| **C003** | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| **C004** | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| **C005** | 0.00 | **1.00** | 0.00 | 0.00 | 1.00 |

*Key finding*: C002 and C005 both exclusively purchased "Pen Set", yielding a similarity score of 1.00. Customers C001, C003, and C004 purchased distinct products.

---

## 4. Collaborative Filtering

Function: `recommend_products_collaborative(customer_id, top_n=3, sales_df=None)`

### Algorithmic Steps:
1. Locate target customer row in $\mathbf{M}$.
2. Query peer similarity vector from $\mathbf{S}$, excluding target customer.
3. Filter peers where $\text{similarity} > 0.0$.
4. Aggregate candidate products purchased by similar peers:
   $$\text{Score}(p) = \sum_{v \in \text{Peers}} \text{sim}(u, v) \times \mathbf{M}_{v, p}$$
5. **Strict Exclusion**: Filter out products where $\mathbf{M}_{u, p} > 0$ (already purchased by target customer).
6. Rank remaining candidate products descending by score.
7. Return top $N$ items with supporting quantity and peer customer IDs.

### Edge Case Handling:
- **Unknown Customer ID**: Returns empty list with 200/404 friendly JSON message: `"Customer '...' not found in purchase history."`
- **Zero Similarity Peers**: If all peer similarities are 0.0, returns an informative explanation: `"No peer customers with similar buying patterns found (zero similarity)."`
- **No Unseen Items Remaining**: If peer customers only bought items the target customer already owns, returns: `"Similar peers exist, but no unseen products remain to recommend."`

---

## 5. Association Rule Mining

Implemented using `mlxtend.frequent_patterns.apriori` and `mlxtend.frequent_patterns.association_rules`.

1. **Transaction Basket Representation**: Group transactions by `order_id` and construct binary one-hot indicators:
   $$\mathbf{B}_{\text{order}, \text{product}} \in \{0, 1\}$$
2. **Support Threshold**: Minimum frequency of an itemset:
   $$\text{Support}(X) = \frac{\text{Count of baskets containing } X}{\text{Total Baskets}}$$
3. **Confidence Threshold**:
   $$\text{Confidence}(X \rightarrow Y) = \frac{\text{Support}(X \cup Y)}{\text{Support}(X)}$$
4. **Lift**:
   $$\text{Lift}(X \rightarrow Y) = \frac{\text{Confidence}(X \rightarrow Y)}{\text{Support}(Y)}$$

### Real Dataset Analysis & Honest Small Data Handling:
In the actual 8-order sales dataset (`clean_sales_data.csv`), each historical order contains a single catalog product. Consequently, frequent itemsets of length $\ge 2$ have a support of 0.0.
The pipeline detects this condition and reports:
`"All orders in current transaction dataset contain only 1 item. Association rules require multi-item baskets."`
No fake multi-item orders were fabricated. Full multi-item basket rule extraction was verified using unit tests.

---

## 6. Recommendation Combination Strategy

Function: `recommend_products(customer_id, top_n=3, sales_df=None)`

The hybrid recommender combines candidate item pools from Collaborative Filtering (CF) and Association Rules (AR):

1. **Candidate Score Normalization**:
   $$\bar{S}_{\text{CF}}(p) = \frac{S_{\text{CF}}(p)}{\max(S_{\text{CF}})}, \quad \bar{S}_{\text{AR}}(p) = \frac{S_{\text{AR}}(p)}{\max(S_{\text{AR}})}$$
2. **Synergy Boost**:
   - If product $p$ is recommended by **both** CF and AR:
     $$\text{Combined Score}(p) = \bar{S}_{\text{CF}}(p) + \bar{S}_{\text{AR}}(p) + 0.5$$
     $$\text{Method}(p) = \text{"both"}$$
   - If product $p$ is only in CF: $\text{Combined Score}(p) = \bar{S}_{\text{CF}}(p), \text{Method}(p) = \text{"collaborative\_filtering"}$
   - If product $p$ is only in AR: $\text{Combined Score}(p) = \bar{S}_{\text{AR}}(p), \text{Method}(p) = \text{"association\_rules"}$
3. Sort candidate pool descending by combined score and return top $N$.

---

## 7. Churn Label Definition

Customer churn is defined using actual transaction recency relative to the latest transaction in the dataset (`2026-01-10`):

$$\text{Days Since Last Order} = \max(\text{Order Date}_{\text{Dataset}}) - \max(\text{Order Date}_{\text{Customer}})$$

### Inactivity Window:
In small business retail with a 6-day recorded operational window:
- If $\text{Days Since Last Order} \ge 2$: $\text{churn} = 1$ (Inactive / At-Risk)
- If $\text{Days Since Last Order} < 2$: $\text{churn} = 0$ (Active)

### Distribution on Real Customer Base:
| Customer | Last Order Date | Inactive Days | Churn Label | Segment (Milestone 2) |
|:---|:---:|:---:|:---:|:---|
| **C001** | 2026-01-06 | 4 | **1** | Regular Customers |
| **C002** | 2026-01-07 | 3 | **1** | Occasional Shoppers |
| **C003** | 2026-01-10 | 0 | **0** | VIP / Loyal Customers |
| **C004** | 2026-01-08 | 2 | **1** | At-Risk / Fading Customers |
| **C005** | 2026-01-09 | 1 | **0** | At-Risk / Fading Customers |

*Result*: Both classes are present (3 churned, 2 active), satisfying binary classification requirements.

---

## 8. Churn Behavioral Features

Feature matrix $\mathbf{X}$ extracts customer behavioral patterns without target leakage:
- `purchase_frequency`: Total lifetime order count.
- `purchase_value`: Total cumulative revenue spend (\$).
- `customer_activity_days`: Calendar span from first to last purchase.

*Target Leakage Prevention*: Recency (`days_since_last_order`) was used to construct the ground-truth target label $y$, so it is explicitly excluded from $\mathbf{X}$.

---

## 9. Train/Test Split & Small Dataset Handling

- Applied `train_test_split(X, y, test_size=0.4, random_state=42, stratify=y)`.
- Stratification maintains proportional class representation across partitions (Train: 3 samples, Test: 2 samples).
- If fewer than 2 samples per class exist, the code falls back to non-stratified partitioning to prevent runtime crashes.

---

## 10. Multi-Model Churn Classification

Three distinct algorithms were implemented and trained:

1. **Baseline Logistic Regression**:
   - Standardized using `StandardScaler` to normalize feature scales:
     $$P(y = 1 \mid \mathbf{x}) = \sigma(\mathbf{w}^T \mathbf{x}_{\text{scaled}} + b) = \frac{1}{1 + e^{-(\mathbf{w}^T \mathbf{x}_{\text{scaled}} + b)}}$$
2. **Random Forest Classifier**:
   - `RandomForestClassifier(n_estimators=100, random_state=42)`
   - Ensemble of 100 decorrelated decision trees using bootstrap aggregation.
3. **XGBoost Classifier**:
   - `XGBClassifier(n_estimators=100, learning_rate=0.1, random_state=42, eval_metric="logloss")`
   - Gradient boosted decision trees optimizing regularized log-loss.

---

## 11. Fair Model Evaluation & Selection

All three classifiers were evaluated on the held-out test partition using standard classification metrics:

$$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}, \quad F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

### Test Set Performance Comparison:

| Classifier Model | Precision | Recall | F1-Score | Accuracy | Test Status |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Logistic Regression** | **50.0%** | **100.0%** | **0.6667** | **50.0%** | **Selected** |
| **Random Forest** | 50.0% | 100.0% | 0.6667 | 50.0% | Evaluated |
| **XGBoost** | 50.0% | 100.0% | 0.6667 | 50.0% | Evaluated |

### Selection Rationale — Why Recall is Prioritized:
In customer retention strategy:
- **Cost of a False Negative (Type II error)**: An at-risk customer is missed, receives no outreach, and defects permanently, resulting in lost customer lifetime value (LTV).
- **Cost of a False Positive (Type I error)**: An active customer is contacted with a courtesy check-in or loyalty discount, incurring minimal communication cost.

Therefore, **Recall** is prioritized over Precision. Logistic Regression achieved 100% test recall and is selected as the active model.

---

## 12. Churn Probabilities & Retention Risk Categories

Continuous churn probabilities are computed using `model.predict_proba()`:

| Customer ID | Segment | Spend | Recency | Churn Probability | Retention Risk |
|:---|:---|:---:|:---:|:---:|:---:|
| **C001** | Regular Customers | \$180.00 | 4 days | **0.6814** | **Medium Risk** |
| **C002** | Occasional Shoppers | \$144.00 | 3 days | **0.6140** | **Medium Risk** |
| **C003** | VIP / Loyal Customers | \$240.00 | 0 days | **0.5124** | **Medium Risk** |
| **C004** | At-Risk / Fading Customers | \$85.00 | 2 days | **0.5921** | **Medium Risk** |
| **C005** | At-Risk / Fading Customers | \$48.00 | 1 day | **0.6002** | **Medium Risk** |

### Business Risk Tiers:
- **High Risk**: $\text{Probability} \ge 0.70$
- **Medium Risk**: $0.40 \le \text{Probability} < 0.70$
- **Low Risk**: $\text{Probability} < 0.40$

*Important Guidance*: Churn probability represents statistical attrition likelihood for operational prioritization, not a guarantee of churn.

---

## 13. Cross-Check with Milestone 2 Customer Segments

| Customer Segment | Retention Risk Level | Customer Count | Avg Spend | Avg Churn Probability |
|:---|:---:|:---:|:---:|:---:|
| **At-Risk / Fading Customers** | Medium Risk | 2 | \$66.50 | 59.62% |
| **Occasional Shoppers** | Medium Risk | 1 | \$144.00 | 61.40% |
| **Regular Customers** | Medium Risk | 1 | \$180.00 | 68.14% |
| **VIP / Loyal Customers** | Medium Risk | 1 | \$240.00 | 51.24% |

VIP customers show the lowest attrition probability (51.24%), while regular customers with longer inactivity exhibit higher retention concern (68.14%).

---

## 14. Anomaly Detection Architecture

Two complementary anomaly detection methodologies were implemented:

```
+--------------------------------------------------------------+
|                   Sales Transaction Stream                   |
|           (order_id, quantity, unit_price, total_amount)     |
+------------------------------+-------------------------------+
                               |
        +----------------------+----------------------+
        |                                             |
        v                                             v
+-------------------------------+             +-------------------------------+
|     Statistical Z-Score       |             |       Isolation Forest        |
|  - Univariate total_amount    |             |  - 3D: [qty, price, total]    |
|  - Threshold: |z| > 3.0       |             |  - Contamination: 0.02        |
+---------------+---------------+             +---------------+---------------+
                |                                             |
                +----------------------+----------------------+
                                       |
                                       v
                     +-----------------------------------+
                     |    Cross-Method Anomaly Matrix    |
                     |  - Overlap Tracking               |
                     |  - Severity Rating (High/Medium)  |
                     |  - Actionable Alert Generation    |
                     +-----------------------------------+
```

---

## 15. Statistical Z-Score Detection

Total transaction revenue is calculated:
$$\text{total\_amount} = \text{quantity} \times \text{unit\_price}$$

Store statistics across the 8 sales transactions:
- **Mean ($\mu$)**: \$87.12
- **Standard Deviation ($\sigma$)**: \$45.71

$$z = \frac{\text{total\_amount} - \mu}{\sigma}$$

Transactions where $|z| > 3.0$ are flagged as univariate outliers.
- In the real dataset, the maximum order value is \$150.00 ($z = 1.38$), so no orders exceed 3 standard deviations.

---

## 16. Isolation Forest (Multidimensional Outliers)

Function: `detect_isolation_forest_anomalies(sales_df, contamination=0.02, random_state=42)`

Features evaluated: `['quantity', 'unit_price', 'total_amount']`.

Isolation Forest isolates observations by randomly selecting a feature and randomly selecting a split value. Outliers require fewer splits to isolate than normal points:
$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$

- Prediction convention: `-1` (Anomaly), `1` (Normal).
- Business label: `"Unusual Pattern Flagged"` vs `"Normal"`.

### Real Data Findings:
- **Order #1002** (Customer `C002`, Pen Set):
  - Quantity: **10 units** (store median is 3.0 units)
  - Unit Price: \$12.00
  - Total Amount: \$120.00
  - Isolation Forest score: **-0.0054** &rarr; **Anomaly Detected**
  - Reason: High item quantity relative to catalog norms.

---

## 17. Method Comparison: Z-Score vs Isolation Forest

| Metric | Statistical Z-Score (1D) | Isolation Forest (3D) | Overlap |
|:---|:---:|:---:|:---:|
| **Features Used** | `total_amount` | `[quantity, unit_price, total_amount]` | Both |
| **Threshold** | $\|z\| > 3.0$ | `contamination = 0.02` | Common |
| **Detected Orders** | 0 orders | **Order #1002** | 0 orders |
| **Analytical Focus** | Extreme monetary outliers | Unconventional volume-price pairings | Compound outliers |

---

## 18. Actionable Alert Generation

Detected anomalies are converted into operational alerts:

```json
{
  "order_id": 1002,
  "customer_id": "C002",
  "product_name": "Pen Set",
  "alert_type": "Unusual Transaction Pattern",
  "severity": "Medium",
  "detection_method": "Isolation Forest",
  "message": "Unusual sales activity detected on Order #1002: High unit quantity (10 units of Pen Set at $12.00/unit) deviates from typical purchasing patterns (score: -0.0054). Flagged for review.",
  "relevant_values": {
    "quantity": 10.0,
    "unit_price": 12.0,
    "total_amount": 120.0,
    "z_score": 0.7191,
    "isolation_forest_score": -0.0054
  }
}
```

*Policy*: Language explicitly states *"Unusual sales activity detected - flagged for review"* rather than *"Fraud confirmed"*.

---

## 19. Inventory Anomaly Support Assessment

The database schema (`db/marketmind.db`) maintains a static snapshot table for inventory:
`[id, product_id, stock_level, reorder_point]`.

- Current data does not contain time-series inventory transaction logs (adjustments, goods received, write-offs).
- Documented limitation: Statistically sound inventory anomaly detection (e.g. phantom stock, unexpected stock run-down) requires timestamped inventory audit movement history.
- Synthetic inventory movements were not fabricated.

---

## 20. Extended Business Excel Report

File: `reports/business_report.xlsx`

The Excel workbook now includes 6 sheets:
1. `Customer Segments`: Milestone 2 K-Means and Hierarchical cohort metrics.
2. `Sales Forecast`: 30-day forecast predictions and confidence intervals.
3. `Model Comparison`: Prophet vs Random Forest vs XGBoost regression errors.
4. `Product Recommendations`: Customer purchase history, recommendations, and status.
5. `Churn Risk`: Customer spend, recency, churn probability, and risk tiers.
6. `Anomaly Alerts`: Flagged transactions, severity, methods, and review notes.

---

## 21. API Reference & RBAC Matrix

All Milestone 3 endpoints are protected by JWT Bearer token authentication and role guards:

| Endpoint | Method | Allowed Roles | Description |
|:---|:---:|:---:|:---|
| `/recommendations/{customer_id}` | GET | `owner`, `manager`, `admin` | Combined hybrid recommendations |
| `/recommendations/{customer_id}/collaborative` | GET | `owner`, `manager`, `admin` | Collaborative filtering recommendations |
| `/recommendations/{customer_id}/association` | GET | `owner`, `manager`, `admin` | Market basket association recommendations |
| `/api/v1/recommendations/overview/matrix` | GET | `owner`, `manager`, `admin` | Customer-product matrix & cosine similarities |
| `/churn` | GET | `owner`, `manager`, `admin` | Churn cohort summary, model metrics, segment cross-check |
| `/churn/{customer_id}` | GET | `owner`, `manager`, `admin` | Specific customer churn probability and risk tier |
| `/anomalies` | GET | `owner`, `manager`, `admin` | Full anomaly report (Z-score, Isolation Forest, alerts) |
| `/anomalies/summary` | GET | `owner`, `manager`, `admin` | Lightweight anomaly counts and review alerts |

*RBAC Rules Enforced*:
- **401 Unauthorized**: Any request without a valid Bearer token.
- **403 Forbidden**: Requests from `sales_executive` to AI analytics endpoints.

---

## 22. React Dashboard Integration

The frontend was extended with three modular components:

1. `ProductRecommendations.jsx`:
   - Interactive customer selector (C001–C005).
   - Algorithm mode toggles: Combined Hybrid, Collaborative Filtering, Association Rules.
   - Real-time card display with method badges, scores, and purchased-item exclusion indicators.
2. `CustomerChurnRisk.jsx`:
   - Active model selection rationale banner.
   - Model comparison table (Precision, Recall, F1, Accuracy).
   - Customer cohort risk table with color-coded probability progress bars (Red = High, Amber = Medium, Green = Low).
   - Segment-churn cross-analysis cards.
3. `AnomalyAlerts.jsx`:
   - Z-score vs Isolation Forest comparison cards.
   - Transaction review queue with priority pills and "Mark Reviewed" verification toggle.
   - Non-alarmist review guidance banner.

Integrated into:
- `OwnerDashboard.jsx` (Business Owner executive view)
- `ManagerDashboard.jsx` (Store Manager operational view)
- `AdminDashboard.jsx` (System Administrator console)

---

## 23. Test Verification Summary

Automated tests across all milestones:

```bash
$env:PYTHONPATH="."; .venv\Scripts\python.exe backend/test_api.py        # 17 / 17 Passed
$env:PYTHONPATH="."; .venv\Scripts\python.exe backend/test_milestone2.py   # 24 / 24 Passed
$env:PYTHONPATH="."; .venv\Scripts\python.exe backend/test_milestone3.py   # 28 / 28 Passed
```

**Total Verified Automated Tests**: **69 / 69 passing**.
