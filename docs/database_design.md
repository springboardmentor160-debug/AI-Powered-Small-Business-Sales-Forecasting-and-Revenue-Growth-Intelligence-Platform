# MarketMind AI: Database Design

## Milestone 1, Day 3-4

This document defines the planned relational database for the MarketMind data foundation. It uses the actual fields from the current raw Sales, Inventory, and Customer datasets where applicable, while adding only the minimal shared entities needed for future platform reuse.

The database is a future design. No database, API, authentication, or application code is implemented in this milestone.

## Design principles

- Preserve the raw CSV files as source inputs; do not overwrite them with database transformations.
- Use stable identifiers to connect stores, products, customers, and transactions.
- Store dates as `DATE` values and monetary amounts as `DECIMAL` values in the relational design.
- Keep product and store information reusable by Sales and Inventory services.
- Allow future forecasting, segmentation, recommendations, churn prediction, and anomaly detection modules to query consistent transactional data.

## 1. `users`

Stores the platform users and their planned project roles. This table supports future platform access configuration; authentication and RBAC are not implemented here.

| Column     | Data type      | Key / constraints                         | Description                                                                             |
| ---------- | -------------- | ----------------------------------------- | --------------------------------------------------------------------------------------- |
| `user_id`  | `VARCHAR(20)`  | Primary key                               | Unique identifier for a platform user.                                                  |
| `name`     | `VARCHAR(150)` | Required                                  | User's display name.                                                                    |
| `email`    | `VARCHAR(255)` | Required, unique                          | User email address.                                                                     |
| `role`     | `VARCHAR(40)`  | Required                                  | One of `Business Owner`, `Store Manager`, `Sales Executive`, or `System Administrator`. |
| `store_id` | `VARCHAR(20)`  | Nullable foreign key to `stores.store_id` | Store assignment for users whose work is store-specific.                                |

**Relationships:** A store can be assigned to many users. A user belongs to zero or one store; a Business Owner or System Administrator may not need a store assignment.

## 2. `stores`

Stores the store identifiers used by the current Sales and Inventory datasets. The current raw files provide `store_id`; `store_name` and `city` are optional database-managed descriptors for future use.

| Column       | Data type      | Key / constraints | Description                               |
| ------------ | -------------- | ----------------- | ----------------------------------------- |
| `store_id`   | `VARCHAR(20)`  | Primary key       | Identifier of a store, such as `S001`.    |
| `store_name` | `VARCHAR(150)` | Nullable          | Human-readable store name when available. |
| `city`       | `VARCHAR(100)` | Nullable          | Store location when available.            |

**Relationships:** A store has many users, sales transactions, and inventory records.

## 3. `customers`

Stores the customer profile fields from `data/raw/customers/customers.csv`.

| Column              | Data type      | Key / constraints | Description                                      |
| ------------------- | -------------- | ----------------- | ------------------------------------------------ |
| `customer_id`       | `VARCHAR(20)`  | Primary key       | Stable customer identifier from the raw dataset. |
| `name`              | `VARCHAR(150)` | Required          | Customer display name.                           |
| `email`             | `VARCHAR(255)` | Required, unique  | Customer email address.                          |
| `gender`            | `VARCHAR(30)`  | Required          | Gender value recorded in the raw dataset.        |
| `age`               | `INTEGER`      | Required          | Customer age in years.                           |
| `city`              | `VARCHAR(100)` | Required          | Customer city.                                   |
| `registration_date` | `DATE`         | Required          | Customer registration date.                      |

**Relationships:** One customer can have many sales transactions. Customer attributes and transaction history support future segmentation, recommendations, and churn prediction.

## 4. `products`

Stores the shared product dimension represented in the Sales and Inventory datasets. It avoids repeating product details as the platform grows.

| Column         | Data type      | Key / constraints | Description                               |
| -------------- | -------------- | ----------------- | ----------------------------------------- |
| `product_id`   | `VARCHAR(20)`  | Primary key       | Product identifier from the raw datasets. |
| `product_name` | `VARCHAR(150)` | Required          | Product name.                             |
| `category`     | `VARCHAR(100)` | Required          | Product category.                         |

