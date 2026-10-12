Milestone 4 - MarketMind AI Testing
# MarketMind AI - Small Business Sales Intelligence Platform

## Live Demo
- Frontend: https://marketmind-frontend-xq18.onrender.com
- Backend API docs: https://marketmind-backend-7sxd.onrender.com/docs
- Note: free hosting hai, pehli request mein 50 second lag sakte hain.

## Demo Login
| Role | Email | Password |
|---|---|---|
| Business Owner | owner@marketmind.ai | owner123 |
| Store Manager | manager@marketmind.ai | manager123 |
| Sales Executive | sales@marketmind.ai | sales123 |
| Administrator | admin@marketmind.ai | admin123 |

## Tech Stack
FastAPI, SQLAlchemy (SQLite), React + Vite, scikit-learn, XGBoost, pandas, Render.

## AI Modules
1. Customer Segmentation: K-Means + Hierarchical Clustering (VIP, Regular, Occasional, At-Risk)
2. Sales Forecasting: Random Forest, XGBoost (Prophet Python 3.14 par install nahi hua)
3. Recommendations: Collaborative Filtering + Association Rules
4. Churn Prediction: Logistic Regression, Random Forest, XGBoost
5. Anomaly Detection: Z-score + Isolation Forest

## Model Testing Results
| Module | Metric | Value |
|---|---|---|
| Forecasting (Random Forest) | MAE / RMSE / R2 | 91010 / 116442 / 0.071 |
| Segmentation | Silhouette | 0.299 |
| Churn (Logistic Reg.) | Precision / Recall / F1 | 0.35 / 0.88 / 0.50 |
| Recommendation (K=5) | Precision@K / Recall@K | 0.134 / 0.269 |
| Anomaly | Detection Rate / False Positive Rate | 0.90 / 0.011 |

## Limitations
Data synthetic hai aur sirf 100 customers hain, isliye forecasting aur recommendation ke scores kam hain. Real data par behtar honge.

## Role-Based Access
Sales Executive ko forecasting aur inventory access nahi hai.
