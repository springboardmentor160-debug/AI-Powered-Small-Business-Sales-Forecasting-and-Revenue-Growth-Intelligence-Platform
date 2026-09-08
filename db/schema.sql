-- MarketMind schema (SQLite). Tables are created automatically by SQLAlchemy
-- (backend/models.py) on first run; this file documents the same shape.

CREATE TABLE roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME
);

CREATE TABLE outlets (
    outlet_id VARCHAR(50) PRIMARY KEY,
    outlet_name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    contact_phone VARCHAR(30),
    created_at DATETIME
);

CREATE TABLE staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role_id INTEGER NOT NULL REFERENCES roles(role_id),
    outlet_id VARCHAR(50) REFERENCES outlets(outlet_id),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME
);

CREATE TABLE patrons (
    patron_id VARCHAR(50) PRIMARY KEY,
    patron_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(30),
    created_at DATETIME
);

CREATE TABLE menu_items (
    item_id VARCHAR(50) PRIMARY KEY,
    item_name VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL,
    unit_price FLOAT NOT NULL,
    stock_units INTEGER NOT NULL DEFAULT 0,
    reorder_level INTEGER NOT NULL DEFAULT 10,
    last_updated DATETIME
);

CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    order_time DATETIME NOT NULL,
    item_id VARCHAR(50) NOT NULL REFERENCES menu_items(item_id),
    quantity INTEGER NOT NULL,
    unit_price FLOAT NOT NULL,
    total_amount FLOAT NOT NULL,
    outlet_id VARCHAR(50) NOT NULL REFERENCES outlets(outlet_id),
    patron_id VARCHAR(50) REFERENCES patrons(patron_id),
    payment_mode VARCHAR(50) NOT NULL,
    created_at DATETIME
);
