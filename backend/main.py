
import os
import json
import re
import threading
import logging
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import FileResponse, JSONResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from scipy.sparse import csr_matrix
from sklearn.preprocessing import normalize

from database import engine
from models import User, Role, SalesTransaction, Transaction, Customer
from schemas import (
    UserCreate,
    UserOut,
    UserMeOut,
    UserLogin,
    SalesTransactionOut,
    TransactionOut,
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)

logger = logging.getLogger("marketmind")

app = FastAPI(title="MarketMind AI API")

# ---------------------------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------------------------
# Configure CORS_ORIGINS in docker-compose.yml or the environment.
# Example:
# CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
#
# Origins must match the browser's frontend origin, including the port.
# Do not use "*" together with allow_credentials=True.

_default_origins = (
    "http://localhost:5173,"
    "http://127.0.0.1:5173"
)

cors_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "CORS_ORIGINS",
        _default_origins,
    ).split(",")
    if origin.strip()
]

logger.info("Allowed CORS origins: %s", cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SessionLocal = sessionmaker(bind=engine)


# ---------------------------------------------------------------------------
# Database error handling
# ---------------------------------------------------------------------------
@app.exception_handler(SQLAlchemyError)
def database_error_handler(request: Request, exc: SQLAlchemyError):
    """Return a controlled response for unhandled database failures."""
    logger.exception("Database error on %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": (
                "The database is temporarily unavailable. "
                "Please try again shortly."
            )
        },
    )


# ---------------------------------------------------------------------------
# Paths and database dependency
# ---------------------------------------------------------------------------
# backend/ and ml/ are expected to be sibling directories.
REPORT_DIR = Path(__file__).resolve().parent.parent / "ml" / "outputs"

RETAIL_DATA = (
    REPORT_DIR.parent.parent
    / "datasets"
    / "processed"
    / "online_retail_prepped.csv"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Authentication and user management
# ---------------------------------------------------------------------------
@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    if not db.query(Role).filter(Role.id == user.role_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown role",
        )

    new_user = User(
        name=user.name,
        email=user.email,
        role_id=user.role_id,
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Could not create the account: "
                "check the role and email"
            ),
        )

    db.refresh(new_user)
    return new_user


@app.post("/login")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == credentials.email)
        .first()
    )

    if not user or not verify_password(
        credentials.password,
        user.hashed_password if user else "",
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user


def require_role(allowed_roles: list[str]):
    def role_checker(
        current_user: User = Depends(get_current_user),
    ):
        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return current_user

    return role_checker


@app.get("/me", response_model=UserMeOut)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserMeOut(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.name,
    )


@app.get("/admin-only")
def admin_only_route(
    current_user: User = Depends(require_role(["admin"])),
):
    return {
        "message": (
            f"Welcome {current_user.name}, you are an admin"
        )
    }


# ---------------------------------------------------------------------------
# Sales and transaction endpoints
# ---------------------------------------------------------------------------
@app.get(
    "/sales-transactions",
    response_model=list[SalesTransactionOut],
)
def get_sales_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["owner", "store_manager", "admin"])
    ),
):
    return db.query(SalesTransaction).limit(50).all()


@app.get(
    "/transactions",
    response_model=list[TransactionOut],
)
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["owner", "admin", "sales_exec"])
    ),
):
    query = db.query(Transaction)

    if current_user.role.name == "sales_exec":
        query = (
            query
            .join(
                Customer,
                Transaction.customer_id == Customer.customer_id,
            )
            .filter(
                Customer.assigned_rep_id == current_user.id
            )
        )

    return query.limit(50).all()


@app.get("/sales/summary")
def sales_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["owner", "store_manager", "admin"])
    ),
):
    total_units_sold = (
        db.query(func.sum(SalesTransaction.units_sold)).scalar()
    )
    total_inventory = (
        db.query(func.sum(SalesTransaction.inventory_level)).scalar()
    )
    low_stock_count = (
        db.query(SalesTransaction)
        .filter(SalesTransaction.inventory_level < 100)
        .count()
    )

    return {
        "total_units_sold": total_units_sold or 0,
        "total_inventory": total_inventory or 0,
        "low_stock_count": low_stock_count,
    }


# ---------------------------------------------------------------------------
# JSON report endpoints
# ---------------------------------------------------------------------------
def load_report(filename: str):
    path = REPORT_DIR / filename

    try:
        return json.loads(path.read_text(encoding="utf-8"))

    except FileNotFoundError:
        logger.error(
            "Report %s not found; run the report-generation scripts",
            path,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="This report is temporarily unavailable",
        )

    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.error("Report %s is empty or corrupted", path)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="This report is temporarily unavailable",
        )


@app.get("/segments")
def get_segments(
    current_user: User = Depends(
        require_role(["owner", "store_manager", "admin"])
    ),
):
    return load_report("segment_summary.json")


@app.get("/forecast/revenue")
def get_revenue_forecast(
    current_user: User = Depends(
        require_role(["owner", "admin"])
    ),
):
    return load_report("forecast_summary.json")


# ---------------------------------------------------------------------------
# CSV reports: churn, anomalies, and cross-sell
# ---------------------------------------------------------------------------
def load_csv_report(filename: str) -> list[dict]:
    path = REPORT_DIR / filename

    try:
        df = pd.read_csv(path)

    except FileNotFoundError:
        logger.error("Report file missing: %s", path)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "This report is temporarily unavailable "
                "(it hasn't been generated yet)"
            ),
        )

    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        logger.error("Report file empty or corrupted: %s", path)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="This report file is damaged. Please regenerate it.",
        )

    return json.loads(df.to_json(orient="records"))


