import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.categories.models import Category
from app.categories.schemas import CategoryCreate, CategoryUpdate
from app.courses.models import Course
from app.exceptions import NotFoundError, ConflictError, BadRequestError


async def list_categories(session: AsyncSession) -> list[Category]:
    result = await session.exec(select(Category).order_by(Category.name))
    return result.all()


async def get_category(session: AsyncSession, category_id: uuid.UUID) -> Category:
    result = await session.exec(select(Category).where(Category.id == category_id))
    cat = result.first()
    if not cat:
        raise NotFoundError("Category not found")
    return cat


async def create_category(session: AsyncSession, data: CategoryCreate) -> Category:
    exists = await session.exec(select(Category).where(Category.name == data.name))
    if exists.first():
        raise ConflictError("Category with this name already exists")
    cat = Category(**data.model_dump())
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    return cat


async def update_category(session: AsyncSession, category_id: uuid.UUID, data: CategoryUpdate) -> Category:
    cat = await get_category(session, category_id)
    if data.name and data.name != cat.name:
        exists = await session.exec(select(Category).where(Category.name == data.name))
        if exists.first():
            raise ConflictError("Category with this name already exists")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, key, value)
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    return cat


async def delete_category(session: AsyncSession, category_id: uuid.UUID) -> None:
    cat = await get_category(session, category_id)
    courses = await session.exec(select(Course).where(Course.category_id == category_id))
    if courses.first():
        raise BadRequestError("Cannot delete category that has courses assigned")
    await session.delete(cat)
    await session.commit()
