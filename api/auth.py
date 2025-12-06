import bcrypt
import secrets
from fastapi import HTTPException, status, Request
from typing import Optional
from datetime import datetime, timedelta
from config.settings import settings
import os
import json

SECRET_KEY = settings.SECRET_KEY
SESSION_DURATION = timedelta(hours=settings.SESSION_DURATION_HOURS)

# Archivo para guardar los hashes generados
HASHES_FILE = os.path.join(os.path.dirname(__file__), ".password_hashes.json")

# Contraseñas por defecto (solo se usan para generar hashes la primera vez)
DEFAULT_PASSWORDS = {
    "jutiapa1": "jut1pass",
    "jutiapa2": "jut2pass",
    "jutiapa3": "jut3pass",
    "progreso": "progpass",
    "quesada": "quespass",
    "acatempa": "acatpass",
    "yupiltepeque": "yupepass",
    "atescatempa": "atespass",
    "adelanto": "adelpass",
    "jerez": "jerpass",
    "comapa": "comapass",
    "carina": "caripass",
    "admin": "admin123"
}

def _load_or_generate_hashes():
    """Cargar hashes existentes o generar nuevos si no existen"""
    if os.path.exists(HASHES_FILE):
        try:
            with open(HASHES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Generar nuevos hashes
    print("Generando hashes de contraseñas por primera vez...")
    hashes = {}
    for username, password in DEFAULT_PASSWORDS.items():
        hash_value = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        hashes[username] = hash_value
        print(f"  {username}: OK")
    
    # Guardar para uso futuro
    try:
        with open(HASHES_FILE, 'w') as f:
            json.dump(hashes, f, indent=2)
        print(f"Hashes guardados en {HASHES_FILE}")
    except Exception as e:
        print(f"No se pudieron guardar los hashes: {e}")
    
    return hashes

# Cargar o generar hashes
_PASSWORD_HASHES = _load_or_generate_hashes()

# Base de datos de usuarios
USERS_DB = {
    "jutiapa1": {
        "password_hash": _PASSWORD_HASHES.get("jutiapa1"),
        "nombre": "Jutiapa 1",
        "sucursal": "Jutiapa 1",
        "rol": "sucursal"
    },
    "jutiapa2": {
        "password_hash": _PASSWORD_HASHES.get("jutiapa2"),
        "nombre": "Jutiapa 2",
        "sucursal": "Jutiapa 2",
        "rol": "sucursal"
    },
    "jutiapa3": {
        "password_hash": _PASSWORD_HASHES.get("jutiapa3"),
        "nombre": "Jutiapa 3",
        "sucursal": "Jutiapa 3",
        "rol": "sucursal"
    },
    "progreso": {
        "password_hash": _PASSWORD_HASHES.get("progreso"),
        "nombre": "Progreso",
        "sucursal": "Progreso",
        "rol": "sucursal"
    },
    "quesada": {
        "password_hash": _PASSWORD_HASHES.get("quesada"),
        "nombre": "Quesada",
        "sucursal": "Quesada",
        "rol": "sucursal"
    },
    "acatempa": {
        "password_hash": _PASSWORD_HASHES.get("acatempa"),
        "nombre": "Acatempa",
        "sucursal": "Acatempa",
        "rol": "sucursal"
    },
    "yupiltepeque": {
        "password_hash": _PASSWORD_HASHES.get("yupiltepeque"),
        "nombre": "Yupiltepeque",
        "sucursal": "Yupiltepeque",
        "rol": "sucursal"
    },
    "atescatempa": {
        "password_hash": _PASSWORD_HASHES.get("atescatempa"),
        "nombre": "Atescatempa",
        "sucursal": "Atescatempa",
        "rol": "sucursal"
    },
    "adelanto": {
        "password_hash": _PASSWORD_HASHES.get("adelanto"),
        "nombre": "Adelanto",
        "sucursal": "Adelanto",
        "rol": "sucursal"
    },
    "jerez": {
        "password_hash": _PASSWORD_HASHES.get("jerez"),
        "nombre": "Jeréz",
        "sucursal": "Jeréz",
        "rol": "sucursal"
    },
    "comapa": {
        "password_hash": _PASSWORD_HASHES.get("comapa"),
        "nombre": "Comapa",
        "sucursal": "Comapa",
        "rol": "sucursal"
    },
    "carina": {
        "password_hash": _PASSWORD_HASHES.get("carina"),
        "nombre": "Carina",
        "sucursal": "Carina",
        "rol": "sucursal"
    },
    "admin": {
        "password_hash": _PASSWORD_HASHES.get("admin"),
        "nombre": "Administrador",
        "sucursal": None,
        "rol": "admin"
    }
}

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
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False

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
    """
    Dependency to require authentication for endpoints.
    
    Args:
        request: FastAPI request object
        
    Returns:
        dict: User data containing username, sucursal, and rol
        
    Raises:
        HTTPException: 401 if user is not authenticated
    """
    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_data

def verificar_permiso_sucursal(user_data: dict, sucursal_requerida: str) -> bool:
    """
    Verify if user has permission to access data from a specific branch.
    
    Args:
        user_data: User data from authentication
        sucursal_requerida: Branch name that needs to be accessed
        
    Returns:
        bool: True if user has permission, False otherwise
        
    Note:
        - Admin users can access all branches
        - Regular users can only access their assigned branch
    """
    if user_data.get("rol") == "admin":
        return True
    
    return user_data.get("sucursal") == sucursal_requerida

def requiere_permiso_sucursal(user_data: dict, sucursal: str) -> None:
    """
    Dependency to require branch permission for endpoints.
    
    Args:
        user_data: User data from authentication
        sucursal: Branch name to check permission for
        
    Raises:
        HTTPException: 403 if user doesn't have permission for the branch
    """
    if not verificar_permiso_sucursal(user_data, sucursal):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tiene permiso para acceder a datos de la sucursal '{sucursal}'"
        )

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
