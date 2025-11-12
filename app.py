import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))
print(f"Directorio base: {BASE_DIR}")

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
TEMPLATES_DIR = BASE_DIR / "templates"
REPORTS_DIR = BASE_DIR / "pdf_reports"

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

try:
    from routers import normales, clientes, admin
except ImportError as e:
    from fastapi import APIRouter
    print(f"Advertencia: No se pudieron importar routers: {e}")
    normales = APIRouter(prefix="/normales", tags=["Normales"])
    clientes = APIRouter(prefix="/clientes", tags=["Clientes"])
    admin = APIRouter(prefix="/admin", tags=["Admin"])

try:
    from config import (
        SABORES_NORMALES,
        SABORES_CLIENTES,
        TAMANOS_NORMALES,
        TAMANOS_CLIENTES,
        SUCURSALES,
    )
except ImportError as e:
    print(f"ERROR al importar configuración: {e}")
    SABORES_NORMALES = ["Error"]
    SABORES_CLIENTES = ["Error"]
    TAMANOS_NORMALES = ["Error"]
    TAMANOS_CLIENTES = ["Error"]
    SUCURSALES = ["Error"]

app = FastAPI(
    title="Mi Pastel — Sistema de Pedidos",
    description="Sistema web para ingreso de pedidos de pasteles",
    version="2.0.0"
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


app.include_router(normales.router)
app.include_router(clientes.router)
app.include_router(admin.router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Página principal con formularios de ingreso
    """
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
    """
    Devuelve el precio automático según sabor y tamaño.
    Si el sabor es 'Otro', se permite manejo personalizado en frontend.
    """
    try:

        if sabor.lower() == "otro":
            return {
                "precio": 0,
                "sabor": sabor,
                "tamano": tamano,
                "encontrado": False,
                "detalle": "Use la opción 'Otro' para precios personalizados."
            }

        from database import obtener_precio_db
        precio = obtener_precio_db(sabor, tamano)

        if precio and precio > 0:
            return {
                "precio": precio,
                "sabor": sabor,
                "tamano": tamano,
                "encontrado": True
            }
        else:
            return {
                "precio": 0,
                "sabor": sabor,
                "tamano": tamano,
                "encontrado": False,
                "detalle": "No se encontró precio registrado para esa combinación."
            }

    except Exception as e:
        print(f"Error en API /api/obtener-precio: {e}")
        return {
            "precio": 0,
            "sabor": sabor,
            "tamano": tamano,
            "encontrado": False,
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """
    Verifica que el servidor esté en ejecución
    """
    return JSONResponse({
        "status": "ok",
        "service": "Mi Pastel API",
        "version": "2.0.0",
        "endpoints": {
            "web": "http://127.0.0.1:5000",
            "api_precio": "/api/obtener-precio",
            "admin": "/admin"
        }
    })

@app.on_event("startup")
async def startup_event():
    print("Servidor Mi Pastel iniciado correctamente")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=5000,
        reload=True,
        log_level="info"
    )
