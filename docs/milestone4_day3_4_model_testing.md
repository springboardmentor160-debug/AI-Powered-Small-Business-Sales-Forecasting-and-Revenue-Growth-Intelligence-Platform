# MarketMind AI: Milestone 4, Days 3-4 Model Testing

## Evaluation methodology

This evaluation extends `data/processed/testing/milestone4_test_results.csv` without deleting or replacing the Milestone 4 Days 1-2 rows. Existing production models and source datasets are not modified.

### Churn

The selected churn artifact is `data/processed/churn/churn_predictions_final.csv`. It contains predictions for all 300 customers after the selected model was fitted on the available customer data. The repository does not contain row-level validation predictions paired with validation labels for that selected model. The comparison file contains precision, recall, and F1 values for a validation split, but it does not contain accuracy or the row-level predictions needed to verify all four requested metrics.

Because scoring full-data predictions would leak training data, Accuracy, Precision, Recall, and F1-score are recorded as unavailable rather than fabricated. The existing churn pipeline remains unchanged.

### Recommendations

The collaborative filtering evaluator uses the existing model implementation and a temporal leave-last-transaction-out holdout:

1. Sort each customer's transactions by date and transaction ID.
2. Hold out that customer's final transaction.
3. Fit an evaluation model on the remaining 11,700 transactions only.
4. Generate three recommendations per customer.
5. Compare recommendations with the held-out product.

The actual dataset remains 12,000 single-product transactions, 300 customers, and 24 products. Precision@3 uses three recommendation slots as the denominator; Recall@3 uses the held-out product set as the denominator. All 300 customers have one labeled held-out transaction.

### Anomaly detection

The original Sales data has no verified anomaly labels. The existing counts of 512 Z-score detections and 120 Isolation Forest detections are therefore not treated as confirmed ground truth.

For controlled testing only, the evaluator creates an in-memory fixture containing 100 labeled normal rows and 2 labeled anomalous rows. The fixture is not written into or merged with the original dataset. Detection Accuracy and False Positive Rate are reported only for this controlled fixture and must not be interpreted as real-world performance.

## Actual results

| Model | Task | Metric | Value |
| --- | --- | --- | ---: |
| Selected churn model | Churn | Accuracy | Unavailable |
| Selected churn model | Churn | Precision | Unavailable |
| Selected churn model | Churn | Recall | Unavailable |
| Selected churn model | Churn | F1-score | Unavailable |
| Collaborative Filtering | Recommendation | Precision@3 | 0.042222 |
| Collaborative Filtering | Recommendation | Recall@3 | 0.126667 |
| Z-score | Anomaly Detection | Detection Accuracy | 1.000000 |
| Z-score | Anomaly Detection | False Positive Rate | 0.000000 |
| Isolation Forest | Anomaly Detection | Detection Accuracy | 1.000000 |
| Isolation Forest | Anomaly Detection | False Positive Rate | 0.000000 |

Full-precision values and evaluation details are recorded in `data/processed/testing/milestone4_test_results.csv`.

## Limitations

- Churn validation cannot be reproduced from the persisted artifacts without refitting a model or using leaked full-data predictions. No churn metric is invented.
- Recommendation results measure one temporal holdout and may vary with a different cutoff or multi-item customer history.
- The recommendation evaluator fits an isolated evaluation instance on training-only rows; it does not overwrite the existing recommendation outputs.
- Controlled anomaly metrics describe the labeled fixture only, not the original Sales data.
- The original anomaly detector outputs remain unlabeled detections, not verified anomalies.
- Imbalanced churn metrics should be interpreted with class support and not accuracy alone; the missing row-level validation artifact prevents a valid calculation here.

## Reproduce the evaluation

From the repository root, use the existing virtual environment:

```powershell
.venv\Scripts\python.exe -m backend.services.model_testing_service
```

The command appends any missing Days 3-4 rows to:

`data/processed/testing/milestone4_test_results.csv`

Running the command again does not duplicate existing result rows.
