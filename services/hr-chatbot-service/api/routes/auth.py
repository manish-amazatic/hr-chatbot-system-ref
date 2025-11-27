"""
Authentication Endpoints
Handles JWT token verification with HRMS API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import httpx
import logging

from core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    """Login request model"""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login endpoint - forwards to HRMS API

    This service doesn't manage users directly, it forwards
    authentication to the HRMS Mock API and passes through the token.
    """
    try:
        # Forward login request to HRMS API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.hrms_api_url}/api/v1/auth/login",
                json={"email": request.email, "password": request.password},
                timeout=settings.hrms_api_timeout
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"User {request.email} logged in successfully")
                return TokenResponse(**data)
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication service error"
                )

    except httpx.RequestError as e:
        logger.error(f"Error connecting to HRMS API: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )


@router.post("/logout")
async def logout():
    """Logout endpoint"""
    # Since we're using stateless JWT, logout is handled client-side
    # In production, you might want to implement token blacklisting
    return {"message": "Logged out successfully"}


@router.get("/verify")
async def verify_token():
    """Verify JWT token (to be implemented with dependency)"""
    # TODO: Implement token verification
    return {"message": "Token verification endpoint"}
