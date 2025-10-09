"""
Authentication API routes
"""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.auth import (
    create_tokens_for_user, 
    verify_token, 
    get_current_user,
    get_current_active_user,
    security,
    create_access_token
)
from app.models.user import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    Token, 
    TokenData,
    UserInDB
)
from app.services.user_service import user_service
from app.schemas.auth import TokenResponse
from app.schemas.base import BaseResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])

class TokenRequest(BaseModel):
    username: str
    password: str


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user
    
    Creates a new user account with hashed password and returns JWT tokens.
    """
    try:
        logger.info(f"🔐 Registration attempt for: {user_data.email}")
        logger.info(f"📝 User data received: email={user_data.email}, full_name='{user_data.full_name}', role={user_data.role}")
        
        # Validate input
        if len(user_data.password) < 8:
            logger.warning(f"⚠️ Password too short for user: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        if not user_data.email or "@" not in user_data.email:
            logger.warning(f"⚠️ Invalid email format: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid email address is required"
            )
        
        if not user_data.full_name or len(user_data.full_name.strip()) < 2:
            logger.warning(f"⚠️ Invalid full name: '{user_data.full_name}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Full name must be at least 2 characters long"
            )
        
        # Check if user already exists
        existing_user = await user_service.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user
        created_user = await user_service.create(user_data)
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create tokens
        token_data = create_tokens_for_user(created_user)
        
        # Prepare user response
        user_response = UserResponse(
            id=str(created_user.id),
            email=created_user.email,
            full_name=created_user.full_name,
            role=created_user.role,
            is_active=created_user.is_active,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
            last_login=created_user.last_login
        )
        
        # Create token response
        token_response = Token(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user=user_response
        )
        
        logger.info(f"✅ User registered successfully: {user_data.email}")
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """
    Login user and return JWT tokens
    
    Authenticates user with email and password and returns access + refresh tokens.
    """
    try:
        logger.info(f"🔐 Login attempt with email: {login_data.email}")

        try:
            # Authenticate user (check password)
            authenticated_user = await user_service.authenticate(login_data.email, login_data.password)
            if not authenticated_user:
                logger.warning(f"⚠️ Invalid credentials for user: {login_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            # Check if user is active
            if not authenticated_user.is_active:
                logger.warning(f"⚠️ Login attempt for inactive user: {login_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Your account has been deactivated. Please contact support."
                )

        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        
        # Create tokens
        token_data = create_tokens_for_user(authenticated_user)
        
        # Prepare user response
        user_response = UserResponse(
            id=str(authenticated_user.id),
            email=authenticated_user.email,
            full_name=authenticated_user.full_name,
            role=authenticated_user.role,
            is_active=authenticated_user.is_active,
            created_at=authenticated_user.created_at,
            updated_at=authenticated_user.updated_at,
            last_login=authenticated_user.last_login
        )
        
        # Create token response
        token_response = Token(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user=user_response
        )
        
        logger.info(f"✅ User logged in successfully: {login_data.email}")
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error. Please try again."
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh access token using refresh token
    
    Validates refresh token and returns new access + refresh tokens.
    """
    try:
        # Verify refresh token
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user from database
        user = await user_service.get_by_id(token_data.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        new_token_data = create_tokens_for_user(user)
        
        # Prepare user response
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        
        # Create token response
        token_response = Token(
            access_token=new_token_data["access_token"],
            refresh_token=new_token_data["refresh_token"],
            token_type=new_token_data["token_type"],
            expires_in=new_token_data["expires_in"],
            user=user_response
        )
        
        logger.info(f"✅ Token refreshed successfully: {user.email}")
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    """
    Get current user information
    
    Returns the current authenticated user's profile information.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login
    )


@router.post("/logout")
async def logout(current_user: Optional[UserInDB] = Depends(get_current_user)):
    """
    Logout user
    
    In a stateless JWT system, logout is handled client-side by removing tokens.
    This endpoint exists for consistency and future session management.
    """
    if current_user:
        logger.info(f"✅ User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}


@router.get("/debug/users")
async def debug_users():
    """
    Debug endpoint to check registered users (development only)
    """
    try:
        from app.services.user_service import _dev_users
        
        users_info = []
        for user_id, user in _dev_users.items():
            users_info.append({
                "id": user_id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            })
        
        return {
            "total_users": len(_dev_users),
            "users": users_info
        }
        
    except Exception as e:
        logger.error(f"❌ Debug users error: {e}")
        return {"error": str(e)}


@router.post("/token", response_model=TokenResponse)
async def create_access_token(request: TokenRequest) -> TokenResponse:
    """Create access token for authentication"""
    try:
        # Mock authentication - replace with real auth logic
        if request.username == "admin" and request.password == "admin123":
            return TokenResponse(
                access_token="mock_jwt_token_12345",
                token_type="bearer",
                expires_in=3600
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )
