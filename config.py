"""
Configuración Maestra - Mi Pastel v3.0
--------------------------------------
Este archivo es la ÚNICA FUENTE DE VERDAD para
las listas maestras del sistema (sabores, tamaños, sucursales).

Todos los demás módulos (app.py, admin_app.py, reportes.py)
deben importar las listas desde aquí.
"""

print("⚙️  Cargando configuración maestra (config.py)...")

# --- SABORES ---
SABORES_NORMALES = [
    "Fresas", "Frutas", "Chocolate", "Selva negra", "Oreo", "Chocofresa",
    "Tres Leches", "Tres leches con Arándanos", "Fiesta", "Ambiente", "Zanahoria", "Otro"
]

SABORES_CLIENTES = SABORES_NORMALES + ["Boda", "Quince Años"]

# --- TAMAÑOS ---
TAMANOS = ["Mini", "Pequeño", "Mediano", "Grande", "Extra grande", "Media plancha"]

# --- SUCURSALES ---
# Lista maestra para reportes y formularios de ingreso
SUCURSALES = [
    "Jutiapa 1", "Jutiapa 2", "Jutiapa 3", "Progreso", "Quesada", "Acatempa",
    "Yupiltepeque", "Atescatempa", "Adelanto", "Jeréz", "Comapa", "Cariña"
]

# Lista para los filtros de la App Admin (incluye "Todas")
SUCURSALES_FILTRO = ["Todas"] + SUCURSALES