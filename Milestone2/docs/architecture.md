# MarketMind AI — Milestone 1 Architecture

## Architecture

```text
Business Owner / Store Manager / Sales Executive / Admin
                         |
                         v
                  React Frontend
                         |
                         v
                    FastAPI API
             ____________|____________
            |            |            |
        Auth/RBAC     Business      Dashboard
                       APIs
            |            |            |
            |            v            |
            |        SQLite DB <------+
            |
            +---- JWT Authentication
```

## Database

```text
users
customers
products
sales
inventory
invoices
```

Relationships:

- `sales.customer_id -> customers.customer_id`
- `sales.product_id -> products.product_id`
- `inventory.product_id -> products.product_id`
- `invoices.sale_id -> sales.id`
```
