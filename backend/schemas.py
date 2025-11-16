from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Client(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    company: Optional[str] = Field(default=None, max_length=120)
    status: str = Field(default="new", description="new | in_progress | completed")
    notes: Optional[str] = Field(default=None, max_length=2000)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ChecklistItem(BaseModel):
    client_id: str
    title: str = Field(..., min_length=1, max_length=200)
    completed: bool = False
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
