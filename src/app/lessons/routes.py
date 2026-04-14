import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.courses.service import get_course_or_404
from src.app.database import get_session
from src.app.dependencies import get_current_user, require_role
from src.app.enrollments.service import check_enrollment
from src.app.exceptions import ForbiddenError
from src.app.lessons.schemas import LessonCreate, LessonUpdate, LessonTitleResponse, LessonResponse
from src.app.lessons.service import get_lesson_or_404, list_lessons_titles, create_lesson, update_lesson, delete_lesson
from src.app.users.models import User, UserRole

router = APIRouter(prefix="/courses/{course_id}/lessons", tags=["Lessons"])


@router.get("/", response_model=list[LessonTitleResponse])
async def get_lesson_titles(course_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await get_course_or_404(session, course_id, published_only=True)
    return await list_lessons_titles(session, course_id)


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    course = await get_course_or_404(session, course_id)
    enrollment = await check_enrollment(session, current_user.id, course_id)
    if not enrollment:
        raise ForbiddenError("You must be enrolled in this course to view lesson content")
    return await get_lesson_or_404(session, lesson_id)


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create(
    course_id: uuid.UUID,
    data: LessonCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    course = await get_course_or_404(session, course_id)
    return await create_lesson(session, course, data, current_user)


@router.patch("/{lesson_id}", response_model=LessonResponse)
async def update(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    data: LessonUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    course = await get_course_or_404(session, course_id)
    lesson = await get_lesson_or_404(session, lesson_id)
    return await update_lesson(session, lesson, data, current_user, course)


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    course = await get_course_or_404(session, course_id)
    lesson = await get_lesson_or_404(session, lesson_id)
    await delete_lesson(session, lesson, current_user, course)
