from fastapi import APIRouter, Request, Form, HTTPException, UploadFile, File
from typing import Optional
from datetime import datetime, date
import logging
import shutil
import os
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos API"])

BASE_DIR = Path(__file__).parent.parent.absolute()
STATIC_UPLOADS = BASE_DIR / "static" / "uploads"
os.makedirs(STATIC_UPLOADS, exist_ok=True)


def parse_fecha_entrega(fecha_str):
    if not fecha_str:
        return None
    try:
        if isinstance(fecha_str, str):
            if 'T' in fecha_str:
                return datetime.fromisoformat(fecha_str.replace('Z', '+00:00')).date()
            return datetime.strptime(fecha_str, '%Y-%m-%d').date()
        elif isinstance(fecha_str, datetime):
            return fecha_str.date()
        elif isinstance(fecha_str, date):
            return fecha_str
    except Exception:
        return None


@router.get("/normales")
async def get_pedidos_normales(
    request: Request, 
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
):
    from auth import verificar_sesion

    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        from database import DatabaseManager
        db = DatabaseManager()

        if not fecha_inicio:
            fecha_inicio = date.today().isoformat()
        if not fecha_fin:
            fecha_fin = fecha_inicio

        pedidos = db.obtener_pasteles_normales(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            sucursal=user_data['sucursal']
        )

        hoy = date.today()
        for pedido in pedidos:
            pedido['total'] = pedido.get('precio', 0) * pedido.get('cantidad', 0)
            fecha_entrega = parse_fecha_entrega(pedido.get('fecha_entrega'))
            pedido['editable'] = fecha_entrega >= hoy if fecha_entrega else False
            if fecha_entrega:
                pedido['fecha_entrega'] = fecha_entrega.isoformat()

        return {"pedidos": pedidos}
    except Exception as e:
        logger.error(f"Error fetching normal orders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clientes")
async def get_pedidos_clientes(
    request: Request,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None
):
    from auth import verificar_sesion

    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        from database import DatabaseManager
        db = DatabaseManager()

        if not fecha_inicio:
            fecha_inicio = date.today().isoformat()
        if not fecha_fin:
            fecha_fin = fecha_inicio

        pedidos = db.obtener_pedidos_clientes(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            sucursal=user_data['sucursal']
        )

        hoy = date.today()
        for pedido in pedidos:
            fecha_entrega = parse_fecha_entrega(pedido.get('fecha_entrega'))
            pedido['editable'] = fecha_entrega >= hoy if fecha_entrega else False
            if fecha_entrega:
                pedido['fecha_entrega'] = fecha_entrega.isoformat()

        return {"pedidos": pedidos}
    except Exception as e:
        logger.error(f"Error fetching client orders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/registrar")
