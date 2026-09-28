# MarketMind AI: Reporting Integration

## Milestone 2, Day 9-10

This milestone integrates the generated customer segmentation and forecasting results into a factual Excel report, protected FastAPI endpoints, and the existing React dashboard. No new authentication/RBAC design or future AI modules were added.

## Report structure

The reporting service is implemented in `backend/services/reporting_service.py`. It reads only generated files under `data/processed/segments/` and `data/processed/forecast/`.

The Excel workbook is:

`data/processed/reports/marketmind_day9_10_report.xlsx`

It contains these sheets:

- **Segment Summary:** customer counts and average behavioral values by named segment.
- **Segment Statistics:** hierarchical cluster counts and behavior means.
- **Forecast Summary:** selected revenue model and forecast window totals/averages.
- **Revenue Forecast:** the actual selected-model revenue forecast rows.
- **Model Comparison:** actual MAE, RMSE, and selection flags for Prophet, XGBoost, and Random Forest.
- **Business Interpretation:** concise observations derived from the generated segment and forecast results.

## Actual segmentation results

The generated segmentation output contains 300 customers and three named segments:

| Segment                | Customers |
| ---------------------- | --------: |
| Regular Customers      |       197 |
| Low Activity Customers |        52 |
| High Value Customers   |        51 |

The report uses the actual `purchase_frequency`, `purchase_value`, and `customer_activity` values from `data/processed/segments/customer_segments.csv`.

## Actual forecasting results

The selected revenue model is **Random Forest**. The selected sales-quantity model remains **Prophet**.

| Target         | Model         |    MAE |   RMSE |
| -------------- | ------------- | -----: | -----: |
| Revenue        | Prophet       | 139.28 | 167.84 |
| Revenue        | XGBoost       | 141.44 | 178.17 |
| Revenue        | Random Forest | 131.74 | 163.80 |
| Sales quantity | Prophet       |   5.90 |   7.66 |
| Sales quantity | XGBoost       |   6.54 |   8.28 |
| Sales quantity | Random Forest |   6.13 |   7.90 |

The selected revenue forecast covers **2026-01-01 to 2026-01-30**. The first generated revenue values are:

| Date       | Model         | Revenue forecast |
| ---------- | ------------- | ---------------: |
| 2026-01-01 | Random Forest |           425.11 |
| 2026-01-02 | Random Forest |           398.33 |
| 2026-01-03 | Random Forest |           464.47 |

## API endpoints

The existing JWT bearer authentication and role dependencies are preserved.

- `GET /segments`
  - Allowed for Business Owner, Store Manager, Sales Executive, and System Administrator.
  - Returns customer count, named segment summaries, and cluster statistics.
- `GET /forecast/revenue`
  - Allowed for Business Owner, Store Manager, and System Administrator.
  - Returns selected revenue model, forecast dates, forecast rows, and revenue model comparison.

The same endpoints are also available under the existing frontend API prefix:

- `GET /api/segments`
- `GET /api/forecast/revenue`

The existing sales, inventory, customer summary, login, logout, and current-user endpoints remain available.

## Dashboard integration

The existing authenticated React dashboard now loads the reporting endpoints with the current JWT alongside its existing summary calls. It adds:

- **Customer Segmentation:** actual segment counts, average purchase value, and activity.
- **Revenue Forecast:** selected model, forecast window, and actual forecast rows.
- **Model Comparison:** actual MAE/RMSE rows with the selected model highlighted.

The panels have loading and error behavior through the existing dashboard request state. Values are fetched from the FastAPI endpoints; no segmentation counts, metrics, or forecast values are hard-coded in the UI.

## Verification performed

- Generated the Excel workbook from the processed segmentation and forecast CSV files.
- Verified workbook sheets and actual row counts with `openpyxl`.
- Verified authenticated `GET /segments` and `GET /forecast/revenue`.
- Verified `/api/segments` and `/api/forecast/revenue` aliases.
- Verified the existing authenticated sales summary endpoint still returns the existing data.
- Verified the React production build.
- Verified the browser dashboard displays actual segment names, selected model, forecast date/value, and validation metric.
- Verified the responsive dashboard has no horizontal overflow at a mobile viewport.

Run the Excel report generator from the repository root:

```powershell
.venv\Scripts\python.exe -m backend.services.reporting_service
```
