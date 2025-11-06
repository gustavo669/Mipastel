from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

# Importar desde el nuevo database.py
from database import (
    DatabaseManager
)

router = APIRouter(prefix="/admin", tags=["Administración"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def vista_admin(request: Request):
    """Vista principal de administración"""
    try:
        # Usar DatabaseManager para obtener datos
        db = DatabaseManager()

        # Obtener datos del día actual
        hoy = datetime.now().date()
        inicio = datetime.combine(hoy, datetime.min.time())
        fin = datetime.combine(hoy, datetime.max.time())

        normales = db.obtener_pasteles_normales(
            fecha_inicio=inicio.isoformat(),
            fecha_fin=fin.isoformat()
        )

        clientes = db.obtener_pedidos_clientes(
            fecha_inicio=inicio.isoformat(),
            fecha_fin=fin.isoformat()
        )

        # Obtener configuración de precios
        precios = db.obtener_precios()

        # Listas para los combobox
        sabores_normales = [
            "Fresas", "Frutas", "Chocolate", "Selva negra", "Oreo", "Chocofresa",
            "Tres Leches", "Tres leches con Arándanos", "Fiesta", "Ambiente", "Zanahoria", "Otro"
        ]

        sabores_clientes = sabores_normales + ["Boda", "Quince Años"]

        tamanos = ["Mini", "Pequeño", "Mediano", "Grande", "Extra grande", "Media plancha"]

        sucursales = [
            "Jutiapa 1", "Jutiapa 2", "Jutiapa 3", "Progreso", "Quesada", "Acatempa",
            "Yupiltepeque", "Atescatempa", "Adelanto", "Jeréz", "Comapa", "Cariña"
        ]

        return templates.TemplateResponse("admin.html", {
            "request": request,
            "normales": normales,
            "clientes": clientes,
            "precios": precios,
            "sabores_normales": sabores_normales,
            "sabores_clientes": sabores_clientes,
            "tamanos": tamanos,
            "sucursales": sucursales,
            "fecha_actual": hoy.strftime("%Y-%m-%d")
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar datos: {str(e)}")

@router.get("/normales")
async def obtener_normales(
        fecha: str = Query(None, description="Fecha en formato YYYY-MM-DD"),
        sucursal: str = Query(None, description="Nombre de la sucursal")
):
    """Endpoint para obtener pasteles normales con filtros"""
    try:
        db = DatabaseManager()

        fecha_inicio = None
        fecha_fin = None

        if fecha:
            try:
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
                fecha_inicio = datetime.combine(fecha_obj, datetime.min.time()).isoformat()
                fecha_fin = datetime.combine(fecha_obj, datetime.max.time()).isoformat()
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Formato de fecha inválido. Use YYYY-MM-DD"}
                )

        normales = db.obtener_pasteles_normales(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            sucursal=sucursal
        )

        return {"normales": normales}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pasteles normales: {str(e)}")

@router.get("/clientes")
async def obtener_clientes(
        fecha: str = Query(None, description="Fecha en formato YYYY-MM-DD"),
        sucursal: str = Query(None, description="Nombre de la sucursal")
):
    """Endpoint para obtener pedidos de clientes con filtros"""
    try:
        db = DatabaseManager()

        fecha_inicio = None
        fecha_fin = None

        if fecha:
            try:
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
                fecha_inicio = datetime.combine(fecha_obj, datetime.min.time()).isoformat()
                fecha_fin = datetime.combine(fecha_obj, datetime.max.time()).isoformat()
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Formato de fecha inválido. Use YYYY-MM-DD"}
                )

        clientes = db.obtener_pedidos_clientes(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            sucursal=sucursal
        )

        return {"clientes": clientes}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos de clientes: {str(e)}")

@router.get("/precios")
async def obtener_precios():
    """Endpoint para obtener la configuración de precios"""
    try:
        db = DatabaseManager()
        precios = db.obtener_precios()
        return {"precios": precios}
    except Exception as e:
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

            if precio['precio'] < 0:
                raise HTTPException(
                    status_code=400,
                    detail="El precio no puede ser negativo"
                )

        resultado = db.actualizar_precios(precios_data)

        if resultado:
            return {"message": "Precios actualizados correctamente", "actualizados": len(precios_data)}
        else:
            raise HTTPException(status_code=500, detail="Error al actualizar precios")

    except HTTPException:
        raise
    except Exception as e:
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

        if pastel_data['precio'] <= 0:
            raise HTTPException(
                status_code=400,
                detail="El precio debe ser mayor a 0"
            )

        if pastel_data['cantidad'] <= 0:
            raise HTTPException(
                status_code=400,
                detail="La cantidad debe ser mayor a 0"
            )

        resultado = db.registrar_pastel_normal(pastel_data)

        if resultado:
            return {"message": "Pastel normal registrado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al registrar pastel normal")

    except HTTPException:
        raise
    except Exception as e:
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

        if pedido_data['precio'] <= 0:
            raise HTTPException(
                status_code=400,
                detail="El precio debe ser mayor a 0"
            )

        if pedido_data['cantidad'] <= 0:
            raise HTTPException(
                status_code=400,
                detail="La cantidad debe ser mayor a 0"
            )

        resultado = db.registrar_pedido_cliente(pedido_data)

        if resultado:
            return {"message": "Pedido de cliente registrado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al registrar pedido de cliente")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar pedido de cliente: {str(e)}")

@router.delete("/normales/{pastel_id}")
async def eliminar_pastel_normal(pastel_id: int):
    """Endpoint para eliminar un pastel normal"""
    try:
        db = DatabaseManager()

        if pastel_id <= 0:
            raise HTTPException(status_code=400, detail="ID de pastel inválido")

        resultado = db.eliminar_pastel_normal(pastel_id)

        if resultado:
            return {"message": f"Pastel normal #{pastel_id} eliminado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar pastel normal")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar pastel normal: {str(e)}")

@router.delete("/clientes/{pedido_id}")
async def eliminar_pedido_cliente(pedido_id: int):
    """Endpoint para eliminar un pedido de cliente"""
    try:
        db = DatabaseManager()

        if pedido_id <= 0:
            raise HTTPException(status_code=400, detail="ID de pedido inválido")

        resultado = db.eliminar_pedido_cliente(pedido_id)

        if resultado:
            return {"message": f"Pedido de cliente #{pedido_id} eliminado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar pedido de cliente")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar pedido de cliente: {str(e)}")

@router.get("/estadisticas")
async def obtener_estadisticas(
        fecha: str = Query(None, description="Fecha en formato YYYY-MM-DD")
):
    """Endpoint para obtener estadísticas del sistema"""
    try:
        db = DatabaseManager()

        fecha_inicio = None
        fecha_fin = None

        if fecha:
            try:
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
                fecha_inicio = datetime.combine(fecha_obj, datetime.min.time()).isoformat()
                fecha_fin = datetime.combine(fecha_obj, datetime.max.time()).isoformat()
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Formato de fecha inválido. Use YYYY-MM-DD"}
                )

        estadisticas = db.obtener_estadisticas(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        return {"estadisticas": estadisticas}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.get("/health")
async def health_check():
    """Endpoint de salud para verificar que el módulo admin está funcionando"""
    try:
        # Probar conexiones a las bases de datos
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