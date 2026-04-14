from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.app.users.models import User
    from src.app.categories.models import Category
    from src.app.lessons.models import Lesson
    from src.app.enrollments.models import Enrollment
    from src.app.assignments.models import Assignment
    from src.app.reviews.models import Review


class Course(SQLModel, table=True):
    __tablename__ = "courses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(index=True, max_length=200)
    description: Optional[str] = Field(default=None)
    price: float = Field(default=0.0, ge=0)
    is_published: bool = Field(default=False)
    thumbnail_url: Optional[str] = Field(default=None)
    instructor_id: uuid.UUID = Field(foreign_key="users.id")
    category_id: Optional[uuid.UUID] = Field(default=None, foreign_key="categories.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    instructor: Optional["User"] = Relationship(
        back_populates="courses",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    category: Optional["Category"] = Relationship(
        back_populates="courses",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    lessons: List["Lesson"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    enrollments: List["Enrollment"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    assignments: List["Assignment"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    reviews: List["Review"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
