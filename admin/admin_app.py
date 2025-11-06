# admin_app.py - VERSIÓN CORREGIDA
import sys
import os
from pathlib import Path

# Configurar paths ABSOLUTOS
BASE_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(BASE_DIR))

print(f"📁 Admin App - Directorio base: {BASE_DIR}")

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from database import DatabaseManager, get_conn_normales, get_conn_clientes
    from admin.ui_main import MainWindow
    print("✅ Módulos importados correctamente en admin_app")
except ImportError as e:
    print(f"❌ Error en imports: {e}")
    # Fallback básico
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Mi Pastel - Admin (Fallback)")
            label = QLabel("Error: No se pudieron cargar los módulos necesarios")
            layout = QVBoxLayout()
            layout.addWidget(label)
            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)

class AdminApp(MainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mi Pastel — Administración Completa v2.0")
        self.db = DatabaseManager()

        # Conectar señales
        self.conectar_señales()

        # Carga inicial
        self.cargar_datos_iniciales()

    def conectar_señales(self):
        """Conecta todas las señales de la UI"""
        try:
            # Pasteles normales
            if hasattr(self, 'btn_actualizar_normales'):
                self.btn_actualizar_normales.clicked.connect(self.cargar_pasteles_normales)

            # Pedidos de clientes
            if hasattr(self, 'btn_actualizar_clientes'):
                self.btn_actualizar_clientes.clicked.connect(self.cargar_pedidos_clientes)

            # Configuración
            if hasattr(self, 'btn_cargar_precios'):
                self.btn_cargar_precios.clicked.connect(self.cargar_precios)
            if hasattr(self, 'btn_guardar_precios'):
                self.btn_guardar_precios.clicked.connect(self.guardar_precios)

            # Nuevos pedidos
            if hasattr(self, 'btn_nuevo_pedido'):
                self.btn_nuevo_pedido.clicked.connect(self.mostrar_dialogo_pedido)

            print("✅ Señales conectadas correctamente")
        except Exception as e:
            print(f"⚠️  Algunas señales no se pudieron conectar: {e}")

    def cargar_datos_iniciales(self):
        """Carga todos los datos al iniciar"""
        try:
            self.cargar_pasteles_normales()
            self.cargar_pedidos_clientes()
            self.cargar_precios()
            self.statusBar().showMessage("✅ Sistema cargado correctamente")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos: {e}")

    def cargar_pasteles_normales(self):
        """Carga pasteles normales"""
        try:
            pasteles = self.db.obtener_pasteles_normales()
            if hasattr(self, 'table_normales'):
                tabla = self.table_normales
                tabla.setRowCount(len(pasteles))

                for i, pastel in enumerate(pasteles):
                    tabla.setItem(i, 0, QTableWidgetItem(str(pastel['id'])))
                    tabla.setItem(i, 1, QTableWidgetItem(pastel['sabor']))
                    tabla.setItem(i, 2, QTableWidgetItem(pastel['tamano']))
                    tabla.setItem(i, 3, QTableWidgetItem(f"Q{pastel['precio']:.2f}"))
                    tabla.setItem(i, 4, QTableWidgetItem(str(pastel['cantidad'])))
                    tabla.setItem(i, 5, QTableWidgetItem(pastel['sucursal']))
                    tabla.setItem(i, 6, QTableWidgetItem(pastel['fecha']))
                    tabla.setItem(i, 7, QTableWidgetItem(pastel.get('detalles', '')))

                self.statusBar().showMessage(f"✅ Pasteles normales: {len(pasteles)} registros")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar pasteles: {e}")

    def cargar_pedidos_clientes(self):
        """Carga pedidos de clientes"""
        try:
            pedidos = self.db.obtener_pedidos_clientes()
            if hasattr(self, 'table_clientes'):
                tabla = self.table_clientes
                tabla.setRowCount(len(pedidos))

                for i, pedido in enumerate(pedidos):
                    tabla.setItem(i, 0, QTableWidgetItem(str(pedido['id'])))
                    tabla.setItem(i, 1, QTableWidgetItem(pedido.get('color', '')))
                    tabla.setItem(i, 2, QTableWidgetItem(pedido['sabor']))
                    tabla.setItem(i, 3, QTableWidgetItem(pedido['tamano']))
                    tabla.setItem(i, 4, QTableWidgetItem(str(pedido['cantidad'])))
                    tabla.setItem(i, 5, QTableWidgetItem(f"Q{pedido['precio']:.2f}"))
                    tabla.setItem(i, 6, QTableWidgetItem(f"Q{pedido['total']:.2f}"))
                    tabla.setItem(i, 7, QTableWidgetItem(pedido['sucursal']))
                    tabla.setItem(i, 8, QTableWidgetItem(pedido['fecha']))
                    tabla.setItem(i, 9, QTableWidgetItem(pedido.get('dedicatoria', '')))
                    tabla.setItem(i, 10, QTableWidgetItem(pedido.get('detalles', '')))

                self.statusBar().showMessage(f"✅ Pedidos clientes: {len(pedidos)} registros")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar pedidos: {e}")

    def cargar_precios(self):
        """Carga configuración de precios"""
        try:
            precios = self.db.obtener_precios()
            if hasattr(self, 'table_precios'):
                tabla = self.table_precios
                tabla.setRowCount(len(precios))

                for i, precio in enumerate(precios):
                    tabla.setItem(i, 0, QTableWidgetItem(str(precio['id'])))
                    tabla.setItem(i, 1, QTableWidgetItem(precio['sabor']))
                    tabla.setItem(i, 2, QTableWidgetItem(precio['tamano']))
                    tabla.setItem(i, 3, QTableWidgetItem(f"{precio['precio']:.2f}"))

                self.statusBar().showMessage(f"✅ Precios cargados: {len(precios)} configuraciones")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar precios: {e}")

    def guardar_precios(self):
        """Guarda cambios en precios"""
        try:
            if not hasattr(self, 'table_precios'):
                return

            precios_actualizados = []
            tabla = self.table_precios

            for row in range(tabla.rowCount()):
                id_item = tabla.item(row, 0)
                sabor_item = tabla.item(row, 1)
                tamano_item = tabla.item(row, 2)
                precio_item = tabla.item(row, 3)

                if all([id_item, sabor_item, tamano_item, precio_item]):
                    try:
                        nuevo_precio = float(precio_item.text())
                        precios_actualizados.append({
                            'id': int(id_item.text()),
                            'sabor': sabor_item.text(),
                            'tamano': tamano_item.text(),
                            'precio': nuevo_precio
                        })
                    except ValueError:
                        QMessageBox.warning(self, "Error", f"Precio inválido en fila {row+1}")
                        return

            if precios_actualizados:
                self.db.actualizar_precios(precios_actualizados)
                QMessageBox.information(self, "Éxito", f"Se actualizaron {len(precios_actualizados)} precios")
                self.cargar_precios()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar precios: {e}")

    def mostrar_dialogo_pedido(self):
        """Muestra diálogo para nuevo pedido"""
        from admin.ui_main import DialogoNuevoPedido
        dialog = DialogoNuevoPedido(self)
        if dialog.exec():
            self.cargar_pedidos_clientes()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = AdminApp()
    ventana.show()
    sys.exit(app.exec())