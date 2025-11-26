from datetime import datetime, date
from database import get_conn_normales, get_conn_clientes
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
from config import SUCURSALES
import os

styles = getSampleStyleSheet()

TAMANO_FUENTE_BODY = 8
TAMANO_FUENTE_HEADER = 9
TAMANO_TITULO = 14

style_celda = ParagraphStyle(
    'CeldaTabla',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=TAMANO_FUENTE_BODY,
    leading=TAMANO_FUENTE_BODY + 2,
    alignment=TA_LEFT,
    wordWrap='CJK'
)

style_celda_centro = ParagraphStyle(
    'CeldaTablaCentro',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=TAMANO_FUENTE_BODY,
    leading=TAMANO_FUENTE_BODY + 2,
    alignment=TA_CENTER,
    wordWrap='CJK'
)

style_celda_derecha = ParagraphStyle(
    'CeldaTablaRight',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=TAMANO_FUENTE_BODY,
    leading=TAMANO_FUENTE_BODY + 2,
    alignment=TA_RIGHT,
    wordWrap='CJK'
)

style_celda_bold = ParagraphStyle(
    'CeldaTablaBold',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=TAMANO_FUENTE_HEADER,
    leading=TAMANO_FUENTE_HEADER + 2,
    alignment=TA_LEFT,
)

style_celda_bold_right = ParagraphStyle(
    'CeldaTablaBoldRight',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=TAMANO_FUENTE_HEADER,
    leading=TAMANO_FUENTE_HEADER + 2,
    alignment=TA_RIGHT,
)

ABREVIACIONES_SUCURSALES = {
    "Jutiapa 1": "Jut1",
    "Jutiapa 2": "Jut2",
    "Jutiapa 3": "Jut3",
    "Progreso": "Prog",
    "Quesada": "Ques",
    "Acatempa": "Acat",
    "Yupiltepeque": "Yupe",
    "Atescatempa": "Ates",
    "Adelanto": "Adel",
    "Jeréz": "Jeréz",
    "Comapa": "Comapa",
    "Carina": "Carina"
}

PRODUCTOS_OFICIALES = [
    "MINI DE FRESAS", "PEQUEÑO DE FRESAS", "MEDIANO DE FRESAS", "GRANDE DE FRESAS", "EXTRA GRANDE DE FRESAS",
    "MINI DE FRUTAS", "PEQUEÑO DE FRUTAS", "MEDIANO DE FRUTAS", "GRANDE DE FRUTAS", "EXTRA GRANDE DE FRUTAS",
    "MINI DE CHOCOLATE", "PEQUEÑO DE CHOCOLATE", "MEDIANO DE CHOCOLATE", "GRANDE DE CHOCOLATE",
    "MINI DE SELVA NEGRA", "PEQUEÑO DE SELVA NEGRA", "MEDIANO DE SELVA NEGRA", "GRANDE DE SELVA NEGRA",
    "MINI DE OREO", "PEQUEÑO DE OREO", "MEDIANO DE OREO",
    "MINI DE CHOCOFRESA", "PEQUEÑO DE CHOCOFRESA", "MEDIANO DE CHOCOFRESA",
    "MINI DE TRES LECHES", "PEQUEÑO DE TRES LECHES", "MEDIANO DE TRES LECHES", "GRANDE DE TRES LECHES",
    "MINI DE TRES LECHES CON ARÁNDANOS", "PEQUEÑO DE TRES LECHES CON ARÁNDANOS", "MEDIANO DE TRES LECHES CON ARÁNDANOS",
]


def agregar_logo_header(elements, fecha, sucursal=None):
    logo_path = "static/uploads/logo1.jpg"
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=1*inch, height=0.4*inch)
            logo.hAlign = 'LEFT'
            elements.append(logo)
            elements.append(Spacer(1, 5))
        except Exception as e:
            print(f"Error al cargar logo: {e}")

    fecha_formateada = fecha.strftime("%d-%m-%Y")
    titulo = Paragraph(f"<font size={TAMANO_TITULO}><b>LISTA DE PRODUCCIÓN Y PEDIDOS</b></font>",
                       ParagraphStyle('TituloCenter', parent=styles['Normal'], alignment=TA_CENTER))
    fecha_label = Paragraph(f"<font size={TAMANO_FUENTE_HEADER + 1}><b>Fecha:</b> {fecha_formateada}</font>", styles["Normal"])

    elements.append(titulo)
    elements.append(fecha_label)
    if sucursal:
        elements.append(Paragraph(f"<font size={TAMANO_FUENTE_HEADER}><b>Sucursal:</b> {sucursal}</font>", styles["Normal"]))
    elements.append(Spacer(1, 10))


