import pyodbc
from contextlib import contextmanager
from typing import Generator
import logging
from .settings import settings

logger = logging.getLogger(__name__)

class DatabasePool:
    def __init__(self, server: str, database: str, driver: str):
        self.server = server
        self.database = database
        self.driver = driver
        self.connection_string = (
            f'DRIVER={{{driver}}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'Trusted_Connection=yes;'
        )
    
    @contextmanager
    def get_connection(self) -> Generator:
        conn = None
        try:
            conn = pyodbc.connect(self.connection_string)
            conn.autocommit = False
            yield conn
        except pyodbc.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Error de conexión a {self.database}: {e}")
            raise
        finally:
            if conn:
                conn.close()

db_pool_normales = DatabasePool(
    settings.DB_SERVER, 
    settings.DB_NAME_NORMALES,
    settings.DB_DRIVER
)

db_pool_clientes = DatabasePool(
    settings.DB_SERVER,
    settings.DB_NAME_CLIENTES,
    settings.DB_DRIVER
)
