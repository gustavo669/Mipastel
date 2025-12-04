from typing import Dict, Any

class PastelNormal:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.sabor = kwargs.get('sabor')
        self.tamano = kwargs.get('tamano')
        self.cantidad = kwargs.get('cantidad')
        self.precio = kwargs.get('precio')
        self.sucursal = kwargs.get('sucursal')
        self.fecha = kwargs.get('fecha')
        self.fecha_entrega = kwargs.get('fecha_entrega')
        self.detalles = kwargs.get('detalles')
        self.sabor_personalizado = kwargs.get('sabor_personalizado')

class PedidoCliente:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.color = kwargs.get('color')
        self.sabor = kwargs.get('sabor')
        self.tamano = kwargs.get('tamano')
        self.cantidad = kwargs.get('cantidad')
        self.precio = kwargs.get('precio')
        self.total = kwargs.get('total')
        self.sucursal = kwargs.get('sucursal')
        self.fecha = kwargs.get('fecha')
        self.foto_path = kwargs.get('foto_path')
        self.dedicatoria = kwargs.get('dedicatoria')
        self.detalles = kwargs.get('detalles')
        self.fecha_entrega = kwargs.get('fecha_entrega')
        self.sabor_personalizado = kwargs.get('sabor_personalizado')
