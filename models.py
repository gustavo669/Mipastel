from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime


class PedidoNormalBase(BaseModel):
    sabor: str = Field(..., min_length=2, max_length=100)
    tamano: str = Field(..., min_length=2, max_length=50)
    cantidad: int = Field(..., gt=0)
    precio: float = Field(..., gt=0)
    sucursal: str = Field(..., min_length=2, max_length=100)
    fecha_entrega: Optional[str] = None
    detalles: Optional[str] = Field(None, max_length=500)
    sabor_personalizado: Optional[str] = Field(None, max_length=100)

    @validator('sabor', 'tamano', 'sucursal', 'sabor_personalizado')
    def validar_caracteres(cls, v):
        if v and any(char in str(v) for char in ['<', '>', '"', "'", ';', '--']):
            raise ValueError('Caracteres no permitidos')
        return v

    @validator('fecha_entrega')
    def validar_fecha_entrega(cls, v):
        if v:
            try:
                fecha_obj = datetime.strptime(v, '%Y-%m-%d').date()
                if fecha_obj < date.today():
                    raise ValueError('La fecha de entrega no puede ser anterior a hoy')
            except ValueError as e:
                raise ValueError(f'Formato de fecha inválido: {str(e)}')
        return v


class PedidoClienteBase(BaseModel):
    sabor: str = Field(..., min_length=2, max_length=100)
    tamano: str = Field(..., min_length=2, max_length=50)
    cantidad: int = Field(..., gt=0)
    precio: float = Field(..., gt=0)
    sucursal: str = Field(..., min_length=2, max_length=100)
    fecha_entrega: Optional[str] = None
    color: Optional[str] = Field(None, max_length=50)
    dedicatoria: Optional[str] = Field(None, max_length=500)
    detalles: Optional[str] = Field(None, max_length=500)
    sabor_personalizado: Optional[str] = Field(None, max_length=100)
    foto_path: Optional[str] = None

    @validator('sabor', 'tamano', 'sucursal', 'color', 'sabor_personalizado')
    def validar_caracteres(cls, v):
        if v and any(char in str(v) for char in ['<', '>', '"', "'", ';', '--']):
            raise ValueError('Caracteres no permitidos')
        return v

    @validator('fecha_entrega')
    def validar_fecha_entrega(cls, v):
        if v:
            try:
                fecha_obj = datetime.strptime(v, '%Y-%m-%d').date()
                if fecha_obj < date.today():
                    raise ValueError('La fecha de entrega no puede ser anterior a hoy')
            except ValueError as e:
                raise ValueError(f'Formato de fecha inválido: {str(e)}')
        return v


class PedidoNormalUpdate(BaseModel):
    sabor: Optional[str] = Field(None, min_length=2, max_length=100)
    tamano: Optional[str] = Field(None, min_length=2, max_length=50)
    cantidad: Optional[int] = Field(None, gt=0)
    precio: Optional[float] = Field(None, gt=0)
    sucursal: Optional[str] = Field(None, min_length=2, max_length=100)
    fecha_entrega: Optional[str] = None
    detalles: Optional[str] = Field(None, max_length=500)
    sabor_personalizado: Optional[str] = Field(None, max_length=100)


class PedidoClienteUpdate(BaseModel):
    sabor: Optional[str] = Field(None, min_length=2, max_length=100)
    tamano: Optional[str] = Field(None, min_length=2, max_length=50)
    cantidad: Optional[int] = Field(None, gt=0)
    precio: Optional[float] = Field(None, gt=0)
    sucursal: Optional[str] = Field(None, min_length=2, max_length=100)
    fecha_entrega: Optional[str] = None
    color: Optional[str] = Field(None, max_length=50)
    dedicatoria: Optional[str] = Field(None, max_length=500)
    detalles: Optional[str] = Field(None, max_length=500)
    sabor_personalizado: Optional[str] = Field(None, max_length=100)


class RangoFechas(BaseModel):
    fecha_inicio: str
    fecha_fin: str
    sucursal: Optional[str] = None

    @validator('fecha_inicio', 'fecha_fin')
    def validar_formato_fecha(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Formato de fecha debe ser YYYY-MM-DD')
        return v

    @validator('fecha_fin')
    def validar_rango(cls, v, values):
        if 'fecha_inicio' in values:
            inicio = datetime.strptime(values['fecha_inicio'], '%Y-%m-%d')
            fin = datetime.strptime(v, '%Y-%m-%d')
            if fin < inicio:
                raise ValueError('La fecha fin debe ser posterior a la fecha inicio')
        return v