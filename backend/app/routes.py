"""Authentication and initial MarketMind summary routes."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, StreamingResponse
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
from .services import (
    get_customer_summary,
    get_inventory_summary,
    get_low_stock_inventory,
    get_sales_summary,
)
from backend.services.anomaly_service import get_sales_anomaly_alerts
from backend.services.churn_comparison_service import get_churn_predictions
from backend.services.invoice_service import (
    InvoiceConflictError,
    InvoiceNotFoundError,
    InvoiceValidationError,
    build_invoice_workbook,
    create_invoice,
    get_invoice,
    list_invoices,
)
from backend.services.recommendation_service import get_customer_recommendations
from backend.services.reporting_service import (
    REPORT_PATH,
    generate_excel_report,
    get_revenue_forecast_report,
    get_segments_report,
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")
reporting_router = APIRouter()


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class InvoiceCreateRequest(BaseModel):
    transaction_id: str = Field(min_length=1, max_length=30)


def _call_service(
    service: Any,
    service_name: str,
    not_found_detail: str | None = None,
) -> Any:
    """Translate known data failures while keeping implementation details in logs."""
    try:
        return service()
    except FileNotFoundError as error:
        logger.error("%s data file is unavailable: %s", service_name, error)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name} data is currently unavailable.",
        ) from error
    except KeyError as error:
        if not_found_detail is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=not_found_detail,
            ) from error
        logger.error("%s data is invalid or empty: %s", service_name, error)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name} data is currently unavailable.",
        ) from error
    except ValueError as error:
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


def _call_invoice_service(service: Any, service_name: str) -> Any:
    """Translate invoice failures without exposing implementation details."""
    try:
        return service()
    except InvoiceConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except InvoiceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except InvoiceValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    except (FileNotFoundError, ValueError) as error:
        logger.error("%s data is unavailable or invalid: %s", service_name, error)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name} data is currently unavailable.",
        ) from error
    except Exception:
        logger.exception("Unexpected error while loading %s data.", service_name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The requested invoice data could not be loaded.",
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


@router.get("/inventory/low-stock")
def low_stock_inventory(
    _: dict[str, Any] = Depends(
        require_roles(
            ROLE_BUSINESS_OWNER,
            ROLE_STORE_MANAGER,
            ROLE_SYSTEM_ADMINISTRATOR,
        )
    ),
) -> dict[str, Any]:
    """Return product/store inventory records needing replenishment review."""
    return _call_service(get_low_stock_inventory, "Inventory")


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


def _get_excel_report_path() -> Any:
    """Return the existing workbook, generating it from validated outputs if absent."""
    if not REPORT_PATH.exists():
        return generate_excel_report()
    return REPORT_PATH


@router.get("/reports/excel")
def download_excel_report(
    _: dict[str, Any] = Depends(
        require_roles(
            ROLE_BUSINESS_OWNER,
            ROLE_STORE_MANAGER,
            ROLE_SYSTEM_ADMINISTRATOR,
        )
    ),
) -> FileResponse:
    """Download the existing protected business reporting workbook."""
    report_path = _call_service(_get_excel_report_path, "Business report")
    return FileResponse(
        path=report_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=REPORT_PATH.name,
    )


@router.post("/invoices", status_code=status.HTTP_201_CREATED)
def create_invoice_endpoint(
    request: InvoiceCreateRequest,
    current_user: dict[str, Any] = Depends(
        require_roles(ROLE_BUSINESS_OWNER, ROLE_SYSTEM_ADMINISTRATOR)
    ),
) -> dict[str, Any]:
    """Create one invoice snapshot for an explicitly selected transaction."""
    invoice = _call_invoice_service(
        lambda: create_invoice(
            request.transaction_id,
            created_by_user_id=int(current_user["user_id"]),
        ),
        "Invoice",
    )
    return {"invoice": invoice}


@router.get("/invoices")
def invoices(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: dict[str, Any] = Depends(
        require_roles(ROLE_BUSINESS_OWNER, ROLE_SYSTEM_ADMINISTRATOR)
    ),
) -> dict[str, Any]:
    """List persisted invoice snapshots."""
    invoice_records = _call_invoice_service(
        lambda: list_invoices(limit=limit, offset=offset),
        "Invoice",
    )
    return {
        "invoices": invoice_records,
        "count": len(invoice_records),
        "limit": limit,
        "offset": offset,
    }


@router.get("/invoices/{invoice_id}/download")
def download_invoice(
    invoice_id: int,
    _: dict[str, Any] = Depends(
        require_roles(ROLE_BUSINESS_OWNER, ROLE_SYSTEM_ADMINISTRATOR)
    ),
) -> StreamingResponse:
    """Download a workbook generated from one persisted invoice snapshot."""
    invoice = _call_invoice_service(lambda: get_invoice(invoice_id), "Invoice")
    workbook = build_invoice_workbook(invoice)
    return StreamingResponse(
        workbook,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{invoice["invoice_number"]}.xlsx"'
            )
        },
    )


@router.get("/invoices/{invoice_id}")
def invoice_detail(
    invoice_id: int,
    _: dict[str, Any] = Depends(
        require_roles(ROLE_BUSINESS_OWNER, ROLE_SYSTEM_ADMINISTRATOR)
    ),
) -> dict[str, Any]:
    """Return one persisted invoice snapshot."""
    return {"invoice": _call_invoice_service(lambda: get_invoice(invoice_id), "Invoice")}


@router.get("/recommendations/{customer_id}")
def customer_recommendations(
    customer_id: str,
    top_n: int = Query(default=3, ge=1, le=20),
    _: dict[str, Any] = Depends(
        require_roles(
            ROLE_BUSINESS_OWNER,
            ROLE_STORE_MANAGER,
            ROLE_SALES_EXECUTIVE,
            ROLE_SYSTEM_ADMINISTRATOR,
        )
    ),
) -> dict[str, Any]:
    """Return existing personalized recommendations for one customer."""
    normalized_customer_id = customer_id.strip()
    if not normalized_customer_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="customer_id must not be empty.",
        )
    recommendations = _call_service(
        lambda: get_customer_recommendations(normalized_customer_id, top_n=top_n),
        "Recommendation",
        not_found_detail="Customer not found.",
    )
    return {
        "customer_id": normalized_customer_id,
        "recommendations": recommendations,
    }


@router.get("/churn")
def churn_predictions(
    customer_id: str | None = Query(default=None),
    _: dict[str, Any] = Depends(
        require_roles(
            ROLE_BUSINESS_OWNER,
            ROLE_STORE_MANAGER,
            ROLE_SALES_EXECUTIVE,
            ROLE_SYSTEM_ADMINISTRATOR,
        )
    ),
) -> dict[str, Any]:
    """Return persisted churn risk predictions with their validation limitation."""
    return _call_service(lambda: get_churn_predictions(customer_id), "Churn")


@router.get("/anomalies")
def sales_anomalies(
    _: dict[str, Any] = Depends(
        require_roles(
            ROLE_BUSINESS_OWNER,
            ROLE_STORE_MANAGER,
            ROLE_SYSTEM_ADMINISTRATOR,
        )
    ),
) -> dict[str, Any]:
    """Return persisted Sales anomaly alerts as review indicators."""
    return _call_service(get_sales_anomaly_alerts, "Anomaly")
