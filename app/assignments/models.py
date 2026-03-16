from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.courses.models import Course
    from app.submissions.models import Submission


class Assignment(SQLModel, table=True):
    __tablename__ = "assignments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None)
    due_date: datetime
    max_score: float = Field(default=100.0, ge=0)
    course_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    course: Optional["Course"] = Relationship(
        back_populates="assignments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    submissions: List["Submission"] = Relationship(
        back_populates="assignment",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
