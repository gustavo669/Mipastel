from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional

class ValidarPedidoNormal(BaseModel):
    sabor: str = Field(..., min_length=2, max_length=100)
    tamano: str = Field(..., min_length=2, max_length=50)
    cantidad: int = Field(..., gt=0)
    precio: float = Field(..., gt=0)
    sucursal: str = Field(..., min_length=2)
    fecha_entrega: Optional[str] = None
    detalles: Optional[str] = Field(None, max_length=500)
    sabor_personalizado: Optional[str] = Field(None, max_length=100)
    
    @field_validator('sabor', 'tamano', 'sucursal', 'detalles', 'sabor_personalizado')
    @classmethod
    def sanitizar_input(cls, v):
        if v is None:
            return v
        caracteres_peligrosos = ['<', '>', '"', "'", ';', '--', '/*', '*/']
        for char in caracteres_peligrosos:
            if char in str(v):
                raise ValueError(f'Caracteres no permitidos: {char}')
        return str(v).strip()

class ValidarPedidoCliente(ValidarPedidoNormal):
    color: Optional[str] = Field(None, max_length=50)
    dedicatoria: Optional[str] = Field(None, max_length=500)
    foto_path: Optional[str] = Field(None, max_length=255)
    
    @field_validator('color', 'dedicatoria')
    @classmethod
    def sanitizar_cliente_input(cls, v):
        if v is None:
            return v
        caracteres_peligrosos = ['<', '>', '"', "'", ';', '--', '/*', '*/']
        for char in caracteres_peligrosos:
            if char in str(v):
                raise ValueError(f'Caracteres no permitidos: {char}')
        return str(v).strip()
