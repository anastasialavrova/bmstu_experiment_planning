from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from PyQt5.QtCore import Qt

class PlanTableWidget(QDialog):
    def __init__(self, ui):
        super().__init__()
        self.ui = uic.loadUi(ui, self)

        self.btn_close.clicked.connect(self.close)
    
    def set_value(self, table, line, column, format, value):
        item = QTableWidgetItem(format % value)
        item.setTextAlignment(Qt.AlignRight)
        table.setItem(line, column, item)

    def show(self, table):
        ui = self.ui

        ui.plan_table.setRowCount(1)
        ui.Table_position = 1

        for i in range(len(table)):            
            self.plan_table.setRowCount(ui.Table_position + 1)
            table_len = len(table[i])
            for j in range(table_len + 1):
                if j == 0:
                    self.set_value(ui.plan_table, ui.Table_position, 0, '%d', ui.Table_position)
                elif j < table_len - 4:
                    self.set_value(ui.plan_table, ui.Table_position, j, '%d', table[i][j - 1])
                else:
                    self.set_value(ui.plan_table, ui.Table_position, j, '%.4f', table[i][j - 1])
            ui.Table_position += 1

        super().show()
