import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.courses.service import get_course_or_404
from src.app.database import get_session
from src.app.dependencies import get_current_user, require_role
from src.app.enrollments.service import check_enrollment
from src.app.exceptions import ForbiddenError
from src.app.reviews.schemas import ReviewCreate, ReviewUpdate, ReviewResponse
from src.app.reviews.service import list_reviews, create_review, update_review, delete_review, get_review_or_404
from src.app.users.models import User, UserRole

router = APIRouter(prefix="/courses/{course_id}/reviews", tags=["Reviews"])


@router.get("/", response_model=list[ReviewResponse])
async def get_reviews(course_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await get_course_or_404(session, course_id, published_only=True)
    return await list_reviews(session, course_id)


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create(
    course_id: uuid.UUID,
    data: ReviewCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(UserRole.student)),
):
    await get_course_or_404(session, course_id)
    enrollment = await check_enrollment(session, current_user.id, course_id)
    if not enrollment:
        raise ForbiddenError("You must be enrolled in this course to leave a review")
    return await create_review(session, data, current_user, course_id)


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update(
    course_id: uuid.UUID,
    review_id: uuid.UUID,
    data: ReviewUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    review = await get_review_or_404(session, review_id)
    return await update_review(session, review, data, current_user)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    course_id: uuid.UUID,
    review_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    review = await get_review_or_404(session, review_id)
    await delete_review(session, review, current_user)