def agregar_logo_header_ventas(elements, fecha, sucursal=None):
    logo_path = "static/uploads/logo1.jpg"
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=1*inch, height=0.4*inch)
            logo.hAlign = 'LEFT'
            elements.append(logo)
            elements.append(Spacer(1, 5))
        except Exception as e:
            print(f"Error al cargar logo: {e}")

    fecha_formateada = fecha.strftime("%d-%m-%Y")
    titulo = Paragraph(f"<font size={TAMANO_TITULO+2}><b>REPORTE DE VENTAS</b></font>",
                       ParagraphStyle('TituloCenter', parent=styles['Normal'], alignment=TA_CENTER))
    fecha_label = Paragraph(f"<font size={TAMANO_FUENTE_HEADER + 1}><b>Fecha:</b> {fecha_formateada}</font>", styles["Normal"])

    elements.append(titulo)
    elements.append(fecha_label)
    if sucursal:
        elements.append(Paragraph(f"<font size={TAMANO_FUENTE_HEADER}><b>Sucursal:</b> {sucursal}</font>", styles["Normal"]))
    elements.append(Spacer(1, 15))


def abreviar_sucursal(sucursal):
    return ABREVIACIONES_SUCURSALES.get(sucursal, sucursal[:3])


def generar_pdf_listas(target_date=None, sucursal=None, output_path=None):
    fecha_obj = target_date or date.today()
    return generar_reporte_listas(fecha_obj, sucursal, output_path)


def generar_reporte_listas(target_date, sucursal=None, output_path=None):
    fecha = target_date
    inicio = datetime.combine(fecha, datetime.min.time())
    fin = datetime.combine(fecha, datetime.max.time())

    conn = get_conn_normales()
    cur = conn.cursor()
    query = "SELECT id, sabor, tamano, precio, cantidad, sucursal, fecha_entrega, sabor_personalizado FROM PastelesNormales WHERE fecha BETWEEN ? AND ?"
    params = [inicio, fin]
    if sucursal:
        query += " AND sucursal = ?"
        params.append(sucursal)
    cur.execute(query, tuple(params))
    normales = cur.fetchall()
    conn.close()

    conn = get_conn_clientes()
    cur = conn.cursor()
    query2 = "SELECT id, sabor, tamano, cantidad, sucursal, dedicatoria, detalles, precio, total, foto_path, sabor_personalizado, color, fecha_entrega FROM PastelesClientes WHERE fecha BETWEEN ? AND ?"
    params2 = [inicio, fin]
    if sucursal:
        query2 += " AND sucursal = ?"
        params2.append(sucursal)
    cur.execute(query2, tuple(params2))
    clientes = cur.fetchall()
    conn.close()

    file_date = fecha.strftime("%d-%m-%Y")
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

    agregar_logo_header(elements, fecha, sucursal)

    elements.append(Paragraph(f"<font size={TAMANO_TITULO - 2}><b>Producción — Pasteles de Tiendas</b></font>", styles["Normal"]))
    elements.append(Spacer(1, 6))
    tabla1 = generar_tabla_produccion(normales)
    elements.append(tabla1)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<font size={TAMANO_TITULO - 2}><b>Control de Pedidos — Clientes</b></font>", styles["Normal"]))
    elements.append(Spacer(1, 6))
    tabla2 = generar_tabla_clientes(clientes)
    elements.append(tabla2)

    doc.build(elements)
    return filename

def generar_tabla_produccion(normales):
    sucursales_abreviadas = [abreviar_sucursal(s) for s in SUCURSALES]
    encabezado = ["No.", "Producto"] + sucursales_abreviadas + ["Total"]
    data = [encabezado]

    conteo = {producto: {s: 0 for s in SUCURSALES} for producto in PRODUCTOS_OFICIALES}

    for row in normales:
        _id, sabor, tamano, precio, cantidad, sucursal, fecha_entrega, sabor_personalizado = row
        sabor_real = sabor_personalizado if sabor_personalizado else sabor
        descripcion_db = f"{tamano} de {sabor_real}".upper()

        if "FRESA" in descripcion_db and "FRESAS" not in descripcion_db:
            descripcion_db = descripcion_db.replace("FRESA", "FRESAS")

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

    fila_totales = ["", Paragraph("<b>TOTAL GENERAL</b>", style_celda_bold)]
    for s in SUCURSALES:
        fila_totales.append(str(totales_sucursales[s]))
    fila_totales.append(str(gran_total_dia))
    data.append(fila_totales)

    num_sucursales = len(SUCURSALES)
    ancho_disponible = 740
    ancho_no = 25
    ancho_total = 35
    ancho_producto = 190
    ancho_restante = ancho_disponible - ancho_no - ancho_producto - ancho_total
    ancho_sucursal = max(25, ancho_restante // num_sucursales)

    col_widths = [ancho_no, ancho_producto] + [ancho_sucursal] * num_sucursales + [ancho_total]

    tabla = Table(data, colWidths=col_widths, repeatRows=1)

    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8C8DC")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), TAMANO_FUENTE_HEADER),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),

        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), TAMANO_FUENTE_BODY),
        ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.whitesmoke, colors.white]),

        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,1), (-1,-1), 4),
        ('BOTTOMPADDING', (0,1), (-1,-1), 4),

        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E0E0E0")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), TAMANO_FUENTE_HEADER),
        ('TOPPADDING', (0,-1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,-1), (-1,-1), 6),
        ('GRID', (0,-1), (-1,-1), 1, colors.black),
    ]))
    return tabla


