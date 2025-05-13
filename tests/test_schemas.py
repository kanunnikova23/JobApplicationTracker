# Schema validation tests - Edge Cases

from app.schemas.job_schemas import JobAppCreate
import pytest
from datetime import date


def test_schema_valid_data():
    job = JobAppCreate(
        company="Airbnb",
        position="SWE",
        status="applied",
        applied_date=date.today()
    )
    assert job.company == "Airbnb"


def test_schema_missing_required():
    with pytest.raises(ValueError):
        JobAppCreate(position="Dev", status="applied", applied_date=date.today())
