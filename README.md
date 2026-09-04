# MarketMind AI

## AI-Powered Small Business Sales Forecasting and Revenue Growth Intelligence Platform

MarketMind AI is a full-stack business intelligence platform designed to help small businesses understand their sales performance, monitor inventory, analyze customers and products, and make data-driven business decisions.

The project combines a FastAPI backend, SQLite database, and ReactJS frontend to provide an interactive analytics dashboard. AI/ML capabilities such as customer segmentation, sales forecasting, recommendations, churn prediction, and anomaly detection are planned for later milestones.

---

## Project Objectives

The main objectives of MarketMind AI are to:

- Analyze historical retail sales data.
- Track revenue, orders, units sold, customers, and products.
- Identify top-performing products and customers.
- Analyze sales performance across countries.
- Monitor inventory levels.
- Provide business insights through an interactive dashboard.
- Implement secure user authentication.
- Implement role-based access control (RBAC).
- Build a foundation for future AI/ML-powered business intelligence.

---

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | ReactJS, Vite, Recharts |
| Backend | FastAPI, Python |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | JWT |
| Password Hashing | PBKDF2-SHA256 |
| API Documentation | Swagger / OpenAPI |
| Data Processing | Pandas |
| Development | VS Code, PowerShell, Git, GitHub |

---
## System Architecture

```text
                ┌─────────────────────────┐
                │       ReactJS UI        │
                │    Vite + Recharts      │
                └────────────┬────────────┘
                             │
                             │ REST API
                             ▼
                ┌─────────────────────────┐
                │       FastAPI API       │
                │                         │
                │ Authentication & RBAC   │
                │ Sales Analytics         │
                │ Product Analytics       │
                │ Customer Analytics      │
                │ Inventory Analytics     │
                └────────────┬────────────┘
                             │
                             ▼
                ┌─────────────────────────┐
                │      SQLAlchemy ORM     │
                └────────────┬────────────┘
                             │
                             ▼
                ┌─────────────────────────┐
                │      SQLite Database    │
                │                         │
                │ Users                   │
                │ Customers               │
                │ Products                │
                │ Sales                   │
                │ Inventory               │
                │ Invoices                │
                └─────────────────────────┘
```

---

## Data Preparation

The project uses a retail sales dataset containing transaction-level information.

The data preparation workflow included:

1. Loading the raw retail sales data.
2. Inspecting the dataset structure.
3. Handling missing and invalid values.
4. Cleaning transaction records.
5. Processing customer and product information.
6. Calculating revenue using:

```text
Revenue = Quantity × Unit Price
```

7. Saving the cleaned dataset for database processing.

### Processed Dataset

The cleaned dataset contains:

- **524,878 sales records**
- **3,922 unique products**
- **4,338 unique customers**

The large raw and processed datasets are intentionally excluded from the Git repository using `.gitignore`.

---
## Database Design

MarketMind AI uses SQLite with SQLAlchemy ORM.

### Database Tables

#### Users

Stores application users and their roles.

Fields include:

- ID
- Name
- Email
- Password Hash
- Role

#### Customers

Stores customer information.

Fields include:

- ID
- Customer ID
- Name
- Contact Information

#### Products

Stores product information.

Fields include:

- ID
- Stock Code
- Product Name
- Category
- Unit Price

#### Sales

Stores transaction-level sales information.

Fields include:

- ID
- Product ID
- Customer ID
- Quantity
- Sale Date
- Country

#### Inventory

Stores inventory information.

Fields include:

- ID
- Product ID
- Stock Level
- Reorder Point

#### Invoices

Stores invoice and payment information.

Fields include:

- ID
- Sale ID
- Amount
- Payment Status

---

## Backend API

The backend is developed using FastAPI.

### Main API Areas

#### Sales Analytics

- `/sales/summary`
- `/sales/trends`
- `/sales/revenue`
- `/sales/revenue/trends`
- `/sales/countries`
- `/sales/countries/revenue`

#### Product Analytics

- `/products/top`
- `/products/top-revenue`
- `/products/performance`

#### Customer Analytics

- `/customers/top`
- `/customers/top-revenue`

#### Inventory

- `/inventory/summary`
- `/inventory/low-stock`

#### Business Insights

- `/insights/overview`

#### Authentication

- `/register`
- `/login`
- `/auth/me`

#### Administration

- `/admin/users`

API documentation is available through FastAPI's Swagger interface during development.

