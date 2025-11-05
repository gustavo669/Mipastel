from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from database import get_conn_normales, get_conn_clientes
import io

def generar_pdf_dia():
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
    print(f"✅ PDF generado: {ruta_pdf}")
