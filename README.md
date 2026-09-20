# MarketMindAI

## Small Business Sales Intelligence Platform

**Author:** Aditya Pandya  
**Internship:** Infosys Internship Project  
**Current milestone:** Milestone 1  
**Planned expansion:** Milestone 2 + Walmart M5 demand/forecasting data integration
**Repository branch:** 'aditya-pandya-milestone-1'

---

## 1. Executive Overview

**MarketMindAI** is a growing sales-intelligence platform designed to help small and medium-sized retail businesses turn operational data into actionable business information.

The platform is being developed incrementally across the internship milestones. Milestone 1 establishes the application foundation: a Streamlit presentation layer, FastAPI backend, authentication and role-based access control, UCI Online Retail II data processing, sales summaries, a forecast prototype, and initial invoice/governance workflows.

The architecture is intentionally being kept extensible so later milestones can add advanced analytics, forecasting, customer intelligence, recommendations, anomaly detection, and production deployment without replacing the approved application structure.

> **Documentation rule  :** implemented functionality, prototype functionality, and planned functionality are explicitly distinguished.
> **Repository principle:** implemented capabilities are documented as implemented; future capabilities are explicitly marked as planned or in-progress.

---

## 2. Project Vision

MarketMindAI is intended to evolve from a basic retail analytics application into a unified business-intelligence platform covering:

- sales intelligence
- customer intelligence
- demand and revenue forecasting
- inventory intelligence
- invoicing workflows
- role-based dashboards / business dashboards
- AI/ML-driven recommendations
- churn and anomaly insights
- reporting and deployment

The project is being developed milestone by milestone so that each stage provides a usable foundation for the next.

---

## 3. Milestone Roadmap

| Milestone | Focus | Status |
|---|---|---|
| **M1** | Application foundation, data foundation, dashboard, authentication, RBAC, initial analytics | ✅ Current |
| **M2** | Advanced analytics, forecasting, segmentation, M5 dataset integration | 🔵 Planned |
| **M3** | Recommendations, churn prediction, anomaly detection | 🔵 Planned |
| **M4** | Testing, deployment, documentation, final demonstration | 🔵 Planned |

### Planned M2 data expansion

Milestone 2 is planned to introduce the **Walmart M5 dataset** as an additional data source for demand/forecasting-oriented analysis.

The M5 source will be treated as a distinct source with its own identifiers and provenance. Raw UCI and M5 records should not be treated as if their product/customer identifiers are automatically interchangeable.

---

## 4. Architecture

### 4.1 Long-term target architecture

```text
                         User
                           │
                           ▼
                Presentation Layer
              Streamlit / React UI
                           │
                           ▼
                 API / Gateway Layer
                        FastAPI
                           │
                           ▼
                Business Services Layer
          Sales | Customers | Inventory | Invoices
                           │
                           ▼
                  AI / Analytics Layer
       Forecasting | Segmentation | Recommendations
              Churn | Anomaly Detection
                           │
                           ▼
                  Data / Storage Layer
        PostgreSQL + approved source datasets

```
> **['docs/architecture.md'] :** The detailed architecture, layer responsibilities, data integration strategy, and milestone evolution.

### 4.2 Current Milestone 1 implementation

The current M1 repository is intentionally simpler:

```text
User
  │
  ▼
Streamlit Frontend
  │
  ▼
FastAPI Backend
  │
  ├── Authentication / RBAC
  ├── Sales Summary
  ├── Forecast Prototype
  ├── Invoice Workflow
  └── Admin User View
  │
  ▼
UCI Online Retail II CSV sources
  │
  ▼
Pandas processing + in-memory analytics cache
```

The distinction is important: the target architecture describes how the platform is intended to evolve; it should not be read as a claim that every target layer is already implemented in M1.

---

## 5. Technology Stack

| Area | Technology | Current role |
|---|---|---|
| Language | Python | Application and data-processing language |
| Frontend | Streamlit | Current dashboard and authentication UI |
| Backend | FastAPI | REST API and application backend |
| Server | Uvicorn | Local ASGI server |
| Data processing | Pandas | CSV loading and analytics |
| Authentication | JWT | Bearer-token authentication |
| Password security | bcrypt | Password hashing |
| Validation | Pydantic | Request/model validation |
| Current data source | UCI Online Retail II | M1 transaction foundation |
| Planned M2 source | Walmart M5 | Demand/forecasting expansion |
| Database direction | PostgreSQL | Planned/pending integration |
| Version control | Git + GitHub | Source control and milestone collaboration |

