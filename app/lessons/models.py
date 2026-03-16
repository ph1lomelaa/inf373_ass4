from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.courses.models import Course


class Lesson(SQLModel, table=True):
    __tablename__ = "lessons"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=200)
    content: Optional[str] = Field(default=None)
    video_url: Optional[str] = Field(default=None)
    order: int = Field(default=1, ge=1)
    course_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    course: Optional["Course"] = Relationship(
        back_populates="lessons",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
