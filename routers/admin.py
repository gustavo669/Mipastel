from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import logging

# Importar desde el nuevo database.py
from database import (
    DatabaseManager
)
# Importar desde config.py
from config import (
    SABORES_NORMALES, SABORES_CLIENTES, TAMANOS, SUCURSALES
)

router = APIRouter(prefix="/admin", tags=["Administración"])
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
async def vista_admin(request: Request):
    """Vista principal de administración"""
    try:
        # Usar DatabaseManager para obtener datos
        db = DatabaseManager()

        # Obtener datos del día actual
        hoy = datetime.now().date()
        # Usamos solo fecha_inicio, el manager de DB sabe qué hacer
        fecha_str = hoy.isoformat()

        normales = db.obtener_pasteles_normales(
            fecha_inicio=fecha_str
        )

        clientes = db.obtener_pedidos_clientes(
            fecha_inicio=fecha_str
        )

        # Obtener configuración de precios
        precios = db.obtener_precios()

        return templates.TemplateResponse("admin.html", {
            "request": request,
            "normales": normales,
            "clientes": clientes,
            "precios": precios,
            "sabores_normales": SABORES_NORMALES, # Desde config
            "sabores_clientes": SABORES_CLIENTES, # Desde config
            "tamanos": TAMANOS, # Desde config
            "sucursales": SUCURSALES, # Desde config
            "fecha_actual": hoy.strftime("%Y-%m-%d")
        })

    except Exception as e:
        logger.error(f"Error al cargar vista admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al cargar datos: {str(e)}")

@router.get("/normales")
async def obtener_normales(
        fecha: str = Query(None, description="Fecha en formato YYYY-MM-DD"),
        sucursal: str = Query(None, description="Nombre de la sucursal")
):
    """Endpoint para obtener pasteles normales con filtros"""
    try:
        db = DatabaseManager()

        # El manager ya maneja la lógica de fecha_inicio/fin
        normales = db.obtener_pasteles_normales(
            fecha_inicio=fecha, # Pasa la fecha (o None)
            sucursal=sucursal
        )

        return {"normales": normales}

    except Exception as e:
        logger.error(f"Error en endpoint /normales: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener pasteles normales: {str(e)}")

@router.get("/clientes")
async def obtener_clientes(
        fecha: str = Query(None, description="Fecha en formato YYYY-MM-DD"),
        sucursal: str = Query(None, description="Nombre de la sucursal")
):
    """Endpoint para obtener pedidos de clientes con filtros"""
    try:
        db = DatabaseManager()

        clientes = db.obtener_pedidos_clientes(
            fecha_inicio=fecha, # Pasa la fecha (o None)
            sucursal=sucursal
        )

        return {"clientes": clientes}

    except Exception as e:
        logger.error(f"Error en endpoint /clientes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos de clientes: {str(e)}")

@router.get("/precios")
async def obtener_precios():
    """Endpoint para obtener la configuración de precios"""
    try:
        db = DatabaseManager()
        precios = db.obtener_precios()
        return {"precios": precios}
    except Exception as e:
        logger.error(f"Error en endpoint /precios: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener precios: {str(e)}")

@router.post("/precios/actualizar")
async def actualizar_precios(precios_data: list):
    """Endpoint para actualizar precios"""
    try:
        db = DatabaseManager()

        # Validar datos
        for precio in precios_data:
            if 'id' not in precio or 'precio' not in precio:
                raise HTTPException(
                    status_code=400,
                    detail="Datos de precios incompletos"
                )
            # Asegurarse de que el dict tenga 'tamano' (sin tilde)
            if 'tamano' not in precio:
                precio['tamano'] = precio.get('tamaño') # Fallback por si la UI envía tilde

        resultado = db.actualizar_precios(precios_data)

        if resultado:
            return {"message": "Precios actualizados correctamente", "actualizados": len(precios_data)}
        else:
            raise HTTPException(status_code=500, detail="Error al actualizar precios")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en endpoint /precios/actualizar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al actualizar precios: {str(e)}")

@router.post("/normales/registrar")
async def registrar_pastel_normal(pastel_data: dict):
    """Endpoint para registrar un nuevo pastel normal"""
    try:
        db = DatabaseManager()

        # Validar datos requeridos
        campos_requeridos = ['sabor', 'tamano', 'cantidad', 'precio', 'sucursal']
        for campo in campos_requeridos:
            if campo not in pastel_data or not pastel_data[campo]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Campo requerido faltante: {campo}"
                )

        resultado = db.registrar_pastel_normal(pastel_data)

        if resultado:
            return {"message": "Pastel normal registrado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al registrar pastel normal")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en endpoint /normales/registrar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al registrar pastel normal: {str(e)}")

@router.post("/clientes/registrar")
async def registrar_pedido_cliente(pedido_data: dict):
    """Endpoint para registrar un nuevo pedido de cliente"""
    try:
        db = DatabaseManager()

        # Validar datos requeridos
        campos_requeridos = ['sabor', 'tamano', 'cantidad', 'precio', 'sucursal']
        for campo in campos_requeridos:
            if campo not in pedido_data or not pedido_data[campo]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Campo requerido faltante: {campo}"
                )

        resultado = db.registrar_pedido_cliente(pedido_data)

        if resultado:
            return {"message": "Pedido de cliente registrado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al registrar pedido de cliente")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en endpoint /clientes/registrar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al registrar pedido de cliente: {str(e)}")

@router.delete("/normales/{pastel_id}")
async def eliminar_pastel_normal(pastel_id: int):
    """Endpoint para eliminar un pastel normal"""
    try:
        db = DatabaseManager()
        resultado = db.eliminar_pastel_normal(pastel_id)
        if resultado:
            return {"message": f"Pastel normal #{pastel_id} eliminado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar pastel normal")
    except Exception as e:
        logger.error(f"Error en endpoint /normales/delete: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al eliminar pastel normal: {str(e)}")

@router.delete("/clientes/{pedido_id}")
async def eliminar_pedido_cliente(pedido_id: int):
    """Endpoint para eliminar un pedido de cliente"""
    try:
        db = DatabaseManager()
        resultado = db.eliminar_pedido_cliente(pedido_id)
        if resultado:
            return {"message": f"Pedido de cliente #{pedido_id} eliminado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar pedido de cliente")
    except Exception as e:
        logger.error(f"Error en endpoint /clientes/delete: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al eliminar pedido de cliente: {str(e)}")

@router.get("/estadisticas")
async def obtener_estadisticas(
        fecha: str = Query(None, description="Fecha en formato YYYY-MM-DD")
):
    """Endpoint para obtener estadísticas del sistema"""
    try:
        db = DatabaseManager()
        estadisticas = db.obtener_estadisticas(
            fecha_inicio=fecha
        )
        return {"estadisticas": estadisticas}
    except Exception as e:
        logger.error(f"Error en endpoint /estadisticas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.get("/health")
async def health_check():
    """Endpoint de salud para verificar que el módulo admin está funcionando"""
    try:
        db = DatabaseManager()
        precios = db.obtener_precios()
        return {
            "status": "healthy",
            "module": "admin",
            "database_precios": len(precios) > 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )