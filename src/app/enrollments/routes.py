import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.courses.service import get_course_or_404
from src.app.database import get_session
from src.app.dependencies import get_current_user, require_role
from src.app.enrollments.schemas import EnrollmentResponse
from src.app.enrollments.service import (
    enroll_student, get_my_enrollments, get_course_enrollments,
    list_all_enrollments, get_enrollment_or_404, complete_enrollment, cancel_enrollment,
)
from src.app.exceptions import ForbiddenError
from src.app.users.models import User, UserRole

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/courses/{course_id}", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll(
    course_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.student)),
):
    course = await get_course_or_404(session, course_id, published_only=True)
    if course.instructor_id == current_user.id:
        raise ForbiddenError("Instructors cannot enroll in their own courses")
    return await enroll_student(session, current_user.id, course_id)


@router.get("/me", response_model=list[EnrollmentResponse])
async def my_enrollments(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await get_my_enrollments(session, current_user.id)


@router.get("/courses/{course_id}", response_model=list[EnrollmentResponse])
async def course_enrollments(
    course_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    course = await get_course_or_404(session, course_id)
    if course.instructor_id != current_user.id:
        raise ForbiddenError("You can only view enrollments for your own courses")
    return await get_course_enrollments(session, course_id)


@router.get("/", response_model=list[EnrollmentResponse])
async def all_enrollments(
    skip: int = 0, limit: int = 50,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_role(UserRole.admin)),
):
    return await list_all_enrollments(session, skip, limit)


@router.post("/{enrollment_id}/complete", response_model=EnrollmentResponse)
async def complete(
    enrollment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    enrollment = await get_enrollment_or_404(session, enrollment_id)
    return await complete_enrollment(session, enrollment, current_user.id)


@router.post("/{enrollment_id}/cancel", response_model=EnrollmentResponse)
async def cancel(
    enrollment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    enrollment = await get_enrollment_or_404(session, enrollment_id)
    return await cancel_enrollment(session, enrollment, current_user.id)
