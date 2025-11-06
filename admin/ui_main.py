import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QHBoxLayout, QComboBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import QDate
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from database import obtener_precio_db, get_conn_clientes, get_conn_normales

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧁 Mi Pastel — Administración de Pedidos")
        self.resize(1200, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.tabs = QTabWidget()
        self.layout_principal = QVBoxLayout(self.central_widget)
        self.layout_principal.addWidget(self.tabs)

        # ==================== Pestaña Configuración de Precios ====================
        self.tab_config = QWidget()
        self.layout_config = QVBoxLayout(self.tab_config)

        self.btn_actualizar_precios = QPushButton("🔄 Actualizar precios desde DB")
        self.btn_actualizar_precios.clicked.connect(self.cargar_precios)
        self.layout_config.addWidget(self.btn_actualizar_precios)

        self.table_precios = QTableWidget()
        self.table_precios.setColumnCount(3)
        self.table_precios.setHorizontalHeaderLabels(["Sabor", "Tamaño", "Precio (Q)"])
        self.layout_config.addWidget(self.table_precios)

        self.tabs.addTab(self.tab_config, "Configuración de Precios")

        # ==================== Pestaña Clientes ====================
        self.tab_clientes = QWidget()
        self.layout_clientes = QVBoxLayout(self.tab_clientes)

        filtros_layout = QHBoxLayout()
        self.date_clientes = QDateEdit(calendarPopup=True)
        self.date_clientes.setDate(QDate.currentDate())
        self.cmb_sucursal_clientes = QComboBox()
        self.cmb_sucursal_clientes.addItems(["Todas", "Central", "Zona 1", "Jutiapa", "Jalapa", "Chiquimula"])
        self.btn_filtrar_clientes = QPushButton("Filtrar")
        self.btn_filtrar_clientes.clicked.connect(self.cargar_clientes)
        filtros_layout.addWidget(QLabel("Fecha:"))
        filtros_layout.addWidget(self.date_clientes)
        filtros_layout.addWidget(QLabel("Sucursal:"))
        filtros_layout.addWidget(self.cmb_sucursal_clientes)
        filtros_layout.addWidget(self.btn_filtrar_clientes)
        self.layout_clientes.addLayout(filtros_layout)

        self.table_clientes = QTableWidget()
        self.table_clientes.setColumnCount(7)
        self.table_clientes.setHorizontalHeaderLabels([
            "ID", "Cantidad", "Sabor", "Sucursal", "Detalles", "Foto", "Dedicatoria"
        ])
        self.layout_clientes.addWidget(self.table_clientes)

        self.btn_reporte_clientes = QPushButton("🖨️ Imprimir Reporte de Clientes")
        self.btn_reporte_clientes.clicked.connect(self.reporte_clientes)
        self.layout_clientes.addWidget(self.btn_reporte_clientes)

        self.tabs.addTab(self.tab_clientes, "Clientes")

        # ==================== Pestaña Pedidos Normales ====================
        self.tab_normales = QWidget()
        self.layout_normales = QVBoxLayout(self.tab_normales)

        filtros_normales = QHBoxLayout()
        self.date_normales = QDateEdit(calendarPopup=True)
        self.date_normales.setDate(QDate.currentDate())
        self.cmb_sucursal_normales = QComboBox()
        self.cmb_sucursal_normales.addItems(["Todas", "Central", "Zona 1", "Jutiapa", "Jalapa", "Chiquimula"])
        self.btn_filtrar_normales = QPushButton("Filtrar")
        self.btn_filtrar_normales.clicked.connect(self.cargar_normales)
        filtros_normales.addWidget(QLabel("Fecha:"))
        filtros_normales.addWidget(self.date_normales)
        filtros_normales.addWidget(QLabel("Sucursal:"))
        filtros_normales.addWidget(self.cmb_sucursal_normales)
        filtros_normales.addWidget(self.btn_filtrar_normales)
        self.layout_normales.addLayout(filtros_normales)

        self.table_normales = QTableWidget()
        self.table_normales.setColumnCount(4)
        self.table_normales.setHorizontalHeaderLabels(["ID", "Sabor", "Tamaño", "Cantidad"])
        self.layout_normales.addWidget(self.table_normales)

        self.btn_reporte_normales = QPushButton("🖨️ Imprimir Reporte de Pedidos")
        self.btn_reporte_normales.clicked.connect(self.reporte_normales)
        self.layout_normales.addWidget(self.btn_reporte_normales)

        self.tabs.addTab(self.tab_normales, "Pedidos Normales")

        # ==================== Cargar datos iniciales ====================
        self.cargar_precios()
        self.cargar_clientes()
        self.cargar_normales()

    # ==================== Funciones de carga ====================
    def cargar_precios(self):
        try:
            precios = obtener_precio_db()
            self.table_precios.setRowCount(0)
            for fila, (sabor, tamano, precio) in enumerate(precios):
                self.table_precios.insertRow(fila)
                self.table_precios.setItem(fila, 0, QTableWidgetItem(sabor))
                self.table_precios.setItem(fila, 1, QTableWidgetItem(tamano))
                self.table_precios.setItem(fila, 2, QTableWidgetItem(f"{precio:.2f}"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los precios:\n{e}")

    def cargar_clientes(self):
        try:
            fecha = self.date_clientes.date().toString("yyyy-MM-dd")
            sucursal = self.cmb_sucursal_clientes.currentText()
            conn = get_conn_clientes()
            cursor = conn.cursor()

            query = "SELECT id, cantidad, sabor, sucursal, detalles, foto, dedicatoria FROM pedidos_clientes WHERE fecha = ?"
            params = [fecha]
            if sucursal != "Todas":
                query += " AND sucursal = ?"
                params.append(sucursal)

            cursor.execute(query, params)
            resultados = cursor.fetchall()

            self.table_clientes.setRowCount(0)
            for fila, datos in enumerate(resultados):
                self.table_clientes.insertRow(fila)
                for col, valor in enumerate(datos):
                    self.table_clientes.setItem(fila, col, QTableWidgetItem(str(valor)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los pedidos de clientes:\n{e}")

    def cargar_normales(self):
        try:
            fecha = self.date_normales.date().toString("yyyy-MM-dd")
            sucursal = self.cmb_sucursal_normales.currentText()
            conn = get_conn_normales()
            cursor = conn.cursor()

            query = "SELECT id, sabor, tamano, cantidad FROM pedidos_normales WHERE fecha = ?"
            params = [fecha]
            if sucursal != "Todas":
                query += " AND sucursal = ?"
                params.append(sucursal)

            cursor.execute(query, params)
            resultados = cursor.fetchall()

            self.table_normales.setRowCount(0)
            for fila, datos in enumerate(resultados):
                self.table_normales.insertRow(fila)
                for col, valor in enumerate(datos):
                    self.table_normales.setItem(fila, col, QTableWidgetItem(str(valor)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los pedidos normales:\n{e}")

    # ==================== Reportes ====================
    def reporte_clientes(self):
        fecha = self.date_clientes.date().toString("yyyy-MM-dd")
        sucursal = self.cmb_sucursal_clientes.currentText()
        ruta = "reportes"
        os.makedirs(ruta, exist_ok=True)
        nombre_pdf = f"{ruta}/Reporte_Clientes_{fecha}_{sucursal.replace(' ', '_')}.pdf"

        conn = get_conn_clientes()
        cursor = conn.cursor()
        query = "SELECT id, cantidad, sabor, sucursal, detalles, foto, dedicatoria FROM pedidos_clientes WHERE fecha = ?"
        params = [fecha]
        if sucursal != "Todas":
            query += " AND sucursal = ?"
            params.append(sucursal)

        cursor.execute(query, params)
        datos = cursor.fetchall()

        doc = SimpleDocTemplate(nombre_pdf, pagesize=landscape(letter))
        estilo = getSampleStyleSheet()
        elementos = [Paragraph(f"<b>Reporte de Clientes - {fecha} ({sucursal})</b>", estilo['Title']), Spacer(1, 20)]

        tabla_datos = [["ID", "Cantidad", "Sabor", "Sucursal", "Detalles", "Foto", "Dedicatoria"]]
        for fila in datos:
            tabla_datos.append([str(c) for c in fila])

        tabla = Table(tabla_datos)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.pink),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))
        elementos.append(tabla)
        doc.build(elementos)
        QMessageBox.information(self, "Reporte generado", f"📄 Reporte guardado en:\n{nombre_pdf}")

    def reporte_normales(self):
        fecha = self.date_normales.date().toString("yyyy-MM-dd")
        ruta = "reportes"
        os.makedirs(ruta, exist_ok=True)
        nombre_pdf = f"{ruta}/Reporte_Normales_{fecha}.pdf"

        conn = get_conn_normales()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT sabor, tamano FROM pedidos_normales WHERE fecha = ?", (fecha,))
        sabores = cursor.fetchall()

        sucursales = ["Central", "Zona 1", "Jutiapa", "Jalapa", "Chiquimula"]
        tabla_datos = [["Sabor", "Tamaño"] + sucursales + ["Total"]]

        for sabor, tamano in sabores:
            if "media plancha" in tamano.lower():
                continue
            fila = [sabor, tamano]
            total_fila = 0
            for suc in sucursales:
                cursor.execute(
                    "SELECT SUM(cantidad) FROM pedidos_normales WHERE fecha=? AND sabor=? AND tamano=? AND sucursal=?",
                    (fecha, sabor, tamano, suc)
                )
                cant = cursor.fetchone()[0] or 0
                fila.append(str(cant))
                total_fila += cant
            fila.append(str(total_fila))
            tabla_datos.append(fila)

        doc = SimpleDocTemplate(nombre_pdf, pagesize=landscape(letter))
        estilo = getSampleStyleSheet()
        elementos = [Paragraph(f"<b>Reporte de Pedidos Normales - {fecha}</b>", estilo['Title']), Spacer(1, 20)]

        tabla = Table(tabla_datos)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))
        elementos.append(tabla)
        doc.build(elementos)
        QMessageBox.information(self, "Reporte generado", f"📄 Reporte guardado en:\n{nombre_pdf}")


if __name__ == "__main__":
    app = QApplication([])
    ventana = Ui_MainWindow()
    ventana.show()
    app.exec()
