# MarketMind AI Database Design

## users
- id
- name
- email
- password_hash
- role

## customers
- id
- customer_id
- customer_name
- email
- city
- registration_date

## products
- id
- product_id
- product_name
- category
- unit_price

## sales
- id
- order_id
- order_date
- product_id
- product_name
- customer_id
- quantity
- unit_price
- revenue

## inventory
- id
- product_id
- product_name
- category
- stock_level
- reorder_point
- unit_price
- warehouse

## invoices
- id
- sale_id
- invoice_number
- amount
- payment_status
- invoice_date
