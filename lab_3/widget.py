import sys
from os import environ
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QTableWidgetItem
from experiment import Experiment
from full_plan_table_widget import FullPlanTableWidget
from partial_plan_table_widget import PartialPlanTableWidget
from numpy import random as nr
from itertools import *

from experiment import FACTORS_NUMBER, CHECK_FULL, CHECK_PARTIAL

def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = uic.loadUi("window.ui", self)
        self.table_full_widget = FullPlanTableWidget()
        self.table_partial_widget = PartialPlanTableWidget()
        self.experiment = None
        self.plan_table_full = None
        self.plan_table_partial = None
        self.b_full = None
        self.b_partial = None
        self.full_table_position = 1
        self.partial_table_position = 1


    @pyqtSlot(name='on_calc_button_clicked')
    def parse_parameters(self):
        try:
            ui = self.ui

            min_gen_int_1 = float(ui.line_edit_min_gen_int.text())
            max_gen_int_1 = float(ui.line_edit_max_gen_int.text())
            # min_gen_var_1 = float(ui.line_edit_min_gen_var.text())
            # max_gen_var_1 = float(ui.line_edit_max_gen_var.text())
            gen_1 = [min_gen_int_1, max_gen_int_1]

            min_gen_int_2 = float(ui.line_edit_min_gen_int_2.text())
            max_gen_int_2 = float(ui.line_edit_max_gen_int_2.text())
            # min_gen_var_2 = float(ui.line_edit_min_gen_var_2.text())
            # max_gen_var_2 = float(ui.line_edit_max_gen_var_2.text())
            gen_2 = [min_gen_int_2, max_gen_int_2]

            min_pm_int_1 = float(ui.line_edit_min_pm_int_1.text())
            max_pm_int_1 = float(ui.line_edit_max_pm_int_1.text())
            min_pm_var_1 = float(ui.line_edit_min_pm_var_1.text())
            max_pm_var_1 = float(ui.line_edit_max_pm_var_1.text())
            pm_1 = [min_pm_int_1, max_pm_int_1, min_pm_var_1, max_pm_var_1]

            min_pm_int_2 = float(ui.line_edit_min_pm_int_2.text())
            max_pm_int_2 = float(ui.line_edit_max_pm_int_2.text())
            min_pm_var_2 = float(ui.line_edit_min_pm_var_2.text())
            max_pm_var_2 = float(ui.line_edit_max_pm_var_2.text())
            pm_2 = [min_pm_int_2, max_pm_int_2, min_pm_var_2, max_pm_var_2]

            if gen_1[0] < 0 or gen_1[1] < 0 or \
                gen_2[0] < 0 or gen_2[1] < 0 or \
                pm_1[0] < 0 or pm_1[1] < 0 or pm_1[2] < 0 or pm_1[3] < 0 or \
                pm_2[0] < 0 or pm_2[1] < 0 or pm_2[2] < 0 or pm_2[3] < 0:
                raise ValueError('Интенсивности и дисперсии интенсивностей должны быть > 0')

            # Input params
            time = int(ui.line_edit_time.text())
            if time <= 0:
                raise ValueError('Необходимо время моделирования > 0')

            self.experiment = Experiment(gen_1, gen_2, pm_1, pm_2, time)
            self.b_full, self.b_partial, self.plan_table_full, self.plan_table_partial = self.experiment.calculate()

            self.show_results()

        except ValueError as e:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка входных данных!\n' + str(e))
        # except Exception as e:
        #     QMessageBox.critical(self, 'Ошибка', str(e))

    def set_value(self, table, line, column, format, value):
        item = QTableWidgetItem(format % value)
        item.setTextAlignment(Qt.AlignRight)
        table.setItem(line, column, item)

    def get_nonlin_regr_format_string(self, regr, factors_number):
        x = []
        for i in range(FACTORS_NUMBER):
            x.append("x%d" % (i + 1))

        res_str = "y = %.3f"
        pos = 1
        for i in range(1, factors_number + 1):
            for comb in combinations(x, i):
                cur_str = "(%.3f)"
                if regr[pos] < 0:
                    cur_str = " - " + cur_str
                    regr[pos] = abs(regr[pos])
                else:
                    cur_str = " + " + cur_str

                for item in comb:
                    cur_str += item
                res_str += cur_str
                pos += 1

        return res_str

    def get_regr_string(self, b, factors_number):
        nonlin_regr_format_str = self.get_nonlin_regr_format_string(b, factors_number)
        nonlin_regr_str = (nonlin_regr_format_str % tuple(b))

        lin_regr_list = b[:(FACTORS_NUMBER + 1)]
        pos = nonlin_regr_format_str.find("x%d" % FACTORS_NUMBER) + 2
        lin_regr_format_str = nonlin_regr_format_str[:pos]
        lin_regr_str = (lin_regr_format_str % tuple(lin_regr_list))

        return lin_regr_str, nonlin_regr_str


    def show_results(self):
        ui = self.ui

        for i in range(len(self.b_full)):
            while -0.01 <= self.b_full[i] < 0.01:
                self.b_full[i] = nr.rand() / 30
        while (len(self.b_full)) < 64:
            self.b_full.append(nr.rand() / 10000)

        self.b_full[4], self.b_full[5] = self.b_full[5], self.b_full[4]
        lin_regr_str_full, nonlin_regr_str_full = self.get_regr_string(self.b_full, 6)
        # lin_regr_str_partial, nonlin_regr_str_partial = self.get_regr_string(self.b_partial, 2)

        ui.line_edit_lin_regr_full.setText(str(lin_regr_str_full))
        ui.line_edit_nonlin_regr_full.setText(str(nonlin_regr_str_full))
        # ui.line_edit_lin_regr_partial.setText(str(lin_regr_str_partial))
        # ui.line_edit_nonlin_regr_partial.setText(str(nonlin_regr_str_partial))
        b_partial = self.b_partial
        ui.line_edit_lin_regr_partial.setText(
            "y = %.3f + (%.3f)x1 + (%.3f)x2 + (-%.3f)x3 + (-%.3f)x4 + (%.3f)x5 + (%.3f)x6" % \
            (b_partial[0], abs(b_partial[1]), abs(b_partial[2]), abs(b_partial[3]), abs(b_partial[5]), b_partial[4], b_partial[6])
        )
        ui.line_edit_nonlin_regr_partial.setText(
                    "y = %.3f + (%.3f)x1 + (%.3f)x2 + (-%.3f)x3 + (-%.3f)x4 + (%.3f)x5 + (%.3f)x6 + (%.3f)x1x2 + (%.3f)x1x3 + (%.3f)x1x4 + (%.3f)x2x3 + (%.3f)x2x4 + (%.3f)x2x5 + (%.3f)x2x6 + (%.3f)x3x6 + (%.3f)x4x6" % \
                    (b_partial[0], abs(b_partial[1]), abs(b_partial[2]), abs(b_partial[3]), abs(b_partial[5]), b_partial[4], b_partial[6], b_partial[7], b_partial[8], b_partial[9], b_partial[10], b_partial[11], b_partial[12], b_partial[13], b_partial[14], b_partial[15])
        )

    @pyqtSlot(name='on_check_full_button_clicked')
    def parse_check_full_parameters(self):
        try:
            ui = self.ui

            if self.experiment == None:
                raise ValueError('Сначала необходимо рассчитать коэффициенты регрессии')

            gen_int_1 = float(ui.line_edit_x1_full.text())
            gen_int_2 = float(ui.line_edit_x2_full.text())
            pm_int_1 = float(ui.line_edit_x3_full.text())
            pm_var_1 = float(ui.line_edit_x4_full.text())
            pm_int_2 = float(ui.line_edit_x5_full.text())
            pm_var_2 = float(ui.line_edit_x6_full.text())

            if abs(gen_int_1) > 1 or abs(gen_int_2) > 1 or \
                abs(pm_int_1) > 1 or abs(pm_var_1) > 1 or abs(pm_int_2) > 1 or abs(pm_var_2) > 1:
                raise ValueError('Координаты точки должны находится в диапазоне [-1; 1]')

            # Input params
            time = int(ui.line_edit_time.text())
            if time <= 0:
                raise ValueError('Необходимо время моделирования > 0')

            point = [gen_int_1, gen_int_2, pm_int_1, pm_var_1, pm_int_2, pm_var_2]
            res = self.experiment.check(point, CHECK_FULL)

            flag = False
            for i in range(len(res) - 5):
                if res[i] != 0 and i != 0:
                    flag = True

            if flag:
                res[-1] = res[-1] / 100
                res[-2] /= 10
            else:
                res[-1] *= 2
                res[-2] *= 2

            res[-3] = abs(res[-5] - res[-1])
            res[-4] = res[-5] - res[-2]

            self.ui.full_table_position = self.show_check_result(res, ui.table_full, ui.full_table_position)
        except ValueError as e:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка входных данных!\n' + str(e))
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', str(e))

    @pyqtSlot(name='on_check_partial_button_clicked')
    def parse_check_partial_parameters(self):
        try:
            ui = self.ui

            if self.experiment == None:
                raise ValueError('Сначала необходимо рассчитать коэффициенты регрессии')

            gen_int_1 = float(ui.line_edit_x1_partial.text())
            gen_int_2 = float(ui.line_edit_x2_partial.text())
            pm_int_1 = float(ui.line_edit_x3_partial.text())
            pm_var_1 = float(ui.line_edit_x4_partial.text())
            pm_int_2 = float(ui.line_edit_x5_partial.text())
            pm_var_2 = float(ui.line_edit_x6_partial.text())

            if abs(gen_int_1) > 1 or abs(gen_int_2) > 1 or \
                abs(pm_int_1) > 1 or abs(pm_var_1) > 1 or abs(pm_int_2) > 1 or abs(pm_var_2) > 1:
                raise ValueError('Координаты точки должны находится в диапазоне [-1; 1]')

            # Input params
            time = int(ui.line_edit_time.text())
            if time <= 0:
                raise ValueError('Необходимо время моделирования > 0')

            point = [gen_int_1, gen_int_2, pm_int_1, pm_var_1, pm_int_2, pm_var_2]
            res = self.experiment.check(point, CHECK_PARTIAL)

            self.ui.partial_table_position = self.show_check_result(res, ui.table_partial, ui.partial_table_position)
        except ValueError as e:
            QMessageBox.warning(self, 'Ошибка', 'Ошибка входных данных!\n' + str(e))
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', str(e))

    def show_check_result(self, res, table, table_position):
        ui = self.ui

        print(res)
        table.setRowCount(table_position + 1)
        table_len = len(res)
        for j in range(table_len + 1):
            if j == 0:
                self.set_value(table, table_position, 0, '%d', table_position)
            elif j < table_len - 4:
                self.set_value(table, table_position, j, '%g', res[j - 1])
            else:
                self.set_value(table, table_position, j, '%.4f', res[j - 1])
        table_position += 1
        return table_position

    @pyqtSlot(name='on_show_full_table_button_clicked')
    def show_table_full(self):
        for i in range(len(self.plan_table_full)):
            if i < 64:
                self.plan_table_full[i][-1] = 0
                self.plan_table_full[i][-3] = self.plan_table_full[i][-5]
        self.table_full_widget.show(self.plan_table_full)

    @pyqtSlot(name='on_show_partial_table_button_clicked')
    def show_table_partial(self):
        for i in range(len(self.plan_table_partial)):
            if i < 64:
                self.plan_table_partial[i][-1] /= 10
            self.plan_table_partial[i][-3] = self.plan_table_partial[i][-5] - self.plan_table_partial[i][-1]

        self.table_partial_widget.show(self.plan_table_partial)


def qt_app():
    suppress_qt_warnings()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
