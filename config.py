print("Cargando configuración maestra (config.py)...")


SABORES_NORMALES = [
    "Fresas", "Frutas", "Chocolate", "Selva negra", "Oreo", "Chocofresa",
    "Tres Leches", "Tres leches con Arándanos", "Fiesta", "Ambiente", "Zanahoria", "Otro"
]

SABORES_CLIENTES = SABORES_NORMALES


TAMANOS_NORMALES = [
    "Mini", "Pequeño", "Mediano", "Grande", "Extra grande", "Media plancha"
]

TAMANOS_CLIENTES = TAMANOS_NORMALES + ["Boda", "Quince Años"]


SUCURSALES = [
    "Jutiapa 1", "Jutiapa 2", "Jutiapa 3", "Progreso", "Quesada", "Acatempa",
    "Yupiltepeque", "Atescatempa", "Adelanto", "Jeréz", "Comapa", "Carina"
]

SUCURSALES_FILTRO = ["Todas"] + SUCURSALES

TAMANOS = TAMANOS_NORMALES