---
## Dashboard

The ReactJS dashboard provides a visual overview of business performance.

The dashboard currently includes:

- Revenue KPI
- Units Sold KPI
- Orders KPI
- Customers KPI
- Products KPI
- Revenue Trend
- Top Products
- Top Customers
- Sales by Country
- AI Insights section
- Inventory Summary
- API connection status

All dashboard revenue values are displayed in **₹ (INR)** for the application's presentation layer.

---

## Authentication and Role-Based Access Control

MarketMind AI includes JWT-based authentication and role-based access control.

The system supports four user roles:

1. **Business Owner**
2. **Store Manager**
3. **Sales Executive**
4. **Administrator**

JWT tokens are used to authenticate API requests.

Role-based authorization is applied to protected endpoints so that users can access functionality according to their assigned role.

Passwords are stored using a password-hashing mechanism rather than plain-text passwords.

---

## Current Analytics

The current system successfully processes the cleaned retail dataset and provides analytics such as:

- Total revenue
- Total units sold
- Total orders
- Product performance
- Customer performance
- Country-level sales
- Inventory information
- Business-level summary insights

The analytics are currently based on deterministic database queries and business logic. The advanced AI/ML components will be introduced in later milestones.

---
## Milestone Progress

### Milestone 1 — Data, System Design and Initial Build

**Status: In Progress / Final Verification**

Completed:

- Retail sales dataset collected
- Dataset explored
- Data cleaning completed
- Cleaned transaction dataset prepared
- Database schema designed
- SQLite database implemented
- Sales data loaded into database
- Inventory structure initialized
- FastAPI backend implemented
- REST API endpoints implemented
- ReactJS dashboard implemented
- Revenue and sales analytics implemented
- JWT authentication implemented
- Role-based access control implemented

Final verification and security cleanup are being completed before Milestone 1 is marked fully complete.

---

### Milestone 2 — Customer Segmentation and Sales Forecasting

Planned features:

- Customer segmentation
- RFM analysis
- Sales forecasting
- Revenue forecasting
- Customer behavior analysis
- Forecast visualization

---

### Milestone 3 — Recommendations, Churn and Anomaly Detection

Planned features:

- Product recommendations
- Customer churn prediction
- Sales anomaly detection
- Revenue growth opportunities
- AI-generated business recommendations

---

### Milestone 4 — Testing, Deployment and Documentation

Planned activities:

- Backend testing
- Frontend testing
- API testing
- Authentication testing
- RBAC testing
- Performance optimization
- Deployment
- Final documentation

---
## Project Structure

```text
marketmind-ai/
│
├── backend/
│   ├── database.py
│   ├── initialize_inventory.py
│   ├── load_sales.py
│   ├── main.py
│   ├── models.py
│   └── update_countries.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── clean_data.py
├── README.md
└── .gitignore
```

Large datasets, generated databases, virtual environments, dependency folders, and other unnecessary files are excluded from version control.

---

## Running the Backend

Navigate to the backend directory:

```powershell
cd backend
```

Activate the Python virtual environment if required:

```powershell
..\venv\Scripts\Activate.ps1
```

Start the FastAPI development server:

```powershell
uvicorn main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Running the Frontend

Open another terminal and navigate to the project directory:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

## Security Considerations

The project includes:

- JWT-based authentication
- Password hashing
- Role-based authorization
- Protected administrative endpoints
- CORS configuration for the frontend
- Environment-based configuration planned for production
- Exclusion of sensitive and large local files through `.gitignore`

Before production deployment, secrets such as the JWT signing key should be moved to environment variables and production security settings should be applied.

---

## Development Status

MarketMind AI has progressed from initial data exploration to a working full-stack analytics application.

The current implementation provides:

- Cleaned retail transaction data
- Structured relational database
- FastAPI backend
- REST APIs
- ReactJS analytics dashboard
- Authentication
- Role-based access control
- Inventory analytics
- Business insights

The next major development stage is the implementation of the AI/ML modules for customer segmentation and sales forecasting.

---

## Future Enhancements

Future versions of MarketMind AI will focus on:

- Machine learning-based sales forecasting
- Customer segmentation
- Customer lifetime value analysis
- Churn prediction
- Product recommendation engine
- Anomaly detection
- Automated business recommendations
- Advanced dashboards
- Deployment and cloud infrastructure

---

## Author

**Krishna Gopal Patra**

MarketMind AI — Internship Project
