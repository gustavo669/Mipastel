from fastapi import APIRouter, Request, Form, HTTPException
from typing import Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos API"])


@router.get("/normales")
async def get_pedidos_normales(request: Request, fecha: Optional[str] = None):
    """Get normal orders for current sucursal"""
    from auth import verificar_sesion
    
    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        if not fecha:
            fecha = date.today().isoformat()
        
        pedidos = db.obtener_pasteles_normales(
            fecha_inicio=fecha,
            fecha_fin=fecha,
            sucursal=user_data['sucursal']
        )
        
        # Add editable status based on delivery date
        hoy = date.today()
        for pedido in pedidos:
            fecha_entrega = pedido.get('fecha_entrega')
            
            # Handle different date formats
            if isinstance(fecha_entrega, str):
                try:
                    fecha_entrega = datetime.strptime(fecha_entrega, '%Y-%m-%d').date()
                except:
                    fecha_entrega = None
            elif isinstance(fecha_entrega, datetime):
                fecha_entrega = fecha_entrega.date()
            
            pedido['editable'] = fecha_entrega >= hoy if fecha_entrega else False
        
        return {"pedidos": pedidos}
    except Exception as e:
        logger.error(f"Error fetching normal orders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clientes")
async def get_pedidos_clientes(request: Request, fecha: Optional[str] = None):
    """Get client orders for current sucursal"""
    from auth import verificar_sesion
    
    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        if not fecha:
            fecha = date.today().isoformat()
        
        pedidos = db.obtener_pasteles_clientes(
            fecha_inicio=fecha,
            fecha_fin=fecha,
            sucursal=user_data['sucursal']
        )
        
        # Add editable status based on delivery date
        hoy = date.today()
        for pedido in pedidos:
            fecha_entrega = pedido.get('fecha_entrega')
            
            # Handle different date formats
            if isinstance(fecha_entrega, str):
                try:
                    fecha_entrega = datetime.strptime(fecha_entrega, '%Y-%m-%d').date()
                except:
                    fecha_entrega = None
            elif isinstance(fecha_entrega, datetime):
                fecha_entrega = fecha_entrega.date()
            
            pedido['editable'] = fecha_entrega >= hoy if fecha_entrega else False
        
        return {"pedidos": pedidos}
    except Exception as e:
        logger.error(f"Error fetching client orders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/normal/{pedido_id}")
async def actualizar_pedido_normal(
    request: Request,
    pedido_id: int,
    cantidad: int = Form(..., gt=0),
    fecha_entrega: str = Form(...)
):
    """Update a normal order (only today/future orders)"""
    from auth import verificar_sesion
    
    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        from database import obtener_normal_por_id_db, actualizar_pastel_normal_db
        
        # Get existing order
        pedido = obtener_normal_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Verify belongs to user's sucursal
        if pedido.get('sucursal') != user_data['sucursal']:
            raise HTTPException(status_code=403, detail="No autorizado para editar este pedido")
        
        # Verify order delivery date is today or future
        fecha_entrega_obj = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
        if fecha_entrega_obj < date.today():
            raise HTTPException(status_code=400, detail="No se pueden editar pedidos con fecha de entrega pasada")
        
        # Calculate new total
        precio_unitario = pedido.get('precio', 0)
        total = precio_unitario * cantidad
        
        # Update order
        actualizar_pastel_normal_db(pedido_id, {
            'cantidad': cantidad,
            'fecha_entrega': fecha_entrega,
            'total': total
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
    """Update a client order (only today/future orders)"""
    from auth import verificar_sesion
    
    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        from database import obtener_cliente_por_id_db, actualizar_pastel_cliente_db
        
        # Get existing order
        pedido = obtener_cliente_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Verify belongs to user's sucursal
        if pedido.get('sucursal') != user_data['sucursal']:
            raise HTTPException(status_code=403, detail="No autorizado para editar este pedido")
        
        # Verify order delivery date is today or future
        fecha_entrega_obj = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
        if fecha_entrega_obj < date.today():
            raise HTTPException(status_code=400, detail="No se pueden editar pedidos con fecha de entrega pasada")
        
        # Calculate new total
        precio_unitario = pedido.get('precio', 0)
        total = precio_unitario * cantidad
        
        # Update order
        actualizar_pastel_cliente_db(pedido_id, {
            'cantidad': cantidad,
            'fecha_entrega': fecha_entrega,
            'color': color,
            'dedicatoria': dedicatoria,
            'detalles': detalles,
            'total': total
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
    """Delete a normal order (only today/future orders)"""
    from auth import verificar_sesion
    
    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        from database import obtener_normal_por_id_db, eliminar_normal_db
        
        # Get existing order
        pedido = obtener_normal_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Verify belongs to user's sucursal
        if pedido.get('sucursal') != user_data['sucursal']:
            raise HTTPException(status_code=403, detail="No autorizado para eliminar este pedido")
        
        # Verify order delivery date is today or future
        fecha_entrega = pedido.get('fecha_entrega')
        if isinstance(fecha_entrega, str):
            fecha_entrega = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
        elif isinstance(fecha_entrega, datetime):
            fecha_entrega = fecha_entrega.date()
        
        if fecha_entrega < date.today():
            raise HTTPException(status_code=400, detail="No se pueden eliminar pedidos con fecha de entrega pasada")
        
        # Delete order
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
    """Delete a client order (only today/future orders)"""
    from auth import verificar_sesion
    
    user_data = verificar_sesion(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    try:
        from database import obtener_cliente_por_id_db, eliminar_cliente_db
        
        # Get existing order
        pedido = obtener_cliente_por_id_db(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Verify belongs to user's sucursal
        if pedido.get('sucursal') != user_data['sucursal']:
            raise HTTPException(status_code=403, detail="No autorizado para eliminar este pedido")
        
        # Verify order delivery date is today or future
        fecha_entrega = pedido.get('fecha_entrega')
        if isinstance(fecha_entrega, str):
            fecha_entrega = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
        elif isinstance(fecha_entrega, datetime):
            fecha_entrega = fecha_entrega.date()
        
        if fecha_entrega < date.today():
            raise HTTPException(status_code=400, detail="No se pueden eliminar pedidos con fecha de entrega pasada")
        
        # Delete order
        eliminar_cliente_db(pedido_id)
        
        logger.info(f"Deleted client order {pedido_id} by {user_data['username']}")
        return {"success": True, "message": "Pedido eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")
