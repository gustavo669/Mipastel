from fastapi import APIRouter, Form, HTTPException, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from database import DatabaseManager, obtener_precio_db
from datetime import datetime, date
import os, logging
from typing import Optional
from config import SABORES_CLIENTES, TAMANOS_CLIENTES, SUCURSALES

router = APIRouter(prefix="/clientes", tags=["Pedidos de Clientes"])
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
MAX_FILE_SIZE = 5 * 1024 * 1024


def validar_imagen(file: UploadFile) -> bool:
    if not file or not file.filename:
        return False
    ext = os.path.splitext(file.filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


@router.get("/formulario")
async def mostrar_formulario_clientes(request: Request):
    """
    Display the client orders form.
    
    PUBLIC ENDPOINT - No authentication required.
    This allows customers to place orders from their phones.
    """
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


@router.post("/registrar")
async def registrar_pedido_cliente(
        request: Request,
        sabor: str = Form(...),
        tamano: str = Form(...),
        cantidad: int = Form(..., gt=0),
        sucursal: str = Form(...),
        precio: Optional[float] = Form(None),
        fecha_entrega: Optional[str] = Form(None),
        color: Optional[str] = Form(None),
        dedicatoria: Optional[str] = Form(None),
        detalles: Optional[str] = Form(None),
        sabor_personalizado: Optional[str] = Form(None),
        foto: Optional[UploadFile] = File(None)
):
    """
    Register a client order.
    
    PUBLIC ENDPOINT - No authentication required.
    This allows customers to place orders from their phones.
    """
    try:
        if fecha_entrega:
            try:
                fecha_entrega_obj = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
                if fecha_entrega_obj < date.today():
                    raise HTTPException(status_code=400, detail="La fecha de entrega no puede ser anterior a hoy")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido")

        db = DatabaseManager()
        foto_path = None
        if foto and foto.filename:
            if not validar_imagen(foto):
                raise HTTPException(status_code=400, detail="Formato de imagen no permitido")
            extension = os.path.splitext(foto.filename)[1]
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{sabor}{extension}"
            file_location = os.path.join(UPLOAD_DIR, filename)
            with open(file_location, "wb") as f:
                f.write(await foto.read())
            foto_path = file_location

        sabor_real = sabor_personalizado if sabor_personalizado else sabor

        # Use sent precio if provided, otherwise fetch from database
        if precio and precio > 0:
            precio_unitario = precio
            logger.info(f"Using precio from frontend: Q{precio_unitario:.2f}")
        else:
            precio_unitario = obtener_precio_db(sabor_real, tamano)
            logger.info(f"Fetched precio from database: Q{precio_unitario:.2f}")

        if precio_unitario <= 0:
            raise HTTPException(status_code=400, detail="No se encontró precio válido para esta combinación")

        precio_total = precio_unitario * cantidad

        pedido_data = {
            "sabor": sabor_real,
            "tamano": tamano,
            "cantidad": cantidad,
            "precio": precio_unitario,
            "sucursal": sucursal,
            "fecha_entrega": fecha_entrega,
            "color": color,
            "dedicatoria": dedicatoria,
            "detalles": detalles,
            "sabor_personalizado": sabor_personalizado or '',
            "foto_path": foto_path
        }

        resultado = db.registrar_pedido_cliente(pedido_data)

        if resultado:
            logger.info(f"Pedido de cliente registrado: {sabor_real} {tamano} x{cantidad} - Q{precio_total:.2f}")
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
        logger.error(f"Error en /clientes/registrar: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al registrar pedido de cliente: {str(e)}")