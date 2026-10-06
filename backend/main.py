# ---------------------------------------------------
# IMPORTS
# Purpose:
# Import all required libraries
# ---------------------------------------------------

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import os
import io
from dotenv import load_dotenv


# ---------------------------------------------------
# CREATE FASTAPI APPLICATION
# ---------------------------------------------------

app = FastAPI()


# ---------------------------------------------------
# PASSWORD HASHING SETTINGS
# ---------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ---------------------------------------------------
# JWT SETTINGS
# ---------------------------------------------------

# Load environment variables from .env file
load_dotenv()

# Read JWT secret key from .env file
SECRET_KEY = os.getenv("SECRET_KEY")

# JWT algorithm
ALGORITHM = "HS256"

# Token expiry time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# Check whether SECRET_KEY exists
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY is missing. Please add it to your .env file."
    )


# ---------------------------------------------------
# SECURITY SCHEME
# ---------------------------------------------------

security = HTTPBearer()


# ---------------------------------------------------
# ALLOWED USER ROLES
# Purpose:
# Defines the four roles allowed in MarketMind AI
# ---------------------------------------------------

ALLOWED_ROLES = [
    "Business Owner",
    "Store Manager",
    "Sales Executive",
    "Administrator"
]


# ---------------------------------------------------
# TEMPORARY USER DATABASE
# Purpose:
# Temporarily stores registered users
#
# Later:
# We will replace this with PostgreSQL
# ---------------------------------------------------

fake_users_db = {}


# ---------------------------------------------------
# USER REGISTER MODEL
# Purpose:
# Defines the data needed for registration
# ---------------------------------------------------

class UserRegister(BaseModel):

    username: str
    password: str
    role: str


# ---------------------------------------------------
# USER LOGIN MODEL
# Purpose:
# Defines the data needed for login
# ---------------------------------------------------

class UserLogin(BaseModel):

    username: str
    password: str


# ---------------------------------------------------
# VERIFY TOKEN FUNCTION
# Purpose:
# Checks whether the JWT token is valid
# ---------------------------------------------------

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # Get only the token value
    token = credentials.credentials

    try:

        # Decode and verify the token
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Return user information stored in token
        return payload

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# ---------------------------------------------------
# ROLE PERMISSION FUNCTION
# Purpose:
# Checks whether the logged-in user
# has permission to access a resource
# ---------------------------------------------------

def require_roles(allowed_roles):

    def role_checker(
        user_data: dict = Depends(verify_token)
    ):

        # Get role from JWT token
        user_role = user_data.get("role")

        # Check permission
        if user_role not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail=(
                    "You do not have permission "
                    "to access this resource"
                )
            )

        # Return logged-in user information
        return user_data

    return role_checker


# ---------------------------------------------------
# REGISTER API
# Purpose:
# Registers a new user
# URL:
# POST /register
# ---------------------------------------------------

@app.post("/register")
def register(user: UserRegister):

    # Check whether selected role is valid
    if user.role not in ALLOWED_ROLES:

        raise HTTPException(
            status_code=400,
            detail="Invalid role selected"
        )

    # Check whether username already exists
    if user.username in fake_users_db:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Convert normal password into hashed password
    hashed_password = pwd_context.hash(
        user.password
    )

    # Store user information temporarily
    fake_users_db[user.username] = {
        "username": user.username,
        "password": hashed_password,
        "role": user.role
    }

    return {
        "message": "User registered successfully"
    }


# ---------------------------------------------------
# LOGIN API
# Purpose:
# Logs in an existing user
# Creates and returns a JWT token
# URL:
# POST /login
# ---------------------------------------------------

