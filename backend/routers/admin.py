import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.auth import require_role
from backend.database import get_db
from backend.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
)


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    user: dict = Depends(
        require_role(["admin"])
    ),
):
    users = db.scalars(
        select(User)
        .order_by(User.email)
    ).all()

    return {
        "status": "Access Granted",
        "feature": (
            "System User Directory "
            "Management"
        ),
        "registered_user_profiles": [
            user.email
            for user in users
        ],
    }