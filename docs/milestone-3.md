# MarketMindAI --- Milestone 3 Evidence

**Milestone:** Milestone 3 --- Recommendations, Churn Prediction, Anomaly Detection
**Data:** UCI Online Retail II (both source files, unchanged on disk)

## 1. What was built

| Days | Feature | Code | Artifacts (`artifacts/milestone-3/`) | API |
|---|---|---|---|---|
| 1-4 | Product recommendations (collaborative filtering + association rules + upsell) | `backend/ml/recommendations.py` | `recommendations/` | `GET /recommendations/overview`, `/recommendations/customer/{id}?stock_code=`, `/recommendations/product/{code}` |
| 5-8 | Churn prediction (Logistic Regression, Random Forest, XGBoost) with High/Medium/Low risk and link to M2 segments | `backend/ml/churn.py` | `churn/` | `GET /churn`, `/churn/customer/{id}` |
| 9-10 | Anomaly detection (Z-score + Isolation Forest + stock write-offs + demand spikes) with alerts | `backend/ml/anomaly.py` | `anomaly/` | `GET /anomalies` |

Shared cleaning is in `backend/ml/common.py`. Everything is regenerated with:

```bash
python -m backend.ml.run_milestone3            # all three
python -m backend.ml.run_milestone3 churn      # one part
```

Following the Milestone 2 pattern, modelling runs offline and the API serves the saved artifacts.
The React app has three new pages: **Recommendations**, **Churn risk** and **Alerts**.
Recommendations are open to all roles; churn and alerts are limited to `business_owner`, `admin` and `store_manager`.

## 2. Data preparation (`common.py`)

* The two UCI files **overlap**: 1,088 invoices (22,523 rows) from December 2010 appear identically in both.
  They are dropped once so nothing is counted twice.
* Fully cancelled invoices are reconciled with the existing Milestone 2 function.
* Only positive quantity/price lines for real products are kept. Fee and adjustment codes (`POST`, `DOT`, `M`, `BANK CHARGES`, ...) are excluded.
* Result: 1,012,034 lines, 39,206 invoices, 5,836 identified customers.

## 3. Recommendations

* **Collaborative filtering:** customer-product matrix of `log(1 + quantity)`, cosine similarity, 20 nearest customers, already-owned products removed.
  The log stops a few wholesale buyers from dominating similarity.
* **Association rules:** single-item rules A -> B with support, confidence and lift
  (min support 0.5% of invoices, min confidence 20%, lift > 1). 3,465 rules.
  This is Apriori restricted to 2-item sets, computed with sparse matrices, so no `mlxtend` dependency is needed.
* **Upsell:** products bought by the same customers (item-item cosine >= 0.15) that cost 20%-200% more. This is a heuristic, not measured revenue uplift.
* **New customers** with no history receive best sellers.

**Evaluation** (learn before 2011-09-10, test on the last 90 days, 2,285 customers):

| Model | Hit rate @10 | Precision @10 | Recall @10 |
|---|---|---|---|
| Collaborative filtering | 35.7% | 5.8% | 1.8% |
| Best-seller baseline | 27.9% | 3.9% | 1.1% |

Collaborative filtering beats the baseline, but absolute precision is modest, which is normal for a catalogue of 4,600 products.

## 4. Churn prediction

**Definition:** a customer *churned* if they made no purchase in the 90 days after a snapshot date (2011-09-10).
Features use **only purchases before the snapshot**: recency, frequency, average order value, total spend, tenure,
orders per month, orders in the last 90 days, distinct products, units per order.

> The simple sample in the learning guide defines churn as "inactive more than 90 days" **and** uses "days inactive"
> as a feature. The model then just re-learns its own label (data leakage) and looks perfect.
> Splitting time into before/after the snapshot avoids this. It also means the 13% churn rate shown in the guide does
> not apply to this data: the real rate is **56.5%**, because most customers in this dataset buy only once or twice.

Stratified 80/20 split, 5,245 customers. The boosted-tree row shows XGBoost when it is installed
(the shipped artifacts were generated where it was not, see section 6).

| Model | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|
| Random Forest | 0.77 | 0.85 | 0.81 | 0.83 |
| Gradient boosting (XGBoost substitute) | 0.76 | 0.84 | 0.80 | 0.83 |
| Logistic Regression | 0.75 | 0.81 | 0.78 | 0.81 |
| "Nobody churns" baseline accuracy | 43.6% | | | |

The model with the best F1 (recall as tie-break) is selected and refitted on all labelled customers.
Recency is by far the most important feature.

**Risk categories** (thresholds 0.7 and 0.4): of 2,876 customers who ordered in the last 90 days,
168 are High Risk, 943 Medium and 1,765 Low. A further 2,960 customers have already been silent for 90+ days;
they are flagged `already_inactive_90d` and treated as win-back targets, not "at risk".

**Link to Milestone 2 segments:** `churn_risk_by_segment.csv` crosses risk with the final segment names.
Note the M2 segment "Occasional / Low-Engagement" contains 91% of customers, so it carries most of the High Risk group
(43% of that segment) while "Active Regular" is only 2% High Risk. The direction is consistent, but the segmentation is too
coarse to be a strong second opinion. The guide mentions an "At-Risk / Fading" segment; that name does not exist in the final M2 output.

## 5. Anomaly detection

| Method | Scope | Flagged |
|---|---|---|
| Z-score (> 3 SD) on invoice value | 39,206 invoices | 453 |
| Isolation Forest (contamination 0.5%) on 6 order features | 39,206 invoices | 197 |
| Flagged by both | | 56 |
| Stock write-offs (price 0, negative quantity, no customer; robust z > 3.5) | recorded adjustments | 10 |
| Demand spikes (>= 1,000 units in a day and >= 10x the product's typical day) | product-days | 12 |

* The Z-score method flags many legitimate large wholesale orders because order values are heavily skewed.
  Those stay in `sales_anomalies.csv` for review but only Isolation Forest hits raise alerts, to avoid flooding the dashboard.
* **Inventory:** the platform has no real stock counts (inventory is estimated as units sold x 1.5), so a "stock dropped overnight" check is not possible.
  The dataset does contain real stock adjustments (damaged, lost, thrown away), which are used instead.
* Result: 219 alerts (75 high severity). High severity = flagged by both methods, a very large write-off, or an extreme demand spike.
* An alert is a prompt to review, not proof of fraud.

## 6. Limitations and honest notes

* The artifacts committed here were generated in an environment **without XGBoost**, so the "XGBoost" slot was filled by
  scikit-learn gradient boosting (recorded in `churn_run_info.json`). Re-run `python -m backend.ml.run_milestone3 churn`
  with the project's requirements installed to include real XGBoost; the selected model may change.
* The existing Milestone 2 customer features count the 1,088 overlapping December 2010 invoices twice (invoice totals double for those customers).
  Milestone 3 removes the overlap, M2 artifacts were left untouched.
* Recommendation and churn quality are measured offline on historical data. No live A/B test was possible.
* Churn probabilities from Random Forest are useful for ranking customers, not exact percentages.

## 7. Tests

* `tests/test_milestone3_models.py` --- churn features cannot see the future, churn labels, risk thresholds,
  association-rule support/confidence/lift on hand-computed data, recommendations exclude owned products, anomaly detectors catch an injected giant order.
* `tests/test_milestone3_api.py` --- authentication, role restrictions, filters and response structure for the new endpoints.
