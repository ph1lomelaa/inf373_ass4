import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.database import get_session
from src.app.dependencies import get_current_user, require_role
from src.app.exceptions import ForbiddenError
from src.app.users.models import User, UserRole
from src.app.users.schemas import UserResponse, UserUpdate, AdminUserUpdate
from src.app.users.service import get_user_by_id, list_users, update_user, admin_update_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await update_user(session, current_user, data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    return await get_user_by_id(session, user_id)


@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_role(UserRole.admin)),
):
    return await list_users(session, skip, limit)


@router.patch("/{user_id}/admin", response_model=UserResponse)
async def admin_update(
    user_id: uuid.UUID,
    data: AdminUserUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_role(UserRole.admin)),
):
    user = await get_user_by_id(session, user_id)
    return await admin_update_user(session, user, data)
