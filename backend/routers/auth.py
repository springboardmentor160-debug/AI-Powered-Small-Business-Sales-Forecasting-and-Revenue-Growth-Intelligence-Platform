import logging

from fastapi import APIRouter, HTTPException

from backend.schemas.auth import UserLogin, UserRegister
from backend.services.auth_service import (
    authenticate_user,
    register_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Authentication"],
)


@router.post("/register")
def register(
    user: UserRegister,
):
    try:
        return register_user(user)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post("/login")
def login(
    credentials: UserLogin,
):
    try:
        return authenticate_user(credentials)

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error