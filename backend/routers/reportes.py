from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from backend.database import DatabaseManager, get_conn_normales, get_conn_clientes
from datetime import datetime, date
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import logging

router = APIRouter(prefix="/reportes", tags=["Reportes"])
logger = logging.getLogger(__name__)

# Configurar directorio de salida para PDFs
PDF_OUTPUT_DIR = "pdf_reports"
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

@router.get("/dia/pdf")
def generar_pdf_dia(
        fecha: str = Query(None, description="Fecha en formato YYYY-MM-DD (por defecto hoy)"),
        sucursal: str = Query(None, description="Filtrar por sucursal específica")
):
    """Genera un PDF con los pedidos del día especificado o actual"""
    try:
        # Determinar fecha
        if fecha:
            try:
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        else:
            fecha_obj = date.today()

        inicio = datetime.combine(fecha_obj, datetime.min.time())
        fin = datetime.combine(fecha_obj, datetime.max.time())

        # Obtener datos usando DatabaseManager
        db = DatabaseManager()

        normales = db.obtener_pasteles_normales(
            fecha_inicio=inicio.isoformat(),
            fecha_fin=fin.isoformat(),
            sucursal=sucursal
        )

        clientes = db.obtener_pedidos_clientes(
            fecha_inicio=inicio.isoformat(),
            fecha_fin=fin.isoformat(),
            sucursal=sucursal
        )

        # Generar nombre de archivo
        if sucursal:
            filename = f"Reporte_{fecha_obj}_{sucursal.replace(' ', '_')}.pdf"
        else:
            filename = f"Reporte_General_{fecha_obj}.pdf"

        filepath = os.path.join(PDF_OUTPUT_DIR, filename)

        # Crear PDF
        doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()

        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor=colors.HexColor('#d63384')
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#e60073')
        )

        elements = []

        # Encabezado
        elements.append(Paragraph("🧁 MI PASTEL", title_style))
        elements.append(Paragraph(f"Reporte del Día - {fecha_obj}", styles['Heading2']))

        if sucursal:
            elements.append(Paragraph(f"Sucursal: {sucursal}", styles['Heading3']))

        elements.append(Spacer(1, 20))

        # Estadísticas rápidas
        total_normales = len(normales)
        total_clientes = len(clientes)
        ingresos_normales = sum(p['precio'] * p['cantidad'] for p in normales)
        ingresos_clientes = sum(p['total'] for p in clientes)

        stats_text = f"""
        <b>Resumen del Día:</b><br/>
        • Pasteles Normales: {total_normales} pedidos - Q{ingresos_normales:,.2f}<br/>
        • Pedidos Clientes: {total_clientes} pedidos - Q{ingresos_clientes:,.2f}<br/>
        • <b>Total: {total_normales + total_clientes} pedidos - Q{ingresos_normales + ingresos_clientes:,.2f}</b>
        """
        elements.append(Paragraph(stats_text, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Pasteles normales
        if normales:
            elements.append(Paragraph("🍰 PASTELES NORMALES", subtitle_style))

            data = [["ID", "Sabor", "Tamaño", "Precio", "Cantidad", "Total", "Sucursal", "Fecha"]]
            for pedido in normales:
                total_pedido = pedido['precio'] * pedido['cantidad']
                data.append([
                    str(pedido['id']),
                    pedido['sabor'][:15],  # Limitar longitud para mejor visualización
                    pedido['tamano'],
                    f"Q{pedido['precio']:.2f}",
                    str(pedido['cantidad']),
                    f"Q{total_pedido:.2f}",
                    pedido['sucursal'][:10],  # Limitar longitud
                    pedido['fecha'][11:16] if len(pedido['fecha']) > 10 else pedido['fecha']  # Solo hora
                ])

            # Crear tabla con estilos
            table = Table(data, repeatRows=1, colWidths=[30, 60, 50, 50, 40, 50, 60, 40])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fff0f5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#d63384')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fffaf6')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ffcce0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')])
            ]))
            elements.append(table)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Total Pasteles Normales: Q{ingresos_normales:,.2f}</b>", styles['Normal']))
        else:
            elements.append(Paragraph("🍰 PASTELES NORMALES", subtitle_style))
            elements.append(Paragraph("No hay pedidos normales para esta fecha.", styles['Normal']))

        elements.append(Spacer(1, 20))

        # Pedidos de clientes
        if clientes:
            elements.append(PageBreak())  # Nueva página para clientes si hay muchos datos
            elements.append(Paragraph("🧁 PEDIDOS DE CLIENTES", subtitle_style))

            data = [["ID", "Color", "Sabor", "Tamaño", "Cant.", "P.Unit", "Total", "Sucursal"]]
            for pedido in clientes:
                data.append([
                    str(pedido['id']),
                    pedido['color'][:8] if pedido['color'] else '-',
                    pedido['sabor'][:12],
                    pedido['tamano'],
                    str(pedido['cantidad']),
                    f"Q{pedido['precio']:.2f}",
                    f"Q{pedido['total']:.2f}",
                    pedido['sucursal'][:8]
                ])

            table = Table(data, repeatRows=1, colWidths=[30, 40, 50, 45, 30, 45, 50, 45])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fff0f5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#d63384')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fffaf6')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ffcce0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')])
            ]))
            elements.append(table)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Total Pedidos Clientes: Q{ingresos_clientes:,.2f}</b>", styles['Normal']))

            # Detalles adicionales para pedidos especiales
            pedidos_con_detalles = [p for p in clientes if p.get('dedicatoria') or p.get('detalles')]
            if pedidos_con_detalles:
                elements.append(Spacer(1, 15))
                elements.append(Paragraph("📝 PEDIDOS ESPECIALES", subtitle_style))
                for pedido in pedidos_con_detalles[:5]:  # Máximo 5 para no saturar
                    detalle_text = f"<b>Pedido #{pedido['id']}</b> - {pedido['sabor']} {pedido['tamano']}"
                    if pedido.get('dedicatoria'):
                        detalle_text += f"<br/>💬: {pedido['dedicatoria'][:50]}..."
                    if pedido.get('detalles'):
                        detalle_text += f"<br/>📋: {pedido['detalles'][:50]}..."
                    elements.append(Paragraph(detalle_text, styles['Normal']))
                    elements.append(Spacer(1, 5))
        else:
            elements.append(Paragraph("🧁 PEDIDOS DE CLIENTES", subtitle_style))
            elements.append(Paragraph("No hay pedidos de clientes para esta fecha.", styles['Normal']))

        # Pie de página
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Paragraph("Sistema Mi Pastel v2.0", styles['Normal']))

        # Construir PDF
        doc.build(elements)

        logger.info(f"PDF generado: {filename} - {total_normales} normales, {total_clientes} clientes")
        return FileResponse(path=filepath, filename=filename, media_type="application/pdf")

    except Exception as e:
        logger.error(f"Error al generar PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {str(e)}")

