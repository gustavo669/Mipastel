from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from database import DatabaseManager, obtener_precio_db
from datetime import datetime
import os, logging
from typing import Optional
from config import (
    SABORES_CLIENTES, TAMANOS_CLIENTES, SUCURSALES
)

router = APIRouter(prefix="/clientes", tags=["Pedidos de Clientes"])
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")

# --- Directorio de subida de imágenes ---
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# --------------------------
# Funciones auxiliares
# --------------------------
def validar_imagen(file: UploadFile) -> bool:
    if not file or not file.filename:
        return False
    ext = os.path.splitext(file.filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def calcular_precio(sabor: str, tamano: str, cantidad: int) -> float:
    """Calcula el total (precio * cantidad)"""
    try:
        precio_unitario = obtener_precio_db(sabor, tamano)
        return precio_unitario * cantidad
    except Exception as e:
        logger.error(f"Error al calcular precio: {e}")
        return 0.0

def obtener_precio_unitario(sabor: str, tamano: str) -> float:
    """Obtiene el precio unitario directo"""
    try:
        return obtener_precio_db(sabor, tamano)
    except Exception as e:
        logger.error(f"Error al obtener precio unitario: {e}")
        return 0.0


# --------------------------
# Página del formulario
# --------------------------
@router.get("/formulario")
async def mostrar_formulario_clientes(request: Request):
    try:
        return templates.TemplateResponse("formulario_clientes.html", {
            "request": request,
            "sabores_clientes": SABORES_CLIENTES,
            "tamanos": TAMANOS_CLIENTES,
            "sucursales": SUCURSALES
        })
    except Exception as e:
        logger.error(f"Error al cargar formulario clientes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al cargar formulario: {str(e)}")


# --------------------------
# Registrar pedido (POST)
# --------------------------
@router.post("/registrar")
async def registrar_pedido_cliente(
        request: Request,
        sabor: str = Form(...),
        tamano: str = Form(...),
        cantidad: int = Form(..., gt=0),
        sucursal: str = Form(...),
        detalles: Optional[str] = Form(None),
        es_otro: bool = Form(False),
        sabor_personalizado: Optional[str] = Form(None),
        imagen: Optional[UploadFile] = File(None)
):
    """Registrar un pedido de cliente desde la web"""
    try:
        # Validación del tamaño
        if tamano not in TAMANOS_CLIENTES:
            raise HTTPException(status_code=400, detail="Tamaño inválido")

        # Si el sabor es personalizado
        sabor_real = sabor_personalizado if es_otro and sabor_personalizado else sabor

        # Obtener precio
        precio_unitario = obtener_precio_unitario(sabor, tamano)
        if precio_unitario == 0 and not es_otro:
            raise HTTPException(
                status_code=400,
                detail=f"No se encontró precio para {sabor} {tamano}. Use la opción 'Otro' para precios personalizados."
            )

        precio_total = precio_unitario * cantidad

        # Guardar imagen si existe
        imagen_path = None
        if imagen and validar_imagen(imagen):
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{imagen.filename}"
            imagen_path = os.path.join(UPLOAD_DIR, filename)
            with open(imagen_path, "wb") as buffer:
                buffer.write(await imagen.read())

        # Registrar en la base de datos
        pedido_data = {
            'sabor': sabor_real,
            'tamano': tamano,
            'cantidad': cantidad,
            'precio': precio_unitario,
            'sucursal': sucursal,
            'detalles': detalles or '',
            'imagen': imagen_path or '',
            'sabor_personalizado': sabor_personalizado or ''
        }

        db = DatabaseManager()
        resultado = db.registrar_pedido_cliente(pedido_data)

        if resultado:
            logger.info(f"Pedido cliente registrado: {sabor_real} {tamano} x{cantidad} - Q{precio_total:.2f}")
            return templates.TemplateResponse("exito.html", {
                "request": request,
                "mensaje": "Pedido de cliente registrado correctamente",
                "detalles": f"{sabor_real} {tamano} x{cantidad} - Total: Q{precio_total:.2f}",
                "tipo": "cliente"
            })
        else:
            raise HTTPException(status_code=500, detail="Error al registrar el pedido en la base de datos")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al registrar pedido cliente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al registrar el pedido: {str(e)}")

