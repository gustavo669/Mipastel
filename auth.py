from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse
from typing import Optional
import secrets
import hashlib

USERS = {
    "Marvin": {
        "password": "mipastel123",
        "nombre": "Marvin"
    },
    "usuario1": {
        "password": "mipastel123",
        "nombre": "Marvin"
    }
}


SECRET_KEY = "123456789"


def verificar_credenciales(username: str, password: str) -> bool:
    """Verifica si las credenciales son correctas"""
    if username not in USERS:
        return False
    return USERS[username]["password"] == password


def hash_session(username: str) -> str:
    """Crea un hash de sesión único"""
    return hashlib.sha256(f"{username}{SECRET_KEY}".encode()).hexdigest()


def verificar_sesion(request: Request) -> Optional[str]:
    """Verifica si existe una sesión válida en las cookies"""
    session_token = request.cookies.get("session_token")
    username = request.cookies.get("username")

    if not session_token or not username:
        return None

    expected_token = hash_session(username)
    if session_token == expected_token and username in USERS:
        return username

    return None


def requiere_autenticacion(request: Request) -> str:
    """
    Dependency que requiere que el usuario esté autenticado.
    Úsalo en las rutas que quieras proteger.
    """
    username = verificar_sesion(request)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado. Inicia sesión primero.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


def crear_respuesta_con_sesion(response, username: str):
    """Agrega las cookies de sesión a una respuesta"""
    session_token = hash_session(username)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=3600 * 24 * 7,
        samesite="lax"
    )
    response.set_cookie(
        key="username",
        value=username,
        httponly=True,
        max_age=3600 * 24 * 7,
        samesite="lax"
    )
    return response


def cerrar_sesion(response):
    """Elimina las cookies de sesión"""
    response.delete_cookie("session_token")
    response.delete_cookie("username")
    return response