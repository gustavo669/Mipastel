import os
import socket
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, date
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging

from auth import (
    verificar_credenciales,
    crear_respuesta_con_sesion,
    cerrar_sesion,
    verificar_sesion,
    requiere_autenticacion
)
from pdf_reportes import generar_pdf_listas, generar_pdf_ventas, generar_pdf_rango_fechas

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.absolute()
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
TEMPLATES_DIR = BASE_DIR / "templates"

os.makedirs(UPLOADS_DIR, exist_ok=True)

try:
    from routers import normales, clientes, admin, pedidos_api
    from config import (
        SABORES_NORMALES, SABORES_CLIENTES,
        TAMANOS_NORMALES, TAMANOS_CLIENTES, SUCURSALES
    )
    print("✓ Todos los routers importados correctamente")
except ImportError as e:
    print(f"Advertencia de Importación: {e}")
    from fastapi import APIRouter
    normales = clientes = admin = pedidos_api = APIRouter()
    SABORES_NORMALES = SABORES_CLIENTES = ["Error Carga"]
    TAMANOS_NORMALES = TAMANOS_CLIENTES = ["Error Carga"]
    SUCURSALES = ["Error Carga"]


def get_local_ip():
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
    local_ip = get_local_ip()
    print(f"\n{'='*60}")
    print(f"MI PASTEL - Sistema de Gestión")
    print(f"{'='*60}")
    print(f"✓ Servidor iniciado en: http://{local_ip}:5000")
    print(f"✓ Acceso local: http://127.0.0.1:5000")
    print(f"✓ Acceso desde red WiFi: http://{local_ip}:5000")
    print(f"{'='*60}\n")
    yield

app = FastAPI(
    title="Mi Pastel - Sistema de Gestión",
    version="2.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Include routers
app.include_router(normales.router)
app.include_router(clientes.router)
app.include_router(admin.router)
app.include_router(pedidos_api.router)

print("✓ Routers registrados:")
print("  - /normales")
print("  - /clientes")
print("  - /admin")
print("  - /api/pedidos")


@app.get("/login", response_class=HTMLResponse)
async def mostrar_login(request: Request, error: str = None):
    user_data = verificar_sesion(request)
    if user_data:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error
    })


@app.post("/login")
async def procesar_login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
):
    user_data = verificar_credenciales(username, password)
    if user_data:
        response = RedirectResponse(url="/", status_code=302)
        crear_respuesta_con_sesion(response, user_data)
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Usuario o contraseña incorrectos"
        })


@app.get("/logout")
async def cerrar_sesion_usuario(request: Request):
    response = RedirectResponse(url="/login", status_code=302)
    cerrar_sesion(response)
    return response


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user_data = verificar_sesion(request)
    if not user_data:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "sabores_normales": SABORES_NORMALES,
        "sabores_clientes": SABORES_CLIENTES,
        "tamanos_normales": TAMANOS_NORMALES,
        "tamanos_clientes": TAMANOS_CLIENTES,
        "sucursales": SUCURSALES,
        "user_data": user_data
    })


@app.get("/api/obtener-precio")
async def api_obtener_precio(sabor: str, tamano: str):
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


@app.get("/reportes/pdf")
async def generar_reporte_pdf(request: Request, fecha: str, sucursal: str = None):
    try:
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"error": "Formato de fecha inválido. Use YYYY-MM-DD"}
            )

        nombre_archivo = generar_pdf_listas(target_date=fecha_obj, sucursal=sucursal if sucursal else None)

        if not os.path.exists(nombre_archivo):
            return JSONResponse(
                status_code=500,
                content={"error": "No se pudo generar el PDF"}
            )

        nombre_descarga = f'Listas_MiPastel_{fecha}'
        if sucursal:
            nombre_descarga += f'_{sucursal}'
        nombre_descarga += '.pdf'

        return FileResponse(
            path=nombre_archivo,
            media_type='application/pdf',
            filename=nombre_descarga
        )

    except Exception as e:
        logger.error(f"Error al generar PDF de listas: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al generar el reporte: {str(e)}"}
        )


@app.get("/reportes/rango-pdf")
async def generar_reporte_rango_pdf(
        request: Request,
        fecha_inicio: str,
        fecha_fin: str,
        sucursal: str = None
):
    try:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"error": "Formato de fecha inválido. Use YYYY-MM-DD"}
            )

        if fecha_fin_obj < fecha_inicio_obj:
            return JSONResponse(
                status_code=400,
                content={"error": "La fecha fin debe ser posterior a la fecha inicio"}
            )

        nombre_archivo = generar_pdf_rango_fechas(
            fecha_inicio=fecha_inicio_obj,
            fecha_fin=fecha_fin_obj,
            sucursal=sucursal if sucursal else None
        )

        if not os.path.exists(nombre_archivo):
            return JSONResponse(
                status_code=500,
                content={"error": "No se pudo generar el PDF"}
            )

        nombre_descarga = f'Reporte_{fecha_inicio}_a_{fecha_fin}'
        if sucursal:
            nombre_descarga += f'_{sucursal}'
        nombre_descarga += '.pdf'

        return FileResponse(
            path=nombre_archivo,
            media_type='application/pdf',
            filename=nombre_descarga
        )

    except Exception as e:
        logger.error(f"Error al generar PDF de rango: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al generar el reporte: {str(e)}"}
        )


@app.get("/reportes/ventas-pdf")
async def generar_reporte_ventas_pdf(request: Request, fecha: str, sucursal: str = None):
    try:
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"error": "Formato de fecha inválido. Use YYYY-MM-DD"}
            )

        nombre_archivo = generar_pdf_ventas(target_date=fecha_obj, sucursal=sucursal if sucursal else None)

        if not os.path.exists(nombre_archivo):
            return JSONResponse(
                status_code=500,
                content={"error": "No se pudo generar el PDF de ventas"}
            )

        nombre_descarga = f'Ventas_MiPastel_{fecha}'
        if sucursal:
            nombre_descarga += f'_{sucursal}'
        nombre_descarga += '.pdf'

        return FileResponse(
            path=nombre_archivo,
            media_type='application/pdf',
            filename=nombre_descarga
        )

    except Exception as e:
        logger.error(f"Error al generar PDF de ventas: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al generar el reporte de ventas: {str(e)}"}
        )


@app.get("/health")
async def health_check():
    return JSONResponse({
        "status": "ok",
        "ip_servidor": get_local_ip(),
        "mensaje": "Conexión exitosa con el servidor de pedidos",
        "routers": [
            "/normales",
            "/clientes",
            "/admin",
            "/api/pedidos"
        ]
    })


@app.get("/debug/routes")
async def debug_routes():
    """Endpoint para debug - muestra todas las rutas disponibles"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    return {"routes": routes}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)