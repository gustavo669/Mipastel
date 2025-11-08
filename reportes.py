from datetime import datetime, date
from database import get_conn_normales, get_conn_clientes
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import logging

logger = logging.getLogger(__name__)

# ==========================================================
# Importamos la lista maestra de sucursales
try:
    from config import SUCURSALES
    print("Reportes.py: Configuración de sucursales cargada.")
except ImportError:
    logger.warning("WARNING (Reportes): No se encontró config.py, usando lista de emergencia")
    SUCURSALES = ["Jutiapa 1", "Jutiapa 2", "Jutiapa 3", "Progreso", "Quesada"] # Fallback
# ==========================================================


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

    # --- OBTENER DATOS DE NORMALES (CORREGIDO) ---
    conn1 = get_conn_normales()
    cur1 = conn1.cursor()

    # (tamano, fecha)
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

    # --- OBTENER DATOS DE CLIENTES (CORREGIDO) ---
    conn2 = get_conn_clientes()
    cur2 = conn2.cursor()

    # (id, tamano, fecha)
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

    # --- Nombre de archivo ---
    file_date = hoy.strftime("%Y-%m-%d")
    filename = output_path or f"Reporte_MiPastel_{file_date}" + (f"_{sucursal}" if sucursal else "") + ".pdf"

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=20, alignment=TA_CENTER)

    elements = []
    elements.append(Paragraph("Mi Pastel Reporte del día", titulo_style))
    elements.append(Paragraph(f"Fecha: {hoy.strftime('%d/%m/%Y')}", styles['Normal']))
    if sucursal:
        elements.append(Paragraph(f"Sucursal: {sucursal}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # ==================================================================
    # <<-- SECCIÓN DE PASTELES NORMALES (ACTUALIZADA CON 2 TABLAS) -->>
    # ==================================================================

    # --- Tabla 1: Normales (POR TAMAÑO) ---
    elements.append(Paragraph("Resumen - Pasteles Normales (por Tamaño)", styles['Heading2']))
    pivot_table_tamano, pivot_note = generar_pdf_normales_pivot_por_tamano(normales, SUCURSALES)
    elements.append(pivot_table_tamano)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(pivot_note, styles['Normal']))
    elements.append(Spacer(1, 18))

    # --- Tabla 2: Normales (TOTAL POR SABOR) ---
    elements.append(Paragraph("Resumen - Pasteles Normales (Total por Sabor)", styles['Heading2']))
    pivot_table_sabor = generar_pdf_normales_pivot_por_sabor(normales, SUCURSALES)
    elements.append(pivot_table_sabor)
    elements.append(Spacer(1, 18))

    # ==================================================================
    # <<-- SECCIÓN DE PEDIDOS DE CLIENTES -->>
    # ==================================================================
    elements.append(Paragraph("Detalle - Pedidos de Clientes", styles['Heading2']))
    clientes_table = generar_pdf_clientes_detalle(clientes)
    elements.append(clientes_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("_" * 80, styles['Normal']))
    elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))

    try:
        doc.build(elements)
        logger.info(f"Reporte PDF generado: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error al construir PDF: {e}", exc_info=True)
        raise Exception(f"Error al construir PDF: {e}")


def generar_pdf_normales_pivot_por_tamano(normales_rows, sucursales_maestra):
    """
    Construye una tabla pivot con:
      - Filas: 'sabor - tamano' (excluye 'Media plancha')
      - Columnas: sucursales_maestra (ordenadas), + 'Total' última columna
      - Celdas: cantidad sumada para esa fila y sucursal
    """
    # Usamos la lista maestra de sucursales para las columnas
    sucursales = sorted(list(set(sucursales_maestra))) # Asegura que sea única y ordenada

    # extraer filas (sabor+tamano) de los datos de HOY
    # Excluye 'media plancha' como se solicitó originalmente
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

        if sucursal in tabla[key]:
            tabla[key][sucursal] = tabla[key].get(sucursal, 0) + (cantidad or 0)
        else:
            if sucursal:
                logger.warning(f"Reporte Pivot (Tamaño): Sucursal '{sucursal}' no encontrada en lista maestra. Omitiendo.")

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
    try:
        col_width_sucursales = max(60, (700 - 160) / (len(sucursales) + 1))
    except ZeroDivisionError:
        col_width_sucursales = 60

    col_widths = [160] + [col_width_sucursales] * (len(sucursales) + 1) # +1 por el Total

    t = Table(data, repeatRows=1, colWidths=col_widths)

    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#764ba2')), # Morado
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 9)
    ]))

    note = "Nota: se excluyen tamaños 'Media plancha' en este resumen."
    return t, note

