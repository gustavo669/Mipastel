import sys
import os
import socket
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, date
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
import logging

from auth import (
    verificar_credenciales,
    crear_respuesta_con_sesion,
    cerrar_sesion,
    verificar_sesion
)
from database import get_conn_normales, get_conn_clientes

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.absolute()
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"
TEMPLATES_DIR = BASE_DIR / "templates"
REPORTS_DIR = BASE_DIR / "pdf_reports"

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

try:
    from routers import normales, clientes, admin
    from config import (
        SABORES_NORMALES, SABORES_CLIENTES,
        TAMANOS_NORMALES, TAMANOS_CLIENTES, SUCURSALES
    )
except ImportError as e:
    print(f"Advertencia de Importación: {e}")
    from fastapi import APIRouter
    normales = clientes = admin = APIRouter()
    SABORES_NORMALES = SABORES_CLIENTES = ["Error Carga"]
    TAMANOS_NORMALES = TAMANOS_CLIENTES = ["Error Carga"]
    SUCURSALES = ["Error Carga"]


cell_style = ParagraphStyle(
    'Cell',
    fontSize=9,
    leading=10,
    alignment=TA_LEFT,
    spaceAfter=2,
    spaceBefore=2,
    wordWrap='CJK'
)


def generar_pdf_normales_pivot_por_tamano(normales_rows, sucursales_maestra):
    """Genera tabla pivot de pasteles normales por tamaño y sabor."""
    sucursales = sorted(list(set(sucursales_maestra)))

    filas_keys = sorted({
        f"{r[0]} - {r[1]}" for r in normales_rows
        if r[0] and r[1] and r[1].lower() != "media plancha"
    })

    tabla = {k: {s: 0 for s in sucursales} for k in filas_keys}
    totales_columna = {s: 0 for s in sucursales}
    total_general = 0

    for r in normales_rows:
        sabor, tamano, precio, cantidad, sucursal_row, fecha = r
        if not sabor or not tamano or tamano.lower() == "media plancha":
            continue

        key = f"{sabor} - {tamano}"
        if key in tabla and sucursal_row in tabla[key]:
            tabla[key][sucursal_row] += (cantidad or 0)

    encabezado = ["Sabor - Tamaño"] + sucursales + ["Total"]
    data = [encabezado]

    for key in filas_keys:
        fila = [Paragraph(key, cell_style)]
        total_fila = 0
        for s in sucursales:
            c = tabla[key].get(s, 0)
            fila.append(Paragraph(str(c), cell_style))
            total_fila += c
            totales_columna[s] += c
            total_general += c
        fila.append(Paragraph(str(total_fila), cell_style))
        data.append(fila)

    fila_totales = ["TOTAL GENERAL"] + [str(totales_columna[s]) for s in sucursales] + [str(total_general)]
    data.append(fila_totales)

    ancho_total = 10.5 * inch
    ancho_col = ancho_total / (len(sucursales) + 2)
    col_widths = [ancho_col] * (len(sucursales) + 2)

    t = Table(data, repeatRows=1, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#44475a')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
    ]))

    nota = "Nota: Esta tabla excluye 'Media Plancha' y solo incluye combinaciones válidas de sabor y tamaño."
    return t, nota


def generar_pdf_normales_pivot_por_sabor(normales_rows, sucursales_maestra):
    """Genera tabla pivot de pasteles normales por sabor (totales)."""
    sucursales = sorted(list(set(sucursales_maestra)))

    filas_keys = sorted({r[0] for r in normales_rows if r[0]})

    tabla = {k: {s: 0 for s in sucursales} for k in filas_keys}
    totales_columna = {s: 0 for s in sucursales}
    total_general = 0

    for r in normales_rows:
        sabor, tamano, precio, cantidad, sucursal_row, fecha = r
        if not sabor:
            continue

        if sabor in tabla and sucursal_row in tabla[sabor]:
            tabla[sabor][sucursal_row] += (cantidad or 0)

    encabezado = ["Sabor (Total)"] + sucursales + ["Total"]
    data = [encabezado]

    for key in filas_keys:
        fila = [Paragraph(key, cell_style)]
        total_fila = 0
        for s in sucursales:
            c = tabla[key].get(s, 0)
            fila.append(Paragraph(str(c), cell_style))
            total_fila += c
            totales_columna[s] += c
            total_general += c
        fila.append(Paragraph(str(total_fila), cell_style))
        data.append(fila)

    fila_totales = ["TOTAL GENERAL"] + [str(totales_columna[s]) for s in sucursales] + [str(total_general)]
    data.append(fila_totales)

    ancho_total = 10.5 * inch
    ancho_col = ancho_total / (len(sucursales) + 2)
    col_widths = [ancho_col] * (len(sucursales) + 2)

    t = Table(data, repeatRows=1, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff79c6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#44475a')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
    ]))
    return t


