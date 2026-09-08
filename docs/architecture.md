# MarketMind AI — System Architecture

## 1. Architectural Overview

MarketMind AI is designed as a modular, tiered web application optimized for reliability, clear separation of concerns, and security. The architecture separates the user presentation tier, backend API and business logic tier, authentication/authorization tier, and persistent storage tier.

```mermaid
graph TD
    subgraph ClientTier ["Presentation Layer (Client)"]
        UI[React 19 + Vite Frontend SPA]
        Router[Role-Based View Dispatcher]
        State[Auth & API State Manager]
        UI --> Router
        Router --> State
    end

    subgraph APITier ["Backend API Layer (FastAPI)"]
        FastAPI[FastAPI Gateway]
        CORS[CORS Middleware]
        AuthRouter["/api/v1/auth Router"]
        SalesRouter["/api/v1/sales Router"]
        InvRouter["/api/v1/inventory Router"]
        AnalyticsRouter["/api/v1/analytics Router"]
        UsersRouter["/api/v1/users Router"]

        FastAPI --> CORS
        CORS --> AuthRouter
        CORS --> SalesRouter
        CORS --> InvRouter
        CORS --> AnalyticsRouter
        CORS --> UsersRouter
    end

    subgraph SecurityTier ["Security & RBAC Layer"]
        BcryptModule[Bcrypt Password Hasher]
        JWTModule[PyJWT Token Provider]
        RBACGuard[Role-Based Dependency Guards]
    end

    subgraph DataTier ["Data Access & Persistence"]
        ORM[SQLAlchemy 2.0 ORM]
        SQLite[(SQLite Database: marketmind.db)]
        ORM --> SQLite
    end

    State -- "HTTP / REST (JSON + Bearer JWT)" --> FastAPI
    AuthRouter --> BcryptModule
    AuthRouter --> JWTModule
    UsersRouter --> RBACGuard
    SalesRouter --> RBACGuard
    InvRouter --> RBACGuard
    AnalyticsRouter --> RBACGuard
    FastAPI --> ORM
```

---

## 2. Component Responsibilities

### Presentation Layer (`frontend/`)
- **Technology**: React 19, Vite, Vanilla CSS.
- **Responsibility**: Provides responsive, accessible, and role-tailored dashboards for Business Owner, Store Manager, Sales Executive, and System Administrator.
- **Session Management**: Securely preserves the signed JWT token in browser `localStorage` and injects `Authorization: Bearer <token>` into outbound HTTP requests via `src/api.js`.

### Backend API Layer (`backend/`)
- **Technology**: FastAPI, Pydantic V2, Uvicorn.
- **Responsibility**: Handles request validation, routes incoming HTTP calls, performs business aggregations (sales summaries, reorder alerts, daily trend lines), and serves interactive OpenAPI documentation at `/docs`.

### Authentication & RBAC Layer (`backend/auth.py`, `backend/dependencies.py`)
- **Technology**: `bcrypt` for one-way password hashing, `PyJWT` for compact, stateless JSON Web Tokens.
- **Responsibility**: Verifies credentials, signs tokens with expiration timestamps, parses bearer headers, and executes role checks. Unauthenticated requests are rejected with `401 Unauthorized`, and unauthorized access to privileged endpoints (e.g. non-admin accessing `/api/v1/users`) is rejected with `403 Forbidden`.

### Data Persistence Layer (`backend/database.py`, `backend/models.py`)
- **Technology**: SQLAlchemy 2.0 ORM, SQLite 3.
- **Responsibility**: Enforces relational schema integrity with primary keys, foreign keys, unique constraints, and indexes across 6 tables: `users`, `customers`, `products`, `sales`, `inventory`, and `invoices`.

---

## 3. End-to-End Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Browser
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant Auth as Auth & RBAC Guard
    participant DB as SQLAlchemy / SQLite

    User->>FE: Enters credentials (username/password)
    FE->>API: POST /api/v1/auth/login
    API->>DB: Query user record by email or alias
    DB-->>API: User record (password_hash, role)
    API->>Auth: Verify bcrypt hash & generate JWT
    API-->>FE: HTTP 200 { access_token, user: { role } }
    FE->>FE: Store token & select Role Dashboard

    User->>FE: Navigates to Dashboard
    FE->>API: GET /api/v1/sales (with Bearer JWT)
    API->>Auth: Validate JWT & verify user role
    Auth-->>API: Authorized
    API->>DB: Query sales joined with product, customer, invoice
    DB-->>API: 8 sales records
    API-->>FE: HTTP 200 [ Sales List JSON ]
    FE-->>User: Render KPI cards, charts, and transaction table
```

---

## 4. Security & Role Permissions Matrix

| Endpoint | HTTP Method | Allowed Roles | Description |
|---|---|---|---|
| `/` | GET | Public | API health check |
| `/api/v1/auth/login` | POST | Public | Authenticate user & issue JWT |
| `/api/v1/auth/register` | POST | Public / Admin | Register new account |
| `/api/v1/auth/me` | GET | All authenticated roles | Retrieve current user profile |
| `/api/v1/sales` | GET | `owner`, `manager`, `sales_executive`, `admin` | List all sales transactions |
| `/api/v1/sales/summary` | GET | `owner`, `manager`, `sales_executive`, `admin` | Compute total revenue, orders, AOV |
| `/api/v1/inventory` | GET | `owner`, `manager`, `admin`, `sales_executive` | List inventory stock levels |
| `/api/v1/inventory/alerts` | GET | `owner`, `manager`, `admin`, `sales_executive` | Filter items below reorder threshold |
| `/api/v1/analytics/summary`| GET | `owner`, `manager`, `admin`, `sales_executive` | High-level KPIs, charts, trends |
| `/api/v1/users` | GET | **`admin` only** | List all users (403 for other roles) |
