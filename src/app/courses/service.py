import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.categories.models import Category
from src.app.courses.models import Course
from src.app.courses.schemas import CourseCreate, CourseUpdate
from src.app.exceptions import NotFoundError, ForbiddenError, BadRequestError
from src.app.lessons.models import Lesson
from src.app.users.models import User


async def get_course_or_404(session: AsyncSession, course_id: uuid.UUID, published_only: bool = False) -> Course:
    result = await session.exec(select(Course).where(Course.id == course_id))
    course = result.first()
    if not course:
        raise NotFoundError("Course not found")
    if published_only and not course.is_published:
        raise NotFoundError("Course not found")
    return course


async def list_courses(
    session: AsyncSession,
    published_only: bool = True,
    category_id: uuid.UUID | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 20,
) -> list[Course]:
    query = select(Course)
    if published_only:
        query = query.where(Course.is_published == True)
    if category_id:
        query = query.where(Course.category_id == category_id)
    if search:
        query = query.where(Course.title.ilike(f"%{search}%"))

    sort_column = getattr(Course, sort_by, Course.created_at)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())
    query = query.offset(skip).limit(limit)

    result = await session.exec(query)
    return result.all()


async def create_course(session: AsyncSession, data: CourseCreate, instructor: User) -> Course:
    if data.category_id:
        cat = await session.exec(select(Category).where(Category.id == data.category_id))
        if not cat.first():
            raise NotFoundError("Category not found")

    course = Course(**data.model_dump(), instructor_id=instructor.id)
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


async def update_course(session: AsyncSession, course: Course, data: CourseUpdate, current_user: User) -> Course:
    if course.instructor_id != current_user.id:
        raise ForbiddenError("You can only update your own courses")
    if data.category_id:
        cat = await session.exec(select(Category).where(Category.id == data.category_id))
        if not cat.first():
            raise NotFoundError("Category not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(course, key, value)
    course.updated_at = datetime.utcnow()
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


async def publish_course(session: AsyncSession, course: Course, current_user: User) -> Course:
    if course.instructor_id != current_user.id:
        raise ForbiddenError("You can only publish your own courses")
    lessons = await session.exec(select(Lesson).where(Lesson.course_id == course.id))
    if not lessons.first():
        raise BadRequestError("Cannot publish a course with no lessons")
    course.is_published = True
    course.updated_at = datetime.utcnow()
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


async def unpublish_course(session: AsyncSession, course: Course, current_user: User) -> Course:
    if course.instructor_id != current_user.id:
        raise ForbiddenError("You can only unpublish your own courses")
    course.is_published = False
    course.updated_at = datetime.utcnow()
    session.add(course)
    await session.commit()
    await session.refresh(course)
    return course


async def delete_course(session: AsyncSession, course: Course, current_user: User) -> None:
    from src.app.users.models import UserRole
    if course.instructor_id != current_user.id and current_user.role != UserRole.admin:
        raise ForbiddenError("You can only delete your own courses")
    await session.delete(course)
    await session.commit()
