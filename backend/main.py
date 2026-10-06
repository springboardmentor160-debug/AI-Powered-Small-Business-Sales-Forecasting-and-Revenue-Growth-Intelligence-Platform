import json
import logging
import threading
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import pandas as pd
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field


# ============================================================
# 1. SYSTEM CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("MarketMindCore")

SECRET_KEY = "super-secret-key-for-internship"
ALGORITHM = "HS256"


# ============================================================
# 2. PROJECT PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

# ------------------------------------------------------------
# UCI RAW DATA
# ------------------------------------------------------------

UCI_RAW_DIR = (
    BACKEND_DIR
    / "data"
    / "raw"
    / "uci"
)

UCI_FILE_1 = (
    UCI_RAW_DIR
    / "online_retail_v1.csv"
)

UCI_FILE_2 = (
    UCI_RAW_DIR
    / "online_retail_v2.csv"
)

# ------------------------------------------------------------
# UCI M2 FORECASTING ARTIFACTS
# ------------------------------------------------------------

UCI_ARTIFACT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)

# ------------------------------------------------------------
# SEGMENTATION ARTIFACTS
# ------------------------------------------------------------

SEGMENTATION_ARTIFACT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
)

# ------------------------------------------------------------
# M5 FORECASTING ARTIFACTS
# ------------------------------------------------------------

M5_ARTIFACT_DIR = (
    BACKEND_DIR
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)

# ------------------------------------------------------------
# INVOICE REGISTRY
# ------------------------------------------------------------

INVOICE_DATA_DIR = (
    BACKEND_DIR
    / "data"
)

INVOICE_FILE = (
    INVOICE_DATA_DIR
    / "invoices.json"
)

INVOICE_LOCK = threading.Lock()


# ============================================================
# 3. GLOBAL APPLICATION STATE
# ============================================================

fake_users_db = {}

CACHED_ANALYTICS = {
    "total_revenue": 0.0,
    "total_orders": 0,
    "top_product": "N/A",
}


# ============================================================
# 4. INVOICE STORAGE HELPERS
# ============================================================

def load_invoice_records() -> list[dict]:
    """
    Load invoices from the persistent JSON registry.

    The invoice registry is separate from the raw UCI/M5 datasets.
    """

    INVOICE_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not INVOICE_FILE.exists():
        return []

    try:

        with INVOICE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (
        json.JSONDecodeError,
        OSError,
    ) as error:

        logger.error(
            "Unable to load invoice registry: %s",
            error,
        )

        return []


def save_invoice_records(
    records: list[dict],
) -> None:
    """
    Persist invoice records safely.

    A temporary file is written first and then replaced.
    """

    INVOICE_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = (
        INVOICE_FILE.with_suffix(".tmp")
    )

    with temporary_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary_file.replace(
        INVOICE_FILE
    )


def read_uci_transactions() -> pd.DataFrame:
    """
    Read the two original UCI files.

    The original files are never modified.
    """

    missing_files = [
        str(path)
        for path in [
            UCI_FILE_1,
            UCI_FILE_2,
        ]
        if not path.exists()
    ]

    if missing_files:

        raise FileNotFoundError(
            "Required UCI files were not found: "
            + ", ".join(missing_files)
        )

    df1 = pd.read_csv(
        UCI_FILE_1,
        encoding="ISO-8859-1",
    )

    df2 = pd.read_csv(
        UCI_FILE_2,
        encoding="ISO-8859-1",
    )

    return pd.concat(
        [df1, df2],
        ignore_index=True,
    )


# ============================================================
# 5. STARTUP DATA PIPELINE
# ============================================================