def generar_tabla_clientes(clientes):
    encabezado = [
        "ID", "Cant.", "Descripción", "Suc.", "Color",
        "F. Entrega", "Detalles", "Foto", "Dedicatoria"
    ]
    data = [encabezado]
    total_cantidad_clientes = 0

    for row in clientes:
        _id, sabor, tamano, cantidad, sucursal, dedicatoria, detalles, precio, total, foto_path, sabor_pers, color, fecha_entrega = row
        cant = int(cantidad) if cantidad else 0
        total_cantidad_clientes += cant
        sabor_real = sabor_pers if sabor_pers else sabor
        descripcion_txt = f"{tamano} de {sabor_real}"

        fecha_entrega_formateada = ""
        if fecha_entrega:
            try:
                if isinstance(fecha_entrega, str):
                    fecha_obj = datetime.strptime(fecha_entrega, "%Y-%m-%d")
                else:
                    fecha_obj = fecha_entrega
                fecha_entrega_formateada = fecha_obj.strftime("%d-%m-%Y")
            except:
                fecha_entrega_formateada = str(fecha_entrega)

        data.append([
            str(_id),
            str(cant),
            Paragraph(descripcion_txt, style_celda),
            Paragraph(abreviar_sucursal(sucursal), style_celda_centro),
            Paragraph(color or "", style_celda_centro),
            Paragraph(fecha_entrega_formateada, style_celda_centro),
            Paragraph(detalles or "", style_celda),
            "SI" if foto_path else "NO",
            Paragraph(dedicatoria or "", style_celda)
        ])

    data.append([
        "",
        str(total_cantidad_clientes),
        Paragraph("<b>TOTAL PEDIDOS</b>", style_celda_bold),
        "", "", "", "", "", ""
    ])

    col_widths = [25, 30, 130, 35, 45, 55, 150, 30, 140]

    tabla = Table(data, colWidths=col_widths, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FFDAB9")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), TAMANO_FUENTE_HEADER),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),


        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'CENTER'),
        ('ALIGN', (3,1), (5,-1), 'CENTER'),
        ('ALIGN', (7,1), (7,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), TAMANO_FUENTE_BODY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.whitesmoke]),


        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),


        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E0E0E0")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), TAMANO_FUENTE_HEADER),
        ('ALIGN', (1,-1), (1,-1), 'CENTER'),
        ('TOPPADDING', (0,-1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,-1), (-1,-1), 6),
        ('GRID', (0,-1), (-1,-1), 1, colors.black),
    ]))

    return tabla

def generar_pdf_ventas(target_date=None, sucursal=None, output_path=None):
    fecha_obj = target_date or date.today()
    return generar_reporte_ventas(fecha_obj, sucursal, output_path)

def generar_reporte_ventas(target_date, sucursal=None, output_path=None):
    fecha = target_date
    inicio = datetime.combine(fecha, datetime.min.time())
    fin = datetime.combine(fecha, datetime.max.time())

    conn = get_conn_normales()
    cur = conn.cursor()
    query = "SELECT id, sabor, tamano, precio, cantidad, sucursal, fecha_entrega, sabor_personalizado FROM PastelesNormales WHERE fecha BETWEEN ? AND ?"
    params = [inicio, fin]
    if sucursal:
        query += " AND sucursal = ?"
        params.append(sucursal)
    cur.execute(query, tuple(params))
    normales = cur.fetchall()
    conn.close()

    conn = get_conn_clientes()
    cur = conn.cursor()
    query2 = "SELECT id, sabor, tamano, cantidad, sucursal, dedicatoria, detalles, precio, total, foto_path, sabor_personalizado, color, fecha_entrega FROM PastelesClientes WHERE fecha BETWEEN ? AND ?"
    params2 = [inicio, fin]
    if sucursal:
        query2 += " AND sucursal = ?"
        params2.append(sucursal)
    cur.execute(query2, tuple(params2))
    clientes = cur.fetchall()
    conn.close()

    file_date = fecha.strftime("%d-%m-%Y")
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

    agregar_logo_header_ventas(elements, fecha, sucursal)

    elements.append(Paragraph(f"<font size={TAMANO_TITULO - 2}><b>Ventas - Pasteles de Tienda</b></font>", styles["Normal"]))
    elements.append(Spacer(1, 8))
    tabla_ventas_normales, total_normales = generar_tabla_ventas_normales(normales)
    elements.append(tabla_ventas_normales)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<font size={TAMANO_TITULO - 2}><b>Ventas - Pedidos de Clientes</b></font>", styles["Normal"]))
    elements.append(Spacer(1, 8))
    tabla_ventas_clientes, total_clientes = generar_tabla_ventas_clientes(clientes)
    elements.append(tabla_ventas_clientes)
    elements.append(Spacer(1, 20))

    total_normales_float = float(total_normales)
    total_clientes_float = float(total_clientes)
    total_general = total_normales_float + total_clientes_float

    resumen = f"""
    <font size={TAMANO_FUENTE_HEADER+1} name="Helvetica">
    <b>RESUMEN DE VENTAS DEL DÍA</b><br/><br/>
    Total Pasteles de Tienda: Q {total_normales_float:,.2f}<br/>
    Total Pedidos de Clientes: Q {total_clientes_float:,.2f}<br/>
    <br/>
    <b><font size={TAMANO_TITULO}>TOTAL GENERAL: Q {total_general:,.2f}</font></b>
    </font>
    """
    elements.append(Paragraph(resumen, styles["Normal"]))

    doc.build(elements)
    return filename

