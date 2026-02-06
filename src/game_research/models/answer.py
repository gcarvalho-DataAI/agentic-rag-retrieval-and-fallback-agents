from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    title: str = Field(..., description="Source title")
    url: Optional[str] = Field(None, description="Source URL if available")
    note: Optional[str] = Field(None, description="Short context for the source")


class Answer(BaseModel):
    answer: str = Field(..., description="Final answer to the user")
    sources: List[Source] = Field(default_factory=list)

