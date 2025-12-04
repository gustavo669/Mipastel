import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_login_page():
    response = client.get("/login")
    assert response.status_code == 200

def test_login_exitoso():
    response = client.post("/login", data={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 302
    assert "session_token" in response.cookies

def test_login_fallido():
    response = client.post("/login", data={
        "username": "admin",
        "password": "contraseña_incorrecta"
    })
    assert response.status_code == 200

def test_obtener_precio():
    response = client.get("/api/obtener-precio?sabor=Fresas&tamano=Mediano")
    assert response.status_code == 200
    data = response.json()
    assert "precio" in data

def test_acceso_sin_autenticacion():
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["location"] == "/login"
