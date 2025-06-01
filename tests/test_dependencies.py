import pytest
from httpx import AsyncClient
from app.main import app  # The actual FastAPI app object being tested


@pytest.mark.anyio
async def test_async_db_dependency_injection(async_client: AsyncClient):
    response = await async_client.get("/users/")
    assert response.status_code in [200, 401, 403], f"Unexpected response: {response.status_code} - {response.text}"
