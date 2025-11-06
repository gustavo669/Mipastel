import sys, os
from datetime import date
import logging
from typing import Optional, Dict, Any # <-- Import de typing

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el directorio padre al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QHBoxLayout, QComboBox, QDateEdit,
    QMessageBox, QFileDialog, QAbstractItemView, QHeaderView
)
from PySide6.QtCore import QDate, Qt, Slot
from PySide6.QtGui import QFont

# Importamos las funciones de base de datos actualizadas
try:
    from database import (
        get_conn_clientes,
        get_conn_normales,
        eliminar_cliente_db,
        eliminar_normal_db,
        obtener_cliente_por_id_db, # <-- CRUD
        obtener_normal_por_id_db   # <-- CRUD
    )
    import reportes
    from config import SUCURSALES_FILTRO
    # Importamos los NUEVOS DIÁLOGOS
    from admin.dialogos import (
        DialogoNuevoNormal,
        DialogoNuevoCliente,
        DialogoPrecios
    )

    print("✅ Módulos de Admin (database, reportes, config, dialogos) importados.")
except ImportError as e:
    logger.error(f"❌ Error fatal en imports de admin_app: {e}", exc_info=True)
    sys.exit(f"Error fatal en imports: {e}")

# ==========================================================
# <<-- TEMA OSCURO (DARK THEME QSS) -->>
# ==========================================================
DARK_STYLE = """
    /* Fondo general */
    QWidget {
        background-color: #282a36; /* Fondo principal (Dracula BG) */
        color: #f8f8f2; /* Texto principal (Dracula FG) */
        font-family: "Segoe UI Variable", "Lato", sans-serif;
        font-size: 10pt;
    }
    
    /* Ventana Principal */
    QMainWindow {
        background-color: #282a36;
    }
    
    /* Pestañas */
    QTabWidget::pane {
        border: 1px solid #44475a; /* Borde del panel (Dracula Comment) */
        border-radius: 5px;
    }
    QTabBar::tab {
        background: #44475a; /* Pestaña inactiva (Dracula Comment) */
        color: #f8f8f2;
        padding: 10px 20px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        border: 1px solid #282a36;
        border-bottom: none;
    }
    QTabBar::tab:selected {
        background: #6272a4; /* Pestaña activa (Dracula Current Line) */
        color: #f8f8f2;
        border: 1px solid #44475a;
        border-bottom: 1px solid #6272a4; /* Oculta borde inferior */
    }
    QTabBar::tab:hover {
        background: #7082b3;
    }
    
    /* Tablas */
    QTableWidget {
        background-color: #3b3d4f; /* Fondo de la tabla (ligeramente más claro) */
        color: #f8f8f2;
        gridline-color: #44475a;
        border-radius: 5px;
        border: 1px solid #44475a;
    }
    QHeaderView::section {
        background-color: #6272a4; /* Cabecera de la tabla */
        color: #f8f8f2;
        padding: 6px;
        border: 1px solid #44475a;
        font-weight: bold;
    }
    QTableWidget::item {
        padding: 5px;
    }
    QTableWidget::item:selected {
        background-color: #bd93f9; /* Morado (Dracula Purple) */
        color: #282a36; /* Texto oscuro en selección */
    }
    
    /* Botones */
    QPushButton {
        background-color: #bd93f9; /* Morado */
        color: #f8f8f2;
        font-weight: bold;
        border: none;
        padding: 8px 15px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #d6b1ff; /* Morado claro */
    }
    QPushButton:disabled {
        background-color: #555;
        color: #999;
    }
    
    /* Botón Verde (Nuevo) */
    QPushButton[cssClass="btnVerde"] {
        background-color: #50fa7b; /* Verde (Dracula Green) */
        color: #282a36;
    }
    QPushButton[cssClass="btnVerde"]:hover {
        background-color: #8affa8;
    }
    
    /* Botón Rosa (Eliminar) */
    QPushButton[cssClass="btnRosa"] {
        background-color: #ff79c6; /* Rosa (Dracula Pink) */
        color: #282a36;
    }
    QPushButton[cssClass="btnRosa"]:hover {
        background-color: #ff9ed9;
    }

    /* Botón Naranja (Editar) */
    QPushButton[cssClass="btnNaranja"] {
        background-color: #ffb86c; /* Naranja (Dracula Orange) */
        color: #282a36;
    }
    QPushButton[cssClass="btnNaranja"]:hover {
        background-color: #ffca8a;
    }
    
    /* ComboBox (Desplegables) */
    QComboBox {
        background-color: #44475a;
        color: #f8f8f2;
        padding: 5px;
        border: 1px solid #6272a4;
        border-radius: 4px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox QAbstractItemView { /* Menú desplegable */
        background-color: #44475a;
        color: #f8f8f2;
        selection-background-color: #bd93f9; /* Morado */
        selection-color: #282a36;
    }
    
    /* Editor de Fechas */
    QDateEdit {
        background-color: #44475a;
        color: #f8f8f2;
        padding: 5px;
        border: 1px solid #6272a4;
        border-radius: 4px;
    }
    QCalendarWidget {
        background-color: #44475a;
        color: #f8f8f2;
    }
    QCalendarWidget QToolButton {
        color: #f8f8f2;
    }
    
    /* Labels (Etiquetas) */
    QLabel {
        color: #f8f8f2;
        font-weight: bold;
    }
    
    /* Barra de Estado */
    QStatusBar {
        color: #999;
    }
    
    /* Scrollbars */
    QScrollBar:vertical {
        background: #282a36;
        width: 10px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background: #6272a4;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar:horizontal {
        background: #282a36;
        height: 10px;
        margin: 0;
    }
    QScrollBar::handle:horizontal {
        background: #6272a4;
        min-width: 20px;
        border-radius: 5px;
    }
    
    /* Diálogos */
    QDialog {
        background-color: #3b3d4f;
    }
    QLineEdit {
        background-color: #44475a;
        color: #f8f8f2;
        padding: 5px;
        border: 1px solid #6272a4;
        border-radius: 4px;
    }
    QLineEdit:read-only {
        background-color: #333;
    }
    QSpinBox {
        background-color: #44475a;
        color: #f8f8f2;
        padding: 5px;
        border: 1px solid #6272a4;
        border-radius: 4px;
    }
"""

class AdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧁 Mi Pastel — Administración de Pedidos v4.0 (Tema Oscuro)")
        self.resize(1300, 800)

        # --- CONSTRUCCIÓN DE UI MANUAL ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout_principal = QVBoxLayout(self.central_widget)

        # --- Layout Superior para Botón de Precios ---
        layout_superior = QHBoxLayout()
        self.btn_admin_precios = QPushButton("⚙️ Administrar Precios")
        layout_superior.addStretch()
        layout_superior.addWidget(self.btn_admin_precios)
        layout_superior.addStretch()
        self.layout_principal.addLayout(layout_superior)

        self.tabs = QTabWidget()
        self.layout_principal.addWidget(self.tabs)

        # ==================== Pestaña Clientes ====================
        self.tab_clientes = QWidget()
        self.layout_clientes = QVBoxLayout(self.tab_clientes)

        # Layout de filtros y CRUD (Centrado)
        filtros_layout_clientes = QHBoxLayout()
        self.date_clientes = QDateEdit(calendarPopup=True)
        self.date_clientes.setDate(QDate.currentDate())
        self.cmb_sucursal_clientes = QComboBox()
        self.cmb_sucursal_clientes.addItems(SUCURSALES_FILTRO)
        self.btn_filtrar_clientes = QPushButton("🔍 Filtrar")
        self.btn_reporte_clientes = QPushButton("🖨️ Imprimir Reporte")

        # --- Botones CRUD Clientes ---
        self.btn_nuevo_cliente = QPushButton("➕ Nuevo")
        self.btn_nuevo_cliente.setProperty("cssClass", "btnVerde") # Estilo verde
        self.btn_editar_cliente = QPushButton("✏️ Editar")
        self.btn_editar_cliente.setProperty("cssClass", "btnNaranja") # Estilo Naranja
        self.btn_eliminar_cliente = QPushButton("❌ Eliminar")
        self.btn_eliminar_cliente.setProperty("cssClass", "btnRosa") # Estilo Rosa

        filtros_layout_clientes.addStretch()
        filtros_layout_clientes.addWidget(QLabel("Fecha:"))
        filtros_layout_clientes.addWidget(self.date_clientes)
        filtros_layout_clientes.addWidget(QLabel("Sucursal:"))
        filtros_layout_clientes.addWidget(self.cmb_sucursal_clientes)
        filtros_layout_clientes.addWidget(self.btn_filtrar_clientes)
        filtros_layout_clientes.addWidget(self.btn_reporte_clientes)
        filtros_layout_clientes.addSpacing(20)
        filtros_layout_clientes.addWidget(self.btn_nuevo_cliente)
        filtros_layout_clientes.addWidget(self.btn_editar_cliente)
        filtros_layout_clientes.addWidget(self.btn_eliminar_cliente)
        filtros_layout_clientes.addStretch()

        self.layout_clientes.addLayout(filtros_layout_clientes)

        self.table_clientes = QTableWidget()
        self.table_clientes.setColumnCount(11)
        self.table_clientes.setHorizontalHeaderLabels([
            "ID", "Color", "Sabor", "Tamano", "Cant.", "Precio U.", "Total",
            "Sucursal", "Fecha", "Dedicatoria", "Detalles"
        ])
        self.table_clientes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_clientes.setSelectionBehavior(QAbstractItemView.SelectRows) # Seleccionar fila entera
        self.table_clientes.setSelectionMode(QAbstractItemView.SingleSelection) # Solo 1 a la vez
        self.table_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_clientes.horizontalHeader().setStretchLastSection(True)
        self.layout_clientes.addWidget(self.table_clientes)
        self.tabs.addTab(self.tab_clientes, "Pedidos de Clientes")

        # ==================== Pestaña Pedidos Normales ====================
        self.tab_normales = QWidget()
        self.layout_normales = QVBoxLayout(self.tab_normales)

        # Layout de filtros y CRUD (Centrado)
        filtros_layout_normales = QHBoxLayout()
        self.date_normales = QDateEdit(calendarPopup=True)
        self.date_normales.setDate(QDate.currentDate())
        self.cmb_sucursal_normales = QComboBox()
        self.cmb_sucursal_normales.addItems(SUCURSALES_FILTRO)
        self.btn_filtrar_normales = QPushButton("🔍 Filtrar")
        self.btn_reporte_normales = QPushButton("🖨️ Imprimir Reporte")

        # --- Botones CRUD Normales ---
        self.btn_nuevo_normal = QPushButton("➕ Nuevo")
        self.btn_nuevo_normal.setProperty("cssClass", "btnVerde")
        self.btn_editar_normal = QPushButton("✏️ Editar")
        self.btn_editar_normal.setProperty("cssClass", "btnNaranja")
        self.btn_eliminar_normal = QPushButton("❌ Eliminar")
        self.btn_eliminar_normal.setProperty("cssClass", "btnRosa")

        filtros_layout_normales.addStretch()
        filtros_layout_normales.addWidget(QLabel("Fecha:"))
        filtros_layout_normales.addWidget(self.date_normales)
        filtros_layout_normales.addWidget(QLabel("Sucursal:"))
        filtros_layout_normales.addWidget(self.cmb_sucursal_normales)
        filtros_layout_normales.addWidget(self.btn_filtrar_normales)
        filtros_layout_normales.addWidget(self.btn_reporte_normales)
        filtros_layout_normales.addSpacing(20)
        filtros_layout_normales.addWidget(self.btn_nuevo_normal)
        filtros_layout_normales.addWidget(self.btn_editar_normal)
        filtros_layout_normales.addWidget(self.btn_eliminar_normal)
        filtros_layout_normales.addStretch()

        self.layout_normales.addLayout(filtros_layout_normales)

        self.table_normales = QTableWidget()
        self.table_normales.setColumnCount(8)
        self.table_normales.setHorizontalHeaderLabels(["ID", "Sabor", "Tamano", "Cant.", "Precio U.", "Sucursal", "Fecha", "Sabor (Otro)"])
        self.table_normales.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_normales.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_normales.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_normales.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_normales.horizontalHeader().setStretchLastSection(True)
        self.layout_normales.addWidget(self.table_normales)
        self.tabs.addTab(self.tab_normales, "Pedidos Normales")
        # --- FIN DE CONSTRUCCIÓN DE UI ---

        # ==================== Conectar Señales y Cargar Datos ====================
        self.conectar_senales()
        self.cargar_datos_iniciales()
        self.statusBar().showMessage("✅ Sistema cargado. Mostrando pedidos de hoy.")

        # Deshabilitar botones CRUD al inicio
        self.actualizar_botones_crud_clientes()
        self.actualizar_botones_crud_normales()

    def conectar_senales(self):
        """Conecta todos los botones a sus funciones"""
        # Admin Precios
        self.btn_admin_precios.clicked.connect(self.abrir_dialogo_precios)

        # Clientes
        self.btn_filtrar_clientes.clicked.connect(self.cargar_clientes)
        self.btn_reporte_clientes.clicked.connect(self.generar_reporte_avanzado)
        self.btn_nuevo_cliente.clicked.connect(self.abrir_dialogo_cliente_nuevo)
        self.btn_editar_cliente.clicked.connect(self.abrir_dialogo_cliente_editar)
        self.btn_eliminar_cliente.clicked.connect(self.eliminar_cliente)
        self.table_clientes.itemSelectionChanged.connect(self.actualizar_botones_crud_clientes)

        # Normales
        self.btn_filtrar_normales.clicked.connect(self.cargar_normales)
        self.btn_reporte_normales.clicked.connect(self.generar_reporte_avanzado)
        self.btn_nuevo_normal.clicked.connect(self.abrir_dialogo_normal_nuevo)
        self.btn_editar_normal.clicked.connect(self.abrir_dialogo_normal_editar)
        self.btn_eliminar_normal.clicked.connect(self.eliminar_normal)
        self.table_normales.itemSelectionChanged.connect(self.actualizar_botones_crud_normales)

    def cargar_datos_iniciales(self):
        """Carga todos los datos al iniciar"""
        # (Ya no cargamos precios aquí)
        self.cargar_clientes()
        self.cargar_normales()

    # ==================== Funciones de Carga (Centradas) ====================

    def _crear_item_centrado(self, texto: str) -> QTableWidgetItem:
        """Helper para crear un QTableWidgetItem centrado y no editable."""
        item = QTableWidgetItem(texto)
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def _get_selected_id(self, table: QTableWidget) -> Optional[int]:
        """Obtiene el ID (col 0) de la fila seleccionada."""
        selected_items = table.selectedItems()
        if not selected_items:
            return None

        try:
            # El ID está en la primera columna (col 0)
            id_item = table.item(selected_items[0].row(), 0)
            return int(id_item.text())
        except Exception as e:
            logger.error(f"Error al obtener ID de fila: {e}")
            return None

    def _get_selected_row_data_dict(self, table: QTableWidget) -> Optional[Dict[str, Any]]:
        """Extrae todos los datos de la fila seleccionada y los devuelve como dict."""
        selected_items = table.selectedItems()
        if not selected_items:
            return None

        try:
            row = selected_items[0].row()
            data = {}
            for col in range(table.columnCount()):
                header = table.horizontalHeaderItem(col).text()
                item = table.item(row, col)
                data[header] = item.text() if item else ""

            # Renombrar claves para que coincidan con la DB
            # Esto es más robusto porque usa los headers de la tabla
            data_db = {
                'id': data.get('ID'),
                'color': data.get('Color'),
                'sabor': data.get('Sabor'),
                'tamano': data.get('Tamano'),
                'cantidad': data.get('Cant.', 1),
                'precio': data.get('Precio U.', 0.0),
                'total': data.get('Total', 0.0),
                'sucursal': data.get('Sucursal'),
                'fecha': data.get('Fecha'),
                'dedicatoria': data.get('Dedicatoria'),
                'detalles': data.get('Detalles'),
                'sabor_personalizado': data.get('Sabor (Otro)')
            }
            return data_db
        except Exception as e:
            logger.error(f"Error al obtener datos de fila: {e}", exc_info=True)
            return None

    def cargar_clientes(self):
        try:
            fecha = self.date_clientes.date().toString("yyyy-MM-dd")
            sucursal = self.cmb_sucursal_clientes.currentText()
            conn = get_conn_clientes()
            cursor = conn.cursor()

            query = """
                SELECT id, color, sabor, tamano, cantidad, precio, total, 
                       sucursal, fecha, dedicatoria, detalles
                FROM PastelesClientes 
                WHERE CAST(fecha AS DATE) = ?
            """
            params = [fecha]
            if sucursal != "Todas":
                query += " AND sucursal = ?"
                params.append(sucursal)
            query += " ORDER BY id DESC"

            cursor.execute(query, params)
            resultados = cursor.fetchall()
            conn.close()

            self.table_clientes.setRowCount(0)
            self.table_clientes.setRowCount(len(resultados))

            for fila, datos in enumerate(resultados):
                for col, valor in enumerate(datos):
                    valor_str = ""
                    if col == 8 and valor: # Columna de fecha
                        valor_str = valor.strftime('%Y-%m-%d %H:%M')
                    else:
                        valor_str = str(valor if valor is not None else '')

                    item = self._crear_item_centrado(valor_str)
                    self.table_clientes.setItem(fila, col, item)

            # self.table_clientes.resizeColumnsToContents() # El header ya lo hace
            self.statusBar().showMessage(f"Clientes: {len(resultados)} pedidos cargados para {fecha}")
        except Exception as e:
            logger.error(f"❌ ERROR DETALLADO (cargar_clientes): {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los pedidos de clientes:\n{e}")
        finally:
            self.actualizar_botones_crud_clientes()

    def cargar_normales(self):
        try:
            fecha = self.date_normales.date().toString("yyyy-MM-dd")
            sucursal = self.cmb_sucursal_normales.currentText()
            conn = get_conn_normales()
            cursor = conn.cursor()

            query = """
                SELECT id, sabor, tamano, cantidad, precio, sucursal, fecha, sabor_personalizado
                FROM PastelesNormales 
                WHERE CAST(fecha AS DATE) = ?
            """
            params = [fecha]
            if sucursal != "Todas":
                query += " AND sucursal = ?"
                params.append(sucursal)
            query += " ORDER BY id DESC"

            cursor.execute(query, params)
            resultados = cursor.fetchall()
            conn.close()

            self.table_normales.setRowCount(0)
            self.table_normales.setRowCount(len(resultados))

            for fila, datos in enumerate(resultados):
                for col, valor in enumerate(datos):
                    valor_str = ""
                    if col == 6 and valor: # Columna de fecha
                        valor_str = valor.strftime('%Y-%m-%d %H:%M')
                    else:
                        valor_str = str(valor if valor is not None else '')

                    item = self._crear_item_centrado(valor_str)
                    self.table_normales.setItem(fila, col, item)

            # self.table_normales.resizeColumnsToContents() # El header ya lo hace
            self.statusBar().showMessage(f"Normales: {len(resultados)} pedidos cargados para {fecha}")
        except Exception as e:
            logger.error(f"❌ ERROR DETALLADO (cargar_normales): {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los pedidos normales:\n{e}")
        finally:
            self.actualizar_botones_crud_normales()

    # ==================== Funciones de Diálogos y CRUD ====================

    @Slot()
    def abrir_dialogo_precios(self):
        """Abre el diálogo de administración de precios."""
        dialog = DialogoPrecios(self)
        dialog.exec()
        # No es necesario recargar nada aquí

    # --- CRUD Clientes ---
    @Slot()
    def actualizar_botones_crud_clientes(self):
        """Habilita/deshabilita botones CRUD si hay una fila seleccionada."""
        hay_seleccion = bool(self.table_clientes.selectedItems())
        self.btn_editar_cliente.setEnabled(hay_seleccion)
        self.btn_eliminar_cliente.setEnabled(hay_seleccion)

    @Slot()
    def abrir_dialogo_cliente_nuevo(self):
        """Abre el diálogo para un cliente NUEVO."""
        dialog = DialogoNuevoCliente(self)
        if dialog.exec():
            self.cargar_clientes()

    @Slot()
    def abrir_dialogo_cliente_editar(self):
        """Abre el diálogo para EDITAR un cliente existente."""
        pedido_id = self._get_selected_id(self.table_clientes)
        if not pedido_id:
            QMessageBox.warning(self, "Error", "No se pudo leer la fila seleccionada.")
            return

        try:
            # Obtener datos frescos de la DB
            data = obtener_cliente_por_id_db(pedido_id)
            if not data:
                QMessageBox.critical(self, "Error", f"No se encontraron datos para el ID {pedido_id}.")
                return

            dialog = DialogoNuevoCliente(self, data_dict=data, pedido_id=pedido_id)
            if dialog.exec():
                self.cargar_clientes()
        except Exception as e:
            logger.error(f"Error al abrir diálogo editar cliente: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos para editar:\n{e}")


    @Slot()
    def eliminar_cliente(self):
        """Elimina el pedido de cliente seleccionado."""
        pedido_id = self._get_selected_id(self.table_clientes)
        if not pedido_id:
            QMessageBox.warning(self, "Error", "No hay ningún pedido seleccionado.")
            return

        respuesta = QMessageBox.warning(self, "Confirmar Eliminación",
                                        f"¿Está seguro de que desea eliminar el pedido de cliente #{pedido_id}?\n\nEsta acción no se puede deshacer.",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No
                                        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                eliminar_cliente_db(pedido_id)
                QMessageBox.information(self, "Éxito", f"Pedido #{pedido_id} eliminado.")
                self.cargar_clientes()
            except Exception as e:
                logger.error(f"Error al eliminar cliente: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el pedido:\n{e}")

    # --- CRUD Normales ---
    @Slot()
    def actualizar_botones_crud_normales(self):
        """Habilita/deshabilita botones CRUD si hay una fila seleccionada."""
        hay_seleccion = bool(self.table_normales.selectedItems())
        self.btn_editar_normal.setEnabled(hay_seleccion)
        self.btn_eliminar_normal.setEnabled(hay_seleccion)

    @Slot()
    def abrir_dialogo_normal_nuevo(self):
        """Abre el diálogo para un pastel normal NUEVO."""
        dialog = DialogoNuevoNormal(self)
        if dialog.exec():
            self.cargar_normales()

    @Slot()
    def abrir_dialogo_normal_editar(self):
        """Abre el diálogo para EDITAR un pastel normal existente."""
        pedido_id = self._get_selected_id(self.table_normales)
        if not pedido_id:
            QMessageBox.warning(self, "Error", "No se pudo leer la fila seleccionada.")
            return

        try:
            # Obtener datos frescos de la DB
            data = obtener_normal_por_id_db(pedido_id)
            if not data:
                QMessageBox.critical(self, "Error", f"No se encontraron datos para el ID {pedido_id}.")
                return

            dialog = DialogoNuevoNormal(self, data_dict=data, pedido_id=pedido_id)
            if dialog.exec():
                self.cargar_normales()
        except Exception as e:
            logger.error(f"Error al abrir diálogo editar normal: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos para editar:\n{e}")

    @Slot()
    def eliminar_normal(self):
        """Elimina el pastel normal seleccionado."""
        pedido_id = self._get_selected_id(self.table_normales)
        if not pedido_id:
            QMessageBox.warning(self, "Error", "No hay ningún pedido seleccionado.")
            return

        respuesta = QMessageBox.warning(self, "Confirmar Eliminación",
                                        f"¿Está seguro de que desea eliminar el pedido normal #{pedido_id}?\n\nEsta acción no se puede deshacer.",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No
                                        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                eliminar_normal_db(pedido_id)
                QMessageBox.information(self, "Éxito", f"Pedido #{pedido_id} eliminado.")
                self.cargar_normales()
            except Exception as e:
                logger.error(f"Error al eliminar normal: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el pedido:\n{e}")

    # ==================== Reportes (Sin cambios) ====================

    def generar_reporte_avanzado(self):
        tab_actual = self.tabs.currentIndex()
        if tab_actual == 0: # Pestaña Clientes (Índice 0 ahora)
            fecha = self.date_clientes.date().toPython()
            sucursal = self.cmb_sucursal_clientes.currentText()
            tipo_reporte = "Clientes"
        elif tab_actual == 1: # Pestaña Normales (Índice 1 ahora)
            fecha = self.date_normales.date().toPython()
            sucursal = self.cmb_sucursal_normales.currentText()
            tipo_reporte = "Normales"
        else:
            return

        if sucursal == "Todas":
            sucursal = None

        ruta = "reportes"
        os.makedirs(ruta, exist_ok=True)
        default_name = f"{ruta}/Reporte_{tipo_reporte}_{fecha.strftime('%Y-%m-%d')}_{sucursal or 'TODAS'}.pdf"
        nombre_pdf, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte", default_name, "PDF Files (*.pdf)"
        )

        if not nombre_pdf:
            self.statusBar().showMessage("Reporte cancelado")
            return

        try:
            self.statusBar().showMessage("Generando reporte avanzado...")
            reportes.generar_reporte_completo(
                target_date=fecha,
                sucursal=sucursal,
                output_path=nombre_pdf
            )
            QMessageBox.information(self, "Reporte generado", f"📄 Reporte guardado en:\n{nombre_pdf}")
            self.statusBar().showMessage("✅ Reporte generado exitosamente")

            try:
                os.startfile(os.path.realpath(nombre_pdf))
            except Exception as e:
                logger.warning(f"No se pudo abrir el PDF automáticamente: {e}")

        except Exception as e:
            logger.error(f"❌ ERROR DETALLADO (generar_reporte): {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte:\n{e}")


# ==================== PUNTO DE ENTRADA ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Establecer fuente bonita
    font = QFont("Segoe UI Variable", 10)
    # --- CORRECCIÓN DE LA LÍNEA ---
    if not font.exactMatch(): # Comprueba la instancia 'font', no la clase 'QFont'
        font = QFont("Lato", 10) # Fallback
    app.setFont(font)

    # Aplicar el TEMA OSCURO
    app.setStyleSheet(DARK_STYLE)

    ventana = AdminApp()
    ventana.show()
    sys.exit(app.exec())