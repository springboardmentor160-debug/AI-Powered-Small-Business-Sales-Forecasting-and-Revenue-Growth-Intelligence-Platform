from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from database import engine, Base, SessionLocal
import models


# ==================================================
# DATABASE
# ==================================================

Base.metadata.create_all(bind=engine)


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(title="MarketMind AI")


# ==================================================
# CORS
# ==================================================

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


# ==================================================
# AUTHENTICATION CONFIGURATION
# ==================================================

SECRET_KEY = "marketmind-ai-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

security = HTTPBearer()


ALLOWED_ROLES = [
    "business_owner",
    "store_manager",
    "sales_executive",
    "admin"
]


# ==================================================
# PYDANTIC AUTH MODELS
# ==================================================

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class InvoiceCreate(BaseModel):
    sale_id: int
    amount: float
    payment_status: str = "pending"


# ==================================================
# DATABASE DEPENDENCY
# ==================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==================================================
# PASSWORD HELPERS
# ==================================================

def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def get_password_hash(password: str):
    return pwd_context.hash(password)


# ==================================================
# JWT HELPERS
# ==================================================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==================================================
# CURRENT USER
# ==================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if user is None:
        raise credentials_exception

    return user


# ==================================================
# ROLE-BASED ACCESS CONTROL
# ==================================================

def require_role(allowed_roles: list[str]):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )
        return current_user

    return role_checker


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():
    return {
        "message": "MarketMind AI API is running"
    }


# ==================================================
# REGISTER
# ==================================================

@app.post("/register")
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):

    if user_data.role not in ALLOWED_ROLES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid role. Choose one of: "
                "business_owner, store_manager, "
                "sales_executive, admin"
            )
        )

    existing_user = db.query(
        models.User
    ).filter(
        models.User.email == user_data.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(
        user_data.password
    )

    new_user = models.User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }


# ==================================================
# LOGIN
# ==================================================

@app.post("/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):

    user = db.query(
        models.User
    ).filter(
        models.User.email == user_data.email
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user_data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }


# ==================================================
# CURRENT USER
# ==================================================

@app.get("/auth/me")
def auth_me(
    current_user: dict = Depends(get_current_user)
):
    return current_user


# ==================================================
# SALES SUMMARY
# All authenticated roles can view
# ==================================================

@app.get("/sales/summary")
def sales_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    total_orders = db.query(
        func.count(models.Sale.id)
    ).scalar()

    total_quantity = db.query(
        func.sum(models.Sale.quantity)
    ).scalar()

    return {
        "total_orders": total_orders or 0,
        "total_quantity": total_quantity or 0
    }


# ==================================================
# SALES TRENDS
# ==================================================

@app.get("/sales/trends")
def sales_trends(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = db.query(
        models.Sale.sale_date,
        func.sum(
            models.Sale.quantity
        ).label("quantity")
    ).group_by(
        models.Sale.sale_date
    ).order_by(
        models.Sale.sale_date
    ).all()

    return [
        {
            "date": str(row.sale_date),
            "quantity": row.quantity
        }
        for row in results
    ]


# ==================================================
# REVENUE SUMMARY
# ==================================================

@app.get("/sales/revenue")
def sales_revenue(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    total_revenue = db.query(
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        )
    ).join(
        models.Product,
        models.Sale.product_id == models.Product.id
    ).scalar()

    return {
        "total_revenue": round(
            total_revenue or 0,
            2
        )
    }


# ==================================================
# REVENUE TRENDS
# ==================================================

@app.get("/sales/revenue/trends")
def revenue_trends(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = db.query(
        models.Sale.sale_date,
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).label("revenue")
    ).join(
        models.Product,
        models.Sale.product_id == models.Product.id
    ).group_by(
        models.Sale.sale_date
    ).order_by(
        models.Sale.sale_date
    ).all()

    return [
        {
            "date": str(row.sale_date),
            "revenue": round(
                row.revenue or 0,
                2
            )
        }
        for row in results
    ]


# ==================================================
# TOP PRODUCTS BY QUANTITY
# ==================================================

@app.get("/products/top")
def top_products(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = db.query(
        models.Product.id,
        models.Product.name,
        func.sum(
            models.Sale.quantity
        ).label("quantity_sold")
    ).join(
        models.Sale,
        models.Product.id == models.Sale.product_id
    ).group_by(
        models.Product.id,
        models.Product.name
    ).order_by(
        func.sum(
            models.Sale.quantity
        ).desc()
    ).limit(10).all()

    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "quantity_sold": row.quantity_sold
        }
        for row in results
    ]


# ==================================================
# TOP PRODUCTS BY REVENUE
# ==================================================

@app.get("/products/top-revenue")
def top_products_revenue(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = db.query(
        models.Product.id,
        models.Product.name,
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).label("revenue")
    ).join(
        models.Sale,
        models.Product.id == models.Sale.product_id
    ).group_by(
        models.Product.id,
        models.Product.name
    ).order_by(
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).desc()
    ).limit(10).all()

    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "revenue": round(
                row.revenue or 0,
                2
            )
        }
        for row in results
    ]


