from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(
    title="MarketMind AI",
    description="AI-Powered Retail Sales Intelligence API"
)

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str


class UserLogin(BaseModel):
    email: str
    password: str

# -----------------------------------------
# Database Connection
# -----------------------------------------
def get_connection():
    connection = sqlite3.connect("database/marketmind.db")
    connection.row_factory = sqlite3.Row
    return connection


# -----------------------------------------
# Home
# -----------------------------------------
@app.get("/")
def home():
    return {
        "message": "MarketMind AI Backend is running"
    }


# -----------------------------------------
# Health Check
# -----------------------------------------
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# -----------------------------------------
# Dashboard Summary
# -----------------------------------------
@app.get("/summary")
def summary():

    connection = get_connection()
    cursor = connection.cursor()

    # Total Revenue
    cursor.execute("""
        SELECT SUM(Revenue)
        FROM sales
    """)
    total_revenue = cursor.fetchone()[0]

    # Total Sales / Invoices
    cursor.execute("""
        SELECT COUNT(DISTINCT InvoiceNo)
        FROM sales
    """)
    total_sales = cursor.fetchone()[0]

    # Total Customers
    cursor.execute("""
        SELECT COUNT(*)
        FROM customers
    """)
    total_customers = cursor.fetchone()[0]

    # Total Products
    cursor.execute("""
        SELECT COUNT(*)
        FROM products
    """)
    total_products = cursor.fetchone()[0]

    connection.close()

    return {
        "revenue": round(total_revenue or 0, 2),
        "sales": total_sales or 0,
        "customers": total_customers or 0,
        "products": total_products or 0
    }


# -----------------------------------------
# Inventory Summary
# -----------------------------------------
@app.get("/inventory/summary")
def inventory_summary():

    connection = get_connection()
    cursor = connection.cursor()

    # Total Inventory Products
    cursor.execute("""
        SELECT COUNT(*)
        FROM inventory
    """)
    total_products = cursor.fetchone()[0]

    # Total Stock Quantity
    cursor.execute("""
        SELECT SUM(Stock_Quantity)
        FROM inventory
    """)
    total_stock = cursor.fetchone()[0]

    # Low Stock Products
    cursor.execute("""
        SELECT COUNT(*)
        FROM inventory
        WHERE Stock_Quantity <= Reorder_Level
    """)
    low_stock = cursor.fetchone()[0]

    connection.close()

    return {
        "total_inventory_products": total_products or 0,
        "total_stock": total_stock or 0,
        "low_stock_products": low_stock or 0
    }


# -----------------------------------------
# Low Stock Products
# -----------------------------------------
@app.get("/inventory/low-stock")
def low_stock_products():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product_ID,
            Product_Name,
            Category,
            Stock_Quantity,
            Reorder_Level,
            Status
        FROM inventory
        WHERE Stock_Quantity <= Reorder_Level
        LIMIT 20
    """)

    rows = cursor.fetchall()

    connection.close()

    products = []

    for row in rows:
        products.append({
            "product_id": row[0],
            "product_name": row[1],
            "category": row[2],
            "stock_quantity": row[3],
            "reorder_level": row[4],
            "status": row[5]
        })

    return products


# -----------------------------------------
# Top Product
# -----------------------------------------
@app.get("/sales/top-product")
def top_product():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Description,
            SUM(Quantity) AS total_quantity
        FROM sales
        GROUP BY Description
        ORDER BY total_quantity DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row:
        return {
            "product": row[0],
            "quantity_sold": row[1]
        }

    return {
        "product": "No data",
        "quantity_sold": 0
    }


# -----------------------------------------
# Sales Trend - Last 30 Days
# -----------------------------------------
@app.get("/sales/trend")
def sales_trend():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            DATE(InvoiceDate) AS date,
            SUM(Revenue) AS revenue
        FROM sales
        WHERE InvoiceDate IS NOT NULL
        GROUP BY DATE(InvoiceDate)
        ORDER BY DATE(InvoiceDate) DESC
        LIMIT 30
    """)

    rows = cursor.fetchall()

    connection.close()

    # Reverse so oldest date comes first
    rows = rows[::-1]

    result = []

    for row in rows:
        result.append({
            "date": row[0],
            "revenue": round(row[1] or 0, 2)
        })

    return result


