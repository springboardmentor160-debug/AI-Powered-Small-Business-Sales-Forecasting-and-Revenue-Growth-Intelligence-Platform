import logging
from fastapi import APIRouter, Depends, HTTPException
from backend.auth import require_role
from backend.services.forecasting_service import (
    load_m5_demand_forecast,
    load_uci_revenue_forecast,
    load_forecast_model_comparison,
)
from backend.config import (
    UCI_ARTIFACT_DIR,
    M5_ARTIFACT_DIR,
)

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/forecast",
    tags=["Forecasting"],
)


@router.get("/demand")
def get_demand_forecast(
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
        "M5 demand forecast requested by %s",
        user["sub"],
    )

    try:
        comparison_path = (
            M5_ARTIFACT_DIR
            / "m5_model_comparison.csv"
        )

        predictions_path = (
            M5_ARTIFACT_DIR
            / "m5_xgboost_predictions.csv"
        )

        result = load_m5_demand_forecast(
            comparison_path,
            predictions_path,
        )

        return {
            "status": "Access Granted",
            "feature": (
                "M5 Item-Store Demand Forecasting"
            ),
            "requested_by": user["sub"],
            **result,
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
            "M5 demand forecast endpoint failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load "
                f"M5 demand forecast: {error}"
            ),
        ) from error
@router.get("/revenue")
def get_revenue_forecast(
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
        "UCI revenue forecast requested by %s",
        user["sub"],
    )

    try:
        comparison_path = (
            UCI_ARTIFACT_DIR
            / "uci_model_comparison.csv"
        )

        predictions_path = (
            UCI_ARTIFACT_DIR
            / "uci_model_comparison_predictions.csv"
        )

        result = load_uci_revenue_forecast(
            comparison_path,
            predictions_path,
        )

        return {
            "status": "Access Granted",
            "feature": (
                "UCI Revenue Forecasting"
            ),
            "requested_by": user["sub"],
            **result,
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
            "UCI revenue forecast endpoint failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load "
                f"UCI revenue forecast: {error}"
            ),

        ) from error
@router.get("/models")
def get_forecast_model_comparison(
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
        "Forecast model comparison requested by %s",
        user["sub"],
    )

    try:
        uci_path = (
            UCI_ARTIFACT_DIR
            / "uci_model_comparison.csv"
        )

        m5_path = (
            M5_ARTIFACT_DIR
            / "m5_model_comparison.csv"
        )

        result = load_forecast_model_comparison(
            uci_path,
            m5_path,
        )

        return {
            "status": "Access Granted",
            **result,
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
            "Forecast model comparison endpoint failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load "
                f"forecast model comparison: {error}"
            ),
        ) from error