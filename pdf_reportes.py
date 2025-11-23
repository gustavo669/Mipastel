from datetime import datetime, date
from database import get_conn_normales, get_conn_clientes
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from config import SUCURSALES

styles = getSampleStyleSheet()

style_celda = ParagraphStyle(
    'CeldaTabla',
    parent=styles['Normal'],
    fontSize=7,
    leading=9,
    alignment=TA_LEFT,
    wordWrap='CJK'
)

style_celda_centro = ParagraphStyle(
    'CeldaTablaCentro',
    parent=styles['Normal'],
    fontSize=7,
    leading=9,
    alignment=TA_CENTER,
    wordWrap='CJK'
)

style_celda_derecha = ParagraphStyle(
    'CeldaTablaRight',
    parent=styles['Normal'],
    fontSize=7,
    leading=9,
    alignment=TA_RIGHT,
    wordWrap='CJK'
)

PRODUCTOS_OFICIALES = [
    "MINI DE FRESA", "PEQUEÑO DE FRESA", "MEDIANO DE FRESA", "GRANDE DE FRESA", "EXTRA GRANDE DE FRESAS",
    "MINI DE FRUTAS", "PEQUEÑO DE FRUTAS", "MEDIANO DE FRUTAS", "GRANDE DE FRUTAS", "EXTRA GRANDE DE FRUTAS",
    "MINI DE 3 LECHES", "PEQUEÑO DE 3 LECHES", "MEDIANO DE 3 LECHES", "GRANDE DE 3 LECHES",
    "MINI DE ARÁNDANOS", "PEQUEÑO DE ARÁNDANOS", "MEDIANO DE ARÁNDANOS",
    "MINI DE CHOCOLATE", "PEQUEÑO DE CHOCOLATE", "MEDIANO DE CHOCOLATE", "GRANDE DE CHOCOLATE",
    "MINI DE SELVA NEGRA", "PEQUEÑO DE SELVA NEGRA", "MEDIANO DE SELVA NEGRA", "GRANDE DE SELVA NEGRA",
    "MINI DE OREO", "PEQUEÑO DE OREO", "MEDIANO DE OREO",
    "MINI CHOCOFRESA", "PEQUEÑO CHOCOFRESA", "MEDIANO DE CHOCOFRESA"
]


def generar_pdf_listas(target_date=None, sucursal=None, output_path=None):
    """Genera el reporte de listas de producción y pedidos"""
    fecha_obj = target_date or date.today()
    return generar_reporte_listas(fecha_obj, sucursal, output_path)


