from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.app.users.models import User
    from src.app.courses.models import Course


class EnrollmentStatus(str, Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class Enrollment(SQLModel, table=True):
    __tablename__ = "enrollments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    student_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    course_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    )
    status: EnrollmentStatus = Field(default=EnrollmentStatus.active)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    student: Optional["User"] = Relationship(
        back_populates="enrollments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    course: Optional["Course"] = Relationship(
        back_populates="enrollments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
