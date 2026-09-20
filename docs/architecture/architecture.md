# MarketMindAI — System Architecture

## 1. Architecture Overview

MarketMindAI follows a layered architecture designed to provide a stable foundation for incremental development across Milestones 1–4.

The architecture separates presentation, API access, business services, AI/analytics processing, and data/storage responsibilities.


                        ┌─────────────────────────┐
                        │          Users          │
                        │ Business Owner          │
                        │ Store Manager           │
                        │ Sales Executive         │
                        │ Administrator           │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   Presentation Layer    │
                        │      Streamlit UI       │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │    API / Gateway Layer  │
                        │        FastAPI          │
                        │ Authentication / RBAC   │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   Business Services     │
                        │ Sales                   │
                        │ Customers               │
                        │ Inventory               │
                        │ Invoices                │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │   AI / Analytics Engine │
                        │ Forecasting             │
                        │ Segmentation            │
                        │ Recommendations         │
                        │ Churn Analysis          │
                        │ Anomaly Detection       │
                        └────────────┬────────────┘
                                     │
                                     ▼
                        ┌─────────────────────────┐
                        │    Data / Storage Layer │
                        │ UCI Online Retail II    │
                        │ Future M5 Data Source   │
                        │ PostgreSQL              │
                        └─────────────────────────┘
---------------------------------------------------

## 2. Milestone 1 Architecture


              User
                │
                ▼
      ┌──────────────────┐
      │ Streamlit        │
      │ Frontend         │
      └────────┬─────────┘
               │ HTTP / REST
               ▼
      ┌──────────────────┐
      │ FastAPI Backend  │
      └────────┬─────────┘
               │
        ┌──────┼───────────┐
        │      │           │
        ▼      ▼           ▼
 Authentication Sales    Invoices
    / RBAC    Analytics  Workflow
        │
        └──────────┬───────────┘
                   ▼
        ┌──────────────────────┐
        │ Pandas Processing    │
        │ + Cached Analytics   │
        └──────────┬───────────┘
                   ▼
        ┌──────────────────────┐
        │ UCI Online Retail II │
        │ Source CSV Files     │
        └──────────────────────┘
--------------------------------
## 3. Layer Responsibilities

Presentation Layer

Technology: Streamlit

Responsibilities:

User interface
Login and registration
Dashboard presentation
Sales KPI visualization
Forecast visualization
Invoice interaction
Role-aware user experience
API / Gateway Layer

Technology: FastAPI + Uvicorn

Responsibilities:

REST API endpoints
Authentication
Authorization
Request handling
Input validation
Frontend/backend communication
Business Services Layer

Responsibilities:

Sales workflows
Customer-related operations
Inventory-related operations
Invoice workflows
Administrative operations
AI / Analytics Layer

Planned capabilities include:

Sales forecasting
Demand forecasting
Customer segmentation
Product recommendations
Churn prediction
Anomaly detection
Data / Storage Layer

Current M1 data source:

UCI Online Retail II

Planned M2 data source:

Walmart M5

Planned persistence direction:

PostgreSQL
----------

## 4. Data Integration Strategy

UCI Online Retail II ───────┐
                            │
                            ▼
                    Data Integration
                            │
M5 Dataset ─────────────────┘
                            │
                            ▼
                  Business / Analytics
                            │
                            ▼
                    AI / ML Services
                            │
                            ▼
                        FastAPI
                            │
                            ▼
                       Dashboard

Source identifiers, transformations, and provenance should be preserved.

The platform should not assume that identifiers from different datasets automatically represent the same products, customers, or transactions.
----------------------------------------------------------------------------------------------------------------------------------------------

## 5. Milestone Evolution

Milestone 1 —       Foundation
                    Streamlit frontend
                    FastAPI backend
                    Authentication
                    Role-Based Access Control
                    UCI Online Retail II data foundation
                    Initial sales analytics
                    Forecast prototype
                    Initial invoice workflow

Milestone 2 —       Intelligence Expansion
                    Walmart M5 dataset integration
                    Demand / sales forecasting
                    Customer segmentation
                    Advanced analytics

Milestone 3 —       Decision Intelligence
                    Product recommendation engine
                    Churn prediction
                    Anomaly detection
                    AI-generated business insights

Milestone 4 —       Production Delivery
                    Comprehensive testing
                    Deployment
                    Reliability improvements
                    Final documentation
                    End-to-end demonstration
--------------------------------------------

## 6. Architecture Principles

   1. Preserve the approved layered architecture.
   2. Keep presentation and backend responsibilities separated.
   3. Integrate future datasets through defined data and service layers.
   4. Preserve source-data provenance.
   5. Keep observed data separate from derived estimates.
   6. Add capabilities incrementally rather than replacing the core architecture.
   7. Keep the system maintainable across all internship milestones.
--------------------------------------------------------------------

## 7. Current vs Target Architecture

| Layer             | Milestone 1                             | Target Platform                                                      |
| ----------------- | --------------------------------------- | -------------------------------------------------------------------- |
| Presentation      | Streamlit                               | Streamlit / future interface expansion                               |
| API               | FastAPI                                 | FastAPI                                                              |
| Business Services | Initial workflows                       | Expanded service layer                                               |
| AI / Analytics    | Initial analytics + forecast prototype  | Forecasting, segmentation, recommendations, churn, anomaly detection |
| Data              | UCI Online Retail II CSV                | UCI + M5                                                             |
| Storage           | Current CSV / cached analytics approach | PostgreSQL integration                                               |
--------------------------------------------------------------------------------------------------------------------------------------

## 8. Architecture Status

Current stage: Milestone 1

The architecture is established as the foundation for later milestones. Future capabilities should extend the existing layers rather than replace the approved application structure.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 9. Author
Aditya Pandya

Infosys Internship Project — MarketMindAI

