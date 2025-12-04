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
            
        def __enter__(self):
            self.context = self.pool.get_connection()
            self.conn = self.context.__enter__()
            return self.conn
            
        def __exit__(self, *args):
            if self.context:
                self.context.__exit__(*args)
        
        def cursor(self):
            if not self.conn:
                self.context = self.pool.get_connection()
                self.conn = self.context.__enter__()
            return self.conn.cursor()
        
        def close(self):
            if self.context:
                self.context.__exit__(None, None, None)
                self.context = None
                self.conn = None
    
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
            
        def __enter__(self):
            self.context = self.pool.get_connection()
            self.conn = self.context.__enter__()
            return self.conn
            
        def __exit__(self, *args):
            if self.context:
                self.context.__exit__(*args)
        
        def cursor(self):
            if not self.conn:
                self.context = self.pool.get_connection()
                self.conn = self.context.__enter__()
            return self.conn.cursor()
        
        def close(self):
            if self.context:
                self.context.__exit__(None, None, None)
                self.context = None
                self.conn = None
    
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