import pytest
from fastapi.testclient import TestClient

from api.auth import hash_session


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)

@pytest.fixture
def db():
    from api.database import DatabaseManager
    return DatabaseManager()

@pytest.fixture
def authenticated_client(client):
    """Create a client with authenticated session for a regular user."""
    username = "jutiapa1"
    session_token = hash_session(username)

    client.cookies.set("session_token", session_token)
    client.cookies.set("username", username)
    client.cookies.set("sucursal", "Jutiapa 1")
    client.cookies.set("rol", "sucursal")

    return client

@pytest.fixture
def admin_client(client):
    """Create a client with authenticated session for admin."""
    username = "admin"
    session_token = hash_session(username)

    client.cookies.set("session_token", session_token)
    client.cookies.set("username", username)
    client.cookies.set("sucursal", "")
    client.cookies.set("rol", "admin")

    return client