def generar_reporte_listas(target_date, sucursal=None, output_path=None):
    fecha = target_date
    inicio = datetime.combine(fecha, datetime.min.time())
    fin = datetime.combine(fecha, datetime.max.time())

    conn = get_conn_normales()
    cur = conn.cursor()
    query = """
        SELECT id, sabor, tamano, precio, cantidad, sucursal, fecha_entrega, sabor_personalizado
        FROM PastelesNormales
        WHERE fecha BETWEEN ? AND ?
    """
    params = [inicio, fin]
    if sucursal:
        query += " AND sucursal = ?"
        params.append(sucursal)
    cur.execute(query, tuple(params))
    normales = cur.fetchall()
    conn.close()

    conn = get_conn_clientes()
    cur = conn.cursor()
    query2 = """
        SELECT id, sabor, tamano, cantidad, sucursal, dedicatoria, detalles, precio, total,
               foto_path, sabor_personalizado
        FROM PastelesClientes
        WHERE fecha BETWEEN ? AND ?
    """
    params2 = [inicio, fin]
    if sucursal:
        query2 += " AND sucursal = ?"
        params2.append(sucursal)
    cur.execute(query2, tuple(params2))
    clientes = cur.fetchall()
    conn.close()

    file_date = fecha.strftime("%Y-%m-%d")
    filename = output_path or f"Listas_{file_date}" + (f"_{sucursal}" if sucursal else "") + ".pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        rightMargin=20,
        leftMargin=20,
        topMargin=25,
        bottomMargin=25
    )
    elements = []

    titulo = Paragraph("<font size=14><b>MI PASTEL - REPORTE DE PRODUCCIÓN Y PEDIDOS</b></font>", styles["Normal"])
    fecha_label = Paragraph(f"<font size=9><b>Fecha:</b> {fecha.strftime('%d/%m/%Y')}</font>", styles["Normal"])

    elements.append(titulo)
    elements.append(fecha_label)
    if sucursal:
        elements.append(Paragraph(f"<font size=9><b>Sucursal:</b> {sucursal}</font>", styles["Normal"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<font size=11><b>Producción — Pasteles Normales</b></font>", styles["Normal"]))
    elements.append(Spacer(1, 5))
    tabla1 = generar_tabla_produccion(normales)
    elements.append(tabla1)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("<font size=11><b>Control de Pedidos — Clientes</b></font>", styles["Normal"]))
    elements.append(Spacer(1, 5))
    tabla2 = generar_tabla_clientes(clientes)
    elements.append(tabla2)

    doc.build(elements)
    return filename


def generar_tabla_produccion(normales):
    encabezado = ["No.", "Producto"] + SUCURSALES + ["Total"]
    data = [encabezado]

    conteo = {producto: {s: 0 for s in SUCURSALES} for producto in PRODUCTOS_OFICIALES}

    for row in normales:
        _id, sabor, tamano, precio, cantidad, sucursal, fecha_entrega, sabor_personalizado = row
        sabor_real = sabor_personalizado if sabor_personalizado else sabor
        descripcion_db = f"{tamano} de {sabor_real}".upper()

        if descripcion_db == "EXTRA GRANDE DE FRESA":
            descripcion_db = "EXTRA GRANDE DE FRESAS"

        if descripcion_db in conteo:
            if sucursal in conteo[descripcion_db]:
                conteo[descripcion_db][sucursal] += cantidad

    totales_sucursales = {s: 0 for s in SUCURSALES}
    gran_total_dia = 0

    codigo = 1
    for descripcion in PRODUCTOS_OFICIALES:
        fila = [str(codigo), Paragraph(descripcion, style_celda)]
        total_fila = 0

        for s in SUCURSALES:
            val = conteo[descripcion][s]
            fila.append("" if val == 0 else str(val))
            total_fila += val
            totales_sucursales[s] += val

        gran_total_dia += total_fila
        fila.append(str(total_fila) if total_fila > 0 else "")
        data.append(fila)
        codigo += 1

    fila_totales = ["", Paragraph("<b>TOTAL GENERAL</b>", style_celda)]
    for s in SUCURSALES:
        fila_totales.append(str(totales_sucursales[s]))
    fila_totales.append(str(gran_total_dia))
    data.append(fila_totales)

    num_sucursales = len(SUCURSALES)
    ancho_disponible = 720

    ancho_no = 25
    ancho_total = 40
    ancho_producto = 140

    ancho_restante = ancho_disponible - ancho_no - ancho_producto - ancho_total
    ancho_sucursal = max(30, ancho_restante // num_sucursales)

    col_widths = [ancho_no, ancho_producto] + [ancho_sucursal] * num_sucursales + [ancho_total]

    tabla = Table(data, colWidths=col_widths, repeatRows=1)

    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#ffd1e6")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.whitesmoke, colors.white]),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),

        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#e0e0e0")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TOPPADDING', (0,-1), (-1,-1), 4),
        ('BOTTOMPADDING', (0,-1), (-1,-1), 4),
        ('GRID', (0,-1), (-1,-1), 1, colors.black),
    ]))
    return tabla


