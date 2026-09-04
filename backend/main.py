import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

app = FastAPI(title="MarketMind AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/processed")

# Login Request Schema
class LoginRequest(BaseModel):
    email: str

@app.post("/api/login")
def login(request: LoginRequest):
    users_df = pd.read_csv(os.path.join(DATA_DIR, "users.csv"))
    user = users_df[users_df["email"].str.lower() == request.email.lower()]
    
    if user.empty:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_record = user.iloc[0].to_dict()
    return {
        "id": int(user_record["id"]),
        "name": user_record["name"],
        "email": user_record["email"],
        "role": user_record["role"]
    }

@app.get("/api/dashboard/{role}")
def get_role_dashboard(role: str):
    sales_df = pd.read_csv(os.path.join(DATA_DIR, "sales.csv"))
    inventory_df = pd.read_csv(os.path.join(DATA_DIR, "inventory.csv"))
    products_df = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
    customers_df = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
    users_df = pd.read_csv(os.path.join(DATA_DIR, "users.csv"))

    merged_sales = sales_df.merge(products_df, left_on="product_id", right_on="product_id")

    # Common metrics
    total_revenue = round(float(sales_df["sales_amount"].sum()), 2)
    low_stock = int((inventory_df["stock_level"] <= inventory_df["reorder_point"]).sum())
    top_product = merged_sales.groupby("name")["sales_amount"].sum().idxmax()
    segment_counts = customers_df["segment"].value_counts().to_dict()

    # Role-specific data payloads
    if role == "Business Owner":
        return {
            "role": role,
            "cards": [
                {"label": "Total Business Revenue", "value": f"${total_revenue:,.2f}"},
                {"label": "Total Customer Accounts", "value": len(customers_df)},
                {"label": "Total SKUs Managed", "value": len(products_df)}
            ],
            "sections": {
                "customer_segments": segment_counts,
                "strategy_note": "Focus on high-margin Corporate accounts across East and West regions."
            }
        }

    elif role == "Store Manager":
        return {
            "role": role,
            "cards": [
                {"label": "Store Revenue", "value": f"${total_revenue:,.2f}"},
                {"label": "Low Stock Alerts", "value": f"{low_stock} Items", "alert": low_stock > 0},
                {"label": "Top Store Product", "value": top_product}
            ],
            "sections": {
                "inventory_action": f"Reorder purchase orders needed immediately for {low_stock} items below safe buffer."
            }
        }

    elif role == "Sales Executive":
        top_5_products = merged_sales.groupby("name")["sales_amount"].sum().nlargest(5).to_dict()
        return {
            "role": role,
            "cards": [
                {"label": "Total Orders Placed", "value": len(sales_df)},
                {"label": "Top Selling Category", "value": products_df["category"].mode()[0]},
                {"label": "Active Customers", "value": len(customers_df)}
            ],
            "sections": {
                "top_products": top_5_products
            }
        }

    elif role == "Administrator":
        return {
            "role": role,
            "cards": [
                {"label": "Registered Users", "value": len(users_df)},
                {"label": "System Status", "value": "Healthy (API Online)"},
                {"label": "Total Data Records", "value": len(sales_df) + len(customers_df) + len(products_df)}
            ],
            "sections": {
                "user_list": users_df[["id", "name", "email", "role"]].to_dict(orient="records")
            }
        }

    raise HTTPException(status_code=400, detail="Invalid role specified")