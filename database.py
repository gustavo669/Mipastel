import pyodbc
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CONFIGURACIÓN
SERVER = '(localdb)\\MSSQLLocalDB'
DRIVER = '{ODBC Driver 17 for SQL Server}'
DB_NORMALES = 'MiPastel'
DB_CLIENTES = 'MiPastel_Clientes'

# PARTE 1: Funciones de Conexión Básica

def get_db_connection(database_name):
    """Función genérica para obtener una conexión"""
    try:
        conn_str = f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={database_name};Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        logger.error(f"Error al conectar a {database_name}: {e}")
        raise Exception(f"Error de conexión: {e}")

def get_conn_normales():
    return get_db_connection(DB_NORMALES)

def get_conn_clientes():
    return get_db_connection(DB_CLIENTES)


# PARTE 2: Funciones de Datos (Standalone)

def obtener_precio_db(sabor: str = None, tamano: str = None) -> Any:
    try:
        conn = get_conn_normales()
        cursor = conn.cursor()

        if sabor and tamano:
            # Modo 1: Obtener precio unitario
            query = "SELECT precio FROM PastelesPrecios WHERE sabor = ? AND tamano = ?"
            cursor.execute(query, (sabor, tamano))
            resultado = cursor.fetchone()
            conn.close()
            return float(resultado[0]) if resultado else 0.0
        else:
            # Modo 2: Obtener toda la lista
            query = "SELECT id, sabor, tamano, precio FROM PastelesPrecios ORDER BY sabor, id"
            cursor.execute(query)
            resultados = cursor.fetchall()
            conn.close()
            return resultados

    except Exception as e:
        logger.error(f"Error al obtener precios: {e}", exc_info=True)
        if "Invalid object name 'PastelesPrecios'" in str(e):
            logger.warning("Tabla 'PastelesPrecios' no encontrada. Creando tabla de ejemplo...")
            return [] if not sabor else 0.0
        raise e

def actualizar_precios_db(lista_precios: List[Dict[str, Any]]) -> bool:
    """Actualiza masivamente los precios (para app PySide)"""
    try:
        conn = get_conn_normales()
        cursor = conn.cursor()
        query = "UPDATE PastelesPrecios SET sabor = ?, tamano = ?, precio = ? WHERE id = ?"
        params = [(p['sabor'], p['tamano'], p['precio'], p['id']) for p in lista_precios]

        cursor.executemany(query, params)
        conn.commit()
        conn.close()
        logger.info(f"Se actualizaron {len(params)} precios (via PySide).")
        return True
    except Exception as e:
        logger.error(f"Error al actualizar precios (PySide): {e}", exc_info=True)
        raise Exception(f"Error al actualizar precios: {e}")

# PARTE 3: Funciones CRUD (Standalone)
# (Usadas por admin_app.py y dialogos.py)

# CRUD PASTELES NORMALES

