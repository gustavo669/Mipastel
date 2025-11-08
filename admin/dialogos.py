"""
Diálogos Emergentes para la App Admin v4.0
--------------------------------------------
Este archivo contiene:
1. DialogoPrecios: Para ver y editar la lista de precios.
2. _BaseFormDialog: Una clase base para los formularios de pedido.
3. DialogoNuevoNormal: Formulario para pedidos normales (Crear/Editar).
4. DialogoNuevoCliente: Formulario para pedidos de cliente (Crear/Editar).
"""
import sys
import logging
from typing import Optional, Dict, Any, List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QCheckBox, QDialogButtonBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QPushButton
)
from PySide6.QtCore import Qt, Slot

# Importar funciones de la base de datos y configuración
try:
    from database import (
        obtener_precio_db,
        actualizar_precios_db,
        registrar_pastel_normal_db,
        actualizar_pastel_normal_db,
        registrar_pedido_cliente_db,
        actualizar_pedido_cliente_db
    )
    from config import SABORES_NORMALES, SABORES_CLIENTES, TAMANOS, SUCURSALES
except ImportError as e:
    logging.error(f"Error fatal en imports de dialogos.py: {e}")
    sys.exit(f"Error fatal en imports de dialogos: {e}")

logger = logging.getLogger(__name__)

# ==========================================================
# DIÁLOGO DE ADMINISTRACIÓN DE PRECIOS
# ==========================================================

