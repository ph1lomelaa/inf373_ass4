import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.exceptions import NotFoundError, ForbiddenError, ConflictError
from app.reviews.models import Review
from app.reviews.schemas import ReviewCreate, ReviewUpdate
from app.users.models import User, UserRole


async def get_review_or_404(session: AsyncSession, review_id: uuid.UUID) -> Review:
    result = await session.exec(select(Review).where(Review.id == review_id))
    r = result.first()
    if not r:
        raise NotFoundError("Review not found")
    return r


async def list_reviews(session: AsyncSession, course_id: uuid.UUID) -> list[Review]:
    result = await session.exec(select(Review).where(Review.course_id == course_id).order_by(Review.created_at.desc()))
    return result.all()


async def create_review(session: AsyncSession, data: ReviewCreate, student: User, course_id: uuid.UUID) -> Review:
    existing = await session.exec(
        select(Review).where(Review.student_id == student.id, Review.course_id == course_id)
    )
    if existing.first():
        raise ConflictError("You have already reviewed this course")

    review = Review(**data.model_dump(), student_id=student.id, course_id=course_id)
    session.add(review)
    await session.commit()
    await session.refresh(review)
    return review


async def update_review(session: AsyncSession, review: Review, data: ReviewUpdate, current_user: User) -> Review:
    if review.student_id != current_user.id:
        raise ForbiddenError("You can only update your own reviews")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(review, key, value)
    review.updated_at = datetime.utcnow()
    session.add(review)
    await session.commit()
    await session.refresh(review)
    return review


async def delete_review(session: AsyncSession, review: Review, current_user: User) -> None:
    if review.student_id != current_user.id and current_user.role != UserRole.admin:
        raise ForbiddenError("You can only delete your own reviews")
    await session.delete(review)
    await session.commit()
