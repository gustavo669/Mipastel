# reportes.py
from datetime import datetime, date
from database import get_conn_normales, get_conn_clientes
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def generar_pdf_dia(date=None, sucursal=None, output_path=None):
    """Genera un PDF con pedidos del día especificado (o hoy si date es None).
       Si sucursal se pasa, filtra por sucursal.
    """
    fecha_obj = date or date.today()
    return generar_reporte_completo(fecha_obj, sucursal, output_path)

def generar_pdf_por_sucursal(date, sucursal, output_path=None):
    """Genera PDF por sucursal (wrapper)."""
    return generar_reporte_completo(date, sucursal, output_path)

def generar_reporte_completo(target_date, sucursal=None, output_path=None):
    hoy = target_date
    inicio = datetime.combine(hoy, datetime.min.time())
    fin = datetime.combine(hoy, datetime.max.time())

    # obtener datos
    conn1 = get_conn_normales()
    cur1 = conn1.cursor()
    if sucursal:
        cur1.execute("""
            SELECT sabor, tamaño, precio, cantidad, sucursal, fecha_pedido
            FROM PastelesNormales
            WHERE fecha_pedido BETWEEN ? AND ? AND sucursal = ?
        """, (inicio, fin, sucursal))
    else:
        cur1.execute("""
            SELECT sabor, tamaño, precio, cantidad, sucursal, fecha_pedido
            FROM PastelesNormales
            WHERE fecha_pedido BETWEEN ? AND ?
        """, (inicio, fin))
    normales = cur1.fetchall()
    conn1.close()

    conn2 = get_conn_clientes()
    cur2 = conn2.cursor()
    if sucursal:
        cur2.execute("""
            SELECT id_pedido_cliente, color, sabor, tamaño, cantidad, precio, total, sucursal, fecha_pedido, foto_path, dedicatoria, detalles
            FROM PastelesClientes
            WHERE fecha_pedido BETWEEN ? AND ? AND sucursal = ?
        """, (inicio, fin, sucursal))
    else:
        cur2.execute("""
            SELECT id_pedido_cliente, color, sabor, tamaño, cantidad, precio, total, sucursal, fecha_pedido, foto_path, dedicatoria, detalles
            FROM PastelesClientes
            WHERE fecha_pedido BETWEEN ? AND ?
        """, (inicio, fin))
    clientes = cur2.fetchall()
    conn2.close()

    # nombre de archivo
    file_date = hoy.strftime("%Y-%m-%d")
    filename = output_path or f"Reporte_MiPastel_{file_date}" + (f"_{sucursal}" if sucursal else "") + ".pdf"

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, alignment=TA_CENTER)

    elements = []
    elements.append(Paragraph("🧁 Mi Pastel — Reporte del día", titulo_style))
    elements.append(Paragraph(f"Fecha: {hoy.strftime('%d/%m/%Y')}", styles['Normal']))
    if sucursal:
        elements.append(Paragraph(f"Sucursal: {sucursal}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # ---------------- Pivot Normales ----------------
    elements.append(Paragraph("🍰 Resumen - Pasteles Normales (pivot)", styles['Heading2']))
    pivot_table, pivot_note = generar_pdf_normales_pivot(normales)
    elements.append(pivot_table)
    elements.append(Spacer(1, 12))
    if pivot_note:
        elements.append(Paragraph(pivot_note, styles['Normal']))
    elements.append(Spacer(1, 18))

    # ---------------- Clientes detalle ----------------
    elements.append(Paragraph("🧁 Detalle - Pedidos de Clientes", styles['Heading2']))
    clientes_table = generar_pdf_clientes_detalle(clientes)
    elements.append(clientes_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("_" * 80, styles['Normal']))
    elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))

    doc.build(elements)
    return filename

def generar_pdf_normales_pivot(normales_rows):
    """
    Construye una tabla pivot con:
      - Filas: 'sabor - tamaño' (excluye 'Media plancha')
      - Columnas: sucursales encontradas en los datos (ordenadas), + 'Total' última columna
      - Celdas: cantidad sumada para esa fila y sucursal
    normales_rows: lista de tuplas (sabor, tamaño, precio, cantidad, sucursal, fecha)
    """
    # extraer sucursales únicas y filas (sabor+tamano)
    sucursales = sorted({r[4] for r in normales_rows})
    filas_keys = sorted({
        f"{r[0]} - {r[1]}" for r in normales_rows if (r[1] and r[1].lower() != "media plancha")
    })

    # mapa (fila -> {sucursal: cantidad})
    tabla = {k: {s: 0 for s in sucursales} for k in filas_keys}

    for r in normales_rows:
        sabor, tamano, precio, cantidad, sucursal, fecha = r
        if not tamano or tamano.lower() == "media plancha":
            continue
        key = f"{sabor} - {tamano}"
        if key not in tabla:
            tabla[key] = {s: 0 for s in sucursales}
        tabla[key][sucursal] = tabla[key].get(sucursal, 0) + (cantidad or 0)

    # construir datos para ReportLab Table
    encabezado = ["Sabor - Tamaño"] + sucursales + ["Total"]
    data = [encabezado]
    for key in filas_keys:
        fila = [key]
        total_fila = 0
        for s in sucursales:
            c = tabla[key].get(s, 0)
            fila.append(str(c))
            total_fila += c
        fila.append(str(total_fila))
        data.append(fila)

    # Estilo tabla
    t = Table(data, repeatRows=1, colWidths=[160] + [60]* (len(encabezado)-2) + [60])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#764ba2')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 9)
    ]))
    note = "Nota: se excluyen tamaños 'Media plancha' en el resumen por filas."
    return t, note

def generar_pdf_clientes_detalle(clientes_rows):
    """
    Construye la tabla de detalle para pedidos de clientes con columnas:
    ID, Cantidad, Sabor, Sucursal, Detalles, FotoID, Dedicatoria, Color
    FotoID: si existe foto_path, usamos f"F-{id_pedido}" como identificador
    """
    encabezado = ["ID Pedido", "Cantidad", "Sabor", "Sucursal", "Detalles", "FotoID", "Dedicatoria", "Color"]
    data = [encabezado]
    for r in clientes_rows:
        id_pedido = r[0]
        color = r[1]
        sabor = r[2]
        tamano = r[3]
        cantidad = r[4] or 0
        precio = r[5]
        total = r[6]
        sucursal = r[7]
        fecha = r[8]
        foto_path = r[9]
        dedicatoria = r[10] if len(r) > 10 else ""
        detalles = r[11] if len(r) > 11 else ""

        foto_id = f"F-{id_pedido}" if foto_path else ""
        # fila con la info solicitada
        fila = [str(id_pedido), str(cantidad), f"{sabor}", sucursal or "", detalles or "", foto_id, dedicatoria or "", color or ""]
        data.append(fila)

    t = Table(data, repeatRows=1, colWidths=[50, 50, 90, 80, 140, 50, 100, 60])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 9)
    ]))
    return t

# cuando se ejecuta como script
if __name__ == "__main__":
    try:
        fname = generar_reporte_completo(date.today())
        print("PDF creado:", fname)
    except Exception as e:
        print("Error al generar reporte:", e)