# ==================================================
# TOP CUSTOMERS BY QUANTITY
# ==================================================

@app.get("/customers/top")
def top_customers(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = db.query(
        models.Customer.customer_id,
        models.Customer.name,
        func.sum(
            models.Sale.quantity
        ).label("quantity_purchased")
    ).join(
        models.Sale,
        models.Customer.id == models.Sale.customer_id
    ).group_by(
        models.Customer.customer_id,
        models.Customer.name
    ).order_by(
        func.sum(
            models.Sale.quantity
        ).desc()
    ).limit(10).all()

    return [
        {
            "customer_id": row.customer_id,
            "customer_name": row.name,
            "quantity_purchased": row.quantity_purchased
        }
        for row in results
    ]


# ==================================================
# TOP CUSTOMERS BY REVENUE
# ==================================================

@app.get("/customers/top-revenue")
def top_customers_revenue(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = db.query(
        models.Customer.customer_id,
        models.Customer.name,
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).label("revenue")
    ).join(
        models.Sale,
        models.Customer.id == models.Sale.customer_id
    ).join(
        models.Product,
        models.Sale.product_id == models.Product.id
    ).group_by(
        models.Customer.customer_id,
        models.Customer.name
    ).order_by(
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).desc()
    ).limit(10).all()

    return [
        {
            "customer_id": row.customer_id,
            "customer_name": row.name,
            "revenue": round(
                row.revenue or 0,
                2
            )
        }
        for row in results
    ]


# ==================================================
# LOW STOCK PRODUCTS
# ==================================================

@app.get("/inventory/low-stock")
def low_stock_products(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = db.query(
        models.Product.id,
        models.Product.name,
        models.Inventory.stock_level,
        models.Inventory.reorder_point
    ).join(
        models.Inventory,
        models.Product.id == models.Inventory.product_id
    ).filter(
        models.Inventory.stock_level <=
        models.Inventory.reorder_point
    ).order_by(
        models.Inventory.stock_level.asc()
    ).all()

    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "stock_level": row.stock_level,
            "reorder_point": row.reorder_point
        }
        for row in results
    ]


# ==================================================
# INVENTORY SUMMARY
# ==================================================

@app.get("/inventory/summary")
def inventory_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    total_products = db.query(
        func.count(models.Inventory.id)
    ).scalar()

    total_stock = db.query(
        func.sum(models.Inventory.stock_level)
    ).scalar()

    low_stock = db.query(
        func.count(models.Inventory.id)
    ).filter(
        models.Inventory.stock_level <=
        models.Inventory.reorder_point
    ).scalar()

    return {
        "total_products": total_products or 0,
        "total_stock_units": total_stock or 0,
        "low_stock_products": low_stock or 0
    }


# ==================================================
# SALES BY COUNTRY
# ==================================================

@app.get("/sales/countries")
def sales_by_country(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = db.query(
        models.Sale.country,
        func.sum(
            models.Sale.quantity
        ).label("quantity_sold")
    ).filter(
        models.Sale.country.isnot(None)
    ).group_by(
        models.Sale.country
    ).order_by(
        func.sum(
            models.Sale.quantity
        ).desc()
    ).all()

    return [
        {
            "country": row.country,
            "quantity_sold": row.quantity_sold
        }
        for row in results
    ]


# ==================================================
# REVENUE BY COUNTRY
# ==================================================

@app.get("/sales/countries/revenue")
def revenue_by_country(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = db.query(
        models.Sale.country,
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).label("revenue")
    ).join(
        models.Product,
        models.Sale.product_id == models.Product.id
    ).filter(
        models.Sale.country.isnot(None)
    ).group_by(
        models.Sale.country
    ).order_by(
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).desc()
    ).all()

    return [
        {
            "country": row.country,
            "revenue": round(
                row.revenue or 0,
                2
            )
        }
        for row in results
    ]


# ==================================================
# PRODUCT PERFORMANCE
# ==================================================

