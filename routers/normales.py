from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from database import DatabaseManager, obtener_precio_db
import logging
from typing import Optional
from config import (
    SABORES_NORMALES, TAMANOS_NORMALES, SUCURSALES
)
from api.auth import requiere_autenticacion, requiere_permiso_sucursal

router = APIRouter(prefix="/normales", tags=["Pasteles Normales"])
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")


@router.get("/formulario")
async def mostrar_formulario_normales(
        request: Request,
        user_data: dict = Depends(requiere_autenticacion)
):
    """
    Display the normal cakes order form.
    
    Requires authentication.
    """
    try:
        return templates.TemplateResponse("formulario_normales.html", {
            "request": request,
            "sabores_normales": SABORES_NORMALES,
            "tamanos": TAMANOS_NORMALES,
            "sucursales": SUCURSALES,
            "user_data": user_data
        })
    except Exception as e:
        logger.error(f"Error al cargar formulario normales: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al cargar formulario: {str(e)}")


@router.post("/registrar")
async def registrar_pedido_normal(
        request: Request,
        sabor: str = Form(...),
        tamano: str = Form(...),
        cantidad: int = Form(..., gt=0),
        sucursal: str = Form(...),
        fecha_entrega: str = Form(...),
        precio: Optional[float] = Form(None),
        detalles: Optional[str] = Form(None),
        sabor_personalizado: Optional[str] = Form(None),
        es_otro: Optional[bool] = Form(False),
        user_data: dict = Depends(requiere_autenticacion)
):
    """
    Register a normal cake order.
    
    Requires authentication and branch permission.
    Users can only register orders for their assigned branch (except admins).
    """
    try:
        # Verify branch permission
        requiere_permiso_sucursal(user_data, sucursal)
        if tamano not in TAMANOS_NORMALES:
            raise HTTPException(status_code=400, detail="Tamaño inválido")

        sabor_real = sabor_personalizado if es_otro and sabor_personalizado else sabor

        # Use sent precio if provided, otherwise fetch from database
        if precio and precio > 0:
            precio_unitario = precio
            logger.info(f"Using precio from frontend: Q{precio_unitario:.2f}")
        else:
            precio_unitario = obtener_precio_db(sabor, tamano)
            logger.info(f"Fetched precio from database: Q{precio_unitario:.2f}")

        if precio_unitario <= 0 and not es_otro:
            raise HTTPException(
                status_code=400,
                detail=f"No se encontró precio para {sabor} {tamano}. Use la opción 'Otro' para precios personalizados."
            )

        try:
            from datetime import datetime
            fecha_valida = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
        except:
            raise HTTPException(status_code=400, detail="Fecha de entrega inválida")

        precio_total = precio_unitario * cantidad

        pastel_data = {
            'sabor': sabor_real,
            'tamano': tamano,
            'cantidad': cantidad,
            'precio': precio_unitario,
            'sucursal': sucursal,
            'detalles': detalles or '',
            'sabor_personalizado': sabor_personalizado or '',
            'fecha_entrega': fecha_entrega
        }

        db = DatabaseManager()
        resultado = db.registrar_pastel_normal(pastel_data)

        if resultado:
            logger.info(
                f"Pastel normal registrado: {sabor_real} {tamano} x{cantidad} - "
                f"Q{precio_total:.2f} - {sucursal} (Entrega: {fecha_entrega})"
            )
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
        logger.error(f"Error al registrar pastel normal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al registrar el pastel: {str(e)}")
