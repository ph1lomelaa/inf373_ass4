import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.assignments.schemas import AssignmentCreate, AssignmentUpdate, AssignmentTitleResponse, AssignmentResponse
from src.app.assignments.service import (
    get_assignment_or_404, list_assignment_titles,
    create_assignment, update_assignment, delete_assignment,
)
from src.app.courses.service import get_course_or_404
from src.app.database import get_session
from src.app.dependencies import get_current_user, require_role
from src.app.enrollments.service import check_enrollment
from src.app.exceptions import ForbiddenError
from src.app.users.models import User, UserRole

router = APIRouter(prefix="/courses/{course_id}/assignments", tags=["Assignments"])


@router.get("/", response_model=list[AssignmentTitleResponse])
async def get_assignment_titles(course_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await get_course_or_404(session, course_id, published_only=True)
    return await list_assignment_titles(session, course_id)


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    course_id: uuid.UUID,
    assignment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await get_course_or_404(session, course_id)
    enrollment = await check_enrollment(session, current_user.id, course_id)
    if not enrollment:
        raise ForbiddenError("You must be enrolled in this course")
    return await get_assignment_or_404(session, assignment_id)


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create(
    course_id: uuid.UUID,
    data: AssignmentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    course = await get_course_or_404(session, course_id)
    return await create_assignment(session, course, data, current_user)


@router.patch("/{assignment_id}", response_model=AssignmentResponse)
async def update(
    course_id: uuid.UUID,
    assignment_id: uuid.UUID,
    data: AssignmentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    course = await get_course_or_404(session, course_id)
    assignment = await get_assignment_or_404(session, assignment_id)
    return await update_assignment(session, assignment, data, current_user, course)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    course_id: uuid.UUID,
    assignment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    course = await get_course_or_404(session, course_id)
    assignment = await get_assignment_or_404(session, assignment_id)
    await delete_assignment(session, assignment, current_user, course)
