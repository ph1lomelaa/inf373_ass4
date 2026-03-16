import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.exceptions import NotFoundError, ConflictError
from app.users.models import User
from app.users.schemas import UserUpdate, AdminUserUpdate


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User:
    result = await session.exec(select(User).where(User.id == user_id))
    user = result.first()
    if not user:
        raise NotFoundError(f"User with id {user_id} not found")
    return user


async def list_users(session: AsyncSession, skip: int = 0, limit: int = 20) -> list[User]:
    result = await session.exec(select(User).offset(skip).limit(limit))
    return result.all()


async def update_user(session: AsyncSession, user: User, data: UserUpdate) -> User:
    if data.username and data.username != user.username:
        exists = await session.exec(select(User).where(User.username == data.username))
        if exists.first():
            raise ConflictError("Username already taken")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    user.updated_at = datetime.utcnow()

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def admin_update_user(session: AsyncSession, user: User, data: AdminUserUpdate) -> User:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    user.updated_at = datetime.utcnow()

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
