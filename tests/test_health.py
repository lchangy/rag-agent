from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from core.db import get_database_url


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_settings_provide_default_database_url() -> None:
    settings = Settings(
        openai_api_key="test-key",
        database_host="localhost",
        database_user="postgres",
        database_password="postgres",
        database_name="rag_agent",
    )

    assert get_database_url(settings) == "postgresql+psycopg://postgres:postgres@localhost:5433/rag_agent"
