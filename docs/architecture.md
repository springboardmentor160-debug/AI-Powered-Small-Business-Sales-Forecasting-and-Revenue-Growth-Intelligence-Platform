# MarketMind AI — Architecture Specification

## 1. System Overview

MarketMind AI is designed as a modern, high-performance web application utilizing a decoupled RESTful architecture. The system comprises a responsive React single-page application (SPA) on the frontend, a high-throughput Python FastAPI application on the backend, and a relational database (SQLite for development / PostgreSQL ready) for state and transactional storage.

---

## 2. System Architecture Diagram

```mermaid
graph TB
    subgraph Frontend ["Client Layer (React Single Page App)"]
        UI_Login["Login / Auth Screen"]
        UI_Owner["Owner Executive Dashboard"]
        UI_Manager["Store Manager Dashboard"]
        UI_Exec["Sales Executive Dashboard"]
        UI_Admin["Administrator Control Panel"]
        
        UI_State["Auth Context & Axios Interceptors (JWT stored in LocalStorage)"]
    end

    subgraph API_Gateway ["Backend Gateway & Middleware Layer (FastAPI)"]
        CORS["CORS Middleware"]
        AuthMiddleware["OAuth2 & JWT Verification Middleware"]
        RBACMiddleware["RBAC Role Validator Dep"]
    end

    subgraph API_Routers ["FastAPI API Routers (/api/v1)"]
        Router_Auth["/api/v1/auth (Login, Register, Me)"]
        Router_Sales["/api/v1/sales (Transactions, Metrics)"]
        Router_Inventory["/api/v1/inventory (Stock levels, Reorders)"]
        Router_Analytics["/api/v1/analytics (Trends, Category totals)"]
        Router_Users["/api/v1/users (Admin user management)"]
    end

    subgraph Database_Layer ["Persistence Layer"]
        ORM["SQLAlchemy ORM Model Layer"]
        DB[(SQLite / PostgreSQL Engine: marketmind.db)]
    end

    %% Client Interactions
    UI_Login --> UI_State
    UI_Owner --> UI_State
    UI_Manager --> UI_State
    UI_Exec --> UI_State
    UI_Admin --> UI_State

    UI_State -->|HTTP Requests with Bearer Token| CORS
    CORS --> AuthMiddleware
    AuthMiddleware --> RBACMiddleware

    %% Router Routing
    RBACMiddleware --> Router_Auth
    RBACMiddleware --> Router_Sales
    RBACMiddleware --> Router_Inventory
    RBACMiddleware --> Router_Analytics
    RBACMiddleware --> Router_Users

    %% DB Connections
    Router_Auth <--> ORM
    Router_Sales <--> ORM
    Router_Inventory <--> ORM
    Router_Analytics <--> ORM
    Router_Users <--> ORM
    
    ORM <--> DB
```

---

## 3. Technology Stack

| Layer | Technology Selected | Rationale |
| :--- | :--- | :--- |
| **Frontend UI** | React 18 (Vite) + Lucide Icons + Recharts | Fast rendering, modular component structure, and responsive rich interactive data visualization. |
| **Frontend Styling** | Modern Vanilla CSS / Glassmorphism Design | High aesthetic control, CSS custom properties design tokens, and smooth micro-animations. |
| **Backend API** | FastAPI (Python 3.14) | Asynchronous non-blocking framework, auto-generated OpenAPI / Swagger docs, fast execution speed. |
| **Security Layer** | Passlib (Bcrypt) + PyJWT | Industry standard password hashing and stateless token-based authorization. |
| **Database** | SQLite / SQLAlchemy ORM | Lightweight relational persistence zero-config setup, easily swappable with PostgreSQL via connection URI. |
| **Data Cleaning** | Pandas & Python standard library | Efficient data normalization, string cleansing, date parsing, and missing value imputation. |

---

## 4. Security & Access Control Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Client
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant Auth as JWT Auth Engine
    participant DB as Database Engine

    User->>FE: Enter Credentials (username, password)
    FE->>API: POST /api/v1/auth/login
    API->>DB: Query user by username
    DB-->>API: Return User Record & Hashed Password
    API->>Auth: Verify password against Hash
    alt Password Valid
        Auth-->>API: Generate Signed JWT Token (exp, user_id, role)
        API-->>FE: Return 200 OK { access_token, token_type, role, user_id }
        FE->>FE: Store token in state & redirect to Role Dashboard
    else Invalid Password
        API-->>FE: Return 401 Unauthorized
        FE-->>User: Display Invalid Credentials Error
    end

    User->>FE: View Analytics Dashboard
    FE->>API: GET /api/v1/analytics/summary (Header: Authorization Bearer JWT)
    API->>Auth: Validate JWT Signature & Expiry
    Auth-->>API: Valid Payload { role: "business_owner" }
    API->>API: Check Role Permissions (RBAC)
    API->>DB: Execute Aggregation Queries
    DB-->>API: Return Sales & Inventory Totals
    API-->>FE: Return 200 OK JSON Data
    FE-->>User: Render KPI Cards & Visual Charts
```