@asynccontextmanager
async def lifespan(
    _: FastAPI,
) -> AsyncIterator[None]:

    logger.info(
        "Initializing MarketMindAI analytics pipeline..."
    )

    try:

        df = read_uci_transactions()

        # ----------------------------------------------------
        # Standardize source column names
        # ----------------------------------------------------

        rename_map = {}

        if "InvoiceNo" in df.columns:
            rename_map["InvoiceNo"] = "Invoice"

        if "UnitPrice" in df.columns:
            rename_map["UnitPrice"] = "Price"

        if rename_map:
            df = df.rename(
                columns=rename_map
            )

        # ----------------------------------------------------
        # Validate source schema
        # ----------------------------------------------------

        required_columns = [
            "Invoice",
            "Quantity",
            "Price",
            "Description",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:

            raise ValueError(
                "UCI dataset missing columns: "
                + str(missing_columns)
            )

        # ----------------------------------------------------
        # M1 analytical preparation
        # ----------------------------------------------------

        df = df.dropna(
            subset=[
                "Quantity",
                "Price",
                "Description",
            ]
        )

        df = df.drop_duplicates()

        df["Invoice"] = (
            df["Invoice"]
            .astype(str)
        )

        df["Quantity"] = pd.to_numeric(
            df["Quantity"],
            errors="coerce",
        )

        df["Price"] = pd.to_numeric(
            df["Price"],
            errors="coerce",
        )

        df = df[
            ~df["Invoice"].str.startswith(
                "C",
                na=True,
            )
            & (df["Quantity"] > 0)
            & (df["Price"] > 0)
        ].copy()

        df["Revenue"] = (
            df["Quantity"]
            * df["Price"]
        )

        # ----------------------------------------------------
        # Cache executive analytics
        # ----------------------------------------------------

        CACHED_ANALYTICS[
            "total_revenue"
        ] = round(
            float(
                df["Revenue"].sum()
            ),
            2,
        )

        CACHED_ANALYTICS[
            "total_orders"
        ] = int(
            df["Invoice"].nunique()
        )

        if not df.empty:

            CACHED_ANALYTICS[
                "top_product"
            ] = str(
                df.groupby(
                    "Description"
                )["Quantity"]
                .sum()
                .idxmax()
            )

        logger.info(
            "UCI analytics loaded successfully."
        )

        logger.info(
            "Total revenue: %.2f",
            CACHED_ANALYTICS[
                "total_revenue"
            ],
        )

        logger.info(
            "Total orders: %s",
            CACHED_ANALYTICS[
                "total_orders"
            ],
        )

    except Exception as error:

        logger.exception(
            "UCI analytics initialization failed: %s",
            error,
        )

    # --------------------------------------------------------
    # Ensure invoice storage exists
    # --------------------------------------------------------

    INVOICE_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not INVOICE_FILE.exists():

        save_invoice_records([])

    yield

    logger.info(
        "MarketMindAI backend shutdown complete."
    )


# ============================================================
# 6. FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="MarketMind AI Secure Server",
    version="2.1.0",
    description=(
        "MarketMind AI - Small Business Sales "
        "Intelligence Platform - Milestone 2 API"
    ),
    lifespan=lifespan,
)


# ============================================================
# 7. CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 8. REQUEST MODELS
# ============================================================

class UserRegister(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=4,
        max_length=128,
    )

    role: str


class UserLogin(BaseModel):

    email: EmailStr

    password: str


class InvoiceCreate(BaseModel):

    customer_name: str = Field(
        min_length=1,
        max_length=150,
    )

    product_name: str = Field(
        min_length=1,
        max_length=200,
    )

    quantity: int = Field(
        gt=0,
        le=1_000_000,
    )

    unit_price: float = Field(
        gt=0,
        le=100_000_000,
    )

    payment_status: str = Field(
        default="Pending",
        min_length=1,
        max_length=30,
    )


# ============================================================
# 9. SECURITY / RBAC
# ============================================================

def get_current_user(
    authorization: str = Header(...),
) -> dict:

    if not authorization.startswith(
        "Bearer "
    ):

        raise HTTPException(
            status_code=401,
            detail=(
                "Malformed Authorization header. "
                "Expected Bearer token."
            ),
        )

    token = (
        authorization[7:]
        .strip()
    )

    if not token:

        raise HTTPException(
            status_code=401,
            detail="Missing bearer token.",
        )

    try:

        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[
                ALGORITHM
            ],
        )

    except JWTError as error:

        logger.warning(
            "JWT validation failed: %s",
            error,
        )

        raise HTTPException(
            status_code=401,
            detail=(
                "Expired or invalid "
                "authentication token."
            ),
        ) from error


