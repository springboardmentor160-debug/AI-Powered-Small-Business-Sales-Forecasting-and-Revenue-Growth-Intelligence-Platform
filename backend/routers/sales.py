import logging

from fastapi import APIRouter, Depends

from backend.auth import require_role
from backend.services.sales_service import calculate_sales_analytics


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
)


# Temporary application-state accessor.
# This will be replaced with the database/service repository
# once PostgreSQL + SQLAlchemy is introduced.
def get_cached_sales_analytics() -> dict:
    return


@router.get("/summary")
def sales_summary(
    user: dict = Depends(
        require_role(
            [
                "business_owner",
                "admin",
            ]
        )
    ),
):
    logger.info(
        "Sales summary requested by %s",
        user["sub"],
    )

    analytics = get_cached_sales_analytics()

    return {
        "status": "Access Granted",
        **analytics,
    }