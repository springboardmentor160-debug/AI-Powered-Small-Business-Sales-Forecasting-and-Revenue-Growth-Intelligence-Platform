from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import SalesTransaction, User

security = HTTPBearer()

SECRET_KEY = "change-this-secret-in-production"
ALGORITHM = "HS256"


app = FastAPI(title="MarketMind AI API")


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/")
def home():
    return {"message": "MarketMind AI backend is running"}


@app.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter(User.username == data.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    password_hash = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user = User(
        username=data.username,
        password_hash=password_hash,
        role="viewer",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "username": user.username,
        "role": user.role,
    }


@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.username == data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    password_ok = bcrypt.checkpw(
        data.password.encode("utf-8"),
        user.password_hash.encode("utf-8")
    )

    if not password_ok:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    token = jwt.encode(
        {
            "sub": user.username,
            "role": user.role,
            "exp": expires_at,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/sales")
def get_sales(db: Session = Depends(get_db)):
    rows = (
        db.query(SalesTransaction)
        .order_by(SalesTransaction.invoice_date.desc())
        .limit(10000)
        .all()
    )

    return [
        {
            "id": row.id,
            "invoice_id": row.invoice_id,
            "product_id": row.product_id,
            "customer_id": row.customer_id,
            "quantity": row.quantity,
            "unit_price": float(row.unit_price),
            "invoice_date": (
                row.invoice_date.isoformat()
                if row.invoice_date
                else None
            ),
            "sales_amount": float(row.sales_amount),
        }
        for row in rows
    ]
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        role = payload.get("role")

        if not username or not role:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return {
            "username": username,
            "role": role
        }

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
def require_roles(allowed_roles):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        return current_user

    return role_checker
@app.get("/admin")
def admin_page(
    current_user=Depends(require_roles(["admin"]))
):
    return {
        "message": "Welcome Admin",
        "user": current_user
    }


@app.get("/analytics")
def analytics_page(
    current_user=Depends(require_roles(["admin", "manager", "analyst"]))
):
    return {
        "message": "Welcome to Analytics",
        "user": current_user
    }


@app.get("/reports")
def reports_page(
    current_user=Depends(require_roles(["admin", "manager"]))
):
    return {
        "message": "Welcome to Reports",
        "user": current_user
    }


@app.get("/dashboard")
def dashboard_page(
    current_user=Depends(
        require_roles(["admin", "manager", "analyst", "viewer"])
    )
):
    return {
        "message": "Welcome to Dashboard",
        "user": current_user
    }