import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.enrollments.models import Enrollment, EnrollmentStatus
from app.exceptions import ConflictError, BadRequestError, ForbiddenError, NotFoundError
from app.users.models import UserRole


async def check_enrollment(session: AsyncSession, student_id: uuid.UUID, course_id: uuid.UUID) -> Optional[Enrollment]:
    result = await session.exec(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
            Enrollment.status == EnrollmentStatus.active,
        )
    )
    return result.first()


async def enroll_student(session: AsyncSession, student_id: uuid.UUID, course_id: uuid.UUID) -> Enrollment:
    # Check for active enrollment
    active = await session.exec(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
            Enrollment.status == EnrollmentStatus.active,
        )
    )
    if active.first():
        raise ConflictError("Already enrolled in this course")

    enrollment = Enrollment(student_id=student_id, course_id=course_id)
    session.add(enrollment)
    await session.commit()
    await session.refresh(enrollment)
    return enrollment


async def get_my_enrollments(session: AsyncSession, student_id: uuid.UUID) -> list[Enrollment]:
    result = await session.exec(select(Enrollment).where(Enrollment.student_id == student_id))
    return result.all()


async def get_course_enrollments(session: AsyncSession, course_id: uuid.UUID) -> list[Enrollment]:
    result = await session.exec(select(Enrollment).where(Enrollment.course_id == course_id))
    return result.all()


async def list_all_enrollments(session: AsyncSession, skip: int = 0, limit: int = 50) -> list[Enrollment]:
    result = await session.exec(select(Enrollment).offset(skip).limit(limit))
    return result.all()


async def get_enrollment_or_404(session: AsyncSession, enrollment_id: uuid.UUID) -> Enrollment:
    result = await session.exec(select(Enrollment).where(Enrollment.id == enrollment_id))
    e = result.first()
    if not e:
        raise NotFoundError("Enrollment not found")
    return e


async def complete_enrollment(session: AsyncSession, enrollment: Enrollment, student_id: uuid.UUID) -> Enrollment:
    if enrollment.student_id != student_id:
        raise ForbiddenError("Not your enrollment")
    if enrollment.status == EnrollmentStatus.completed:
        raise BadRequestError("Enrollment is already completed")
    if enrollment.status == EnrollmentStatus.cancelled:
        raise BadRequestError("Cannot complete a cancelled enrollment")
    enrollment.status = EnrollmentStatus.completed
    enrollment.completed_at = datetime.utcnow()
    session.add(enrollment)
    await session.commit()
    await session.refresh(enrollment)
    return enrollment


async def cancel_enrollment(session: AsyncSession, enrollment: Enrollment, student_id: uuid.UUID) -> Enrollment:
    if enrollment.student_id != student_id:
        raise ForbiddenError("Not your enrollment")
    if enrollment.status == EnrollmentStatus.cancelled:
        raise BadRequestError("Enrollment is already cancelled")
    enrollment.status = EnrollmentStatus.cancelled
    session.add(enrollment)
    await session.commit()
    await session.refresh(enrollment)
    return enrollment
