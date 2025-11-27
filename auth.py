import bcrypt
import secrets
import os
from fastapi import HTTPException, status, Request
from typing import Optional
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
SESSION_DURATION = timedelta(hours=8)

USERS_DB = {
    "jutiapa1": {
        "password_hash": bcrypt.hashpw("jut1pass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Jutiapa 1",
        "sucursal": "Jutiapa 1",
        "rol": "sucursal"
    },
    "jutiapa2": {
        "password_hash": bcrypt.hashpw("jut2pass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Jutiapa 2",
        "sucursal": "Jutiapa 2",
        "rol": "sucursal"
    },
    "jutiapa3": {
        "password_hash": bcrypt.hashpw("jut3pass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Jutiapa 3",
        "sucursal": "Jutiapa 3",
        "rol": "sucursal"
    },
    "progreso": {
        "password_hash": bcrypt.hashpw("progpass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Progreso",
        "sucursal": "Progreso",
        "rol": "sucursal"
    },
    "quesada": {
        "password_hash": bcrypt.hashpw("quespass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Quesada",
        "sucursal": "Quesada",
        "rol": "sucursal"
    },
    "acatempa": {
        "password_hash": bcrypt.hashpw("acatpass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Acatempa",
        "sucursal": "Acatempa",
        "rol": "sucursal"
    },
    "yupiltepeque": {
        "password_hash": bcrypt.hashpw("yupepass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Yupiltepeque",
        "sucursal": "Yupiltepeque",
        "rol": "sucursal"
    },
    "atescatempa": {
        "password_hash": bcrypt.hashpw("atespass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Atescatempa",
        "sucursal": "Atescatempa",
        "rol": "sucursal"
    },
    "adelanto": {
        "password_hash": bcrypt.hashpw("adelpass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Adelanto",
        "sucursal": "Adelanto",
        "rol": "sucursal"
    },
    "jerez": {
        "password_hash": bcrypt.hashpw("jerpass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Jeréz",
        "sucursal": "Jeréz",
        "rol": "sucursal"
    },
    "comapa": {
        "password_hash": bcrypt.hashpw("comapass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Comapa",
        "sucursal": "Comapa",
        "rol": "sucursal"
    },
    "carina": {
        "password_hash": bcrypt.hashpw("caripass".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Carina",
        "sucursal": "Carina",
        "rol": "sucursal"
    },
    "admin": {
        "password_hash": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
        "nombre": "Administrador",
        "sucursal": None,
        "rol": "admin"
    }
}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def verificar_credenciales(username: str, password: str) -> Optional[dict]:
    if username not in USERS_DB:
        return None

    user = USERS_DB[username]
    if verify_password(password, user["password_hash"]):
        return {
            "username": username,
            "nombre": user["nombre"],
            "sucursal": user["sucursal"],
            "rol": user["rol"]
        }
    return None


def hash_session(username: str) -> str:
    import hashlib
    return hashlib.sha256(f"{username}{SECRET_KEY}".encode()).hexdigest()


def verificar_sesion(request: Request) -> Optional[dict]:
    session_token = request.cookies.get("session_token")
    username = request.cookies.get("username")
    sucursal = request.cookies.get("sucursal")
    rol = request.cookies.get("rol")

    if not session_token or not username:
        return None

    expected_token = hash_session(username)
    if session_token == expected_token and username in USERS_DB:
        return {
            "username": username,
            "sucursal": sucursal,
            "rol": rol
        }

    return None


def requiere_autenticacion(request: Request) -> dict:
    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_data


def crear_respuesta_con_sesion(response, user_data: dict):
    session_token = hash_session(user_data["username"])
    max_age = int(SESSION_DURATION.total_seconds())

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=max_age,
        samesite="lax"
    )
    response.set_cookie(
        key="username",
        value=user_data["username"],
        httponly=True,
        max_age=max_age,
        samesite="lax"
    )
    response.set_cookie(
        key="sucursal",
        value=user_data["sucursal"] or "",
        httponly=True,
        max_age=max_age,
        samesite="lax"
    )
    response.set_cookie(
        key="rol",
        value=user_data["rol"],
        httponly=True,
        max_age=max_age,
        samesite="lax"
    )
    return response


def cerrar_sesion(response):
    response.delete_cookie("session_token")
    response.delete_cookie("username")
    response.delete_cookie("sucursal")
    response.delete_cookie("rol")
    return response