import sys, os
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QHBoxLayout, QComboBox, QDateEdit,
    QFileDialog, QAbstractItemView, QHeaderView, QGridLayout, QMenu,
    QApplication, QDialog, QDialogButtonBox
)
from PySide6.QtCore import QDate, Qt, Slot
from PySide6.QtGui import QFont, QKeyEvent, QPixmap

try:
    from database import (
        get_conn_clientes,
        get_conn_normales,
        eliminar_cliente_db,
        eliminar_normal_db,
        obtener_cliente_por_id_db,
        obtener_normal_por_id_db
    )
    import pdf_reportes
    from config import SUCURSALES_FILTRO
    from admin.dialogos import (
        DialogoNuevoNormal,
        DialogoNuevoCliente,
        DialogoPrecios,
        DialogoConfirmacionMejorado
    )

    print("Módulos de Admin (database, reportes, config, dialogos) importados.")
except ImportError as e:
    logger.error(f"Error fatal en imports de admin_app: {e}", exc_info=True)
    sys.exit(f"Error fatal en imports: {e}")

DARK_STYLE = """
QMainWindow {
    background-color: #ffffff; 
}

QWidget {
    background-color: #ffffff;
    color: #2b1b3a; 
    font-family: "Open Sans", "Lato", sans-serif;
    font-size: 10pt;
    border: none;
}

QTabWidget::pane {
    border: 3px solid #f0d6ec;
    border-radius: 8px;
    background-color: #ffffff;
}

QTabBar::tab {
    background: #ffffff; 
    color: #2b1b3a;
    padding: 12px 24px;
    margin: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 3px solid #e8b8d6;
    font-weight: bold;
    min-width: 120px;
}

QTabBar::tab:selected {
    background: #8e44ad;
    color: #ffffff;
    border: 1px solid #6f2f86;
}

QTabBar::tab:hover {
    background: #b65fae;
    color: #ffffff;
}

QTableWidget {
    background-color: #ffffff;
    color: #2b1b3a;
    gridline-color: #f0d6ec;
    border-radius: 6px;
    border: 2px solid #f0d6ec;
    alternate-background-color: #fff5fb;
}

QHeaderView::section {
    background-color: #8e44ad; 
    color: #ffffff;
    padding: 4px;
    border: 1px solid #6f2f86;
    font-weight: bold;
    font-size: 10pt;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #fff0f6;
}

QTableWidget::item:selected {
    background-color: #b65fae;
    color: #ffffff;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #9b59b6, stop:1 #7d3c98);
    color: #ffffff;
    font-weight: 600;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    min-width: 100px;
    font-size: 12pt; 
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #a66bbf, stop:1 #6e3288);
    padding: 11px 21px;
}

QPushButton:pressed {
    background-color: #5e2a74;
    padding: 9px 19px;
}

QPushButton:disabled {
    background-color: #e9d9ea;
    color: #a78aa8;
}

QPushButton[cssClass="btnVerde"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #48c774, stop:1 #2e8b57);
    color: #ffffff;
    font-size: 12pt;
    padding: 8px 10px;
    border: 2px solid #2b7f4f;
    min-width: 120px;
}

QPushButton[cssClass="btnVerde"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3fb868, stop:1 #256b46);
    padding: 11px 21px;
    border: 2px solid #215c3a;
}

QPushButton[cssClass="btnVerde"]:pressed {
    background: #215c3a;
    padding: 9px 19px;
}

QPushButton[cssClass="btnRosa"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ff88b8, stop:1 #ff6fa3);
    color: #ffffff;
    font-size: 12pt;
    padding: 8px 10px;
    border: 2px solid #ff5f97;
    min-width: 100px;
}

QPushButton[cssClass="btnRosa"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ff6fa3, stop:1 #ff4f87);
    padding: 11px 21px;
    border: 2px solid #e0446f;
}

QPushButton[cssClass="btnRosa"]:pressed {
    background: #e0446f;
    padding: 9px 19px;
}
 
QPushButton[cssClass="btnNaranja"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #7feaf0, stop:1 #2ccadf);
    color: #000000;
    font-size: 12pt;
    padding: 8px 10px;
    border: 2px solid #16a6a6;
    min-width: 100px;
}

QPushButton[cssClass="btnNaranja"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #66e6ea, stop:1 #20bfcf);
    padding: 11px 21px;
    border: 2px solid #118f8f;
}

QPushButton[cssClass="btnNaranja"]:pressed {
    background: #118f8f;
    padding: 9px 19px;
}

QPushButton[cssClass="btnMorado"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #48c774, stop:1 #2e8b57);
    color: #ffffff;
    font-size: 12pt;
    font-weight: bold;
    padding: 8px 10px;
    border: 2px solid #2b7f4f;
    border-radius: 10px;
    min-width: 180px;
}

QPushButton[cssClass="btnMorado"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3fb868, stop:1 #256b46);
    padding: 13px 29px;
    border: 2px solid #215c3a;
}

QPushButton[cssClass="btnMorado"]:pressed {
    background: #215c3a;
    padding: 11px 27px;
}

QPushButton[cssClass="btnAzul"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #6f2f86, stop:1 #4b1257);
    color: #ffffff;
    font-size: 12pt;
    padding: 8px 10px;
    border: 2px solid #5a236f;
    min-width: 120px;
}

QPushButton[cssClass="btnAzul"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #5a236f, stop:1 #3d0e4a);
    padding: 11px 21px;
}

QComboBox {
    background-color: #ffffff;
    color: #2b1b3a;
    padding: 8px;
    border: 2px solid #f0d6ec;
    border-radius: 5px;
    min-width: 120px;
}

QComboBox:hover {
    border-color: #b65fae;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #2b1b3a;
    selection-background-color: #b65fae;
    selection-color: #ffffff;
    border: 1px solid #f0d6ec;
}

QDateEdit {
    background-color: #ffffff;
    color: #2b1b3a;
    padding: 8px;
    border: 2px solid #f0d6ec;
    border-radius: 5px;
    min-width: 120px;
}

QDateEdit:hover {
    border-color: #b65fae;
}

QLabel {
    color: #2b1b3a;
    font-size: 15pt;
    font-family: "Hughs", "Lato", sans-serif;
    text-align: center;
    alignment: center;
    margin: 0 auto;
}

QDialog {
    background-color: #fffff;
    border-radius: 10px;
}

QDialogButtonBox QPushButton {
    min-width: 100px;
    padding: 10px 20px;
    font-size: 12pt;
}

QStatusBar {
    background-color: #6f2f86;
    color: #fff0f6;
    padding: 5px;
}

QScrollBar:vertical {
    background: #fff5fb;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #b65fae;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #8e44ad;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #f0d6ec;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px 0 8px;
    color: #2b1b3a;
}
"""


class AdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mi Pastel — Sistema de Administración")
        self.resize(1350, 690)
        self.setStyleSheet(DARK_STYLE)

        self.setFont(QFont("Segoe UI", 12))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout_principal = QVBoxLayout(self.central_widget)
        self.layout_principal.setSpacing(5)
        self.layout_principal.setContentsMargins(15, 15, 15, 15)

        header_layout = QHBoxLayout()

        img_label = QLabel()
        img = QPixmap("static/uploads/logo1.jpg")
        img = img.scaledToHeight(80)
        img_label.setPixmap(img)

        title_label = QLabel("Panel de Administración de Pedidos")
        title_label.setStyleSheet("""
            QLabel {
                color: #690F73;
                font-family: "Hughs", "Lato", sans-serif; 
                font-size: 38pt;
                padding: 0px;
                margin-left: 5px;      
            }
        """)

        header_layout.addWidget(img_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.btn_admin_precios = QPushButton("Editar Precios")
        self.btn_admin_precios.setProperty("cssClass", "btnMorado")
        self.btn_admin_precios.setToolTip("Configurar precios de pasteles")
        header_layout.addWidget(self.btn_admin_precios)

        self.btn_reporte_ventas = QPushButton("Reportes")
        self.btn_reporte_ventas.setProperty("cssClass", "btnVerde")
        self.btn_reporte_ventas.setToolTip("Generar reporte de ventas")
        header_layout.addWidget(self.btn_reporte_ventas)

        self.layout_principal.addLayout(header_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                margin-top: 10px;
            }
        """)
        self.layout_principal.addWidget(self.tabs)

        self.tab_clientes = QWidget()
        self.layout_clientes = QVBoxLayout(self.tab_clientes)
        self.layout_clientes.setSpacing(10)
        self.layout_clientes.setContentsMargins(10, 10, 10, 10)

        filtros_layout_clientes = QGridLayout()
        filtros_layout_clientes.setSpacing(10)

        filtros_layout_clientes.addWidget(QLabel("Fecha:"), 0, 0)
        self.date_clientes = QDateEdit(calendarPopup=True)
        self.date_clientes.setDate(QDate.currentDate())
        self.date_clientes.setMaximumWidth(150)
        filtros_layout_clientes.addWidget(self.date_clientes, 0, 1)

        filtros_layout_clientes.addWidget(QLabel("Sucursal:"), 0, 2)
        self.cmb_sucursal_clientes = QComboBox()
        self.cmb_sucursal_clientes.addItems(SUCURSALES_FILTRO)
        self.cmb_sucursal_clientes.setMaximumWidth(150)
        filtros_layout_clientes.addWidget(self.cmb_sucursal_clientes, 0, 3)

        self.btn_filtrar_clientes = QPushButton("VER PEDIDOS")
        self.btn_filtrar_clientes.setProperty("cssClass", "btnAzul")
        filtros_layout_clientes.addWidget(self.btn_filtrar_clientes, 0, 4)

        self.btn_reporte_clientes = QPushButton("GENERAR LISTAS")
        self.btn_reporte_clientes.setProperty("cssClass", "btnAzul")
        filtros_layout_clientes.addWidget(self.btn_reporte_clientes, 0, 5)

        self.layout_clientes.addLayout(filtros_layout_clientes)

        self.table_clientes = QTableWidget()
        self.table_clientes.setColumnCount(13)
        self.table_clientes.setHorizontalHeaderLabels([
            "ID", "Cant.", "Tamaño", "Sabor", "Sucursal", "Fecha",
            "Fecha Entrega", "Detalles", "Dedicatoria", "Color", "Precio U.", "Total", "Foto"
        ])
        self.table_clientes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_clientes.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_clientes.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_clientes.setAlternatingRowColors(True)

        header_clientes = self.table_clientes.horizontalHeader()
        header_clientes.setSectionResizeMode(QHeaderView.ResizeToContents)
        header_clientes.setSectionResizeMode(7, QHeaderView.Stretch)
        header_clientes.setSectionResizeMode(8, QHeaderView.Stretch)

        self.layout_clientes.addWidget(self.table_clientes)

        btns_clientes_layout = QHBoxLayout()
        btns_clientes_layout.setSpacing(5)
        btns_clientes_layout.addStretch()

        self.btn_nuevo_cliente = QPushButton("Nuevo")
        self.btn_nuevo_cliente.setProperty("cssClass", "btnVerde")
        self.btn_nuevo_cliente.setFixedWidth(110)
        btns_clientes_layout.addWidget(self.btn_nuevo_cliente)

        self.btn_editar_cliente = QPushButton("Editar")
        self.btn_editar_cliente.setProperty("cssClass", "btnNaranja")
        self.btn_editar_cliente.setFixedWidth(110)
        btns_clientes_layout.addWidget(self.btn_editar_cliente)

        self.btn_eliminar_cliente = QPushButton("Eliminar")
        self.btn_eliminar_cliente.setProperty("cssClass", "btnRosa")
        self.btn_eliminar_cliente.setFixedWidth(110)
        btns_clientes_layout.addWidget(self.btn_eliminar_cliente)

        btns_clientes_layout.addStretch()
        self.layout_clientes.addLayout(btns_clientes_layout)

        self.tabs.addTab(self.tab_clientes, "Pedidos de Clientes")

        self.tab_normales = QWidget()
        self.layout_normales = QVBoxLayout(self.tab_normales)
        self.layout_normales.setSpacing(10)
        self.layout_normales.setContentsMargins(10, 10, 10, 10)

        filtros_layout_normales = QGridLayout()
        filtros_layout_normales.setSpacing(10)

        filtros_layout_normales.addWidget(QLabel("Fecha:"), 0, 0)
        self.date_normales = QDateEdit(calendarPopup=True)
        self.date_normales.setDate(QDate.currentDate())
        self.date_normales.setMaximumWidth(150)
        filtros_layout_normales.addWidget(self.date_normales, 0, 1)

        filtros_layout_normales.addWidget(QLabel("Sucursal:"), 0, 2)
        self.cmb_sucursal_normales = QComboBox()
        self.cmb_sucursal_normales.addItems(SUCURSALES_FILTRO)
        self.cmb_sucursal_normales.setMaximumWidth(150)
        filtros_layout_normales.addWidget(self.cmb_sucursal_normales, 0, 3)

        self.btn_filtrar_normales = QPushButton("VER PEDIDOS")
        self.btn_filtrar_normales.setProperty("cssClass", "btnAzul")
        filtros_layout_normales.addWidget(self.btn_filtrar_normales, 0, 4)

        self.btn_reporte_normales = QPushButton("GENERAR LISTAS")
        self.btn_reporte_normales.setProperty("cssClass", "btnAzul")
        filtros_layout_normales.addWidget(self.btn_reporte_normales, 0, 5)

        self.layout_normales.addLayout(filtros_layout_normales)

        self.table_normales = QTableWidget()
        self.table_normales.setColumnCount(9)
        self.table_normales.setHorizontalHeaderLabels([
            "ID", "Cant.", "Tamaño", "Sabor", "Sucursal", "Fecha", "Fecha Entrega", "Precio U.", "Total"
        ])
        self.table_normales.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_normales.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_normales.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_normales.setAlternatingRowColors(True)

        header_normales = self.table_normales.horizontalHeader()
        header_normales.setSectionResizeMode(QHeaderView.Stretch)

        self.layout_normales.addWidget(self.table_normales)

        btns_normales_layout = QHBoxLayout()
        btns_normales_layout.setSpacing(5)
        btns_normales_layout.addStretch()

        self.btn_nuevo_normal = QPushButton("Nuevo")
        self.btn_nuevo_normal.setProperty("cssClass", "btnVerde")
        self.btn_nuevo_normal.setFixedWidth(110)
        btns_normales_layout.addWidget(self.btn_nuevo_normal)

        self.btn_editar_normal = QPushButton("Editar")
        self.btn_editar_normal.setProperty("cssClass", "btnNaranja")
        self.btn_editar_normal.setFixedWidth(110)
        btns_normales_layout.addWidget(self.btn_editar_normal)

        self.btn_eliminar_normal = QPushButton("Eliminar")
        self.btn_eliminar_normal.setProperty("cssClass", "btnRosa")
        self.btn_eliminar_normal.setFixedWidth(110)
        btns_normales_layout.addWidget(self.btn_eliminar_normal)

        btns_normales_layout.addStretch()
        self.layout_normales.addLayout(btns_normales_layout)

        self.tabs.addTab(self.tab_normales, "Pedidos de Tiendas")

        self.conectar_senales()
        self.configurar_tablas_copia()
        self.cargar_datos_iniciales()

        self.statusBar().showMessage("Sistema cargado exitosamente. Mostrando pedidos de hoy.")

        self.actualizar_botones_crud_clientes()
        self.actualizar_botones_crud_normales()

    def conectar_senales(self):
        self.btn_admin_precios.clicked.connect(self.abrir_dialogo_precios)
        self.btn_reporte_ventas.clicked.connect(self.generar_reporte_ventas)
        self.btn_filtrar_clientes.clicked.connect(self.cargar_clientes)
        self.btn_reporte_clientes.clicked.connect(self.generar_reporte_listas)
        self.btn_nuevo_cliente.clicked.connect(self.abrir_dialogo_cliente_nuevo)
        self.btn_editar_cliente.clicked.connect(self.abrir_dialogo_cliente_editar)
        self.btn_eliminar_cliente.clicked.connect(self.eliminar_cliente)
        self.table_clientes.itemSelectionChanged.connect(self.actualizar_botones_crud_clientes)
        self.btn_filtrar_normales.clicked.connect(self.cargar_normales)
        self.btn_reporte_normales.clicked.connect(self.generar_reporte_listas)
        self.btn_nuevo_normal.clicked.connect(self.abrir_dialogo_normal_nuevo)
        self.btn_editar_normal.clicked.connect(self.abrir_dialogo_normal_editar)
        self.btn_eliminar_normal.clicked.connect(self.eliminar_normal)
        self.table_normales.itemSelectionChanged.connect(self.actualizar_botones_crud_normales)

    def configurar_tablas_copia(self):
        self.table_clientes.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table_normales.setSelectionBehavior(QAbstractItemView.SelectItems)

        self.table_clientes.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table_normales.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.table_clientes.keyPressEvent = self._key_press_event_clientes
        self.table_normales.keyPressEvent = self._key_press_event_normales

        self.table_clientes.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_normales.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_clientes.customContextMenuRequested.connect(self._mostrar_menu_contextual_clientes)
        self.table_normales.customContextMenuRequested.connect(self._mostrar_menu_contextual_normales)

    def _key_press_event_clientes(self, event: QKeyEvent):
        if event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
            self._copiar_seleccion(self.table_clientes)
        else:
            QTableWidget.keyPressEvent(self.table_clientes, event)

    def _key_press_event_normales(self, event: QKeyEvent):
        if event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
            self._copiar_seleccion(self.table_normales)
        else:
            QTableWidget.keyPressEvent(self.table_normales, event)

    def _copiar_seleccion(self, table: QTableWidget):
        selected_items = table.selectedItems()

        if not selected_items:
            return

        min_row = min(item.row() for item in selected_items)
        max_row = max(item.row() for item in selected_items)
        min_col = min(item.column() for item in selected_items)
        max_col = max(item.column() for item in selected_items)

        copied_text = ""

        for row in range(min_row, max_row + 1):
            row_data = []
            for col in range(min_col, max_col + 1):
                item = table.item(row, col)
                if item and item.text():
                    row_data.append(item.text())
                else:
                    row_data.append("")
            copied_text += "\t".join(row_data) + "\n"

        QApplication.clipboard().setText(copied_text.strip())

        self.statusBar().showMessage("Copiado al portapapeles", 3000)

    def _mostrar_menu_contextual_clientes(self, pos):
        self._mostrar_menu_contextual(self.table_clientes, pos)

    def _mostrar_menu_contextual_normales(self, pos):
        self._mostrar_menu_contextual(self.table_normales, pos)

    def _mostrar_menu_contextual(self, table: QTableWidget, pos):
        menu = QMenu(self)

        copiar_action = menu.addAction("Copiar selección")
        copiar_todo_action = menu.addAction("Copiar toda la tabla")

        action = menu.exec(table.mapToGlobal(pos))

        if action == copiar_action:
            self._copiar_seleccion(table)
        elif action == copiar_todo_action:
            self._copiar_toda_tabla(table)

    def _copiar_toda_tabla(self, table: QTableWidget):
        if table.rowCount() == 0:
            return

        headers = []
        for col in range(table.columnCount()):
            header = table.horizontalHeaderItem(col)
            if header:
                headers.append(header.text())
            else:
                headers.append(f"Columna {col+1}")

        copied_text = "\t".join(headers) + "\n"

        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and item.text():
                    row_data.append(item.text())
                else:
                    row_data.append("")
            copied_text += "\t".join(row_data) + "\n"

        QApplication.clipboard().setText(copied_text.strip())

        self.statusBar().showMessage("Tabla completa copiada al portapapeles", 3000)

    def cargar_datos_iniciales(self):
        self.cargar_clientes()
        self.cargar_normales()

    def _crear_item_centrado(self, texto: str) -> QTableWidgetItem:
        item = QTableWidgetItem(texto)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def _crear_item_moneda(self, valor: float) -> QTableWidgetItem:
        item = QTableWidgetItem(f"Q{valor:,.2f}")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def _get_selected_id(self, table: QTableWidget) -> Optional[int]:
        selected_items = table.selectedItems()
        if not selected_items:
            return None

        try:
            id_item = table.item(selected_items[0].row(), 0)
            return int(id_item.text())
        except Exception as e:
            logger.error(f"Error al obtener ID de fila: {e}")
            return None

    def cargar_clientes(self):
        try:
            fecha = self.date_clientes.date().toString("yyyy-MM-dd")
            sucursal = self.cmb_sucursal_clientes.currentText()
            conn = get_conn_clientes()
            cursor = conn.cursor()

            query = """
                SELECT id, cantidad, tamano, sabor, sucursal, fecha, fecha_entrega, 
                       detalles, dedicatoria, color, precio, total, foto_path
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

                for col in range(13):
                    valor = datos[col]
                    valor_str = ""

                    if col == 5:
                        if valor:
                            valor_str = valor.strftime('%Y-%m-%d %H:%M')
                        else:
                            valor_str = ''
                        item = self._crear_item_centrado(valor_str)
                        self.table_clientes.setItem(fila, col, item)

                    elif col == 6:
                        if valor:
                            valor_str = valor.strftime('%Y-%m-%d')
                        else:
                            valor_str = 'Sin especificar'
                        item = self._crear_item_centrado(valor_str)
                        self.table_clientes.setItem(fila, col, item)

                    elif col in (10, 11):
                        if valor is not None:
                            try:
                                valor_float = float(valor)
                                item = self._crear_item_moneda(valor_float)
                                self.table_clientes.setItem(fila, col, item)
                            except (ValueError, TypeError):
                                valor_str = str(valor)
                                item = self._crear_item_centrado(valor_str)
                                self.table_clientes.setItem(fila, col, item)
                        else:
                            item = self._crear_item_centrado('')
                            self.table_clientes.setItem(fila, col, item)

                    elif col == 12:
                        if valor:
                            nombre_foto = os.path.basename(valor) if valor else ""
                            item = self._crear_item_centrado(f"{nombre_foto}")
                        else:
                            item = self._crear_item_centrado("Sin foto")
                        self.table_clientes.setItem(fila, col, item)

                    else:
                        valor_str = str(valor if valor is not None else '')
                        item = self._crear_item_centrado(valor_str)
                        self.table_clientes.setItem(fila, col, item)

            self.statusBar().showMessage(f"Clientes: {len(resultados)} pedidos cargados para {fecha}")
        except Exception as e:
            logger.error(f"ERROR DETALLADO (cargar_clientes): {e}", exc_info=True)
            dialogo = DialogoConfirmacionMejorado(
                self,
                "Error al Cargar",
                f"No se pudieron cargar los pedidos de clientes:\n\n{str(e)}",
                "error"
            )
            dialogo.exec()
        finally:
            self.actualizar_botones_crud_clientes()

    def cargar_normales(self):
        try:
            fecha = self.date_normales.date().toString("yyyy-MM-dd")
            sucursal = self.cmb_sucursal_normales.currentText()
            conn = get_conn_normales()
            cursor = conn.cursor()

            query = """
                SELECT id, cantidad, tamano, sabor, sucursal, fecha, fecha_entrega, precio, total
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

                for col in range(9):
                    valor = datos[col]
                    valor_str = ""

                    if col == 5:
                        if valor:
                            valor_str = valor.strftime('%Y-%m-%d %H:%M')
                        else:
                            valor_str = ''
                        item = self._crear_item_centrado(valor_str)
                        self.table_normales.setItem(fila, col, item)

                    elif col == 6:
                        if valor:
                            valor_str = valor.strftime('%Y-%m-%d')
                        else:
                            valor_str = 'Sin especificar'
                        item = self._crear_item_centrado(valor_str)
                        self.table_normales.setItem(fila, col, item)

                    elif col in (7, 8):
                        if valor is not None:
                            try:
                                valor_float = float(valor)
                                item = self._crear_item_moneda(valor_float)
                                self.table_normales.setItem(fila, col, item)
                            except (ValueError, TypeError):
                                valor_str = str(valor)
                                item = self._crear_item_centrado(valor_str)
                                self.table_normales.setItem(fila, col, item)
                        else:
                            item = self._crear_item_centrado('')
                            self.table_normales.setItem(fila, col, item)

                    else:
                        valor_str = str(valor if valor is not None else '')
                        item = self._crear_item_centrado(valor_str)
                        self.table_normales.setItem(fila, col, item)

            self.statusBar().showMessage(f"Tiendas: {len(resultados)} pedidos cargados para {fecha}")
        except Exception as e:
            logger.error(f"ERROR DETALLADO (cargar_normales): {e}", exc_info=True)
            dialogo = DialogoConfirmacionMejorado(
                self,
                "Error al Cargar",
                f"No se pudieron cargar los pedidos de tienda:\n\n{str(e)}",
                "error"
            )
            dialogo.exec()
        finally:
            self.actualizar_botones_crud_normales()

    @Slot()
    def abrir_dialogo_precios(self):
        dialog = DialogoPrecios(self)
        dialog.exec()

    @Slot()
    def actualizar_botones_crud_clientes(self):
        hay_seleccion = bool(self.table_clientes.selectedItems())
        self.btn_editar_cliente.setEnabled(hay_seleccion)
        self.btn_eliminar_cliente.setEnabled(hay_seleccion)

    @Slot()
    def abrir_dialogo_cliente_nuevo(self):
        dialog = DialogoNuevoCliente(self)
        if dialog.exec():
            self.cargar_clientes()
            self.statusBar().showMessage("Nuevo pedido de cliente agregado exitosamente", 5000)

    @Slot()
    def abrir_dialogo_cliente_editar(self):
        pedido_id = self._get_selected_id(self.table_clientes)
        if not pedido_id:
            dialogo = DialogoConfirmacionMejorado(
                self,
                "Sin Selección",
                "Por favor, seleccione un pedido de la tabla para editar.",
                "error"
            )
            dialogo.exec()
            return

        try:
            data = obtener_cliente_por_id_db(pedido_id)
            if not data:
                dialogo = DialogoConfirmacionMejorado(
                    self,
                    "Error",
                    f"No se encontraron datos para el pedido #{pedido_id}.",
                    "error"
                )
                dialogo.exec()
                return

            dialog = DialogoNuevoCliente(self, data_dict=data, pedido_id=pedido_id)
            if dialog.exec():
                self.cargar_clientes()
                self.statusBar().showMessage(f"Pedido #{pedido_id} actualizado exitosamente", 5000)
        except Exception as e:
            logger.error(f"Error al abrir diálogo editar cliente: {e}", exc_info=True)
            dialogo = DialogoConfirmacionMejorado(
                self,
                "Error al Editar",
                f"No se pudieron cargar los datos para editar:\n\n{str(e)}",
                "error"
            )
            dialogo.exec()

    @Slot()
    def eliminar_cliente(self):
        pedido_id = self._get_selected_id(self.table_clientes)
        if not pedido_id:
            dialogo = DialogoConfirmacionMejorado(
                self,
                "Sin Selección",
                "Por favor, seleccione un pedido de la tabla para eliminar.",
                "error"
            )
            dialogo.exec()
            return

        dialogo = DialogoConfirmacionMejorado(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar el pedido de cliente #{pedido_id}?\n\n"
            f"Esta acción no se puede deshacer.",
            "warning"
        )

        if dialogo.exec():
            try:
                eliminar_cliente_db(pedido_id)
                self.cargar_clientes()
                self.statusBar().showMessage(f"Pedido #{pedido_id} eliminado exitosamente", 5000)
            except Exception as e:
                logger.error(f"Error al eliminar cliente: {e}", exc_info=True)
                dialogo_error = DialogoConfirmacionMejorado(
                    self,
                    "Error al Eliminar",
                    f"No se pudo eliminar el pedido:\n\n{str(e)}",
                    "error"
                )
                dialogo_error.exec()

    @Slot()
    def actualizar_botones_crud_normales(self):
        hay_seleccion = bool(self.table_normales.selectedItems())
        self.btn_editar_normal.setEnabled(hay_seleccion)
        self.btn_eliminar_normal.setEnabled(hay_seleccion)

    @Slot()
    def abrir_dialogo_normal_nuevo(self):
        dialog = DialogoNuevoNormal(self)
        if dialog.exec():
            self.cargar_normales()
            self.statusBar().showMessage("Nuevo pedido agregado exitosamente", 5000)

    @Slot()
    def abrir_dialogo_normal_editar(self):
        pedido_id = self._get_selected_id(self.table_normales)
        if not pedido_id:
            dialogo = DialogoConfirmacionMejorado(
                self,
                "Sin Selección",
                "Por favor, seleccione un pedido de la tabla para editar.",
                "error"
            )
            dialogo.exec()
            return

        try:
            data = obtener_normal_por_id_db(pedido_id)
            if not data:
                dialogo = DialogoConfirmacionMejorado(
                    self,
                    "Error",
                    f"No se encontraron datos para el pedido #{pedido_id}.",
                    "error"
                )
                dialogo.exec()
                return

            dialog = DialogoNuevoNormal(self, data_dict=data, pedido_id=pedido_id)
            if dialog.exec():
                self.cargar_normales()
                self.statusBar().showMessage(f"Pedido #{pedido_id} actualizado exitosamente", 5000)
        except Exception as e:
            logger.error(f"Error al abrir diálogo editar normal: {e}", exc_info=True)
            dialogo = DialogoConfirmacionMejorado(
                self,
                "Error al Editar",
                f"No se pudieron cargar los datos para editar:\n\n{str(e)}",
                "error"
            )
            dialogo.exec()

    @Slot()
    def eliminar_normal(self):
        pedido_id = self._get_selected_id(self.table_normales)
        if not pedido_id:
            dialogo = DialogoConfirmacionMejorado(
                self,
                "Sin Selección",
                "Por favor, seleccione un pedido de la tabla para eliminar.",
                "error"
            )
            dialogo.exec()
            return

        dialogo = DialogoConfirmacionMejorado(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar el pedido normal #{pedido_id}?\n\n"
            f"Esta acción no se puede deshacer.",
            "warning"
        )

        if dialogo.exec():
            try:
                eliminar_normal_db(pedido_id)
                self.cargar_normales()
                self.statusBar().showMessage(f"Pedido #{pedido_id} eliminado exitosamente", 5000)
            except Exception as e:
                logger.error(f"Error al eliminar normal: {e}", exc_info=True)
                dialogo_error = DialogoConfirmacionMejorado(
                    self,
                    "Error al Eliminar",
                    f"No se pudo eliminar el pedido:\n\n{str(e)}",
                    "error"
                )
                dialogo_error.exec()

    def generar_reporte_listas(self):
        """Genera el reporte de listas de producción y pedidos"""
        tab_actual = self.tabs.currentIndex()
        if tab_actual == 0:
            fecha = self.date_clientes.date().toPython()
            sucursal = self.cmb_sucursal_clientes.currentText()
        elif tab_actual == 1:
            fecha = self.date_normales.date().toPython()
            sucursal = self.cmb_sucursal_normales.currentText()
        else:
            return

        if sucursal == "Todas":
            sucursal = None

        ruta = "reportes"
        os.makedirs(ruta, exist_ok=True)
        default_name = f"{ruta}/Listas_{fecha.strftime('%Y-%m-%d')}_{sucursal or 'TODAS'}.pdf"
        nombre_pdf, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte de Listas", default_name, "PDF Files (*.pdf)"
        )

        if not nombre_pdf:
            self.statusBar().showMessage("Generación de reporte cancelada")
            return

        try:
            from pdf_reportes import generar_pdf_listas

            self.statusBar().showMessage("Generando reporte de listas...")
            generar_pdf_listas(
                target_date=fecha,
                sucursal=sucursal,
                output_path=nombre_pdf
            )

            dialogo = DialogoConfirmacionMejorado(
                self,
                "Reporte Generado",
                f"El reporte de listas se ha generado exitosamente:\n\n{nombre_pdf}",
                "success"
            )
            dialogo.exec()

            self.statusBar().showMessage("Reporte de listas generado exitosamente", 5000)

            try:
                if os.name == 'nt':
                    os.startfile(os.path.realpath(nombre_pdf))
                elif os.name == 'posix':
                    import subprocess
                    if os.uname().sysname == 'Darwin':
                        subprocess.call(['open', nombre_pdf])
                    else:  # Linux
                        subprocess.call(['xdg-open', nombre_pdf])
            except Exception as e:
                logger.warning(f"No se pudo abrir el PDF automáticamente: {e}")

        except Exception as e:
            logger.error(f"ERROR DETALLADO (generar_reporte_listas): {e}", exc_info=True)
            dialogo = DialogoConfirmacionMejorado(
                self,
                "Error al Generar Reporte",
                f"No se pudo generar el reporte de listas:\n\n{str(e)}",
                "error"
            )
            dialogo.exec()

    def generar_reporte_ventas(self):
        """Genera el reporte de ventas con selector de fecha y sucursal"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Generar Reporte de Ventas")
        dialog.resize(400, 180)
        dialog.setStyleSheet(DARK_STYLE)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("Seleccione:")
        titulo.setStyleSheet("font-size: 15pt; margin-bottom: 10px;")
        layout.addWidget(titulo)

        fecha_layout = QHBoxLayout()
        fecha_layout.addStretch()
        fecha_layout.addWidget(QLabel("Fecha:"))
        date_selector = QDateEdit(calendarPopup=True)
        date_selector.setDate(QDate.currentDate())
        date_selector.setMaximumWidth(150)
        fecha_layout.addWidget(date_selector)
        fecha_layout.addStretch()
        layout.addLayout(fecha_layout)

        sucursal_layout = QHBoxLayout()
        sucursal_layout.addStretch()
        sucursal_layout.addWidget(QLabel("Sucursal:"))
        sucursal_combo = QComboBox()
        sucursal_combo.addItems(SUCURSALES_FILTRO)
        sucursal_combo.setMaximumWidth(150)
        sucursal_layout.addWidget(sucursal_combo)
        sucursal_layout.addStretch()
        layout.addLayout(sucursal_layout)

        layout.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Generar")
        buttons.button(QDialogButtonBox.Cancel).setText("Cancelar")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        buttons.setCenterButtons(True)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.Accepted:
            from pdf_reportes import generar_pdf_ventas

            fecha_py = date_selector.date().toPython()
            sucursal_sel = sucursal_combo.currentText()
            sucursal_filtro = None if sucursal_sel == "Todas" else sucursal_sel

            ruta = "reportes"
            os.makedirs(ruta, exist_ok=True)
            filename = f"{ruta}/Ventas_{fecha_py.strftime('%Y-%m-%d')}_{sucursal_filtro or 'TODAS'}.pdf"

            try:
                self.statusBar().showMessage("Generando reporte de ventas...")
                generar_pdf_ventas(fecha_py, sucursal_filtro, filename)

                dialogo = DialogoConfirmacionMejorado(
                    self,
                    "Reporte Generado",
                    f"El reporte de ventas se ha generado exitosamente:\n\n{filename}",
                    "success"
                )
                dialogo.exec()

                self.statusBar().showMessage("Reporte de ventas generado exitosamente", 5000)

                try:
                    if os.name == 'nt':
                        os.startfile(os.path.realpath(filename))
                    elif os.name == 'posix':
                        import subprocess
                        if os.uname().sysname == 'Darwin':
                            subprocess.call(['open', filename])
                        else:
                            subprocess.call(['xdg-open', filename])
                except Exception as e:
                    logger.warning(f"No se pudo abrir el PDF automáticamente: {e}")

            except Exception as e:
                logger.error(f"ERROR DETALLADO (generar_reporte_ventas): {e}", exc_info=True)
                dialogo = DialogoConfirmacionMejorado(
                    self,
                    "Error al Generar Reporte",
                    f"No se pudo generar el reporte de ventas:\n\n{str(e)}",
                    "error"
                )
                dialogo.exec()