@router.get("/sucursal/pdf")
def generar_pdf_sucursal(
        sucursal: str = Query(..., description="Nombre de la sucursal"),
        fecha: str = Query(None, description="Fecha en formato YYYY-MM-DD (por defecto hoy)")
):
    """Genera un PDF específico para una sucursal"""
    return generar_pdf_dia(fecha=fecha, sucursal=sucursal)

@router.get("/mensual/pdf")
def generar_pdf_mensual(
        año: int = Query(..., description="Año (ej: 2024)"),
        mes: int = Query(..., description="Mes (1-12)"),
        sucursal: str = Query(None, description="Filtrar por sucursal")
):
    """Genera un PDF con los pedidos de un mes completo"""
    try:
        # Validar mes
        if mes < 1 or mes > 12:
            raise HTTPException(status_code=400, detail="Mes debe estar entre 1 y 12")

        # Calcular fechas del mes
        inicio_mes = datetime(año, mes, 1)
        if mes == 12:
            fin_mes = datetime(año + 1, 1, 1)
        else:
            fin_mes = datetime(año, mes + 1, 1)

        inicio = inicio_mes
        fin = fin_mes

        # Obtener datos
        db = DatabaseManager()

        normales = db.obtener_pasteles_normales(
            fecha_inicio=inicio.isoformat(),
            fecha_fin=fin.isoformat(),
            sucursal=sucursal
        )

        clientes = db.obtener_pedidos_clientes(
            fecha_inicio=inicio.isoformat(),
            fecha_fin=fin.isoformat(),
            sucursal=sucursal
        )

        # Generar nombre de archivo
        nombre_mes = inicio_mes.strftime("%B")
        if sucursal:
            filename = f"Reporte_Mensual_{nombre_mes}_{año}_{sucursal.replace(' ', '_')}.pdf"
        else:
            filename = f"Reporte_Mensual_{nombre_mes}_{año}.pdf"

        filepath = os.path.join(PDF_OUTPUT_DIR, filename)

        # Crear PDF (similar estructura al diario pero con estadísticas mensuales)
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()

        elements = []
        elements.append(Paragraph(f"🧁 MI PASTEL - REPORTE MENSUAL", styles['Heading1']))
        elements.append(Paragraph(f"{nombre_mes} {año}", styles['Heading2']))

        if sucursal:
            elements.append(Paragraph(f"Sucursal: {sucursal}", styles['Heading3']))

        elements.append(Spacer(1, 20))

        # Estadísticas mensuales
        total_normales = len(normales)
        total_clientes = len(clientes)
        ingresos_normales = sum(p['precio'] * p['cantidad'] for p in normales)
        ingresos_clientes = sum(p['total'] for p in clientes)

        stats_text = f"""
        <b>Resumen Mensual:</b><br/>
        • Pasteles Normales: {total_normales} pedidos - Q{ingresos_normales:,.2f}<br/>
        • Pedidos Clientes: {total_clientes} pedidos - Q{ingresos_clientes:,.2f}<br/>
        • <b>Total General: {total_normales + total_clientes} pedidos - Q{ingresos_normales + ingresos_clientes:,.2f}</b>
        """
        elements.append(Paragraph(stats_text, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Aquí podrías agregar más análisis mensuales como:
        # - Promedio diario
        # - Sucursal con más ventas
        # - Sabor más popular, etc.

        # Por ahora usamos la misma tabla que el reporte diario
        if normales:
            elements.append(Paragraph("🍰 PASTELES NORMALES", styles['Heading2']))
            # ... (misma lógica de tabla que en generar_pdf_dia)

        if clientes:
            elements.append(Paragraph("🧁 PEDIDOS DE CLIENTES", styles['Heading2']))
            # ... (misma lógica de tabla que en generar_pdf_dia)

        doc.build(elements)

        logger.info(f"PDF mensual generado: {filename}")
        return FileResponse(path=filepath, filename=filename, media_type="application/pdf")

    except Exception as e:
        logger.error(f"Error al generar PDF mensual: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar reporte mensual: {str(e)}")

@router.get("/estadisticas")
def obtener_estadisticas_reporte(
        fecha: str = Query(None, description="Fecha en formato YYYY-MM-DD"),
        sucursal: str = Query(None, description="Filtrar por sucursal")
):
    """Endpoint para obtener estadísticas sin generar PDF"""
    try:
        if fecha:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            inicio = datetime.combine(fecha_obj, datetime.min.time())
            fin = datetime.combine(fecha_obj, datetime.max.time())
        else:
            fecha_obj = date.today()
            inicio = datetime.combine(fecha_obj, datetime.min.time())
            fin = datetime.combine(fecha_obj, datetime.max.time())

        db = DatabaseManager()

        normales = db.obtener_pasteles_normales(
            fecha_inicio=inicio.isoformat(),
            fecha_fin=fin.isoformat(),
            sucursal=sucursal
        )

        clientes = db.obtener_pedidos_clientes(
            fecha_inicio=inicio.isoformat(),
            fecha_fin=fin.isoformat(),
            sucursal=sucursal
        )

        estadisticas = {
            "fecha": fecha_obj.isoformat(),
            "sucursal": sucursal or "Todas",
            "pasteles_normales": {
                "total": len(normales),
                "cantidad_total": sum(p['cantidad'] for p in normales),
                "ingresos": sum(p['precio'] * p['cantidad'] for p in normales)
            },
            "pedidos_clientes": {
                "total": len(clientes),
                "cantidad_total": sum(p['cantidad'] for p in clientes),
                "ingresos": sum(p['total'] for p in clientes)
            },
            "totales": {
                "pedidos": len(normales) + len(clientes),
                "ingresos": sum(p['precio'] * p['cantidad'] for p in normales) + sum(p['total'] for p in clientes)
            }
        }

        return estadisticas

    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")