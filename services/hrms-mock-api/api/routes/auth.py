"""
Authentication Endpoints
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import timedelta
import logging

from utils.jwt_utils import verify_password, create_access_token, get_password_hash
from utils.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    user: dict


# Mock users (in production, this would be in database)
# Password for all: password123
MOCK_USERS = {
    "manish.w@amazatic.com": {
        "id": "EMP001",
        "email": "manish.w@amazatic.com",
        "password_hash": get_password_hash("password123"),
        "first_name": "Manish",
        "last_name": "Wagh",
        "department": "Engineering",
        "designation": "Engineering Manager"
    },
    "priyanka.c@amazatic.com": {
        "id": "EMP002",
        "email": "priyanka.c@amazatic.com",
        "password_hash": get_password_hash("password123"),
        "first_name": "Priyanka",
        "last_name": "Chavan",
        "department": "Engineering",
        "designation": "Senior Backend Developer"
    },
    "palak.s@amazatic.com": {
        "id": "EMP003",
        "email": "palak.s@amazatic.com",
        "password_hash": get_password_hash("password123"),
        "first_name": "Palak",
        "last_name": "Shah",
        "department": "Engineering",
        "designation": "Backend Developer"
    },
    "rohit.g@amazatic.com": {
        "id": "EMP004",
        "email": "rohit.g@amazatic.com",
        "password_hash": get_password_hash("password123"),
        "first_name": "Rohit",
        "last_name": "Gupta",
        "department": "Engineering",
        "designation": "Frontend Developer"
    },
    "manik.l@amazatic.com": {
        "id": "EMP005",
        "email": "manik.l@amazatic.com",
        "password_hash": get_password_hash("password123"),
        "first_name": "Manik",
        "last_name": "Lal",
        "department": "Engineering",
        "designation": "DevOps Engineer"
    }
}


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Employee login endpoint

    Default password for all users: password123
    """
    user = MOCK_USERS.get(request.email)

    if not user:
        logger.warning(f"Login attempt with non-existent email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(request.password, user["password_hash"]):
        logger.warning(f"Failed login attempt for: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )

    # Remove sensitive data
    user_data = {k: v for k, v in user.items() if k != "password_hash"}

    logger.info(f"User {request.email} logged in successfully")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_data
    )


@router.post("/refresh")
async def refresh_token():
    """Refresh access token"""
    # TODO: Implement token refresh logic
    return {"message": "Token refresh endpoint"}


@router.post("/logout")
async def logout():
    """Logout endpoint"""
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user():
    """Get current user profile"""
    # TODO: Implement with JWT verification
    return {"message": "Get current user endpoint"}


@router.get("/verify")
async def verify_token():
    """Verify JWT token"""
    # TODO: Implement token verification
    return {"message": "Token verification endpoint"}
