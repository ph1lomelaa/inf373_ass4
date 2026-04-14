import uuid
from typing import Optional

import redis.asyncio as aioredis
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.auth.utils import decode_token
from src.app.config import settings
from src.app.database import get_session
from src.app.exceptions import UnauthorizedError, ForbiddenError
from src.app.users.models import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)

_redis_client: Optional[aioredis.Redis] = None


def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
    redis: aioredis.Redis = Depends(get_redis),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Missing authentication token")

    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    # Check blocklist
    is_blocked = await redis.get(f"blocklist:{token}")
    if is_blocked:
        raise UnauthorizedError("Token has been revoked")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")

    from sqlmodel import select
    result = await session.exec(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.first()

    if not user:
        raise UnauthorizedError("User not found")

    if not user.is_active:
        raise ForbiddenError("User account is deactivated")

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
    redis: aioredis.Redis = Depends(get_redis),
) -> Optional[User]:
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials, session, redis)
    except Exception:
        return None


def require_role(*roles: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenError(
                f"Required role(s): {', '.join(r.value for r in roles)}"
            )
        return current_user

    return role_checker
