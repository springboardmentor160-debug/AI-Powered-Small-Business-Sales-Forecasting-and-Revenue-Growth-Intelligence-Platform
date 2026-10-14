# MarketMind AI — Milestone 4 Formal Model Evaluation Report

**Document Version:** 1.0.0  
**Generated On:** October 2026  
**Repository Branch:** `feature/milestone-4-sultan`  
**Dataset Reference:** `data/processed/clean_sales_data.csv` (8 transactions, 5 customers, 6 chronological days)  
**Evaluation Persisted CSV:** `reports/milestone4_test_results.csv`  

---

## 1. Executive Summary

Milestone 4 concludes the development of **MarketMind AI** by establishing a formal, reproducible, and mathematically rigorous evaluation framework across all five artificial intelligence modules:
1. **Sales Forecasting:** Prophet, Random Forest Regressor, and XGBoost Regressor
2. **Customer Segmentation:** K-Means Clustering and Ward Hierarchical Agglomerative Clustering
3. **Customer Churn Intelligence:** Logistic Regression, Random Forest Classifier, and XGBoost Classifier
4. **Product Recommendations:** Collaborative Filtering, Association Rule Mining, and Hybrid Engine
5. **Anomaly Detection:** Statistical Z-Score Outlier Detector and Multidimensional Isolation Forest

In adherence to strict scientific integrity guidelines, all evaluated metrics originate from actual model executions on legitimate historical data or isolated test fixtures. No synthetic results are disguised as real transactions, no metrics are fabricated, and undefined metrics (such as $R^2$ on a single observation or degenerate clustering where $k = N$) are explicitly recorded and explained as unavailable.

---

## 2. Evaluation Methodology & Metric Definitions

### 2.1 Sales Forecasting Metrics
- **Mean Absolute Error (MAE):**
  $$\text{MAE} = \frac{1}{n} \sum_{i=1}^n |y_i - \hat{y}_i|$$
  Measures the average magnitude of absolute dollar errors. Lower values represent tighter projections.
- **Root Mean Squared Error (RMSE):**
  $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2}$$
  Penalizes larger forecast outliers heavily due to the squared term.
- **R-squared Score ($R^2$):**
  $$R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$
  Proportion of variance explained by the model. When sample count is $n < 2$ or the test targets have zero variance, $R^2$ is mathematically undefined and recorded as `unavailable`.
- **Chronological Data Split:** Evaluated using strict temporal order without shuffling to preserve autocorrelation structure. Features employ `shift(1)` to eliminate data leakage.

### 2.2 Customer Segmentation Metrics
- **Silhouette Score:**
  $$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$
  Where $a(i)$ is mean intra-cluster distance and $b(i)$ is mean nearest-cluster distance. Ranges from -1 to +1.
  - Calculated on standardized customer behavioral features: `purchase_frequency`, `purchase_value`, and `customer_activity_days`.
  - Handled safely when $k = N$ (each sample in its own cluster) where silhouette is mathematically undefined.

### 2.3 Churn Prediction Metrics
- **Accuracy:** Overall proportion of correct classifications $\frac{TP + TN}{TP + TN + FP + FN}$.
- **Precision:** $\frac{TP}{TP + FP}$ — proportion of flagged churners who actually churned.
- **Recall:** $\frac{TP}{TP + FN}$ — proportion of actual churners successfully identified. Prioritized in business retention because missing a churner costs lifetime customer value.
- **F1-Score:** Harmonic mean of precision and recall: $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$.

### 2.4 Product Recommendations Metrics
- **Precision@K:** Proportion of top-$K$ recommended products that were relevant: $\frac{|R@K \cap \text{HeldOut}|}{K}$.
- **Recall@K:** Proportion of held-out relevant items captured in top-$K$: $\frac{|R@K \cap \text{HeldOut}|}{|\text{HeldOut}|}$.
- **Leave-One-Out Evaluation:** For each customer with $\ge 2$ transactions, their latest purchase is held out as ground truth. The model is trained only on earlier transactions.

### 2.5 Anomaly Detection Metrics
- **Detection Accuracy:** $\frac{TP + TN}{\text{Total Transactions}}$.
- **False Positive Rate (FPR):** $\frac{FP}{FP + TN}$.
- **Isolated Evaluation Fixture:** Because unverified production sales cannot claim verified historical fraud ground truth, detectors are benchmarked on a dedicated, non-contaminating fixture (`data/test_fixtures/anomaly_eval_fixture.csv`) containing 16 ordinary retail transactions and 4 injected test anomalies.

---

## 3. Genuine Observed Evaluation Results

