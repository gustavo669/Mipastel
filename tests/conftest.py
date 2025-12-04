import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)

@pytest.fixture
def db():
    from api.database import DatabaseManager
    return DatabaseManager()
