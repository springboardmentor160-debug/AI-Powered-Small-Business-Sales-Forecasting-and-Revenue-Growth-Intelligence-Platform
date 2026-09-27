from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import pandas as pd
from pathlib import Path


# -----------------------------------------
# FASTAPI APPLICATION
# -----------------------------------------

app = FastAPI(
    title="MarketMind AI",
    description="AI-Powered Retail Sales Intelligence API",
    version="1.0.0"
)


# -----------------------------------------
# CORS CONFIGURATION
# -----------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------
# REQUEST MODELS
# -----------------------------------------

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str


class UserLogin(BaseModel):
    email: str
    password: str


# -----------------------------------------
# DATABASE CONNECTION
# -----------------------------------------

def get_connection():

    connection = sqlite3.connect(
        "database/marketmind.db"
    )

    connection.row_factory = sqlite3.Row

    return connection


# -----------------------------------------
# CREATE USERS TABLE
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
# HOME
# -----------------------------------------

@app.get("/")
def home():

    return {
        "message": "MarketMind AI Backend is running"
    }


# -----------------------------------------
# HEALTH CHECK
# -----------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# -----------------------------------------
# DASHBOARD SUMMARY
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

        "revenue": round(
            total_revenue or 0,
            2
        ),

        "sales": total_sales or 0,

        "customers": total_customers or 0,

        "products": total_products or 0

    }


# -----------------------------------------
# INVENTORY SUMMARY
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

        "total_inventory_products":
            total_products or 0,

        "total_stock":
            total_stock or 0,

        "low_stock_products":
            low_stock or 0

    }


# -----------------------------------------
# LOW STOCK PRODUCTS
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

            "product_id":
                row[0],

            "product_name":
                row[1],

            "category":
                row[2],

            "stock_quantity":
                row[3],

            "reorder_level":
                row[4],

            "status":
                row[5]

        })


    return products


# -----------------------------------------
# TOP SELLING PRODUCT
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

            "product":
                row[0],

            "quantity_sold":
                row[1]

        }


    return {

        "product":
            "No data",

        "quantity_sold":
            0

    }


# -----------------------------------------
# SALES TREND - LAST 30 DAYS
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

            "date":
                row[0],

            "revenue":
                round(row[1] or 0, 2)

        })


    return result


# -----------------------------------------
# REVENUE FORECAST - PROPHET
# -----------------------------------------

@app.get("/forecast/revenue")
def revenue_forecast():

    try:

        project_root = Path(__file__).resolve().parent.parent

        forecast_file = (
            project_root
            / "data"
            / "revenue_forecast.csv"
        )

        if not forecast_file.exists():

            raise HTTPException(
                status_code=404,
                detail="Revenue forecast not found. Run revenue_forecasting.py first."
            )

        forecast_df = pd.read_csv(
            forecast_file
        )

        forecast_df["ds"] = pd.to_datetime(
            forecast_df["ds"]
        )

        forecast_df = forecast_df.tail(30)

        forecast = []

        for _, row in forecast_df.iterrows():

            forecast.append({
                "date": row["ds"].strftime("%Y-%m-%d"),
                "predicted_revenue": round(
                    float(row["yhat"]),
                    2
                ),
                "lower_bound": round(
                    float(row["yhat_lower"]),
                    2
                ),
                "upper_bound": round(
                    float(row["yhat_upper"]),
                    2
                )
            })

        return {
            "forecast_days": len(forecast),
            "forecast": forecast
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load revenue forecast: {str(e)}"
        )

# -----------------------------------------
# CUSTOMER SEGMENTATION
# -----------------------------------------

@app.get("/customers/segments")
def customer_segments():

    try:

        # Locate the segmentation output file
        project_root = Path(__file__).resolve().parent.parent

        segmentation_file = (
            project_root
            / "data"
            / "customer_segmentation_output.csv"
        )

        # Check whether the file exists
        if not segmentation_file.exists():

            raise HTTPException(
                status_code=404,
                detail="Customer segmentation output not found. Run customer_segmentation.py first."
            )

        # Load ML segmentation output
        segmentation_df = pd.read_csv(
            segmentation_file
        )

        # Convert dataframe into API response
        customers = []

        for _, row in segmentation_df.iterrows():

            customers.append({

                "customer_id": row["CustomerID"],

                "purchase_frequency": row[
                    "purchase_frequency"
                ],

                "purchase_value": row[
                    "purchase_value"
                ],

                "customer_activity_days": row[
                    "customer_activity_days"
                ],

                "cluster": int(
                    row["cluster"]
                ),

                "cluster_hierarchical": int(
                    row["cluster_hierarchical"]
                ),

                "segment": row["segment"]

            })

        return customers

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load customer segmentation: {str(e)}"
        )

# -----------------------------------------
# AI INVENTORY RECOMMENDATIONS
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


        # Recommendation Logic

        if stock_quantity <= reorder_level:

            recommendation = (
                "Reorder immediately"
            )

            priority = "High"


        elif stock_quantity <= reorder_level * 1.5:

            recommendation = (
                "Monitor stock and prepare reorder"
            )

            priority = "Medium"


        else:

            recommendation = (
                "Stock level is sufficient"
            )

            priority = "Low"


        recommendations.append({

            "product_id":
                product_id,

            "product_name":
                product_name,

            "category":
                category,

            "stock_quantity":
                stock_quantity,

            "reorder_level":
                reorder_level,

            "status":
                status,

            "recommendation":
                recommendation,

            "priority":
                priority

        })


    return recommendations


# -----------------------------------------
# REGISTER USER
# -----------------------------------------

@app.post("/register")
def register_user(user: UserRegister):

    connection = get_connection()

    cursor = connection.cursor()


    try:

        cursor.execute("""

            INSERT INTO users (

                name,

                email,

                password,

                role

            )

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

        "message":
            "User registered successfully",

        "name":
            user.name,

        "role":
            user.role

    }


# -----------------------------------------
# LOGIN USER
# -----------------------------------------

@app.post("/login")
def login_user(user: UserLogin):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        SELECT

            id,

            name,

            email,

            role

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

        "message":
            "Login successful",

        "user": {

            "id":
                row[0],

            "name":
                row[1],

            "email":
                row[2],

            "role":
                row[3]

        }

    }


# -----------------------------------------
# GET ALL USERS
# ADMIN ENDPOINT
# -----------------------------------------

@app.get("/admin/users")
def get_users():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""

        SELECT

            id,

            name,

            email,

            role

        FROM users

    """)


    rows = cursor.fetchall()

    connection.close()


    users = []


    for row in rows:

        users.append({

            "id":
                row[0],

            "name":
                row[1],

            "email":
                row[2],

            "role":
                row[3]

        })


    return users


# -----------------------------------------
# RUN APPLICATION
# -----------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "main:app",

        host="127.0.0.1",

        port=8000,

        reload=True

    )