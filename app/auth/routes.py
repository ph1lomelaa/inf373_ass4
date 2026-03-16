from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    RegisterRequest, LoginRequest, TokenResponse,
    AccessTokenResponse, RefreshRequest,
)
from app.auth.service import register_user, login_user, refresh_access_token, logout_user
from app.config import settings
from app.database import get_session
from app.dependencies import get_current_user, get_redis
from app.users.models import User
from app.users.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, session: AsyncSession = Depends(get_session)):
    user = await register_user(session, data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    access_token, refresh_token = await login_user(session, data)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(data: RefreshRequest, session: AsyncSession = Depends(get_session)):
    access_token = await refresh_access_token(session, data.refresh_token)
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    data: RefreshRequest | None = None,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    redis=Depends(get_redis),
):
    expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_token = data.refresh_token if data else None
    await logout_user(
        session, redis,
        credentials.credentials,
        refresh_token,
        expire_seconds,
    )
    return {"message": "Successfully logged out"}
