# Maps DB to tables.
# The file is responsible for Object-Relational Mapping -
# defining how Python classes = database tables.

from sqlalchemy import Column, Integer, String, Date
from app.db.database import Base
from app.schemas.job_schemas import ApplicationStatus
from sqlalchemy import Enum as SQLEnum


class JobApplication(Base):
    __tablename__ = "job_applications"
    # primary key column
    id = Column(Integer, primary_key=True, index=True)
    # other columns
    company = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)
    location = Column(String(100), nullable=True)
    status = Column(SQLEnum(ApplicationStatus, name="application_status"), nullable=True)
    applied_date = Column(Date, nullable=False)
    link = Column(String(2048), nullable=True)
    notes = Column(String(500), nullable=True)
