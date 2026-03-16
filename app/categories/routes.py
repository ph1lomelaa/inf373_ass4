import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.categories.service import list_categories, get_category, create_category, update_category, delete_category
from app.database import get_session
from app.dependencies import require_role
from app.users.models import UserRole

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryResponse])
async def get_categories(session: AsyncSession = Depends(get_session)):
    return await list_categories(session)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(category_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    return await get_category(session, category_id)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_session),
    _=Depends(require_role(UserRole.admin)),
):
    return await create_category(session, data)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    session: AsyncSession = Depends(get_session),
    _=Depends(require_role(UserRole.admin)),
):
    return await update_category(session, category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    category_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _=Depends(require_role(UserRole.admin)),
):
    await delete_category(session, category_id)