def generar_pdf_clientes_detalle(clientes_rows):
    """Genera tabla detallada de pedidos de clientes."""
    encabezado = ["Sabor", "ID Pedido", "Cantidad", "Sucursal", "Detalles", "FotoID", "Dedicatoria", "Color"]
    data = [encabezado]

    for r in clientes_rows:
        id_pedido, color, sabor, tamano, cantidad, precio, total, sucursal, fecha, foto_path, dedicatoria, detalles = r
        foto_id = f"F-{id_pedido}" if foto_path else ""

        fila = [
            Paragraph(f"{sabor} ({tamano})", cell_style),
            str(id_pedido),
            str(cantidad),
            Paragraph(sucursal or "", cell_style),
            Paragraph(detalles or "", cell_style),
            foto_id,
            Paragraph(dedicatoria or "", cell_style),
            Paragraph(color or "", cell_style)
        ]
        data.append(fila)

    ancho_total = 10.5 * inch
    col_widths = [ancho_total / len(encabezado)] * len(encabezado)

    t = Table(data, repeatRows=1, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (2, -1), 'CENTER'),
    ]))
    return t


def generar_reporte_completo(target_date, sucursal=None, output_path=None):
    """
    Genera un reporte completo en PDF con:
    - Resumen de pasteles normales por tamaño
    - Resumen de pasteles normales por sabor
    - Detalle de pedidos de clientes
    """
    hoy = target_date
    inicio = datetime.combine(hoy, datetime.min.time())
    fin = datetime.combine(hoy, datetime.max.time())

    conn1 = get_conn_normales()
    cur1 = conn1.cursor()

    query_normales = """
        SELECT sabor, tamano, precio, cantidad, sucursal, fecha
        FROM PastelesNormales
        WHERE fecha BETWEEN ? AND ?
    """
    params_normales = [inicio, fin]

    if sucursal:
        query_normales += " AND sucursal = ?"
        params_normales.append(sucursal)

    cur1.execute(query_normales, tuple(params_normales))
    normales = cur1.fetchall()
    conn1.close()

    conn2 = get_conn_clientes()
    cur2 = conn2.cursor()

    query_clientes = """
        SELECT id, color, sabor, tamano, cantidad, precio, total, sucursal, fecha, foto_path, dedicatoria, detalles
        FROM PastelesClientes
        WHERE fecha BETWEEN ? AND ?
    """
    params_clientes = [inicio, fin]

    if sucursal:
        query_clientes += " AND sucursal = ?"
        params_clientes.append(sucursal)

    cur2.execute(query_clientes, tuple(params_clientes))
    clientes = cur2.fetchall()
    conn2.close()

    file_date = hoy.strftime("%Y-%m-%d")
    if output_path:
        filename = str(output_path)
    else:
        nombre_base = f"Reporte_MiPastel_{file_date}"
        if sucursal:
            nombre_base += f"_{sucursal}"
        nombre_base += ".pdf"
        filename = str(REPORTS_DIR / nombre_base)

    doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, alignment=TA_CENTER)

    elements = []
    elements.append(Paragraph("Mi Pastel - Reporte del Día", titulo_style))
    elements.append(Paragraph(f"Fecha: {hoy.strftime('%d/%m/%Y')}", styles['Normal']))
    if sucursal:
        elements.append(Paragraph(f"Sucursal: {sucursal}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Resumen por tamaño
    elements.append(Paragraph("Resumen - Pasteles Normales (por Tamaño)", styles['Heading2']))
    pivot_table_tamano, pivot_note = generar_pdf_normales_pivot_por_tamano(normales, SUCURSALES)
    elements.append(pivot_table_tamano)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(pivot_note, styles['Normal']))
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Resumen - Pasteles Normales (Total por Sabor)", styles['Heading2']))
    pivot_table_sabor = generar_pdf_normales_pivot_por_sabor(normales, SUCURSALES)
    elements.append(pivot_table_sabor)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Detalle - Pedidos de Clientes", styles['Heading2']))
    clientes_table = generar_pdf_clientes_detalle(clientes)
    elements.append(clientes_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("_" * 80, styles['Normal']))
    elements.append(Paragraph(
        f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        styles['Normal']
    ))

    try:
        doc.build(elements)
        logger.info(f"✓ Reporte PDF generado: {filename}")
        return filename
    except Exception as e:
        logger.error(f"✗ Error al construir PDF: {e}", exc_info=True)
        raise Exception(f"Error al construir PDF: {e}")


def generar_pdf_dia(target_date=None, sucursal=None, output_path=None):
    """Genera un PDF con pedidos del día especificado (o hoy si target_date es None)."""
    fecha_obj = target_date or date.today()
    return generar_reporte_completo(fecha_obj, sucursal, output_path)


def get_local_ip():
    """Obtiene la IP real de la máquina en la red WiFi"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Mensaje al iniciar la API"""
    local_ip = get_local_ip()
    print(f"MI PASTEL - Sistema de Gestión")
    print(f"Servidor iniciado en: http://{local_ip}:5000")
    print(f"Acceso local: http://127.0.0.1:5000")
    print(f"Acceso desde red WiFi: http://{local_ip}:5000")
    yield

app = FastAPI(
    title="Mi Pastel - Sistema de Gestión",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.include_router(normales.router)
app.include_router(clientes.router)
app.include_router(admin.router)


@app.get("/login", response_class=HTMLResponse)
async def mostrar_login(request: Request, error: str = None):
    """Muestra el formulario de login"""
    username = verificar_sesion(request)
    if username:
        return RedirectResponse(url="/admin", status_code=302)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error
    })


