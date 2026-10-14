# MarketMind AI: Milestone 4 Final Presentation

This is a 12-slide presentation outline. All figures below come from the
existing processed artifacts or the consolidated Milestone 4 evaluation file.

## Slide 1 — MarketMind AI

**Slide content**

- Small-business sales forecasting and revenue-growth intelligence platform.
- Milestone 4 final delivery: testing, integration, deployment preparation,
  and end-to-end demonstration.
- FastAPI + React + SQLite.

**Speaker notes**

Introduce the business problem: make sales, customer, and forecast information
available in one usable application while keeping the analytics measurable and
the deployment path practical.

## Slide 2 — End-to-end architecture

**Slide content**

- React/Vite dashboard.
- FastAPI API and services.
- Existing analytics models and generated reports.
- SQLite plus processed CSV artifacts.
- Docker Compose: Nginx frontend + FastAPI backend + persistent data volume.

**Speaker notes**

Explain that the milestone preserved the existing architecture rather than
replacing it. The frontend calls protected FastAPI routes, while the backend
loads existing processed outputs.

## Slide 3 — Data foundation

**Slide content**

- 12,000 single-product sales transactions.
- 300 customers.
- 24 products.
- 96 inventory rows.
- 300 persisted customer segment assignments.
- 30 consolidated Milestone 4 evaluation rows.

**Speaker notes**

Emphasize that original datasets were not fabricated or rewritten. Evaluation
uses persisted artifacts and explicit holdout or controlled-fixture rules.

## Slide 4 — Forecasting evaluation design

**Slide content**

- Existing persisted validation predictions.
- Same chronological holdout for available models.
- Holdout: 2025-12-02 to 2025-12-31.
- 30 validation rows per model-target pair.
- Metrics: MAE, RMSE, and R².
- Targets evaluated separately: revenue and sales quantity.

**Speaker notes**

Describe leakage prevention: models were not compared across different test
periods, and the evaluator did not rebuild or replace the existing models.

## Slide 5 — Revenue forecasting results

**Slide content**

| Model | MAE | RMSE | R² |
| --- | ---: | ---: | ---: |
| Prophet | 139.280055 | 167.841098 | 0.026297 |
| XGBoost | 141.439689 | 178.166143 | -0.097186 |
| Random Forest | 131.738268 | 163.801818 | 0.072599 |

**Speaker notes**

Random Forest has the best measured revenue MAE, RMSE, and R² on this holdout.
The result is evidence for this validation period only, not a guarantee of
future superiority.

## Slide 6 — Sales quantity and segmentation results

**Slide content**

**Sales quantity**

- Prophet: MAE 5.904611, RMSE 7.662424, R² 0.051746.
- XGBoost: MAE 6.536274, RMSE 8.284615, R² -0.108504.
- Random Forest: MAE 6.128144, RMSE 7.903255, R² -0.008798.

**Segmentation**

- K-Means silhouette: 0.434129.
- Hierarchical silhouette: 0.375785.

**Speaker notes**

Prophet performs best on the measured sales-quantity holdout. K-Means has the
higher geometric separation score among the existing three-cluster outputs.

## Slide 7 — Recommendation evaluation

**Slide content**

- Collaborative filtering.
- K=3 recommendations.
- Temporal leave-last-transaction-out evaluation.
- 11,700 training rows; 300 held-out rows; 300 customers.
- Precision@3: 0.042222.
- Recall@3: 0.126667.

**Speaker notes**

The held-out transaction was not used to generate that customer's
recommendations. These metrics reflect one temporal holdout and should not be
generalized without further backtesting.

## Slide 8 — Churn and anomaly evaluation boundaries

**Slide content**

- Churn Accuracy, Precision, Recall, and F1: **unavailable**.
- Persisted churn predictions are full-dataset predictions without paired
  row-level validation labels.
- Original anomaly data has no verified labels.
- Controlled fixture: 100 normal rows + 2 anomalous rows.
- Z-score and Isolation Forest fixture accuracy: 1.000000.
- Fixture false-positive rate: 0.000000 for both.

**Speaker notes**

This is an important integrity result. Full-data churn scoring would leak
training data, and unlabeled anomaly detections cannot be presented as
confirmed anomalies. Controlled fixture results are explicitly not production
performance.

## Slide 9 — Product experience and integration

**Slide content**

- Login and logout.
- Sales, inventory, and customer summaries.
- Segmentation and revenue forecast reports.
- Loading, empty, timeout, network, 401, and 403 states.
- Responsive dashboard cards and horizontally safe narrow tables.
- Existing response formats and RBAC preserved.

**Speaker notes**

Point out that recommendation, churn, and anomaly logic remains available as
backend services/evaluation artifacts, but no unsupported claim is made that
they are frontend-integrated routes.

## Slide 10 — Security and access control

**Slide content**

- JWT bearer authentication.
- Salted scrypt password hashes.
- Short-lived access tokens.
- Four roles:
  - Business Owner
  - Store Manager
  - Sales Executive
  - System Administrator
- Route-level role dependencies.
- Safe user-facing errors and server-side logging.

**Speaker notes**

Explain the distinction between authentication and authorization. A valid
token does not automatically grant access to every protected route.

## Slide 11 — Docker and deployment readiness

**Slide content**

- Backend image built successfully.
- Frontend image built successfully.
- Docker Compose started both services.
- Backend container healthy.
- Frontend verified at `localhost:3000`.
- Backend verified at `localhost:8000`.
- SQLite persisted through the Compose named volume.
- No cloud deployment has occurred.

**Speaker notes**

Describe the production preparation honestly: the container topology has been
validated locally, while Render/Railway deployment remains a future operation.
Cloud use requires a stable secret and persistent storage.

## Slide 12 — Limitations and next steps

**Slide content**

- One forecast holdout limits generalization.
- Churn needs leakage-free labeled validation artifacts.
- Anomaly detection needs verified production-like labels.
- Recommendation evaluation needs additional temporal backtests.
- Standalone analytics need API/UI exposure if required.
- SQLite should be replaced or carefully managed before scaling.
- Future: monitoring, drift checks, scheduled refresh, automated browser tests.

**Speaker notes**

Close by separating what is measured and verified from what remains future
work. The current milestone provides a working, tested foundation without
inventing unavailable metrics or claiming a cloud deployment.
