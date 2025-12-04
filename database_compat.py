from config.database import db_pool_normales, db_pool_clientes

def get_conn_normales():
    """Wrapper for backwards compatibility - returns connection from pool"""
    return db_pool_normales.get_connection().__enter__()

def get_conn_clientes():
    """Wrapper for backwards compatibility - returns connection from pool"""
    return db_pool_clientes.get_connection().__enter__()
