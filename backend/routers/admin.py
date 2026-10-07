import logging

from fastapi import APIRouter, Depends

from backend.auth import require_role
from backend.services.user_service import fake_users_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
)
@router.get("/users")
def list_users(
    user: dict = Depends(
        require_role(["admin"])
    ),
):
    return {
        "status": "Access Granted",
        "feature": (
            "System User Directory "
            "Management"
        ),
        "registered_user_profiles": list(
            fake_users_db.keys()
        ),
    }