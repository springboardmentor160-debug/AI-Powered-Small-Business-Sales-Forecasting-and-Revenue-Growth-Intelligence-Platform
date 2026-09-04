import sqlite3
import pandas as pd


# -----------------------------------------
# Load CSV files
# -----------------------------------------

sales = pd.read_csv("data/clean_retail_sales.csv")

customers = pd.read_csv("data/clean_customers.csv")

products = pd.read_csv("data/clean_products.csv")

inventory = pd.read_csv("data/clean_inventory.csv")


# -----------------------------------------
# Connect to database
# -----------------------------------------

connection = sqlite3.connect("database/marketmind.db")

cursor = connection.cursor()


# -----------------------------------------
# Create data tables
# -----------------------------------------

sales.to_sql(
    "sales",
    connection,
    if_exists="replace",
    index=False
)

customers.to_sql(
    "customers",
    connection,
    if_exists="replace",
    index=False
)

products.to_sql(
    "products",
    connection,
    if_exists="replace",
    index=False
)

inventory.to_sql(
    "inventory",
    connection,
    if_exists="replace",
    index=False
)


# -----------------------------------------
# Create Users Table
# -----------------------------------------

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
""")


# -----------------------------------------
# Delete dummy Swagger user
# -----------------------------------------

cursor.execute("""
    DELETE FROM users
    WHERE name = 'string'
    OR email = 'string'
""")


# -----------------------------------------
# Fix Arya's role
# -----------------------------------------

cursor.execute("""
    UPDATE users
    SET role = 'user'
    WHERE email = 'arya@example.com'
""")


# -----------------------------------------
# Make sure Admin is admin
# -----------------------------------------

cursor.execute("""
    UPDATE users
    SET role = 'admin'
    WHERE email = 'admin@marketmind.com'
""")


# -----------------------------------------
# Save changes
# -----------------------------------------

connection.commit()

connection.close()


# -----------------------------------------
# Success messages
# -----------------------------------------

print("Database created successfully!")

print("Sales records:", len(sales))

print("Customer records:", len(customers))

print("Product records:", len(products))

print("Inventory records:", len(inventory))

print("Users cleaned and roles updated successfully!")