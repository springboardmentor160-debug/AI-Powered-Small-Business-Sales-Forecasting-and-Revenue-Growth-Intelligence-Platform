"""Authentication and initial MarketMind summary routes."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from .auth import (
    ROLE_BUSINESS_OWNER,
    ROLE_SALES_EXECUTIVE,
    ROLE_STORE_MANAGER,
    ROLE_SYSTEM_ADMINISTRATOR,
    authenticate_user,
    create_access_token,
    get_current_user,
    require_roles,
)
from .services import get_customer_summary, get_inventory_summary, get_sales_summary


router = APIRouter(prefix="/api")


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


@router.post("/auth/login")
def login(credentials: LoginRequest) -> dict[str, Any]:
    """Authenticate a user and return a signed access token."""
    user = authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": user,
    }


@router.post("/auth/logout")
def logout(_: dict[str, Any] = Depends(get_current_user)) -> dict[str, str]:
    """Acknowledge logout; the client removes its short-lived JWT."""
    return {"message": "Logged out successfully."}


@router.get("/auth/me")
def current_user(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    """Return the authenticated user's safe profile."""
    return current_user


@router.get("/sales/summary")
def sales_summary(
    _: dict[str, Any] = Depends(
        require_roles(
            ROLE_BUSINESS_OWNER,
            ROLE_STORE_MANAGER,
            ROLE_SYSTEM_ADMINISTRATOR,
        )
    ),
) -> dict:
    """Return aggregate sales metrics from processed data."""
    return get_sales_summary()


@router.get("/inventory/summary")
def inventory_summary(
    _: dict[str, Any] = Depends(
        require_roles(
            ROLE_BUSINESS_OWNER,
            ROLE_STORE_MANAGER,
            ROLE_SYSTEM_ADMINISTRATOR,
        )
    ),
) -> dict:
    """Return aggregate inventory metrics from processed data."""
    return get_inventory_summary()


@router.get("/customers/summary")
def customer_summary(
    _: dict[str, Any] = Depends(
        require_roles(
            ROLE_BUSINESS_OWNER,
            ROLE_STORE_MANAGER,
            ROLE_SALES_EXECUTIVE,
            ROLE_SYSTEM_ADMINISTRATOR,
        )
    ),
) -> dict:
    """Return aggregate customer metrics from processed data."""
    return get_customer_summary()
