
import logging

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from backend.config import ALGORITHM, SECRET_KEY

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Missing bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

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
            detail="Expired or invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


def require_role(allowed_roles: list[str]):
    def role_checker(
        user: dict = Depends(get_current_user),
    ):
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Access denied. Required role(s): "
                    + ", ".join(allowed_roles)
                ),
            )

        return user

    return role_checker
