"""
Servidor FastAPI principal - Mi Pastel v2.0
CORREGIDO - Versión funcional
"""
import sys
import os
from pathlib import Path

# Configurar paths ABSOLUTOS
BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))

print(f"📍 Directorio base: {BASE_DIR}")

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# --- CORRECCIÓN ---
# Crear directorios directamente en la raíz (o donde estén tus plantillas)
# Asumimos que 'static' y 'templates' están en BASE_DIR
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
TEMPLATES_DIR = BASE_DIR / "templates"
REPORTS_DIR = BASE_DIR / "pdf_reports" # Movido aquí por consistencia

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
# --- FIN CORRECCIÓN ---

# Importar routers
try:
    from routers import normales, clientes, admin
    print("✅ Routers importados correctamente")
except ImportError as e:
    print(f"❌ Error importando routers: {e}")
    # Crear routers básicos si no existen
    from fastapi import APIRouter
    normales = APIRouter(prefix="/normales", tags=["Normales"])
    clientes = APIRouter(prefix="/clientes", tags=["Clientes"])
    admin = APIRouter(prefix="/admin", tags=["Admin"])

# ==========================================================
# <<-- MODIFICACIÓN IMPORTANTE -->>
# Importamos las listas maestras desde config.py
try:
    from config import SABORES_NORMALES, SABORES_CLIENTES, TAMANOS, SUCURSALES
except ImportError:
    print("❌ Error: No se encontró config.py. Usando listas de emergencia.")
    # Mantener esto como fallback por si acaso
    SABORES_NORMALES = ["Error"]
    SABORES_CLIENTES = ["Error"]
    TAMANOS = ["Error"]
    SUCURSALES = ["Error"]
# ==========================================================


app = FastAPI(
    title="Mi Pastel — Sistema de Pedidos",
    description="Sistema web para ingreso de pedidos de pasteles",
    version="2.0.0"
)

# --- CORRECCIÓN ---
# Montar archivos estáticos desde la URL /static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
# --- FIN CORRECCIÓN ---

# Incluir routers
app.include_router(normales.router)
app.include_router(clientes.router)
app.include_router(admin.router)

# Las listas de abajo ya no están hard-coded
# Vienen del import de config.py

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal con formularios de ingreso"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "sabores_normales": SABORES_NORMALES,
        "sabores_clientes": SABORES_CLIENTES,
        "tamanos": TAMANOS,
        "sucursales": SUCURSALES
    })

@app.get("/api/obtener-precio")
async def api_obtener_precio(sabor: str, tamano: str):
    """Endpoint para obtener precio automático"""
    try:
        from database import obtener_precio_db
        precio = obtener_precio_db(sabor, tamano)
        return {
            "precio": precio,
            "sabor": sabor,
            "tamano": tamano,
            "encontrado": precio > 0
        }
    except Exception as e:
        return {
            "precio": 0,
            "sabor": sabor,
            "tamano": tamano,
            "encontrado": False,
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Endpoint de salud"""
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
    """Ejecutar al iniciar el servidor"""
    print("=" * 60)
    print("🧁 Mi Pastel - Servidor Web Iniciado v2.0")
    print(f"📍 URL: http://127.0.0.1:5000")
    print(f"📊 Health: http://127.0.0.1:5000/health")
    print(f"👁️  Admin: http://127.0.0.1:5000/admin")
    print("=" * 60)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=5000,
        reload=True,
        log_level="info"
    )