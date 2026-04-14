import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.app.enrollments.models import EnrollmentStatus


class EnrollmentResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    course_id: uuid.UUID
    status: EnrollmentStatus
    enrolled_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}
