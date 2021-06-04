from PyQt5.QtWidgets import QDialog, QLabel


class EquationWindow(QDialog):
    def __init__(self):
        super(EquationWindow, self).__init__()
        self.setWindowTitle("Полное уравнение")
        self.label = QLabel(self)
        self.label.move(20, 10)
        self.resize(1250, 160)

    def show(self, y):
        self.label.setText(y)
        super(EquationWindow, self).show()