def generar_pdf_normales_pivot_por_sabor(normales_rows, sucursales_maestra):
    """
    <<-- NUEVA FUNCIÓN -->>
    Construye una tabla pivot con:
      - Filas: 'sabor' (agrupado)
      - Columnas: sucursales_maestra (ordenadas), + 'Total' última columna
      - Celdas: cantidad sumada para esa fila y sucursal
    """
    # Usamos la lista maestra de sucursales para las columnas
    sucursales = sorted(list(set(sucursales_maestra))) # Asegura que sea única y ordenada

    # extraer filas (SOLO sabor) de los datos de HOY
    filas_keys = sorted({ r[0] for r in normales_rows if r[0] })

    # mapa (fila -> {sucursal: cantidad})
    tabla = {k: {s: 0 for s in sucursales} for k in filas_keys}

    for r in normales_rows:
        sabor, tamano, precio, cantidad, sucursal, fecha = r

        # Esta tabla SÍ incluye 'media plancha' y todos los tamaños
        key = sabor
        if key not in tabla:
            tabla[key] = {s: 0 for s in sucursales}

        if sucursal in tabla[key]:
            tabla[key][sucursal] = tabla[key].get(sucursal, 0) + (cantidad or 0)
        else:
            if sucursal:
                logger.warning(f"Reporte Pivot (Sabor): Sucursal '{sucursal}' no encontrada en lista maestra. Omitiendo.")

    # construir datos para ReportLab Table
    encabezado = ["Sabor (Total)"] + sucursales + ["Total"]
    data = [encabezado]

    # Fila de totales (al final)
    totales_columna = {s: 0 for s in sucursales}
    total_general = 0

    for key in filas_keys:
        fila = [key]
        total_fila = 0
        for s in sucursales:
            c = tabla[key].get(s, 0)
            fila.append(str(c))
            total_fila += c
            totales_columna[s] += c # Sumar al total de la columna
            total_general += c    # Sumar al total general
        fila.append(str(total_fila))
        data.append(fila)

    # Añadir fila de TOTALES al final
    fila_totales = ["TOTAL GENERAL"]
    for s in sucursales:
        fila_totales.append(str(totales_columna[s]))
    fila_totales.append(str(total_general))
    data.append(fila_totales)


    # Estilo tabla
    try:
        col_width_sucursales = max(60, (700 - 160) / (len(sucursales) + 1))
    except ZeroDivisionError:
        col_width_sucursales = 60

    col_widths = [160] + [col_width_sucursales] * (len(sucursales) + 1) # +1 por el Total

    t = Table(data, repeatRows=1, colWidths=col_widths)

    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ff79c6')), # Rosa
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        # Estilo para la fila de TOTAL
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#44475a')), # Fondo oscuro
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
    ]))

    return t


def generar_pdf_clientes_detalle(clientes_rows):
    """
    Construye la tabla de detalle para pedidos de clientes.
    Columnas: Sabor, ID Pedido, Cantidad, Sucursal, Detalles, FotoID, Dedicatoria, Color
    """
    # Orden de columnas solicitado
    encabezado = ["Sabor", "ID Pedido", "Cantidad", "Sucursal", "Detalles", "FotoID", "Dedicatoria", "Color"]
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

        # Fila con el orden solicitado
        fila = [
            f"{sabor} ({tamano})", # Sabor
            str(id_pedido),         # ID Pedido
            str(cantidad),          # Cantidad
            sucursal or "",         # Sucursal
            detalles or "",         # Detalles
            foto_id,                # FotoID
            dedicatoria or "",      # Dedicatoria
            color or ""             # Color
        ]
        data.append(fila)

    # Ajustar anchos de columna para el nuevo orden
    t = Table(data, repeatRows=1, colWidths=[100, 60, 60, 80, 120, 50, 100, 60])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#667eea')), # Azul
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 9)
    ]))
    return t

# cuando se ejecuta como script
if __name__ == "__main__":
    try:
        # Importar config para la prueba
        from config import SUCURSALES
        fname = generar_reporte_completo(date.today())
        print("PDF creado:", fname)
    except ImportError:
        print("Error: No se pudo importar 'config.py'. Ejecuta desde 'run.py'.")
    except Exception as e:
        print(f"Error al generar reporte: {e}")