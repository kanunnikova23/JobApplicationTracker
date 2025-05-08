# Maps DB to tables.
# The file is responsible for Object-Relational Mapping -
# defining how Python classes = database tables.

from sqlalchemy import Column, Integer, String, Date
from app.database import Base


class JobApplication(Base):
    __tablename__ = "job_applications"
    # primary key column
    id = Column(Integer, primary_key=True, index=True)
    # other columns
    company = Column(String, index=True)
    position = Column(String)
    location = Column(String, nullable=True)
    status = Column(String)  # e.g. applied, interviewed, rejected, offer
    applied_date = Column(Date)
    link = Column(String, nullable=True)
    notes = Column(String, nullable=True)
