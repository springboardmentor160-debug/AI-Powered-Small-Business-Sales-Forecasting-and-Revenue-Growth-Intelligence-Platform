# MarketMind AI: System Architecture

## Milestone 1, Day 3-4

This document defines the planned architecture for MarketMind AI. It is a design document only. FastAPI, React, authentication, RBAC, AI/ML models, dashboards, and APIs are not implemented in this milestone.

## Architecture layers

### 1. User Layer

The User Layer represents the people who use MarketMind AI:

- **Business Owner:** reviews business-wide sales, revenue, inventory, customer, forecast, and insight information.
- **Store Manager:** reviews store-level sales and inventory performance.
- **Sales Executive:** reviews customer activity, sales history, segmentation, and recommendations.
- **System Administrator:** maintains the platform configuration and user access configuration in future milestones.

### 2. Business Services Layer

The Business Services Layer contains the domain services that organize business workflows and calculations. Planned services are:

- **Sales:** transaction and revenue analysis.
- **Inventory:** stock-level and reorder-threshold monitoring.
- **Invoice:** future invoice-related business processing based on sales transactions.
- **Customer Segmentation:** preparation of customer groups from customer and sales behavior.
- **Forecasting:** preparation and delivery of revenue forecasts.
- **Churn Prediction:** identification of customers who may become inactive.
- **Recommendations:** product recommendations based on sales and customer behavior.
- **Anomaly Detection:** identification of unusual sales, inventory, or customer patterns.
- **Dashboard/Reports:** delivery of business metrics and analytical results to users.

These services are planned boundaries for later implementation, not current application modules.

### 3. AI Analytics Engine

The AI Analytics Engine will provide the analytical and AI/ML processing needed by the business services. It will consume approved processed data and produce forecasts, customer segments, recommendations, churn-risk results, and anomaly indicators. The engine will not directly own raw data or presentation concerns.

### 4. API / Gateway Layer

The API / Gateway Layer will provide a controlled interface between the presentation layer and backend services. In a later milestone, the planned FastAPI backend will route requests, validate inputs, call business services, and return structured results. API implementation is outside the current milestone.

### 5. Storage / Database Layer

The Storage / Database Layer will persist the relational business data and future analytical results. It will contain the designed users, stores, customers, products, sales transactions, and inventory entities. Raw CSV files remain the initial source inputs; the database is a future persistence layer for processed data.

### 6. Presentation / Dashboard / Reporting Layer

The Presentation / Dashboard / Reporting Layer will display business KPIs, sales and inventory information, customer insights, forecasts, alerts, recommendations, churn results, anomalies, and reports. The views will be organized for the Business Owner, Store Manager, Sales Executive, and System Administrator.

## Layer flow

The primary request and insight flow is:

1. A user selects a business view or report in the Presentation Layer.
2. The Presentation Layer sends the request through the API / Gateway Layer.
3. The API / Gateway Layer routes the request to the relevant Business Services Layer service.
4. The business service reads processed data from the Storage / Database Layer and calls the AI Analytics Engine when analytical processing is required.
5. The AI Analytics Engine returns analytical results to the business service.
6. The business service returns structured business results through the API / Gateway Layer.
7. The Presentation Layer displays the result as a dashboard view or report to the user.

Data preparation follows the earlier documented path from raw Sales, Inventory, and Customer data through exploration, cleaning, processed data, and database storage.

## Mermaid architecture diagram

```mermaid
flowchart TD
    U[User Layer\nBusiness Owner | Store Manager\nSales Executive | System Administrator]
    P[Presentation / Dashboard / Reporting Layer]
    G[API / Gateway Layer\nFuture FastAPI Backend]
    B[Business Services Layer\nSales | Inventory | Invoice\nSegmentation | Forecasting\nChurn | Recommendations | Anomaly Detection]
    A[AI Analytics Engine\nForecasts | Segments | Recommendations\nChurn Results | Anomaly Indicators]
    D[(Storage / Database Layer\nUsers | Stores | Customers\nProducts | Sales Transactions | Inventory)]

    U --> P
    P --> G
    G --> B
    B --> D
    B --> A
    A --> D
    A --> B
    D --> B
    B --> G
    G --> P
    P --> U
```

## Milestone boundary

Day 3-4 establishes the architecture design and layer responsibilities only. No FastAPI backend, React interface, authentication, JWT, RBAC implementation, AI/ML model, dashboard, or API is created by this document.
