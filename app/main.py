import os
import socket
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, date
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config.settings import settings
from config.constants import SABORES_NORMALES, SABORES_CLIENTES, TAMANOS_NORMALES, TAMANOS_CLIENTES, SUCURSALES
from api.auth import verificar_credenciales, crear_respuesta_con_sesion, cerrar_sesion, verificar_sesion, requiere_autenticacion
from api.database import obtener_precio_db
from pdf_reportes import generar_pdf_listas, generar_pdf_ventas, generar_pdf_rango_fechas
from utils.logger import logger
from app.middleware import setup_security_middleware

try:
    from routers import normales, clientes, admin, pedidos_api
    print("Todos los routers importados correctamente")
except ImportError as e:
    print(f"Advertencia de Importación: {e}")
    from fastapi import APIRouter
    normales = clientes = admin = pedidos_api = APIRouter()

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
    print(f"Servidor iniciado en: http://{local_ip}:5000")
    print(f"Acceso local: http://127.0.0.1:5000")
    print(f"Acceso desde red WiFi: http://{local_ip}:5000")
    print(f"{'='*60}\n")
    yield

app = FastAPI(
    title="Mi Pastel - Sistema de Gestión",
    description="""
    ## Sistema de Gestión de Pedidos para Mi Pastel
    
    Este API permite gestionar pedidos de pasteles normales y personalizados para clientes.
    
    ### Características principales:
    
    * **Autenticación**: Sistema de sesiones basado en cookies
    * **Gestión de Pedidos**: Crear, leer, actualizar y eliminar pedidos
    * **Control de Sucursales**: Permisos basados en sucursales
    * **Reportes**: Generación de PDFs con listas y ventas
    * **Auditoría**: Registro completo de todas las operaciones
    
    ### Autenticación
    
    La mayoría de los endpoints requieren autenticación. Primero debe iniciar sesión en `/login`
    para obtener una sesión válida. Las credenciales se verifican contra la base de datos de usuarios.
    
    ### Permisos
    
    * **Admin**: Acceso completo a todas las sucursales
    * **Sucursal**: Acceso solo a datos de su sucursal asignada
    
    ### Sucursales Disponibles
    
    Jutiapa 1, Jutiapa 2, Jutiapa 3, Progreso, Quesada, Acatempa, 
    Yupiltepeque, Atescatempa, Adelanto, Jeréz, Comapa, Carina
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Autenticación",
            "description": "Endpoints para login, logout y gestión de sesiones"
        },
        {
            "name": "Pasteles Normales",
            "description": "Gestión de pedidos de pasteles normales"
        },
        {
            "name": "Pedidos de Clientes",
            "description": "Gestión de pedidos personalizados de clientes"
        },
        {
            "name": "Administración",
            "description": "Panel de administración y gestión de datos"
        },
        {
            "name": "Pedidos API",
            "description": "API REST para operaciones CRUD de pedidos"
        },
        {
            "name": "Reportes",
            "description": "Generación de reportes en PDF"
        },
        {
            "name": "Sistema",
            "description": "Endpoints de salud y diagnóstico del sistema"
        }
    ],
    contact={
        "name": "Mi Pastel",
        "email": "soporte@mipastel.com"
    },
    license_info={
        "name": "Propietario",
    }
)

setup_security_middleware(app)

app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

app.include_router(normales.router)
app.include_router(clientes.router)
app.include_router(admin.router)
app.include_router(pedidos_api.router)

print("Routers registrados:")
print("  - /normales")
print("  - /clientes")
print("  - /admin")
print("  - /api/pedidos")

@app.get("/login", response_class=HTMLResponse, tags=["Autenticación"])
async def mostrar_login(request: Request, error: str = None):
    """
    Display the login page.
    
    If user is already authenticated, redirects to home page.
    """
    user_data = verificar_sesion(request)
    if user_data:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error
    })

@app.post("/login", tags=["Autenticación"])
async def procesar_login(
        request: Request,
        username: str = Form(..., description="Nombre de usuario"),
        password: str = Form(..., description="Contraseña")
):
    """
    Process login credentials and create a session.
    
    Returns a redirect to the home page if successful,
    or back to login page with error message if failed.
    """
    from utils.audit import AuditLogger
    
    user_data = verificar_credenciales(username, password)
    if user_data:
        # Log successful login
        client_ip = request.client.host if request.client else None
        AuditLogger.log_login_success(username, ip_address=client_ip)
        
        response = RedirectResponse(url="/", status_code=302)
        crear_respuesta_con_sesion(response, user_data)
        return response
    else:
        # Log failed login attempt
        client_ip = request.client.host if request.client else None
        AuditLogger.log_login_failure(
            username,
            reason="Invalid credentials",
            ip_address=client_ip
        )
        
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Usuario o contraseña incorrectos"
        })

@app.get("/logout", tags=["Autenticación"])
async def cerrar_sesion_usuario(request: Request):
    """
    Log out the current user and destroy their session.
    
    Redirects to the login page.
    """
    from utils.audit import AuditLogger
    
    user_data = verificar_sesion(request)
    if user_data:
        client_ip = request.client.host if request.client else None
        AuditLogger.log_logout(user_data.get("username"), ip_address=client_ip)
    
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

        precio = obtener_precio_db(sabor, tamano)

        if precio and precio > 0:
            return {"precio": precio, "encontrado": True}
        else:
            return {"precio": 0, "encontrado": False, "detalle": "No registrado"}
    except Exception as e:
        logger.error(f"Error al obtener precio: {e}")
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

@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    Health check endpoint to verify server status.
    
    Returns server status, IP address, and available routers.
    """
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

@app.get("/debug/routes", tags=["Sistema"])
async def debug_routes():
    """
    Debug endpoint to list all registered routes.
    
    Useful for development and troubleshooting.
    """
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
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
