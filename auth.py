from fastapi import HTTPException, status, Request
from typing import Optional
import hashlib
import os

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

SECRET_KEY = os.getenv("SECRET_KEY", "mipastel_secret_key_2024_cambiar_en_produccion")


def verificar_credenciales(username: str, password: str) -> bool:
    if username not in USERS:
        return False
    return USERS[username]["password"] == password


def hash_session(username: str) -> str:
    return hashlib.sha256(f"{username}{SECRET_KEY}".encode()).hexdigest()


def verificar_sesion(request: Request) -> Optional[str]:
    session_token = request.cookies.get("session_token")
    username = request.cookies.get("username")

    if not session_token or not username:
        return None

    expected_token = hash_session(username)
    if session_token == expected_token and username in USERS:
        return username

    return None


def requiere_autenticacion(request: Request) -> str:
    username = verificar_sesion(request)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado. Inicia sesión primero.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


def crear_respuesta_con_sesion(response, username: str):
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
    response.delete_cookie("session_token")
    response.delete_cookie("username")
    return response