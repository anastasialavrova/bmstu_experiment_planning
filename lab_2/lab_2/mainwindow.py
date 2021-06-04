from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from experiment_math import *
from model import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.show()
        self.almost_zero = 1e-10
        self.btn_do_plan.clicked.connect(self.do_plan)
        self.btn_set1.clicked.connect(self.set1)
        self.btn_set2.clicked.connect(self.set2)
        self.btn_set3.clicked.connect(self.set3)
        self.table_plan.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_plan.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.plan = matrix_plan()
        self.custom_plan = [list() for i in range(3)]
        for i in range(len(self.plan)):
            for j in range(len(self.plan[i])):
                self.table_plan.setItem(i + 1, j + 1, QTableWidgetItem(str(round(self.plan[i][j], 3))))

    def get_factor(self, entry):
        try:
            res = float(entry.text())
        except ValueError:
            entry.setStyleSheet("background:#f88;")
            raise ValueError()

        entry.setStyleSheet("background:#fff;")

        if abs(res) < self.almost_zero:
            res = self.almost_zero

        return res

    @staticmethod
    def get_custom_factor(entry):
        try:
            res = float(entry.text())
            if not -1 <= res <= 1:
                raise ValueError()
            if res.is_integer():
                res = int(res)
        except ValueError:
            entry.setStyleSheet("background:#f88;")
            raise ValueError()

        entry.setStyleSheet("background:#fff;")
        return res

    def do_plan(self):
        self.plan = matrix_plan()
        self.xmat = calc_xmat(self.plan)
        total_apps = 10000
        try:
            gen_int_min = self.get_factor(self.entry_gen_int_min)
            gen_int_max = self.get_factor(self.entry_gen_int_max)
            proc_int_min = self.get_factor(self.entry_proc_int_min)
            proc_int_max = self.get_factor(self.entry_proc_int_max)
            proc_dev_min = self.get_factor(self.entry_proc_dev_min)
            proc_dev_max = self.get_factor(self.entry_proc_dev_max)
        except ValueError:
            pass
        else:
            y = list()
            # for each experiment
            for exp in self.plan:
                print(exp)
                gen_int = scale_factor(exp[1], gen_int_min, gen_int_max)
                proc_int = scale_factor(exp[2], proc_int_min, proc_int_max)
                proc_dev = scale_factor(exp[3], proc_dev_min, proc_dev_max)

                gens = [Generator(exp_by_intensity, (gen_int,))]
                proc = Generator(norm_by_intensity, (proc_int, proc_dev))
                model = EventModel(gens, proc, total_apps)

                y.append(model.proceed() / total_apps)

            for exp in self.custom_plan:
                if len(exp) > 0:
                    gen_int = scale_factor(exp[1], gen_int_min, gen_int_max)
                    proc_int = scale_factor(exp[2], proc_int_min, proc_int_max)
                    proc_dev = scale_factor(exp[3], proc_dev_min, proc_dev_max)

                    gens = [Generator(exp_by_intensity, (gen_int,))]
                    proc = Generator(norm_by_intensity, (proc_int, proc_dev))
                    model = EventModel(gens, proc, total_apps)

                    y.append(model.proceed() / total_apps)

            old_size = len(self.plan)
            self.plan, b = expand_plan(self.plan, self.custom_plan, y, self.xmat)

            for i in range(len(self.plan)):
                for j in range(old_size, len(self.plan[i])):
                    self.table_plan.setItem(i + 1, j + 1, QTableWidgetItem(str(round(self.plan[i][j], 3))))

            self.set_equasions(b)

    def set_equasions(self, b, accuracy=3):
        yl = str(round(b[0], accuracy)) + " + " + str(round(b[1], accuracy)) + "x1 + " + str(
            round(b[2], accuracy)) + "x2 + " + str(round(b[3], accuracy)) + "x3"
        yl = yl.replace("+ -", "- ")
        ynl = yl + " + " + str(round(b[4], accuracy)) + "x1x2 + " + str(round(b[5], accuracy)) + "x1x3 + " + str(
            round(b[6], accuracy)) + "x2x3 + " + str(round(b[7], accuracy)) + "x1x2x3"
        ynl = ynl.replace("+ -", "- ")
        self.label_yl.setText(yl)
        self.label_ynl.setText(ynl)

    def set1(self):
        try:
            x1 = self.get_custom_factor(self.entry_x1_1)
            x2 = self.get_custom_factor(self.entry_x2_1)
            x3 = self.get_custom_factor(self.entry_x3_1)
        except ValueError:
            pass
        else:
            item = QTableWidgetItem("9")
            item.setTextAlignment(Qt.AlignCenter)
            self.table_plan.setItem(9, 0, item)
            self.custom_plan[0] = [1, x1, x2, x3, x1 * x2, x1 * x3, x2 * x3, x1 * x2 * x3]
            for i in range(len(self.custom_plan[0])):
                self.table_plan.setItem(9, i + 1, QTableWidgetItem(str(self.custom_plan[0][i])))
            for i in range(len(self.custom_plan[0]) + 1, self.table_plan.columnCount()):
                self.table_plan.setItem(9, i, QTableWidgetItem(''))

    def set2(self):
        try:
            x1 = self.get_custom_factor(self.entry_x1_2)
            x2 = self.get_custom_factor(self.entry_x2_2)
            x3 = self.get_custom_factor(self.entry_x3_2)
        except ValueError:
            pass
        else:
            item = QTableWidgetItem("10")
            item.setTextAlignment(Qt.AlignCenter)
            self.table_plan.setItem(10, 0, item)
            self.custom_plan[1] = [1, x1, x2, x3, x1 * x2, x1 * x3, x2 * x3, x1 * x2 * x3]
            for i in range(len(self.custom_plan[1])):
                self.table_plan.setItem(10, i + 1, QTableWidgetItem(str(self.custom_plan[1][i])))
            for i in range(len(self.custom_plan[0]) + 1, self.table_plan.columnCount()):
                self.table_plan.setItem(10, i, QTableWidgetItem(''))


    def set3(self):
        try:
            x1 = self.get_custom_factor(self.entry_x1_3)
            x2 = self.get_custom_factor(self.entry_x2_3)
            x3 = self.get_custom_factor(self.entry_x3_3)
        except ValueError:
            pass
        else:
            item = QTableWidgetItem("11")
            item.setTextAlignment(Qt.AlignCenter)
            self.table_plan.setItem(11, 0, item)
            self.custom_plan[2] = [1, x1, x2, x3, x1 * x2, x1 * x3, x2 * x3, x1 * x2 * x3]
            for i in range(len(self.custom_plan[2])):
                self.table_plan.setItem(11, i + 1, QTableWidgetItem(str(self.custom_plan[2][i])))
            for i in range(len(self.custom_plan[0]) + 1, self.table_plan.columnCount()):
                self.table_plan.setItem(11, i, QTableWidgetItem(''))
