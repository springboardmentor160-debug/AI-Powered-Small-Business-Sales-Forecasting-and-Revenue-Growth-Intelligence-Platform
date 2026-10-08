import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.auth import UserLogin, UserRegister
from backend.services.auth_service import (
    authenticate_user,
    register_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])


@router.post("/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db),
):
    try:
        return register_user(
            db,
            user,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post("/login")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    try:
        return authenticate_user(
            db,
            credentials,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error