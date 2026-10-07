import logging

from fastapi import APIRouter, Depends, HTTPException

from backend.auth import require_role
from backend.config import SEGMENTATION_ARTIFACT_DIR
from backend.services.segmentation_service import (
    load_customer_segments,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/segments",
    tags=["Segmentation"],
)


@router.get("")
def get_customer_segments(
    user: dict = Depends(
        require_role(
            [
                "business_owner",
                "admin",
                "store_manager",
            ]
        )
    ),
):
    logger.info(
        "Customer segmentation requested by %s",
        user["sub"],
    )

    try:
        segmentation_file = (
            SEGMENTATION_ARTIFACT_DIR
            / "customer_segments_final.csv"
        )

        result = load_customer_segments(
            segmentation_file
        )

        return {
            "status": "Access Granted",
            "feature": (
                "Customer Segmentation "
                "Intelligence"
            ),
            "total_customers": result[
                "total_customers"
            ],
            "segment_count": result[
                "segment_count"
            ],
            "segment_summary": result[
                "segment_summary"
            ],
            "customers": result[
                "customers"
            ],
        }

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Segmentation endpoint failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load "
                f"segmentation results: {error}"
            ),
        ) from error