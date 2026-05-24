"""
API Key authentication dependency for FastAPI.
All POST endpoints require X-API-Key header.
"""

import os
import secrets
import logging

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def _get_api_secret() -> str:
    """
    Resolve API secret key securely.
    Priority: environment variable -> .env file -> ephemeral random key (dev only).
    """
    secret = os.getenv("API_SECRET_KEY")
    if secret:
        return secret

    # TODO(security): In production, use KMS or established secret management.
    # Fallback to ephemeral random key for local dev — NOT horizontally scalable.
    logger.warning(
        "API_SECRET_KEY not found in environment. "
        "Generating ephemeral secret. Instance-isolated — NOT safe for production!"
    )
    return secrets.token_hex(32)


_RESOLVED_SECRET = _get_api_secret()


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """FastAPI dependency — validates X-API-Key header against stored secret."""
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    if not secrets.compare_digest(api_key, _RESOLVED_SECRET):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return api_key
