import sys
from abc import ABC, abstractmethod
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QLineEdit, QListWidget, QProgressBar, QComboBox, QCheckBox,
    QStatusBar, QVBoxLayout, QHBoxLayout, QMessageBox
)


class MyMap:
    def __init__(self):
        self._pairs = []

    def put(self, key, value):
        for i, (k, _) in enumerate(self._pairs):
            if k == key:
                self._pairs[i] = (key, value)
                return
        self._pairs.append((key, value))

    def get(self, key):
        for k, v in self._pairs:
            if k == key:
                return v
        return None


class AbstractEntity(ABC):
    @abstractmethod
    def show_info(self):
        pass


class Item(AbstractEntity):
    def __init__(self, name: str, cost: float, warehouse: str):
        self._name = name
        self._cost = float(cost)
        self._warehouse = warehouse

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = str(val)

    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, val):
        self._cost = float(val)

    @property
    def warehouse(self):
        return self._warehouse

    @warehouse.setter
    def warehouse(self, val):
        self._warehouse = str(val)

    def show_info(self):
        return f"{self._name} [{self._warehouse}] — {self._cost:.0f} руб."

    def __str__(self):
        return self.show_info()

    def __repr__(self):
        return f"Item('{self._name}', {self._cost}, '{self._warehouse}')"

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return self._cost == other.cost and self._name == other.name

    def __lt__(self, other):
        return self._cost < other.cost

    def __len__(self):
        return len(self._name)

    def __add__(self, other):
        return self._cost + (other.cost if isinstance(other, Item) else float(other))


class Reporter:
    start_time = datetime.now()

    @staticmethod
    def write_log(user="UserName"):
        t_fmt = "%d.%m.%Y %H:%M:%S"
        t_in = Reporter.start_time.strftime(t_fmt)
        t_out = datetime.now().strftime(t_fmt)

        report = (
            "+\n+\n"
            "| login | time_in | time_out |\n"
            f"|{user} | {t_in} | {t_out}\n"
            "+\n+\n"
        )
        with open("report.txt", "w", encoding="utf-8") as f:
            f.write(report)


class UIWindow(QMainWindow):
    def closeEvent(self, event):
        Reporter.write_log()
        event.accept()

class UIPanel(QWidget):
    def __init__(self):
        super().__init__()

class UILabel(QLabel):
    def setText(self, text):
        super().setText(f"Раздел: {text}")

class UIButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setMinimumHeight(30)

class UIInput(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)

class UIList(QListWidget):
    def __init__(self):
        super().__init__()

class UICheck(QCheckBox):
    def __init__(self, text):
        super().__init__(text)

class UICombo(QComboBox):
    def __init__(self, items):
        super().__init__()
        self.addItems(items)

