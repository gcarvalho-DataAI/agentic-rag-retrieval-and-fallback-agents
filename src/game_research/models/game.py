from __future__ import annotations

from pydantic import BaseModel, Field


class Game(BaseModel):
    name: str = Field(alias="Name")
    platform: str = Field(alias="Platform")
    genre: str = Field(alias="Genre")
    publisher: str = Field(alias="Publisher")
    description: str = Field(alias="Description")
    year_of_release: int = Field(alias="YearOfRelease")

    model_config = {
        "populate_by_name": True,
    }

