from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel
from database import engine
from models import User, SalesTransaction, Transaction, Customer
from schemas import UserCreate,UserOut ,UserMeOut ,UserLogin, SalesTransactionOut, TransactionOut
from auth import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    u = User(
        name = user.name,
        email = user.email,
        role_id = user.role_id,
        hashed_password = hashed_password
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@app.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user login",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(allowed_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        role_name_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong user",
            headers={"WW-Authenticate":"Bearer"},
        )
        if current_user.role.name not in allowed_roles: 
            raise role_name_exception

        return current_user
    return role_checker

@app.get("/admin-only")
def admin_only_route(current_user: User = Depends(require_role(["admin"]))):
    return {"message" : f"Welcome {current_user.name}, you are an admin"}

@app.get("/sales-transactions",response_model=list[SalesTransactionOut])
def get_sales_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["owner", "store_manager", "admin"]))
):
    return db.query(SalesTransaction).limit(50).all()


@app.get("/transactions", response_model=list[TransactionOut])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["owner", "admin", "sales_exec"])
    )
):
    query = db.query(Transaction)

    if current_user.role.name == "sales_exec":
        query = (
            query
            .join(
                Customer,
                Transaction.customer_id == Customer.customer_id
            )
            .filter(Customer.assigned_rep_id == current_user.id)
        )

    return query.limit(50).all()

@app.get("/sales/summary")
def sales_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["owner", "store_manager", "admin"]))
):
    total_units_sold = db.query(func.sum(SalesTransaction.units_sold)).scalar()
    total_inventory = db.query(func.sum(SalesTransaction.inventory_level)).scalar()
    low_stock_count = db.query(SalesTransaction).filter(SalesTransaction.inventory_level < 100).count()

    return {
        "total_units_sold": total_units_sold,
        "total_inventory": total_inventory,
        "low_stock_count": low_stock_count
    }

@app.get("/me", response_model=UserMeOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserMeOut(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.name
    )