def cross_sell_for(
    product: str,
    limit: int = 3,
) -> list[str]:
    product = product.strip()
    matches = []

    for rule in load_csv_report("association_rules.csv"):
        antecedent = re.sub(
            r"\s+,",
            ",",
            str(rule["antecedents"]),
        ).strip()

        if f", {product}, " in f", {antecedent}, ":
            matches.append(rule)

    matches.sort(
        key=lambda rule: rule["lift"],
        reverse=True,
    )

    suggestions = []

    for rule in matches:
        name = str(rule["consequents"]).strip()

        if name not in suggestions:
            suggestions.append(name)

    return suggestions[:limit]


@app.get("/churn")
def get_churn_predictions(
    current_user: User = Depends(
        require_role(["owner", "admin"])
    ),
):
    records = load_csv_report("churn_predictions.csv")

    counts = Counter(
        record.get("retention_risk")
        for record in records
    )

    records.sort(
        key=lambda record: record.get("churn_probability") or 0,
        reverse=True,
    )

    return {
        "total_customers": len(records),
        "risk_summary": {
            risk: counts.get(risk, 0)
            for risk in (
                "High Risk",
                "Medium Risk",
                "Low Risk",
            )
        },
        "model_used": (
            records[0].get("model_used")
            if records
            else None
        ),
        "customers": records[:100],
    }


@app.get("/anomalies")
def get_anomaly_alerts(
    current_user: User = Depends(
        require_role(["owner", "admin", "store_manager"])
    ),
):
    records = load_csv_report("anomaly_alerts.csv")

    records.sort(
        key=lambda record: (
            0 if record.get("severity") == "high" else 1
        )
    )

    return {
        "total_alerts": len(records),
        "high_severity": sum(
            record.get("severity") == "high"
            for record in records
        ),
        "medium_severity": sum(
            record.get("severity") == "medium"
            for record in records
        ),
        "alerts": records[:100],
    }


# ---------------------------------------------------------------------------
# Business report download
# ---------------------------------------------------------------------------
@app.get("/reports/business")
def download_business_report(
    current_user: User = Depends(
        require_role(["owner", "admin"])
    ),
):
    path = REPORT_DIR / "business_report.xlsx"

    if not path.exists():
        logger.error(
            "Report %s not found; run ml/generate_reports.py",
            path,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The business report is temporarily unavailable",
        )

    return FileResponse(
        path,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        filename="business_report.xlsx",
    )


# ---------------------------------------------------------------------------
# Collaborative filtering recommendation engine
# ---------------------------------------------------------------------------
_rec_engine: dict = {}
_rec_lock = threading.Lock()


def _build_rec_engine() -> dict:
    df = pd.read_csv(
        RETAIL_DATA,
        usecols=["CustomerID", "Description", "Quantity"],
    )

    df["Description"] = df["Description"].str.strip()

    sums = df.groupby(
        ["CustomerID", "Description"],
        as_index=False,
    )["Quantity"].sum()

    cust_codes, customers = pd.factorize(sums["CustomerID"])
    _, products = pd.factorize(sums["Description"])

    product_codes, products = pd.factorize(sums["Description"])

    matrix = csr_matrix(
        (
            sums["Quantity"].to_numpy(dtype=float),
            (cust_codes, product_codes),
        ),
        shape=(len(customers), len(products)),
    )

    return {
        "mtime": RETAIL_DATA.stat().st_mtime,
        "matrix": matrix,
        "normed": normalize(matrix),
        "products": np.asarray(products, dtype=object),
        "row_of": {
            int(customer_id): index
            for index, customer_id in enumerate(customers)
        },
    }


def get_rec_engine() -> dict:
    try:
        mtime = RETAIL_DATA.stat().st_mtime

    except FileNotFoundError:
        logger.error(
            "Recommendation data missing: %s",
            RETAIL_DATA,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation data is temporarily unavailable",
        )

    with _rec_lock:
        if _rec_engine.get("mtime") != mtime:
            _rec_engine.clear()
            _rec_engine.update(_build_rec_engine())

        return _rec_engine


def recommend_products(
    customer_id: int,
    top_n: int = 5,
    n_similar: int = 5,
) -> list[str] | None:
    engine_data = get_rec_engine()
    row = engine_data["row_of"].get(customer_id)

    if row is None:
        return None

    similarity = (
        engine_data["normed"]
        @ engine_data["normed"][row].T
    ).toarray().ravel()

    similarity[row] = -1

    neighbours = np.argsort(
        -similarity,
        kind="stable",
    )[:n_similar]

    score = np.asarray(
        engine_data["matrix"][neighbours].sum(axis=0)
    ).ravel()

    purchased = (
        engine_data["matrix"][row].toarray().ravel() > 0
    )
    score[purchased] = -1

    best = np.argsort(
        -score,
        kind="stable",
    )[:top_n]

    return [
        str(engine_data["products"][index])
        for index in best
        if score[index] > 0
    ]


@app.on_event("startup")
def warm_recommendation_engine():
    def _warm():
        try:
            get_rec_engine()
            logger.info("Recommendation engine ready")
        except Exception:
            logger.exception(
                "Could not warm up the recommendation engine"
            )

    threading.Thread(
        target=_warm,
        daemon=True,
    ).start()


@app.get("/recommendations")
def get_product_recommendations(
    customer_id: int,
    current_product: str | None = None,
    current_user: User = Depends(
        require_role(["owner", "admin", "store_manager"])
    ),
):
    recommendations = recommend_products(customer_id)

    if recommendations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found",
        )

    result = {
        "customer_id": customer_id,
        "recommended_for_you": recommendations,
    }

    if current_product and current_product.strip():
        result["frequently_bought_with"] = cross_sell_for(
            current_product
        )

    return result
