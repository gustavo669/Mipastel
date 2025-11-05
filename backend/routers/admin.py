from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from database import get_conn_normales, get_conn_clientes
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io
import os

router = APIRouter(prefix="/admin", tags=["Administrador"])

templates = Jinja2Templates(directory="templates")

# 📊 Vista general en el navegador (sin PySide6)
@router.get("/", response_class=HTMLResponse)
async def vista_admin(request: Request):
    conn1 = get_conn_normales()
    cur1 = conn1.cursor()
    cur1.execute("SELECT id_pastel, sabor, tamaño, precio, cantidad, sucursal, fecha_pedido FROM PastelesNormales ORDER BY fecha_pedido DESC")
    normales = cur1.fetchall()
    conn1.close()

    conn2 = get_conn_clientes()
    cur2 = conn2.cursor()
    cur2.execute("SELECT id_pedido_cliente, nombre_cliente, sabor, tamaño, cantidad, total, sucursal, fecha_pedido FROM PastelesClientes ORDER BY fecha_pedido DESC")
    clientes = cur2.fetchall()
    conn2.close()

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "normales": normales,
        "clientes": clientes
    })

# 🧾 Generar reporte PDF del día
@router.get("/reporte/pdf", response_class=FileResponse)
async def generar_pdf_dia():
    hoy = date.today()
    inicio = datetime.combine(hoy, datetime.min.time())
    fin = datetime.combine(hoy, datetime.max.time())

    conn1 = get_conn_normales()
    cur1 = conn1.cursor()
    cur1.execute("SELECT sabor, tamaño, precio, cantidad, sucursal, fecha_pedido FROM PastelesNormales WHERE fecha_pedido BETWEEN ? AND ?", (inicio, fin))
    normales = cur1.fetchall()
    conn1.close()

    conn2 = get_conn_clientes()
    cur2 = conn2.cursor()
    cur2.execute("SELECT nombre_cliente, sabor, tamaño, cantidad, total, sucursal, fecha_pedido FROM PastelesClientes WHERE fecha_pedido BETWEEN ? AND ?", (inicio, fin))
    clientes = cur2.fetchall()
    conn2.close()

    # 📄 Crear PDF
    ruta_pdf = f"Lista_dia_{hoy}.pdf"
    doc = SimpleDocTemplate(ruta_pdf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph(f"Mi Pastel — Lista del día ({hoy})", styles['Heading1']), Spacer(1, 12)]

    # ---- Pasteles normales ----
    elements.append(Paragraph("Pasteles Normales", styles['Heading2']))
    if normales:
        data = [["Sabor","Tamaño","Precio","Cantidad","Sucursal","Fecha"]] + [[*r] for r in normales]
        t = Table(data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
            ('GRID',(0,0),(-1,-1),0.5,colors.grey)
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No hay pedidos normales hoy.", styles['Normal']))

    elements.append(Spacer(1, 12))

    # ---- Pedidos de clientes ----
    elements.append(Paragraph("Pedidos de Clientes", styles['Heading2']))
    if clientes:
        data2 = [["Cliente","Sabor","Tamaño","Cantidad","Total","Sucursal","Fecha"]] + [[*r] for r in clientes]
        t2 = Table(data2, repeatRows=1)
        t2.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
            ('GRID',(0,0),(-1,-1),0.5,colors.grey)
        ]))
        elements.append(t2)
    else:
        elements.append(Paragraph("No hay pedidos de clientes hoy.", styles['Normal']))

    doc.build(elements)

    return FileResponse(path=ruta_pdf, filename=f"Lista_dia_{hoy}.pdf", media_type="application/pdf")
