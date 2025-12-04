from .constants import (
    SABORES_NORMALES,
    SABORES_CLIENTES,
    TAMANOS_NORMALES,
    TAMANOS_CLIENTES,
    SUCURSALES,
    SUCURSALES_FILTRO,
    TAMANOS
)

try:
    from .settings import settings
except Exception as e:
    print(f"Warning: Could not import settings: {e}")
    settings = None

__all__ = [
    'SABORES_NORMALES',
    'SABORES_CLIENTES', 
    'TAMANOS_NORMALES',
    'TAMANOS_CLIENTES',
    'SUCURSALES',
    'SUCURSALES_FILTRO',
    'TAMANOS',
    'settings'
]
