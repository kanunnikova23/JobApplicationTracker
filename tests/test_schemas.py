# Schema validation tests - Edge Cases
from pydantic import ValidationError
from app.schemas.job_schemas import JobAppCreate
import pytest
from datetime import date
from app.schemas.job_schemas import ApplicationStatus


def test_schema_valid_data():
    job = JobAppCreate(
        company="Airbnb",
        position="SWE",
        status="applied",
        applied_date=date.today()
    )
    assert job.position == "SWE"


def test_valid_job_app_schema():
    job = JobAppCreate(
        company="OpenAI",
        position="Backend Engineer",
        location="Remote",
        status=ApplicationStatus.APPLIED,
        applied_date=date.today(),
        link="https://openai.com/careers",
        notes="Very exciting!"
    )
    assert job.company == "OpenAI"


def test_schema_missing_required():
    with pytest.raises(ValueError):
        JobAppCreate(position="Dev", status="applied", applied_date=date.today())


def test_invalid_company_name_length():
    with pytest.raises(ValidationError):
        JobAppCreate(
            company="",  # invalid: too short
            position="Backend Engineer",
            location="Remote",
            status=ApplicationStatus.APPLIED,
            applied_date=date.today(),
            link="https://openai.com/careers",
            notes="Nice"
        )


def test_invalid_link():
    with pytest.raises(ValidationError):
        JobAppCreate(
            company="OpenAI",
            position="Engineer",
            location="Remote",
            status=ApplicationStatus.APPLIED,
            applied_date=date.today(),
            link="not-a-valid-url",  # invalid
            notes="Nice"
        )
