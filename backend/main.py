from pathlib import Path
import sqlite3

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "marketmind.db"
DATA_DIR = PROJECT_ROOT / "data"

FORECAST_FILE = DATA_DIR / "revenue_forecast.csv"
SEGMENTATION_FILE = DATA_DIR / "customer_segmentation_output.csv"
COLLABORATIVE_FILE = DATA_DIR / "product_recommendations.csv"
ASSOCIATION_FILE = DATA_DIR / "association_recommendations.csv"


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="MarketMind AI",
    description="AI-Powered Retail Sales Intelligence API",
    version="1.1.0",
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str


class UserLogin(BaseModel):
    email: str
    password: str


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    if not DATABASE_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Database file not found: {DATABASE_PATH}",
        )

    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    return connection


# --------------------------------------------------
# STARTUP
# --------------------------------------------------

@app.on_event("startup")
def create_users_table():
    connection = get_connection()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


# --------------------------------------------------
# HOME AND HEALTH
# --------------------------------------------------

@app.get("/")
def home():
    return {"message": "MarketMind AI Backend is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# --------------------------------------------------
# DASHBOARD SUMMARY
# --------------------------------------------------

@app.get("/summary")
def summary():
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT SUM(Revenue) FROM sales")
        total_revenue = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT InvoiceNo) FROM sales")
        total_sales = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load dashboard summary: {exc}",
        ) from exc
    finally:
        connection.close()

    return {
        "revenue": round(float(total_revenue or 0), 2),
        "sales": int(total_sales or 0),
        "customers": int(total_customers or 0),
        "products": int(total_products or 0),
    }


# --------------------------------------------------
# INVENTORY SUMMARY
# --------------------------------------------------

@app.get("/inventory/summary")
def inventory_summary():
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM inventory")
        total_products = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(Stock_Quantity) FROM inventory")
        total_stock = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM inventory
            WHERE Stock_Quantity <= Reorder_Level
            """
        )
        low_stock = cursor.fetchone()[0]
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load inventory summary: {exc}",
        ) from exc
    finally:
        connection.close()

    return {
        "total_inventory_products": int(total_products or 0),
        "total_stock": float(total_stock or 0),
        "low_stock_products": int(low_stock or 0),
    }


# --------------------------------------------------
# LOW-STOCK PRODUCTS
# --------------------------------------------------

@app.get("/inventory/low-stock")
def low_stock_products():
    connection = get_connection()
    try:
        rows = connection.execute(
            """
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
            """
        ).fetchall()
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load low-stock products: {exc}",
        ) from exc
    finally:
        connection.close()

    return [
        {
            "product_id": row["Product_ID"],
            "product_name": row["Product_Name"],
            "category": row["Category"],
            "stock_quantity": row["Stock_Quantity"],
            "reorder_level": row["Reorder_Level"],
            "status": row["Status"],
        }
        for row in rows
    ]


# --------------------------------------------------
# TOP-SELLING PRODUCT
# --------------------------------------------------

@app.get("/sales/top-product")
def top_product():
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT Description, SUM(Quantity) AS total_quantity
            FROM sales
            GROUP BY Description
            ORDER BY total_quantity DESC
            LIMIT 1
            """
        ).fetchone()
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load top product: {exc}",
        ) from exc
    finally:
        connection.close()

    if row:
        return {
            "product": row["Description"],
            "quantity_sold": row["total_quantity"],
        }

    return {"product": "No data", "quantity_sold": 0}


# --------------------------------------------------
# SALES TREND
# --------------------------------------------------