def registrar_pastel_normal_db(data: Dict[str, Any]) -> bool:
    """Registra un nuevo pastel normal."""
    query = """
        INSERT INTO PastelesNormales 
        (sabor, tamano, cantidad, precio, sucursal, detalles, sabor_personalizado, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
    """
    params = (
        data.get('sabor'), data.get('tamano'), data.get('cantidad'),
        data.get('precio'), data.get('sucursal'), data.get('detalles'),
        data.get('sabor_personalizado')
    )
    try:
        conn = get_conn_normales()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al registrar pastel normal: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def actualizar_pastel_normal_db(pedido_id: int, data: Dict[str, Any]) -> bool:
    """Actualiza un pastel normal existente."""
    query = """
        UPDATE PastelesNormales SET
            sabor = ?, tamano = ?, cantidad = ?, precio = ?, sucursal = ?, 
            detalles = ?, sabor_personalizado = ?
        WHERE id = ?
    """
    params = (
        data.get('sabor'), data.get('tamano'), data.get('cantidad'),
        data.get('precio'), data.get('sucursal'), data.get('detalles'),
        data.get('sabor_personalizado'),
        pedido_id
    )
    try:
        conn = get_conn_normales()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al actualizar pastel normal ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def eliminar_normal_db(pedido_id: int) -> bool:
    """Elimina un pastel normal por ID."""
    try:
        conn = get_conn_normales()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM PastelesNormales WHERE id = ?", (pedido_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al eliminar pastel normal ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def obtener_normal_por_id_db(pedido_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene los datos de un pastel normal para editar."""
    try:
        conn = get_conn_normales()
        cursor = conn.cursor()
        query = "SELECT id, sabor, tamano, cantidad, precio, sucursal, fecha, detalles, sabor_personalizado FROM PastelesNormales WHERE id = ?"
        cursor.execute(query, (pedido_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            'id': row[0], 'sabor': row[1], 'tamano': row[2], 'cantidad': row[3],
            'precio': float(row[4]), 'sucursal': row[5], 'fecha': row[6].isoformat(),
            'detalles': row[7], 'sabor_personalizado': row[8]
        }
    except Exception as e:
        logger.error(f"Error al obtener normal por ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

# CRUD PEDIDOS CLIENTES

def registrar_pedido_cliente_db(data: Dict[str, Any]) -> bool:
    """Registra un nuevo pedido de cliente."""
    query = """
        INSERT INTO PastelesClientes 
        (color, sabor, tamano, cantidad, precio, sucursal, fecha, 
         dedicatoria, detalles, sabor_personalizado, foto_path, fecha_entrega)
        VALUES (?, ?, ?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, ?)
    """
    params = (
        data.get('color'), data.get('sabor'), data.get('tamano'), data.get('cantidad'),
        data.get('precio'), data.get('sucursal'),
        data.get('dedicatoria'), data.get('detalles'), data.get('sabor_personalizado'),
        data.get('foto_path'), data.get('fecha_entrega')
    )
    try:
        conn = get_conn_clientes()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al registrar pedido cliente: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def actualizar_pedido_cliente_db(pedido_id: int, data: Dict[str, Any]) -> bool:
    """Actualiza un pedido de cliente existente."""
    query = """
        UPDATE PastelesClientes SET
            color = ?, sabor = ?, tamano = ?, cantidad = ?, precio = ?, sucursal = ?,
            dedicatoria = ?, detalles = ?, sabor_personalizado = ?, 
            foto_path = ?, fecha_entrega = ?
        WHERE id = ?
    """
    params = (
        data.get('color'), data.get('sabor'), data.get('tamano'), data.get('cantidad'),
        data.get('precio'), data.get('sucursal'),
        data.get('dedicatoria'), data.get('detalles'), data.get('sabor_personalizado'),
        data.get('foto_path'), data.get('fecha_entrega'),
        pedido_id
    )
    try:
        conn = get_conn_clientes()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al actualizar pedido cliente ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def eliminar_cliente_db(pedido_id: int) -> bool:
    """Elimina un pedido de cliente por ID."""
    try:
        conn = get_conn_clientes()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM PastelesClientes WHERE id = ?", (pedido_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al eliminar cliente ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

def obtener_cliente_por_id_db(pedido_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene los datos de un pedido de cliente para editar."""
    try:
        conn = get_conn_clientes()
        cursor = conn.cursor()
        query = """
            SELECT id, color, sabor, tamano, cantidad, precio, total, sucursal, 
                   fecha, foto_path, dedicatoria, detalles, fecha_entrega, sabor_personalizado
            FROM PastelesClientes WHERE id = ?
        """
        cursor.execute(query, (pedido_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            'id': row[0], 'color': row[1], 'sabor': row[2], 'tamano': row[3],
            'cantidad': row[4], 'precio': float(row[5]), 'total': float(row[6]),
            'sucursal': row[7], 'fecha': row[8].isoformat(), 'foto_path': row[9],
            'dedicatoria': row[10], 'detalles': row[11],
            'fecha_entrega': row[12].isoformat() if row[12] else None,
            'sabor_personalizado': row[13]
        }
    except Exception as e:
        logger.error(f"Error al obtener cliente por ID {pedido_id}: {e}", exc_info=True)
        raise Exception(f"Error de base de datos: {e}")

# PARTE 4: DatabaseManager

class DatabaseManager:
    """Gestor principal de operaciones de base de datos para la API y la web"""

    def _ejecutar_query(self, conn_func, query, params=(), commit=False, fetchone=False, fetchall=False):
        """Método helper para ejecutar consultas de forma segura"""
        try:
            conn = conn_func()
            cursor = conn.cursor()
            cursor.execute(query, params)

            resultado = None
            if fetchone:
                resultado = cursor.fetchone()
            if fetchall:
                resultado = cursor.fetchall()

            if commit:
                conn.commit()

            conn.close()
            return resultado
        except Exception as e:
            logger.error(f"Error de DB en query ({query[:50]}...): {e}", exc_info=True)
            raise Exception(f"Error de base de datos: {e}")

    # ===========================
    #        PRECIOS
    # ===========================
    def obtener_precios(self) -> List[Dict[str, Any]]:
        """Obtiene la lista completa de precios"""
        resultados = obtener_precio_db()  # Función standalone
        precios = []
        for row in resultados:
            precios.append({
                'id': row[0],
                'sabor': row[1],
                'tamano': row[2],
                'precio': float(row[3])
            })
        return precios

    def actualizar_precios(self, lista_precios: List[Dict[str, Any]]) -> bool:
        """Actualiza precios masivamente"""
        return actualizar_precios_db(lista_precios)

    # ===========================
    #     PASTELES NORMALES
    # ===========================
    def registrar_pastel_normal(self, data: Dict[str, Any]) -> bool:
        """Registra un pastel normal"""
        return registrar_pastel_normal_db(data)

    def obtener_pasteles_normales(self, fecha_inicio: str = None, fecha_fin: str = None, sucursal: str = None) -> List[Dict[str, Any]]:
        query = "SELECT id, sabor, tamano, precio, cantidad, sucursal, fecha, detalles, sabor_personalizado FROM PastelesNormales WHERE 1=1"
        params = []

        if fecha_inicio and not fecha_fin:
            fecha_fin = fecha_inicio

        if fecha_inicio and fecha_fin:
            query += " AND CAST(fecha AS DATE) BETWEEN ? AND ?"
            params.extend([fecha_inicio, fecha_fin])

        if not fecha_inicio:
            query += " AND CAST(fecha AS DATE) = CAST(GETDATE() AS DATE)"

        if sucursal and sucursal.lower() != "todas":
            query += " AND sucursal = ?"
            params.append(sucursal)

        query += " ORDER BY fecha DESC"

        resultados = self._ejecutar_query(get_conn_normales, query, tuple(params), fetchall=True)

        pasteles = []
        for row in resultados:
            pasteles.append({
                'id': row[0],
                'sabor': row[1],
                'tamano': row[2],
                'precio': float(row[3]),
                'cantidad': row[4],
                'sucursal': row[5],
                'fecha': row[6].isoformat(),
                'detalles': row[7],
                'sabor_personalizado': row[8]
            })
        return pasteles

    def eliminar_pastel_normal(self, pastel_id: int) -> bool:
        """Elimina un pastel normal"""
        return eliminar_normal_db(pastel_id)

    # ===========================
    #     PEDIDOS CLIENTES
    # ===========================
    def registrar_pedido_cliente(self, data: Dict[str, Any]) -> bool:
        """Registra un pedido de cliente"""
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

        if sucursal and sucursal.lower() != "todas":
            query += " AND sucursal = ?"
            params.append(sucursal)

        query += " ORDER BY fecha DESC"

        resultados = self._ejecutar_query(get_conn_clientes, query, tuple(params), fetchall=True)

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
                'fecha': row[8].isoformat(),
                'foto_path': row[9],
                'dedicatoria': row[10],
                'detalles': row[11],
                'fecha_entrega': row[12].isoformat() if row[12] else None,
                'sabor_personalizado': row[13]
            })
        return pedidos

    def eliminar_pedido_cliente(self, pedido_id: int) -> bool:
        """Elimina un pedido de cliente"""
        return eliminar_cliente_db(pedido_id)

    # ===========================
    #       ESTADÍSTICAS
    # ===========================
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
