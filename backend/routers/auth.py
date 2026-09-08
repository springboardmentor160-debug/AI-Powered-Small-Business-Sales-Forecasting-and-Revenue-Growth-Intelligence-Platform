from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Staff).filter(models.Staff.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    role_name = user.role.role_name if user.role else "unknown"
    token = create_access_token(data={"sub": user.username, "role": role_name, "outlet_id": user.outlet_id})

    return schemas.Token(
        access_token=token,
        token_type="bearer",
        role=role_name,
        username=user.username,
        outlet_id=user.outlet_id
    )


@router.get("/me", response_model=schemas.StaffOut)
def read_current_user(current_user: models.Staff = Depends(get_current_user)):
    return schemas.StaffOut(
        staff_id=current_user.staff_id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role_id=current_user.role_id,
        outlet_id=current_user.outlet_id,
        is_active=current_user.is_active,
        role_name=current_user.role.role_name if current_user.role else None
    )