@app.post("/login")
async def procesar_login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
):
    """Procesa el formulario de login"""
    if verificar_credenciales(username, password):
        response = RedirectResponse(url="/admin", status_code=302)
        crear_respuesta_con_sesion(response, username)
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Usuario o contraseña incorrectos"
        })


@app.get("/logout")
async def cerrar_sesion_usuario(request: Request):
    """Cierra la sesión del usuario"""
    response = RedirectResponse(url="/login", status_code=302)
    cerrar_sesion(response)
    return response



@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Pantalla principal de pedidos - PÚBLICA"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "sabores_normales": SABORES_NORMALES,
        "sabores_clientes": SABORES_CLIENTES,
        "tamanos_normales": TAMANOS_NORMALES,
        "tamanos_clientes": TAMANOS_CLIENTES,
        "sucursales": SUCURSALES
    })


@app.get("/api/obtener-precio")
async def api_obtener_precio(sabor: str, tamano: str):
    """API para cálculo de precios - PÚBLICA"""
    try:
        if sabor.lower() == "otro":
            return {"precio": 0, "encontrado": False, "detalle": "Precio manual requerido"}

        from database import obtener_precio_db
        precio = obtener_precio_db(sabor, tamano)

        if precio and precio > 0:
            return {"precio": precio, "encontrado": True}
        else:
            return {"precio": 0, "encontrado": False, "detalle": "No registrado"}
    except Exception as e:
        print(f"Error DB: {e}")
        return {"precio": 0, "encontrado": False, "error": str(e)}


@app.get("/reportes/pdf")
async def generar_reporte_pdf(request: Request, fecha: str, sucursal: str = None):
    """Genera PDF con fecha y sucursal específicas"""
    try:
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"error": "Formato de fecha inválido. Use YYYY-MM-DD"}
            )

        nombre_archivo = generar_pdf_dia(target_date=fecha_obj, sucursal=sucursal if sucursal else None)

        if not os.path.exists(nombre_archivo):
            return JSONResponse(
                status_code=500,
                content={"error": "No se pudo generar el PDF"}
            )

        nombre_descarga = f'Reporte_MiPastel_{fecha}'
        if sucursal:
            nombre_descarga += f'_{sucursal}'
        nombre_descarga += '.pdf'

        return FileResponse(
            path=nombre_archivo,
            media_type='application/pdf',
            filename=nombre_descarga
        )

    except Exception as e:
        logger.error(f"Error al generar PDF: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al generar el reporte: {str(e)}"}
        )

@app.get("/reportes/dia/pdf")
async def generar_pdf_del_dia(request: Request):
    """Genera y descarga el PDF del día actual (ruta rápida)"""
    try:
        fecha_hoy = date.today()
        nombre_archivo = generar_pdf_dia(target_date=fecha_hoy)

        if not os.path.exists(nombre_archivo):
            return JSONResponse(
                status_code=500,
                content={"error": "No se pudo generar el PDF"}
            )

        return FileResponse(
            path=nombre_archivo,
            media_type='application/pdf',
            filename=f'Reporte_MiPastel_{fecha_hoy.strftime("%Y-%m-%d")}.pdf'
        )

    except Exception as e:
        logger.error(f"Error al generar PDF: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al generar el reporte: {str(e)}"}
        )

@app.get("/health")
async def health_check():
    """Health check para verificar conexión"""
    return JSONResponse({
        "status": "ok",
        "ip_servidor": get_local_ip(),
        "mensaje": "Conexión exitosa con el servidor de pedidos"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)