@app.get("/sales/trend")
def sales_trend():
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT DATE(InvoiceDate) AS date, SUM(Revenue) AS revenue
            FROM sales
            WHERE InvoiceDate IS NOT NULL
            GROUP BY DATE(InvoiceDate)
            ORDER BY DATE(InvoiceDate) DESC
            LIMIT 30
            """
        ).fetchall()
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load sales trend: {exc}",
        ) from exc
    finally:
        connection.close()

    rows = list(reversed(rows))
    return [
        {
            "date": row["date"],
            "revenue": round(float(row["revenue"] or 0), 2),
        }
        for row in rows
    ]


# --------------------------------------------------
# REVENUE FORECAST
# --------------------------------------------------

@app.get("/forecast/revenue")
def revenue_forecast():
    if not FORECAST_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Revenue forecast file not found. "
                "Run revenue_forecasting.py first."
            ),
        )

    try:
        forecast_df = pd.read_csv(FORECAST_FILE)
        required_columns = ["ds", "yhat", "yhat_lower", "yhat_upper"]
        missing = [
            column for column in required_columns
            if column not in forecast_df.columns
        ]
        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Forecast file is missing columns: {missing}",
            )

        forecast_df["ds"] = pd.to_datetime(
            forecast_df["ds"], errors="coerce"
        )
        forecast_df = forecast_df.dropna(subset=["ds"]).tail(30)

        forecast = []
        for _, row in forecast_df.iterrows():
            forecast.append(
                {
                    "date": row["ds"].strftime("%Y-%m-%d"),
                    "predicted_revenue": round(float(row["yhat"]), 2),
                    "lower_bound": round(float(row["yhat_lower"]), 2),
                    "upper_bound": round(float(row["yhat_upper"]), 2),
                }
            )

        return {"forecast_days": len(forecast), "forecast": forecast}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load revenue forecast: {exc}",
        ) from exc


# --------------------------------------------------
# CUSTOMER SEGMENTATION
# --------------------------------------------------

@app.get("/customers/segments")
def customer_segments():
    if not SEGMENTATION_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Customer segmentation output not found. "
                "Run customer_segmentation.py first."
            ),
        )

    try:
        df = pd.read_csv(SEGMENTATION_FILE)
        required_columns = [
            "CustomerID",
            "purchase_frequency",
            "purchase_value",
            "customer_activity_days",
            "cluster",
            "cluster_hierarchical",
            "segment",
        ]
        missing = [
            column for column in required_columns
            if column not in df.columns
        ]
        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Segmentation file is missing columns: {missing}",
            )

        df = df.where(pd.notna(df), None)
        customers = []

        for _, row in df.iterrows():
            customers.append(
                {
                    "customer_id": row["CustomerID"],
                    "purchase_frequency": row["purchase_frequency"],
                    "purchase_value": row["purchase_value"],
                    "customer_activity_days": row["customer_activity_days"],
                    "cluster": int(row["cluster"]),
                    "cluster_hierarchical": int(
                        row["cluster_hierarchical"]
                    ),
                    "segment": row["segment"],
                }
            )

        return customers

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load customer segmentation: {exc}",
        ) from exc


# --------------------------------------------------
# INVENTORY RECOMMENDATIONS
# --------------------------------------------------

@app.get("/inventory/recommendations")
def inventory_recommendations():
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT
                Product_ID,
                Product_Name,
                Category,
                Stock_Quantity,
                Reorder_Level,
                Status
            FROM inventory
            LIMIT 20
            """
        ).fetchall()
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load inventory recommendations: {exc}",
        ) from exc
    finally:
        connection.close()

    recommendations = []

    for row in rows:
        stock_quantity = float(row["Stock_Quantity"] or 0)
        reorder_level = float(row["Reorder_Level"] or 0)

        if stock_quantity <= reorder_level:
            recommendation = "Reorder immediately"
            priority = "High"
        elif stock_quantity <= reorder_level * 1.5:
            recommendation = "Monitor stock and prepare reorder"
            priority = "Medium"
        else:
            recommendation = "Stock level is sufficient"
            priority = "Low"

        recommendations.append(
            {
                "product_id": row["Product_ID"],
                "product_name": row["Product_Name"],
                "category": row["Category"],
                "stock_quantity": row["Stock_Quantity"],
                "reorder_level": row["Reorder_Level"],
                "status": row["Status"],
                "recommendation": recommendation,
                "priority": priority,
            }
        )

    return recommendations


# --------------------------------------------------
# MILESTONE 3: RECOMMENDATION FILE HELPERS
# --------------------------------------------------

def load_collaborative_recommendations():
    if not COLLABORATIVE_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Collaborative recommendation file not found. "
                "Run product_recommendations.py first."
            ),
        )

    try:
        df = pd.read_csv(COLLABORATIVE_FILE)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read collaborative recommendations: {exc}",
        ) from exc

    required = {
        "CustomerID",
        "StockCode",
        "Product",
        "RecommendationScore",
    }
    missing = required.difference(df.columns)
    if missing:
        raise HTTPException(
            status_code=500,
            detail=(
                "Collaborative recommendation file is missing columns: "
                f"{sorted(missing)}"
            ),
        )

    df["CustomerID"] = df["CustomerID"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str)
    df["RecommendationScore"] = pd.to_numeric(
        df["RecommendationScore"], errors="coerce"
    )
    df = df.dropna(
        subset=["CustomerID", "StockCode", "Product", "RecommendationScore"]
    )
    return df


