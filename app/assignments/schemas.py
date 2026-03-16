import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    max_score: float = 100.0


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    max_score: Optional[float] = None


class AssignmentTitleResponse(BaseModel):
    id: uuid.UUID
    title: str
    due_date: datetime

    model_config = {"from_attributes": True}


class AssignmentResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    due_date: datetime
    max_score: float
    course_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
