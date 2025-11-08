from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import DatabaseManager, obtener_precio_db
from datetime import datetime
import os
import logging
from typing import Optional


from config import (
    SABORES_CLIENTES, TAMANOS, SUCURSALES
)

router = APIRouter(prefix="/clientes", tags=["Pedidos de Clientes"])
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def validar_imagen(file: UploadFile) -> bool:
    """Válida que el archivo sea una imagen válida"""
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
        return templates.TemplateResponse("formulario_clientes.html", {
            "request": request,
            "sabores_clientes": SABORES_CLIENTES,
            "tamanos": TAMANOS,
            "sucursales": SUCURSALES
        })
    except Exception as e:
        logger.error(f"Error al cargar formulario clientes: {e}", exc_info=True)
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
    foto_path_db = None
    foto_path_disk = None

    try:
        if tamano not in TAMANOS:
            raise HTTPException(status_code=400, detail="Tamaño inválido")

        sabor_real = sabor_personalizado if es_otro and sabor_personalizado else sabor
        precio_unitario = obtener_precio_unitario(sabor, tamano)

        if precio_unitario == 0 and not es_otro:
            raise HTTPException(
                status_code=400,
                detail=f"No se encontró precio para {sabor} {tamano}. Use la opción 'Otro' para precios personalizados."
            )

        precio_total = precio_unitario * cantidad

        fecha_entrega_val = None
        if fecha_entrega:
            try:
                # Tratar de parsear fecha YYYY-MM-DD
                fecha_entrega_val = datetime.strptime(fecha_entrega, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha de entrega inválido. Use YYYY-MM-DD")

        if foto and foto.filename:
            if not validar_imagen(foto):
                raise HTTPException(status_code=400, detail="Tipo de archivo no permitido. Use JPG, PNG, GIF o BMP")

            contenido = await foto.read()
            if len(contenido) > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="Archivo muy grande. Máximo: 5 MB")

            timestamp = int(datetime.now().timestamp())
            extension = os.path.splitext(foto.filename)[1].lower()
            filename = f"cliente_{timestamp}{extension}"

            foto_path_disk = os.path.join(UPLOAD_DIR, filename)
            foto_path_db = f"/static/uploads/{filename}"

            with open(foto_path_disk, "wb") as f:
                f.write(contenido)
            logger.info(f"Foto guardada: {filename}")

        pedido_data = {
            'color': color or '',
            'sabor': sabor_real,
            'tamano': tamano,
            'cantidad': cantidad,
            'precio': precio_unitario,
            'sucursal': sucursal,
            'dedicatoria': dedicatoria or '',
            'detalles': detalles or '',
            'sabor_personalizado': sabor_personalizado or '',
            'foto_path': foto_path_db,
            'fecha_entrega': fecha_entrega_val
        }

        db = DatabaseManager()
        resultado = db.registrar_pedido_cliente(pedido_data)

        if resultado:
            logger.info(f"Pedido cliente registrado: {sabor_real} {tamano} x{cantidad} - Q{precio_total:.2f} - {sucursal}")
            return templates.TemplateResponse("exito.html", {
                "request": request,
                "mensaje": "Pedido registrado correctamente",
                "detalles": f"{sabor_real} {tamano} x{cantidad} - Total: Q{precio_total:.2f}",
                "tipo": "cliente"
            })
        else:
            raise HTTPException(status_code=500, detail="Error al registrar el pedido en la base de datos")

    except HTTPException:
        if foto_path_disk and os.path.exists(foto_path_disk):
            os.remove(foto_path_disk)
        raise
    except Exception as e:
        logger.error(f"Error al registrar pedido de cliente: {e}", exc_info=True)
        if foto_path_disk and os.path.exists(foto_path_disk):
            os.remove(foto_path_disk)
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
    except Exception as e:
        logger.error(f"Error en /precio cliente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al calcular precio: {str(e)}")

@router.delete("/{pedido_id}")
async def eliminar_pedido_cliente(pedido_id: int):
    """Endpoint para eliminar un pedido de cliente"""
    try:
        db = DatabaseManager()
        if pedido_id <= 0:
            raise HTTPException(status_code=400, detail="ID de pedido inválido")

        #Info del pedido ANTES de borrarlo
        pedidos = db.obtener_pedidos_clientes()
        pedido = next((p for p in pedidos if p['id'] == pedido_id), None)

        # Borramos el registro de la DB
        resultado = db.eliminar_pedido_cliente(pedido_id)

        if resultado:
            # Si se borra de la DB, borra la foto
            if pedido and pedido.get('foto_path'):
                foto_path_rel = pedido['foto_path']
                foto_path_disk = os.path.abspath(os.path.join(UPLOAD_DIR, os.path.basename(foto_path_rel)))
                if os.path.exists(foto_path_disk):
                    try:
                        os.remove(foto_path_disk)
                        logger.info(f"Foto eliminada: {foto_path_disk}")
                    except Exception as e:
                        logger.error(f"Error al eliminar foto: {e}")

            return {"message": f"Pedido de cliente #{pedido_id} eliminado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al eliminar pedido de cliente")

    except Exception as e:
        logger.error(f"Error en /delete cliente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al eliminar pedido de cliente: {str(e)}")