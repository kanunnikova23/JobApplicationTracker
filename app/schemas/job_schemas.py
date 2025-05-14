# Defines what data should look like (input/output).

# this file tells FastAPI how data should
# be shaped for requests (input) and responses (output).

from pydantic import BaseModel, AnyUrl, Field
from datetime import date
from typing import Optional
from enum import Enum as PyEnum


class ApplicationStatus(str, PyEnum):
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


# Schema  which maps to DB model, minus the id.
# shared base for create + response, reused in other schemas
class JobAppBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=100, description="Company you applied to")
    position: str = Field(..., min_length=1, max_length=100, description="Position you applied to")
    location: Optional[str] = Field(default=None, max_length=100, description="Company you applied to")
    status: Optional[ApplicationStatus] = Field(default=None, description="Status of your application")
    applied_date: date = Field(..., description="Date of application")
    link: AnyUrl | None = Field(default=None, description="Link to the job description")
    notes: Optional[str] = Field(default=None, max_length=500, description="Additional notes")


# Schema for incoming data (POST)
class JobAppCreate(JobAppBase):
    pass


# Schema for outgoing data (GET)
class JobApp(JobAppBase):
    id: int

    model_config = {
        "from_attributes": True
    }


# For partial updates (PATCH/PUT)
# This lets the user update only one field
# without sending the whole object.
class JobAppUpdate:
    company: Optional[str] = None,
    position: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    applied_date: Optional[date] = None
    link: Optional[str] = None
    notes: Optional[str] = None
