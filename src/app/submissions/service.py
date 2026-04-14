import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.assignments.models import Assignment
from src.app.exceptions import NotFoundError, ForbiddenError, BadRequestError, ConflictError
from src.app.submissions.models import Submission, SubmissionStatus
from src.app.submissions.schemas import SubmissionCreate, GradeSubmission
from src.app.users.models import User


async def get_submission_or_404(session: AsyncSession, submission_id: uuid.UUID) -> Submission:
    result = await session.exec(select(Submission).where(Submission.id == submission_id))
    s = result.first()
    if not s:
        raise NotFoundError("Submission not found")
    return s


async def submit_assignment(
    session: AsyncSession, data: SubmissionCreate,
    assignment: Assignment, student: User,
) -> Submission:
    if datetime.utcnow() > assignment.due_date:
        raise BadRequestError("Assignment due date has passed")

    existing = await session.exec(
        select(Submission).where(
            Submission.student_id == student.id,
            Submission.assignment_id == assignment.id,
        )
    )
    if existing.first():
        raise ConflictError("You already submitted this assignment")

    submission = Submission(
        content=data.content,
        student_id=student.id,
        assignment_id=assignment.id,
    )
    session.add(submission)
    await session.commit()
    await session.refresh(submission)
    return submission


async def get_my_submissions(session: AsyncSession, student_id: uuid.UUID, course_id: uuid.UUID | None = None) -> list[Submission]:
    query = select(Submission).where(Submission.student_id == student_id)
    result = await session.exec(query)
    return result.all()


async def get_assignment_submissions(session: AsyncSession, assignment: Assignment, instructor: User, course) -> list[Submission]:
    if course.instructor_id != instructor.id:
        raise ForbiddenError("You can only view submissions for your own courses")
    result = await session.exec(
        select(Submission).where(Submission.assignment_id == assignment.id)
    )
    return result.all()


async def grade_submission(
    session: AsyncSession,
    submission: Submission,
    data: GradeSubmission,
    instructor: User,
    assignment: Assignment,
    course,
) -> Submission:
    if course.instructor_id != instructor.id:
        raise ForbiddenError("You can only grade submissions in your own courses")
    if data.score > assignment.max_score:
        raise BadRequestError(f"Score cannot exceed max score of {assignment.max_score}")
    submission.score = data.score
    submission.feedback = data.feedback
    submission.status = SubmissionStatus.graded
    session.add(submission)
    await session.commit()
    await session.refresh(submission)
    return submission
