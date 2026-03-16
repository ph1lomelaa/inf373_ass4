import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = 0.0
    category_id: Optional[uuid.UUID] = None
    thumbnail_url: Optional[str] = None


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[uuid.UUID] = None
    thumbnail_url: Optional[str] = None


class CourseResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    price: float
    is_published: bool
    instructor_id: uuid.UUID
    category_id: Optional[uuid.UUID]
    thumbnail_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
