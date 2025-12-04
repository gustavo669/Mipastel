import pyodbc
from typing import List, Dict, Any, Optional
from config.database import db_pool_normales, db_pool_clientes
from utils.logger import logger

def obtener_precio_db(sabor: str = None, tamano: str = None) -> Any:
    try:
        with db_pool_normales.get_connection() as conn:
            cursor = conn.cursor()
            
            if sabor and tamano:
                query = "SELECT precio FROM PastelesPrecios WHERE sabor = ? AND tamano = ?"
                cursor.execute(query, (sabor, tamano))
                resultado = cursor.fetchone()
                return float(resultado[0]) if resultado else 0.0
            else:
                query = "SELECT id, sabor, tamano, precio FROM PastelesPrecios ORDER BY sabor, id"
                cursor.execute(query)
                resultados = cursor.fetchall()
                return resultados

    except Exception as e:
        logger.error(f"Error al obtener precios: {e}", exc_info=True)
        if "Invalid object name 'PastelesPrecios'" in str(e):
            logger.warning("Tabla 'PastelesPrecios' no encontrada")
            return [] if not sabor else 0.0
        raise e

def actualizar_precios_db(lista_precios: List[Dict[str, Any]]) -> bool:
    try:
        with db_pool_normales.get_connection() as conn:
            cursor = conn.cursor()
            query = "UPDATE PastelesPrecios SET sabor = ?, tamano = ?, precio = ? WHERE id = ?"
            params = [(p['sabor'], p['tamano'], p['precio'], p['id']) for p in lista_precios]
            
            cursor.executemany(query, params)
            conn.commit()
            logger.info(f"Se actualizaron {len(params)} precios")
            return True
    except Exception as e:
        logger.error(f"Error al actualizar precios: {e}", exc_info=True)
        raise Exception(f"Error al actualizar precios: {e}")

