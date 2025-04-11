from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SystemSettingsUpdate(BaseModel):
    archive_hours: int

class SystemSettingsResponse(BaseModel):
    archive_hours: int
    modified_at: datetime

class ProblemTypeCreate(BaseModel):
    name: str

class ProblemTypeResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True

class SolutionTypeCreate(BaseModel):
    name: str

class SolutionTypeResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True 