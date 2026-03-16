import uuid
from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.models import RefreshToken
from app.auth.schemas import RegisterRequest, LoginRequest
from app.auth.utils import create_access_token, create_refresh_token, decode_token
from app.exceptions import ConflictError, UnauthorizedError, ForbiddenError
from app.users.models import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


async def register_user(session: AsyncSession, data: RegisterRequest) -> User:
    result = await session.exec(select(User).where(User.email == data.email))
    if result.first():
        raise ConflictError("Email already registered")

    result = await session.exec(select(User).where(User.username == data.username))
    if result.first():
        raise ConflictError("Username already taken")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=UserRole.student,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def login_user(session: AsyncSession, data: LoginRequest) -> tuple[str, str]:
    result = await session.exec(select(User).where(User.email == data.email))
    user = result.first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")

    if not user.is_active:
        raise ForbiddenError("User account is deactivated")

    access_token = create_access_token(str(user.id))
    refresh_token_str, expires_at = create_refresh_token(str(user.id))

    token_obj = RefreshToken(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=expires_at,
    )
    session.add(token_obj)
    await session.commit()

    return access_token, refresh_token_str


async def refresh_access_token(session: AsyncSession, refresh_token: str) -> str:
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid token type")

    result = await session.exec(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    token_obj = result.first()

    if not token_obj:
        raise UnauthorizedError("Refresh token not found or already used")

    if token_obj.expires_at < datetime.utcnow():
        await session.delete(token_obj)
        await session.commit()
        raise UnauthorizedError("Refresh token expired")

    user_id = payload.get("sub")
    return create_access_token(user_id)


async def logout_user(
    session: AsyncSession,
    redis,
    access_token: str,
    refresh_token: str | None,
    access_token_expire_seconds: int,
) -> None:
    # Blocklist the access token in Redis
    await redis.setex(f"blocklist:{access_token}", access_token_expire_seconds, "1")

    # Delete refresh token from DB if provided
    if refresh_token:
        result = await session.exec(
            select(RefreshToken).where(RefreshToken.token == refresh_token)
        )
        token_obj = result.first()
        if token_obj:
            await session.delete(token_obj)
            await session.commit()
