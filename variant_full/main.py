from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog,
    QMessageBox, QTableWidgetItem,
    QVBoxLayout, QTableWidget
)
import sys
import db_api


class PartnerEditDialog(QDialog):
    def __init__(self, parent=None, partner_id=None):
        super().__init__(parent)
        uic.loadUi("partner_edit.ui", self)

        self.partner_id = partner_id

        types = db_api.fetch_partner_types()
        for tid, name in types:
            self.comboType.addItem(name, tid)

        if partner_id is not None:
            self.load_partner()

        self.buttonBox.accepted.connect(self.on_save)
        self.buttonBox.rejected.connect(self.reject)

    def load_partner(self):
        row = db_api.get_partner(self.partner_id)
        pid, type_id, name, director, email, tel, adres, inn, rating = row

        self.lineName.setText(name or "")
        self.lineDirector.setText(director or "")
        self.lineEmail.setText(email or "")
        self.linePhone.setText(tel or "")
        self.textAddress.setPlainText(adres or "")
        self.lineInn.setText(str(inn) if inn else "")
        self.spinRating.setValue(int(rating or 0))

        for i in range(self.comboType.count()):
            if self.comboType.itemData(i) == type_id:
                self.comboType.setCurrentIndex(i)
                break

    def on_save(self):
        name = self.lineName.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Наименование обязательно.")
            return

        inn_text = self.lineInn.text().strip()
        inn = int(inn_text) if inn_text.isdigit() else None

        data = {
            "type_id": self.comboType.currentData(),
            "name_partner": name,
            "director": self.lineDirector.text(),
            "email": self.lineEmail.text(),
            "tel": self.linePhone.text(),
            "adres": self.textAddress.toPlainText(),
            "inn": inn,
            "rating": self.spinRating.value()
        }

        try:
            if self.partner_id is None:
                db_api.insert_partner(data)
            else:
                db_api.update_partner(self.partner_id, data)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))
            return

        self.accept()


class HistoryDialog(QDialog):
    def __init__(self, parent=None, partner_id=None, partner_name=""):
        super().__init__(parent)
        self.setWindowTitle(f"История продаж: {partner_name}")
        self.resize(600, 400)

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(
            ["Дата", "Продукция", "Количество"]
        )

        if partner_id is not None:
            self.load_data(partner_id)

    def load_data(self, partner_id):
        rows = db_api.fetch_sales_history(partner_id)
        self.table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            date, product, qty = row
            self.table.setItem(r, 0, QTableWidgetItem(str(date)))
            self.table.setItem(r, 1, QTableWidgetItem(product))
            self.table.setItem(r, 2, QTableWidgetItem(str(qty)))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main_window.ui", self)

        self.btnAdd.clicked.connect(self.on_add)
        self.btnEdit.clicked.connect(self.on_edit)
        self.btnDelete.clicked.connect(self.on_delete)
        self.btnRefresh.clicked.connect(self.load_partners)
        self.btnHistory.clicked.connect(self.on_history)

        self.load_partners()

    def load_partners(self):
        rows = db_api.fetch_partners()
        self.tablePartners.setRowCount(len(rows))

        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                self.tablePartners.setItem(r, c, QTableWidgetItem(str(v)))

    def get_selected_id(self):
        row = self.tablePartners.currentRow()
        if row < 0:
            return None
        return int(self.tablePartners.item(row, 0).text())

    def on_add(self):
        dlg = PartnerEditDialog(self)
        if dlg.exec():
            self.load_partners()

    def on_edit(self):
        pid = self.get_selected_id()
        if pid is None:
            QMessageBox.warning(self, "Ошибка", "Выберите партнера.")
            return
        dlg = PartnerEditDialog(self, partner_id=pid)
        if dlg.exec():
            self.load_partners()

    def on_delete(self):
        pid = self.get_selected_id()
        if pid is None:
            QMessageBox.warning(self, "Ошибка", "Выберите партнера.")
            return
        reply = QMessageBox.question(
            self, "Удаление", "Удалить запись?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            db_api.delete_partner(pid)
            self.load_partners()

    def on_history(self):
        pid = self.get_selected_id()
        if pid is None:
            QMessageBox.warning(self, "Ошибка", "Выберите партнера.")
            return
        name = self.tablePartners.item(self.tablePartners.currentRow(), 2).text()
        dlg = HistoryDialog(self, partner_id=pid, partner_name=name)
        dlg.exec()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()