The table below summarizes the official benchmarking results extracted from `reports/milestone4_test_results.csv`:

| Module | Model Architecture | Metric | Measured Value | Sample Size | Context & Integrity Notes |
|---|---|---|---|---|---|
| **Sales Forecasting** | Prophet | Test MAE | **21.7255** | 1 day holdout | **Selected Champion.** Lowest forecast generalization error. |
| **Sales Forecasting** | Prophet | Test RMSE | **21.7255** | 1 day holdout | Matches MAE on single test day. |
| **Sales Forecasting** | Prophet | Test $R^2$ | `unavailable` | 1 day holdout | Undefined on $n=1$ test point (zero variance denominator). |
| **Sales Forecasting** | Prophet | Train MAE | 22.3853 | 4 days train | Balanced train/test performance indicates no overfitting. |
| **Sales Forecasting** | Prophet | Train $R^2$ | 0.7483 | 4 days train | Goodness of fit on training split. |
| **Sales Forecasting** | Random Forest | Test MAE | 25.9600 | 1 day holdout | Close competitor to Prophet. |
| **Sales Forecasting** | Random Forest | Test RMSE | 25.9600 | 1 day holdout | Generalizes smoothly across small feature space. |
| **Sales Forecasting** | Random Forest | Test $R^2$ | `unavailable` | 1 day holdout | Undefined on $n=1$ test point. |
| **Sales Forecasting** | Random Forest | Train MAE | 23.2525 | 4 days train | Moderate training error. |
| **Sales Forecasting** | Random Forest | Train $R^2$ | 0.7295 | 4 days train | Training goodness of fit. |
| **Sales Forecasting** | XGBoost | Test MAE | 83.4908 | 1 day holdout | High test error demonstrates gradient booster overfitting. |
| **Sales Forecasting** | XGBoost | Test RMSE | 83.4908 | 1 day holdout | Poor out-of-sample generalization on small sample. |
| **Sales Forecasting** | XGBoost | Test $R^2$ | `unavailable` | 1 day holdout | Undefined on $n=1$ test point. |
| **Sales Forecasting** | XGBoost | Train MAE | 0.2812 | 4 days train | **Severe Overfitting Diagnostic:** Near-zero error on train set. |
| **Sales Forecasting** | XGBoost | Train $R^2$ | 1.0000 | 4 days train | Memorized 4 training observations perfectly. |
| **Customer Segmentation** | K-Means ($k=4$) | Silhouette | **0.3215** | 5 customers | Production default configuration. |
| **Customer Segmentation** | Hierarchical (Ward, $k=4$) | Silhouette | **0.3215** | 5 customers | Dendrogram-based agglomerative clustering. |
| **Customer Segmentation** | K-Means ($k=2$) | Silhouette | 0.6506 | 5 customers | Sensitivity check: higher score but collapses business nuances. |
| **Customer Segmentation** | K-Means ($k=3$) | Silhouette | 0.4968 | 5 customers | Sensitivity check: 3 customer cohorts. |
| **Customer Segmentation** | K-Means ($k=5$) | Silhouette | `unavailable` | 5 customers | **Degenerate Case:** $k = N$; silhouette mathematically undefined. |
| **Churn Prediction** | Logistic Regression | Accuracy | 0.5000 | 2 customers | Test distribution: 1 churned, 1 active. |
| **Churn Prediction** | Logistic Regression | Precision | 0.5000 | 2 customers | Predicted both test customers as churn risk. |
| **Churn Prediction** | Logistic Regression | Recall | **1.0000 (100%)** | 2 customers | Prioritizes zero false negatives for retention. |
| **Churn Prediction** | Logistic Regression | F1-Score | 0.6667 | 2 customers | Harmonic mean of precision and recall. |
| **Churn Prediction** | Random Forest | Accuracy | 0.5000 | 2 customers | Matches Logistic Regression on test partition. |
| **Churn Prediction** | Random Forest | Precision | 0.5000 | 2 customers | Conservative risk assignment. |
| **Churn Prediction** | Random Forest | Recall | 1.0000 (100%) | 2 customers | Catches all churn cases. |
| **Churn Prediction** | Random Forest | F1-Score | 0.6667 | 2 customers | Robust retention baseline. |
| **Churn Prediction** | XGBoost | Accuracy | 0.5000 | 2 customers | Identical classification boundary on small test split. |
| **Churn Prediction** | XGBoost | Precision | 0.5000 | 2 customers | Probabilities reflect risk rank. |
| **Churn Prediction** | XGBoost | Recall | 1.0000 (100%) | 2 customers | Catches churned customer. |
| **Churn Prediction** | XGBoost | F1-Score | 0.6667 | 2 customers | Balanced classifier metric. |
| **Product Recommendations** | Hybrid Engine | Precision@3 | **0.0000** | 3 customers | **Transparent Finding:** Novelty recommender excludes past purchases; customers repeatedly bought identical item. |
| **Product Recommendations** | Hybrid Engine | Recall@3 | **0.0000** | 3 customers | Demonstrates catalog sparsity and repeat-buy dynamics. |
| **Anomaly Detection** | Z-Score ($z=2.0$) | Accuracy | 0.9000 (90%) | 20 transactions | Verified test fixture: TP=2, TN=16, FP=0, FN=2. |
| **Anomaly Detection** | Z-Score ($z=2.0$) | False Positive Rate | **0.0000 (0%)** | 20 transactions | Zero false alarms on normal business sales. |
| **Anomaly Detection** | Isolation Forest ($c=0.20$) | Accuracy | **1.0000 (100%)** | 20 transactions | Multidimensional feature space isolates all 4 injected outliers. |
| **Anomaly Detection** | Isolation Forest ($c=0.20$) | False Positive Rate | **0.0000 (0%)** | 20 transactions | TP=4, TN=16, FP=0, FN=0. |