def require_role(
    allowed_roles: list[str],
):

    def role_checker(
        user: dict = Depends(
            get_current_user
        ),
    ):

        if user.get("role") not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Access denied. "
                    "Required role(s): "
                    + ", ".join(
                        allowed_roles
                    )
                ),
            )

        return user

    return role_checker


# ============================================================
# 10. SYSTEM HEALTH
# ============================================================

@app.get("/")
def root():

    return {
        "application": "MarketMind AI",
        "version": "2.1.0",
        "status": "online",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "MarketMind AI backend",
        "version": "2.1.0",
    }


# ============================================================
# 11. REGISTRATION
# ============================================================

@app.post("/register")
def register(
    user: UserRegister,
):

    email = (
        str(user.email)
        .lower()
        .strip()
    )

    allowed_roles = {
        "business_owner",
        "store_manager",
        "sales_executive",
        "admin",
    }

    if user.role not in allowed_roles:

        raise HTTPException(
            status_code=400,
            detail="Invalid business role.",
        )

    if not user.password.strip():

        raise HTTPException(
            status_code=400,
            detail="Password cannot be empty.",
        )

    if email in fake_users_db:

        raise HTTPException(
            status_code=400,
            detail=(
                "This profile is "
                "already registered."
            ),
        )

    hashed_password = (
        bcrypt.hashpw(
            user.password.encode(
                "utf-8"
            ),
            bcrypt.gensalt(),
        )
        .decode("utf-8")
    )

    fake_users_db[email] = {
        "name": user.name.strip(),
        "role": user.role,
        "hashed_password": hashed_password,
    }

    logger.info(
        "Registered user: %s",
        email,
    )

    return {
        "message": (
            "User registered successfully!"
        ),
        "email": email,
        "role": user.role,
    }


# ============================================================
# 12. LOGIN
# ============================================================

