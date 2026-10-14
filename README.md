# MarketMind AI — Small Business Sales Intelligence Platform

**An AI-powered platform for sales analytics, revenue forecasting, customer segmentation, product recommendations, churn prediction, and anomaly detection.**

MarketMind AI helps small businesses transform historical sales data into actionable insights through machine learning, interactive dashboards, and business reporting.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [AI Modules](#ai-modules)
- [User Roles](#user-roles)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Docker](#docker)
- [API Documentation](#api-documentation)
- [Model Evaluation](#model-evaluation)
- [Deployment](#deployment)
- [Security](#security)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)
- [Author](#author)

## Overview

MarketMind AI is a full-stack business intelligence application developed to demonstrate how traditional machine learning can support small-business decision-making.

The platform combines a React dashboard with a FastAPI backend and machine-learning pipelines to analyze sales performance, identify customer segments, forecast revenue, recommend products, predict customer churn, and detect unusual sales activity.

The project is developed incrementally through four milestones:

- **Milestone 1:** Application foundation, data processing, database integration, authentication, role-based access control, and dashboards.
- **Milestone 2:** Customer segmentation, revenue forecasting, model comparison, and business reporting.
- **Milestone 3:** Product recommendations, churn prediction, and anomaly detection.
- **Milestone 4:** Model evaluation, error handling, integration testing, Docker packaging, deployment preparation, and final documentation.

## Features

- Sales data processing and cleaning.
- Business analytics dashboard.
- Revenue, order, and sales performance indicators.
- Customer segmentation using clustering.
- Revenue forecasting using multiple models.
- Customer-product recommendations.
- Association rule mining.
- Customer churn probability and risk classification.
- Sales anomaly detection.
- Downloadable business reports.
- JWT-based authentication.
- Role-based access control.
- REST APIs built with FastAPI.
- Automated testing and model evaluation.
- Docker and Docker Compose support, subject to verified configuration.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React 19, Vite |
| Backend | Python 3.13, FastAPI |
| Database | SQLite, SQLAlchemy |
| Data processing | pandas, NumPy |
| Machine learning | scikit-learn, XGBoost |
| Time-series forecasting | Prophet |
| Authentication | JWT, bcrypt |
| API testing | pytest, FastAPI testing utilities |
| Version control | Git, GitHub |
| Containerization | Docker, Docker Compose |
| Deployment | Render or Railway, depending on final configuration |

## System Architecture

```text
                    User
                     |
                     v
          React + Vite Frontend
                     |
              REST API Requests
                     |
                     v
              FastAPI Backend
                     |
          Authentication + RBAC
                     |
          +----------+----------+
          |          |          |
          v          v          v
       SQLite     Data/ML     Reporting
      Database   Pipelines     Service
                     |
       +-------------+-------------+
       |             |             |
       v             v             v
   Forecasting   Segmentation   Recommendations
       |             |             |
       +-------------+-------------+
                     |
             Churn Prediction
                     |
             Anomaly Detection
                     |
                     v
          Dashboard + Business Reports
```

## AI Modules

### 1. Customer Segmentation

Groups customers according to their purchasing behavior and activity.

- Customer-level behavioral feature engineering.
- Feature scaling.
- K-Means clustering.
- Hierarchical/Agglomerative Clustering.
- Business-oriented customer segment labels.
- Silhouette Score evaluation, where the data supports it.

### 2. Sales Forecasting

Predicts future revenue from historical sales.

- Daily revenue time-series preparation.
- Prophet forecasting.
- Random Forest regression.
- XGBoost regression.
- Chronological model evaluation.
- Model comparison using MAE, RMSE, and R².
- Revenue forecasts with uncertainty bounds where supported by the selected model.

### 3. Product Recommendation

Identifies potentially relevant products for customers.

- Customer-product purchase matrix.
- Collaborative filtering.
- Cosine similarity.
- Association Rule Mining.
- Support, confidence, and lift.
- Precision@K and Recall@K evaluation when sufficient held-out purchase data is available.

### 4. Customer Churn Prediction

Estimates which customers may be at risk of becoming inactive.

- Customer behavioral features.
- Churn labeling based on the implemented inactivity definition.
- Logistic Regression baseline.
- Random Forest classification.
- XGBoost classification.
- Churn probability estimates.
- High, Medium, and Low risk categories.
- Evaluation using accuracy, precision, recall, and F1-score.

### 5. Anomaly Detection

Flags unusual sales transactions for further investigation.

- Statistical Z-score detection.
- Isolation Forest.
- Transaction quantity and price analysis.
- Total amount analysis.
- Anomaly alerts and severity information where implemented.
- Detection Accuracy and False Positive Rate evaluation using appropriately labeled test cases.

**Important:** An anomaly is a signal for human review, not proof of fraud.

## User Roles

The application uses role-based access control.

| Role | Intended permissions |
|---|---|
| Business Owner | Business analytics, forecasts, segmentation, churn, recommendations, and authorized exports |
| Store Manager | Permitted sales and inventory operations, recommendation reports, and segmentation summaries |
| Sales Executive | Authorized sales records, invoices, assigned customer information, and personal reports |
| System Administrator | System administration, user management, and AI configuration |

Actual access is determined by the backend's configured permission rules.

## Project Structure

The following is the intended high-level structure. Exact filenames may differ in the current repository.

```text
marketmind-ai/
├── backend/
│   ├── main.py
│   ├── services/
│   ├── routes/
│   └── tests/
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── data/
│   ├── raw/
│   └── processed/
├── db/
├── docs/
├── reports/
├── .gitignore
├── .env.example
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

Install the following tools:

- Python 3.13, or the Python version supported by the project dependencies.
- Node.js and npm, using a version compatible with the frontend.
- Git.
- Docker Desktop, if using containerized execution.

### 1. Clone the repository

```bash
git clone https://github.com/springboardmentor160-debug/AI-Powered-Small-Business-Sales-Forecasting-and-Revenue-Growth-Intelligence-Platform.git
cd AI-Powered-Small-Business-Sales-Forecasting-and-Revenue-Growth-Intelligence-Platform
```

### 2. Configure the Python environment

On Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If the project already contains a working virtual environment, activate it instead.

Install the dependencies using the dependency file maintained by the project:

```powershell
python -m pip install -r backend/requirements.txt
```

If the dependency file is stored elsewhere, use its actual repository path.

### 3. Configure environment variables

Inspect `.env.example` and configure the required variables using your local environment.

Typical settings may include:

- JWT secret.
- Database URL or database path.
- Frontend API base URL.
- CORS allowed origins.

Never commit real secrets to GitHub.

## Running the Application

Open two terminal windows from the project directory.

### Terminal 1 — Backend

Activate the virtual environment, then run:

```powershell
cd backend
python -m uvicorn main:app --reload
```

This command assumes `backend/main.py` exports the FastAPI application as `app`. Adjust it if the actual entry point differs.

### Terminal 2 — Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the frontend URL displayed by Vite, usually:

`http://localhost:5173`

### API documentation

When the backend is running, open:

`http://127.0.0.1:8000/docs`

This Swagger interface displays the available API endpoints and allows you to test requests.

## Testing

Run the tests from the project root using the configured virtual environment:

```powershell
python -m pytest
```

To display individual test results:

```powershell
python -m pytest -v
```

If pytest reports **zero collected tests**, investigate test filenames, test functions, directory configuration, and import errors. Zero collected tests must not be reported as a passing test suite.

The test suite should cover:

- Forecasting evaluation.
- Customer segmentation.
- Churn prediction.
- Recommendation metrics.
- Anomaly detection.
- API behavior.
- Authentication and authorization.
- Error handling.
- Regression tests for previous milestones.

Record the actual number of passed, failed, and skipped tests after execution.

## Docker

If the repository contains a valid Docker Compose configuration, validate it first:

```bash
docker compose config
```

Build the containers:

```bash
docker compose build
```

Start the application:

```bash
docker compose up
```

Stop the services:

```bash
docker compose down
```

Database persistence and environment-variable configuration must be verified before using the container setup for deployment.

## API Documentation

FastAPI automatically provides interactive API documentation when configured with its default documentation routes.

Available documentation:

- Swagger UI: `/docs`
- OpenAPI schema: `/openapi.json`
- ReDoc: `/redoc`

The actual API routes depend on the current backend implementation. The major functional areas include:

- Authentication and user management.
- Sales and inventory.
- Business analytics.
- Customer segmentation.
- Revenue forecasting.
- Product recommendations.
- Churn prediction.
- Anomaly detection.
- Business reporting.

Consult Swagger for the exact endpoint paths, request parameters, response formats, and authorization requirements.

## Model Evaluation

The final evaluation record is intended to be maintained at:

`reports/milestone4_test_results.csv`

The accompanying report is intended to be maintained at:

`reports/milestone4_evaluation_report.md`

| Module | Evaluation metrics |
|---|---|
| Sales forecasting | MAE, RMSE, R² |
| Customer segmentation | Silhouette Score |
| Churn prediction | Accuracy, Precision, Recall, F1-score |
| Product recommendations | Precision@K, Recall@K |
| Anomaly detection | Detection Accuracy, False Positive Rate |

Metrics must be calculated from actual model execution using appropriate evaluation data.

A small sample dataset can demonstrate the implementation pipeline but may not support statistically reliable performance claims. Undefined metrics must be marked unavailable rather than replaced with invented values.

## Deployment

The application is designed to be prepared for deployment to a cloud platform such as Render or Railway.

Deployment requires appropriate configuration for:

- Frontend hosting.
- Backend service.
- API base URL and CORS.
- Secure environment variables.
- Database persistence.
- Report and upload storage.
- Health checks.

A public deployment URL should be added here only after deployment and external verification.

**Deployment status:** Update this section with the actual provider, verified public URL, and any known limitations once deployment is complete.

## Security

- Keep secrets in environment variables or a secure secrets manager.
- Do not commit `.env` files containing real credentials.
- Enforce permissions on protected backend endpoints.
- Do not expose database credentials or internal stack traces.
- Use HTTPS for public deployments.
- Configure allowed CORS origins appropriately.
- Protect database and report storage.
- Rotate exposed credentials immediately.

## Limitations

- Model quality depends on the amount and quality of historical sales data.
- Small datasets may make model evaluation unreliable or some metrics undefined.
- Churn predictions depend on the chosen inactivity definition.
- Recommendations require sufficient customer-product interactions for meaningful results.
- Anomaly detection flags unusual patterns and does not independently establish fraud.
- Production deployment requires suitable database persistence, secure configuration, and monitoring.

## Future Enhancements

Potential future improvements include:

- Larger real-world datasets.
- More robust temporal model validation.
- Recommendation evaluation across a broader customer base.
- Improved churn features and calibration.
- Inventory anomaly monitoring.
- Automated scheduled reports.
- Expanded cloud monitoring and observability.
- Scalability improvements for concurrent users.

## Author

**Sultan Ansari**

Project: MarketMind AI — Small Business Sales Intelligence Platform

GitHub repository:

[AI-Powered Small Business Sales Forecasting and Revenue Growth Intelligence Platform](https://github.com/springboardmentor160-debug/AI-Powered-Small-Business-Sales-Forecasting-and-Revenue-Growth-Intelligence-Platform)

---

*MarketMind AI is an internship project demonstrating full-stack application development, machine learning, business analytics, model evaluation, and deployment practices.*
