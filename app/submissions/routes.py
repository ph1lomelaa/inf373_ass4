import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.assignments.service import get_assignment_or_404
from app.courses.service import get_course_or_404
from app.database import get_session
from app.dependencies import get_current_user, require_role
from app.enrollments.service import check_enrollment
from app.exceptions import ForbiddenError
from app.submissions.schemas import SubmissionCreate, GradeSubmission, SubmissionResponse
from app.submissions.service import (
    submit_assignment, get_my_submissions,
    get_assignment_submissions, grade_submission, get_submission_or_404,
)
from app.users.models import User, UserRole

router = APIRouter(tags=["Submissions"])


@router.post("/courses/{course_id}/assignments/{assignment_id}/submissions",
             response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit(
    course_id: uuid.UUID,
    assignment_id: uuid.UUID,
    data: SubmissionCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.student)),
):
    await get_course_or_404(session, course_id)
    enrollment = await check_enrollment(session, current_user.id, course_id)
    if not enrollment:
        raise ForbiddenError("You must be enrolled in this course to submit")
    assignment = await get_assignment_or_404(session, assignment_id)
    return await submit_assignment(session, data, assignment, current_user)


@router.get("/submissions/me", response_model=list[SubmissionResponse])
async def my_submissions(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await get_my_submissions(session, current_user.id)


@router.get("/courses/{course_id}/assignments/{assignment_id}/submissions",
            response_model=list[SubmissionResponse])
async def assignment_submissions(
    course_id: uuid.UUID,
    assignment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    course = await get_course_or_404(session, course_id)
    assignment = await get_assignment_or_404(session, assignment_id)
    return await get_assignment_submissions(session, assignment, current_user, course)


@router.patch("/submissions/{submission_id}/grade", response_model=SubmissionResponse)
async def grade(
    submission_id: uuid.UUID,
    data: GradeSubmission,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.instructor)),
):
    submission = await get_submission_or_404(session, submission_id)
    assignment = await get_assignment_or_404(session, submission.assignment_id)
    course = await get_course_or_404(session, assignment.course_id)
    return await grade_submission(session, submission, data, current_user, assignment, course)