def generar_tabla_ventas_normales(normales):
    encabezado = ["Sucursal", "Producto", "Cant.", "Precio Unit.", "Subtotal"]
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
            abreviar_sucursal(sucursal),
            Paragraph(producto, style_celda),
            str(cantidad),
            f"Q {precio:.2f}",
            f"Q {subtotal:.2f}"
        ])

    data.append([
        "",
        Paragraph("<b>TOTAL</b>", style_celda_bold),
        "",
        "",
        Paragraph(f"<b>Q {total_general:,.2f}</b>", style_celda_bold_right)
    ])

    col_widths = [65, 220, 50, 80, 90]

    tabla = Table(data, colWidths=col_widths, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#C8E6C9")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,0), TAMANO_FUENTE_HEADER),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),

        ('ALIGN', (0,1), (0,-1), 'CENTER'),
        ('ALIGN', (2,1), (2,-1), 'CENTER'),
        ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), TAMANO_FUENTE_BODY),
        ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.whitesmoke]),

        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),

        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#A5D6A7")),
        ('FONTSIZE', (0,-1), (-1,-1), TAMANO_FUENTE_HEADER),
        ('GRID', (0,-1), (-1,-1), 1, colors.black),
    ]))
    return tabla, total_general

def generar_tabla_ventas_clientes(clientes):
    encabezado = ["ID", "Suc.", "Producto", "Cant.", "Precio", "Total"]
    data = [encabezado]
    total_general = 0.0

    for row in clientes:
        _id, sabor, tamano, cantidad, sucursal, dedicatoria, detalles, precio, total, foto_path, sabor_pers, color, fecha_entrega = row
        sabor_real = sabor_pers if sabor_pers else sabor
        descripcion = f"{tamano} de {sabor_real}"
        cant = int(cantidad) if cantidad else 0
        precio_val = float(precio) if precio else 0.0
        total_val = float(total) if total else (precio_val * cant)
        total_general += total_val

        data.append([
            str(_id),
            abreviar_sucursal(sucursal),
            Paragraph(descripcion, style_celda),
            str(cant),
            f"Q {precio_val:.2f}",
            f"Q {total_val:.2f}"
        ])

    data.append([
        "",
        "",
        Paragraph("<b>TOTAL</b>", style_celda_bold),
        "",
        "",
        Paragraph(f"<b>Q {total_general:,.2f}</b>", style_celda_bold_right)
    ])

    col_widths = [40, 55, 200, 45, 80, 90]

    tabla = Table(data, colWidths=col_widths, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FFF9C4")),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,0), TAMANO_FUENTE_HEADER),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),

        ('ALIGN', (0,1), (1,-1), 'CENTER'),
        ('ALIGN', (3,1), (3,-1), 'CENTER'),
        ('ALIGN', (4,1), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTSIZE', (0,0), (-1,-1), TAMANO_FUENTE_BODY),
        ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.whitesmoke]),

        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),

        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#FFF59D")),
        ('FONTSIZE', (0,-1), (-1,-1), TAMANO_FUENTE_HEADER),
        ('GRID', (0,-1), (-1,-1), 1, colors.black),
    ]))

    return tabla, total_general

def generar_pdf_dia(target_date=None, sucursal=None, output_path=None):
    return generar_pdf_listas(target_date, sucursal, output_path)

def generar_pdf_por_sucursal(target_date, sucursal, output_path=None):
    return generar_pdf_listas(target_date, sucursal, output_path)