"""Password hashing (bcrypt), JWT creation/verification and the Access Matrix as code."""
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import models
from config import ACCESS_TOKEN_EXPIRE_HOURS, SECRET_KEY
from database import get_db

ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)

OWNER, MANAGER, SALES, ADMIN = "business_owner", "store_manager", "sales_executive", "admin"
ROLES = (OWNER, MANAGER, SALES, ADMIN)

# Access Matrix. Forecast / invoice / user-management rows follow the matrix quoted in the project guide;
# the others are assumptions - edit this one dict to change who can see what.
ACCESS = {
    "sales_summary":    (OWNER, MANAGER, SALES, ADMIN),
    "inventory_alerts": (OWNER, MANAGER, ADMIN),
    "segments":         (OWNER, MANAGER, SALES, ADMIN),
    "recommendations":  (OWNER, MANAGER, SALES, ADMIN),
    "churn":            (OWNER, MANAGER, SALES, ADMIN),
    "anomalies":        (OWNER, MANAGER, ADMIN),
    "forecast":         (OWNER, MANAGER, ADMIN),            # Owner yes, Manager view, Sales Exec NO, Admin yes
    "report_download":  (OWNER, MANAGER, ADMIN),
    "invoice_view":     (OWNER, MANAGER, SALES, ADMIN),     # Owner/Manager view
    "invoice_create":   (SALES, ADMIN),                      # Sales Exec + Admin create / update
    "user_management":  (ADMIN,),                            # Admin only
    "model_performance": (OWNER, MANAGER, ADMIN),            # Milestone 4 evaluation dashboard
}


def hash_password(p: str) -> str:
    # bcrypt only looks at the first 72 bytes; truncate explicitly so newer bcrypt versions never raise
    return bcrypt.hashpw(p.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(email: str, role: str, name: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": email, "role": role, "name": name, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> dict:
    """Validate the JWT, then re-read the user so deleted users and role changes take effect immediately."""
    if creds is None:
        raise HTTPException(401, "Not authenticated", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Invalid or expired token - please log in again", headers={"WWW-Authenticate": "Bearer"})
    email = payload.get("sub")
    try:
        u = db.query(models.User).filter(models.User.email == email).first()
    except SQLAlchemyError:
        raise HTTPException(503, "Database is temporarily unavailable")
    if u is None:
        raise HTTPException(401, "This account no longer exists - please log in again", headers={"WWW-Authenticate": "Bearer"})
    return {"sub": u.email, "role": u.role.name, "name": u.name, "id": u.id}


def require_access(feature: str):
    allowed = ACCESS[feature]

    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in allowed:
            raise HTTPException(403, "You do not have permission to access this")
        return user
    return checker
