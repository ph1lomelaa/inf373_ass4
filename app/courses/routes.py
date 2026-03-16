import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.courses.schemas import CourseCreate, CourseUpdate, CourseResponse
from app.courses.service import (
    get_course_or_404, list_courses, create_course,
    update_course, publish_course, unpublish_course, delete_course,
)
from app.database import get_session
from app.dependencies import get_current_user, require_role
from app.users.models import User, UserRole

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/", response_model=list[CourseResponse])
async def get_courses(
    category_id: Optional[uuid.UUID] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at", enum=["created_at", "price", "title"]),
    order: str = Query("desc", enum=["asc", "desc"]),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    return await list_courses(session, published_only=True, category_id=category_id,
                              search=search, sort_by=sort_by, order=order, skip=skip, limit=limit)


@router.get("/admin/all", response_model=list[CourseResponse])
async def get_all_courses_admin(
    skip: int = 0, limit: int = 20,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_role(UserRole.admin)),
):
    return await list_courses(session, published_only=False, skip=skip, limit=limit)


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    return await get_course_or_404(session, course_id, published_only=True)


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: CourseCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    return await create_course(session, data, current_user)


@router.patch("/{course_id}", response_model=CourseResponse)
async def update(
    course_id: uuid.UUID,
    data: CourseUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    course = await get_course_or_404(session, course_id)
    return await update_course(session, course, data, current_user)


@router.post("/{course_id}/publish", response_model=CourseResponse)
async def publish(
    course_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    course = await get_course_or_404(session, course_id)
    return await publish_course(session, course, current_user)


@router.post("/{course_id}/unpublish", response_model=CourseResponse)
async def unpublish(
    course_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    course = await get_course_or_404(session, course_id)
    return await unpublish_course(session, course, current_user)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    course_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    course = await get_course_or_404(session, course_id)
    await delete_course(session, course, current_user)