def registrar_pastel_normal_db(data: Dict[str, Any]) -> int:
    query = """
        INSERT INTO PastelesNormales 
        (sabor, tamano, cantidad, precio, sucursal, fecha_entrega, detalles, sabor_personalizado, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
    """
    
    params = (
        data.get('sabor'),
        data.get('tamano'),
        data.get('cantidad'),
        data.get('precio'),
        data.get('sucursal'),
        data.get('fecha_entrega'),
        data.get('detalles'),
        data.get('sabor_personalizado'),
    )
    
    try:
        with db_pool_normales.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            cursor.execute("SELECT @@IDENTITY")
            new_id = cursor.fetchone()[0]
            
            conn.commit()
            logger.info(f"Pedido normal #{new_id} registrado exitosamente")
            return int(new_id)
            
    except Exception as e:
        logger.error(f"Error al registrar pastel normal: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def actualizar_pastel_normal_db(pedido_id: int, data: Dict[str, Any]) -> bool:
    query = """
        UPDATE PastelesNormales SET
            sabor = ?, tamano = ?, cantidad = ?, precio = ?, sucursal = ?, 
            fecha_entrega = ?, detalles = ?, sabor_personalizado = ?
        WHERE id = ?
    """
    params = (
        data.get('sabor'), data.get('tamano'), data.get('cantidad'),
        data.get('precio'), data.get('sucursal'), data.get('fecha_entrega'),
        data.get('detalles'), data.get('sabor_personalizado'),
        pedido_id
    )
    try:
        with db_pool_normales.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            logger.info(f"Pedido normal #{pedido_id} actualizado")
            return True
    except Exception as e:
        logger.error(f"Error al actualizar pastel normal ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def eliminar_normal_db(pedido_id: int) -> bool:
    try:
        with db_pool_normales.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM PastelesNormales WHERE id = ?", (pedido_id,))
            conn.commit()
            logger.info(f"Pedido normal #{pedido_id} eliminado")
            return True
    except Exception as e:
        logger.error(f"Error al eliminar pastel normal ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def obtener_normal_por_id_db(pedido_id: int) -> Optional[Dict[str, Any]]:
    try:
        with db_pool_normales.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, sabor, tamano, cantidad, precio, sucursal, fecha, fecha_entrega, detalles, sabor_personalizado FROM PastelesNormales WHERE id = ?"
            cursor.execute(query, (pedido_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'id': row[0], 'sabor': row[1], 'tamano': row[2], 'cantidad': row[3],
                'precio': float(row[4]), 'sucursal': row[5], 'fecha': row[6].isoformat() if row[6] else None,
                'fecha_entrega': row[7].isoformat() if row[7] else None,
                'detalles': row[8], 'sabor_personalizado': row[9]
            }
    except Exception as e:
        logger.error(f"Error al obtener normal por ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def registrar_pedido_cliente_db(data: Dict[str, Any]) -> int:
    precio = data.get('precio')
    if not precio or precio <= 0:
        raise ValueError("El precio debe ser mayor a 0")
    
    query = """
        INSERT INTO PastelesClientes 
        (color, sabor, tamano, cantidad, precio, sucursal, fecha, 
         dedicatoria, detalles, sabor_personalizado, foto_path, fecha_entrega)
        VALUES (?, ?, ?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, ?)
    """
    params = (
        data.get('color'), data.get('sabor'), data.get('tamano'), data.get('cantidad'),
        precio, data.get('sucursal'),
        data.get('dedicatoria'), data.get('detalles'), data.get('sabor_personalizado'),
        data.get('foto_path'), data.get('fecha_entrega')
    )
    try:
        with db_pool_clientes.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            cursor.execute("SELECT @@IDENTITY")
            new_id = cursor.fetchone()[0]
            
            conn.commit()
            logger.info(f"Pedido cliente #{new_id} registrado exitosamente")
            return int(new_id)
    except Exception as e:
        logger.error(f"Error al registrar pedido cliente: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def actualizar_pedido_cliente_db(pedido_id: int, data: Dict[str, Any]) -> bool:
    precio = data.get('precio')
    if precio and precio <= 0:
        raise ValueError("El precio debe ser mayor a 0")
    
    query = """
        UPDATE PastelesClientes SET
            color = ?, sabor = ?, tamano = ?, cantidad = ?, precio = ?, sucursal = ?,
            dedicatoria = ?, detalles = ?, sabor_personalizado = ?, 
            foto_path = ?, fecha_entrega = ?
        WHERE id = ?
    """
    params = (
        data.get('color'), data.get('sabor'), data.get('tamano'), data.get('cantidad'),
        precio, data.get('sucursal'),
        data.get('dedicatoria'), data.get('detalles'), data.get('sabor_personalizado'),
        data.get('foto_path'), data.get('fecha_entrega'),
        pedido_id
    )
    try:
        with db_pool_clientes.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            logger.info(f"Pedido cliente #{pedido_id} actualizado")
            return True
    except Exception as e:
        logger.error(f"Error al actualizar pedido cliente ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def eliminar_cliente_db(pedido_id: int) -> bool:
    try:
        with db_pool_clientes.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM PastelesClientes WHERE id = ?", (pedido_id,))
            conn.commit()
            logger.info(f"Pedido cliente #{pedido_id} eliminado")
            return True
    except Exception as e:
        logger.error(f"Error al eliminar cliente ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def obtener_cliente_por_id_db(pedido_id: int) -> Optional[Dict[str, Any]]:
    try:
        with db_pool_clientes.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT id, color, sabor, tamano, cantidad, precio, total, sucursal, 
                       fecha, foto_path, dedicatoria, detalles, fecha_entrega, sabor_personalizado
                FROM PastelesClientes WHERE id = ?
            """
            cursor.execute(query, (pedido_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'id': row[0], 'color': row[1], 'sabor': row[2], 'tamano': row[3],
                'cantidad': row[4], 'precio': float(row[5]), 'total': float(row[6]),
                'sucursal': row[7], 'fecha': row[8].isoformat() if row[8] else None, 'foto_path': row[9],
                'dedicatoria': row[10], 'detalles': row[11],
                'fecha_entrega': row[12].isoformat() if row[12] else None,
                'sabor_personalizado': row[13]
            }
    except Exception as e:
        logger.error(f"Error al obtener cliente por ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

class DatabaseManager:
    def _ejecutar_query(self, db_pool, query, params=(), commit=False, fetchone=False, fetchall=False):
        try:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                resultado = None
                if fetchone:
                    resultado = cursor.fetchone()
                if fetchall:
                    resultado = cursor.fetchall()
                
                if commit:
                    conn.commit()
                
                return resultado
        except Exception as e:
            logger.error(f"Error de DB en query ({query[:50]}...): {e}", exc_info=True)
            raise

    def obtener_precios(self) -> List[Dict[str, Any]]:
        resultados = obtener_precio_db()
        precios = []
        for row in resultados:
            precios.append({
                'id': row[0],
                'sabor': row[1],
                'tamano': row[2],
                'precio': float(row[3])
            })
        return precios

    def obtener_precio_por_sabor_tamano(self, sabor: str, tamano: str) -> float:
        return obtener_precio_db(sabor, tamano)

    def actualizar_precios(self, lista_precios: List[Dict[str, Any]]) -> bool:
        return actualizar_precios_db(lista_precios)

    def registrar_pastel_normal(self, data: Dict[str, Any]) -> int:
        return registrar_pastel_normal_db(data)

    def insertar_pastel_normal(self, data: Dict[str, Any]) -> int:
        return registrar_pastel_normal_db(data)

    def crear_pastel_normal(self, data: Dict[str, Any]) -> int:
        return registrar_pastel_normal_db(data)

    def guardar_pastel_normal(self, data: Dict[str, Any]) -> int:
        return registrar_pastel_normal_db(data)

    def obtener_pasteles_normales(self, fecha_inicio: str = None, fecha_fin: str = None, sucursal: str = None) -> List[Dict[str, Any]]:
        query = "SELECT id, sabor, tamano, precio, cantidad, sucursal, fecha, fecha_entrega, detalles, sabor_personalizado FROM PastelesNormales WHERE 1=1"
        params = []

        if fecha_inicio and not fecha_fin:
            fecha_fin = fecha_inicio

        if fecha_inicio and fecha_fin:
            query += " AND CAST(fecha AS DATE) BETWEEN ? AND ?"
            params.extend([fecha_inicio, fecha_fin])
        elif not fecha_inicio:
            query += " AND CAST(fecha AS DATE) = CAST(GETDATE() AS DATE)"

        if sucursal:
            sucursal_lower = sucursal.lower()
            if sucursal_lower != "todas":
                query += " AND sucursal = ?"
                params.append(sucursal)

        query += " ORDER BY fecha DESC"

        resultados = self._ejecutar_query(db_pool_normales, query, tuple(params), fetchall=True)

        pasteles = []
        for row in resultados:
            pasteles.append({
                'id': row[0],
                'sabor': row[1],
                'tamano': row[2],
                'precio': float(row[3]),
                'cantidad': row[4],
                'sucursal': row[5],
                'fecha': row[6].isoformat() if row[6] else None,
                'fecha_entrega': row[7].isoformat() if row[7] else None,
                'detalles': row[8],
                'sabor_personalizado': row[9]
            })
        return pasteles

    def eliminar_pastel_normal(self, pastel_id: int) -> bool:
        return eliminar_normal_db(pastel_id)

    def registrar_pedido_cliente(self, data: Dict[str, Any]) -> int:
        return registrar_pedido_cliente_db(data)

    def insertar_pedido_cliente(self, data: Dict[str, Any]) -> int:
        return registrar_pedido_cliente_db(data)

    def crear_pedido_cliente(self, data: Dict[str, Any]) -> int:
        return registrar_pedido_cliente_db(data)

    def guardar_pedido_cliente(self, data: Dict[str, Any]) -> int:
        return registrar_pedido_cliente_db(data)

    def obtener_pedidos_clientes(self, fecha_inicio: str = None, fecha_fin: str = None, sucursal: str = None) -> List[Dict[str, Any]]:
        query = ("SELECT id, color, sabor, tamano, cantidad, precio, total, sucursal, fecha, "
                 "foto_path, dedicatoria, detalles, fecha_entrega, sabor_personalizado FROM PastelesClientes WHERE 1=1")
        params = []

        if fecha_inicio and not fecha_fin:
            fecha_fin = fecha_inicio

        if fecha_inicio and fecha_fin:
            query += " AND CAST(fecha AS DATE) BETWEEN ? AND ?"
            params.extend([fecha_inicio, fecha_fin])

        if not fecha_inicio:
            query += " AND CAST(fecha AS DATE) = CAST(GETDATE() AS DATE)"

        if sucursal:
            sucursal_lower = sucursal.lower()
            if sucursal_lower != "todas":
                query += " AND sucursal = ?"
                params.append(sucursal)

        query += " ORDER BY fecha DESC"

        resultados = self._ejecutar_query(db_pool_clientes, query, tuple(params), fetchall=True)

        pedidos = []
        for row in resultados:
            pedidos.append({
                'id': row[0],
                'color': row[1],
                'sabor': row[2],
                'tamano': row[3],
                'cantidad': row[4],
                'precio': float(row[5]),
                'total': float(row[6]),
                'sucursal': row[7],
                'fecha': row[8].isoformat() if row[8] else None,
                'foto_path': row[9],
                'dedicatoria': row[10],
                'detalles': row[11],
                'fecha_entrega': row[12].isoformat() if row[12] else None,
                'sabor_personalizado': row[13]
            })
        return pedidos

    def eliminar_pedido_cliente(self, pedido_id: int) -> bool:
        return eliminar_cliente_db(pedido_id)

    def obtener_estadisticas(self, fecha_inicio: str = None, fecha_fin: str = None) -> Dict[str, Any]:
        if fecha_inicio and not fecha_fin:
            fecha_fin = fecha_inicio

        normales = self.obtener_pasteles_normales(fecha_inicio, fecha_fin)
        clientes = self.obtener_pedidos_clientes(fecha_inicio, fecha_fin)

        stats = {
            'normales_count': len(normales),
            'normales_cantidad': sum(p['cantidad'] for p in normales),
            'normales_ingresos': sum(p['precio'] * p['cantidad'] for p in normales),
            'clientes_count': len(clientes),
            'clientes_cantidad': sum(p['cantidad'] for p in clientes),
            'clientes_ingresos': sum(p['total'] for p in clientes),
        }
        return stats