class UIProgress(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setMaximum(20)
        self.setFormat("Заполнено мест на складе: %v из %m")

class UIStatusBar(QStatusBar):
    def showMessage(self, msg, timeout=0):
        super().showMessage(f"Итог: {msg}", timeout)


class App(UIWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учет оборудования")
        self.resize(480, 560)
        self.sort_ascending = True
        self.displayed_items = []

        self.settings = MyMap()
        self.settings.put("all", "Все склады")
        self.settings.put("main", "Главный склад")
        self.settings.put("branch", "Филиал")

        self.items = [
            Item("Сервер Dell", 145000, "Главный склад"),
            Item("Офисная мышь", 1200, "Филиал"),
            Item("Ноутбук Lenovo", 68000, "Главный склад"),
            Item("Клавиатура", 3500, "Филиал"),
            Item("Монитор 27\"", 24000, "Главный склад"),
            Item("Веб-камера", 4200, "Филиал"),
            Item("Принтер Kyocera", 32000, "Главный склад"),
            Item("Маршрутизатор", 7500, "Филиал"),
            Item("ИБП APC", 19000, "Главный склад"),
            Item("Гарнитура", 2800, "Филиал")
        ]

        self.setup_ui()
        self.render_items()

    def setup_ui(self):
        container = UIPanel()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)

        self.label = UILabel()
        self.label.setText(self.settings.get("all"))

        input_row = QHBoxLayout()
        self.name_input = UIInput("Название техники...")
        self.cost_input = UIInput("Цена (руб.)...")
        self.name_input.returnPressed.connect(self.add_item)
        self.cost_input.returnPressed.connect(self.add_item)
        input_row.addWidget(self.name_input)
        input_row.addWidget(self.cost_input)

        btn_row = QHBoxLayout()
        self.add_btn = UIButton("Добавить")
        self.add_btn.clicked.connect(self.add_item)

        self.sort_btn = UIButton("Сортировать по цене")
        self.sort_btn.clicked.connect(self.sort_data)

        self.del_btn = UIButton("Удалить выбранное")
        self.del_btn.clicked.connect(self.delete_item)

        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.sort_btn)
        btn_row.addWidget(self.del_btn)

        self.list_widget = UIList()

        filter_row = QHBoxLayout()
        self.combo_box = UICombo([
            self.settings.get("all"),
            self.settings.get("main"),
            self.settings.get("branch")
        ])
        self.combo_box.currentTextChanged.connect(self.render_items)

        self.check_box = UICheck("Только дороже 10 000 руб.")
        self.check_box.stateChanged.connect(self.render_items)

        filter_row.addWidget(self.combo_box)
        filter_row.addWidget(self.check_box)

        self.progress = UIProgress()
        self.status = UIStatusBar()
        self.setStatusBar(self.status)

        layout.addWidget(self.label)
        layout.addLayout(input_row)
        layout.addLayout(btn_row)
        layout.addWidget(self.list_widget)
        layout.addLayout(filter_row)
        layout.addWidget(self.progress)

    def render_items(self):
        selected_warehouse = self.combo_box.currentText()
        only_expensive = self.check_box.isChecked()

        self.label.setText(selected_warehouse)
        self.list_widget.clear()
        self.displayed_items = []
        total_sum = 0.0

        for item in self.items:
            if selected_warehouse != self.settings.get("all") and item.warehouse != selected_warehouse:
                continue
            if only_expensive and item.cost <= 10000:
                continue

            self.displayed_items.append(item)
            self.list_widget.addItem(str(item))
            total_sum = item + total_sum

        self.progress.setValue(min(len(self.items), 20))
        self.status.showMessage(f"показано {len(self.displayed_items)} шт. на сумму {total_sum:,.0f} руб.".replace(",", " "))

    def add_item(self):
        name = self.name_input.text().strip()
        cost_str = self.cost_input.text().strip()

        if not name or not cost_str:
            QMessageBox.warning(self, "Внимание", "Введите название и цену устройства.")
            return

        try:
            cost = float(cost_str)
            if cost < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Цена должна быть положительным числом.")
            return

        current_filter = self.combo_box.currentText()
        target_warehouse = current_filter if current_filter != self.settings.get("all") else self.settings.get("main")

        new_item = Item(name, cost, target_warehouse)
        self.items.append(new_item)

        self.name_input.clear()
        self.cost_input.clear()
        self.render_items()

    def delete_item(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QMessageBox.information(self, "Удаление", "Сначала выберите строку в списке.")
            return

        item_to_remove = self.displayed_items[row]
        self.items.remove(item_to_remove)
        self.render_items()

    def sort_data(self):
        self.items.sort(reverse=not self.sort_ascending)
        direction = "возрастанию" if self.sort_ascending else "убыванию"
        self.sort_btn.setText(f"Цена: по {direction}")
        self.sort_ascending = not self.sort_ascending
        self.render_items()


class Runner:
    @staticmethod
    def start():
        app = QApplication(sys.argv)
        win = App()
        win.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    Runner.start()