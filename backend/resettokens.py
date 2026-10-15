"""Password-reset token helpers. Only the SHA-256 hash of a token is stored, so a leaked database cannot be used to reset passwords."""
import hashlib
import secrets


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
