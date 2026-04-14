from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.app.users.models import User


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    token: str = Field(unique=True, index=True)
    user_id: uuid.UUID = Field(
        sa_column=sa.Column(sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    )
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(
        back_populates="refresh_tokens",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
