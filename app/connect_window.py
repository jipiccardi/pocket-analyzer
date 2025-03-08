import serial.tools.list_ports
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout

from globals import serial_client


def show_connect_window():
    window = ConnectWindow()
    window.exec_()


class ConnectWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(250, 250, 500, 300)

        main_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout

        self.port_list = QListWidget()
        refresh_button = QPushButton('Refresh')
        refresh_button.clicked.connect(self.refresh_button)

        connect_button = QPushButton('Connect')
        connect_button.clicked.connect(lambda: serial_client.connect(self.port_list.currentItem().text()))

        main_layout.addWidget(self.port_list)
        main_layout.addWidget(refresh_button)
        main_layout.addWidget(connect_button)
        #buttons_layout.addWidget(refresh_button)
        #buttons_layout.addWidget(connect_button)

        #main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)
        self.refresh_button()

    def refresh_button(self):
        self.port_list.clear()
        ports = serial.tools.list_ports.comports()

        for port in ports:
            self.port_list.addItem(port.device)