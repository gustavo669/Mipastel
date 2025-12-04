import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.DB_SERVER = os.getenv("DB_SERVER", "(localdb)\\MSSQLLocalDB")
        self.DB_USER = os.getenv("DB_USER", "")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        self.DB_NAME_NORMALES = os.getenv("DB_NAME_NORMALES", "MiPastel")
        self.DB_NAME_CLIENTES = os.getenv("DB_NAME_CLIENTES", "MiPastel_Clientes")
        self.DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
        
        self.SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())
        self.ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")
        
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "5000"))
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5000,http://127.0.0.1:5000")
        self.ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_str.split(",")]
        
        self.SESSION_DURATION_HOURS = int(os.getenv("SESSION_DURATION_HOURS", "8"))
        self.MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
        self.LOGIN_TIMEOUT_SECONDS = int(os.getenv("LOGIN_TIMEOUT_SECONDS", "300"))
        
        self.BASE_DIR = Path(__file__).parent.parent.absolute()
        self.STATIC_DIR = self.BASE_DIR / "static"
        self.UPLOADS_DIR = self.STATIC_DIR / "uploads"
        self.TEMPLATES_DIR = self.BASE_DIR / "templates"
        self.LOGS_DIR = self.BASE_DIR / "logs"
        
        os.makedirs(self.UPLOADS_DIR, exist_ok=True)
        os.makedirs(self.LOGS_DIR, exist_ok=True)

settings = Settings()
