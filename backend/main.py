import os                                                   # STANDARD LIB IMPORT
import logging                                              # STANDARD LIB IMPORT
import bcrypt                                               # THIRD-PARTY FW & SECURITY IMPORT
from contextlib import asynccontextmanager                  # STANDARD LIB IMPORT
from datetime import datetime, timedelta, timezone          # STANDARD LIB IMPORT
from fastapi import FastAPI, HTTPException, Depends, Header # THIRD-PARTY FW & SECURITY IMPORT
from fastapi.middleware.cors import CORSMiddleware          # THIRD-PARTY FW & SECURITY IMPORT
from pydantic import BaseModel, EmailStr                    # THIRD-PARTY FW & SECURITY IMPORT
from jose import jwt, JWTError                              # THIRD-PARTY FW & SECURITY IMPORT
import pandas as pd                                         # THIRD-PARTY FW & SECURITY IMPORT

#---------------------------------------
# 1. SYSTEM CONFIGURATION & ARCHITECTURE
#---------------------------------------

# Setup Production Logging Architecture
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MarketMindCore")

# Security configuration for generating and verifying the JSON Web Token (JWT)
SECRET_KEY = "super-secret-key-for-internship"  # Used to sign session token (Which is kept as secret in production)
ALGORITHM = "HS256"                             # Cryptographic Algorithm used for signature matching (Simple Matching)

# Global variables stored in the server's volatile RAM memory (TEMP-MEMORY)
fake_users_db = {}  # The in-memory dictionary acting as a Temp DB for user account
CACHED_ANALYTICS = {"total_revenue": 0.0, "total_orders": 0, "top_product": "N/A"}  # This is the global cache store to hold heavy analytical calculations at startup of the code

#--------------------------------------------------------------
# 2. LIFESPAN EVENT HANDLING (THIS IS FOR THE STARTUP PIPELINE)
#--------------------------------------------------------------

