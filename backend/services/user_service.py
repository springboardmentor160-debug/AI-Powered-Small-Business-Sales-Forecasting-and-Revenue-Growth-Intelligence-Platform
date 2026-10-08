import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.user import User

logger = logging.getLogger(__name__)


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    normalized_email = email.lower().strip()

    return db.scalar(
        select(User).where(
            User.email == normalized_email
        )
    )