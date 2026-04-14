import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.app.submissions.models import SubmissionStatus


class SubmissionCreate(BaseModel):
    content: str


class GradeSubmission(BaseModel):
    score: float
    feedback: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    content: str
    score: Optional[float]
    feedback: Optional[str]
    status: SubmissionStatus
    submitted_at: datetime
    student_id: uuid.UUID
    assignment_id: uuid.UUID

    model_config = {"from_attributes": True}