@app.post("/login")
def login(
    credentials: UserLogin,
):

    email = (
        str(credentials.email)
        .lower()
        .strip()
    )

    user = fake_users_db.get(
        email
    )

    if (
        not user
        or not bcrypt.checkpw(
            credentials.password.encode(
                "utf-8"
            ),
            user[
                "hashed_password"
            ].encode(
                "utf-8"
            ),
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    token = jwt.encode(
        {
            "sub": email,
            "role": user["role"],
            "exp": (
                datetime.now(
                    timezone.utc
                )
                + timedelta(hours=8)
            ),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "access_token": token,
        "role": user["role"],
    }


# ============================================================
# 13. M1 SALES SUMMARY
# ============================================================

@app.get("/sales/summary")
def sales_summary(
    user: dict = Depends(
        require_role(
            [
                "business_owner",
                "admin",
            ]
        )
    ),
):

    logger.info(
        "Sales summary requested by %s",
        user["sub"],
    )

    return {
        "status": "Access Granted",
        **CACHED_ANALYTICS,
    }


# ============================================================
# 14. M2 UCI REVENUE FORECAST
# ============================================================

@app.get("/forecast/revenue")
def get_revenue_forecast(
    user: dict = Depends(
        require_role(
            [
                "business_owner",
                "admin",
                "store_manager",
            ]
        )
    ),
):

    comparison_path = (
        UCI_ARTIFACT_DIR
        / "uci_model_comparison.csv"
    )

    predictions_path = (
        UCI_ARTIFACT_DIR
        / "uci_model_comparison_predictions.csv"
    )

    if not comparison_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "UCI model comparison "
                "artifact not found."
            ),
        )

    comparison = pd.read_csv(
        comparison_path
    )

    required_columns = {
        "model",
        "mae",
        "rmse",
    }

    if not required_columns.issubset(
        comparison.columns
    ):

        raise HTTPException(
            status_code=500,
            detail=(
                "UCI model comparison "
                "artifact has an unexpected schema."
            ),
        )

    validation = {}

    for column in [
        "test_split",
        "test_start",
        "test_end",
        "test_rows",
    ]:

        if (
            column in comparison.columns
            and not comparison.empty
        ):

            value = comparison[
                column
            ].iloc[0]

            if column == "test_rows":

                validation[column] = int(
                    value
                )

            else:

                validation[column] = str(
                    value
                )

    response = {
        "status": "Access Granted",
        "feature": (
            "UCI Revenue Forecasting"
        ),
        "requested_by": user["sub"],
        "validation": validation,
        "models": comparison[
            [
                "model",
                "mae",
                "rmse",
            ]
        ].to_dict(
            orient="records"
        ),
    }

    if predictions_path.exists():

        predictions = pd.read_csv(
            predictions_path
        )

        if "date" in predictions.columns:

            predictions["date"] = (
                pd.to_datetime(
                    predictions["date"],
                    errors="coerce",
                )
                .dt.strftime(
                    "%Y-%m-%d"
                )
            )

        numeric_columns = [
            "actual_revenue",
            "prophet_prediction",
            "random_forest_prediction",
            "xgboost_prediction",
        ]

        for column in numeric_columns:

            if column in predictions.columns:

                predictions[column] = (
                    pd.to_numeric(
                        predictions[column],
                        errors="coerce",
                    )
                    .fillna(0)
                )

        response[
            "predictions"
        ] = (
            predictions
            .fillna("")
            .to_dict(
                orient="records"
            )
        )

    return response


# ============================================================
# 15. M2 CUSTOMER SEGMENTATION
# ============================================================

@app.get("/segments")
def get_customer_segments(
    user: dict = Depends(
        require_role(
            [
                "business_owner",
                "admin",
                "store_manager",
            ]
        )
    ),
):

    segmentation_file = (
        SEGMENTATION_ARTIFACT_DIR
        / "customer_segments_final.csv"
    )

    if not segmentation_file.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Customer segmentation "
                "artifact not found."
            ),
        )

    try:

        df = pd.read_csv(
            segmentation_file
        )

        required_columns = [
            "Customer ID",
            "purchase_frequency",
            "purchase_value",
            "last_purchase_date",
            "customer_activity_days",
            "cluster",
            "cluster_hierarchical",
            "segment_name",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:

            raise HTTPException(
                status_code=500,
                detail=(
                    "Segmentation artifact "
                    "missing columns: "
                    + str(
                        missing_columns
                    )
                ),
            )

        segment_summary = (
            df.groupby(
                "segment_name",
                dropna=False,
            )
            .agg(
                customer_count=(
                    "Customer ID",
                    "count",
                ),
                average_purchase_frequency=(
                    "purchase_frequency",
                    "mean",
                ),
                average_purchase_value=(
                    "purchase_value",
                    "mean",
                ),
                average_customer_activity_days=(
                    "customer_activity_days",
                    "mean",
                ),
            )
            .reset_index()
            .rename(
                columns={
                    "segment_name": "segment"
                }
            )
        )

        for column in [
            "average_purchase_frequency",
            "average_purchase_value",
            "average_customer_activity_days",
        ]:

            segment_summary[
                column
            ] = segment_summary[
                column
            ].round(2)

        customers = (
            df[
                required_columns
            ]
            .where(
                pd.notnull(
                    df[
                        required_columns
                    ]
                ),
                None,
            )
            .to_dict(
                orient="records"
            )
        )

        return {
            "status": "Access Granted",
            "feature": (
                "Customer Segmentation "
                "Intelligence"
            ),
            "total_customers": int(
                len(df)
            ),
            "segment_count": int(
                df[
                    "segment_name"
                ].nunique()
            ),
            "segment_summary": (
                segment_summary
                .to_dict(
                    orient="records"
                )
            ),
            "customers": customers,
        }

    except HTTPException:
        raise

    except Exception as error:

        logger.exception(
            "Segmentation endpoint failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load "
                f"segmentation results: {error}"
            ),
        ) from error


# ============================================================
# 16. M2 M5 DEMAND FORECAST
# ============================================================

