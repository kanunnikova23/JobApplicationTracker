# Maps DB to tables.

from sqlalchemy import Column, Integer, String, Date
from app.database import Base


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, index=True)
    position = Column(String)
    status = Column(String)  # e.g. applied, interviewed, rejected, offer
    applied_date = Column(Date)
    link = Column(String, nullable=True)
    notes = Column(String, nullable=True)
