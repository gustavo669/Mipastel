from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QTableWidget, QPushButton, QHBoxLayout
)

class Ui_MainWindow(QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.resize(1000, 700)
        self.centralwidget = QWidget(MainWindow)
        self.tabs = QTabWidget(self.centralwidget)

        self.tabNormales = QWidget()
        layout_normales = QVBoxLayout()
        self.tblNormales = QTableWidget()
        self.tblNormales.setColumnCount(7)
        self.tblNormales.setHorizontalHeaderLabels(["ID","Sabor","Tamaño","Precio","Cantidad","Sucursal","Fecha"])
        layout_btns_n = QHBoxLayout()
        self.btnActualizar = QPushButton("🔄 Actualizar")
        self.btnEliminarNormal = QPushButton("🗑️ Eliminar")
        self.btnGenerarPDF = QPushButton("📄 Generar PDF del día")
        layout_btns_n.addWidget(self.btnActualizar)
        layout_btns_n.addWidget(self.btnEliminarNormal)
        layout_btns_n.addWidget(self.btnGenerarPDF)
        layout_normales.addLayout(layout_btns_n)
        layout_normales.addWidget(self.tblNormales)
        self.tabNormales.setLayout(layout_normales)

        self.tabClientes = QWidget()
        layout_clientes = QVBoxLayout()
        self.tblClientes = QTableWidget()
        self.tblClientes.setColumnCount(8)
        self.tblClientes.setHorizontalHeaderLabels(["ID","Cliente","Sabor","Tamaño","Cantidad","Total","Sucursal","Fecha"])
        layout_btns_c = QHBoxLayout()
        self.btnEliminarCliente = QPushButton("🗑️ Eliminar")
        layout_btns_c.addWidget(self.btnEliminarCliente)
        layout_clientes.addLayout(layout_btns_c)
        layout_clientes.addWidget(self.tblClientes)
        self.tabClientes.setLayout(layout_clientes)

        self.tabs.addTab(self.tabNormales, "🍰 Pasteles Normales")
        self.tabs.addTab(self.tabClientes, "🧁 Pedidos de Clientes")

        layout_main = QVBoxLayout()
        layout_main.addWidget(self.tabs)
        self.centralwidget.setLayout(layout_main)
        MainWindow.setCentralWidget(self.centralwidget)
