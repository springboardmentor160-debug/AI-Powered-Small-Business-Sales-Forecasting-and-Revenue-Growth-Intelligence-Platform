"""Authentication and initial MarketMind summary routes."""

import logging
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
from backend.services.reporting_service import get_revenue_forecast_report, get_segments_report


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")
reporting_router = APIRouter()


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


def _call_service(service: Any, service_name: str) -> Any:
    """Translate known data failures while keeping implementation details in logs."""
    try:
        return service()
    except FileNotFoundError as error:
        logger.error("%s data file is unavailable: %s", service_name, error)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name} data is currently unavailable.",
        ) from error
    except (ValueError, KeyError) as error:
        logger.error("%s data is invalid or empty: %s", service_name, error)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name} data is currently unavailable.",
        ) from error
    except Exception:
        logger.exception("Unexpected error while loading %s data.", service_name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The requested data could not be loaded.",
        ) from None


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
) -> dict[str, Any]:
    """Return aggregate sales metrics from processed data."""
    return _call_service(get_sales_summary, "Sales")


@router.get("/inventory/summary")
def inventory_summary(
    _: dict[str, Any] = Depends(
        require_roles(
            ROLE_BUSINESS_OWNER,
            ROLE_STORE_MANAGER,
            ROLE_SYSTEM_ADMINISTRATOR,
        )
    ),
) -> dict[str, Any]:
    """Return aggregate inventory metrics from processed data."""
    return _call_service(get_inventory_summary, "Inventory")


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
) -> dict[str, Any]:
    """Return aggregate customer metrics from processed data."""
    return _call_service(get_customer_summary, "Customer")


@router.get("/segments")
@reporting_router.get("/segments")
def segments_report(
    _: dict[str, Any] = Depends(
        require_roles(
            ROLE_BUSINESS_OWNER,
            ROLE_STORE_MANAGER,
            ROLE_SALES_EXECUTIVE,
            ROLE_SYSTEM_ADMINISTRATOR,
        )
    ),
) -> dict[str, Any]:
    """Return actual generated customer segment summaries."""
    return _call_service(get_segments_report, "Segmentation")


@router.get("/forecast/revenue")
@reporting_router.get("/forecast/revenue")
def revenue_forecast_report(
    _: dict[str, Any] = Depends(
        require_roles(
            ROLE_BUSINESS_OWNER,
            ROLE_STORE_MANAGER,
            ROLE_SYSTEM_ADMINISTRATOR,
        )
    ),
) -> dict[str, Any]:
    """Return actual generated revenue forecasts and model comparison results."""
    return _call_service(get_revenue_forecast_report, "Forecast")
