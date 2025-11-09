from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
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

# 📁 Directorio para guardar las imágenes
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔒 Configuración de archivos
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# ===============================
# FUNCIONES AUXILIARES
# ===============================
def validar_imagen(file: UploadFile) -> bool:
    """Verifica si el archivo es una imagen válida."""
    if not file or not file.filename:
        return False
    ext = os.path.splitext(file.filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def calcular_precio(sabor: str, tamano: str, cantidad: int) -> float:
    """Calcula el precio total del pedido según sabor y tamaño."""
    try:
        precio_unitario = obtener_precio_db(sabor, tamano)
        return precio_unitario * cantidad
    except Exception as e:
        logger.error(f"Error al calcular precio: {e}")
        return 0.0


def obtener_precio_unitario(sabor: str, tamano: str) -> float:
    """Obtiene el precio unitario desde la base de datos."""
    try:
        return obtener_precio_db(sabor, tamano)
    except Exception as e:
        logger.error(f"Error al obtener precio unitario: {e}")
        return 0.0


# ===============================
# MOSTRAR FORMULARIO
# ===============================
@router.get("/formulario")
async def mostrar_formulario_clientes(request: Request):
    """Muestra el formulario de pedidos de clientes."""
    try:
        return templates.TemplateResponse("formulario_clientes.html", {
            "request": request,
            "sabores_clientes": SABORES_CLIENTES,
            "tamanos_clientes": TAMANOS_CLIENTES,
            "sucursales": SUCURSALES
        })
    except Exception as e:
        logger.error(f"Error al cargar formulario clientes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al cargar formulario: {str(e)}")


# ===============================
# REGISTRAR PEDIDO DE CLIENTE
# ===============================
@router.post("/registrar")
async def registrar_pedido_cliente(
        sabor: str = Form(...),
        tamano: str = Form(...),
        cantidad: int = Form(...),
        sucursal: str = Form(...),
        fecha_entrega: str = Form(...),
        color: Optional[str] = Form(None),
        dedicatoria: Optional[str] = Form(None),
        detalles: Optional[str] = Form(None),
        precio_personalizado: Optional[float] = Form(None),
        foto: Optional[UploadFile] = File(None),
        sabor_otro: Optional[str] = Form(None),
        tamano_otro: Optional[str] = Form(None)
):
    """Guarda el pedido del cliente en la base de datos."""
    try:
        # ✅ Si el sabor o tamaño son personalizados
        if sabor == "Otro" and sabor_otro:
            sabor = sabor_otro
        if tamano == "Otro" and tamano_otro:
            tamano = tamano_otro

        # 📸 Guardar la imagen si se sube
        foto_path = None
        if foto and validar_imagen(foto):
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{foto.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)

            with open(file_path, "wb") as f:
                content = await foto.read()
                if len(content) > MAX_FILE_SIZE:
                    raise HTTPException(status_code=400, detail="El archivo excede los 5 MB permitidos.")
                f.write(content)
            foto_path = f"/static/uploads/{filename}"

        # 💰 Calcular precio
        if precio_personalizado and precio_personalizado > 0:
            precio_total = precio_personalizado * cantidad
        else:
            precio_unitario = obtener_precio_unitario(sabor, tamano)
            precio_total = precio_unitario * cantidad

        # 📅 Convertir fecha
        fecha_entrega_dt = datetime.strptime(fecha_entrega, "%Y-%m-%d")

        # 🧾 Insertar en la base de datos
        db = DatabaseManager()
        db.insertar_pedido_cliente(
            sabor=sabor,
            tamano=tamano,
            cantidad=cantidad,
            sucursal=sucursal,
            fecha_entrega=fecha_entrega_dt,
            color=color,
            dedicatoria=dedicatoria,
            detalles=detalles,
            precio_total=precio_total,
            foto_path=foto_path
        )

        logger.info(f"Pedido de cliente registrado: {sabor} ({tamano}) - {sucursal}")
        return RedirectResponse(url="/clientes/formulario", status_code=303)

    except Exception as e:
        logger.error(f"Error al registrar pedido de cliente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al registrar el pedido: {str(e)}")