class DialogoPrecios(QDialog):
    """Diálogo para ver y editar la lista de precios."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Administración de Precios")
        self.setMinimumSize(700, 500)
        self.precios_originales = {}

        layout = QVBoxLayout(self)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_cargar = QPushButton("🔄 Cargar Precios")
        self.btn_guardar = QPushButton("💾 Guardar Cambios")
        self.btn_guardar.setProperty("cssClass", "btnVerde")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cargar)
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Tabla
        self.table_precios = QTableWidget()
        self.table_precios.setColumnCount(4)
        self.table_precios.setHorizontalHeaderLabels(["ID", "Sabor", "Tamano", "Precio (Q)"])
        self.table_precios.setColumnHidden(0, True) # Ocultamos ID
        self.table_precios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_precios.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_precios.setSelectionMode(QAbstractItemView.SingleSelection)
        # Permitir editar con doble click
        self.table_precios.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)

        layout.addWidget(self.table_precios)

        # Conexiones
        self.btn_cargar.clicked.connect(self.cargar_precios)
        self.btn_guardar.clicked.connect(self.guardar_precios)
        self.table_precios.itemChanged.connect(self.marcar_cambio)

        # Carga inicial
        self.cargar_precios()

    @Slot()
    def cargar_precios(self):
        try:
            precios = obtener_precio_db()
            self.table_precios.setRowCount(0)
            self.table_precios.setRowCount(len(precios))
            self.precios_originales.clear()

            for fila, (id_precio, sabor, tamano, precio) in enumerate(precios):
                # Guardar estado original
                self.precios_originales[fila] = f"{sabor}|{tamano}|{precio:.2f}"

                # ID (Col 0)
                item_id = QTableWidgetItem(str(id_precio))
                item_id.setFlags(item_id.flags() & ~Qt.ItemIsEditable) # No editable
                item_id.setTextAlignment(Qt.AlignCenter)
                self.table_precios.setItem(fila, 0, item_id)

                # Sabor (Col 1)
                item_sabor = QTableWidgetItem(sabor)
                item_sabor.setTextAlignment(Qt.AlignCenter)
                self.table_precios.setItem(fila, 1, item_sabor)

                # Tamano (Col 2)
                item_tamano = QTableWidgetItem(tamano)
                item_tamano.setTextAlignment(Qt.AlignCenter)
                self.table_precios.setItem(fila, 2, item_tamano)

                # Precio (Col 3)
                item_precio = QTableWidgetItem(f"{precio:.2f}")
                item_precio.setTextAlignment(Qt.AlignCenter)
                self.table_precios.setItem(fila, 3, item_precio)

            self.table_precios.resizeColumnsToContents()
            self.btn_guardar.setEnabled(False) # Deshabilitar hasta que haya cambios
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los precios:\n{e}")

    @Slot(QTableWidgetItem)
    def marcar_cambio(self, item: QTableWidgetItem):
        """Habilita el botón de guardar si el contenido de una celda cambia."""
        fila = item.row()
        if fila not in self.precios_originales:
            return # Fila nueva, aún no relevante

        # Reconstruir el estado actual
        try:
            sabor_actual = self.table_precios.item(fila, 1).text()
            tamano_actual = self.table_precios.item(fila, 2).text()
            precio_actual_str = self.table_precios.item(fila, 3).text().replace("Q", "")
            precio_actual = float(precio_actual_str)
            estado_actual = f"{sabor_actual}|{tamano_actual}|{precio_actual:.2f}"

            if estado_actual != self.precios_originales[fila]:
                self.btn_guardar.setEnabled(True)
        except Exception:
            pass # Error al parsear float, el usuario está escribiendo

    @Slot()
    def guardar_precios(self):
        try:
            precios_actualizados = []
            filas_con_error = []

            for row in range(self.table_precios.rowCount()):
                try:
                    id_item = self.table_precios.item(row, 0)
                    sabor_item = self.table_precios.item(row, 1)
                    tamano_item = self.table_precios.item(row, 2)
                    precio_item = self.table_precios.item(row, 3)

                    if not all([id_item, sabor_item, tamano_item, precio_item]):
                        raise ValueError("Fila incompleta")

                    nuevo_precio = float(precio_item.text().replace("Q", "").strip())
                    precios_actualizados.append({
                        'id': int(id_item.text()),
                        'sabor': sabor_item.text().strip(),
                        'tamano': tamano_item.text().strip(),
                        'precio': nuevo_precio
                    })
                except Exception as e:
                    logger.warning(f"Error al parsear fila {row}: {e}")
                    filas_con_error.append(str(row + 1))

            if filas_con_error:
                QMessageBox.warning(self, "Error de Formato",
                                    f"No se pudo guardar.\nPrecio inválido en filas: {', '.join(filas_con_error)}")
                return

            if not precios_actualizados:
                QMessageBox.information(self, "Sin Cambios", "No hay cambios que guardar.")
                return

            # Confirmar
            respuesta = QMessageBox.question(self, "Confirmar Cambios",
                                             f"¿Está seguro de que desea guardar {len(precios_actualizados)} cambios en los precios?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if respuesta == QMessageBox.StandardButton.Yes:
                actualizar_precios_db(precios_actualizados)
                QMessageBox.information(self, "Éxito", f"Se actualizaron {len(precios_actualizados)} precios")
                self.cargar_precios() # Recargar para resetear el estado
        except Exception as e:
            logger.error(f"Error al guardar precios: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al guardar precios:\n{e}")


# ==========================================================
# CLASE BASE PARA FORMULARIOS DE PEDIDO
# ==========================================================

class _BaseFormDialog(QDialog):
    """Clase base para los formularios de 'Nuevo Pedido'."""

    def __init__(self, parent=None, data_dict: Optional[Dict[str, Any]] = None, pedido_id: Optional[int] = None):
        super().__init__(parent)

        self.is_edit_mode = (pedido_id is not None)
        self.pedido_id = pedido_id
        self.data_dict = data_dict or {}

        # Título y tamaño
        titulo = "Editar Pedido" if self.is_edit_mode else "Registrar Nuevo Pedido"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(500)

        # --- Layouts ---
        self.layout_principal = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        # --- Widgets Comunes ---
        self.cmb_sabor = QComboBox()
        self.cmb_tamano = QComboBox()
        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setMinimum(1)
        self.spin_cantidad.setValue(1)

        self.line_precio_unitario = QLineEdit()
        self.line_precio_unitario.setReadOnly(True)
        self.line_precio_total = QLineEdit()
        self.line_precio_total.setReadOnly(True)

        self.check_es_otro = QCheckBox("Es un sabor personalizado")
        self.line_sabor_personalizado = QLineEdit()
        self.line_sabor_personalizado.setPlaceholderText("Ej: Vainilla con almendras")

        self.cmb_sucursal = QComboBox()
        self.cmb_sucursal.addItems(SUCURSALES) # Lista maestra sin "Todas"

        self.line_detalles = QLineEdit()

        # --- Botones OK/Cancel ---
        self.botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        # --- Conexiones Comunes ---
        self.cmb_sabor.currentTextChanged.connect(self.actualizar_precio)
        self.cmb_tamano.currentTextChanged.connect(self.actualizar_precio)
        self.spin_cantidad.valueChanged.connect(self.actualizar_precio)
        self.check_es_otro.toggled.connect(self.toggle_sabor_personalizado)
        self.botones.accepted.connect(self.accept)
        self.botones.rejected.connect(self.reject)

    @Slot()
    def toggle_sabor_personalizado(self):
        """Activa/desactiva el campo de sabor personalizado."""
        es_otro = self.check_es_otro.isChecked()
        self.line_sabor_personalizado.setEnabled(es_otro)
        if not es_otro:
            self.line_sabor_personalizado.clear()
        self.actualizar_precio() # Recalcular

    @Slot()
    def actualizar_precio(self):
        """Calcula el precio unitario y total automáticamente."""
        sabor = self.cmb_sabor.currentText()
        tamano = self.cmb_tamano.currentText()
        cantidad = self.spin_cantidad.value()
        es_otro = self.check_es_otro.isChecked()

        # Si es "Otro" y no es modo edición, el precio es 0 (manual)
        if es_otro and not self.is_edit_mode:
            precio_unitario = 0.0
            self.line_precio_unitario.setText("0.00 (Manual)")
            self.line_precio_unitario.setReadOnly(False) # Permitir editar

        # Si es modo edición y es "Otro", usar el precio guardado
        elif es_otro and self.is_edit_mode:
            precio_unitario = float(self.data_dict.get('precio', 0.0))
            self.line_precio_unitario.setText(f"{precio_unitario:.2f} (Manual)")
            self.line_precio_unitario.setReadOnly(False) # Permitir editar

        # Si es un sabor normal, buscarlo en la DB
        else:
            try:
                precio_unitario = obtener_precio_db(sabor, tamano)
                self.line_precio_unitario.setText(f"{precio_unitario:.2f}")
                self.line_precio_unitario.setReadOnly(True) # No editable
            except Exception as e:
                logger.error(f"Error al obtener precio: {e}")
                precio_unitario = 0.0
                self.line_precio_unitario.setText("Error")
                self.line_precio_unitario.setReadOnly(True)

        total = precio_unitario * cantidad
        self.line_precio_total.setText(f"{total:.2f}")

    def accept(self):
        """Valida y guarda los datos antes de cerrar."""
        try:
            if self.check_es_otro.isChecked() and not self.line_sabor_personalizado.text():
                raise ValueError("Debe especificar el 'Sabor (Otro)' si la casilla está marcada.")

            data = self.obtener_datos_formulario()

            # Decidir si crear o actualizar
            if self.is_edit_mode:
                self.actualizar_en_db(data)
            else:
                self.registrar_en_db(data)

            QMessageBox.information(self, "Éxito", "Pedido guardado correctamente.")
            super().accept() # Cierra el diálogo

        except Exception as e:
            logger.error(f"Error al guardar pedido: {e}", exc_info=True)
            QMessageBox.critical(self, "Error al Guardar", str(e))
            # No cerramos el diálogo si hay error

    def obtener_datos_formulario(self) -> Dict[str, Any]:
        """Función placeholder, debe ser implementada por las clases hijas."""
        raise NotImplementedError

    def registrar_en_db(self, data: Dict[str, Any]):
        """Función placeholder, debe ser implementada por las clases hijas."""
        raise NotImplementedError

    def actualizar_en_db(self, data: Dict[str, Any]):
        """Función placeholder, debe ser implementada por las clases hijas."""
        raise NotImplementedError

# ==========================================================
# DIÁLOGO PARA PASTELES NORMALES
# ==========================================================

class DialogoNuevoNormal(_BaseFormDialog):
    def __init__(self, parent=None, data_dict: Optional[Dict[str, Any]] = None, pedido_id: Optional[int] = None):
        super().__init__(parent, data_dict, pedido_id)

        # Llenar ComboBoxes
        self.cmb_sabor.addItems(SABORES_NORMALES)
        self.cmb_tamano.addItems(TAMANOS)

        # Construir formulario
        self.form_layout.addRow("Sabor:", self.cmb_sabor)
        self.form_layout.addRow("Tamaño:", self.cmb_tamano)
        self.form_layout.addRow(self.check_es_otro)
        self.form_layout.addRow("Sabor (Otro):", self.line_sabor_personalizado)
        self.form_layout.addRow("Cantidad:", self.spin_cantidad)
        self.form_layout.addRow("Precio Unitario (Q):", self.line_precio_unitario)
        self.form_layout.addRow("Precio Total (Q):", self.line_precio_total)
        self.form_layout.addRow("Sucursal:", self.cmb_sucursal)
        self.form_layout.addRow("Detalles:", self.line_detalles)

        self.layout_principal.addLayout(self.form_layout)
        self.layout_principal.addWidget(self.botones)

        # Cargar datos si estamos en modo edición
        if self.is_edit_mode:
            self._cargar_datos()

        # Estado inicial del campo "Otro"
        self.toggle_sabor_personalizado()

    def _cargar_datos(self):
        """Carga los datos del pedido en el formulario para edición."""
        self.cmb_sabor.setCurrentText(self.data_dict.get('sabor', ''))
        self.cmb_tamano.setCurrentText(self.data_dict.get('tamano', ''))
        self.spin_cantidad.setValue(int(self.data_dict.get('cantidad', 1)))
        self.cmb_sucursal.setCurrentText(self.data_dict.get('sucursal', ''))
        self.line_detalles.setText(self.data_dict.get('detalles', ''))

        sabor_otro = self.data_dict.get('sabor_personalizado', '')
        if sabor_otro:
            self.check_es_otro.setChecked(True)
            self.line_sabor_personalizado.setText(sabor_otro)

        # El precio se actualiza automáticamente al final
        self.actualizar_precio()

    def obtener_datos_formulario(self) -> Dict[str, Any]:
        """Recoge los datos del formulario de Pedido Normal."""
        sabor_real = self.line_sabor_personalizado.text() if self.check_es_otro.isChecked() else self.cmb_sabor.currentText()

        # Si el precio fue manual, leerlo del QLineEdit
        if not self.line_precio_unitario.isReadOnly():
            try:
                precio_unitario = float(self.line_precio_unitario.text())
            except ValueError:
                raise ValueError("El precio unitario manual no es un número válido.")
        else:
            precio_unitario = obtener_precio_db(self.cmb_sabor.currentText(), self.cmb_tamano.currentText())

        return {
            "sabor": sabor_real,
            "tamano": self.cmb_tamano.currentText(),
            "cantidad": self.spin_cantidad.value(),
            "precio": precio_unitario,
            "sucursal": self.cmb_sucursal.currentText(),
            "detalles": self.line_detalles.text(),
            "sabor_personalizado": self.line_sabor_personalizado.text() if self.check_es_otro.isChecked() else None
        }

    def registrar_en_db(self, data: Dict[str, Any]):
        registrar_pastel_normal_db(data)

    def actualizar_en_db(self, data: Dict[str, Any]):
        actualizar_pastel_normal_db(self.pedido_id, data)


# ==========================================================
# DIÁLOGO PARA PEDIDOS DE CLIENTES
# ==========================================================

class DialogoNuevoCliente(_BaseFormDialog):
    def __init__(self, parent=None, data_dict: Optional[Dict[str, Any]] = None, pedido_id: Optional[int] = None):
        super().__init__(parent, data_dict, pedido_id)

        # Widgets específicos de Cliente
        self.line_color = QLineEdit()
        self.line_dedicatoria = QLineEdit()

        # Llenar ComboBoxes
        self.cmb_sabor.addItems(SABORES_CLIENTES)
        self.cmb_tamano.addItems(TAMANOS)

        # Construir formulario
        self.form_layout.addRow("Sabor:", self.cmb_sabor)
        self.form_layout.addRow("Tamaño:", self.cmb_tamano)
        self.form_layout.addRow(self.check_es_otro)
        self.form_layout.addRow("Sabor (Otro):", self.line_sabor_personalizado)
        self.form_layout.addRow("Cantidad:", self.spin_cantidad)
        self.form_layout.addRow("Precio Unitario (Q):", self.line_precio_unitario)
        self.form_layout.addRow("Precio Total (Q):", self.line_precio_total)
        self.form_layout.addRow("Sucursal:", self.cmb_sucursal)
        self.form_layout.addRow("Color:", self.line_color)
        self.form_layout.addRow("Dedicatoria:", self.line_dedicatoria)
        self.form_layout.addRow("Detalles Adicionales:", self.line_detalles)

        self.layout_principal.addLayout(self.form_layout)
        self.layout_principal.addWidget(self.botones)

        # Cargar datos si estamos en modo edición
        if self.is_edit_mode:
            self._cargar_datos()

        # Estado inicial del campo "Otro"
        self.toggle_sabor_personalizado()

    def _cargar_datos(self):
        """Carga los datos del pedido en el formulario para edición."""
        self.cmb_sabor.setCurrentText(self.data_dict.get('sabor', ''))
        self.cmb_tamano.setCurrentText(self.data_dict.get('tamano', ''))
        self.spin_cantidad.setValue(int(self.data_dict.get('cantidad', 1)))
        self.cmb_sucursal.setCurrentText(self.data_dict.get('sucursal', ''))
        self.line_detalles.setText(self.data_dict.get('detalles', ''))
        self.line_color.setText(self.data_dict.get('color', ''))
        self.line_dedicatoria.setText(self.data_dict.get('dedicatoria', ''))

        sabor_otro = self.data_dict.get('sabor_personalizado', '')
        if sabor_otro:
            self.check_es_otro.setChecked(True)
            self.line_sabor_personalizado.setText(sabor_otro)

        # El precio se actualiza automáticamente al final
        self.actualizar_precio()

    def obtener_datos_formulario(self) -> Dict[str, Any]:
        """Recoge los datos del formulario de Pedido Cliente."""
        sabor_real = self.line_sabor_personalizado.text() if self.check_es_otro.isChecked() else self.cmb_sabor.currentText()

        if not self.line_precio_unitario.isReadOnly():
            try:
                precio_unitario = float(self.line_precio_unitario.text())
            except ValueError:
                raise ValueError("El precio unitario manual no es un número válido.")
        else:
            precio_unitario = obtener_precio_db(self.cmb_sabor.currentText(), self.cmb_tamano.currentText())

        total = precio_unitario * self.spin_cantidad.value()

        return {
            "sabor": sabor_real,
            "tamano": self.cmb_tamano.currentText(),
            "cantidad": self.spin_cantidad.value(),
            "precio": precio_unitario,
            "total": total,
            "sucursal": self.cmb_sucursal.currentText(),
            "color": self.line_color.text(),
            "dedicatoria": self.line_dedicatoria.text(),
            "detalles": self.line_detalles.text(),
            "sabor_personalizado": self.line_sabor_personalizado.text() if self.check_es_otro.isChecked() else None,
            "foto_path": self.data_dict.get('foto_path'),
            "fecha_entrega": self.data_dict.get('fecha_entrega')
        }

    def registrar_en_db(self, data: Dict[str, Any]):
        registrar_pedido_cliente_db(data)

    def actualizar_en_db(self, data: Dict[str, Any]):
        actualizar_pedido_cliente_db(self.pedido_id, data)