@app.get("/products/performance")
def product_performance(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    results = db.query(
        models.Product.id,
        models.Product.name,
        func.sum(
            models.Sale.quantity
        ).label("quantity_sold"),
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).label("revenue")
    ).join(
        models.Sale,
        models.Product.id == models.Sale.product_id
    ).group_by(
        models.Product.id,
        models.Product.name
    ).order_by(
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).desc()
    ).all()

    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "quantity_sold": row.quantity_sold,
            "revenue": round(
                row.revenue or 0,
                2
            )
        }
        for row in results
    ]


# ==================================================
# AI INSIGHTS OVERVIEW
# ==================================================

@app.get("/insights/overview")
def insights_overview(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    total_revenue = db.query(
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        )
    ).join(
        models.Product,
        models.Sale.product_id == models.Product.id
    ).scalar()

    total_quantity = db.query(
        func.sum(models.Sale.quantity)
    ).scalar()

    best_product = db.query(
        models.Product.name,
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).label("revenue")
    ).join(
        models.Sale,
        models.Product.id == models.Sale.product_id
    ).group_by(
        models.Product.id,
        models.Product.name
    ).order_by(
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).desc()
    ).first()

    top_customer = db.query(
        models.Customer.customer_id,
        models.Customer.name,
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).label("revenue")
    ).join(
        models.Sale,
        models.Customer.id == models.Sale.customer_id
    ).join(
        models.Product,
        models.Sale.product_id == models.Product.id
    ).group_by(
        models.Customer.id,
        models.Customer.customer_id,
        models.Customer.name
    ).order_by(
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).desc()
    ).first()

    best_country = db.query(
        models.Sale.country,
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).label("revenue")
    ).join(
        models.Product,
        models.Sale.product_id == models.Product.id
    ).filter(
        models.Sale.country.isnot(None)
    ).group_by(
        models.Sale.country
    ).order_by(
        func.sum(
            models.Sale.quantity *
            models.Product.unit_price
        ).desc()
    ).first()

    low_stock = db.query(
        func.count(models.Inventory.id)
    ).filter(
        models.Inventory.stock_level <=
        models.Inventory.reorder_point
    ).scalar()

    return {
        "total_revenue": round(
            total_revenue or 0,
            2
        ),
        "total_units_sold": total_quantity or 0,

        "best_product": (
            {
                "product_name": best_product.name,
                "revenue": round(
                    best_product.revenue or 0,
                    2
                )
            }
            if best_product else None
        ),

        "top_customer": (
            {
                "customer_id": top_customer.customer_id,
                "customer_name": top_customer.name,
                "revenue": round(
                    top_customer.revenue or 0,
                    2
                )
            }
            if top_customer else None
        ),

        "best_country": (
            {
                "country": best_country.country,
                "revenue": round(
                    best_country.revenue or 0,
                    2
                )
            }
            if best_country else None
        ),

        "low_stock_products": low_stock or 0
    }


# ==================================================
# FORECAST ACCESS TEST
# Business Owner / Store Manager / Admin
# ==================================================

@app.get("/forecast/revenue")
def revenue_forecast_access(
    current_user: dict = Depends(
        require_role([
            "business_owner",
            "store_manager",
            "admin"
        ])
    )
):

    return {
        "message": "Revenue forecasting access granted",
        "requested_by": current_user["email"],
        "role": current_user["role"],
        "forecast": "Forecasting module will be implemented in Milestone 2"
    }


# ==================================================
# INVOICE MANAGEMENT
# ==================================================

@app.get("/invoices")
def get_invoices(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    invoices = db.query(
        models.Invoice
    ).all()

    return [
        {
            "id": invoice.id,
            "sale_id": invoice.sale_id,
            "amount": invoice.amount,
            "payment_status": invoice.payment_status
        }
        for invoice in invoices
    ]


@app.post("/invoices")
def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: dict = Depends(
        require_role([
            "sales_executive",
            "admin"
        ])
    ),
    db: Session = Depends(get_db)
):

    sale = db.query(
        models.Sale
    ).filter(
        models.Sale.id == invoice_data.sale_id
    ).first()

    if not sale:

        raise HTTPException(
            status_code=404,
            detail="Sale not found"
        )

    invoice = models.Invoice(
        sale_id=invoice_data.sale_id,
        amount=invoice_data.amount,
        payment_status=invoice_data.payment_status
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return {
        "message": "Invoice created successfully",
        "invoice": {
            "id": invoice.id,
            "sale_id": invoice.sale_id,
            "amount": invoice.amount,
            "payment_status": invoice.payment_status
        },
        "created_by": current_user["email"]
    }


# ==================================================
# ADMIN USER MANAGEMENT
# ==================================================

@app.get("/admin/users")
def list_users(
    current_user: dict = Depends(
        require_role(["admin"])
    ),
    db: Session = Depends(get_db)
):

    users = db.query(
        models.User
    ).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]