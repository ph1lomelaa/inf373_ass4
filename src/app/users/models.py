from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.app.courses.models import Course
    from src.app.enrollments.models import Enrollment
    from src.app.submissions.models import Submission
    from src.app.reviews.models import Review
    from src.app.auth.models import RefreshToken


class UserRole(str, Enum):
    student = "student"
    instructor = "instructor"
    admin = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str
    role: UserRole = Field(default=UserRole.student)
    is_active: bool = Field(default=True)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    courses: List["Course"] = Relationship(
        back_populates="instructor",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    enrollments: List["Enrollment"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    submissions: List["Submission"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    reviews: List["Review"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    refresh_tokens: List["RefreshToken"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
