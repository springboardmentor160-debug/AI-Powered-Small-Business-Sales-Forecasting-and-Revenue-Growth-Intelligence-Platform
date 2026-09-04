from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas
from auth import RoleChecker, get_password_hash

router = APIRouter(prefix="/api/v1/users", tags=["Users Admin"])
admin_only = RoleChecker(["administrator"])

@router.get("/", response_model=List[schemas.UserOut], dependencies=[Depends(admin_only)])
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    res = []
    for u in users:
        res.append(schemas.UserOut(
            user_id=u.user_id,
            username=u.username,
            email=u.email,
            full_name=u.full_name,
            role_id=u.role_id,
            store_id=u.store_id,
            is_active=u.is_active,
            role_name=u.role.role_name if u.role else None
        ))
    return res

@router.post("/", response_model=schemas.UserOut, dependencies=[Depends(admin_only)])
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        (models.User.username == user_in.username) | (models.User.email == user_in.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    role = db.query(models.Role).filter(models.Role.role_id == user_in.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role ID not found")

    new_u = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role_id=user_in.role_id,
        store_id=user_in.store_id
    )
    db.add(new_u)
    db.commit()
    db.refresh(new_u)

    return schemas.UserOut(
        user_id=new_u.user_id,
        username=new_u.username,
        email=new_u.email,
        full_name=new_u.full_name,
        role_id=new_u.role_id,
        store_id=new_u.store_id,
        is_active=new_u.is_active,
        role_name=role.role_name
    )
