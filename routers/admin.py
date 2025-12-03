from fastapi import APIRouter, Request, HTTPException, Query, Depends, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import logging
from typing import Optional

from database import (
    DatabaseManager,
    obtener_normal_por_id_db,
    obtener_cliente_por_id_db,
    actualizar_pastel_normal_db,
    actualizar_pedido_cliente_db
)
from config import (
    SABORES_NORMALES,
    SABORES_CLIENTES,
    TAMANOS_NORMALES,
    TAMANOS_CLIENTES,
    SUCURSALES
)

from auth import requiere_autenticacion, verificar_sesion

router = APIRouter(prefix="/admin", tags=["Administración"])
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def vista_admin(
        request: Request,
        fecha_inicio: str = Query(None, description="Fecha inicio en formato YYYY-MM-DD"),
        fecha_fin: str = Query(None, description="Fecha fin en formato YYYY-MM-DD"),
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        db = DatabaseManager()
        hoy = datetime.now().date()
        fecha_str = hoy.isoformat()

        # Usar las fechas proporcionadas o la fecha actual


        fecha_inicio_filtro = fecha_inicio if fecha_inicio else fecha_str


        fecha_fin_filtro = fecha_fin if fecha_fin else fecha_str



        sucursal_filtro = user_data["sucursal"] if user_data["rol"] != "admin" else None



        normales = db.obtener_pasteles_normales(fecha_inicio=fecha_inicio_filtro, fecha_fin=fecha_fin_filtro, sucursal=sucursal_filtro)


        clientes = db.obtener_pedidos_clientes(fecha_inicio=fecha_inicio_filtro, fecha_fin=fecha_fin_filtro, sucursal=sucursal_filtro)
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
            "fecha_actual": fecha_str,
            "user_data": user_data
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cargar vista admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al cargar datos: {str(e)}")


@router.get("/normales")
async def obtener_normales(
        request: Request,
        fecha_inicio: str = Query(None, description="Fecha inicio en formato YYYY-MM-DD"),
        fecha_fin: str = Query(None, description="Fecha fin en formato YYYY-MM-DD"),
        sucursal: str = Query(None, description="Nombre de la sucursal"),
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        db = DatabaseManager()

        sucursal_filtro = sucursal
        if user_data["rol"] != "admin" and not sucursal:
            sucursal_filtro = user_data["sucursal"]

        normales = db.obtener_pasteles_normales(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, sucursal=sucursal_filtro)
        return {"normales": normales}
    except Exception as e:
        logger.error(f"Error en /admin/normales: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener pasteles normales: {str(e)}")


@router.get("/normales/{pedido_id}")
async def obtener_normal_por_id(
        pedido_id: int,
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        pedido = obtener_normal_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if user_data["rol"] != "admin" and pedido.get("sucursal") != user_data["sucursal"]:
            raise HTTPException(status_code=403, detail="No autorizado")

        return {"pedido": pedido}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener pedido normal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/normales/{pedido_id}")
async def actualizar_normal(
        pedido_id: int,
        pedido_data: dict = Body(...),
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        pedido_actual = obtener_normal_por_id_db(pedido_id)
        if not pedido_actual:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if user_data["rol"] != "admin" and pedido_actual.get("sucursal") != user_data["sucursal"]:
            raise HTTPException(status_code=403, detail="No autorizado")

        actualizar_pastel_normal_db(pedido_id, pedido_data)
        return {"message": "Pedido actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar pedido normal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/normales/{pedido_id}")
async def eliminar_normal(
        pedido_id: int,
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        pedido = obtener_normal_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if user_data["rol"] != "admin" and pedido.get("sucursal") != user_data["sucursal"]:
            raise HTTPException(status_code=403, detail="No autorizado")

        db = DatabaseManager()
        if db.eliminar_pastel_normal(pedido_id):
            return {"message": f"Pedido #{pedido_id} eliminado correctamente"}

        raise HTTPException(status_code=500, detail="Error al eliminar")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar pedido normal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clientes")
async def obtener_clientes(
        request: Request,
        fecha_inicio: str = Query(None, description="Fecha inicio en formato YYYY-MM-DD"),
        fecha_fin: str = Query(None, description="Fecha fin en formato YYYY-MM-DD"),
        sucursal: str = Query(None, description="Nombre de la sucursal"),
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        db = DatabaseManager()

        sucursal_filtro = sucursal
        if user_data["rol"] != "admin" and not sucursal:
            sucursal_filtro = user_data["sucursal"]

        clientes = db.obtener_pedidos_clientes(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, sucursal=sucursal_filtro)
        return {"clientes": clientes}
    except Exception as e:
        logger.error(f"Error en /admin/clientes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos de clientes: {str(e)}")


@router.get("/clientes/{pedido_id}")
async def obtener_cliente_por_id(
        pedido_id: int,
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        pedido = obtener_cliente_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if user_data["rol"] != "admin" and pedido.get("sucursal") != user_data["sucursal"]:
            raise HTTPException(status_code=403, detail="No autorizado")

        return {"pedido": pedido}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener pedido cliente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/clientes/{pedido_id}")
async def actualizar_cliente(
        pedido_id: int,
        pedido_data: dict = Body(...),
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        pedido_actual = obtener_cliente_por_id_db(pedido_id)
        if not pedido_actual:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if user_data["rol"] != "admin" and pedido_actual.get("sucursal") != user_data["sucursal"]:
            raise HTTPException(status_code=403, detail="No autorizado")

        actualizar_pedido_cliente_db(pedido_id, pedido_data)
        return {"message": "Pedido actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar pedido cliente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clientes/{pedido_id}")
async def eliminar_cliente(
        pedido_id: int,
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        pedido = obtener_cliente_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if user_data["rol"] != "admin" and pedido.get("sucursal") != user_data["sucursal"]:
            raise HTTPException(status_code=403, detail="No autorizado")

        db = DatabaseManager()
        if db.eliminar_pedido_cliente(pedido_id):
            return {"message": f"Pedido #{pedido_id} eliminado correctamente"}

        raise HTTPException(status_code=500, detail="Error al eliminar")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar pedido cliente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/precios")
async def obtener_precios(
        request: Request,
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        db = DatabaseManager()
        precios = db.obtener_precios()
        return {"precios": precios}
    except Exception as e:
        logger.error(f"Error en /admin/precios: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener precios: {str(e)}")


@router.post("/precios/actualizar")
async def actualizar_precios(
        precios_data: list,
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        if user_data["rol"] != "admin":
            raise HTTPException(status_code=403, detail="Solo administradores pueden actualizar precios")

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


@router.get("/estadisticas")
async def obtener_estadisticas(
        fecha: str = Query(None, description="YYYY-MM-DD"),
        user_data: dict = Depends(requiere_autenticacion)
):
    try:
        db = DatabaseManager()
        estadisticas = db.obtener_estadisticas(fecha_inicio=fecha)
        return {"estadisticas": estadisticas}
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")


@router.get("/health")
async def health_check():
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