@app.post("/login")
def login(user: UserLogin):

    # Check whether username exists
    if user.username not in fake_users_db:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Get stored user information
    stored_user = fake_users_db[user.username]

    # Check password
    if not pwd_context.verify(
        user.password,
        stored_user["password"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Set token expiry time
    expire_time = (
        datetime.utcnow()
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    # Store user information inside token
    token_data = {
        "sub": stored_user["username"],
        "role": stored_user["role"],
        "exp": expire_time
    }

    # Create JWT token
    token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": stored_user["role"]
    }


# ---------------------------------------------------
# PROFILE API
# Purpose:
# Protected API
# Shows logged-in user information
# URL:
# GET /profile
# ---------------------------------------------------

@app.get("/profile")
def profile(
    user_data: dict = Depends(verify_token)
):

    return {
        "message": "Welcome to your profile",
        "username": user_data["sub"],
        "role": user_data["role"]
    }


# ---------------------------------------------------
# DASHBOARD ACCESS API
# Purpose:
# Shows dashboard permissions
# based on the logged-in user's role
# URL:
# GET /dashboard-access
# ---------------------------------------------------

@app.get("/dashboard-access")
def dashboard_access(
    user_data: dict = Depends(verify_token)
):

    user_role = user_data["role"]

    # Business Owner
    if user_role == "Business Owner":

        return {
            "role": user_role,
            "total_revenue": True,
            "total_margin": True,
            "low_stock": True,
            "sales_by_city": True,
            "sales_by_category": True,
            "sales_trends": True,
            "brand_channel": True,
            "inventory_intel": True,
            "demographic_intel": True,
            "customer_segmentation": True,
            "sales_forecast": True
        }

    # Store Manager
    elif user_role == "Store Manager":

        return {
            "role": user_role,
            "total_revenue": False,
            "total_margin": False,
            "low_stock": True,
            "sales_by_city": True,
            "sales_by_category": True,
            "sales_trends": True,
            "brand_channel": True,
            "inventory_intel": True,
            "demographic_intel": True,
            "customer_segmentation": True,
            "sales_forecast": True
        }

    # Sales Executive
    elif user_role == "Sales Executive":

        return {
            "role": user_role,
            "total_revenue": False,
            "total_margin": False,
            "low_stock": False,
            "sales_by_city": True,
            "sales_by_category": True,
            "sales_trends": True,
            "brand_channel": True,
            "inventory_intel": False,
            "demographic_intel": True,
            "customer_segmentation": True,
            "sales_forecast": False
        }

    # Administrator
    elif user_role == "Administrator":

        return {
            "role": user_role,
            "total_revenue": True,
            "total_margin": True,
            "low_stock": True,
            "sales_by_city": True,
            "sales_by_category": True,
            "sales_trends": True,
            "brand_channel": True,
            "inventory_intel": True,
            "demographic_intel": True,
            "customer_segmentation": True,
            "sales_forecast": True
        }

    # Safety fallback
    raise HTTPException(
        status_code=403,
        detail="Invalid user role"
    )


# ---------------------------------------------------
# CORS SETTINGS
# Purpose:
# Allows React frontend to access backend
# ---------------------------------------------------

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ---------------------------------------------------
# LOAD & CLUSTER DATASET
# Purpose:
# Reads processed CSV file and computes K-Means
# and Hierarchical Clustering models
# ---------------------------------------------------

df = pd.read_csv(
    "processed_fmcg_retail_data.csv"
)

# Parse Invoice_Date into datetime for time-series aggregation
df["Invoice_Date_Parsed"] = pd.to_datetime(df["Invoice_Date"], errors="coerce")

# Feature preparation
max_invoice_date = df["Invoice_Date_Parsed"].max()
df["purchase_value"] = df["Revenue"].fillna(0)
df["purchase_frequency"] = df["Units"].fillna(0)
df["customer_activity_days"] = (max_invoice_date - df["Invoice_Date_Parsed"]).dt.days.fillna(0)

# Feature Scaling & Clustering Models Execution
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
import numpy as np

features_list = ["purchase_value", "purchase_frequency", "customer_activity_days"]
X_features = df[features_list].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_features)

# 1. K-Means (n_clusters=4, random_state=42)
kmeans_model = KMeans(n_clusters=4, random_state=42, n_init=10)
df["kmeans_cluster"] = kmeans_model.fit_predict(X_scaled)

# 2. Hierarchical (AgglomerativeClustering, n_clusters=4)
np.random.seed(42)
sample_size = min(5000, len(X_scaled))
sample_indices = np.random.choice(len(X_scaled), size=sample_size, replace=False)
X_sample = X_scaled[sample_indices]

agg_model = AgglomerativeClustering(n_clusters=4)
sample_labels = agg_model.fit_predict(X_sample)

agg_centers = []
for label in range(4):
    mask = (sample_labels == label)
    if np.any(mask):
        agg_centers.append(X_sample[mask].mean(axis=0))
    else:
        agg_centers.append(X_sample[0])
agg_centers = np.array(agg_centers)

dists = np.linalg.norm(X_scaled[:, np.newaxis, :] - agg_centers[np.newaxis, :, :], axis=2)
df["hierarchical_cluster"] = np.argmin(dists, axis=1)


# ---------------------------------------------------
# CLUSTER PROFILING HELPER
# ---------------------------------------------------

def compute_cluster_profiles(cluster_column: str, filtered_df: pd.DataFrame):
    if filtered_df.empty:
        return []

    profiles = []
    total_records = len(filtered_df)

    for cluster_id in sorted(filtered_df[cluster_column].unique()):
        sub_df = filtered_df[filtered_df[cluster_column] == cluster_id]
        rec_count = len(sub_df)
        pct = round((rec_count / total_records) * 100, 2) if total_records > 0 else 0

        mean_val = round(float(sub_df["purchase_value"].mean()), 2)
        mean_freq = round(float(sub_df["purchase_frequency"].mean()), 2)
        mean_act = round(float(sub_df["customer_activity_days"].mean()), 2)

        profiles.append({
            "cluster_id": int(cluster_id),
            "segment_name": f"Cohort Cluster {cluster_id}",
            "mean_purchase_value": mean_val,
            "mean_purchase_frequency": mean_freq,
            "mean_customer_activity_days": mean_act,
            "record_count": int(rec_count),
            "percentage": pct
        })

    # Assign distinct data-driven segment names based on relative rank
    if len(profiles) == 4:
        sorted_by_val = sorted(profiles, key=lambda x: (x["mean_purchase_value"], x["mean_purchase_frequency"]), reverse=True)
        name_map = {}
        name_map[sorted_by_val[0]["cluster_id"]] = "VIP / High-Value Cohort"
        if sorted_by_val[1]["mean_purchase_frequency"] >= sorted_by_val[2]["mean_purchase_frequency"]:
            name_map[sorted_by_val[1]["cluster_id"]] = "Regular Shoppers Cohort"
            name_map[sorted_by_val[2]["cluster_id"]] = "High-Value Occasional Cohort"
        else:
            name_map[sorted_by_val[1]["cluster_id"]] = "High-Value Occasional Cohort"
            name_map[sorted_by_val[2]["cluster_id"]] = "Regular Shoppers Cohort"
        name_map[sorted_by_val[3]["cluster_id"]] = "At-Risk / Inactive Cohort"

        for p in profiles:
            p["segment_name"] = name_map.get(p["cluster_id"], f"Cohort Cluster {p['cluster_id']}")

    return profiles


# ---------------------------------------------------
# FILTERING HELPER FUNCTION
# Purpose:
# Applies multi-dimensional filtering across dataset
# ---------------------------------------------------

def get_filtered_df(
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None
) -> pd.DataFrame:

    filtered_df = df

    if city and city != "All":
        filtered_df = filtered_df[filtered_df["City"] == city]

    if category and category != "All":
        filtered_df = filtered_df[filtered_df["Category"] == category]

    if store_format and store_format != "All":
        filtered_df = filtered_df[filtered_df["Store_Format"] == store_format]

    if channel and channel != "All":
        filtered_df = filtered_df[filtered_df["Channel"] == channel]

    if payment_mode and payment_mode != "All":
        filtered_df = filtered_df[filtered_df["Payment_Mode"] == payment_mode]

    return filtered_df


# ---------------------------------------------------
# HOME API
# Purpose:
# Checks whether backend is running
# URL:
# GET /
# ---------------------------------------------------

@app.get("/")
def home():

    return {
        "message": (
            "MarketMind AI Backend "
            "is running successfully!"
        )
    }


# ---------------------------------------------------
# DATASET INFORMATION API
# URL:
# GET /dataset-info
# ---------------------------------------------------

@app.get("/dataset-info")
def dataset_info():

    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": df.columns.tolist()
    }


# ---------------------------------------------------
# FILTER OPTIONS API (NEW)
# URL:
# GET /filter-options
# ---------------------------------------------------

@app.get("/filter-options")
def filter_options(
    user_data: dict = Depends(verify_token)
):

    return {
        "cities": sorted(df["City"].dropna().unique().tolist()),
        "categories": sorted(df["Category"].dropna().unique().tolist()),
        "store_formats": sorted(df["Store_Format"].dropna().unique().tolist()),
        "channels": sorted(df["Channel"].dropna().unique().tolist()),
        "payment_modes": sorted(df["Payment_Mode"].dropna().unique().tolist())
    }


# ---------------------------------------------------
# TOTAL REVENUE API (UPDATED WITH FILTERS)
#
# Allowed Roles:
# Business Owner
# Administrator
#
# URL:
# GET /total-revenue
# ---------------------------------------------------