@app.get("/forecast/demand")
def get_demand_forecast(
    user: dict = Depends(
        require_role(
            [
                "business_owner",
                "admin",
                "store_manager",
            ]
        )
    ),
):

    comparison_path = (
        M5_ARTIFACT_DIR
        / "m5_model_comparison.csv"
    )

    predictions_path = (
        M5_ARTIFACT_DIR
        / "m5_xgboost_predictions.csv"
    )

    if not comparison_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "M5 model comparison "
                "artifact not found."
            ),
        )

    comparison = pd.read_csv(
        comparison_path
    )

    required_columns = {
        "model",
        "mae",
        "rmse",
    }

    if not required_columns.issubset(
        comparison.columns
    ):

        raise HTTPException(
            status_code=500,
            detail=(
                "M5 model comparison "
                "artifact has an unexpected schema."
            ),
        )

    model_columns = [
        column
        for column in [
            "model",
            "mae",
            "rmse",
            "mae_change_vs_baseline_pct",
            "rmse_change_vs_baseline_pct",
        ]
        if column in comparison.columns
    ]

    response = {
        "status": "Access Granted",
        "feature": (
            "M5 Item-Store Demand Forecasting"
        ),
        "requested_by": user["sub"],
        "validation_horizon_days": 28,
        "validation_start": (
            str(
                comparison[
                    "validation_start"
                ].iloc[0]
            )
            if "validation_start"
            in comparison.columns
            else None
        ),
        "validation_end": (
            str(
                comparison[
                    "validation_end"
                ].iloc[0]
            )
            if "validation_end"
            in comparison.columns
            else None
        ),
        "models": comparison[
            model_columns
        ].to_dict(
            orient="records"
        ),
    }

    if predictions_path.exists():

        predictions = pd.read_csv(
            predictions_path
        )

        if "date" in predictions.columns:

            predictions["date"] = (
                pd.to_datetime(
                    predictions["date"],
                    errors="coerce",
                )
                .dt.strftime(
                    "%Y-%m-%d"
                )
            )

        for column in [
            "actual_units",
            "predicted_units",
            "absolute_error",
            "squared_error",
        ]:

            if column in predictions.columns:

                predictions[column] = (
                    pd.to_numeric(
                        predictions[column],
                        errors="coerce",
                    )
                    .fillna(0)
                )

        response[
            "predictions"
        ] = (
            predictions
            .fillna("")
            .to_dict(
                orient="records"
            )
        )

    return response


# ============================================================
# 17. M2 MODEL COMPARISON
# ============================================================

@app.get("/forecast/models")
def get_forecast_model_comparison(
    user: dict = Depends(
        require_role(
            [
                "business_owner",
                "admin",
                "store_manager",
            ]
        )
    ),
):

    uci_path = (
        UCI_ARTIFACT_DIR
        / "uci_model_comparison.csv"
    )

    m5_path = (
        M5_ARTIFACT_DIR
        / "m5_model_comparison.csv"
    )

    if not uci_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "UCI comparison "
                "artifact not found."
            ),
        )

    if not m5_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "M5 comparison "
                "artifact not found."
            ),
        )

    uci = pd.read_csv(
        uci_path
    )

    m5 = pd.read_csv(
        m5_path
    )

    return {
        "status": "Access Granted",
        "uci_revenue_models": uci[
            [
                "model",
                "mae",
                "rmse",
            ]
        ].to_dict(
            orient="records"
        ),
        "m5_demand_models": m5[
            [
                "model",
                "mae",
                "rmse",
            ]
        ].to_dict(
            orient="records"
        ),
    }


# ============================================================
# 18. ADMIN GOVERNANCE
# ============================================================

@app.get("/admin/users")
def list_users(
    user: dict = Depends(
        require_role(
            ["admin"]
        )
    ),
):

    return {
        "status": "Access Granted",
        "feature": (
            "System User Directory "
            "Management"
        ),
        "registered_user_profiles": list(
            fake_users_db.keys()
        ),
    }


# ============================================================
# 19. INVOICE REGISTRY — VIEW
# ============================================================

@app.get("/invoices/view")
def view_invoices(
    user: dict = Depends(
        require_role(
            [
                "business_owner",
                "admin",
                "store_manager",
                "sales_executive",
            ]
        )
    ),
):

    logger.info(
        "Invoice registry requested by %s",
        user["sub"],
    )

    with INVOICE_LOCK:

        records = load_invoice_records()

    records = sorted(
        records,
        key=lambda item: item.get(
            "created_at",
            "",
        ),
        reverse=True,
    )

    return {
        "status": "Access Granted",
        "mode": "Read-Only",
        "message": (
            "Displaying active transaction "
            "invoice registry."
        ),
        "total_invoices": len(
            records
        ),
        "invoices": records,
    }


# ============================================================
# 20. INVOICE REGISTRY — CREATE
# ============================================================

