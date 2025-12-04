import bcrypt
import secrets
from fastapi import HTTPException, status, Request
from typing import Optional
from datetime import datetime, timedelta
from config.settings import settings

SECRET_KEY = settings.SECRET_KEY
SESSION_DURATION = timedelta(hours=settings.SESSION_DURATION_HOURS)

USERS_DB = {
    "jutiapa1": {
        "password_hash": "$2b$12$KQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Jutiapa 1",
        "sucursal": "Jutiapa 1",
        "rol": "sucursal",
        "password_plain": "jut1pass"
    },
    "jutiapa2": {
        "password_hash": "$2b$12$LQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Jutiapa 2",
        "sucursal": "Jutiapa 2",
        "rol": "sucursal",
        "password_plain": "jut2pass"
    },
    "jutiapa3": {
        "password_hash": "$2b$12$MQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Jutiapa 3",
        "sucursal": "Jutiapa 3",
        "rol": "sucursal",
        "password_plain": "jut3pass"
    },
    "progreso": {
        "password_hash": "$2b$12$NQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Progreso",
        "sucursal": "Progreso",
        "rol": "sucursal",
        "password_plain": "progpass"
    },
    "quesada": {
        "password_hash": "$2b$12$OQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Quesada",
        "sucursal": "Quesada",
        "rol": "sucursal",
        "password_plain": "quespass"
    },
    "acatempa": {
        "password_hash": "$2b$12$PQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Acatempa",
        "sucursal": "Acatempa",
        "rol": "sucursal",
        "password_plain": "acatpass"
    },
    "yupiltepeque": {
        "password_hash": "$2b$12$QQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Yupiltepeque",
        "sucursal": "Yupiltepeque",
        "rol": "sucursal",
        "password_plain": "yupepass"
    },
    "atescatempa": {
        "password_hash": "$2b$12$RQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Atescatempa",
        "sucursal": "Atescatempa",
        "rol": "sucursal",
        "password_plain": "atespass"
    },
    "adelanto": {
        "password_hash": "$2b$12$SQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Adelanto",
        "sucursal": "Adelanto",
        "rol": "sucursal",
        "password_plain": "adelpass"
    },
    "jerez": {
        "password_hash": "$2b$12$TQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Jeréz",
        "sucursal": "Jeréz",
        "rol": "sucursal",
        "password_plain": "jerpass"
    },
    "comapa": {
        "password_hash": "$2b$12$UQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Comapa",
        "sucursal": "Comapa",
        "rol": "sucursal",
        "password_plain": "comapass"
    },
    "carina": {
        "password_hash": "$2b$12$VQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Carina",
        "sucursal": "Carina",
        "rol": "sucursal",
        "password_plain": "caripass"
    },
    "admin": {
        "password_hash": "$2b$12$WQF8vX5zJ5YqZ8vX5zJ5YuOqZ8vX5zJ5YqZ8vX5zJ5YqZ8vX5zJ5Yu",
        "nombre": "Administrador",
        "sucursal": None,
        "rol": "admin",
        "password_plain": "admin123"
    }
}

def _initialize_passwords():
    """Initialize password hashes on first import"""
    for username, user_data in USERS_DB.items():
        if 'password_plain' in user_data:
            user_data['password_hash'] = bcrypt.hashpw(user_data['password_plain'].encode(), bcrypt.gensalt()).decode()

_initialize_passwords()

class LoginAttempts:
    def __init__(self):
        self.attempts = {}
    
    def check_attempt(self, username: str) -> bool:
        now = datetime.now()
        if username in self.attempts:
            attempt_time, count = self.attempts[username]
            if (now - attempt_time).seconds < settings.LOGIN_TIMEOUT_SECONDS and count >= settings.MAX_LOGIN_ATTEMPTS:
                return False
            if (now - attempt_time).seconds > settings.LOGIN_TIMEOUT_SECONDS:
                self.attempts[username] = (now, 1)
            else:
                self.attempts[username] = (attempt_time, count + 1)
        else:
            self.attempts[username] = (now, 1)
        return True

login_attempts = LoginAttempts()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def verificar_credenciales(username: str, password: str) -> Optional[dict]:
    if not login_attempts.check_attempt(username):
        return None
    
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
    if session_token != expected_token or username not in USERS_DB:
        return None

    return {
        "username": username,
        "sucursal": sucursal,
        "rol": rol
    }

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
