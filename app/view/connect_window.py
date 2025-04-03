from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton
from PyQt5.QtCore import pyqtSignal

class ConnectWindow(QDialog):
    connection_established_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(250, 250, 500, 300)

        main_layout = QVBoxLayout()

        self.port_list = QListWidget()

        self.connect_button = QPushButton('Connect')
        self.connect_button.setEnabled(False)

        self.fresh_button = QPushButton('Refresh')

        main_layout.addWidget(self.port_list)
        main_layout.addWidget(self.fresh_button)
        main_layout.addWidget(self.connect_button)

        self.setLayout(main_layout)


