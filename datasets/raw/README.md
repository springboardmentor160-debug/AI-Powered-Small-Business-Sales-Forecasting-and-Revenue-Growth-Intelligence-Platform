Raw source files (included in this ZIP):

| File | Source | Used for |
|------|--------|----------|
| `retail_store_inventory.csv` | store/inventory dataset (73,100 rows, 2022-01-01 -> 2024-01-01, 5 stores x 20 products); most likely synthetic | forecasting, anomaly detection, inventory alerts, dashboard KPIs |
| `online_retail_II.xlsx` | UCI Online Retail II (1,067,371 invoice lines, 2009-12 -> 2011-12), real transactions | segmentation, recommendations, churn |

Regenerate the processed files with `python ml\run_all.py` (or run `datasets/data_cleaning.py` and `datasets/data_cleaning_segmentation.py`).
