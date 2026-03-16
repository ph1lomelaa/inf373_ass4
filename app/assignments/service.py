import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.assignments.models import Assignment
from app.assignments.schemas import AssignmentCreate, AssignmentUpdate
from app.courses.models import Course
from app.exceptions import NotFoundError, ForbiddenError
from app.users.models import User


async def get_assignment_or_404(session: AsyncSession, assignment_id: uuid.UUID) -> Assignment:
    result = await session.exec(select(Assignment).where(Assignment.id == assignment_id))
    a = result.first()
    if not a:
        raise NotFoundError("Assignment not found")
    return a


async def list_assignment_titles(session: AsyncSession, course_id: uuid.UUID) -> list[Assignment]:
    result = await session.exec(select(Assignment).where(Assignment.course_id == course_id).order_by(Assignment.due_date))
    return result.all()


async def create_assignment(session: AsyncSession, course: Course, data: AssignmentCreate, instructor: User) -> Assignment:
    if course.instructor_id != instructor.id:
        raise ForbiddenError("You can only create assignments for your own courses")
    assignment = Assignment(**data.model_dump(), course_id=course.id)
    session.add(assignment)
    await session.commit()
    await session.refresh(assignment)
    return assignment


async def update_assignment(session: AsyncSession, assignment: Assignment, data: AssignmentUpdate, instructor: User, course: Course) -> Assignment:
    if course.instructor_id != instructor.id:
        raise ForbiddenError("You can only update assignments in your own courses")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(assignment, key, value)
    assignment.updated_at = datetime.utcnow()
    session.add(assignment)
    await session.commit()
    await session.refresh(assignment)
    return assignment


async def delete_assignment(session: AsyncSession, assignment: Assignment, instructor: User, course: Course) -> None:
    if course.instructor_id != instructor.id:
        raise ForbiddenError("You can only delete assignments in your own courses")
    await session.delete(assignment)
    await session.commit()
