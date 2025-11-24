from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog,
    QMessageBox, QTableWidgetItem
)
import sys
import db_api


class PartnerEditDialog(QDialog):
    def __init__(self, parent=None, partner_id=None):
        super().__init__(parent)
        uic.loadUi("partner_edit.ui", self)

        self.partner_id = partner_id

        for tid, name in db_api.fetch_partner_types():
            self.comboType.addItem(name, tid)

        if partner_id is not None:
            self.load_partner()

        self.buttonBox.accepted.connect(self.save)
        self.buttonBox.rejected.connect(self.reject)

    def load_partner(self):
        row = db_api.get_partner(self.partner_id)
        pid, type_id, name, director, email, tel, adres, inn, rating = row

        self.lineName.setText(name)
        self.lineDirector.setText(director)
        self.lineEmail.setText(email)
        self.linePhone.setText(tel)
        self.textAddress.setPlainText(adres)
        self.lineInn.setText(str(inn) if inn else "")
        self.spinRating.setValue(int(rating))

        for i in range(self.comboType.count()):
            if self.comboType.itemData(i) == type_id:
                self.comboType.setCurrentIndex(i)

    def save(self):
        name = self.lineName.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите наименование.")
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

        if self.partner_id is None:
            db_api.insert_partner(data)
        else:
            db_api.update_partner(self.partner_id, data)

        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main_window.ui", self)

        self.btnAdd.clicked.connect(self.add)
        self.btnEdit.clicked.connect(self.edit)
        self.btnDelete.clicked.connect(self.delete)
        self.btnRefresh.clicked.connect(self.load_partners)

        self.load_partners()

    def load_partners(self):
        rows = db_api.fetch_partners()
        self.tablePartners.setRowCount(len(rows))

        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.tablePartners.setItem(r, c, QTableWidgetItem(str(value)))

    def get_id(self):
        row = self.tablePartners.currentRow()
        if row < 0:
            return None
        return int(self.tablePartners.item(row, 0).text())

    def add(self):
        dlg = PartnerEditDialog(self)
        if dlg.exec():
            self.load_partners()

    def edit(self):
        pid = self.get_id()
        if not pid:
            QMessageBox.warning(self, "Ошибка", "Выберите строку.")
            return

        dlg = PartnerEditDialog(self, pid)
        if dlg.exec():
            self.load_partners()

    def delete(self):
        pid = self.get_id()
        if not pid:
            QMessageBox.warning(self, "Ошибка", "Выберите строку.")
            return

        db_api.delete_partner(pid)
        self.load_partners()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()