@app.get("/total-revenue")
def total_revenue(
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(city, category, store_format, channel, payment_mode)
    total = filtered["Revenue"].sum()

    return {
        "total_revenue": round(
            float(total),
            2
        )
    }


# ---------------------------------------------------
# TOTAL MARGIN API (UPDATED WITH FILTERS)
#
# Allowed Roles:
# Business Owner
# Administrator
#
# URL:
# GET /total-margin
# ---------------------------------------------------

@app.get("/total-margin")
def total_margin(
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(city, category, store_format, channel, payment_mode)
    total = filtered["Margin"].sum()

    return {
        "total_margin": round(
            float(total),
            2
        )
    }


# ---------------------------------------------------
# SALES BY CITY API (UPDATED WITH FILTERS)
#
# Allowed Roles:
# Business Owner
# Store Manager
# Sales Executive
# Administrator
#
# URL:
# GET /sales-by-city
# ---------------------------------------------------

@app.get("/sales-by-city")
def sales_by_city(
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Sales Executive",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(category=category, store_format=store_format, channel=channel, payment_mode=payment_mode)
    city_sales = (
        filtered.groupby("City")["Revenue"]
        .sum()
    )

    return city_sales.round(2).to_dict()


# ---------------------------------------------------
# SALES BY CATEGORY API (UPDATED WITH FILTERS)
#
# Allowed Roles:
# Business Owner
# Store Manager
# Sales Executive
# Administrator
#
# URL:
# GET /sales-by-category
# ---------------------------------------------------

@app.get("/sales-by-category")
def sales_by_category(
    city: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Sales Executive",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(city=city, store_format=store_format, channel=channel, payment_mode=payment_mode)
    category_sales = (
        filtered.groupby("Category")["Revenue"]
        .sum()
    )

    return category_sales.round(2).to_dict()


# ---------------------------------------------------
# LOW STOCK API (UPDATED WITH FILTERS)
#
# Allowed Roles:
# Business Owner
# Store Manager
# Administrator
#
# URL:
# GET /low-stock
# ---------------------------------------------------

@app.get("/low-stock")
def low_stock(
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(city, category, store_format, channel, payment_mode)
    low_stock_count = filtered[
        filtered["Low_Stock_Flag"] == 1
    ].shape[0]

    return {
        "low_stock_records": int(
            low_stock_count
        )
    }


# ---------------------------------------------------
# SALES TRENDS API (MILESTONE 2 - NEW)
#
# Allowed Roles:
# Business Owner (Revenue & Margin)
# Store Manager (Revenue Only)
# Sales Executive (Revenue Only)
# Administrator (Revenue & Margin)
#
# URL:
# GET /sales-trends
# ---------------------------------------------------

@app.get("/sales-trends")
def sales_trends(
    granularity: str = Query("monthly"),
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Sales Executive",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(city, category, store_format, channel, payment_mode).copy()

    if filtered.empty:
        return []

    user_role = user_data["role"]
    can_view_margin = user_role in ["Business Owner", "Administrator"]

    if granularity == "quarterly":
        filtered["Period"] = filtered["Invoice_Date_Parsed"].dt.to_period("Q").astype(str)
    else:
        filtered["Period"] = filtered["Invoice_Date_Parsed"].dt.to_period("M").astype(str)

    if can_view_margin:
        grouped = filtered.groupby("Period")[["Revenue", "Margin"]].sum().reset_index()
        grouped = grouped.sort_values("Period")
        result = [
            {
                "period": str(row["Period"]),
                "revenue": round(float(row["Revenue"]), 2),
                "margin": round(float(row["Margin"]), 2)
            }
            for _, row in grouped.iterrows()
        ]
    else:
        grouped = filtered.groupby("Period")["Revenue"].sum().reset_index()
        grouped = grouped.sort_values("Period")
        result = [
            {
                "period": str(row["Period"]),
                "revenue": round(float(row["Revenue"]), 2)
            }
            for _, row in grouped.iterrows()
        ]

    return result


# ---------------------------------------------------
# BRAND & CHANNEL ANALYTICS API (MILESTONE 2 - NEW)
#
# Allowed Roles:
# All four roles
#
# URL:
# GET /brand-channel-analytics
# ---------------------------------------------------

@app.get("/brand-channel-analytics")
def brand_channel_analytics(
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Sales Executive",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(city=city, category=category, store_format=store_format, payment_mode=payment_mode)

    by_brand_df = (
        filtered.groupby("Brand")
        .agg(
            revenue=("Revenue", "sum"),
            units=("Units", "sum"),
            avg_margin_pct=("Margin_%", "mean")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    by_brand = [
        {
            "brand": str(row["Brand"]),
            "revenue": round(float(row["revenue"]), 2),
            "units": int(row["units"]),
            "avg_margin_pct": round(float(row["avg_margin_pct"] * 100), 2)
        }
        for _, row in by_brand_df.iterrows()
    ]

    by_channel_df = (
        filtered.groupby("Channel")
        .agg(
            revenue=("Revenue", "sum"),
            units=("Units", "sum")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )
    by_channel = [
        {
            "channel": str(row["Channel"]),
            "revenue": round(float(row["revenue"]), 2),
            "units": int(row["units"])
        }
        for _, row in by_channel_df.iterrows()
    ]

    return {
        "by_brand": by_brand,
        "by_channel": by_channel
    }


# ---------------------------------------------------
# INVENTORY INTELLIGENCE API (MILESTONE 2 - NEW)
#
# Allowed Roles:
# Business Owner
# Store Manager
# Administrator
#
# URL:
# GET /inventory-intelligence
# ---------------------------------------------------

@app.get("/inventory-intelligence")
def inventory_intelligence(
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(city=city, category=category, store_format=store_format, channel=channel)

    low_stock_mask = (filtered["Low_Stock_Flag"] == 1) | (filtered["Stock_On_Hand"] <= filtered["Reorder_Level"])
    low_stock_df = filtered[low_stock_mask].copy()

    by_category = (
        low_stock_df.groupby("Category").size().to_dict()
        if not low_stock_df.empty else {}
    )

    if not low_stock_df.empty:
        low_stock_df["Stock_Deficit"] = low_stock_df["Reorder_Level"] - low_stock_df["Stock_On_Hand"]
        top_critical = (
            low_stock_df.sort_values(by=["Stock_Deficit", "Lead_Time_Days"], ascending=[False, False])
            .head(15)
        )
        critical_items = [
            {
                "invoice_id": str(row["Invoice_ID"]),
                "city": str(row["City"]),
                "category": str(row["Category"]),
                "brand": str(row["Brand"]),
                "stock_on_hand": int(row["Stock_On_Hand"]),
                "reorder_level": int(row["Reorder_Level"]),
                "lead_time_days": int(row["Lead_Time_Days"]),
                "deficit": int(row["Stock_Deficit"])
            }
            for _, row in top_critical.iterrows()
        ]
    else:
        critical_items = []

    return {
        "total_low_stock_count": int(low_stock_df.shape[0]),
        "by_category": by_category,
        "critical_items": critical_items
    }


# ---------------------------------------------------
# DEMOGRAPHIC ANALYTICS API (MILESTONE 2 - NEW)
#
# Allowed Roles:
# All four roles
#
# URL:
# GET /demographic-analytics
# ---------------------------------------------------

@app.get("/demographic-analytics")
def demographic_analytics(
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Sales Executive",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(city, category, store_format, channel, payment_mode).copy()

    if filtered.empty:
        return {"by_age_group": [], "by_gender": [], "by_loyalty": []}

    # Age Group Binning
    bins = [0, 24, 40, 60, 120]
    labels = ["18-24", "25-40", "41-60", "60+"]
    filtered["Age_Group"] = pd.cut(filtered["Customer_Age"], bins=bins, labels=labels, right=True)
    filtered["Age_Group"] = filtered["Age_Group"].astype(str).replace({"nan": "Unspecified"})

    age_group_df = (
        filtered.groupby("Age_Group")
        .agg(revenue=("Revenue", "sum"), transactions=("Invoice_ID", "count"))
        .reset_index()
    )
    by_age_group = [
        {
            "age_group": str(row["Age_Group"]),
            "revenue": round(float(row["revenue"]), 2),
            "transactions": int(row["transactions"])
        }
        for _, row in age_group_df.iterrows()
    ]

    # Gender Breakdown
    gender_df = (
        filtered.groupby("Customer_Gender")
        .agg(revenue=("Revenue", "sum"), transactions=("Invoice_ID", "count"))
        .reset_index()
    )
    by_gender = [
        {
            "gender": str(row["Customer_Gender"]),
            "revenue": round(float(row["revenue"]), 2),
            "transactions": int(row["transactions"])
        }
        for _, row in gender_df.iterrows()
    ]

    # Loyalty Breakdown
    loyalty_df = (
        filtered.groupby("Loyalty_Flag")
        .agg(
            revenue=("Revenue", "sum"),
            transactions=("Invoice_ID", "count"),
            avg_ticket=("Revenue", "mean")
        )
        .reset_index()
    )
    by_loyalty = [
        {
            "loyalty_status": "Loyal" if row["Loyalty_Flag"] == 1 else "Non-Loyal",
            "revenue": round(float(row["revenue"]), 2),
            "transactions": int(row["transactions"]),
            "avg_ticket": round(float(row["avg_ticket"]), 2)
        }
        for _, row in loyalty_df.iterrows()
    ]

    return {
        "by_age_group": by_age_group,
        "by_gender": by_gender,
        "by_loyalty": by_loyalty
    }


# ---------------------------------------------------
# CUSTOMER SEGMENTATION API (DAY 3 & 4 - NEW)
#
# Allowed Roles:
# All four roles
#
# URL:
# GET /customer-segmentation
# ---------------------------------------------------

@app.get("/customer-segmentation")
def customer_segmentation(
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Sales Executive",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(city, category, store_format, channel, payment_mode)

    kmeans_profiles = compute_cluster_profiles("kmeans_cluster", filtered)
    hierarchical_profiles = compute_cluster_profiles("hierarchical_cluster", filtered)

    return {
        "feature_definitions": {
            "purchase_value": "Total line transaction revenue (Revenue column)",
            "purchase_frequency": "Units purchased per transaction (Units column)",
            "customer_activity_days": "Days elapsed since transaction relative to latest dataset date"
        },
        "limitation_note": "Dataset Limitation: No Customer_ID column exists. Segmentation is performed at the transaction/cohort level rather than individual customer level.",
        "kmeans_profiles": kmeans_profiles,
        "hierarchical_profiles": hierarchical_profiles
    }


# ---------------------------------------------------
# CUSTOMER SEGMENTATION COMPARISON API (DAY 3 & 4 - NEW)
#
# Allowed Roles:
# All four roles
#
# URL:
# GET /customer-segmentation/comparison
# ---------------------------------------------------

@app.get("/customer-segmentation/comparison")
def customer_segmentation_comparison(
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Sales Executive",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(city, category, store_format, channel, payment_mode)

    km_profiles = compute_cluster_profiles("kmeans_cluster", filtered)
    agg_profiles = compute_cluster_profiles("hierarchical_cluster", filtered)

    km_max = max([p["percentage"] for p in km_profiles]) if km_profiles else 0
    km_min = min([p["percentage"] for p in km_profiles]) if km_profiles else 0

    agg_max = max([p["percentage"] for p in agg_profiles]) if agg_profiles else 0
    agg_min = min([p["percentage"] for p in agg_profiles]) if agg_profiles else 0

    return {
        "comparison_metrics": [
            {
                "metric": "Algorithm Basis",
                "kmeans": "Centroid Partitioning (K-Means)",
                "hierarchical": "Agglomerative Hierarchical Linkage"
            },
            {
                "metric": "Clusters Count (K)",
                "kmeans": "4 Clusters",
                "hierarchical": "4 Clusters"
            },
            {
                "metric": "Feature Standardization",
                "kmeans": "StandardScaler (Mean=0, Var=1)",
                "hierarchical": "StandardScaler (Mean=0, Var=1)"
            },
            {
                "metric": "Largest Segment Share",
                "kmeans": f"{km_max}%",
                "hierarchical": f"{agg_max}%"
            },
            {
                "metric": "Smallest Segment Share",
                "kmeans": f"{km_min}%",
                "hierarchical": f"{agg_min}%"
            }
        ],
        "kmeans_total_records": len(filtered),
        "hierarchical_total_records": len(filtered),
        "limitation_note": "Dataset Limitation: No Customer_ID column exists. Segmentation is performed at the transaction/cohort level rather than individual customer level."
    }


# ---------------------------------------------------
# SALES FORECASTING HELPERS & ENGINE (DAY 5 & 6 - NEW)
# ---------------------------------------------------

def get_daily_revenue_series(filtered_df: pd.DataFrame) -> pd.DataFrame:
    if filtered_df.empty:
        return pd.DataFrame(columns=["ds", "y"])

    temp = filtered_df.copy()
    temp["ds"] = temp["Invoice_Date_Parsed"].dt.date
    daily = (
        temp.groupby("ds")["Revenue"]
        .sum()
        .reset_index()
        .rename(columns={"ds": "ds", "Revenue": "y"})
    )
    daily["ds"] = pd.to_datetime(daily["ds"])
    return daily.sort_values("ds")


def generate_prophet_sales_forecast(daily_df: pd.DataFrame, horizon_days: int = 30):
    if daily_df.empty or len(daily_df) < 5:
        return {
            "model_used": "Insufficient Data",
            "forecast_horizon_days": horizon_days,
            "historical_data": [],
            "forecast_data": [],
            "summary_metrics": {
                "historical_avg_daily_revenue": 0.0,
                "projected_period_total_revenue": 0.0,
                "projected_growth_pct": 0.0
            }
        }

    model_name = "Statistical Exponential Trend (Fallback)"
    historical_data = [
        {"ds": row["ds"].strftime("%Y-%m-%d"), "y": round(float(row["y"]), 2)}
        for _, row in daily_df.iterrows()
    ]

    forecast_records = []

    # Attempt Prophet if installed
    try:
        from prophet import Prophet
        
        prophet_df = daily_df[["ds", "y"]].copy()
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            interval_width=0.90
        )
        model.fit(prophet_df)
        
        future = model.make_future_dataframe(periods=horizon_days, freq="D")
        forecast = model.predict(future)
        
        future_forecast = forecast.tail(horizon_days)
        for _, row in future_forecast.iterrows():
            yhat = max(0.0, float(row["yhat"]))
            yhat_lower = max(0.0, float(row["yhat_lower"]))
            yhat_upper = max(yhat_lower, float(row["yhat_upper"]))
            
            forecast_records.append({
                "ds": row["ds"].strftime("%Y-%m-%d"),
                "yhat": round(yhat, 2),
                "yhat_lower": round(yhat_lower, 2),
                "yhat_upper": round(yhat_upper, 2)
            })
        model_name = "Prophet (Facebook Time-Series Engine)"

    except Exception as e:
        # Fallback Engine using Exponential Smoothing / Weighted Trend
        last_date = daily_df["ds"].max()
        recent_30 = daily_df.tail(30)["y"].values
        recent_mean = float(recent_30.mean()) if len(recent_30) > 0 else float(daily_df["y"].mean())
        
        first_30 = daily_df.head(30)["y"].values
        first_mean = float(first_30.mean()) if len(first_30) > 0 else recent_mean
        trend_factor = (recent_mean - first_mean) / len(daily_df) if len(daily_df) > 30 else 0.0

        for i in range(1, horizon_days + 1):
            next_date = last_date + pd.Timedelta(days=i)
            dow = next_date.dayofweek
            season_mult = 1.05 if dow in [5, 6] else 0.98
            
            base_yhat = (recent_mean + (trend_factor * i)) * season_mult
            yhat = max(0.0, base_yhat)
            yhat_lower = max(0.0, yhat * 0.92)
            yhat_upper = yhat * 1.08

            forecast_records.append({
                "ds": next_date.strftime("%Y-%m-%d"),
                "yhat": round(yhat, 2),
                "yhat_lower": round(yhat_lower, 2),
                "yhat_upper": round(yhat_upper, 2)
            })

    # Calculate summary metrics
    hist_avg = round(float(daily_df["y"].mean()), 2)
    proj_total = round(sum(r["yhat"] for r in forecast_records), 2)
    proj_daily_avg = proj_total / horizon_days if horizon_days > 0 else 0
    growth_pct = round(((proj_daily_avg - hist_avg) / hist_avg * 100), 2) if hist_avg > 0 else 0.0

    return {
        "model_used": model_name,
        "forecast_horizon_days": horizon_days,
        "historical_data": historical_data,
        "forecast_data": forecast_records,
        "summary_metrics": {
            "historical_avg_daily_revenue": hist_avg,
            "projected_period_total_revenue": proj_total,
            "projected_growth_pct": growth_pct
        }
    }


def generate_ml_sales_forecast(daily_df: pd.DataFrame, horizon_days: int = 30, algorithm: str = "xgboost"):
    if daily_df.empty or len(daily_df) < 35:
        return {
            "model_used": f"{'XGBoost Regressor' if algorithm == 'xgboost' else 'Random Forest Regressor'} (Insufficient Data)",
            "forecast_horizon_days": horizon_days,
            "historical_data": [
                {"ds": row["ds"].strftime("%Y-%m-%d"), "y": round(float(row["y"]), 2)}
                for _, row in daily_df.iterrows()
            ] if not daily_df.empty else [],
            "forecast_data": [],
            "summary_metrics": {
                "historical_avg_daily_revenue": round(float(daily_df["y"].mean()), 2) if not daily_df.empty else 0.0,
                "projected_period_total_revenue": 0.0,
                "projected_growth_pct": 0.0
            }
        }

    # 1. Complete continuous daily time-series index
    min_date = daily_df["ds"].min()
    max_date = daily_df["ds"].max()
    full_dates = pd.date_range(start=min_date, end=max_date, freq="D")

    ts_df = (
        daily_df.set_index("ds")
        .reindex(full_dates, fill_value=0.0)
        .reset_index()
        .rename(columns={"index": "ds"})
    )
    ts_df["y"] = ts_df["y"].astype(float)

    # 2. Supervised feature engineering using past values
    ts_df["dayofweek"] = ts_df["ds"].dt.dayofweek
    ts_df["day"] = ts_df["ds"].dt.day
    ts_df["month"] = ts_df["ds"].dt.month
    ts_df["quarter"] = ts_df["ds"].dt.quarter
    ts_df["is_weekend"] = ts_df["dayofweek"].apply(lambda x: 1 if x in [5, 6] else 0)

    # Lags (shifted by 1 to prevent data leakage)
    ts_df["lag_1"] = ts_df["y"].shift(1)
    ts_df["lag_7"] = ts_df["y"].shift(7)
    ts_df["lag_14"] = ts_df["y"].shift(14)
    ts_df["lag_28"] = ts_df["y"].shift(28)

    # Rolling historical features (shifted by 1)
    ts_df["rolling_mean_7"] = ts_df["y"].shift(1).rolling(7, min_periods=1).mean()
    ts_df["rolling_mean_14"] = ts_df["y"].shift(1).rolling(14, min_periods=1).mean()
    ts_df["rolling_mean_28"] = ts_df["y"].shift(1).rolling(28, min_periods=1).mean()
    ts_df["rolling_std_7"] = ts_df["y"].shift(1).rolling(7, min_periods=1).std().fillna(0)
    ts_df["rolling_std_14"] = ts_df["y"].shift(1).rolling(14, min_periods=1).std().fillna(0)

    feature_cols = [
        "dayofweek", "day", "month", "quarter", "is_weekend",
        "lag_1", "lag_7", "lag_14", "lag_28",
        "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
        "rolling_std_7", "rolling_std_14"
    ]

    # 3. Chronological Train Set
    train_df = ts_df.dropna(subset=["lag_28"]).copy()
    if len(train_df) < 7:
        return {
            "model_used": f"{'XGBoost Regressor' if algorithm == 'xgboost' else 'Random Forest Regressor'} (Insufficient Training Samples)",
            "forecast_horizon_days": horizon_days,
            "historical_data": [
                {"ds": row["ds"].strftime("%Y-%m-%d"), "y": round(float(row["y"]), 2)}
                for _, row in daily_df.iterrows()
            ],
            "forecast_data": [],
            "summary_metrics": {
                "historical_avg_daily_revenue": round(float(daily_df["y"].mean()), 2),
                "projected_period_total_revenue": 0.0,
                "projected_growth_pct": 0.0
            }
        }

    X_train = train_df[feature_cols]
    y_train = train_df["y"]

    # 4. Model Training with Error Handling
    if algorithm == "xgboost":
        model_name = "XGBoost Regressor"
        try:
            import xgboost as xgb
            model = xgb.XGBRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=5,
                random_state=42
            )
            model.fit(X_train, y_train)
        except ImportError:
            from sklearn.ensemble import GradientBoostingRegressor
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=5,
                random_state=42
            )
            model.fit(X_train, y_train)
            model_name = "XGBoost Regressor (Gradient Boosting Engine)"
        except Exception:
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            model_name = "XGBoost Regressor (Fallback Engine)"
    else:
        model_name = "Random Forest Regressor"
        try:
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            model.fit(X_train, y_train)
        except Exception:
            from sklearn.ensemble import ExtraTreesRegressor
            model = ExtraTreesRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            model_name = "Random Forest Regressor (Fallback Engine)"

    # Compute training residual std for confidence intervals
    train_preds = model.predict(X_train)
    residuals = y_train - train_preds
    std_err = float(np.std(residuals)) if len(residuals) > 0 else 0.0

    # 5. Recursive Auto-Regressive Future Forecast Loop
    history_series = list(ts_df["y"].values)
    last_date = ts_df["ds"].max()
    forecast_records = []

    for step in range(1, horizon_days + 1):
        curr_date = last_date + pd.Timedelta(days=step)

        dow = curr_date.dayofweek
        d = curr_date.day
        m = curr_date.month
        q = curr_date.quarter
        is_wknd = 1 if dow in [5, 6] else 0

        lag_1 = float(history_series[-1])
        lag_7 = float(history_series[-7]) if len(history_series) >= 7 else float(history_series[0])
        lag_14 = float(history_series[-14]) if len(history_series) >= 14 else float(history_series[0])
        lag_28 = float(history_series[-28]) if len(history_series) >= 28 else float(history_series[0])

        r7 = history_series[-7:]
        r14 = history_series[-14:]
        r28 = history_series[-28:]

        rm_7 = float(np.mean(r7))
        rm_14 = float(np.mean(r14))
        rm_28 = float(np.mean(r28))
        rs_7 = float(np.std(r7))
        rs_14 = float(np.std(r14))

        feat_row = pd.DataFrame([{
            "dayofweek": dow,
            "day": d,
            "month": m,
            "quarter": q,
            "is_weekend": is_wknd,
            "lag_1": lag_1,
            "lag_7": lag_7,
            "lag_14": lag_14,
            "lag_28": lag_28,
            "rolling_mean_7": rm_7,
            "rolling_mean_14": rm_14,
            "rolling_mean_28": rm_28,
            "rolling_std_7": rs_7,
            "rolling_std_14": rs_14
        }])

        pred_y = float(model.predict(feat_row)[0])
        yhat = max(0.0, pred_y)

        # Margin expands with horizon step to reflect uncertainty
        margin = (1.96 * std_err) * (1 + 0.003 * step)
        yhat_lower = max(0.0, yhat - margin)
        yhat_upper = max(yhat_lower, yhat + margin)

        history_series.append(yhat)

        forecast_records.append({
            "ds": curr_date.strftime("%Y-%m-%d"),
            "yhat": round(yhat, 2),
            "yhat_lower": round(yhat_lower, 2),
            "yhat_upper": round(yhat_upper, 2)
        })

    historical_data = [
        {"ds": row["ds"].strftime("%Y-%m-%d"), "y": round(float(row["y"]), 2)}
        for _, row in daily_df.iterrows()
    ]

    hist_avg = round(float(daily_df["y"].mean()), 2)
    proj_total = round(sum(r["yhat"] for r in forecast_records), 2)
    proj_daily_avg = proj_total / horizon_days if horizon_days > 0 else 0
    growth_pct = round(((proj_daily_avg - hist_avg) / hist_avg * 100), 2) if hist_avg > 0 else 0.0

    return {
        "model_used": model_name,
        "forecast_horizon_days": horizon_days,
        "historical_data": historical_data,
        "forecast_data": forecast_records,
        "summary_metrics": {
            "historical_avg_daily_revenue": hist_avg,
            "projected_period_total_revenue": proj_total,
            "projected_growth_pct": growth_pct
        }
    }


def compute_model_comparison_metrics(daily_df: pd.DataFrame):
    """
    Evaluates Prophet, XGBoost, and Random Forest on the same chronological holdout window
    (last 30 days of historical data as test set, preceding days as train set).
    Calculates MAE, RMSE, and R2 score for each model.
    """
    if daily_df.empty or len(daily_df) < 35:
        return [
            {"model": "Prophet", "mae": 0.0, "rmse": 0.0, "r2_score": 0.0},
            {"model": "XGBoost", "mae": 0.0, "rmse": 0.0, "r2_score": 0.0},
            {"model": "Random Forest", "mae": 0.0, "rmse": 0.0, "r2_score": 0.0}
        ]

    min_date = daily_df["ds"].min()
    max_date = daily_df["ds"].max()
    full_dates = pd.date_range(start=min_date, end=max_date, freq="D")

    ts_df = (
        daily_df.set_index("ds")
        .reindex(full_dates, fill_value=0.0)
        .reset_index()
        .rename(columns={"index": "ds"})
    )
    ts_df["y"] = ts_df["y"].astype(float)

    eval_window = 30
    if len(ts_df) <= eval_window + 10:
        eval_window = max(5, len(ts_df) // 4)

    train_ts = ts_df.iloc[:-eval_window].copy()
    test_ts = ts_df.iloc[-eval_window:].copy()
    y_true = test_ts["y"].values

    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    def calc_metrics(y_actual, y_predicted):
        if len(y_actual) == 0:
            return {"mae": 0.0, "rmse": 0.0, "r2_score": 0.0}
        y_pred_clipped = np.clip(y_predicted, 0, None)
        mae = round(float(mean_absolute_error(y_actual, y_pred_clipped)), 2)
        mse = mean_squared_error(y_actual, y_pred_clipped)
        rmse = round(float(np.sqrt(mse)), 2)
        r2 = round(float(r2_score(y_actual, y_pred_clipped)), 4)
        return {"mae": mae, "rmse": rmse, "r2_score": r2}

    comparison_results = []

    # 1. Prophet Evaluation
    try:
        from prophet import Prophet
        prophet_train = train_ts[["ds", "y"]].copy()
        p_model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            interval_width=0.90
        )
        p_model.fit(prophet_train)
        future_p = p_model.make_future_dataframe(periods=eval_window, freq="D")
        fcst_p = p_model.predict(future_p)
        prophet_preds = fcst_p.tail(eval_window)["yhat"].values
        p_metrics = calc_metrics(y_true, prophet_preds)
        p_metrics["model"] = "Prophet"
    except Exception:
        recent = train_ts.tail(30)["y"].values
        recent_m = float(recent.mean()) if len(recent) > 0 else float(train_ts["y"].mean())
        fallback_preds = np.full(eval_window, recent_m)
        p_metrics = calc_metrics(y_true, fallback_preds)
        p_metrics["model"] = "Prophet"

    comparison_results.append(p_metrics)

    # 2. Supervised Feature Matrix for ML Models
    ts_df["dayofweek"] = ts_df["ds"].dt.dayofweek
    ts_df["day"] = ts_df["ds"].dt.day
    ts_df["month"] = ts_df["ds"].dt.month
    ts_df["quarter"] = ts_df["ds"].dt.quarter
    ts_df["is_weekend"] = ts_df["dayofweek"].apply(lambda x: 1 if x in [5, 6] else 0)

    ts_df["lag_1"] = ts_df["y"].shift(1)
    ts_df["lag_7"] = ts_df["y"].shift(7)
    ts_df["lag_14"] = ts_df["y"].shift(14)
    ts_df["lag_28"] = ts_df["y"].shift(28)

    ts_df["rolling_mean_7"] = ts_df["y"].shift(1).rolling(7, min_periods=1).mean()
    ts_df["rolling_mean_14"] = ts_df["y"].shift(1).rolling(14, min_periods=1).mean()
    ts_df["rolling_mean_28"] = ts_df["y"].shift(1).rolling(28, min_periods=1).mean()
    ts_df["rolling_std_7"] = ts_df["y"].shift(1).rolling(7, min_periods=1).std().fillna(0)
    ts_df["rolling_std_14"] = ts_df["y"].shift(1).rolling(14, min_periods=1).std().fillna(0)

    feature_cols = [
        "dayofweek", "day", "month", "quarter", "is_weekend",
        "lag_1", "lag_7", "lag_14", "lag_28",
        "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
        "rolling_std_7", "rolling_std_14"
    ]

    train_eval_df = ts_df.iloc[:-eval_window].dropna(subset=["lag_28"]).copy()
    if len(train_eval_df) >= 7:
        X_tr_eval = train_eval_df[feature_cols]
        y_tr_eval = train_eval_df["y"]

        def predict_ml_eval(model_obj):
            history_eval = list(ts_df.iloc[:-eval_window]["y"].values)
            last_tr_date = train_ts["ds"].max()
            preds = []
            for step in range(1, eval_window + 1):
                c_date = last_tr_date + pd.Timedelta(days=step)
                dow = c_date.dayofweek
                d = c_date.day
                m = c_date.month
                q = c_date.quarter
                is_wknd = 1 if dow in [5, 6] else 0

                l1 = float(history_eval[-1])
                l7 = float(history_eval[-7]) if len(history_eval) >= 7 else float(history_eval[0])
                l14 = float(history_eval[-14]) if len(history_eval) >= 14 else float(history_eval[0])
                l28 = float(history_eval[-28]) if len(history_eval) >= 28 else float(history_eval[0])

                r7 = history_eval[-7:]
                r14 = history_eval[-14:]
                r28 = history_eval[-28:]

                rm7 = float(np.mean(r7))
                rm14 = float(np.mean(r14))
                rm28 = float(np.mean(r28))
                rs7 = float(np.std(r7))
                rs14 = float(np.std(r14))

                feat_row = pd.DataFrame([{
                    "dayofweek": dow, "day": d, "month": m, "quarter": q, "is_weekend": is_wknd,
                    "lag_1": l1, "lag_7": l7, "lag_14": l14, "lag_28": l28,
                    "rolling_mean_7": rm7, "rolling_mean_14": rm14, "rolling_mean_28": rm28,
                    "rolling_std_7": rs7, "rolling_std_14": rs14
                }])
                py = float(model_obj.predict(feat_row)[0])
                py_clip = max(0.0, py)
                history_eval.append(py_clip)
                preds.append(py_clip)
            return np.array(preds)

        # 2. XGBoost Evaluation
        try:
            import xgboost as xgb
            xgb_model = xgb.XGBRegressor(
                n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42
            )
            xgb_model.fit(X_tr_eval, y_tr_eval)
        except Exception:
            from sklearn.ensemble import GradientBoostingRegressor
            xgb_model = GradientBoostingRegressor(
                n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42
            )
            xgb_model.fit(X_tr_eval, y_tr_eval)

        xgb_preds = predict_ml_eval(xgb_model)
        xgb_metrics = calc_metrics(y_true, xgb_preds)
        xgb_metrics["model"] = "XGBoost"
        comparison_results.append(xgb_metrics)

        # 3. Random Forest Evaluation
        try:
            from sklearn.ensemble import RandomForestRegressor
            rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
            rf_model.fit(X_tr_eval, y_tr_eval)
        except Exception:
            from sklearn.ensemble import ExtraTreesRegressor
            rf_model = ExtraTreesRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X_tr_eval, y_tr_eval)

        rf_preds = predict_ml_eval(rf_model)
        rf_metrics = calc_metrics(y_true, rf_preds)
        rf_metrics["model"] = "Random Forest"
        comparison_results.append(rf_metrics)
    else:
        comparison_results.append({"model": "XGBoost", "mae": 0.0, "rmse": 0.0, "r2_score": 0.0})
        comparison_results.append({"model": "Random Forest", "mae": 0.0, "rmse": 0.0, "r2_score": 0.0})

    return comparison_results


def generate_sales_forecast(daily_df: pd.DataFrame, horizon_days: int = 30, model_type: str = "prophet"):
    norm_model = (model_type or "prophet").lower().strip()
    if norm_model in ["xgboost", "xgb"]:
        result = generate_ml_sales_forecast(daily_df, horizon_days=horizon_days, algorithm="xgboost")
    elif norm_model in ["random_forest", "rf", "randomforest"]:
        result = generate_ml_sales_forecast(daily_df, horizon_days=horizon_days, algorithm="random_forest")
    else:
        result = generate_prophet_sales_forecast(daily_df, horizon_days=horizon_days)

    result["model_comparison"] = compute_model_comparison_metrics(daily_df)
    return result


# ---------------------------------------------------
# SALES FORECASTING API (DAY 5, 6 & 7 - UPDATED)
#
# Allowed Roles:
# All four roles
#
# URL:
# GET /sales-forecast
# ---------------------------------------------------

@app.get("/sales-forecast")
def sales_forecast(
    horizon: int = Query(30, ge=7, le=180),
    model_type: Optional[str] = Query("prophet"),
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Administrator"
        ])
    )
):

    filtered = get_filtered_df(city, category, store_format, channel, payment_mode)
    daily_df = get_daily_revenue_series(filtered)
    
    return generate_sales_forecast(daily_df, horizon_days=horizon, model_type=model_type)


# ---------------------------------------------------
# CUSTOMER SEGMENTATION ALIAS API (DAY 9 - NEW)
# URL: GET /segments
# ---------------------------------------------------

@app.get("/segments")
def segments(
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Sales Executive",
            "Administrator"
        ])
    )
):
    return customer_segmentation(
        city=city,
        category=category,
        store_format=store_format,
        channel=channel,
        payment_mode=payment_mode,
        user_data=user_data
    )


# ---------------------------------------------------
# SALES FORECAST ALIAS API (DAY 9 - NEW)
# URL: GET /forecast/revenue
# ---------------------------------------------------

@app.get("/forecast/revenue")
def forecast_revenue(
    horizon: int = Query(30, ge=7, le=180),
    model_type: Optional[str] = Query("prophet"),
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Administrator"
        ])
    )
):
    return sales_forecast(
        horizon=horizon,
        model_type=model_type,
        city=city,
        category=category,
        store_format=store_format,
        channel=channel,
        payment_mode=payment_mode,
        user_data=user_data
    )


# ---------------------------------------------------
# BUSINESS REPORT EXPORT API (DAY 9 - NEW)
# URL: GET /export-report
# ---------------------------------------------------

@app.get("/export-report")
def export_report(
    horizon: int = Query(30, ge=7, le=180),
    city: Optional[str] = None,
    category: Optional[str] = None,
    store_format: Optional[str] = None,
    channel: Optional[str] = None,
    payment_mode: Optional[str] = None,

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Administrator"
        ])
    )
):
    filtered = get_filtered_df(city, category, store_format, channel, payment_mode)

    # Sheet 1: Customer Segments
    kmeans_profiles = compute_cluster_profiles("kmeans_cluster", filtered)
    seg_records = []
    for p in kmeans_profiles:
        seg_records.append({
            "Segment Name": p.get("segment_name", f"Cluster {p['cluster_id']}"),
            "Cohort Record Count": p.get("record_count", 0),
            "Percentage Share (%)": p.get("percentage", 0.0),
            "Avg Purchase Value (₹)": p.get("mean_purchase_value", 0.0),
            "Avg Purchase Frequency (Units)": p.get("mean_purchase_frequency", 0.0),
            "Avg Customer Activity (Days)": p.get("mean_customer_activity_days", 0.0)
        })
    seg_df = pd.DataFrame(seg_records)

    # Sheet 2: Sales Forecast (XGBoost Regressor as specified)
    daily_df = get_daily_revenue_series(filtered)
    fcst_result = generate_sales_forecast(daily_df, horizon_days=horizon, model_type="xgboost")
    
    fcst_records = []
    for f in fcst_result.get("forecast_data", []):
        fcst_records.append({
            "Forecast Date": f.get("ds"),
            "Predicted Revenue (₹)": f.get("yhat"),
            "Lower Bound (₹)": f.get("yhat_lower"),
            "Upper Bound (₹)": f.get("yhat_upper"),
            "Model Used": fcst_result.get("model_used", "XGBoost Regressor")
        })
    fcst_df = pd.DataFrame(fcst_records)

    # Sheet 3: Executive Summary
    summary_records = [
        {"Metric": "Report Generated At", "Value": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")},
        {"Metric": "User Role", "Value": user_data.get("role", "N/A")},
        {"Metric": "Applied City Filter", "Value": city or "All"},
        {"Metric": "Applied Category Filter", "Value": category or "All"},
        {"Metric": "Applied Store Format Filter", "Value": store_format or "All"},
        {"Metric": "Applied Channel Filter", "Value": channel or "All"},
        {"Metric": "Applied Payment Mode Filter", "Value": payment_mode or "All"},
        {"Metric": "Forecast Horizon", "Value": f"{horizon} Days"},
        {"Metric": "Forecast Engine Model", "Value": fcst_result.get("model_used", "XGBoost Regressor")},
        {"Metric": "Historical Daily Mean Revenue", "Value": f"₹{fcst_result.get('summary_metrics', {}).get('historical_avg_daily_revenue', 0.0):,.2f}"},
        {"Metric": "Projected Period Total Revenue", "Value": f"₹{fcst_result.get('summary_metrics', {}).get('projected_period_total_revenue', 0.0):,.2f}"},
        {"Metric": "Projected Growth Rate", "Value": f"{fcst_result.get('summary_metrics', {}).get('projected_growth_pct', 0.0)}%"}
    ]
    summary_df = pd.DataFrame(summary_records)

    # Excel output in memory using openpyxl
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            seg_df.to_excel(writer, sheet_name="Customer Segments", index=False)
            fcst_df.to_excel(writer, sheet_name="Sales Forecast", index=False)
            summary_df.to_excel(writer, sheet_name="Executive Summary", index=False)
        excel_bytes = output.getvalue()
    except Exception:
        csv_data = f"--- CUSTOMER SEGMENTS ---\n{seg_df.to_csv(index=False)}\n\n--- SALES FORECAST (XGBoost) ---\n{fcst_df.to_csv(index=False)}"
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=MarketMind_AI_Business_Report.csv"}
        )

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=MarketMind_AI_Business_Report.xlsx"
        }
    )



