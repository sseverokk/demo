from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QMessageBox, QTableWidgetItem
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
            self._load_partner()

        self.buttonBox.accepted.connect(self.on_save)
        self.buttonBox.rejected.connect(self.reject)

    def _load_partner(self):
        row = db_api.get_partner(self.partner_id)
        pid, type_id, name, director, email, tel, adres, inn, rating = row

        self.lineName.setText(name or "")
        self.lineDirector.setText(director or "")
        self.lineEmail.setText(email or "")
        self.linePhone.setText(tel or "")
        self.textAddress.setPlainText(adres or "")
        self.lineInn.setText(str(inn) if inn is not None else "")
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

        data = {
            "type_id": self.comboType.currentData(),
            "name_partner": name,
            "director": self.lineDirector.text(),
            "email": self.lineEmail.text(),
            "tel": self.linePhone.text(),
            "adres": self.textAddress.toPlainText(),
            "inn": int(self.lineInn.text()) if self.lineInn.text().isdigit() else None,
            "rating": self.spinRating.value()
        }

        try:
            if self.partner_id is None:
                db_api.insert_partner(data)
            else:
                db_api.update_partner(self.partner_id, data)
        except Exception as e:
            text = str(e)
            if "unique constraint" in text or "duplicate key value" in text:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Партнёр с таким наименованием уже существует."
                )
            else:
                QMessageBox.critical(self, "Ошибка БД", text)
            return

        self.accept()


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
            for c, value in enumerate(row):
                self.tablePartners.setItem(r, c, QTableWidgetItem(str(value)))

    def get_selected_partner_id(self):
        row = self.tablePartners.currentRow()
        if row < 0:
            return None
        return int(self.tablePartners.item(row, 0).text())

    def on_add(self):
        dlg = PartnerEditDialog(self)
        if dlg.exec():
            self.load_partners()

    def on_edit(self):
        pid = self.get_selected_partner_id()
        if pid is None:
            QMessageBox.warning(self, "Ошибка", "Выберите партнёра.")
            return
        dlg = PartnerEditDialog(self, partner_id=pid)
        if dlg.exec():
            self.load_partners()

    def on_delete(self):
        pid = self.get_selected_partner_id()
        if pid is None:
            QMessageBox.warning(self, "Ошибка", "Выберите партнёра.")
            return

        reply = QMessageBox.question(
            self,
            "Удаление",
            "Удалить выбранного партнёра?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            db_api.delete_partner(pid)
            self.load_partners()

    def on_history(self):
        QMessageBox.information(
            self,
            "История продаж",
            "Модуль истории продаж пока не реализован."
        )


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()