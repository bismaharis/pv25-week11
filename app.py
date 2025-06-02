import sys
import sqlite3
import csv
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem,
    QMessageBox, QFileDialog, QTabWidget, QLabel, QDockWidget, QLineEdit, QVBoxLayout
)
from PyQt5.QtGui import QFont, QColor, QClipboard
from PyQt5.QtCore import Qt

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("manajemenBuku.ui", self)
        self.setWindowTitle("Manajemen Buku")
        self.statusbar.showMessage("Lalu Bisma Kurniawan Haris | F1D022055")

        self.labelJudul.setFont(QFont("Arial", 16, QFont.Bold))
        self.labelJudul.setStyleSheet("color: #091F51;")
        self.labelNama.setFont(QFont("Arial", 10, QFont.StyleItalic))
        self.labelNama.setStyleSheet("color: #333333;")
        self.labelNama.setText("Lalu Bisma Kurniawan Haris | F1D022055")

        self.inputJudul.setPlaceholderText("Masukkan Judul Buku...")
        self.inputJudul.setStyleSheet("QLineEdit { color: #555555; } QLineEdit:focus { color: black; }")
        self.inputPengarang.setPlaceholderText("Masukkan Nama Pengarang...")
        self.inputPengarang.setStyleSheet("QLineEdit { color: #555555; } QLineEdit:focus { color: black; }")
        self.inputTahun.setPlaceholderText("Masukkan Tahun Terbit...")
        self.inputTahun.setStyleSheet("QLineEdit { color: #555555; } QLineEdit:focus { color: black; }")

        button_style = "QPushButton { background-color: #091F51; color: white; border-radius: 5px; padding: 5px; }" \
                       "QPushButton:hover { background-color: #1A3C7A; }" \
                       "QPushButton:pressed { background-color: #0A2759; }"
        self.btnSimpan.setStyleSheet(button_style)
        self.btnHapus.setStyleSheet(button_style)
        self.btnExportCSV.setStyleSheet(button_style)
        self.btnPasteClipboard.setStyleSheet(button_style)

        layout = QVBoxLayout(self.dockWidgetContents_2)
        layout.addWidget(self.lineCari)
        self.dockWidgetContents_2.setLayout(layout)

        self.dockSearch.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        self.dockSearch.setWindowTitle("Search Bar")
        self.lineCari.setPlaceholderText("Cari...")
        self.lineCari.setStyleSheet("QLineEdit { color: #555555; } QLineEdit:focus { color: black; }")
        self.addDockWidget(Qt.TopDockWidgetArea, self.dockSearch)
        self.lineCari.textChanged.connect(self.cariData)
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.initDB()
        self.loadData()

        self.btnSimpan.clicked.connect(self.simpanData)
        self.btnHapus.clicked.connect(self.hapusData)
        self.btnExportCSV.clicked.connect(self.eksporCSV)
        self.btnPasteClipboard.clicked.connect(self.pasteTeks)
        self.tableWidget.itemDoubleClicked.connect(self.editData)

        self.actionSimpan.triggered.connect(self.simpanData)
        self.actionExport_CSV.triggered.connect(self.eksporCSV)
        self.actionKeluar.triggered.connect(self.close)
        self.actionCari_Data.triggered.connect(self.focusCari)
        self.actionHapus_Data.triggered.connect(self.hapusData)

    def initDB(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS buku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT,
                pengarang TEXT,
                tahun INTEGER
            )
        """)
        self.conn.commit()

    def loadData(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        for row_index, row_data in enumerate(self.c.execute("SELECT * FROM buku")):
            self.tableWidget.insertRow(row_index)
            for col_index, col_data in enumerate(row_data):
                self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))

    def simpanData(self):
        judul = self.inputJudul.text()
        pengarang = self.inputPengarang.text()
        tahun = self.inputTahun.text()

        if not (judul and pengarang and tahun.isdigit()):
            QMessageBox.warning(self, "Error", "Harap isi semua field dengan benar.")
            return

        self.c.execute("INSERT INTO buku (judul, pengarang, tahun) VALUES (?, ?, ?)",
                       (judul, pengarang, int(tahun)))
        self.conn.commit()
        self.inputJudul.clear()
        self.inputPengarang.clear()
        self.inputTahun.clear()
        self.loadData()

    def hapusData(self):
        selected = self.tableWidget.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data yang dipilih!")
            return

        reply = QMessageBox.question(
            self, 
            "Konfirmasi", 
            "Yakin ingin menghapus data ini?", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        id_item = self.tableWidget.item(selected, 0).text()
        self.c.execute("DELETE FROM buku WHERE id = ?", (id_item,))
        self.conn.commit()
        self.loadData()
        QMessageBox.information(self, "Sukses", "Data berhasil dihapus.")

    def editData(self, item):
        row = item.row()
        id_data = self.tableWidget.item(row, 0).text()
        judul = self.tableWidget.item(row, 1).text()
        pengarang = self.tableWidget.item(row, 2).text()
        tahun = self.tableWidget.item(row, 3).text()

        self.inputJudul.setText(judul)
        self.inputPengarang.setText(pengarang)
        self.inputTahun.setText(tahun)

        self.c.execute("DELETE FROM buku WHERE id = ?", (id_data,))
        self.conn.commit()
        self.loadData()

    def cariData(self, text):
        for i in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(i, 1)  
            self.tableWidget.setRowHidden(i, text.lower() not in item.text().lower())

    def focusCari(self):
        self.lineCari.setFocus()
        self.lineCari.selectAll()
        if not self.dockSearch.isVisible():
            self.dockSearch.show()

    def pasteTeks(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.inputJudul.setText(text)
        else:
            QMessageBox.warning(self, "Peringatan", "Tidak ada teks di clipboard!")

    def eksporCSV(self):
        if self.tableWidget.rowCount() == 0:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data untuk diekspor!")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", "", "CSV Files (*.csv)")
        if filename:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                header = ["ID", "Judul", "Pengarang", "Tahun"]
                writer.writerow(header)

                for row in range(self.tableWidget.rowCount()):
                    rowdata = []
                    for col in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, col)
                        rowdata.append(item.text() if item else "")
                    writer.writerow(rowdata)
            QMessageBox.information(self, "Sukses", "Data berhasil diekspor.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())