# -----------------------------------------
# Revenue Forecast
# Simple forecast based on recent sales data
# -----------------------------------------
@app.get("/forecast/revenue")
def revenue_forecast():

    connection = get_connection()
    cursor = connection.cursor()

    # Get recent daily revenue
    cursor.execute("""
        SELECT
            DATE(InvoiceDate) AS date,
            SUM(Revenue) AS revenue
        FROM sales
        WHERE InvoiceDate IS NOT NULL
        GROUP BY DATE(InvoiceDate)
        ORDER BY DATE(InvoiceDate) DESC
        LIMIT 30
    """)

    rows = cursor.fetchall()

    connection.close()

    if not rows:
        return {
            "forecast": [],
            "message": "No sales data available"
        }

    # Calculate average revenue
    revenues = [row[1] for row in rows if row[1] is not None]

    if not revenues:
        average_revenue = 0
    else:
        average_revenue = sum(revenues) / len(revenues)

    # Simple 7-day forecast
    forecast = []

    for day in range(1, 8):
        forecast.append({
            "day": f"Day {day}",
            "predicted_revenue": round(average_revenue, 2)
        })

    return {
        "average_daily_revenue": round(average_revenue, 2),
        "forecast_days": 7,
        "forecast": forecast
    }


# -----------------------------------------
# Run Information
# -----------------------------------------
# Start the server using:
#
# uvicorn main:app --reload
#

# -----------------------------------------
# Customer Segmentation
# -----------------------------------------
@app.get("/customers/segments")
def customer_segments():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            CustomerID,
            COUNT(DISTINCT InvoiceNo) AS total_orders,
            ROUND(SUM(Revenue), 2) AS total_spent
        FROM sales
        WHERE CustomerID IS NOT NULL
        GROUP BY CustomerID
        ORDER BY total_spent DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()

    connection.close()

    customers = []

    for row in rows:

        total_spent = row[2] or 0

        # Temporary rule-based segmentation
        if total_spent >= 50000:
            segment = "High Value"
        elif total_spent >= 20000:
            segment = "Medium Value"
        else:
            segment = "Low Value"

        customers.append({
            "customer_id": row[0],
            "total_orders": row[1],
            "total_spent": total_spent,
            "segment": segment
        })

    return customers

# -----------------------------------------
# Create Users Table
# -----------------------------------------
@app.on_event("startup")
def create_users_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# -----------------------------------------
# Register User
# -----------------------------------------
@app.post("/register")
def register_user(user: UserRegister):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            user.name,
            user.email,
            user.password,
            user.role
        ))

        connection.commit()

    except sqlite3.IntegrityError:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    connection.close()

    return {
        "message": "User registered successfully",
        "name": user.name,
        "role": user.role
    }


# -----------------------------------------
# Login User
# -----------------------------------------
@app.post("/login")
def login_user(user: UserLogin):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, email, role
        FROM users
        WHERE email = ?
        AND password = ?
    """, (
        user.email,
        user.password
    ))

    row = cursor.fetchone()

    connection.close()

    if not row:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "user": {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3]
        }
    }


# -----------------------------------------
# List All Users
# -----------------------------------------
@app.get("/admin/users")
def get_users():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, email, role
        FROM users
    """)

    rows = cursor.fetchall()

    connection.close()

    users = []

    for row in rows:
        users.append({
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3]
        })

    return users

    # -----------------------------------------
# AI Inventory Recommendations
# -----------------------------------------
@app.get("/inventory/recommendations")
def inventory_recommendations():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            Product_ID,
            Product_Name,
            Category,
            Stock_Quantity,
            Reorder_Level,
            Status
        FROM inventory
        LIMIT 20
    """)

    rows = cursor.fetchall()

    connection.close()

    recommendations = []

    for row in rows:

        product_id = row[0]
        product_name = row[1]
        category = row[2]
        stock_quantity = row[3]
        reorder_level = row[4]
        status = row[5]

        if stock_quantity <= reorder_level:

            recommendation = "Reorder immediately"

            priority = "High"

        elif stock_quantity <= reorder_level * 1.5:

            recommendation = "Monitor stock and prepare reorder"

            priority = "Medium"

        else:

            recommendation = "Stock level is sufficient"

            priority = "Low"

        recommendations.append({
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "stock_quantity": stock_quantity,
            "reorder_level": reorder_level,
            "status": status,
            "recommendation": recommendation,
            "priority": priority
        })

    return recommendations