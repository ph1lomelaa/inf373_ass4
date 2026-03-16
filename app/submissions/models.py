from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.users.models import User
    from app.assignments.models import Assignment


class SubmissionStatus(str, Enum):
    pending = "pending"
    graded = "graded"


class Submission(SQLModel, table=True):
    __tablename__ = "submissions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str
    score: Optional[float] = Field(default=None, ge=0)
    feedback: Optional[str] = Field(default=None)
    status: SubmissionStatus = Field(default=SubmissionStatus.pending)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    student_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    assignment_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    )

    student: Optional["User"] = Relationship(
        back_populates="submissions",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    assignment: Optional["Assignment"] = Relationship(
        back_populates="submissions",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
