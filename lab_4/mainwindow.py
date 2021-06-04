from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from equationwindow import *
from experiment_math import *
from model import *
from validentry import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)

        self.plan = matrix_plan(6)
        self.custom_plan = [list()]

        self.btn_do_plan.clicked.connect(self.do_plan)
        self.btn_set.clicked.connect(self.set)
        self.btn_full.clicked.connect(self.show_full_equasion)

        self.b = list()
        self.equation_window = EquationWindow()

        n = calc_n(6)
        exp_amount = calc_exp_amount(6, n)
        self.label_length.setText(str(calc_star_length(n, exp_amount)))
        self.label_a.setText(str(calc_star_shift(n, exp_amount)))

        for i in range(1, calc_exp_amount(6, calc_n(6)) + 2):
            self.table_plan.setItem(i, 0, QTableWidgetItem(str(i)))
        self.fill_table()

        self.show()

    def get_factor(self, entry):
        almost_zero = 1e-10
        res = get_valid(entry, float, lambda val: False)

        if abs(res) < almost_zero:
            res = almost_zero

        return res

    def check_factors(self):
        passed = True
        n = calc_n(6)
        exp_amount = calc_exp_amount(6, n)
        entries = [
            [self.entry_gen1_int_min, self.entry_gen1_int_max],
            [self.entry_gen2_int_min, self.entry_gen2_int_max],
            [self.entry_proc1_int_min, self.entry_proc1_int_max],
            [self.entry_proc1_dev_min, self.entry_proc1_dev_max],
            [self.entry_proc2_int_min, self.entry_proc2_int_max],
            [self.entry_proc2_dev_min, self.entry_proc2_dev_max]
        ]
        for i in range(len(entries)):
            try:
                min_val = self.get_factor(entries[i][0])
                max_val = self.get_factor(entries[i][1])
                if -calc_star_length(n, exp_amount) < -1 - 2 * min_val / (max_val - min_val):
                    make_invalid(entries[i][0])
                    make_invalid(entries[i][1])
                    passed = False
                else:
                    make_valid(entries[i][0])
                    make_valid(entries[i][1])
            except ValueError:
                pass
        return passed

    def do_plan(self):
        if self.check_factors():
            self.plan = matrix_plan(6)
            total_apps = 10000
            try:
                gen1_int_min = self.get_factor(self.entry_gen1_int_min)
                gen1_int_max = self.get_factor(self.entry_gen1_int_max)
                gen2_int_min = self.get_factor(self.entry_gen2_int_min)
                gen2_int_max = self.get_factor(self.entry_gen2_int_max)
                proc1_int_min = self.get_factor(self.entry_proc1_int_min)
                proc1_int_max = self.get_factor(self.entry_proc1_int_max)
                proc1_dev_min = self.get_factor(self.entry_proc1_dev_min)
                proc1_dev_max = self.get_factor(self.entry_proc1_dev_max)
                proc2_int_min = self.get_factor(self.entry_proc2_int_min)
                proc2_int_max = self.get_factor(self.entry_proc2_int_max)
                proc2_dev_min = self.get_factor(self.entry_proc2_dev_min)
                proc2_dev_max = self.get_factor(self.entry_proc2_dev_max)
            except ValueError:
                pass
            else:
                y = list()
                # for each experiment
                for exp in self.plan:
                    gen_int1 = scale_factor(exp[1], gen1_int_min, gen1_int_max)
                    gen_int2 = scale_factor(exp[2], gen2_int_min, gen2_int_max)
                    proc_int1 = scale_factor(exp[3], proc1_int_min, proc1_int_max)
                    proc_dev1 = scale_factor(exp[4], proc1_dev_min, proc1_dev_max)
                    proc_int2 = scale_factor(exp[5], proc2_int_min, proc2_int_max)
                    proc_dev2 = scale_factor(exp[6], proc2_dev_min, proc2_dev_max)

                    gens = [Generator(exp_by_intensity, (gen_int1,)), Generator(exp_by_intensity, (gen_int2,))]
                    procs = [Generator(norm_by_intensity, (proc_int1, proc_dev1)),
                             Generator(norm_by_intensity, (proc_int2, proc_dev2))]
                    model = EventModel(gens, procs, total_apps)

                    y.append(model.proceed() / total_apps)

                for i in range(len(self.custom_plan)):
                    if len(self.custom_plan[i]) > 0:
                        gen_int1 = scale_factor(self.custom_plan[i][1], gen1_int_min, gen1_int_max)
                        gen_int2 = scale_factor(self.custom_plan[i][2], gen2_int_min, gen2_int_max)
                        proc_int1 = scale_factor(self.custom_plan[i][3], proc1_int_min, proc1_int_max)
                        proc_dev1 = scale_factor(self.custom_plan[i][4], proc1_dev_min, proc1_dev_max)
                        proc_int2 = scale_factor(self.custom_plan[i][5], proc2_int_min, proc2_int_max)
                        proc_dev2 = scale_factor(self.custom_plan[i][6], proc2_dev_min, proc2_dev_max)

                        gens = [Generator(exp_by_intensity, (gen_int1,)),
                                Generator(exp_by_intensity, (gen_int2,))]
                        procs = [Generator(norm_by_intensity, (proc_int1, proc_dev1)),
                                 Generator(norm_by_intensity, (proc_int2, proc_dev2))]
                        model = EventModel(gens, procs, total_apps)

                        y.append(model.proceed() / total_apps)

                else:
                    y.append(None)

                self.b = expand_plan(self.plan, self.custom_plan, y)

                self.fill_table()
                self.set_equasion()

    def fill_table(self):
        for i in range(len(self.plan)):
            for j in range(len(self.plan[i])):
                self.table_plan.setItem(i + 1, j + 1, QTableWidgetItem(str(round(self.plan[i][j], 3))))
        for i in range(len(self.custom_plan)):
            for j in range(len(self.custom_plan[i])):
                self.table_plan.setItem(i + len(self.plan) + 1, j + 1,
                                        QTableWidgetItem(str(round(self.custom_plan[i][j], 3))))

    def set_equasion(self, accuracy=3):
        if len(self.b) == 70:
            y = str(round(self.b[0], accuracy)) + " + " + str(round(self.b[1], accuracy)) + "x1 + " + str(
                round(self.b[2], accuracy)) + "x2 + " + str(round(self.b[3], accuracy)) + "x3 + " + str(
                round(self.b[4], accuracy)) + "x4 + " + str(round(self.b[5], accuracy)) + "x5 + " + str(
                round(self.b[6], accuracy)) + "x6 + " + str(round(self.b[7], accuracy)) + "x1x2 + " + str(
                round(self.b[8], accuracy)) + "x1x3 + " + str(round(self.b[9], accuracy)) + "x1x4 + " + str(
                round(self.b[10], accuracy)) + "x1x5 + \n" + str(round(self.b[11], accuracy)) + "x1x6 + " + str(
                round(self.b[12], accuracy)) + "x2x3 + " + str(round(self.b[13], accuracy)) + "x2x4 + " + str(
                round(self.b[14], accuracy)) + "x2x5 + " + str(round(self.b[15], accuracy)) + "x2x6 + " + str(
                round(self.b[16], accuracy)) + "x3x4 + " + str(round(self.b[17], accuracy)) + "x3x5 + " + str(
                round(self.b[18], accuracy)) + "x3x6 + " + str(round(self.b[19], accuracy)) + "x4x5 + " + str(
                round(self.b[20], accuracy)) + "x4x6 + " + str(round(self.b[21], accuracy)) + "x5x6 + \n" + str(
                round(self.b[64], accuracy)) + "x1^2 + " + str(round(self.b[65], accuracy)) + "x2^2 + " + str(
                round(self.b[66], accuracy)) + "x3^2 + " + str(round(self.b[67], accuracy)) + "x4^2 + " + str(
                round(self.b[68], accuracy)) + "x5^2 + " + str(round(self.b[69], accuracy)) + "x6^2 + ..."
            y = y.replace("+ -", "- ")
            y = y.replace("+ \n-", "-\n")
            self.label_y.setText(y)

    def show_full_equasion(self):
        accuracy = 3
        if len(self.b) == 70:
            y = "y = " + str(round(self.b[0], accuracy)) + " + " + str(round(self.b[1], accuracy)) + "x1 + " + str(
                round(self.b[2], accuracy)) + "x2 + " + str(round(self.b[3], accuracy)) + "x3 + " + str(
                round(self.b[4], accuracy)) + "x4 +" + str(round(self.b[5], accuracy)) + "x5 + " + str(
                round(self.b[6], accuracy)) + "x6 + " + str(round(self.b[7], accuracy)) + "x1x2 + " + str(
                round(self.b[8], accuracy)) + "x1x3 + " + str(round(self.b[9], accuracy)) + "x1x4 + " + str(
                round(self.b[10], accuracy)) + "x1x5 + \n" + str(round(self.b[11], accuracy)) + "x1x6 + " + str(
                round(self.b[12], accuracy)) + "x2x3 + " + str(round(self.b[13], accuracy)) + "x2x4 + " + str(
                round(self.b[14], accuracy)) + "x2x5 + " + str(round(self.b[15], accuracy)) + "x2x6 + " + str(
                round(self.b[16], accuracy)) + "x3x4 + " + str(round(self.b[17], accuracy)) + "x3x5 + " + str(
                round(self.b[18], accuracy)) + "x3x6 + " + str(round(self.b[19], accuracy)) + "x4x5 + " + str(
                round(self.b[20], accuracy)) + "x4x6 + " + str(round(self.b[21], accuracy)) + "x5x6 + \n" + str(
                round(self.b[22], accuracy)) + "x1x2x3 + " + str(round(self.b[23], accuracy)) + "x1x2x4 + " + str(
                round(self.b[24], accuracy)) + "x1x2x5 + " + str(round(self.b[25], accuracy)) + "x1x2x6 + " + str(
                round(self.b[26], accuracy)) + "x1x3x4 + " + str(round(self.b[27], accuracy)) + "x1x3x5 + " + str(
                round(self.b[28], accuracy)) + "x1x3x6 + " + str(round(self.b[28], accuracy)) + "x1x4x5 + " + str(
                round(self.b[30], accuracy)) + "x1x4x6 + " + str(round(self.b[31], accuracy)) + "x1x5x6 + " + str(
                round(self.b[32], accuracy)) + "x2x3x4 + \n" + str(round(self.b[33], accuracy)) + "x2x3x5 + " + str(
                round(self.b[34], accuracy)) + "x2x3x6 + " + str(round(self.b[35], accuracy)) + "x2x4x5 + " + str(
                round(self.b[36], accuracy)) + "x2x4x6 + " + str(round(self.b[37], accuracy)) + "x2x5x6 + " + str(
                round(self.b[38], accuracy)) + "x3x4x5 + " + str(round(self.b[39], accuracy)) + "x3x4x6 + " + str(
                round(self.b[40], accuracy)) + "x3x5x6 + " + str(round(self.b[41], accuracy)) + "x4x5x6 + " + str(
                round(self.b[42], accuracy)) + "x1x2x3x4 + " + str(round(self.b[43], accuracy)) + "x1x2x3x5 + \n" + str(
                round(self.b[44], accuracy)) + "x1x2x3x6 + " + str(round(self.b[45], accuracy)) + "x1x2x4x5 + " + str(
                round(self.b[46], accuracy)) + "x1x2x4x6 + " + str(round(self.b[47], accuracy)) + "x1x2x5x6 + " + str(
                round(self.b[48], accuracy)) + "x1x3x4x5 + " + str(round(self.b[49], accuracy)) + "x1x3x4x6 + " + str(
                round(self.b[50], accuracy)) + "x1x3x5x6 + " + str(round(self.b[51], accuracy)) + "x1x4x5x6 + " + str(
                round(self.b[52], accuracy)) + "x2x3x4x5 + " + str(round(self.b[53], accuracy)) + "x2x3x4x6 + " + str(
                round(self.b[54], accuracy)) + "x2x3x5x6 + \n" + str(round(self.b[55], accuracy)) + "x2x4x5x6 + " + str(
                round(self.b[56], accuracy)) + "x3x4x5x6 + " + str(round(self.b[57], accuracy)) + "x1x2x3x4x5 + " + str(
                round(self.b[58], accuracy)) + "x1x2x3x4x6 + " + str(
                round(self.b[59], accuracy)) + "x1x2x3x5x6 + " + str(
                round(self.b[60], accuracy)) + "x1x2x4x5x6 + " + str(
                round(self.b[61], accuracy)) + "x1x3x4x5x6 + " + str(
                round(self.b[62], accuracy)) + "x2x3x4x5x6 + " + str(
                round(self.b[63], accuracy)) + "x1x2x3x4x5x6 + \n" + str(
                round(self.b[64], accuracy)) + "x1^2 + " + str(round(self.b[65], accuracy)) + "x2^2 + " + str(
                round(self.b[66], accuracy)) + "x3^2 + " + str(round(self.b[67], accuracy)) + "x4^2 + " + str(
                round(self.b[68], accuracy)) + "x5^2 + " + str(round(self.b[69], accuracy)) + "x6^2"
            y = y.replace("+ -", "- ")
            y = y.replace("+ \n-", "-\n")
            self.equation_window.show(y)

    def set(self):
        try:
            x1 = get_valid(self.entry_x1, float, lambda val: val < -1 or val > 1)
            x2 = get_valid(self.entry_x2, float, lambda val: val < -1 or val > 1)
            x3 = get_valid(self.entry_x3, float, lambda val: val < -1 or val > 1)
            x4 = get_valid(self.entry_x4, float, lambda val: val < -1 or val > 1)
            x5 = get_valid(self.entry_x5, float, lambda val: val < -1 or val > 1)
            x6 = get_valid(self.entry_x6, float, lambda val: val < -1 or val > 1)
        except ValueError:
            pass
        else:
            factors = [x1, x2, x3, x4, x5, x6]
            n = calc_n(6)
            self.custom_plan[0] = [1]
            self.custom_plan[0].extend(factors)
            self.custom_plan[0].extend(combination(factors))
            self.custom_plan[0].extend(shifted_points(factors, calc_star_length(n, calc_exp_amount(6, n))))
            for i in range(len(self.custom_plan)):
                for j in range(len(self.custom_plan[i])):
                    self.table_plan.setItem(78, j + 1, QTableWidgetItem(str(round(self.custom_plan[i][j], 3))))
