# Defines what data should look like (input/output).
from pydantic import BaseModel
from datetime import date
from typing import Optional


class JobAppBase(BaseModel):
    company: str
    position: str
    location: Optional[str] = None
    status: str
    applied_date: date
    link: Optional[str] = None
    notes: Optional[str] = None


class JobAppCreate(JobAppBase):
    pass


class JobApp(JobAppBase):
    id: int

    model_config = {
        "from_attributes": True
    }
