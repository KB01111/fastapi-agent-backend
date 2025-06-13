"""Authentication utilities for Clerk JWT verification."""

import json
import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient

from app.config import settings
import structlog

logger = structlog.get_logger()

# JWT validation setup
security = HTTPBearer()


class ClerkUser:
    """Represents an authenticated Clerk user."""
    
    def __init__(self, user_id: str, email: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.email = email
        self.metadata = metadata or {}
    
    def __repr__(self) -> str:
        return f"ClerkUser(user_id='{self.user_id}', email='{self.email}')"


def get_jwks_client() -> PyJWKClient:
    """Get JWKS client for Clerk token verification."""
    # Extract the instance ID from the publishable key
    parts = settings.clerk_publishable_key.split('_')
    if len(parts) < 2:
        raise ValueError("Invalid Clerk publishable key format")
    
    instance_id = parts[1]
    jwks_url = f"https://clerk.{instance_id}.lcl.dev/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


async def verify_clerk_jwt(token: str) -> ClerkUser:
    """
    Verify a Clerk-issued JWT token and return user information.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        ClerkUser: Authenticated user information
        
    Raises:
        HTTPException: If token is invalid or verification fails
    """
    try:
        # Get the signing key from Clerk's JWKS endpoint
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.clerk_publishable_key,
            options={"verify_exp": True}
        )
        
        # Extract user information from payload
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        email = payload.get("email")
        metadata = payload.get("public_metadata", {})
        
        logger.info("JWT verified successfully", user_id=user_id, email=email)
        return ClerkUser(user_id=user_id, email=email, metadata=metadata)
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid JWT token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error("JWT verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> ClerkUser:
    """
    FastAPI dependency to get the current authenticated user.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        ClerkUser: The authenticated user
    """
    token_value: str = credentials.credentials
    return await verify_clerk_jwt(token_value)


# Optional security for endpoints that can work with or without auth
optional_security = HTTPBearer(auto_error=False)


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)) -> Optional[ClerkUser]:
    """
    FastAPI dependency for optional authentication.
    
    Args:
        credentials: Optional HTTP authorization credentials
        
    Returns:
        ClerkUser or None: The authenticated user if present
    """
    if not credentials:
        return None
    
    try:
        token_value: str = credentials.credentials
        return await verify_clerk_jwt(token_value)
    except HTTPException:
        return None 