# MarketMind AI — Small Business Sales Forecasting & Revenue Growth Intelligence Platform

**MarketMind AI** is a web-based business intelligence platform that helps small businesses understand sales performance, forecast revenue, analyze customer-related patterns, and identify potential business risks using data analytics and machine learning.

## Key Features

- **Dashboard:** View an overview of business performance and key metrics.
- **Sales Analytics:** Explore revenue trends and sales performance.
- **Inventory Intelligence:** Monitor stock levels, reorder levels, and low-stock indicators.
- **Customer Segmentation:** Group sales records or customer-related cohorts using clustering.
- **Churn Prediction:** Estimate potential inactivity and churn risk.
- **Sales Forecasting:** Forecast future revenue using statistical and machine learning models.
- **Product Recommendations:** Generate product similarity, cross-sell, and upsell suggestions.
- **Anomaly Detection:** Identify unusual revenue, quantity, margin, and inventory patterns.
- **Data Upload:** Upload supported CSV and Excel datasets for validation and analysis.
- **Reports:** Generate downloadable business reports.
- **Authentication and RBAC:** Protect restricted features through authentication and role-based permissions.

## Technology Stack

### Frontend
- React.js
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- REST APIs

### Data Analytics and Machine Learning
- Pandas
- NumPy
- Scikit-learn
- Prophet, when available
- XGBoost and Random Forest

## Project Structure

```text
Market_Mind/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
└── README.md
```

## Getting Started

### Prerequisites
- Python
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone -b marketmind-ai-hema https://github.com/springboardmentor160-debug/AI-Powered-Small-Business-Sales-Forecasting-and-Revenue-Growth-Intelligence-Platform.git
cd AI-Powered-Small-Business-Sales-Forecasting-and-Revenue-Growth-Intelligence-Platform
```

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
```

Start the backend using the project's configured FastAPI entry point and port. Check the environment configuration before running it.

### 3. Set up the frontend

Open a separate terminal from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in your terminal.

## Machine Learning Approach

The platform combines several analytical approaches:

- Clustering for segmentation.
- Classification models for churn-risk estimation.
- Time-series and supervised learning models for revenue forecasting.
- Product similarity and association rules for recommendations.
- Statistical rules and Isolation Forest for anomaly detection.

Model outputs depend on the quality, completeness, and structure of the input data.

## Dataset Considerations

The original dataset does not contain a unique Customer ID. Therefore, customer-related analyses use available transaction and demographic cohort information rather than claiming to identify individual customers.

Forecasts and anomaly flags are analytical estimates and should be interpreted alongside business context.

## Future Enhancements

- Improve model evaluation using additional real-world datasets.
- Strengthen uploaded-dataset integration across all analytics modules.
- Improve forecast validation and recommendation evaluation.
- Enhance deployment, documentation, and automated testing.

## Author

**Hema Suma Gurajarla**

GitHub: [@springboardmentor160-debug](https://github.com/springboardmentor160-debug)

---

*MarketMind AI — Turning sales data into actionable business insights.*