**Relationships:** One product can appear in many sales transactions and many inventory records, including records for different stores.

## 5. `sales_transactions`

Stores the sales transaction fields from `data/raw/sales/sales.csv`. The table name is explicit so it can support future invoice and sales services.

| Column           | Data type       | Key / constraints                               | Description                                          |
| ---------------- | --------------- | ----------------------------------------------- | ---------------------------------------------------- |
| `transaction_id` | `VARCHAR(30)`   | Primary key                                     | Unique sales transaction identifier.                 |
| `date`           | `DATE`          | Required                                        | Date on which the sale occurred.                     |
| `product_id`     | `VARCHAR(20)`   | Required foreign key to `products.product_id`   | Product sold.                                        |
| `quantity`       | `INTEGER`       | Required                                        | Number of units sold.                                |
| `unit_price`     | `DECIMAL(12,2)` | Required                                        | Price per unit.                                      |
| `total_amount`   | `DECIMAL(14,2)` | Required                                        | Transaction value, equal to `quantity * unit_price`. |
| `store_id`       | `VARCHAR(20)`   | Required foreign key to `stores.store_id`       | Store where the sale occurred.                       |
| `customer_id`    | `VARCHAR(20)`   | Required foreign key to `customers.customer_id` | Customer associated with the sale.                   |
| `payment_method` | `VARCHAR(40)`   | Required                                        | Payment method used for the transaction.             |

`product_name` and `category` are retained in the raw Sales CSV for source traceability, but the relational design uses the `products` table as the shared product reference.

**Relationships:** Each transaction belongs to one product, one store, and one customer. A customer, product, or store can be related to many transactions. This table is the primary source for sales analytics, revenue forecasting, recommendations, churn features, and anomaly detection.

## 6. `inventory`

Stores the inventory fields from `data/raw/inventory/inventory.csv`. Because the current inventory data is recorded by product and store, the primary key is composite.

| Column              | Data type      | Key / constraints                                           | Description                                                   |
| ------------------- | -------------- | ----------------------------------------------------------- | ------------------------------------------------------------- |
| `product_id`        | `VARCHAR(20)`  | Composite primary key; foreign key to `products.product_id` | Product whose stock is recorded.                              |
| `product_name`      | `VARCHAR(150)` | Required                                                    | Product name from the raw inventory dataset.                  |
| `category`          | `VARCHAR(100)` | Required                                                    | Product category from the raw inventory dataset.              |
| `stock_level`       | `INTEGER`      | Required                                                    | Current stock quantity at the store.                          |
| `reorder_threshold` | `INTEGER`      | Required                                                    | Stock level at which replenishment may need to be considered. |
| `store_id`          | `VARCHAR(20)`  | Composite primary key; foreign key to `stores.store_id`     | Store holding the stock.                                      |

**Relationships:** Each inventory record belongs to one product and one store. A product and a store can each have many inventory records. The composite key `(product_id, store_id)` prevents two current inventory records for the same product at the same store.

## Relationship summary

| Relationship                        | Cardinality | Purpose                                                      |
| ----------------------------------- | ----------- | ------------------------------------------------------------ |
| `stores` to `users`                 | One-to-many | Assign users to a store when their role requires it.         |
| `stores` to `sales_transactions`    | One-to-many | Analyze store-level sales and revenue.                       |
| `stores` to `inventory`             | One-to-many | Monitor stock by store.                                      |
| `customers` to `sales_transactions` | One-to-many | Build customer purchase history and customer-level features. |
| `products` to `sales_transactions`  | One-to-many | Analyze product demand, revenue, and recommendations.        |
| `products` to `inventory`           | One-to-many | Compare product availability across stores.                  |

## Future module reuse

The planned schema provides a shared foundation for the future Sales, Inventory, Invoice, Customer Segmentation, Forecasting, Churn Prediction, Recommendations, Anomaly Detection, and Dashboard/Reports modules. No separate future table is created for those modules at this stage; they can reuse the transaction, inventory, customer, product, store, and user data defined above.