@app.post("/invoices/create")
def create_invoice(
    invoice: InvoiceCreate,
    user: dict = Depends(
        require_role(
            [
                "sales_executive",
                "admin",
            ]
        )
    ),
):

    payment_status = (
        invoice.payment_status
        .strip()
        .title()
    )

    allowed_statuses = {
        "Pending",
        "Paid",
        "Cancelled",
    }

    if payment_status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid payment status. "
                "Use Pending, Paid, or Cancelled."
            ),
        )

    total_amount = round(
        invoice.quantity
        * invoice.unit_price,
        2,
    )

    invoice_record = {
        "invoice_id": (
            "INV-"
            + uuid.uuid4()
            .hex[:10]
            .upper()
        ),
        "customer_name": (
            invoice.customer_name
            .strip()
        ),
        "product_name": (
            invoice.product_name
            .strip()
        ),
        "quantity": invoice.quantity,
        "unit_price": round(
            invoice.unit_price,
            2,
        ),
        "total_amount": total_amount,
        "payment_status": payment_status,
        "created_by": user["sub"],
        "created_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
    }

    with INVOICE_LOCK:

        records = (
            load_invoice_records()
        )

        records.append(
            invoice_record
        )

        save_invoice_records(
            records
        )

    logger.info(
        "Invoice %s created by %s",
        invoice_record[
            "invoice_id"
        ],
        user["sub"],
    )

    return {
        "status": "Success",
        "mode": "Write-Authorized",
        "message": (
            "Invoice created and "
            "persisted successfully."
        ),
        "invoice": invoice_record,
    }


# ============================================================
# 21. M2 INVENTORY PREVIEW
# ============================================================

@app.get("/milestone2/preview")
def milestone2_inventory_preview():

    """
    Generate estimated inventory from
    the original UCI source files.

    Formula:

        InitialStock =
            TotalUnitsSold × 1.5

    Raw UCI files are read only.
    """

    try:

        df = read_uci_transactions()

        required_columns = [
            "StockCode",
            "Description",
            "Quantity",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Missing required "
                    "inventory columns: "
                    + str(
                        missing_columns
                    )
                ),
            )

        df["Quantity"] = pd.to_numeric(
            df["Quantity"],
            errors="coerce",
        )

        sales_df = df[
            df["Quantity"] > 0
        ].copy()

        inventory = (
            sales_df
            .groupby(
                [
                    "StockCode",
                    "Description",
                ],
                dropna=False,
            )
            .agg(
                TotalUnitsSold=(
                    "Quantity",
                    "sum",
                )
            )
            .reset_index()
            .rename(
                columns={
                    "StockCode": "ProductID",
                    "Description": (
                        "ProductDescription"
                    ),
                }
            )
        )

        inventory[
            "InitialStock"
        ] = (
            inventory[
                "TotalUnitsSold"
            ]
            * 1.5
        ).round().astype(
            "int64"
        )

        inventory[
            "EstimatedRemainingStock"
        ] = (
            inventory[
                "InitialStock"
            ]
            - inventory[
                "TotalUnitsSold"
            ]
        ).clip(
            lower=0
        ).round().astype(
            "int64"
        )

        records = (
            inventory
            .fillna("")
            .to_dict(
                orient="records"
            )
        )

        return {
            "message": (
                "Milestone 2 inventory "
                "preview generated"
            ),
            "source_files": [
                UCI_FILE_1.name,
                UCI_FILE_2.name,
            ],
            "inventory_method": (
                "Estimated InitialStock = "
                "TotalUnitsSold × 1.5"
            ),
            "note": (
                "This is estimated inventory, "
                "not verified physical stock."
            ),
            "total_products": len(
                records
            ),
            "total_units_sold": int(
                inventory[
                    "TotalUnitsSold"
                ].sum()
            ),
            "total_estimated_initial_stock": int(
                inventory[
                    "InitialStock"
                ].sum()
            ),
            "total_estimated_remaining_stock": int(
                inventory[
                    "EstimatedRemainingStock"
                ].sum()
            ),
            "products": records,
        }

    except HTTPException:
        raise

    except Exception as error:

        logger.exception(
            "Inventory preview failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Inventory preview failed: "
                f"{error}"
            ),
        ) from error