from api.database import (
    obtener_precio_db,
    actualizar_precios_db,
    registrar_pastel_normal_db,
    actualizar_pastel_normal_db,
    eliminar_normal_db,
    obtener_normal_por_id_db,
    registrar_pedido_cliente_db,
    actualizar_pedido_cliente_db,
    eliminar_cliente_db,
    obtener_cliente_por_id_db,
    DatabaseManager
)

from api.database import (
    obtener_precio_db,
    actualizar_precios_db,
    registrar_pastel_normal_db,
    actualizar_pastel_normal_db,
    eliminar_normal_db,
    obtener_normal_por_id_db,
    registrar_pedido_cliente_db,
    actualizar_pedido_cliente_db,
    eliminar_cliente_db,
    obtener_cliente_por_id_db,
    DatabaseManager
)
from config.database import db_pool_normales, db_pool_clientes

def get_conn_normales():
    """Backwards compatibility wrapper - DO NOT USE conn.close() with this"""
    class ConnectionWrapper:
        def __init__(self, pool):
            self.pool = pool
            self.conn = None
            self.context = None
            self._entered = False

        def __enter__(self):
            if not self._entered:
                self.context = self.pool.get_connection()
                self.conn = self.context.__enter__()
                self._entered = True
            return self.conn

        def __exit__(self, *args):
            if self.context and self._entered:
                self.context.__exit__(*args)
                self.context = None
                self.conn = None
                self._entered = False

        def cursor(self):
            if not self.conn:
                self.__enter__()
            return self.conn.cursor()

        def close(self):
            """Close the connection properly"""
            if self._entered:
                self.__exit__(None, None, None)

    wrapper = ConnectionWrapper(db_pool_normales)
    wrapper.__enter__()
    return wrapper

def get_conn_clientes():
    """Backwards compatibility wrapper - DO NOT USE conn.close() with this"""
    class ConnectionWrapper:
        def __init__(self, pool):
            self.pool = pool
            self.conn = None
            self.context = None
            self._entered = False

        def __enter__(self):
            if not self._entered:
                self.context = self.pool.get_connection()
                self.conn = self.context.__enter__()
                self._entered = True
            return self.conn

        def __exit__(self, *args):
            if self.context and self._entered:
                self.context.__exit__(*args)
                self.context = None
                self.conn = None
                self._entered = False

        def cursor(self):
            if not self.conn:
                self.__enter__()
            return self.conn.cursor()

        def close(self):
            """Close the connection properly"""
            if self._entered:
                self.__exit__(None, None, None)

    wrapper = ConnectionWrapper(db_pool_clientes)
    wrapper.__enter__()
    return wrapper

__all__ = [
    'obtener_precio_db',
    'actualizar_precios_db',
    'registrar_pastel_normal_db',
    'actualizar_pastel_normal_db',
    'eliminar_normal_db',
    'obtener_normal_por_id_db',
    'registrar_pedido_cliente_db',
    'actualizar_pedido_cliente_db',
    'eliminar_cliente_db',
    'obtener_cliente_por_id_db',
    'DatabaseManager',
    'get_conn_normales',
    'get_conn_clientes'
]