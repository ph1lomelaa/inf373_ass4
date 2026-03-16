import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LessonCreate(BaseModel):
    title: str
    content: Optional[str] = None
    video_url: Optional[str] = None
    order: int = 1


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    order: Optional[int] = None


class LessonTitleResponse(BaseModel):
    id: uuid.UUID
    title: str
    order: int

    model_config = {"from_attributes": True}


class LessonResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: Optional[str]
    video_url: Optional[str]
    order: int
    course_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