def generar_tabla_clientes(clientes):
    encabezado = [
        "ID", "Cant.", "Descripción", "Suc.",
        "Detalles / Relleno", "Img", "Dedicatoria"
    ]

    data = [encabezado]
    total_cantidad_clientes = 0

    for row in clientes:
        _id, sabor, tamano, cantidad, sucursal, dedicatoria, detalles, precio, total, foto_path, sabor_pers = row

        cant = int(cantidad) if cantidad else 0
        total_cantidad_clientes += cant

        sabor_real = sabor_pers if sabor_pers else sabor
        descripcion_txt = f"{tamano} de {sabor_real}"

        p_descripcion = Paragraph(descripcion_txt, style_celda)
        p_detalles = Paragraph(detalles or "", style_celda)
        p_dedicatoria = Paragraph(dedicatoria or "", style_celda)
        p_sucursal = Paragraph(sucursal, style_celda_centro)

        data.append([
            str(_id),
            str(cant),
            p_descripcion,
            p_sucursal,
            p_detalles,
            "SI" if foto_path else "NO",
            p_dedicatoria
        ])

    data.append([
        "",
        str(total_cantidad_clientes),
        Paragraph("<b>TOTAL PEDIDOS</b>", style_celda),
        "", "", "", ""
    ])

    col_widths = [30, 35, 140, 50, 200, 30, 200]

    tabla = Table(data, colWidths=col_widths, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#ffe9c4")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'CENTER'),
        ('ALIGN', (3,1), (3,-1), 'CENTER'),
        ('ALIGN', (5,1), (5,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.whitesmoke]),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),

        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#e0e0e0")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (1,-1), (1,-1), 'CENTER'),
        ('GRID', (0,-1), (-1,-1), 1, colors.black),
    ]))

    return tabla


def generar_pdf_ventas(target_date=None, sucursal=None, output_path=None):
    """Genera el reporte de ventas con totales en dinero"""
    fecha_obj = target_date or date.today()
    return generar_reporte_ventas(fecha_obj, sucursal, output_path)


def generar_reporte_ventas(target_date, sucursal=None, output_path=None):
    fecha = target_date
    inicio = datetime.combine(fecha, datetime.min.time())
    fin = datetime.combine(fecha, datetime.max.time())

    conn = get_conn_normales()
    cur = conn.cursor()
    query = """
        SELECT id, sabor, tamano, precio, cantidad, sucursal, fecha_entrega, sabor_personalizado
        FROM PastelesNormales
        WHERE fecha BETWEEN ? AND ?
    """
    params = [inicio, fin]
    if sucursal:
        query += " AND sucursal = ?"
        params.append(sucursal)
    cur.execute(query, tuple(params))
    normales = cur.fetchall()
    conn.close()

    conn = get_conn_clientes()
    cur = conn.cursor()
    query2 = """
        SELECT id, sabor, tamano, cantidad, sucursal, dedicatoria, detalles, precio, total,
               foto_path, sabor_personalizado
        FROM PastelesClientes
        WHERE fecha BETWEEN ? AND ?
    """
    params2 = [inicio, fin]
    if sucursal:
        query2 += " AND sucursal = ?"
        params2.append(sucursal)
    cur.execute(query2, tuple(params2))
    clientes = cur.fetchall()
    conn.close()

    file_date = fecha.strftime("%Y-%m-%d")
    filename = output_path or f"Ventas_{file_date}" + (f"_{sucursal}" if sucursal else "") + ".pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    elements = []

    titulo = Paragraph("<font size=16><b>MI PASTEL - REPORTE DE VENTAS</b></font>", styles["Normal"])
    fecha_label = Paragraph(f"<font size=10><b>Fecha:</b> {fecha.strftime('%d/%m/%Y')}</font>", styles["Normal"])

    elements.append(titulo)
    elements.append(fecha_label)
    if sucursal:
        elements.append(Paragraph(f"<font size=10><b>Sucursal:</b> {sucursal}</font>", styles["Normal"]))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("<font size=12><b>Ventas - Pasteles de Tienda</b></font>", styles["Normal"]))
    elements.append(Spacer(1, 8))
    tabla_ventas_normales, total_normales = generar_tabla_ventas_normales(normales)
    elements.append(tabla_ventas_normales)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<font size=12><b>Ventas - Pedidos de Clientes</b></font>", styles["Normal"]))
    elements.append(Spacer(1, 8))
    tabla_ventas_clientes, total_clientes = generar_tabla_ventas_clientes(clientes)
    elements.append(tabla_ventas_clientes)
    elements.append(Spacer(1, 20))

    total_normales_float = float(total_normales)
    total_clientes_float = float(total_clientes)
    total_general = total_normales_float + total_clientes_float

    resumen = f"""
    <font size=11>
    <b>RESUMEN DE VENTAS DEL DÍA</b><br/>
    <br/>
    Total Pasteles de Tienda: Q {total_normales_float:,.2f}<br/>
    Total Pedidos de Clientes: Q {total_clientes_float:,.2f}<br/>
    <br/>
    <b><font size=13>TOTAL GENERAL: Q {total_general:,.2f}</font></b>
    </font>
    """
    elements.append(Paragraph(resumen, styles["Normal"]))

    doc.build(elements)
    return filename