async def registrar_pedido(
        request: Request,
        tipo: str = Form(...),  # 'normal' o 'cliente'
        sabor: str = Form(...),
        tamano: str = Form(...),
        cantidad: int = Form(...),
        fecha_entrega: Optional[str] = Form(None),
        detalles: Optional[str] = Form(None),
        color: Optional[str] = Form(None),
        dedicatoria: Optional[str] = Form(None),
        # foto es opcional, solo para pedidos de cliente
        foto: Optional[UploadFile] = File(None)
):
    from auth import verificar_sesion

    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")

    tipo = (tipo or "").strip().lower()
    if tipo not in ("normal", "cliente"):
        raise HTTPException(status_code=400, detail="Tipo inválido (debe ser 'normal' o 'cliente')")

    if not sabor or not tamano:
        raise HTTPException(status_code=400, detail="Faltan campos obligatorios: sabor y tamaño")

    try:
        fecha_obj = parse_fecha_entrega(fecha_entrega) if fecha_entrega else None

        if fecha_entrega and not fecha_obj:
            raise HTTPException(status_code=400, detail="Formato de fecha de entrega inválido. Use YYYY-MM-DD")

        if cantidad is None or int(cantidad) <= 0:
            raise HTTPException(status_code=400, detail="Cantidad inválida")

        # Preparar datos comunes
        pedido_data = {
            "sabor": sabor.strip(),
            "tamano": tamano.strip(),
            "cantidad": int(cantidad),
            "fecha_entrega": fecha_obj.isoformat() if fecha_obj else None,
            "detalles": detalles.strip() if detalles else "",
            "sucursal": user_data.get("sucursal"),
            "precio": None,
            "sabor_personalizado": None
        }

        # Guardar archivo foto (si viene) y devolver ruta relativa
        foto_path = None
        if foto and foto.filename:
            filename = f"{int(datetime.now().timestamp())}_{os.path.basename(foto.filename)}"
            destino = STATIC_UPLOADS / filename
            with destino.open("wb") as f:
                shutil.copyfileobj(foto.file, f)
            foto_path = f"/static/uploads/{filename}"
            pedido_data["foto_path"] = foto_path

        from database import DatabaseManager
        db = DatabaseManager()

        if tipo == "normal":
            try:
                precio = db.obtener_precio_por_sabor_tamano(sabor.strip(), tamano.strip())
                pedido_data["precio"] = float(precio) if precio else 0
            except Exception:
                pedido_data["precio"] = 0

            # Insertar usando la función que tenga tu DB (ajusta nombre si es distinto)
            if hasattr(db, "insertar_pastel_normal"):
                new_id = db.insertar_pastel_normal(pedido_data)
            elif hasattr(db, "crear_pastel_normal"):
                new_id = db.crear_pastel_normal(pedido_data)
            else:
                # Si no tienes una función concreta, intenta método genérico
                if hasattr(db, "guardar_pastel_normal"):
                    new_id = db.guardar_pastel_normal(pedido_data)
                else:
                    raise Exception("Función de inserción para 'normal' no encontrada en DatabaseManager")

            return {"success": True, "message": "Pedido normal registrado", "id": new_id}

        else:  # cliente
            pedido_data["color"] = color.strip() if color else None
            pedido_data["dedicatoria"] = dedicatoria.strip() if dedicatoria else None

            # Obtenemos precio si existe
            try:
                precio = db.obtener_precio_por_sabor_tamano(sabor.strip(), tamano.strip())
                pedido_data["precio"] = float(precio) if precio else 0
            except Exception:
                pedido_data["precio"] = 0

            if hasattr(db, "insertar_pedido_cliente"):
                new_id = db.insertar_pedido_cliente(pedido_data)
            elif hasattr(db, "crear_pedido_cliente"):
                new_id = db.crear_pedido_cliente(pedido_data)
            else:
                if hasattr(db, "guardar_pedido_cliente"):
                    new_id = db.guardar_pedido_cliente(pedido_data)
                else:
                    raise Exception("Función de inserción para 'cliente' no encontrada en DatabaseManager")

            return {"success": True, "message": "Pedido de cliente registrado", "id": new_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering order: {e}", exc_info=True)
        # Si ocurrió un fallo guardando la foto, intenta limpiar el archivo
        try:
            if foto and foto_path:
                fp = STATIC_UPLOADS / Path(foto_path).name
                if fp.exists():
                    fp.unlink()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Error al registrar pedido: {str(e)}")


@router.put("/normal/{pedido_id}")
async def actualizar_pedido_normal(
        request: Request,
        pedido_id: int,
        cantidad: int = Form(..., gt=0),
        fecha_entrega: str = Form(...),
        detalles: Optional[str] = Form(None)
):
    from auth import verificar_sesion

    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        from database import obtener_normal_por_id_db, actualizar_pastel_normal_db

        pedido = obtener_normal_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if pedido.get('sucursal') != user_data['sucursal']:
            raise HTTPException(status_code=403, detail="No autorizado para editar este pedido")

        fecha_entrega_obj = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
        if fecha_entrega_obj < date.today():
            raise HTTPException(status_code=400, detail="No se pueden editar pedidos con fecha de entrega pasada")

        actualizar_pastel_normal_db(pedido_id, {
            'sabor': pedido.get('sabor'),
            'tamano': pedido.get('tamano'),
            'cantidad': cantidad,
            'precio': pedido.get('precio'),
            'sucursal': pedido.get('sucursal'),
            'fecha_entrega': fecha_entrega,
            'detalles': detalles or pedido.get('detalles', ''),
            'sabor_personalizado': pedido.get('sabor_personalizado')
        })

        logger.info(f"Updated normal order {pedido_id} by {user_data['username']}")
        return {"success": True, "message": "Pedido actualizado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating normal order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")


@router.put("/cliente/{pedido_id}")
async def actualizar_pedido_cliente(
        request: Request,
        pedido_id: int,
        cantidad: int = Form(..., gt=0),
        fecha_entrega: str = Form(...),
        color: Optional[str] = Form(None),
        dedicatoria: Optional[str] = Form(None),
        detalles: Optional[str] = Form(None)
):
    from auth import verificar_sesion

    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        from database import obtener_cliente_por_id_db, actualizar_pedido_cliente_db

        pedido = obtener_cliente_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if pedido.get('sucursal') != user_data['sucursal']:
            raise HTTPException(status_code=403, detail="No autorizado para editar este pedido")

        fecha_entrega_obj = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
        if fecha_entrega_obj < date.today():
            raise HTTPException(status_code=400, detail="No se pueden editar pedidos con fecha de entrega pasada")

        actualizar_pedido_cliente_db(pedido_id, {
            'color': color or pedido.get('color'),
            'sabor': pedido.get('sabor'),
            'tamano': pedido.get('tamano'),
            'cantidad': cantidad,
            'precio': pedido.get('precio'),
            'sucursal': pedido.get('sucursal'),
            'dedicatoria': dedicatoria if dedicatoria is not None else pedido.get('dedicatoria'),
            'detalles': detalles if detalles is not None else pedido.get('detalles'),
            'sabor_personalizado': pedido.get('sabor_personalizado'),
            'foto_path': pedido.get('foto_path'),
            'fecha_entrega': fecha_entrega
        })

        logger.info(f"Updated client order {pedido_id} by {user_data['username']}")
        return {"success": True, "message": "Pedido actualizado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")


@router.delete("/normal/{pedido_id}")
async def eliminar_pedido_normal(request: Request, pedido_id: int):
    from auth import verificar_sesion

    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        from database import obtener_normal_por_id_db, eliminar_normal_db

        pedido = obtener_normal_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if pedido.get('sucursal') != user_data['sucursal']:
            raise HTTPException(status_code=403, detail="No autorizado para eliminar este pedido")

        fecha_entrega = parse_fecha_entrega(pedido.get('fecha_entrega'))
        if fecha_entrega and fecha_entrega < date.today():
            raise HTTPException(status_code=400, detail="No se pueden eliminar pedidos con fecha de entrega pasada")

        eliminar_normal_db(pedido_id)

        logger.info(f"Deleted normal order {pedido_id} by {user_data['username']}")
        return {"success": True, "message": "Pedido eliminado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting normal order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")


@router.delete("/cliente/{pedido_id}")
async def eliminar_pedido_cliente(request: Request, pedido_id: int):
    from auth import verificar_sesion

    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")

    try:
        from database import obtener_cliente_por_id_db, eliminar_cliente_db

        pedido = obtener_cliente_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        if pedido.get('sucursal') != user_data['sucursal']:
            raise HTTPException(status_code=403, detail="No autorizado para eliminar este pedido")

        fecha_entrega = parse_fecha_entrega(pedido.get('fecha_entrega'))
        if fecha_entrega and fecha_entrega < date.today():
            raise HTTPException(status_code=400, detail="No se pueden eliminar pedidos con fecha de entrega pasada")

        eliminar_cliente_db(pedido_id)

        logger.info(f"Deleted client order {pedido_id} by {user_data['username']}")
        return {"success": True, "message": "Pedido eliminado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")
