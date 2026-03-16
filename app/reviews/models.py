from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.users.models import User
    from app.courses.models import Course


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None)
    student_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    course_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    student: Optional["User"] = Relationship(
        back_populates="reviews",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    course: Optional["Course"] = Relationship(
        back_populates="reviews",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