---

## 6. Current Milestone 1 Capabilities

### Authentication

- User registration endpoint
- Login endpoint
- JWT access-token generation
- Bearer-token protected API requests
- Password hashing with bcrypt

### Role-Based Access Control

The current application models the following roles:

- `business_owner`
- `store_manager`
- `sales_executive`
- `admin`

Backend authorization dependencies are used to restrict protected endpoints according to role.

### Sales Intelligence

The current backend loads the two UCI-derived CSV source files and prepares a cached analytical summary including:

- total revenue
- total valid orders
- top product by quantity

### Forecast Prototype

The current application exposes a revenue-forecast route and presents sample forecast-trend output in the Streamlit interface.

This is documented as a **prototype/initial implementation**, not as a validated production forecasting model.

### Invoice Workflow

The current interface exposes:

- invoice viewing workflow
- invoice creation workflow

These are part of the M1 application foundation and still require persistence/production hardening in later stages.

### Administration

An administrative endpoint provides a basic view of registered user profiles for authorized users.

---

## 7. Data Architecture

### 7.1 Milestone 1 — UCI Online Retail II

The current M1 implementation uses UCI Online Retail II transaction data.

Relevant source attributes include:

- invoice number
- stock/product code
- product description
- quantity
- invoice date
- unit price
- customer identifier
- country

The source files are retained as project data inputs and processed by the backend at startup.

### 7.2 Milestone 2 — Walmart M5

M5 is planned as a separate data source for demand and forecasting analysis.

The integration strategy should preserve:

- source identity
- original source identifiers
- dataset-specific semantics
- provenance
- transformation history

The platform should integrate the datasets at the application/data-service level instead of blindly concatenating their raw rows.

---

## 8. Data Governance and Provenance

MarketMindAI distinguishes between:

### Observed source data

Values directly available in the source dataset.

### Derived analytics

Values calculated from observed transaction data, such as:

- revenue
- order counts
- top-product calculations
- aggregated product/customer metrics

### Estimated inventory

M1 does not contain verified physical stock-count records.

The current inventory concept is therefore an **estimate derived from sales**, rather than observed warehouse stock.

The documented M1 estimation approach is:

```text
Initial Stock = Total Units Sold × 1.5

Estimated Remaining Stock =
    Initial Stock − Total Units Sold
```

These figures must be presented as estimates and should not be represented as verified physical inventory.

---

## 9. Project Structure

```text
marketmindai/
│
├── backend/
│   ├── main.py
│   ├── online_retail_v1.csv
│   ├── online_retail_v2.csv
│   └── preview_milestone2.py
├── docs/
│   ├── screenshots
│   └── architecture.md
├── frontend/
│   └── app.py
├──.gitignore
└── README.md
```
Repository metadata, Python virtual environments, cache files, and environment secrets are excluded through `.gitignore`.
The repository intentionally keeps the current M1 structure simple. Additional modules should be introduced only when required by the approved milestone architecture and actual implementation needs.

## 9.1 Documentation Map

| Document | Purpose |
|---|---|
| `README.md` | Main project overview and navigation |
| `docs/architecture.md` | Layered architecture, data integration strategy, and milestone evolution |
| `docs/screenshots/` | Milestone evidence and UI screenshots |

> Future documentation can be added under `docs/` as the platform grows without restructuring the application itself.
---

## 10. API Surface — Milestone 1

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/register` | Register a user |
| `POST` | `/login` | Authenticate a user and issue a JWT |
| `GET` | `/sales/summary` | Return current sales KPI summary |
| `GET` | `/forecast/revenue` | Return forecast prototype output |
| `GET` | `/invoices/view` | View invoice workflow |
| `POST` | `/invoices/create` | Create invoice workflow entry |
| `GET` | `/admin/users` | Authorized administrative user view |

Protected endpoints require a valid bearer token and, where applicable, an authorized role.

---

## 11. Security Model

The M1 foundation includes:

```text
User
  │
  ├── Register
  │
  └── Login
        │
        ▼
     JWT Token
        │
        ▼
 Authorization Header
        │
        ▼
 FastAPI Authentication Dependency
        │
        ▼
 Role Validation
        │
        ▼
 Protected Endpoint
