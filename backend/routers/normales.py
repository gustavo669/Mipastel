from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from backend.database import get_conn_normales, DatabaseManager, obtener_precio_db
from datetime import datetime
import logging

router = APIRouter(prefix="/normales", tags=["Pasteles Normales"])
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")

def calcular_precio(sabor: str, tamano: str, cantidad: int) -> float:
    """Calcula el precio total basado en sabor, tamaño y cantidad"""
    try:
        precio_unitario = obtener_precio_db(sabor, tamano)
        return precio_unitario * cantidad
    except Exception as e:
        logger.error(f"Error al calcular precio: {e}")
        return 0.0

def obtener_precio_unitario(sabor: str, tamano: str) -> float:
    """Obtiene el precio unitario desde la base de datos"""
    try:
        return obtener_precio_db(sabor, tamano)
    except Exception as e:
        logger.error(f"Error al obtener precio unitario: {e}")
        return 0.0

@router.get("/formulario")
async def mostrar_formulario_normales(request: Request):
    """Muestra el formulario para pasteles normales"""
    try:
        # Listas para el formulario
        sabores_normales = [
            "Fresas", "Frutas", "Chocolate", "Selva negra", "Oreo", "Chocofresa",
            "Tres Leches", "Tres leches con Arándanos", "Fiesta", "Ambiente", "Zanahoria", "Otro"
        ]

        tamanos = ["Mini", "Pequeño", "Mediano", "Grande", "Extra grande", "Media plancha"]

        sucursales = [
            "Jutiapa 1", "Jutiapa 2", "Jutiapa 3", "Progreso", "Quesada", "Acatempa",
            "Yupiltepeque", "Atescatempa", "Adelanto", "Jeréz", "Comapa", "Cariña"
        ]

        return templates.TemplateResponse("formulario_normales.html", {
            "request": request,
            "sabores_normales": sabores_normales,
            "tamanos": tamanos,
            "sucursales": sucursales
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar formulario: {str(e)}")

@router.post("/registrar")
async def registrar_pedido_normal(
        request: Request,
        sabor: str = Form(...),
        tamano: str = Form(...),
        cantidad: int = Form(..., gt=0),
        sucursal: str = Form(...),
        fecha_pedido: str = Form(None),
        detalles: str = Form(None),
        es_otro: bool = Form(False),
        sabor_personalizado: str = Form(None)
):
    """Registra un nuevo pedido de pastel normal con precio automático"""
    try:
        # Validar tamaño
        tamanos_validos = ["Mini", "Pequeño", "Mediano", "Grande", "Extra grande", "Media plancha"]
        if tamano not in tamanos_validos:
            raise HTTPException(status_code=400, detail="Tamaño inválido")

        # Determinar sabor real
        sabor_real = sabor_personalizado if es_otro and sabor_personalizado else sabor

        # Calcular precio automático
        precio_unitario = obtener_precio_unitario(sabor, tamano)
        if precio_unitario == 0 and not es_otro:
            raise HTTPException(
                status_code=400,
                detail=f"No se encontró precio para {sabor} {tamano}. Use la opción 'Otro' para precios personalizados."
            )

        # Calcular precio total
        if es_otro:
            # Para sabores personalizados, el precio se establecerá manualmente o será 0
            precio_total = 0.0
        else:
            precio_total = calcular_precio(sabor, tamano, cantidad)

        # Parsear fecha
        fecha_val = None
        if fecha_pedido:
            try:
                fecha_val = datetime.fromisoformat(fecha_pedido.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Intentar otro formato común
                    fecha_val = datetime.strptime(fecha_pedido, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        fecha_val = datetime.strptime(fecha_pedido, "%Y-%m-%d")
                    except ValueError:
                        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD o YYYY-MM-DD HH:MM:SS")

        # Preparar datos para la base de datos
        pastel_data = {
            'sabor': sabor_real,
            'tamano': tamano,
            'cantidad': cantidad,
            'precio': precio_unitario if not es_otro else 0.0,
            'sucursal': sucursal,
            'detalles': detalles or '',
            'sabor_personalizado': sabor_personalizado or ''
        }

        # Insertar en base de datos usando DatabaseManager
        db = DatabaseManager()
        resultado = db.registrar_pastel_normal(pastel_data)

        if resultado:
            logger.info(f"Pastel normal registrado: {sabor_real} {tamano} x{cantidad} - Q{precio_total:.2f} - {sucursal}")

            # Redirigir a página de éxito
            return templates.TemplateResponse("exito.html", {
                "request": request,
                "mensaje": "Pastel normal registrado correctamente",
                "detalles": f"{sabor_real} {tamano} x{cantidad} - Total: Q{precio_total:.2f}",
                "tipo": "normal"
            })
        else:
            raise HTTPException(status_code=500, detail="Error al registrar el pastel en la base de datos")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar pastel normal: {e}")
        raise HTTPException(status_code=500, detail=f"Error al registrar el pastel: {str(e)}")

@router.get("/precio")
async def obtener_precio_automatico(sabor: str, tamano: str, cantidad: int = 1):
    """Endpoint para obtener precio automático"""
    try:
        if cantidad <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")

        precio_unitario = obtener_precio_unitario(sabor, tamano)
        precio_total = calcular_precio(sabor, tamano, cantidad)

        return {
            "precio_total": precio_total,
            "precio_unitario": precio_unitario,
            "sabor": sabor,
            "tamano": tamano,
            "cantidad": cantidad,
            "encontrado": precio_unitario > 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al calcular precio: {e}")
        raise HTTPException(status_code=500, detail=f"Error al calcular precio: {str(e)}")

@router.get("/")
async def listar_pasteles_normales(
        fecha: str = None,
        sucursal: str = None
):
    """Endpoint para listar pasteles normales con filtros"""
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

        pasteles = db.obtener_pasteles_normales(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            sucursal=sucursal
        )

        return {"pasteles": pasteles}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pasteles normales: {str(e)}")

@router.delete("/{pastel_id}")
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

@router.get("/estadisticas")
async def obtener_estadisticas_normales(
        fecha: str = None
):
    """Endpoint para obtener estadísticas de pasteles normales"""
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

        # Filtrar solo estadísticas relevantes para normales
        stats_normales = {
            'total_pasteles': estadisticas.get('normales_count', 0),
            'total_cantidad': estadisticas.get('normales_cantidad', 0),
            'total_ingresos': estadisticas.get('normales_ingresos', 0),
            'promedio_por_pastel': estadisticas.get('normales_ingresos', 0) / max(estadisticas.get('normales_count', 1), 1)
        }

        return {"estadisticas": stats_normales}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.get("/sabores")
async def obtener_sabores_disponibles():
    """Endpoint para obtener la lista de sabores disponibles"""
    try:
        sabores_normales = [
            "Fresas", "Frutas", "Chocolate", "Selva negra", "Oreo", "Chocofresa",
            "Tres Leches", "Tres leches con Arándanos", "Fiesta", "Ambiente", "Zanahoria", "Otro"
        ]

        return {"sabores": sabores_normales}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener sabores: {str(e)}")

@router.get("/tamanos")
async def obtener_tamanos_disponibles():
    """Endpoint para obtener la lista de tamaños disponibles"""
    try:
        tamanos = ["Mini", "Pequeño", "Mediano", "Grande", "Extra grande", "Media plancha"]
        return {"tamanos": tamanos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tamaños: {str(e)}")