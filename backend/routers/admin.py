import logging

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.auth import require_role
from backend.database import get_db
from backend.models.user import User
from backend.schemas.admin import AdminUserCreate, AdminUserUpdate
from backend.services.auth_service import ALLOWED_ROLES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Administration"])

admin_only = Depends(require_role(["admin"]))


def _serialize(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _get_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


def _check_role(role: str) -> None:
    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role.")


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A user with this name or email already exists.",
        ) from error


@router.get("/users")
def list_users(db: Session = Depends(get_db), admin: dict = admin_only):
    users = db.scalars(select(User).order_by(User.id)).all()
    return {
        "status": "Access Granted",
        "feature": "System User Directory Management",
        "registered_user_profiles": [u.email for u in users],
        "users": [_serialize(u) for u in users],
    }


@router.post("/users", status_code=201)
def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    admin: dict = admin_only,
):
    _check_role(payload.role)
    user = User(
        username=payload.name.strip(),
        email=str(payload.email).lower().strip(),
        hashed_password=_hash(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    _commit(db)
    db.refresh(user)
    logger.info("Admin %s created user %s", admin["sub"], user.email)
    return {"message": "User created.", "user": _serialize(user)}


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: dict = admin_only,
):
    user = _get_or_404(db, user_id)
    is_self = user.email == admin["sub"]

    if payload.role is not None:
        _check_role(payload.role)
        if is_self and payload.role != "admin":
            raise HTTPException(status_code=400, detail="You cannot remove your own admin role.")
        user.role = payload.role
    if payload.is_active is not None:
        if is_self and not payload.is_active:
            raise HTTPException(status_code=400, detail="You cannot deactivate your own account.")
        user.is_active = payload.is_active
    if payload.name is not None:
        user.username = payload.name.strip()
    if payload.email is not None:
        user.email = str(payload.email).lower().strip()
    if payload.password:
        user.hashed_password = _hash(payload.password)

    _commit(db)
    db.refresh(user)
    logger.info("Admin %s updated user %s", admin["sub"], user.email)
    return {"message": "User updated.", "user": _serialize(user)}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: dict = admin_only,
):
    user = _get_or_404(db, user_id)
    if user.email == admin["sub"]:
        raise HTTPException(status_code=400, detail="You cannot delete your own account.")
    db.delete(user)
    _commit(db)
    logger.info("Admin %s deleted user %s", admin["sub"], user.email)
    return {"message": "User deleted."}
