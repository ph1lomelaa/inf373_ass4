import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.courses.models import Course
from src.app.exceptions import NotFoundError, ForbiddenError, ConflictError
from src.app.lessons.models import Lesson
from src.app.lessons.schemas import LessonCreate, LessonUpdate
from src.app.users.models import User


async def get_lesson_or_404(session: AsyncSession, lesson_id: uuid.UUID) -> Lesson:
    result = await session.exec(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.first()
    if not lesson:
        raise NotFoundError("Lesson not found")
    return lesson


async def list_lessons_titles(session: AsyncSession, course_id: uuid.UUID) -> list[Lesson]:
    result = await session.exec(
        select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.order)
    )
    return result.all()


async def create_lesson(session: AsyncSession, course: Course, data: LessonCreate, instructor: User) -> Lesson:
    if course.instructor_id != instructor.id:
        raise ForbiddenError("You can only add lessons to your own courses")

    existing = await session.exec(
        select(Lesson).where(Lesson.course_id == course.id, Lesson.order == data.order)
    )
    if existing.first():
        raise ConflictError(f"A lesson with order {data.order} already exists in this course")

    lesson = Lesson(**data.model_dump(), course_id=course.id)
    session.add(lesson)
    await session.commit()
    await session.refresh(lesson)
    return lesson


async def update_lesson(session: AsyncSession, lesson: Lesson, data: LessonUpdate, instructor: User, course: Course) -> Lesson:
    if course.instructor_id != instructor.id:
        raise ForbiddenError("You can only update lessons in your own courses")

    if data.order is not None and data.order != lesson.order:
        existing = await session.exec(
            select(Lesson).where(Lesson.course_id == lesson.course_id, Lesson.order == data.order)
        )
        if existing.first():
            raise ConflictError(f"A lesson with order {data.order} already exists in this course")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(lesson, key, value)
    lesson.updated_at = datetime.utcnow()
    session.add(lesson)
    await session.commit()
    await session.refresh(lesson)
    return lesson


async def delete_lesson(session: AsyncSession, lesson: Lesson, instructor: User, course: Course) -> None:
    if course.instructor_id != instructor.id:
        raise ForbiddenError("You can only delete lessons in your own courses")
    await session.delete(lesson)
    await session.commit()
