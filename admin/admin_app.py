from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PySide6.QtCore import Qt
from ui_main import Ui_MainWindow
from database import get_conn_normales, get_conn_clientes
import sys
from reportes import generar_pdf_dia

class AdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Mi Pastel — Administración")

        self.ui.btnActualizar.clicked.connect(self.cargar_datos)
        self.ui.btnGenerarPDF.clicked.connect(self.generar_pdf)
        self.ui.btnEliminarNormal.clicked.connect(self.eliminar_normal)
        self.ui.btnEliminarCliente.clicked.connect(self.eliminar_cliente)

        self.cargar_datos()

    def cargar_datos(self):
        conn = get_conn_normales()
        cur = conn.cursor()
        cur.execute("SELECT id_pastel, sabor, tamaño, precio, cantidad, sucursal, fecha_pedido FROM PastelesNormales")
        normales = cur.fetchall()
        conn.close()
        self.ui.tblNormales.setRowCount(len(normales))
        for i, row in enumerate(normales):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.ui.tblNormales.setItem(i, j, item)

        conn = get_conn_clientes()
        cur = conn.cursor()
        cur.execute("SELECT id_pedido_cliente, nombre_cliente, sabor, tamaño, cantidad, total, sucursal, fecha_pedido FROM PastelesClientes")
        clientes = cur.fetchall()
        conn.close()
        self.ui.tblClientes.setRowCount(len(clientes))
        for i, row in enumerate(clientes):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.ui.tblClientes.setItem(i, j, item)

    def generar_pdf(self):
        generar_pdf_dia()
        QMessageBox.information(self, "Éxito", "Lista del día generada en PDF.")

    def eliminar_normal(self):
        fila = self.ui.tblNormales.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Selecciona un pedido normal.")
            return
        id_pastel = self.ui.tblNormales.item(fila, 0).text()
        conn = get_conn_normales()
        cur = conn.cursor()
        cur.execute("DELETE FROM PastelesNormales WHERE id_pastel = ?", (id_pastel,))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Eliminado", "Pedido normal eliminado.")
        self.cargar_datos()

    def eliminar_cliente(self):
        fila = self.ui.tblClientes.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Selecciona un pedido de cliente.")
            return
        id_pedido = self.ui.tblClientes.item(fila, 0).text()
        conn = get_conn_clientes()
        cur = conn.cursor()
        cur.execute("DELETE FROM PastelesClientes WHERE id_pedido_cliente = ?", (id_pedido,))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Eliminado", "Pedido de cliente eliminado.")
        self.cargar_datos()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminApp()
    window.show()
    sys.exit(app.exec())
