import logging

from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt

from backend.config import ALGORITHM, SECRET_KEY

logger = logging.getLogger(__name__)


def get_current_user(
    authorization: str = Header(...),
) -> dict:

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail=(
                "Malformed Authorization header. "
                "Expected Bearer token."
            ),
        )

    token = authorization[7:].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing bearer token.",
        )

    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

    except JWTError as error:
        logger.warning(
            "JWT validation failed: %s",
            error,
        )

        raise HTTPException(
            status_code=401,
            detail=(
                "Expired or invalid "
                "authentication token."
            ),
        ) from error


def require_role(
    allowed_roles: list[str],
):
    def role_checker(
        user: dict = Depends(get_current_user),
    ):
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Access denied. "
                    "Required role(s): "
                    + ", ".join(allowed_roles)
                ),
            )

        return user

    return role_checker