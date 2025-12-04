import pytest
from api.database import DatabaseManager

db = DatabaseManager()

def test_obtener_precios():
    precios = db.obtener_precios()
    assert isinstance(precios, list)

def test_obtener_precio_por_sabor_tamano():
    precio = db.obtener_precio_por_sabor_tamano("Fresas", "Mediano")
    assert isinstance(precio, (int, float))
    assert precio >= 0

def test_obtener_pasteles_normales():
    pasteles = db.obtener_pasteles_normales()
    assert isinstance(pasteles, list)

def test_obtener_pedidos_clientes():
    pedidos = db.obtener_pedidos_clientes()
    assert isinstance(pedidos, list)

def test_obtener_estadisticas():
    stats = db.obtener_estadisticas()
    assert isinstance(stats, dict)
    assert 'normales_count' in stats
    assert 'clientes_count' in stats
