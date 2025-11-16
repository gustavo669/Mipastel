from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import logging

from database import DatabaseManager
from config import (
    SABORES_NORMALES,
    SABORES_CLIENTES,
    TAMANOS_NORMALES,
    TAMANOS_CLIENTES,
    SUCURSALES
)

router = APIRouter(prefix="/admin", tags=["Administración"])
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def vista_admin(request: Request):
    """Vista principal del panel de administración."""
    try:
        db = DatabaseManager()
        hoy = datetime.now().date()
        fecha_str = hoy.isoformat()

        normales = db.obtener_pasteles_normales(fecha_inicio=fecha_str)
        clientes = db.obtener_pedidos_clientes(fecha_inicio=fecha_str)
        precios = db.obtener_precios()

        return templates.TemplateResponse("admin.html", {
            "request": request,
            "normales": normales,
            "clientes": clientes,
            "precios": precios,
            "sabores_normales": SABORES_NORMALES,
            "sabores_clientes": SABORES_CLIENTES,
            "tamanos_normales": TAMANOS_NORMALES,
            "tamanos_clientes": TAMANOS_CLIENTES,
            "sucursales": SUCURSALES,
            "fecha_actual": fecha_str
        })

    except Exception as e:
        logger.error(f"Error al cargar vista admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al cargar datos: {str(e)}")


@router.get("/normales")
async def obtener_normales(
        fecha: str = Query(None, description="Fecha en formato YYYY-MM-DD"),
        sucursal: str = Query(None, description="Nombre de la sucursal")
):
    """Obtener pasteles normales con filtros opcionales."""
    try:
        db = DatabaseManager()
        normales = db.obtener_pasteles_normales(fecha_inicio=fecha, sucursal=sucursal)
        return {"normales": normales}
    except Exception as e:
        logger.error(f"Error en /admin/normales: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener pasteles normales: {str(e)}")


@router.get("/clientes")
async def obtener_clientes(
        fecha: str = Query(None, description="Fecha en formato YYYY-MM-DD"),
        sucursal: str = Query(None, description="Nombre de la sucursal")
):
    """Obtener pedidos de clientes filtrados."""
    try:
        db = DatabaseManager()
        clientes = db.obtener_pedidos_clientes(fecha_inicio=fecha, sucursal=sucursal)
        return {"clientes": clientes}
    except Exception as e:
        logger.error(f"Error en /admin/clientes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos de clientes: {str(e)}")


@router.get("/precios")
async def obtener_precios():
    """Obtener configuración completa de precios."""
    try:
        db = DatabaseManager()
        precios = db.obtener_precios()
        return {"precios": precios}
    except Exception as e:
        logger.error(f"Error en /admin/precios: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener precios: {str(e)}")


@router.post("/precios/actualizar")
async def actualizar_precios(precios_data: list):
    """Actualizar los precios en la base de datos."""
    try:
        db = DatabaseManager()

        for precio in precios_data:
            if not all(k in precio for k in ("id", "precio")):
                raise HTTPException(status_code=400, detail="Datos de precios incompletos")

        resultado = db.actualizar_precios(precios_data)

        if resultado:
            return {"message": "Precios actualizados correctamente", "actualizados": len(precios_data)}

        raise HTTPException(status_code=500, detail="Error al actualizar precios")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar precios: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al actualizar precios: {str(e)}")


@router.post("/normales/registrar")
async def registrar_pastel_normal(pastel_data: dict):
    """Registrar un nuevo pastel normal."""
    try:
        db = DatabaseManager()

        campos = ["sabor", "tamano", "cantidad", "precio", "sucursal"]
        for campo in campos:
            if campo not in pastel_data or not pastel_data[campo]:
                raise HTTPException(status_code=400, detail=f"Campo requerido faltante: {campo}")

        if db.registrar_pastel_normal(pastel_data):
            return {"message": "Pastel normal registrado correctamente"}

        raise HTTPException(status_code=500, detail="Error al registrar pastel normal")

    except Exception as e:
        logger.error(f"Error registrando pastel normal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al registrar pastel normal: {str(e)}")


@router.post("/clientes/registrar")
async def registrar_pedido_cliente(pedido_data: dict):
    """Registrar un nuevo pedido de cliente."""
    try:
        db = DatabaseManager()

        campos = ["sabor", "tamano", "cantidad", "precio", "sucursal"]
        for campo in campos:
            if campo not in pedido_data or not pedido_data[campo]:
                raise HTTPException(status_code=400, detail=f"Campo requerido faltante: {campo}")

        if db.registrar_pedido_cliente(pedido_data):
            return {"message": "Pedido de cliente registrado correctamente"}

        raise HTTPException(status_code=500, detail="Error al registrar pedido de cliente")

    except Exception as e:
        logger.error(f"Error registrando pedido cliente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al registrar pedido de cliente: {str(e)}")


@router.delete("/normales/{pastel_id}")
async def eliminar_pastel_normal(pastel_id: int):
    """Eliminar pastel normal."""
    try:
        db = DatabaseManager()

        if db.eliminar_pastel_normal(pastel_id):
            return {"message": f"Pastel normal #{pastel_id} eliminado correctamente"}

        raise HTTPException(status_code=500, detail="Error al eliminar pastel normal")

    except Exception as e:
        logger.error(f"Error eliminando pastel normal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al eliminar pastel normal: {str(e)}")


@router.delete("/clientes/{pedido_id}")
async def eliminar_pedido_cliente(pedido_id: int):
    """Eliminar pedido cliente."""
    try:
        db = DatabaseManager()

        if db.eliminar_pedido_cliente(pedido_id):
            return {"message": f"Pedido cliente #{pedido_id} eliminado correctamente"}

        raise HTTPException(status_code=500, detail="Error al eliminar pedido de cliente")

    except Exception as e:
        logger.error(f"Error eliminando pedido cliente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al eliminar pedido de cliente: {str(e)}")


@router.get("/estadisticas")
async def obtener_estadisticas(fecha: str = Query(None, description="YYYY-MM-DD")):
    """Obtener estadísticas globales."""
    try:
        db = DatabaseManager()
        estadisticas = db.obtener_estadisticas(fecha_inicio=fecha)
        return {"estadisticas": estadisticas}
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")


@router.get("/health")
async def health_check():
    """Comprueba salud del módulo admin."""
    try:
        db = DatabaseManager()
        precios = db.obtener_precios()

        return {
            "status": "healthy",
            "module": "admin",
            "database_ok": len(precios) > 0,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
