from PyQt5.QtWidgets import QMainWindow, QDialog, QTextEdit, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox, QLabel


class StartMeasurementWindow(QDialog):
    def __init__(self, parent=None):
        super(StartMeasurementWindow, self).__init__(parent)

        self.setWindowTitle("New measure")

        layout = QVBoxLayout()

        configs = QTextEdit("Configs...")
        layout.addWidget(configs)

        self.setLayout(layout)

        self.resize(1000, 500)
        self.show()