def generar_tabla_ventas_normales(normales):
    encabezado = ["Sucursal", "Producto", "Cantidad", "Precio Unit.", "Subtotal"]
    data = [encabezado]

    ventas = {}
    for row in normales:
        _id, sabor, tamano, precio, cantidad, sucursal, fecha_entrega, sabor_personalizado = row
        sabor_real = sabor_personalizado if sabor_personalizado else sabor
        descripcion = f"{tamano} de {sabor_real}"

        precio_float = float(precio) if precio is not None else 0.0

        key = (sucursal, descripcion, precio_float)
        if key not in ventas:
            ventas[key] = 0
        ventas[key] += cantidad

    total_general = 0.0

    for (sucursal, producto, precio), cantidad in sorted(ventas.items()):
        subtotal = precio * cantidad
        total_general += subtotal

        data.append([
            sucursal,
            Paragraph(producto, style_celda),
            str(cantidad),
            f"Q {precio:.2f}",
            f"Q {subtotal:.2f}"
        ])

    data.append([
        "",
        Paragraph("<b>TOTAL</b>", style_celda),
        "",
        "",
        f"Q {total_general:,.2f}"
    ])

    col_widths = [80, 200, 60, 80, 90]

    tabla = Table(data, colWidths=col_widths, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#d4edda")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (2,1), (2,-1), 'CENTER'),
        ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.whitesmoke]),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),

        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#c3e6cb")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 10),
        ('GRID', (0,-1), (-1,-1), 1, colors.black),
    ]))

    return tabla, total_general


def generar_tabla_ventas_clientes(clientes):
    encabezado = ["ID", "Sucursal", "Producto", "Cant.", "Precio", "Total"]
    data = [encabezado]

    total_general = 0.0

    for row in clientes:
        _id, sabor, tamano, cantidad, sucursal, dedicatoria, detalles, precio, total, foto_path, sabor_pers = row

        sabor_real = sabor_pers if sabor_pers else sabor
        descripcion = f"{tamano} de {sabor_real}"

        cant = int(cantidad) if cantidad else 0
        precio_val = float(precio) if precio else 0.0
        total_val = float(total) if total else (precio_val * cant)

        total_general += total_val

        data.append([
            str(_id),
            sucursal,
            Paragraph(descripcion, style_celda),
            str(cant),
            f"Q {precio_val:.2f}",
            f"Q {total_val:.2f}"
        ])

    data.append([
        "",
        "",
        Paragraph("<b>TOTAL</b>", style_celda),
        "",
        "",
        f"Q {total_general:,.2f}"
    ])

    col_widths = [40, 80, 180, 45, 80, 90]

    tabla = Table(data, colWidths=col_widths, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#fff3cd")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (3,1), (3,-1), 'CENTER'),
        ('ALIGN', (4,1), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.whitesmoke]),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),

        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#ffeaa7")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 10),
        ('GRID', (0,-1), (-1,-1), 1, colors.black),
    ]))

    return tabla, total_general


def generar_pdf_dia(target_date=None, sucursal=None, output_path=None):
    """Alias para generar_pdf_listas (compatibilidad)"""
    return generar_pdf_listas(target_date, sucursal, output_path)


def generar_pdf_por_sucursal(target_date, sucursal, output_path=None):
    """Alias para generar_pdf_listas (compatibilidad)"""
    return generar_pdf_listas(target_date, sucursal, output_path)