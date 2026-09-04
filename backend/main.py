# ---------------------------------------------------
# IMPORTS
# Purpose:
# Import all required libraries
# ---------------------------------------------------

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import pandas as pd
import os
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
            "sales_by_category": True
        }

    # Store Manager
    elif user_role == "Store Manager":

        return {
            "role": user_role,
            "total_revenue": False,
            "total_margin": False,
            "low_stock": True,
            "sales_by_city": True,
            "sales_by_category": True
        }

    # Sales Executive
    elif user_role == "Sales Executive":

        return {
            "role": user_role,
            "total_revenue": False,
            "total_margin": False,
            "low_stock": False,
            "sales_by_city": True,
            "sales_by_category": True
        }

    # Administrator
    elif user_role == "Administrator":

        return {
            "role": user_role,
            "total_revenue": True,
            "total_margin": True,
            "low_stock": True,
            "sales_by_city": True,
            "sales_by_category": True
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
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ---------------------------------------------------
# LOAD DATASET
# Purpose:
# Reads processed CSV file
# when backend starts
# ---------------------------------------------------

df = pd.read_csv(
    "processed_fmcg_retail_data.csv"
)


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
# TOTAL REVENUE API
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

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Administrator"
        ])
    )
):

    # Add all revenue values
    total = df["Revenue"].sum()

    return {
        "total_revenue": round(
            float(total),
            2
        )
    }


# ---------------------------------------------------
# TOTAL MARGIN API
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

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Administrator"
        ])
    )
):

    # Add all margin values
    total = df["Margin"].sum()

    return {
        "total_margin": round(
            float(total),
            2
        )
    }


# ---------------------------------------------------
# SALES BY CITY API
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

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Sales Executive",
            "Administrator"
        ])
    )
):

    # Group data by city
    # and calculate total revenue
    city_sales = (
        df.groupby("City")["Revenue"]
        .sum()
    )

    # Round values and convert to dictionary
    return city_sales.round(
        2
    ).to_dict()


# ---------------------------------------------------
# SALES BY CATEGORY API
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

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Sales Executive",
            "Administrator"
        ])
    )
):

    # Group data by category
    # and calculate total revenue
    category_sales = (
        df.groupby("Category")["Revenue"]
        .sum()
    )

    # Round values and convert to dictionary
    return category_sales.round(
        2
    ).to_dict()


# ---------------------------------------------------
# LOW STOCK API
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

    user_data: dict = Depends(
        require_roles([
            "Business Owner",
            "Store Manager",
            "Administrator"
        ])
    )
):

    # Count records where
    # Low_Stock_Flag is equal to 1
    low_stock_count = df[
        df["Low_Stock_Flag"] == 1
    ].shape[0]

    return {
        "low_stock_records": int(
            low_stock_count
        )
    }