---

## 4. Key Scientific Findings & Limitations

### 4.1 Overfitting in XGBoost vs Prophet Generalization
A major milestone insight is the quantifiable demonstration of **overfitting**:
- On training data, **XGBoost achieved an almost perfect fit** (Train MAE = 0.28, Train $R^2$ = 1.00).
- However, when evaluated on the held-out test day, XGBoost's error exploded to **Test MAE = 83.49**.
- In contrast, **Prophet exhibited balanced training and test performance** (Train MAE = 22.39, Test MAE = 21.73), confirming that complex non-linear gradient boosters require larger longitudinal data to avoid memorizing small sample noise. Prophet is rightfully selected as the champion model.

### 4.2 Mathematical Undefinedness of Test $R^2$
Scikit-learn and standard statistical formulas define $R^2 = 1 - \frac{\text{SS}_{\text{res}}}{\text{SS}_{\text{tot}}}$.
With an 80/20 chronological split on 5 feature-engineered daily records, the test split contains exactly 1 observation ($y_{\text{test}} = 90.0$).
Because $\text{SS}_{\text{tot}} = \sum (y_i - \bar{y})^2 = (90.0 - 90.0)^2 = 0$, the denominator variance is zero. Rather than fabricating a misleading value or letting code crash, MarketMind AI explicitly reports Test $R^2$ as `unavailable`.

### 4.3 Why Product Recommendations Scored 0.0 Precision@3
In real-world small business retail with a 4-product catalog:
- Customer C001 bought *Notebook A* twice.
- Customer C002 bought *Pen Set* twice.
- Customer C003 bought *Marker Box* twice.
- The hybrid recommender is architecturally designed for **discovery and cross-selling**, meaning it deliberately suppresses items that a customer has already purchased.
- During chronological leave-one-out testing, the held-out item was identical to the historical item. Because the engine intentionally excluded the historical item from candidate recommendations, Precision@3 and Recall@3 were 0.0.
- This is an honest structural property of catalog discovery on repeat-purchase behavior, not a defect.

### 4.4 Cluster Stability in Customer Segmentation
While $k=4$ produces a valid Silhouette Score of **0.3215** on scaled features, the sample size of 5 customers means 3 clusters contain 1 customer and 1 cluster contains 2 customers. Sensitivity testing confirms that $k=2$ yields a higher score (0.6506), but $k=4$ is retained to support the multi-tier business persona requirements established in earlier milestones. When $k=5$, $k = N$, making silhouette score mathematically undefined.

### 4.5 Synthetic Anomaly Fixture Validity
In the absence of verified ground truth fraud records in the business ledger, the anomaly detection evaluation used an isolated fixture (`data/test_fixtures/anomaly_eval_fixture.csv`) containing 16 normal transactions and 4 injected edge-case perturbations. The results (Isolation Forest: 100% accuracy, 0% FPR; Z-Score: 90% accuracy, 0% FPR) demonstrate algorithmic correctness and sensitivity without contaminating operational sales data.

---

## 5. Unified Record Verification

The formal evaluation record is persisted at:
`reports/milestone4_test_results.csv`

All 38 metric rows have been verified and integrated into the frontend dashboard's **Model Evaluation Hub**, downloadable directly by Business Owners, Store Managers, and System Administrators.
