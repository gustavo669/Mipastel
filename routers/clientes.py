from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from database import DatabaseManager, obtener_precio_db
from datetime import datetime
import os
import logging
from typing import Optional

router = APIRouter(prefix="/clientes", tags=["Pedidos de Clientes"])
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def validar_imagen(file: UploadFile) -> bool:
    """Valida que el archivo sea una imagen válida"""
    if not file or not file.filename:
        return False
    ext = os.path.splitext(file.filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

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
async def mostrar_formulario_clientes(request: Request):
    """Muestra el formulario para pedidos de clientes"""
    try:
        # Listas para el formulario
        sabores_clientes = [
            "Fresas", "Frutas", "Chocolate", "Selva negra", "Oreo", "Chocofresa",
            "Tres Leches", "Tres leches con Arándanos", "Fiesta", "Ambiente", "Zanahoria",
            "Boda", "Quince Años", "Otro"
        ]

        tamanos = ["Mini", "Pequeño", "Mediano", "Grande", "Extra grande", "Media plancha"]

        sucursales = [
            "Jutiapa 1", "Jutiapa 2", "Jutiapa 3", "Progreso", "Quesada", "Acatempa",
            "Yupiltepeque", "Atescatempa", "Adelanto", "Jeréz", "Comapa", "Cariña"
        ]

        return templates.TemplateResponse("formulario_clientes.html", {
            "request": request,
            "sabores_clientes": sabores_clientes,
            "tamanos": tamanos,
            "sucursales": sucursales
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar formulario: {str(e)}")

@router.post("/registrar")
async def registrar_pedido_cliente(
        request: Request,
        sabor: str = Form(..., min_length=1, max_length=50),
        tamano: str = Form(...),
        cantidad: int = Form(..., gt=0),
        sucursal: str = Form(..., min_length=1, max_length=100),
        color: Optional[str] = Form(None, max_length=50),
        fecha_entrega: Optional[str] = Form(None),
        foto: Optional[UploadFile] = File(None),
        detalles: Optional[str] = Form(None, max_length=500),
        dedicatoria: Optional[str] = Form(None, max_length=300),
        es_otro: bool = Form(False),
        sabor_personalizado: Optional[str] = Form(None, max_length=100)
):
    """Registra un nuevo pedido de cliente con todos los campos"""
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

        # Si es "Otro", el precio unitario será 0 y se debe establecer manualmente
        # Para este caso, usaremos el precio calculado automáticamente si está disponible
        if es_otro and precio_unitario == 0:
            # Para sabores personalizados sin precio, podrías tener un precio por defecto
            # o requerir que se ingrese manualmente. Por ahora usamos 0.
            precio_total = 0.0
        else:
            precio_total = calcular_precio(sabor, tamano, cantidad)

        # Parsear fecha de entrega
        fecha_entrega_val = None
        if fecha_entrega:
            try:
                fecha_entrega_val = datetime.fromisoformat(fecha_entrega.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Intentar otro formato común
                    fecha_entrega_val = datetime.strptime(fecha_entrega, "%Y-%m-%d")
                except ValueError:
                    raise HTTPException(status_code=400, detail="Formato de fecha de entrega inválido. Use YYYY-MM-DD")

        # Procesar foto si existe
        foto_path = None
        if foto and foto.filename:
            if not validar_imagen(foto):
                raise HTTPException(status_code=400, detail="Tipo de archivo no permitido. Use JPG, PNG, GIF o BMP")

            contenido = await foto.read()

            if len(contenido) > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="Archivo muy grande. Máximo: 5 MB")

            timestamp = int(datetime.now().timestamp())
            extension = os.path.splitext(foto.filename)[1].lower()
            filename = f"cliente_{timestamp}{extension}"
            dest = os.path.join(UPLOAD_DIR, filename)

            try:
                with open(dest, "wb") as f:
                    f.write(contenido)
                foto_path = f"/static/uploads/{filename}"  # Ruta relativa para la web
                logger.info(f"Foto guardada: {filename}")
            except Exception as e:
                logger.error(f"Error al guardar foto: {e}")
                raise HTTPException(status_code=500, detail="Error al guardar la foto")

        # Preparar datos para la base de datos
        pedido_data = {
            'color': color or '',
            'sabor': sabor_real,
            'tamano': tamano,
            'cantidad': cantidad,
            'precio': precio_unitario,
            'sucursal': sucursal,
            'dedicatoria': dedicatoria or '',
            'detalles': detalles or '',
            'sabor_personalizado': sabor_personalizado or ''
        }

        # Insertar en base de datos usando DatabaseManager
        db = DatabaseManager()
        resultado = db.registrar_pedido_cliente(pedido_data)

        if resultado:
            logger.info(f"Pedido cliente registrado: {sabor_real} {tamano} x{cantidad} - Q{precio_total:.2f} - {sucursal}")

            # Redirigir a página de éxito
            return templates.TemplateResponse("exito.html", {
                "request": request,
                "mensaje": "Pedido registrado correctamente",
                "detalles": f"{sabor_real} {tamano} x{cantidad} - Total: Q{precio_total:.2f}",
                "tipo": "cliente"
            })
        else:
            # Si falla la inserción, eliminar la foto si se subió
            if foto_path and os.path.exists(foto_path.replace('/static/uploads/', UPLOAD_DIR + '/')):
                try:
                    os.remove(foto_path.replace('/static/uploads/', UPLOAD_DIR + '/'))
                except:
                    pass
            raise HTTPException(status_code=500, detail="Error al registrar el pedido en la base de datos")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar pedido de cliente: {e}")
        # Limpiar foto si hubo error
        if 'foto_path' in locals() and foto_path and os.path.exists(foto_path.replace('/static/uploads/', UPLOAD_DIR + '/')):
            try:
                os.remove(foto_path.replace('/static/uploads/', UPLOAD_DIR + '/'))
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error al registrar el pedido: {str(e)}")

@router.get("/precio")
async def obtener_precio_cliente(sabor: str, tamano: str, cantidad: int = 1):
    """Endpoint para obtener precio automático para clientes"""
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
async def listar_pedidos_clientes(
        fecha: Optional[str] = None,
        sucursal: Optional[str] = None
):
    """Endpoint para listar pedidos de clientes con filtros"""
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

        pedidos = db.obtener_pedidos_clientes(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            sucursal=sucursal
        )

        return {"pedidos": pedidos}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos de clientes: {str(e)}")

@router.delete("/{pedido_id}")
async def eliminar_pedido_cliente(pedido_id: int):
    """Endpoint para eliminar un pedido de cliente"""
    try:
        db = DatabaseManager()

        if pedido_id <= 0:
            raise HTTPException(status_code=400, detail="ID de pedido inválido")

        # Primero obtener información del pedido para eliminar la foto si existe
        pedidos = db.obtener_pedidos_clientes()
        pedido = next((p for p in pedidos if p['id'] == pedido_id), None)

        if pedido and pedido.get('foto_path'):
            foto_path = pedido['foto_path']
            if os.path.exists(foto_path):
                try:
                    os.remove(foto_path)
                    logger.info(f"Foto eliminada: {foto_path}")
                except Exception as e:
                    logger.error(f"Error al eliminar foto: {e}")

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
async def obtener_estadisticas_clientes(
        fecha: Optional[str] = None
):
    """Endpoint para obtener estadísticas de pedidos de clientes"""
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

        # Filtrar solo estadísticas relevantes para clientes
        stats_clientes = {
            'total_pedidos': estadisticas.get('clientes_count', 0),
            'total_cantidad': estadisticas.get('clientes_cantidad', 0),
            'total_ingresos': estadisticas.get('clientes_ingresos', 0),
            'promedio_por_pedido': estadisticas.get('clientes_ingresos', 0) / max(estadisticas.get('clientes_count', 1), 1)
        }

        return {"estadisticas": stats_clientes}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")