# SETUP OF THE LIFESPAN EVENT
@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    DATA ENGINEERING PIPELINE EXECUTED AND LOADS EXACTLY ONCE WHEN THE SERVER BOOTS UP.
    FOR THE EXTRACTION, CLEANING, PROCESSES AND CACHES ANALYTICS THE DATASET FROM THE PHYSICAL RAW DATABASE OR DATASET.
    """
    logger.info("🎬 Initializing enterprise data extraction and cleaning pipeline...")

    # HERE THE INTERNAL FILE PATHS DYNAMICALLY BASED ON EXECUTION WORKSPACE CONTEXT
    file1 = "backend/online_retail_v1.csv" if os.path.exists("backend/online_retail_v1.csv") else "online_retail_v1.csv"
    file2 = "backend/online_retail_v2.csv" if os.path.exists("backend/online_retail_v2.csv") else "online_retail_v2.csv"

    # EMERGENCY FALLBACK CHECK IF UNDERLYING RESOURCE DATA IS MISSING
    if not os.path.exists(file1) or not os.path.exists(file2):
        logger.error("❌ Critical Error: Missing required retail dataset CSV source arrays!")
    else:
        try:
            #-----------------------------
            # PHASE 1 : EXTRACTION OF DATA
            #-----------------------------

            # LOAD RAW STRUCTURAL FILES AND MERGE THEM TOGETHER SEQUENTIALLY INTO A UNIFIED MATRIX
            df1 = pd.read_csv(file1)
            df2 = pd.read_csv(file2)
            df = pd.concat([df1, df2], ignore_index=True)

            #----------------------------------
            # PHASE 2 : STANDARDIZATION OF DATA
            #----------------------------------

            # NORMALIZE COLUMN KEY NAMES DYNAMICALLY TO PROTECT DOWNSTREAM DATA WORKFLOWS
            if "InvoiceNo" in df.columns:
                df.rename(columns={"InvoiceNo": "Invoice"}, inplace=True)
            if "UnitPrice" in df.columns:
                df.rename(columns={"UnitPrice": "Price"}, inplace=True)

            #----------------------------
            # PHASE 3 : CLEANSING OF DATA
            #----------------------------

            # DROPS INCOMPLETE CRITICAL TRACKING VALUES (NULL ROWS) AND FILTER OUT DUPLICATE ENTRIES
            df = df.dropna(subset=["Quantity", "Price", "Description"])
            df = df.drop_duplicates()

            # PURGE ORDER CANCELLATION ('C' PREFIX VALUES) CLEANLY BEFORE CALCULATING METRICS
            df["Invoice"] = df["Invoice"].astype(str)
            df = df[~df["Invoice"].str.startswith("C", na=True)]

            # CONVERT PRICING AND QUANTITIES TO NUMBERS, FORCING FACULTY VALUES/TEXT TO NaN
            df["Quantity"] = pd.to_numeric(df["Quantity"], errors='coerce')
            df["Price"] = pd.to_numeric(df["Price"], errors='coerce')
            # THIS ONLY REALISTIC TRANSACTION METRICS (GREATER THAN ZERO)
            df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]

            # PRECOMPUTE AND COMMIT ANALYTICAL FIELDS INTO MEMORY
            df["Revenue"] = df["Quantity"] * df["Price"]

            # FORMATE METRICS CLEANLY AND MAP THEM STRAIGHT INTO THE GLOBAL RAM STATE
            CACHED_ANALYTICS["total_revenue"] = round(float(df["Revenue"].sum()), 2)
            CACHED_ANALYTICS["total_orders"] = int(df["Invoice"].nunique())
            CACHED_ANALYTICS["top_product"] = str(df.groupby("Description")["Quantity"].sum().idxmax())

            logger.info("✅ Core retail transaction blocks successfully parsed, standardized, and committed to cache.")
        except Exception as e:
            logger.error(f"❌ Failed to parse data system frames on bootstrap lifecycle sequence: {str(e)}")

    yield   # SYSTEM RUNTIME WINDOW HANDOFF
    logger.info("🛑 Shutting down backend resources...")

#-----------------------------------------
# 3. APP INITIALIZATION & MIDDLEWARE SETUP
#-----------------------------------------

# Initialize FastAPI application with Lifespan
app = FastAPI(title="MarketMind AI Final Secure Server", version="1.0.0", lifespan=lifespan)

# CROSS-ORIGIN RESOURCE SHARING (CORS) RULES TO ALLOW FRONTEND BROWSERS TO CONNECT TO THIS API SECURELY
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # THE PRODUCTION, SWAP "*" FOR YOUR SPECIFIC FRONTEND URL
    allow_credentials=True,
    allow_methods=["*"],    # ALLOWS ALL REST METHODS (GET,POST,ETC)
    allow_headers=["*"],    # ALLOWS ALL AUTHORIZATION/PAYLOAD HEADERS
)

#----------------------------------------------------
# 4. DATA AUTHENTICATION STRUCT AND VALIDATION SCHEMA
#----------------------------------------------------

class UserRegister(BaseModel):
    name: str
    email: EmailStr # AUTOMATICALLY ENFORCES STRICT EMAIL SYNTAXES (e.g. name@domain.com)
    password: str
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

#----------------------------------------------
# 5. SECURITY & ROLE AUTHORIZATION DEPENDENCIES
#----------------------------------------------
def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Malformed security parameter string signature.")

    # EXTRACT THE RAW CRYPTOGRAPHIC TOKEN BLOCK
    token = authorization.replace("Bearer ", "")
    try:
        # DECODE AND INSPECT TAKEN PAYLOAD FIELDS
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # CONTAIN USER EMAIL,ROLE, AND TOKEN LIFESPAN LIMIT EXPIRATION
    except JWTError:
        raise HTTPException(status_code=401, detail="Expired session window or secure validation mismatch error.")


def require_role(allowed_roles: list):
    def role_checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403,
                                detail="Access Denied: Privilege validation match not found in role matrix.")
        return user

    return role_checker

#---------------------------------------
# 6. ROUTEING & API FUNCTIONAL ENDPOINTS
#---------------------------------------
@app.post("/register")
def register(user: UserRegister):
    if not user.password.strip():
        raise HTTPException(status_code=400, detail="Registration error: Password field cannot be empty.")

    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Resource Conflict: This profile is already registered.")

    # SCRAMBLE THE CLEAR TEXT PASSWORD NATIVELY USING STRONG CRYPTOGRAPHIC SALT HASHES BEFORE STORAGE
    hashed_bytes = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # MAO DETAILS CLEANLY BACK TO THE GLOBAL KEY DATABASE TRACKING MATRIX
    fake_users_db[user.email] = {
        "name": user.name,
        "role": user.role,
        "hashed_password": hashed_bytes.decode('utf-8')
    }
    return {"message": "User registered successfully!"}


@app.post("/login")
def login(credentials: UserLogin):
    user = fake_users_db.get(credentials.email)

    # SAFE VERIFICATION : EXTRACT bytes NATIVELY AND USE SECURE COMPARISON LOGIC TO VERIFY PASSWORDS
    if not user or not bcrypt.checkpw(credentials.credentials.password.encode('utf-8') if hasattr(credentials,
                                                                                                  'credentials') else credentials.password.encode(
            'utf-8'), user["hashed_password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credential combination passed.")

    # ENCODE INTERNAL METADATA TOKENS SET TO SELF-DESTRUCT EXACTLY 8 HOURS INTO THE FUTURE
    token = jwt.encode(
        {"sub": credentials.email, "role": user["role"], "exp": datetime.now(timezone.utc) + timedelta(hours=8)},
        SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": token, "role": user["role"]}


@app.get("/sales/summary")
def sales_summary(user: dict = Depends(require_role(["business_owner", "admin"]))):
    """
    FETCHES THE PRECOMPUTED TRANSACTION DATA.
    RESTRICTED TO ONLY HIGH-LEVEL STAKEHOLDER ('business_owner' AND 'admin').
    """
    logger.info(f"📊 Sales summary metrics requested by user identity: {user['sub']}")
    # RETURNS THE DICTIONARY GENERATED DURING SERVER BOOT-UP FROM MEMORY (LOW LATENCY)
    return CACHED_ANALYTICS


@app.get("/forecast/revenue")
def get_revenue_forecast(user: dict = Depends(require_role(["business_owner", "admin", "store_manager"]))):
    """
    RETRIEVES PREDICTIVE ANALYTICS TREND FORECASTS.
     ACCESSIBLE BY MANAGEMENT TIERS ('business_owner', 'admin', AND 'store_manager').
    """
    logger.info(f"📈 Revenue forecast model data accessed by: {user['sub']}")
    return {
        "status": "Access Granted",
        "feature": "Forecast Reports Grid",
        "requested_by": user["sub"],
        # MOCK FORECAST VALUES FOR DOWNSTREAM CHARTING/UI COMPONENTS
        "sample_forecast_trends": {"October_2026": 1250000.00, "November_2026": 1380000.00}
    }


@app.get("/admin/users")
def list_users(user: dict = Depends(require_role(["admin"]))):
    """
    STRICT ADMINISTRATIVE ROUTE TO AUDIT PROFILE REGISTRATION LISTINGS.
    EXCLUSIVE PRIVILEGE BOUNDARY ASSIGNED ONLY TO 'admin' USERS.
    """
    logger.info(f"⚙️ Identity workspace configuration reviewed by Admin context: {user['sub']}")
    return {
        "status": "Access Granted",
        "feature": "System User Directory Management",
        # PULLS UNIQUE TRACKING KEYS DIRECTLY FROM OUR GLOBAL IN-MEMORY DATABASE STORE
        "registered_user_profiles": list(fake_users_db.keys())
    }


@app.get("/invoices/view")
def view_invoices(user: dict = Depends(require_role(["business_owner", "admin", "store_manager", "sales_executive"]))):
    """
    READ-ONLY TRACKING ARCHIVE ENDPOINT FOR BILLING HISTORY.
    BROAD VISIBILITY ALLOWED ACROSS ALL FUNCTIONAL WORKPLACE PROFILE TYPES.
    """
    logger.info(f"🧾 Read-Only invoice log archive fetched by: {user['sub']}")
    return {
        "status": "Access Granted",
        "mode": "Read-Only",
        "message": "Displaying active transaction invoices archive database."
    }


@app.post("/invoices/create")
def create_invoice(user: dict = Depends(require_role(["sales_executive", "admin"]))):
    """
    WRITE-AUTHORIZED PIPELINE TO CREATE AND LOG NEW BILLING ENTRIES.
    STRICTLY ISOLATED TO TRANSACTIONAL PERSONNEL ('sales_executive' AND 'admin')
    """
    logger.info(f"➕ New ledger voucher generated securely by: {user['sub']}")
    return {
        "status": "Success",
        "mode": "Write-Authorized",
        "message": "New invoice ledger voucher record finalized successfully."
    }
