"""
backend/core/security.py
------------------------
Central security surface for FleetOS.

Provides two independent concerns:
  1. Password hashing / verification via passlib + bcrypt.
  2. JWT access and refresh token creation / decoding via python-jose.

All expiry durations and the signing secret are read from settings — nothing
is hardcoded here. Import and call these functions from auth routers and
permission helpers; never reimplement token or hashing logic elsewhere.

Usage example:
    from backend.core.security import (
        hash_password,
        verify_password,
        create_access_token,
        create_refresh_token,
        decode_token,
    )
"""

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.core.config import settings

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALGORITHM = "HS256"
"""
JWT signing algorithm.
HS256 (HMAC-SHA256) is a symmetric algorithm — the same SECRET_KEY is used to
both sign and verify tokens. Suitable for a single-service architecture where
the server both issues and consumes tokens.
"""

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
"""
passlib CryptContext configured for bcrypt.

deprecated="auto" means any hash produced with an older cost factor will be
transparently identified as deprecated on verify, allowing future re-hashing
without breaking existing logins. Only bcrypt is accepted — weaker schemes
(md5_crypt, sha1_crypt, etc.) are rejected rather than silently verified.
"""


def hash_password(password: str) -> str:
    """
    Return a bcrypt hash of the given plaintext password.

    The salt is generated internally by passlib on every call, so two calls
    with the same password produce different hashes — both will verify correctly.

    Args:
        password: The plaintext password string to hash.

    Returns:
        A bcrypt hash string suitable for storage in the database.
    """
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Return True if the plaintext password matches the stored bcrypt hash.

    Args:
        plain:   The plaintext password supplied by the user at login.
        hashed:  The bcrypt hash retrieved from the database.

    Returns:
        True if the password matches, False otherwise.
    """
    return _pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT token creation
# ---------------------------------------------------------------------------


def create_access_token(data: dict) -> str:
    """
    Create a signed JWT access token.

    A short-lived token intended to be sent with every API request in the
    Authorization header. Expiry is controlled by
    settings.ACCESS_TOKEN_EXPIRE_MINUTES.

    The payload is a shallow copy of `data` with two claims added:
      - "exp": absolute UTC expiry timestamp (read by decode_token)
      - "type": literal "access" (allows decode_token to reject refresh tokens
                used where an access token is expected, if that check is added)

    Args:
        data: Arbitrary claims to embed in the token (e.g. {"sub": user_id}).
              Must be JSON-serialisable. Do not include sensitive values such
              as passwords or raw secrets.

    Returns:
        A signed JWT string.
    """
    payload = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create a signed JWT refresh token.

    A long-lived token used exclusively to obtain new access tokens. Expiry
    is controlled by settings.REFRESH_TOKEN_EXPIRE_DAYS.

    The payload is a shallow copy of `data` with two claims added:
      - "exp": absolute UTC expiry timestamp
      - "type": literal "refresh"

    Args:
        data: Arbitrary claims to embed in the token (e.g. {"sub": user_id}).
              Must be JSON-serialisable.

    Returns:
        A signed JWT string.
    """
    payload = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# JWT token decoding
# ---------------------------------------------------------------------------


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token, returning its payload.

    Verification steps performed by python-jose:
      - Signature is valid (signed with settings.SECRET_KEY + HS256).
      - Token has not expired ("exp" claim is in the future).

    If either check fails, or if the token is malformed, a 401 HTTPException
    is raised so FastAPI can return an appropriate response to the client.

    Args:
        token: The raw JWT string (without "Bearer " prefix).

    Returns:
        The decoded payload dictionary (all claims embedded at token creation).

    Raises:
        HTTPException 401: If the token is invalid, expired, or malformed.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
