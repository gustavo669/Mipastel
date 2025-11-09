from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import pyodbc
import os
from typing import List, Dict, Any

app = FastAPI(title="Mi Pastel - Sistema de Pedidos")

# ===========================
# CONFIGURACIONES DE CONEXIÓN
# ===========================

def get_conn_normales():
    """Conexión a BD MiPastel"""
    return pyodbc.connect(
        "DRIVER={SQL Server};SERVER=localhost;DATABASE=MiPastel;Trusted_Connection=yes;"
    )

def get_conn_clientes():
    """Conexión a BD MiPastel_Clientes"""
    return pyodbc.connect(
        "DRIVER={SQL Server};SERVER=localhost;DATABASE=MiPastel_Clientes;Trusted_Connection=yes;"
    )

# ===========================
# CONFIGURACIÓN FRONTEND
# ===========================
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ===========================
# FUNCIONES AUXILIARES
# ===========================

def obtener_precio_db() -> List[tuple]:
    """Obtiene todos los precios disponibles"""
    conn = get_conn_normales()
    cursor = conn.cursor()
    cursor.execute("SELECT id, sabor, tamano, precio FROM PastelesPrecios")
    data = cursor.fetchall()
    conn.close()
    return data

def obtener_precios() -> List[Dict[str, Any]]:
    resultados = obtener_precio_db()
    precios = []
    for row in resultados:
        precios.append({
            'id': row[0],
            'sabor': row[1],
            'tamano': row[2],
            'precio': float(row[3])
        })
    return precios

def obtener_listas_para_html():
    precios = obtener_precios()
    sabores = sorted(set([p["sabor"] for p in precios]))
    tamanos = sorted(set([p["tamano"] for p in precios]))
    sucursales = ["Central", "Jutiapa", "El Progreso", "Asunción Mita"]
    return sabores, tamanos, sucursales

# ===========================
# RUTAS PRINCIPALES
# ===========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    sabores_normales, tamanos_normales, sucursales = obtener_listas_para_html()
    sabores_clientes, tamanos_clientes, _ = obtener_listas_para_html()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "sabores_normales": sabores_normales,
        "tamanos_normales": tamanos_normales,
        "sabores_clientes": sabores_clientes,
        "tamanos_clientes": tamanos_clientes,
        "sucursales": sucursales
    })

# ===========================
# REGISTRO PASTELES NORMALES
# ===========================

@app.post("/normales/registrar")
async def registrar_normal(
        sabor: str = Form(...),
        sabor_otro: str = Form(None),
        tamano: str = Form(...),
        tamano_otro: str = Form(None),
        cantidad: int = Form(...),
        sucursal: str = Form(...),
        precio_personalizado: float = Form(None)
):
    sabor_final = sabor_otro if sabor == "Otro" and sabor_otro else sabor
    tamano_final = tamano_otro if tamano == "Otro" and tamano_otro else tamano

    conn = get_conn_normales()
    cursor = conn.cursor()

    # Obtener precio base si no es personalizado
    if not precio_personalizado:
        cursor.execute("SELECT precio FROM PastelesPrecios WHERE sabor=? AND tamano=?", (sabor_final, tamano_final))
        row = cursor.fetchone()
        if row:
            precio = float(row[0])
        else:
            precio = 0.0
    else:
        precio = precio_personalizado

    total = precio * cantidad

    cursor.execute("""
        INSERT INTO PastelesNormales (sabor, tamano, cantidad, precio, total, sucursal, sabor_personalizado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (sabor_final, tamano_final, cantidad, precio, total, sucursal, sabor_otro))

    conn.commit()
    conn.close()

    return RedirectResponse("/", status_code=303)

# ===========================
# REGISTRO PASTELES CLIENTES
# ===========================

@app.post("/clientes/registrar")
async def registrar_cliente(
        sabor: str = Form(...),
        sabor_otro: str = Form(None),
        tamano: str = Form(...),
        tamano_otro: str = Form(None),
        cantidad: int = Form(...),
        sucursal: str = Form(...),
        fecha_entrega: str = Form(...),
        color: str = Form(None),
        dedicatoria: str = Form(None),
        detalles: str = Form(None),
        precio_personalizado: float = Form(None),
        foto: UploadFile = File(None)
):
    sabor_final = sabor_otro if sabor == "Otro" and sabor_otro else sabor
    tamano_final = tamano_otro if tamano == "Otro" and tamano_otro else tamano

    # Guardar foto si existe
    foto_path = None
    if foto and foto.filename != "":
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        foto_path = os.path.join(upload_dir, foto.filename)
        with open(foto_path, "wb") as buffer:
            buffer.write(await foto.read())

    conn = get_conn_clientes()
    cursor = conn.cursor()

    # Obtener precio base
    conn_normales = get_conn_normales()
    cursor_norm = conn_normales.cursor()
    if not precio_personalizado:
        cursor_norm.execute("SELECT precio FROM PastelesPrecios WHERE sabor=? AND tamano=?", (sabor_final, tamano_final))
        row = cursor_norm.fetchone()
        if row:
            precio = float(row[0])
        else:
            precio = 0.0
    else:
        precio = precio_personalizado
    conn_normales.close()

    total = precio * cantidad

    cursor.execute("""
        INSERT INTO PastelesClientes (color, sabor, tamano, cantidad, precio, total, sucursal, dedicatoria, detalles, sabor_personalizado, foto_path, fecha_entrega)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (color, sabor_final, tamano_final, cantidad, precio, total, sucursal, dedicatoria, detalles, sabor_otro, foto_path, fecha_entrega))

    conn.commit()
    conn.close()

    return RedirectResponse("/", status_code=303)

# ===========================
# API: OBTENER PRECIO
# ===========================

@app.get("/api/obtener-precio")
async def obtener_precio_api(sabor: str, tamano: str):
    conn = get_conn_normales()
    cursor = conn.cursor()
    cursor.execute("SELECT precio FROM PastelesPrecios WHERE sabor=? AND tamano=?", (sabor, tamano))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"encontrado": True, "precio": float(row[0])}
    else:
        return {"encontrado": False, "detail": f"No se encontró precio para {sabor} {tamano}. Use 'Otro' para precios personalizados."}
