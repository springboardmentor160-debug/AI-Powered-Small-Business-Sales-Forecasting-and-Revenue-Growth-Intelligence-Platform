# MarketMind AI — Project Objectives & Overview

## 1. Problem Statement

Small and medium retail businesses face critical operational bottlenecks:
- **Fragmented Sales Data**: Sales transactions are recorded across disparate Point-of-Sale (POS) systems, cash logs, and manual spreadsheets without centralized analytics.
- **Inventory Stockouts and Overstocking**: Lack of real-time inventory visibility leads to loss of sales due to stockouts of popular items or capital tied up in slow-moving merchandise.
- **Lack of Actionable Insights**: Business owners often lack data science tools to analyze customer purchase behavior, peak sales trends, or store performance across multiple locations.
- **Role Inaccessibility**: Front-line store managers and sales executives lack tailored, role-specific views suited to their daily workflow responsibilities.

**MarketMind AI** solves these challenges by providing an intelligent, lightweight sales and inventory intelligence platform. It ingests raw transactional data, cleans and structures it into relational storage, and provides role-aware dashboard analytics for real-time decision making.

---

## 2. Target User Personas & Roles

MarketMind AI features a **Role-Based Access Control (RBAC)** architecture supporting four distinct organizational roles:

| User Role | Key Responsibilities | Access Scope & Dashboard Views |
| :--- | :--- | :--- |
| **Business Owner** | Executive oversight, strategic planning, financial health tracking, location expansion. | **Global View**: Access to overall revenue, net sales trends, top performing products, cross-store metrics, and store comparison analytics. |
| **Store Manager** | Local inventory management, stock replenishment alerts, daily store sales targets. | **Store-Specific View**: Store inventory stock levels, low-stock reorder alerts, daily store sales performance, and staff/register metrics. |
| **Sales Executive** | Front-line customer interactions, individual transaction processing, daily targets. | **Personal / Operational View**: Personal sales total, recent transaction logs, product quick-lookup, and payment method statistics. |
| **Administrator** | System maintenance, user provision/deprovision, RBAC role assignment, system health audit. | **Admin Control Panel**: User management interface, database stats, role configuration, data pipeline status, and system audit logs. |

---

## 3. End-to-End Data Flow Architecture

The data pipeline transforms raw POS streams into actionable interactive dashboards:

```mermaid
flowchart TD
    subgraph Source ["1. Data Ingestion (Raw Data Layer)"]
        A1[POS Raw CSV Exports]
        A2[Inventory Log Files]
        A3[Customer Transaction Feeds]
    end

    subgraph Prep ["2. Data Prep & ETL Pipeline (Backend Python Engine)"]
        B1[generate_raw_data.py] --> B2[clean_data.py Engine]
        B2 -->|Handling Missing Values| B3[Standardized Fields]
        B2 -->|Fixing Date & Casing Formats| B3
        B2 -->|Deduplication & Schema Validation| B3
        B3 -->|Output Clean CSVs| C1[data/processed/clean_sales.csv]
        B3 -->|ORM / SQL Loader| C2[(SQLite / PostgreSQL DB)]
    end

    subgraph Storage ["3. Database & Persistence Layer"]
        C2 --> D1[users table]
        C2 --> D2[transactions table]
        C2 --> D3[inventory table]
        C2 --> D4[stores & customers tables]
    end

    subgraph Application ["4. Application & API Layer (FastAPI Backend)"]
        E1[JWT Auth / RBAC Middleware]
        E2[Analytics Service Engine]
        E3[RESTful API Endpoints]
        C2 <-->|SQLAlchemy / SQL Queries| E2
        E1 --> E3
        E2 --> E3
    end

    subgraph Dashboard ["5. Frontend Presentation Layer (React SPA)"]
        F1[Auth Gateway / Login Page]
        F2[Role Router]
        F3[Business Owner Dashboard]
        F4[Store Manager Dashboard]
        F5[Sales Executive Dashboard]
        F6[Admin Dashboard]

        F1 -->|JWT Token| F2
        F2 -->|Role: Owner| F3
        F2 -->|Role: Manager| F4
        F2 -->|Role: Sales Exec| F5
        F2 -->|Role: Admin| F6
        E3 <-->|JSON REST APIs| F1
        E3 <-->|REST API Data| F3
        E3 <-->|REST API Data| F4
        E3 <-->|REST API Data| F5
        E3 <-->|REST API Data| F6
    end
```

---

## 4. Key Success Criteria (Milestone 1)

1. Automated synthetic data generation and cleaning script pipeline.
2. Normalized database schema supporting SQLite / relational persistence.
3. Modular FastAPI backend returning real-time sales and inventory metrics.
4. Interactive React single-page frontend with responsive charts and metrics cards.
5. RBAC security layer ensuring data isolation by user privilege level.
