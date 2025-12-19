import logging
from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from api.auth import requiere_autenticacion, requiere_permiso_sucursal
from config import (
    SABORES_NORMALES, TAMANOS_NORMALES, SUCURSALES
)
from database import DatabaseManager, obtener_precio_db

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
        es_otro: Optional[bool] = Form(False),  # ← AHORA CON DEFAULT
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

        # Determinar sabor real
        sabor_real = sabor_personalizado if sabor_personalizado else sabor

        # Usar precio enviado, si no está disponible obtener de base de datos
        if precio and precio > 0:
            precio_unitario = precio
            logger.info(f"Usando precio del cliente: Q{precio_unitario:.2f}")
        else:
            precio_unitario = obtener_precio_db(sabor, tamano)
            logger.info(f"Obtenido precio de base de datos: Q{precio_unitario:.2f}")

        if precio_unitario <= 0 and not es_otro:
            raise HTTPException(
                status_code=400,
                detail=f"No se encontró precio para {sabor} {tamano}. Use la opción 'Otro' para precios personalizados."
            )

        # Validar fecha de entrega
        try:
            fecha_valida = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
            if fecha_valida < date.today():
                raise HTTPException(status_code=400, detail="La fecha de entrega no puede ser anterior a hoy")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido (use YYYY-MM-DD)")

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
                f"Pastel normal registrado por {user_data['username']}: {sabor_real} {tamano} x{cantidad} - "
                f"Q{precio_total:.2f} - {sucursal} (Entrega: {fecha_entrega})"
            )

            # Registrar en auditoría
            try:
                from utils.audit import log_pedido_normal_created
                log_pedido_normal_created(
                    username=user_data['username'],
                    pedido_id=resultado,
                    sucursal=sucursal,
                    sabor=sabor_real,
                    tamano=tamano
                )
            except Exception as audit_error:
                logger.warning(f"Error al registrar auditoría: {audit_error}")

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