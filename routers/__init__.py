# Este archivo hace que la carpeta routers sea un paquete Python

# Importar todos los routers para que sean accesibles
from . import normales
from . import clientes
from . import admin
from . import pedidos_api

__all__ = ['normales', 'clientes', 'admin', 'pedidos_api']