import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth import require_role
from backend.database import get_db
from backend.config import (
    UCI_FILE_1,
    UCI_FILE_2,
)
from backend.services.inventory_service import (
    generate_inventory_preview,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.get("/preview")
def inventory_preview(
    db: Session = Depends(get_db),
    user: dict = Depends(
        require_role(
            [
                "business_owner",
                "admin",
                "store_manager",
                "sales_executive",
            ]
        )
    ),
):
    try:
        result = generate_inventory_preview(db)

        return {
            "message": (
                "Inventory preview generated"
            ),
            "source_files": [
                UCI_FILE_1.name,
                UCI_FILE_2.name,
            ],
            "inventory_method": (
                "Estimated InitialStock = "
                "TotalUnitsSold × 1.5"
            ),
            "note": (
                "This is estimated inventory, "
                "not verified physical stock."
            ),
            **result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Inventory preview failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Inventory preview failed: "
                f"{error}"
            ),
        ) from error