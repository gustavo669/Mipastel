from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates
from database import DatabaseManager, obtener_precio_db
from datetime import datetime
import logging
from typing import Optional
from config import (
    SABORES_NORMALES, TAMANOS_NORMALES, SUCURSALES
)

router = APIRouter(prefix="/normales", tags=["Pasteles Normales"])
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="templates")

def calcular_precio(sabor: str, tamano: str, cantidad: int) -> float:
    try:
        precio_unitario = obtener_precio_db(sabor, tamano)
        return precio_unitario * cantidad
    except Exception as e:
        logger.error(f"Error al calcular precio: {e}")
        return 0.0

def obtener_precio_unitario(sabor: str, tamano: str) -> float:
    try:
        return obtener_precio_db(sabor, tamano)
    except Exception as e:
        logger.error(f"Error al obtener precio unitario: {e}")
        return 0.0

@router.get("/formulario")
async def mostrar_formulario_normales(request: Request):
    try:
        return templates.TemplateResponse("formulario_normales.html", {
            "request": request,
            "sabores_normales": SABORES_NORMALES,
            "tamanos": TAMANOS_NORMALES,
            "sucursales": SUCURSALES
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
        detalles: Optional[str] = Form(None),
        es_otro: bool = Form(False),
        sabor_personalizado: Optional[str] = Form(None)
):
    try:
        if tamano not in TAMANOS_NORMALES:
            raise HTTPException(status_code=400, detail="Tamaño inválido")

        sabor_real = sabor_personalizado if es_otro and sabor_personalizado else sabor
        precio_unitario = obtener_precio_unitario(sabor, tamano)

        if precio_unitario == 0 and not es_otro:
            raise HTTPException(
                status_code=400,
                detail=f"No se encontró precio para {sabor} {tamano}. Use la opción 'Otro' para precios personalizados."
            )

        precio_total = precio_unitario * cantidad
        pastel_data = {
            'sabor': sabor_real,
            'tamano': tamano,
            'cantidad': cantidad,
            'precio': precio_unitario,
            'sucursal': sucursal,
            'detalles': detalles or '',
            'sabor_personalizado': sabor_personalizado or ''
        }

        db = DatabaseManager()
        resultado = db.registrar_pastel_normal(pastel_data)

        if resultado:
            logger.info(f"Pastel normal registrado: {sabor_real} {tamano} x{cantidad} - Q{precio_total:.2f} - {sucursal}")
            return templates.TemplateResponse("exito.html", {
                "request": request,
                "mensaje": "Pastel normal registrado correctamente",
                "detalles": f"{sabor_real} {tamano} x{cantidad} - Total: Q{precio_total:.2f}",
                "tipo": "normal"
            })
        else:
            raise HTTPException(status_code=500, detail="Error al registrar el pastel en la base de datos")

    except Exception as e:
        logger.error(f"Error al registrar pastel normal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al registrar el pastel: {str(e)}")
