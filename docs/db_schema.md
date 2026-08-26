# MarketMind AI — Database Schema Specification

This document details the relational database schema, data types, constraints, and entity-relationship models for MarketMind AI.

---

## 1. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    ROLES ||--o{ USERS : "assigned to"
    STORES ||--o{ USERS : "assigned to"
    STORES ||--o{ TRANSACTIONS : "location for"
    CUSTOMERS ||--o{ TRANSACTIONS : "conducts"
    INVENTORY ||--o{ TRANSACTIONS : "purchased in"

    ROLES {
        int role_id PK
        string role_name UNIQUE
        string description
    }

    STORES {
        string store_id PK
        string store_name
        string location
        string contact_phone
    }

    USERS {
        int user_id PK
        string username UNIQUE
        string email UNIQUE
        string hashed_password
        string full_name
        int role_id FK
        string store_id FK
        boolean is_active
    }

    CUSTOMERS {
        string customer_id PK
        string customer_name
        string email
        string phone
    }

    INVENTORY {
        string product_id PK
        string product_name
        string category
        decimal unit_price
        int stock_level
        int reorder_threshold
    }

    TRANSACTIONS {
        string transaction_id PK
        datetime transaction_date
        string product_id FK
        int quantity
        decimal unit_price
        decimal total_amount
        string store_id FK
        string customer_id FK
        string payment_method
    }
```

---

## 2. Table Definitions

### Table: `roles`
Defines available system access levels.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `role_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique role identifier. |
| `role_name` | VARCHAR(50) | UNIQUE, NOT NULL | Role code (`business_owner`, `store_manager`, `sales_executive`, `administrator`). |
| `description` | TEXT | NULLABLE | Human-readable role description. |

### Table: `stores`
Stores organizational retail branch locations.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `store_id` | VARCHAR(50) | PRIMARY KEY | Store identifier (e.g. `STORE-001`). |
| `store_name` | VARCHAR(100) | NOT NULL | Retail branch name. |
| `location` | VARCHAR(150) | NULLABLE | Physical address / region. |
| `contact_phone` | VARCHAR(30) | NULLABLE | Branch contact number. |

### Table: `users`
System user accounts with credential hashes and role bindings.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique internal user ID. |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | Authentication username. |
| `email` | VARCHAR(100) | UNIQUE, NOT NULL | User email address. |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt hashed password. |
| `full_name` | VARCHAR(100) | NULLABLE | User full name. |
| `role_id` | INTEGER | FK -> `roles.role_id`, NOT NULL | Foreign key referencing system role. |
| `store_id` | VARCHAR(50) | FK -> `stores.store_id`, NULLABLE | Associated store branch (for Store Manager / Sales Exec). |
| `is_active` | BOOLEAN | DEFAULT 1 | Account status flag. |

### Table: `customers`
Registered loyalty customers.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `customer_id` | VARCHAR(50) | PRIMARY KEY | Customer identifier (e.g. `CUST-1001` or `GUEST`). |
| `customer_name` | VARCHAR(100) | NOT NULL | Customer full name. |
| `email` | VARCHAR(100) | NULLABLE | Contact email. |
| `phone` | VARCHAR(30) | NULLABLE | Contact telephone. |

### Table: `inventory`
Product catalog and real-time inventory tracking.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `product_id` | VARCHAR(50) | PRIMARY KEY | Unique SKU / product code (e.g. `P101`). |
| `product_name` | VARCHAR(150) | NOT NULL | Title of product. |
| `category` | VARCHAR(80) | NOT NULL | Standardized merchandise category. |
| `unit_price` | DECIMAL(10,2) | NOT NULL, >= 0 | Selling price per unit. |
| `stock_level` | INTEGER | NOT NULL, >= 0 | Available stock count. |
| `reorder_threshold` | INTEGER | NOT NULL, >= 0 | Alert threshold for low inventory. |

### Table: `transactions`
Individual line item sales transactions.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `transaction_id` | VARCHAR(50) | PRIMARY KEY | Transaction receipt ID. |
| `transaction_date` | TIMESTAMP | NOT NULL | POS sale timestamp. |
| `product_id` | VARCHAR(50) | FK -> `inventory.product_id`, NOT NULL | Sold product code. |
| `quantity` | INTEGER | NOT NULL, > 0 | Quantity sold. |
| `unit_price` | DECIMAL(10,2) | NOT NULL | Selling price per unit at transaction time. |
| `total_amount` | DECIMAL(10,2) | NOT NULL | Line item total amount (`quantity * unit_price`). |
| `store_id` | VARCHAR(50) | FK -> `stores.store_id`, NOT NULL | Store branch location where sale occurred. |
| `customer_id` | VARCHAR(50) | FK -> `customers.customer_id`, NULLABLE | Purchasing customer ID. |
| `payment_method` | VARCHAR(50) | NOT NULL | Payment channel used. |