```

Security hardening planned for later iterations includes:

- moving secrets out of source code
- persistent user storage
- stronger administration controls
- production CORS configuration
- broader security testing
- deployment-specific secret management

---

## 12. Current Limitations

The repository intentionally documents known limitations rather than presenting prototype behavior as production functionality.

Current M1 limitations include:

- user data is currently maintained in application memory rather than persistent database storage
- source analytics are CSV-based
- PostgreSQL application integration remains a subsequent integration step
- forecasting is a prototype/initial output and requires validation
- invoice workflows require persistence and fuller validation
- inventory values are estimates rather than physical stock counts
- production secret/configuration hardening remains to be completed
- broader automated testing and deployment are planned for later milestones

---

## 13. Milestone Implementation Matrix

| Capability | M1 | M2 | M3 | M4 |
|---|:---:|:---:|:---:|:---:|
| Authentication | ✅ | Enhance | Enhance | Validate |
| RBAC | ✅ | Enhance | Enhance | Validate |
| Sales analytics | ✅ | Enhance | Enhance | Validate |
| Inventory estimation | ✅ | Enhance | Enhance | Validate |
| PostgreSQL integration | 🟡 | 🔵 | Extend | Validate |
| Forecasting | 🟡 | 🔵 | Enhance | Validate |
| Walmart M5 integration | — | 🔵 | Extend | Validate |
| Customer segmentation | — | 🔵 | Enhance | Validate |
| Product recommendations | — | — | 🔵 | Validate |
| Churn prediction | — | — | 🔵 | Validate |
| Anomaly detection | — | — | 🔵 | Validate |
| Deployment | — | — | — | 🔵 |
| Final documentation | — | — | — | 🔵 |

**Legend**

- ✅ Implemented
- 🟡 Prototype / validation or hardening required
- 🔵 Planned
- — Not part of the current milestone scope

---

## 14. Local Setup

### Prerequisites

- Python 3.x
- Git
- PyCharm or another Python IDE
- Required Python packages for the backend/frontend

### Backend

```powershell
cd backend
python -m uvicorn main:app --reload
```

The FastAPI backend runs locally on:

```text
http://127.0.0.1:8000
```

### Frontend

Open a second terminal:

```powershell
cd frontend
python -m streamlit run app.py
```

The Streamlit application then connects to the FastAPI backend through:

```text
http://127.0.0.1:8000
```

---

## 15. Development Workflow

The repository follows a milestone-based development approach:

```text
Design
  ↓
Implementation
  ↓
Validation
  ↓
Documentation
  ↓
Milestone Review
  ↓
Next-Milestone Extension
```

The architecture is intended to remain stable while individual capabilities are expanded.

---

## 16. Engineering Principles

MarketMindAI follows these principles:

1. **Preserve the approved architecture.**
2. **Separate source data from derived analytics.**
3. **Maintain dataset provenance.**
4. **Do not present estimates as observed facts.**
5. **Document implemented versus planned functionality clearly.**
6. **Prefer incremental, testable improvements over unnecessary complexity.**
7. **Keep the repository maintainable as the project grows across milestones.**

---

## 17. Future Platform Direction

The planned evolution is:

```text
M1 - Foundation
   ↓
M2 - Data Expansion + Forecasting + Segmentation
   ↓
M3 - Decision Intelligence
     │
     ├── Recommendations
     ├── Churn
     └── Anomaly Intelligence
   ↓
M4 - Production Delivery
     │
     ├── Testing
     ├── Deployment
     └── Final Demonstration
```

The long-term goal is a single role-aware business-intelligence platform in which operational retail data feeds analytics and AI capabilities through a consistent application architecture.

---

## 18. Milestone Evidence

Each milestone should be supported by verifiable repository and project evidence, such as:

- source code
- architecture documentation
- authentication screenshots
- sales analytics evidence
- forecast prototype evidence
- invoice workflow evidence
- RBAC/authorization evidence
- data documentation
- API behavior
- dashboard screenshots
- validation/test results
- milestone reports
- implementation notes

The repository README is intended to remain the central navigation document as the project evolves.

---

## 19. Status

**Current repository stage: Milestone 1 — Foundation**

The M1 repository establishes the initial MarketMindAI application structure and provides the foundation for subsequent data, analytics, AI/ML, testing, and deployment work.

The repository is designed to evolve without replacing the approved application architecture. Future milestone additions should update the implementation sections and status indicators rather than rewriting the project's foundational structure.

**Next major expansion:** Milestone 2, including Walmart M5 data integration and advanced forecasting/segmentation capabilities.

## The Author

**Aditya Pandya**

Infosys Internship Project — MarketMindAI

---