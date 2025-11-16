import sys
import os
import socket
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).parent.absolute()
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
TEMPLATES_DIR = BASE_DIR / "templates"
REPORTS_DIR = BASE_DIR / "pdf_reports"

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

try:
    from routers import normales, clientes, admin
    from config import (
        SABORES_NORMALES, SABORES_CLIENTES,
        TAMANOS_NORMALES, TAMANOS_CLIENTES, SUCURSALES
    )
except ImportError as e:
    print(f"Advertencia de Importación: {e}")
    from fastapi import APIRouter
    normales = clientes = admin = APIRouter()
    SABORES_NORMALES = SABORES_CLIENTES = ["Error Carga"]
    TAMANOS_NORMALES = TAMANOS_CLIENTES = ["Error Carga"]
    SUCURSALES = ["Error Carga"]

def get_local_ip():
    """Obtiene la IP real de la máquina en la red WiFi"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Mensaje al iniciar la API"""
    local_ip = get_local_ip()
    print(f"Desde tu celular entra a:  http://{local_ip}:5000")
    print(f"Desde esta PC:             http://127.0.0.1:5000")
    yield

app = FastAPI(
    title="Mi Pastel - Sistema de Gestión",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.include_router(normales.router)
app.include_router(clientes.router)
app.include_router(admin.router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Pantalla principal de pedidos"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "sabores_normales": SABORES_NORMALES,
        "sabores_clientes": SABORES_CLIENTES,
        "tamanos_normales": TAMANOS_NORMALES,
        "tamanos_clientes": TAMANOS_CLIENTES,
        "sucursales": SUCURSALES
    })

@app.get("/api/obtener-precio")
async def api_obtener_precio(sabor: str, tamano: str):
    """API para cálculo de precios"""
    try:
        if sabor.lower() == "otro":
            return {"precio": 0, "encontrado": False, "detalle": "Precio manual requerido"}

        from database import obtener_precio_db
        precio = obtener_precio_db(sabor, tamano)

        if precio and precio > 0:
            return {"precio": precio, "encontrado": True}
        else:
            return {"precio": 0, "encontrado": False, "detalle": "No registrado"}
    except Exception as e:
        print(f"Error DB: {e}")
        return {"precio": 0, "encontrado": False, "error": str(e)}

@app.get("/health")
async def health_check():
    """Health check para verificar conexión desde celular"""
    return JSONResponse({
        "status": "ok",
        "ip_servidor": get_local_ip(),
        "mensaje": "Conexión exitosa con el servidor de pedidos"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)