def load_association_recommendations():
    if not ASSOCIATION_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Association recommendation file not found. "
                "Run association_rules.py first."
            ),
        )

    try:
        df = pd.read_csv(ASSOCIATION_FILE)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read association recommendations: {exc}",
        ) from exc

    required = {
        "PurchasedStockCode",
        "PurchasedProduct",
        "RecommendedStockCode",
        "RecommendedProduct",
        "support",
        "confidence",
        "lift",
    }
    missing = required.difference(df.columns)
    if missing:
        raise HTTPException(
            status_code=500,
            detail=(
                "Association recommendation file is missing columns: "
                f"{sorted(missing)}"
            ),
        )

    for column in ["PurchasedStockCode", "RecommendedStockCode"]:
        df[column] = df[column].astype(str)

    for column in ["support", "confidence", "lift"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(
        subset=[
            "PurchasedStockCode",
            "PurchasedProduct",
            "RecommendedStockCode",
            "RecommendedProduct",
            "support",
            "confidence",
            "lift",
        ]
    )
    return df


# --------------------------------------------------
# MILESTONE 3: PERSONALIZED RECOMMENDATIONS
# --------------------------------------------------

@app.get("/recommendations/customer/{customer_id}")
def personalized_recommendations(customer_id: str, limit: int = 5):
    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 20.",
        )

    df = load_collaborative_recommendations()
    customer_rows = df[df["CustomerID"] == str(customer_id)].copy()

    if customer_rows.empty:
        return {
            "customer_id": str(customer_id),
            "count": 0,
            "recommendations": [],
            "message": "No recommendations found for this customer.",
        }

    customer_rows = customer_rows.sort_values(
        "RecommendationScore", ascending=False
    ).head(limit)

    recommendations = []
    for _, row in customer_rows.iterrows():
        recommendations.append(
            {
                "stock_code": row["StockCode"],
                "product": row["Product"],
                "recommendation_score": round(
                    float(row["RecommendationScore"]), 4
                ),
                "method": "Collaborative Filtering",
            }
        )

    return {
        "customer_id": str(customer_id),
        "count": len(recommendations),
        "recommendations": recommendations,
    }


# --------------------------------------------------
# MILESTONE 3: FREQUENTLY BOUGHT TOGETHER
# --------------------------------------------------

@app.get("/recommendations/product/{stock_code}")
def frequently_bought_together(
    stock_code: str,
    limit: int = 5,
    min_confidence: float = 0.20,
    min_support: float = 0.005,
):
    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 20.",
        )

    if not 0 <= min_confidence <= 1:
        raise HTTPException(
            status_code=400,
            detail="min_confidence must be between 0 and 1.",
        )

    if not 0 <= min_support <= 1:
        raise HTTPException(
            status_code=400,
            detail="min_support must be between 0 and 1.",
        )

    df = load_association_recommendations()
    rows = df[
        (df["PurchasedStockCode"] == str(stock_code))
        & (df["confidence"] >= min_confidence)
        & (df["support"] >= min_support)
    ].copy()

    if rows.empty:
        return {
            "stock_code": str(stock_code),
            "count": 0,
            "recommendations": [],
            "message": (
                "No matching product association found with the "
                "requested support and confidence thresholds."
            ),
        }

    rows = rows.sort_values(
        ["lift", "confidence", "support"],
        ascending=False,
    ).head(limit)

    recommendations = []
    for _, row in rows.iterrows():
        recommendations.append(
            {
                "purchased_product": row["PurchasedProduct"],
                "recommended_stock_code": row["RecommendedStockCode"],
                "recommended_product": row["RecommendedProduct"],
                "support": round(float(row["support"]), 6),
                "confidence": round(float(row["confidence"]), 6),
                "lift": round(float(row["lift"]), 4),
                "method": "Association Rules",
            }
        )

    return {
        "stock_code": str(stock_code),
        "count": len(recommendations),
        "recommendations": recommendations,
    }


# --------------------------------------------------
# REGISTER USER
# --------------------------------------------------

@app.post("/register")
def register_user(user: UserRegister):
    connection = get_connection()
    try:
        connection.execute(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            (user.name, user.email, user.password, user.role),
        )
        connection.commit()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        ) from exc
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to register user: {exc}",
        ) from exc
    finally:
        connection.close()

    return {
        "message": "User registered successfully",
        "name": user.name,
        "role": user.role,
    }


# --------------------------------------------------
# LOGIN USER
# --------------------------------------------------

@app.post("/login")
def login_user(user: UserLogin):
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT id, name, email, role
            FROM users
            WHERE email = ? AND password = ?
            """,
            (user.email, user.password),
        ).fetchone()
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to log in: {exc}",
        ) from exc
    finally:
        connection.close()

    if not row:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return {
        "message": "Login successful",
        "user": {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "role": row["role"],
        },
    }


# --------------------------------------------------
# GET ALL USERS
# --------------------------------------------------

@app.get("/admin/users")
def get_users():
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT id, name, email, role FROM users"
        ).fetchall()
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load users: {exc}",
        ) from exc
    finally:
        connection.close()

    return [
        {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "role": row["role"],
        }
        for row in rows
    ]


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
